"""
Transcribe all answer audio files using LemonFox AI
This script will:
1. Find all answer audio files (_A*.mp3)
2. Transcribe them using LemonFox AI
3. Match them with questions in the database
4. Save to a JSON file for later use
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

# Add parent directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models import Question

# LemonFox AI API configuration
LEMONFOX_API_URL = "https://api.lemonfox.ai/v1/audio/transcriptions"
LEMONFOX_API_KEY = os.getenv('LEMONFOX_API_KEY', '')  # Set this in your environment

def transcribe_audio_lemonfox(audio_file_path, api_key):
    """
    Transcribe audio file using LemonFox AI
    """
    if not api_key:
        print("⚠️  Warning: No LemonFox API key found. Set LEMONFOX_API_KEY environment variable.")
        return None
    
    try:
        print(f"  📝 Transcribing: {os.path.basename(audio_file_path)}")
        
        with open(audio_file_path, 'rb') as audio_file:
            files = {
                'file': (os.path.basename(audio_file_path), audio_file, 'audio/mpeg')
            }
            headers = {
                'Authorization': f'Bearer {api_key}'
            }
            data = {
                'model': 'whisper-1',
                'language': 'en'
            }
            
            response = requests.post(
                LEMONFOX_API_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                transcription = result.get('text', '').strip()
                print(f"  ✅ Success: {transcription[:60]}...")
                return transcription
            else:
                print(f"  ❌ Error: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        print(f"  ❌ Error transcribing {audio_file_path}: {str(e)}")
        return None

def find_all_answer_files():
    """
    Find all answer audio files in the uploads/questions directory
    """
    answer_files = []
    questions_dir = os.path.join(project_root, 'uploads', 'questions')
    
    if not os.path.exists(questions_dir):
        print(f"❌ Questions directory not found: {questions_dir}")
        return answer_files
    
    # Walk through all directories
    for root, dirs, files in os.walk(questions_dir):
        for file in files:
            # Check if it's an answer file (contains _A and is .mp3)
            if '_A' in file and file.endswith('.mp3'):
                full_path = os.path.join(root, file)
                # Get relative path from project root
                rel_path = os.path.relpath(full_path, project_root)
                # Normalize path separators to forward slashes
                rel_path = rel_path.replace('\\', '/')
                answer_files.append(rel_path)
    
    return sorted(answer_files)

def extract_question_info(audio_path):
    """
    Extract level, topic, and question number from audio path
    Example: uploads/questions/english/AL/01. Newspapers/01_A1.mp3
    Returns: (level, topic, question_number, answer_number)
    """
    parts = audio_path.split('/')
    
    if len(parts) < 5:
        return None, None, None, None
    
    level = parts[3]  # AL, IH, or IM
    topic_folder = parts[4]  # e.g., "01. Newspapers"
    filename = parts[-1]  # e.g., "01_A1.mp3"
    
    # Extract topic name (remove number prefix)
    if '. ' in topic_folder:
        topic = topic_folder.split('. ', 1)[1]
    else:
        topic = topic_folder
    
    # Extract question and answer numbers from filename
    # Format: XX_AY.mp3 where XX is question number, Y is answer number
    base_name = filename.replace('.mp3', '')
    parts_name = base_name.split('_')
    
    if len(parts_name) >= 2:
        question_prefix = parts_name[0]  # e.g., "01"
        answer_part = parts_name[1]  # e.g., "A1" or "A2-1"
        
        # Extract answer number (remove 'A' and any sub-parts)
        answer_num = answer_part.replace('A', '').split('-')[0]
        
        return level, topic, question_prefix, answer_num
    
    return None, None, None, None

def match_answer_to_question(level, topic, question_prefix, answer_num):
    """
    Find the question in the database that corresponds to this answer
    """
    app = create_app()
    with app.app_context():
        # Query for questions matching difficulty_level and topic
        questions = Question.query.filter_by(
            difficulty_level=level,
            topic=topic
        ).all()
        
        # Find the question that matches the prefix and number pattern
        for q in questions:
            if q.audio_url:
                # Extract question number from audio path
                # e.g., "uploads/questions/english/AL/01. Newspapers/01_Q1.mp3"
                filename = os.path.basename(q.audio_url)
                if filename.startswith(question_prefix + '_Q'):
                    # Extract the Q number part
                    q_part = filename.replace('.mp3', '').split('_')[1]  # e.g., "Q1" or "Q2-1"
                    q_num = q_part.replace('Q', '').split('-')[0]
                    
                    # Match if the answer number corresponds to this question
                    # For now, we'll match A1 to Q1, A2 to Q2, etc.
                    if q_num == answer_num:
                        return q.id
        
        return None

def save_level_backups(answers_by_level):
    """
    Save answer transcriptions to transcription_backups folder, organized by level
    Each level has ONE file that gets updated (no timestamps)
    """
    # Create transcription_backups folder if it doesn't exist
    backup_dir = os.path.join(project_root, 'transcription_backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Save each level to a separate file (overwrite existing)
    for level, answers in answers_by_level.items():
        if answers:  # Only save if there are answers for this level
            filename = f'answers_{level}.json'
            filepath = os.path.join(backup_dir, filename)
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(answers, f, indent=2, ensure_ascii=False)
                print(f"  ✅ Saved {level} backup: {len(answers)} answers")
            except Exception as e:
                print(f"  ⚠️  Warning: Could not save backup for {level}: {e}")

def main():
    """
    Main function to transcribe all answer files
    """
    print("=" * 70)
    print("🎤 Answer Transcription Script - LemonFox AI")
    print("=" * 70)
    print()
    
    # Check for API key
    api_key = os.getenv('LEMONFOX_API_KEY', '')
    if not api_key:
        print("❌ Error: LEMONFOX_API_KEY environment variable not set!")
        print()
        print("Please set your LemonFox AI API key:")
        print("  Windows: set LEMONFOX_API_KEY=your_api_key_here")
        print("  Linux/Mac: export LEMONFOX_API_KEY=your_api_key_here")
        print()
        return
    
    print(f"✅ LemonFox API key found: {api_key[:10]}...")
    print()
    
    # Find all answer files
    print("🔍 Searching for answer audio files...")
    answer_files = find_all_answer_files()
    print(f"✅ Found {len(answer_files)} answer files")
    print()
    
    if not answer_files:
        print("❌ No answer files found!")
        return
    
    # Process each answer file
    answers_data = {}
    processed = 0
    failed = 0
    skipped = 0
    
    # Organize answers by level for backup
    answers_by_level = {
        'AL': {},
        'IH': {},
        'IM': {}
    }
    
    # Check if we have existing level-specific backup files to resume from
    backup_dir = os.path.join(project_root, 'transcription_backups')
    for level in ['AL', 'IH', 'IM']:
        backup_file = os.path.join(backup_dir, f'answers_{level}.json')
        if os.path.exists(backup_file):
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    level_data = json.load(f)
                answers_by_level[level] = level_data
                print(f"📂 Loaded existing {level} backup: {len(level_data)} answers")
            except Exception as e:
                print(f"⚠️  Warning: Could not load {level} backup: {e}")
    
    # Check if we have a partial results file to resume from
    output_file = os.path.join(project_root, 'static', 'sample_answers.json')
    if os.path.exists(output_file):
        print("📂 Found existing combined answers file, loading...")
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                answers_data = json.load(f)
            print(f"✅ Loaded {len(answers_data)} existing transcriptions")
            
            # Organize existing data by level (merge with backup data)
            for audio_path, answer_info in answers_data.items():
                level = answer_info.get('level', '')
                if level in answers_by_level:
                    answers_by_level[level][audio_path] = answer_info.get('transcription', '')
            
            print()
        except Exception as e:
            print(f"⚠️  Warning: Could not load existing file: {e}")
            print()
    
    print("🚀 Starting transcription process...")
    print(f"   Total files to process: {len(answer_files)}")
    print()
    
    for idx, audio_path in enumerate(answer_files, 1):
        print(f"[{idx}/{len(answer_files)}] Processing: {audio_path}")
        
        # Skip if already transcribed
        if audio_path in answers_data and answers_data[audio_path].get('transcription'):
            print(f"  ⏭️  Already transcribed, skipping...")
            skipped += 1
            continue
        
        # Get full path
        full_path = os.path.join(project_root, audio_path)
        
        if not os.path.exists(full_path):
            print(f"  ⚠️  File not found: {full_path}")
            failed += 1
            continue
        
        # Extract question info
        level, topic, question_prefix, answer_num = extract_question_info(audio_path)
        
        if not level or not topic:
            print(f"  ⚠️  Could not extract info from path")
            failed += 1
            continue
        
        print(f"  📋 Level: {level}, Topic: {topic}, Prefix: {question_prefix}, Answer: {answer_num}")
        
        # Find matching question in database
        question_id = match_answer_to_question(level, topic, question_prefix, answer_num)
        
        # Transcribe the audio
        transcription = transcribe_audio_lemonfox(full_path, api_key)
        
        if transcription:
            # Store the result
            answers_data[audio_path] = {
                'transcription': transcription,
                'level': level,
                'topic': topic,
                'question_prefix': question_prefix,
                'answer_number': answer_num,
                'question_id': question_id,
                'audio_file': audio_path
            }
            
            # Add to level-specific dictionary
            if level in answers_by_level:
                answers_by_level[level][audio_path] = transcription
            
            processed += 1
            
            # Save progress every 10 files
            if processed % 10 == 0:
                print(f"\n  💾 Saving progress... ({processed} transcriptions)")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(answers_data, f, indent=2, ensure_ascii=False)
                
                # Also save to transcription_backups folder
                save_level_backups(answers_by_level)
                
                print(f"  ✅ Progress saved to {output_file} and transcription_backups/\n")
            
            # Rate limiting - be nice to the API
            time.sleep(1)
        else:
            failed += 1
        
        print()
    
    # Save final results
    print("=" * 70)
    print("💾 Saving final results...")
    
    # Save to static folder
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(answers_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Results saved to: {output_file}")
    
    # Save to transcription_backups folder
    print("💾 Saving level-specific backups...")
    save_level_backups(answers_by_level)
    
    print()
    print("=" * 70)
    print("📊 Summary:")
    print(f"   Total files found: {len(answer_files)}")
    print(f"   Successfully transcribed: {processed}")
    print(f"   Skipped (already done): {skipped}")
    print(f"   Failed: {failed}")
    print()
    print(f"   AL level answers: {len(answers_by_level['AL'])}")
    print(f"   IH level answers: {len(answers_by_level['IH'])}")
    print(f"   IM level answers: {len(answers_by_level['IM'])}")
    print("=" * 70)
    print()
    
    if processed > 0:
        print("✅ Transcription complete!")
        print()
        print("Next steps:")
        print("1. Check the generated files:")
        print("   - static/sample_answers.json (for web use)")
        print("   - transcription_backups/answers_AL.json (AL level backup)")
        print("   - transcription_backups/answers_IH.json (IH level backup)")
        print("   - transcription_backups/answers_IM.json (IM level backup)")
        print("2. Answers will be available in practice mode")
        print("3. You can re-run this script to transcribe any missing files")
    else:
        print("⚠️  No new files were transcribed")
    
    print()

if __name__ == '__main__':
    main()


