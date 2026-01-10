"""
TTS Service for OPIc Practice Portal
Uses edge-tts (Microsoft Edge Text-to-Speech) for free, high-quality neural voices.
Includes auto-scan functionality to generate audio for questions without voice.
"""
import os
import asyncio
import threading
import time
import edge_tts
from flask import current_app
from typing import List, Dict, Optional, Tuple

class TTSService:
    """Service for generating Text-to-Speech audio using edge-tts"""
    
    # Voice mapping - using "Ava" as requested for OPIc interviewer style
    VOICE_MAPPING = {
        'ava': 'en-US-AvaNeural',      # The requested voice (OPIc interviewer style)
        'jenny': 'en-US-JennyNeural',  # Good alternative
        'guy': 'en-US-GuyNeural',      # Male option
        'aria': 'en-US-AriaNeural'     # Another female option
    }
    
    def __init__(self):
        self.default_voice = self.VOICE_MAPPING['aria']
    
    async def _generate_audio_async(self, text: str, output_path: str, voice: str) -> bool:
        """Async internal method to generate audio"""
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            return True
        except Exception as e:
            # We can't log to current_app here easily if it's not in context, 
            # but we are in a thread where we might lose context. 
            # However, we are just returning False and logging in the caller.
            print(f"Error in edge-tts generation: {e}")
            return False

    def _run_async_in_thread(self, text: str, output_path: str, voice: str) -> bool:
        """Run async function in a separate thread with its own event loop"""
        result = [False]
        
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(self._generate_audio_async(text, output_path, voice))
                result[0] = success
            except Exception as e:
                print(f"Thread error: {e}")
            finally:
                loop.close()

        t = threading.Thread(target=run_in_thread)
        t.start()
        t.join()
        
        return result[0]

    def generate_audio_standalone(self, text: str, output_path: str, voice_key: str = 'aria') -> bool:
        """
        Generate audio file from text using edge-tts (standalone, no Flask context required).
        
        Args:
            text: Text to convert to speech
            output_path: Full path to save the audio file
            voice_key: Key from VOICE_MAPPING (default: 'aria')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Get voice ID
            voice = self.VOICE_MAPPING.get(voice_key.lower(), self.default_voice)
            
            print(f"Generating TTS audio using voice: {voice}")
            
            # Run async function in a separate thread
            success = self._run_async_in_thread(text, output_path, voice)
            
            # Verify file was created
            if success and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"TTS audio saved to: {output_path}")
                return True
            else:
                print("TTS audio file was not created or is empty")
                return False
                
        except Exception as e:
            print(f"Failed to generate TTS audio: {e}")
            import traceback
            traceback.print_exc()
            return False

    def generate_audio(self, text: str, output_path: str, voice_key: str = 'aria') -> bool:
        """
        Generate audio file from text using edge-tts.
        
        Args:
            text: Text to convert to speech
            output_path: Full path to save the audio file
            voice_key: Key from VOICE_MAPPING (default: 'aria')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Get voice ID
            voice = self.VOICE_MAPPING.get(voice_key.lower(), self.default_voice)
            
            current_app.logger.info(f"Generating TTS audio using voice: {voice}")
            
            # Run async function in a separate thread with its own loop
            # This avoids conflicts with Flask's loop or nest_asyncio issues
            result = [False]
            
            def run_in_thread():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    success = loop.run_until_complete(self._generate_audio_async(text, output_path, voice))
                    result[0] = success
                except Exception as e:
                    print(f"Thread error: {e}")
                finally:
                    loop.close()

            t = threading.Thread(target=run_in_thread)
            t.start()
            t.join()
                
            # Verify file was created
            if result[0] and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                current_app.logger.info(f"TTS audio saved to: {output_path}")
                return True
            else:
                current_app.logger.error("TTS audio file was not created or is empty")
                return False
                
        except Exception as e:
            current_app.logger.error(f"Failed to generate TTS audio: {e}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return False

    def _get_upload_base_dir(self) -> str:
        """Get the base upload directory path for questions audio"""
        # Get the project root directory (OPP folder)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_dir, 'uploads', 'questions')

    def scan_missing_audio(self, include_sample_answer: bool = True) -> Dict[str, List[Dict]]:
        """
        Scan for questions that have text but no audio file.
        
        Args:
            include_sample_answer: Also check for sample answers missing audio
            
        Returns:
            Dict with:
                - 'questions': List of questions missing main audio
                - 'sample_answers': List of questions missing sample answer audio
                - 'total_missing': Total count of missing audio files
        """
        from app.models import Question
        from app import db
        from sqlalchemy import or_, and_
        
        result = {
            'questions': [],
            'sample_answers': [],
            'total_missing': 0
        }
        
        # Find questions with text but no audio_url
        missing_question_audio = Question.query.filter(
            and_(
                Question.text.isnot(None),
                Question.text != '',
                or_(
                    Question.audio_url.is_(None),
                    Question.audio_url == ''
                )
            )
        ).all()
        
        for q in missing_question_audio:
            result['questions'].append({
                'id': q.id,
                'topic': q.topic,
                'level': q.difficulty_level,
                'text': q.text[:100] + '...' if len(q.text or '') > 100 else q.text,
                'text_full': q.text
            })
        
        # Find questions with sample_answer_text but no sample_answer_audio_url
        if include_sample_answer:
            missing_sample_audio = Question.query.filter(
                and_(
                    Question.sample_answer_text.isnot(None),
                    Question.sample_answer_text != '',
                    or_(
                        Question.sample_answer_audio_url.is_(None),
                        Question.sample_answer_audio_url == ''
                    )
                )
            ).all()
            
            for q in missing_sample_audio:
                result['sample_answers'].append({
                    'id': q.id,
                    'topic': q.topic,
                    'level': q.difficulty_level,
                    'text': q.sample_answer_text[:100] + '...' if len(q.sample_answer_text or '') > 100 else q.sample_answer_text,
                    'text_full': q.sample_answer_text
                })
        
        result['total_missing'] = len(result['questions']) + len(result['sample_answers'])
        return result

    def generate_missing_audio(
        self, 
        voice_key: str = 'ava',
        generate_questions: bool = True,
        generate_sample_answers: bool = True,
        limit: Optional[int] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Auto-generate TTS audio for all questions that have text but no voice.
        
        Args:
            voice_key: Voice to use for TTS generation
            generate_questions: Generate audio for main question text
            generate_sample_answers: Generate audio for sample answers
            limit: Maximum number of items to process (None for all)
            progress_callback: Optional callback function(current, total, message)
            
        Returns:
            Dict with generation results:
                - 'success_count': Number of successfully generated
                - 'failed_count': Number of failures
                - 'skipped_count': Number skipped
                - 'details': List of individual results
        """
        from app.models import Question
        from app import db
        
        result = {
            'success_count': 0,
            'failed_count': 0,
            'skipped_count': 0,
            'details': []
        }
        
        upload_dir = self._get_upload_base_dir()
        os.makedirs(upload_dir, exist_ok=True)
        
        # Scan for missing audio
        missing = self.scan_missing_audio(include_sample_answer=generate_sample_answers)
        
        items_to_process = []
        
        # Add questions missing audio
        if generate_questions:
            for q_info in missing['questions']:
                items_to_process.append({
                    'id': q_info['id'],
                    'type': 'question',
                    'text': q_info['text_full'],
                    'topic': q_info['topic'],
                    'level': q_info['level']
                })
        
        # Add sample answers missing audio
        if generate_sample_answers:
            for q_info in missing['sample_answers']:
                items_to_process.append({
                    'id': q_info['id'],
                    'type': 'sample_answer',
                    'text': q_info['text_full'],
                    'topic': q_info['topic'],
                    'level': q_info['level']
                })
        
        # Apply limit if specified
        if limit and limit > 0:
            items_to_process = items_to_process[:limit]
        
        total = len(items_to_process)
        
        for idx, item in enumerate(items_to_process):
            question_id = item['id']
            item_type = item['type']
            text = item['text']
            
            if progress_callback:
                progress_callback(idx + 1, total, f"Processing {item_type} for question #{question_id}")
            
            # Skip if text is empty or too short
            if not text or len(text.strip()) < 5:
                result['skipped_count'] += 1
                result['details'].append({
                    'question_id': question_id,
                    'type': item_type,
                    'status': 'skipped',
                    'reason': 'Text too short or empty'
                })
                continue
            
            try:
                # Generate filename
                timestamp = int(time.time() * 1000)  # Use milliseconds for uniqueness
                if item_type == 'question':
                    filename = f"q_{question_id}_{timestamp}.mp3"
                else:
                    filename = f"sa_{question_id}_{timestamp}.mp3"
                
                output_path = os.path.join(upload_dir, filename)
                audio_url = f"/uploads/questions/{filename}"
                
                # Generate audio using standalone method (no Flask context required in thread)
                success = self.generate_audio_standalone(text, output_path, voice_key)
                
                if success:
                    # Update database
                    question = Question.query.get(question_id)
                    if question:
                        if item_type == 'question':
                            question.audio_url = audio_url
                        else:
                            question.sample_answer_audio_url = audio_url
                        db.session.commit()
                        
                        result['success_count'] += 1
                        result['details'].append({
                            'question_id': question_id,
                            'type': item_type,
                            'status': 'success',
                            'audio_url': audio_url
                        })
                        print(f"✓ Generated {item_type} audio for question #{question_id}")
                    else:
                        result['failed_count'] += 1
                        result['details'].append({
                            'question_id': question_id,
                            'type': item_type,
                            'status': 'failed',
                            'reason': 'Question not found in database'
                        })
                else:
                    result['failed_count'] += 1
                    result['details'].append({
                        'question_id': question_id,
                        'type': item_type,
                        'status': 'failed',
                        'reason': 'TTS generation failed'
                    })
                    print(f"✗ Failed to generate {item_type} audio for question #{question_id}")
                    
            except Exception as e:
                result['failed_count'] += 1
                result['details'].append({
                    'question_id': question_id,
                    'type': item_type,
                    'status': 'failed',
                    'reason': str(e)
                })
                print(f"✗ Error generating {item_type} audio for question #{question_id}: {e}")
                # Rollback any pending changes
                db.session.rollback()
        
        return result

    def generate_missing_audio_for_topic(
        self,
        topic: str,
        voice_key: str = 'ava',
        generate_questions: bool = True,
        generate_sample_answers: bool = True
    ) -> Dict:
        """
        Generate missing audio for questions in a specific topic.
        
        Args:
            topic: Topic name to filter by
            voice_key: Voice to use for TTS
            generate_questions: Generate main question audio
            generate_sample_answers: Generate sample answer audio
            
        Returns:
            Dict with generation results
        """
        from app.models import Question
        from app import db
        from sqlalchemy import or_, and_
        
        result = {
            'success_count': 0,
            'failed_count': 0,
            'skipped_count': 0,
            'details': []
        }
        
        upload_dir = self._get_upload_base_dir()
        os.makedirs(upload_dir, exist_ok=True)
        
        # Find questions in topic missing audio
        items_to_process = []
        
        if generate_questions:
            missing_q = Question.query.filter(
                and_(
                    Question.topic == topic,
                    Question.text.isnot(None),
                    Question.text != '',
                    or_(
                        Question.audio_url.is_(None),
                        Question.audio_url == ''
                    )
                )
            ).all()
            
            for q in missing_q:
                items_to_process.append({
                    'id': q.id,
                    'type': 'question',
                    'text': q.text
                })
        
        if generate_sample_answers:
            missing_sa = Question.query.filter(
                and_(
                    Question.topic == topic,
                    Question.sample_answer_text.isnot(None),
                    Question.sample_answer_text != '',
                    or_(
                        Question.sample_answer_audio_url.is_(None),
                        Question.sample_answer_audio_url == ''
                    )
                )
            ).all()
            
            for q in missing_sa:
                items_to_process.append({
                    'id': q.id,
                    'type': 'sample_answer',
                    'text': q.sample_answer_text
                })
        
        # Process items
        for item in items_to_process:
            question_id = item['id']
            item_type = item['type']
            text = item['text']
            
            if not text or len(text.strip()) < 5:
                result['skipped_count'] += 1
                continue
            
            try:
                timestamp = int(time.time() * 1000)
                if item_type == 'question':
                    filename = f"q_{question_id}_{timestamp}.mp3"
                else:
                    filename = f"sa_{question_id}_{timestamp}.mp3"
                
                output_path = os.path.join(upload_dir, filename)
                audio_url = f"/uploads/questions/{filename}"
                
                success = self.generate_audio_standalone(text, output_path, voice_key)
                
                if success:
                    question = Question.query.get(question_id)
                    if question:
                        if item_type == 'question':
                            question.audio_url = audio_url
                        else:
                            question.sample_answer_audio_url = audio_url
                        db.session.commit()
                        result['success_count'] += 1
                        result['details'].append({
                            'question_id': question_id,
                            'type': item_type,
                            'status': 'success',
                            'audio_url': audio_url
                        })
                else:
                    result['failed_count'] += 1
                    result['details'].append({
                        'question_id': question_id,
                        'type': item_type,
                        'status': 'failed'
                    })
            except Exception as e:
                result['failed_count'] += 1
                db.session.rollback()
        
        return result


# Global instance for easy import
tts_service = TTSService()
