#!/usr/bin/env python3
"""
Database initialization script for OPIc Practice Portal
Creates tables and inserts sample data
"""

import os
import sys
from flask import Flask, current_app
from app import create_app, db
from app.models import User, Question, Response, Survey
from werkzeug.security import generate_password_hash
import shutil
from pathlib import Path

def create_tables():
    """Create all database tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")

def insert_sample_data():
    """Insert sample questions and admin user"""
    app = create_app()
    
    with app.app_context():
        print("Inserting sample data...")
        
        # Create admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@opic-portal.com',
                name='Administrator',
                target_language='english',
                is_admin=True
            )
            # Use environment variable or prompt for password
            import os
            import getpass
            password = os.environ.get('ADMIN_PASSWORD')
            if not password:
                password = getpass.getpass('Enter admin password (min 6 characters): ')
                if len(password) < 6:
                    print('Error: Password must be at least 6 characters long.')
                    return
            admin_user.set_password(password)
            db.session.add(admin_user)
            print("Admin user created (username: admin)")
        
        # If there are external mp3 question files, import them first
        external_root = Path('question_data/voices')
        uploads_root = Path(current_app.config['UPLOAD_FOLDER']) / 'questions'
        if external_root.exists():
            print(f"Importing external question audio from {external_root}...")
            for topic_dir in external_root.iterdir():
                if not topic_dir.is_dir():
                    continue
                topic_name = topic_dir.name.split('.', 1)[-1].strip() if '.' in topic_dir.name else topic_dir.name
                for mp3_path in topic_dir.glob('*.mp3'):
                    # Only import files that look like question prompts (contain '_Q' or end with 'Q*.mp3')
                    if '_Q' not in mp3_path.stem and not mp3_path.stem.endswith('Q'):
                        continue
                    # Create a placeholder text from filename
                    question_text = f"Audio question: {topic_name} - {mp3_path.stem}"
                    existing = Question.query.filter_by(text=question_text, language='english').first()
                    if existing:
                        continue
                    # Copy file to uploads/questions preserving topic subfolder
                    target_dir = uploads_root / 'english' / topic_name
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target_file = target_dir / mp3_path.name
                    if not target_file.exists():
                        shutil.copy2(mp3_path, target_file)
                    rel_url = str(Path('uploads') / 'questions' / 'english' / topic_name / mp3_path.name).replace('\\','/')
                    q = Question(topic=topic_name, language='english', text=question_text, difficulty='intermediate', audio_url='/' + rel_url)
                    db.session.add(q)
            db.session.commit()
            print("External question audio import complete.")

        # Sample questions (fallback/demo)
        sample_questions = [
            # English Questions
            {
                'topic': 'Personal Information',
                'language': 'english',
                'text': 'Tell me about yourself. What do you do for work?',
                'difficulty': 'beginner'
            },
            {
                'topic': 'Personal Information',
                'language': 'english',
                'text': 'Describe your hometown. What makes it special?',
                'difficulty': 'beginner'
            },
            {
                'topic': 'Daily Life',
                'language': 'english',
                'text': 'What is your typical day like? Walk me through your routine.',
                'difficulty': 'intermediate'
            },
            {
                'topic': 'Daily Life',
                'language': 'english',
                'text': 'How do you usually spend your weekends?',
                'difficulty': 'intermediate'
            },
            {
                'topic': 'Travel',
                'language': 'english',
                'text': 'Describe a memorable trip you have taken. What made it special?',
                'difficulty': 'intermediate'
            },
            {
                'topic': 'Travel',
                'language': 'english',
                'text': 'If you could travel anywhere in the world, where would you go and why?',
                'difficulty': 'advanced'
            },
            {
                'topic': 'Work',
                'language': 'english',
                'text': 'What are the main responsibilities in your current job?',
                'difficulty': 'intermediate'
            },
            {
                'topic': 'Work',
                'language': 'english',
                'text': 'Describe a challenging project you worked on recently.',
                'difficulty': 'advanced'
            },
            {
                'topic': 'Hobbies',
                'language': 'english',
                'text': 'What hobbies do you enjoy? How did you get interested in them?',
                'difficulty': 'beginner'
            },
            {
                'topic': 'Hobbies',
                'language': 'english',
                'text': 'If you had unlimited time and resources, what new skill would you like to learn?',
                'difficulty': 'advanced'
            },
            # Korean Questions
            {
                'topic': 'Personal Information',
                'language': 'korean',
                'text': '자기소개를 해주세요. 어떤 일을 하시나요?',
                'difficulty': 'beginner'
            },
            {
                'topic': 'Personal Information',
                'language': 'korean',
                'text': '고향에 대해 설명해주세요. 어떤 점이 특별한가요?',
                'difficulty': 'beginner'
            },
            {
                'topic': 'Daily Life',
                'language': 'korean',
                'text': '평소 하루 일과는 어떻게 되나요?',
                'difficulty': 'intermediate'
            },
            {
                'topic': 'Daily Life',
                'language': 'korean',
                'text': '주말에는 보통 어떻게 보내시나요?',
                'difficulty': 'intermediate'
            },
            {
                'topic': 'Travel',
                'language': 'korean',
                'text': '기억에 남는 여행에 대해 말해주세요. 무엇이 특별했나요?',
                'difficulty': 'intermediate'
            },
            {
                'topic': 'Travel',
                'language': 'korean',
                'text': '세계 어디든 갈 수 있다면 어디로 가고 싶으신가요?',
                'difficulty': 'advanced'
            },
            {
                'topic': 'Work',
                'language': 'korean',
                'text': '현재 직장에서 주된 업무는 무엇인가요?',
                'difficulty': 'intermediate'
            },
            {
                'topic': 'Work',
                'language': 'korean',
                'text': '최근에 작업한 어려운 프로젝트에 대해 설명해주세요.',
                'difficulty': 'advanced'
            },
            {
                'topic': 'Hobbies',
                'language': 'korean',
                'text': '어떤 취미를 즐기시나요? 어떻게 관심을 갖게 되었나요?',
                'difficulty': 'beginner'
            },
            {
                'topic': 'Hobbies',
                'language': 'korean',
                'text': '무제한의 시간과 자원이 있다면 어떤 새로운 기술을 배우고 싶으신가요?',
                'difficulty': 'advanced'
            }
        ]
        
        # Insert questions
        for q_data in sample_questions:
            existing_question = Question.query.filter_by(
                text=q_data['text'],
                language=q_data['language']
            ).first()
            
            if not existing_question:
                question = Question(**q_data)
                db.session.add(question)
        
        db.session.commit()
        print("Sample questions inserted successfully!")
        
        print(f"\nDatabase initialized successfully!")
        print(f"Admin user: admin (password set during initialization)")
        print(f"Total questions: {Question.query.count()}")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        print("Resetting database...")
        app = create_app()
        with app.app_context():
            db.drop_all()
            print("Database dropped")
    
    create_tables()
    insert_sample_data()

if __name__ == "__main__":
    main()