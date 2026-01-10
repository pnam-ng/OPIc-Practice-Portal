"""
Question Generation Service for OPIc Practice Portal
Provides AI-powered question generation, variation, and intelligent rotation
"""
import os
import json
import random
from typing import Dict, List, Optional, Tuple
from flask import current_app
from app.models import Question, QuestionSession
from app import db


class QuestionGeneratorService:
    """Service for AI-powered question generation and management"""
    
    # Question type templates for different categories
    QUESTION_TEMPLATES = {
        'general': [
            "Tell me about {topic} in your area/country.",
            "What do you know about {topic}?",
            "Can you describe {topic} to me?",
        ],
        'experience': [
            "Tell me about a memorable experience related to {topic}.",
            "Describe a time when you had an interesting experience with {topic}.",
            "What was your best/worst experience involving {topic}?",
        ],
        'comparison': [
            "Compare {topic} in the past and now. What has changed?",
            "What are the differences between {topic} in your country and other countries?",
            "Compare two different aspects of {topic}.",
        ],
        'roleplay': [
            "Imagine you are at a place related to {topic}. Ask 3-4 questions about it.",
            "You need to help a friend with {topic}. What would you say?",
            "There's a problem with {topic}. Call to report the issue and ask questions.",
        ],
        'opinion': [
            "What do you think about {topic}? Why?",
            "Do you think {topic} is important? Explain your reasons.",
            "What are the advantages and disadvantages of {topic}?",
        ]
    }
    
    # Variation prompts for generating question variations
    VARIATION_PROMPTS = {
        'rephrase': """Rephrase the following OPIc question while keeping the same meaning.
Original: {question}
Topic: {topic}
Level: {level}

Create a new version that asks the same thing but uses different words and structure.
Keep the difficulty level appropriate for {level}.
Respond with ONLY the new question text, nothing else.""",

        'followup': """Create a follow-up question based on this OPIc question.
Original: {question}
Topic: {topic}
Level: {level}

Create a deeper exploration question that could be asked after the original.
It should encourage more detailed or specific responses.
Respond with ONLY the follow-up question text, nothing else.""",

        'perspective': """Create a perspective-shift version of this OPIc question.
Original: {question}
Topic: {topic}
Level: {level}

Change the point of view (e.g., from personal to hypothetical, or add a scenario).
Examples: "If a tourist asked you...", "From your friend's perspective...", "In a professional setting..."
Respond with ONLY the new question text, nothing else.""",

        'timeshift': """Create a time-based variation of this OPIc question.
Original: {question}
Topic: {topic}
Level: {level}

Shift the time frame (past, present, or future) to create a new question.
Examples: past experiences, current habits, future plans, or changes over time.
Respond with ONLY the new question text, nothing else."""
    }
    
    def __init__(self):
        self._ai_service = None
    
    @property
    def ai_service(self):
        """Lazy load AI service"""
        if self._ai_service is None:
            from app.services.ai_service import AIService
            self._ai_service = AIService()
        return self._ai_service
    
    def generate_question(self, topic: str, level: str, question_type: str = 'general',
                         existing_questions: List[str] = None) -> Optional[Dict]:
        """
        Generate a new OPIc question using AI with template fallback
        
        Args:
            topic: The topic for the question (e.g., "Restaurants")
            level: Difficulty level (IM, IH, AL)
            question_type: Type of question to generate
            existing_questions: List of existing question texts to avoid duplication
            
        Returns:
            Dict with 'text', 'sample_answer', 'keywords' or None if failed
        """
        # Try AI-powered generation only (no template fallback)
        result = self._generate_with_ai(topic, level, question_type, existing_questions)
        return result  # Returns None if AI fails
    
    def _generate_with_ai(self, topic: str, level: str, question_type: str,
                          existing_questions: List[str] = None) -> Optional[Dict]:
        """Generate question using AI (Gemini API)"""
        try:
            existing_list = existing_questions or []
            existing_str = '\n'.join([f"- {q}" for q in existing_list[:10]])  # Limit to 10
            
            prompt = f"""You are an OPIc (Oral Proficiency Interview - Computer) test question creator.

Generate a NEW, UNIQUE question for the OPIc test.

**Parameters:**
- Topic: {topic}
- Level: {level} (IM=Intermediate-Mid, IH=Intermediate-High, AL=Advanced-Low)
- Question Type: {question_type}

**Existing questions to AVOID duplicating:**
{existing_str if existing_str else "(No existing questions)"}

**Requirements:**
1. The question must be appropriate for level {level}
2. It must be related to the topic "{topic}"
3. It should encourage a 1-2 minute spoken response
4. It must be DIFFERENT from the existing questions listed above
5. For {question_type} type: {"general description/introduction" if question_type == 'general' else "personal experience/story" if question_type == 'experience' else "compare two things" if question_type == 'comparison' else "role-play scenario" if question_type == 'roleplay' else "opinion/viewpoint"}

**Respond in JSON format:**
{{
    "question_text": "The full question text",
    "sample_answer": "A model 1-2 minute response to this question",
    "keywords": ["keyword1", "keyword2", "keyword3"]
}}"""

            content = self.ai_service._call_google_api(prompt)
            
            if not content:
                return None
            
            # Parse JSON response
            import re
            content = content.strip()
            content = re.sub(r'^```(?:json)?\s*', '', content, flags=re.MULTILINE)
            content = re.sub(r'\s*```$', '', content, flags=re.MULTILINE)
            
            # Find JSON object
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    'text': data.get('question_text', ''),
                    'sample_answer': data.get('sample_answer', ''),
                    'keywords': data.get('keywords', [])
                }
            
            return None
            
        except Exception as e:
            try:
                current_app.logger.warning(f"AI generation failed, will use template: {e}")
            except:
                print(f"AI generation failed, will use template: {e}")
            return None
    
    def _generate_from_template(self, topic: str, level: str, question_type: str,
                                existing_questions: List[str] = None) -> Optional[Dict]:
        """Generate question from templates (fallback when AI is unavailable)"""
        existing_list = existing_questions or []
        
        # Clean topic name first (remove numbering like "01. " and lowercase)
        clean_topic = topic
        if '. ' in topic:
            clean_topic = topic.split('. ', 1)[1]
        clean_topic = clean_topic.lower()
        
        # Extended templates for variety (using clean topic)
        templates = {
            'general': [
                f"Tell me about {clean_topic} in your area. What is it like?",
                f"Can you describe {clean_topic} in detail? What are the main characteristics?",
                f"I'd like to know about {clean_topic}. What can you tell me?",
                f"What is {clean_topic} like in your country? Please describe it.",
                f"Describe your experience with {clean_topic}. What do you know about it?",
                f"Let's talk about {clean_topic}. What comes to mind when you think about it?",
                f"Tell me everything you know about {clean_topic}.",
                f"Can you give me an overview of {clean_topic}?"
            ],
            'experience': [
                f"Tell me about a memorable experience you had with {clean_topic}.",
                f"Describe a specific time when {clean_topic} was important to you.",
                f"What was your best experience related to {clean_topic}? Why was it special?",
                f"Share a story about {clean_topic} that you remember well.",
                f"When was the last time you dealt with {clean_topic}? What happened?",
                f"Tell me about a time when {clean_topic} surprised you.",
                f"Describe an unforgettable moment involving {clean_topic}.",
                f"What interesting experience have you had with {clean_topic}?"
            ],
            'comparison': [
                f"Compare {clean_topic} now and 10 years ago. What has changed?",
                f"What are the differences between {clean_topic} in your country and abroad?",
                f"Compare two different aspects of {clean_topic}. Which do you prefer?",
                f"How has {clean_topic} changed since you were young?",
                f"Compare the advantages and disadvantages of {clean_topic}.",
                f"How does {clean_topic} differ between different age groups?",
                f"Compare traditional and modern approaches to {clean_topic}.",
                f"What's the difference between {clean_topic} in urban and rural areas?"
            ],
            'roleplay': [
                f"Imagine you're explaining {clean_topic} to a foreigner. What would you say?",
                f"You're helping a friend who knows nothing about {clean_topic}. Describe it to them.",
                f"Pretend you're a tour guide talking about {clean_topic}. What do you say?",
                f"You're writing a blog post about {clean_topic}. What would you include?",
                f"Imagine someone asks you about {clean_topic}. How would you explain it?",
                f"You're making a recommendation about {clean_topic}. What advice would you give?",
                f"Pretend you're being interviewed about {clean_topic}. What's your response?",
                f"A new colleague asks about {clean_topic}. How do you explain it?"
            ],
            'opinion': [
                f"What do you think about {clean_topic}? Do you like it or not? Why?",
                f"In your opinion, is {clean_topic} important? Explain your reasons.",
                f"What are your thoughts on {clean_topic}? Share your perspective.",
                f"Do you think {clean_topic} is beneficial or harmful? Why?",
                f"How do you feel about {clean_topic}? Has your opinion changed over time?",
                f"What's your personal view on {clean_topic}?",
                f"If you had to rate {clean_topic}, what would you say and why?",
                f"Do you agree that {clean_topic} is important in modern life? Why or why not?"
            ]
        }
        
        # Get templates for the requested type
        available_templates = templates.get(question_type, templates['general'])
        
        # Filter out templates that are too similar to existing questions
        unused_templates = []
        for template in available_templates:
            is_similar = False
            for existing in existing_list:
                # Simple similarity check
                if template.lower()[:30] == existing.lower()[:30]:
                    is_similar = True
                    break
            if not is_similar:
                unused_templates.append(template)
        
        # If all templates used, just pick a random one
        if not unused_templates:
            unused_templates = available_templates
        
        # Pick a random template
        question_text = random.choice(unused_templates)
        
        return {
            'text': question_text,
            'sample_answer': f"Sample answer for {clean_topic} question.",
            'keywords': [clean_topic, question_type, level.lower()]
        }

    
    def generate_variation(self, question: Question, variation_type: str) -> Optional[str]:
        """
        Generate a variation of an existing question
        
        Args:
            question: The original Question object
            variation_type: Type of variation ('rephrase', 'followup', 'perspective', 'timeshift')
            
        Returns:
            New question text or None if failed
        """
        if variation_type not in self.VARIATION_PROMPTS:
            current_app.logger.error(f"Invalid variation type: {variation_type}")
            return None
        
        try:
            prompt = self.VARIATION_PROMPTS[variation_type].format(
                question=question.text,
                topic=question.topic,
                level=question.difficulty_level or 'IH'
            )
            
            content = self.ai_service._call_google_api(prompt)
            
            if content:
                # Clean up the response
                content = content.strip()
                # Remove any quotes or extra formatting
                content = content.strip('"\'')
                if len(content) > 10:  # Basic validation
                    return content
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error generating variation: {e}")
            return None
    
    def generate_variations_batch(self, question: Question, types: List[str] = None) -> List[Dict]:
        """
        Generate multiple variations of a question
        
        Args:
            question: The original Question object
            types: List of variation types to generate
            
        Returns:
            List of dicts with 'text' and 'variation_type'
        """
        if types is None:
            types = ['rephrase', 'followup', 'perspective', 'timeshift']
        
        variations = []
        for var_type in types:
            text = self.generate_variation(question, var_type)
            if text:
                variations.append({
                    'text': text,
                    'variation_type': var_type,
                    'parent_id': question.id
                })
        
        return variations
    
    def get_next_question(self, user_id: int, topic: str, level: str) -> Tuple[Optional[Question], bool]:
        """
        Get the next question for a user using intelligent rotation
        
        Args:
            user_id: The user's ID
            topic: The topic to practice
            level: The difficulty level
            
        Returns:
            Tuple of (Question, is_new_round)
            - Question: The next question to show
            - is_new_round: True if a new round just started
        """
        try:
            # Get current round
            current_round = QuestionSession.get_current_round(user_id, topic, level)
            
            # Get seen question IDs in current round
            seen_ids = QuestionSession.get_seen_question_ids(user_id, topic, level, current_round)
            
            # Get all questions for this topic/level
            all_questions = Question.query.filter_by(
                topic=topic,
                difficulty_level=level
            ).all()
            
            if not all_questions:
                current_app.logger.warning(f"No questions found for topic={topic}, level={level}")
                return None, False
            
            # Filter unseen questions
            unseen_questions = [q for q in all_questions if q.id not in seen_ids]
            
            is_new_round = False
            
            if unseen_questions:
                # Pick random from unseen
                question = random.choice(unseen_questions)
            else:
                # All questions seen - start new round
                current_round += 1
                is_new_round = True
                question = random.choice(all_questions)
                current_app.logger.info(f"User {user_id} completed round {current_round - 1} for {topic}/{level}. Starting round {current_round}")
            
            # Log this session
            session = QuestionSession(
                user_id=user_id,
                question_id=question.id,
                topic=topic,
                difficulty_level=level,
                round_number=current_round,
                was_answered=False
            )
            db.session.add(session)
            db.session.commit()
            
            return question, is_new_round
            
        except Exception as e:
            current_app.logger.error(f"Error getting next question: {e}")
            db.session.rollback()
            # Fallback to random question
            question = Question.query.filter_by(
                topic=topic,
                difficulty_level=level
            ).order_by(db.func.random()).first()
            return question, False
    
    def mark_question_answered(self, user_id: int, question_id: int) -> bool:
        """Mark a question as answered in the current session"""
        try:
            session = QuestionSession.query.filter_by(
                user_id=user_id,
                question_id=question_id,
                was_answered=False
            ).order_by(QuestionSession.shown_at.desc()).first()
            
            if session:
                session.was_answered = True
                db.session.commit()
                return True
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error marking question answered: {e}")
            db.session.rollback()
            return False
    
    def get_user_progress(self, user_id: int, topic: str = None, level: str = None) -> Dict:
        """
        Get user's progress across topics/levels
        
        Args:
            user_id: The user's ID
            topic: Optional specific topic
            level: Optional specific level
            
        Returns:
            Dict with progress information
        """
        if topic and level:
            return QuestionSession.get_progress(user_id, topic, level)
        
        # Get overall progress
        from sqlalchemy import func
        
        # Get stats per topic/level
        stats_query = db.session.query(
            QuestionSession.topic,
            QuestionSession.difficulty_level,
            func.max(QuestionSession.round_number).label('max_round'),
            func.count(QuestionSession.id).label('total_shown')
        ).filter_by(user_id=user_id).group_by(
            QuestionSession.topic,
            QuestionSession.difficulty_level
        ).all()
        
        progress = {}
        for stat in stats_query:
            key = f"{stat.topic}_{stat.difficulty_level}"
            total_questions = Question.query.filter_by(
                topic=stat.topic,
                difficulty_level=stat.difficulty_level
            ).count()
            progress[key] = {
                'topic': stat.topic,
                'level': stat.difficulty_level,
                'rounds_completed': stat.max_round - 1 if stat.max_round else 0,
                'current_round': stat.max_round or 1,
                'total_shown': stat.total_shown,
                'total_questions': total_questions
            }
        
        return progress
    
    def save_generated_question(self, topic: str, level: str, text: str, 
                                sample_answer: str = None, keywords: List[str] = None,
                                parent_id: int = None, variation_type: str = None,
                                generation_source: str = 'gemini',
                                auto_generate_audio: bool = True) -> Optional[Question]:
        """
        Save a generated question to the database
        
        Args:
            topic: Topic for the question
            level: Difficulty level
            text: Question text
            sample_answer: Optional sample answer
            keywords: Optional list of keywords
            parent_id: Optional parent question ID (for variations)
            variation_type: Type of variation if applicable
            generation_source: Source of generation ('gemini', 'template', 'manual')
            auto_generate_audio: Whether to auto-generate TTS audio (default: True)
            
        Returns:
            The created Question object or None
        """
        try:
            question = Question(
                topic=topic,
                difficulty_level=level,
                text=text,
                sample_answer_text=sample_answer,
                keywords=keywords,
                parent_id=parent_id,
                variation_type=variation_type,
                is_generated=True,
                generation_source=generation_source,
                language='english',
                question_type='question'
            )
            db.session.add(question)
            db.session.commit()
            
            current_app.logger.info(f"Saved generated question: {text[:50]}...")
            
            # Auto-generate TTS audio for question and sample answer
            if auto_generate_audio:
                self._generate_audio_for_question(question)
            
            return question
            
        except Exception as e:
            current_app.logger.error(f"Error saving generated question: {e}")
            db.session.rollback()
            return None

    def _generate_audio_for_question(self, question: Question):
        """
        Generate TTS audio for a question in a background thread.
        This is called automatically after saving a generated question.
        """
        import threading
        
        def generate_in_background(question_id, text, sample_answer_text):
            try:
                from app.services.tts_service import TTSService
                import os
                import time
                
                tts = TTSService()
                upload_dir = tts._get_upload_base_dir()
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate question audio
                if text and len(text.strip()) >= 5:
                    timestamp = int(time.time() * 1000)
                    filename = f"q_{question_id}_{timestamp}.mp3"
                    output_path = os.path.join(upload_dir, filename)
                    audio_url = f"/uploads/questions/{filename}"
                    
                    if tts.generate_audio_standalone(text, output_path, voice_key='ava'):
                        # Update database using a new app context
                        from app import create_app, db
                        app = create_app()
                        with app.app_context():
                            from app.models import Question
                            q = Question.query.get(question_id)
                            if q:
                                q.audio_url = audio_url
                                db.session.commit()
                                print(f"✓ Auto-generated question audio for #{question_id}")
                
                # Generate sample answer audio
                if sample_answer_text and len(sample_answer_text.strip()) >= 5:
                    timestamp = int(time.time() * 1000)
                    filename = f"sa_{question_id}_{timestamp}.mp3"
                    output_path = os.path.join(upload_dir, filename)
                    audio_url = f"/uploads/questions/{filename}"
                    
                    if tts.generate_audio_standalone(sample_answer_text, output_path, voice_key='ava'):
                        from app import create_app, db
                        app = create_app()
                        with app.app_context():
                            from app.models import Question
                            q = Question.query.get(question_id)
                            if q:
                                q.sample_answer_audio_url = audio_url
                                db.session.commit()
                                print(f"✓ Auto-generated sample answer audio for #{question_id}")
                                
            except Exception as e:
                print(f"✗ Error auto-generating audio for question #{question_id}: {e}")
        
        # Run in background thread to not block the main request
        thread = threading.Thread(
            target=generate_in_background,
            args=(question.id, question.text, question.sample_answer_text),
            daemon=True
        )
        thread.start()


# Global instance
question_generator = QuestionGeneratorService()

