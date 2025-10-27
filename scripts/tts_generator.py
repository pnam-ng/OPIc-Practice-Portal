#!/usr/bin/env python3
"""
TTS Generator Script for OPIc Practice Portal
Generates audio files for questions using OpenAI TTS API
"""

import os
import sys
import time
from pathlib import Path
from flask import Flask
from app import create_app, db
from app.models.question import Question
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_tts_audio(text, output_path, voice="alloy"):
    """Generate TTS audio using OpenAI API"""
    try:
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        print(f"Generating audio for: {text[:50]}...")
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save audio file
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Audio saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error generating audio: {str(e)}")
        return False

def update_question_audio_url(question_id, audio_url):
    """Update question with audio URL"""
    try:
        question = Question.query.get(question_id)
        if question:
            question.audio_url = audio_url
            db.session.commit()
            print(f"✓ Updated question {question_id} with audio URL")
            return True
    except Exception as e:
        print(f"✗ Error updating question: {str(e)}")
        return False

def generate_all_question_audio():
    """Generate audio for all questions that don't have audio"""
    app = create_app()
    
    with app.app_context():
        # Get questions without audio
        questions_without_audio = Question.query.filter(
            (Question.audio_url.is_(None)) | (Question.audio_url == '')
        ).all()
        
        if not questions_without_audio:
            print("All questions already have audio files!")
            return
        
        print(f"Found {len(questions_without_audio)} questions without audio")
        
        success_count = 0
        total_count = len(questions_without_audio)
        
        for question in questions_without_audio:
            # Generate filename
            filename = f"question_{question.id}.mp3"
            output_path = os.path.join("uploads", "questions", filename)
            audio_url = f"/uploads/questions/{filename}"
            
            # Generate audio
            if generate_tts_audio(question.text, output_path):
                # Update database
                if update_question_audio_url(question.id, audio_url):
                    success_count += 1
                
                # Rate limiting - wait 1 second between requests
                time.sleep(1)
            else:
                print(f"✗ Failed to generate audio for question {question.id}")
        
        print(f"\nCompleted: {success_count}/{total_count} questions processed successfully")

def generate_specific_question_audio(question_id):
    """Generate audio for a specific question"""
    app = create_app()
    
    with app.app_context():
        question = Question.query.get(question_id)
        
        if not question:
            print(f"Question {question_id} not found!")
            return False
        
        # Generate filename
        filename = f"question_{question.id}.mp3"
        output_path = os.path.join("uploads", "questions", filename)
        audio_url = f"/uploads/questions/{filename}"
        
        # Generate audio
        if generate_tts_audio(question.text, output_path):
            # Update database
            if update_question_audio_url(question.id, audio_url):
                print(f"✓ Successfully generated audio for question {question_id}")
                return True
        
        print(f"✗ Failed to generate audio for question {question_id}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python tts_generator.py all                    # Generate audio for all questions")
        print("  python tts_generator.py question <id>          # Generate audio for specific question")
        print("  python tts_generator.py check                  # Check which questions need audio")
        return
    
    command = sys.argv[1]
    
    if command == "all":
        generate_all_question_audio()
    elif command == "question" and len(sys.argv) > 2:
        question_id = int(sys.argv[2])
        generate_specific_question_audio(question_id)
    elif command == "check":
        app = create_app()
        with app.app_context():
            questions_without_audio = Question.query.filter(
                (Question.audio_url.is_(None)) | (Question.audio_url == '')
            ).all()
            
            if questions_without_audio:
                print(f"Questions without audio ({len(questions_without_audio)}):")
                for q in questions_without_audio:
                    print(f"  ID: {q.id}, Topic: {q.topic}, Text: {q.text[:50]}...")
            else:
                print("All questions have audio files!")
    else:
        print("Invalid command. Use 'all', 'question <id>', or 'check'")

if __name__ == "__main__":
    main()



