#!/usr/bin/env python3
"""
Database Initialization Script for OPIc Practice Portal
Creates database with sample questions and admin user
"""

import os
import sys
from datetime import datetime, date
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.models import User, Question, Response, Survey

def create_sample_questions():
    """Create sample questions for testing"""
    print("📝 Creating sample questions...")
    
    sample_questions = [
        # IM Level Questions
        {
            'topic': '01. Newspapers',
            'category': 'Newspapers',
            'language': 'english',
            'text': 'Tell me about newspapers in your country. What kinds of newspapers are popular?',
            'difficulty': 'intermediate',
            'difficulty_level': 'IM',
            'question_type': 'question',
            'audio_url': 'questions/english/IM/01. Newspapers/01_Q1.mp3'
        },
        {
            'topic': '01. Newspapers',
            'category': 'Newspapers',
            'language': 'english',
            'text': 'How often do you read newspapers? What sections do you usually read?',
            'difficulty': 'intermediate',
            'difficulty_level': 'IM',
            'question_type': 'question',
            'audio_url': 'questions/english/IM/01. Newspapers/01_Q2.mp3'
        },
        {
            'topic': '02. Television',
            'category': 'Television',
            'language': 'english',
            'text': 'What types of TV programs do you like to watch? Why do you enjoy them?',
            'difficulty': 'intermediate',
            'difficulty_level': 'IM',
            'question_type': 'question',
            'audio_url': 'questions/english/IM/02. Television/02_Q1.mp3'
        },
        {
            'topic': '03. Internet',
            'category': 'Internet',
            'language': 'english',
            'text': 'How do you use the internet in your daily life? What websites do you visit most often?',
            'difficulty': 'intermediate',
            'difficulty_level': 'IM',
            'question_type': 'question',
            'audio_url': 'questions/english/IM/03. Internet/03_Q1.mp3'
        },
        {
            'topic': '04. Phones + Technology',
            'category': 'Phones + Technology',
            'language': 'english',
            'text': 'Tell me about your mobile phone. What features do you use most often?',
            'difficulty': 'intermediate',
            'difficulty_level': 'IM',
            'question_type': 'question',
            'audio_url': 'questions/english/IM/04. Phones + Technology/04_Q1.mp3'
        },
        
        # IH Level Questions
        {
            'topic': '01. Newspapers',
            'category': 'Newspapers',
            'language': 'english',
            'text': 'Compare online news with traditional newspapers. What are the advantages and disadvantages of each?',
            'difficulty': 'intermediate',
            'difficulty_level': 'IH',
            'question_type': 'question',
            'audio_url': 'questions/english/IH/01. Newspapers/01_Q1.mp3'
        },
        {
            'topic': '02. Television',
            'category': 'Television',
            'language': 'english',
            'text': 'How has television programming changed over the years? What do you think about reality TV shows?',
            'difficulty': 'intermediate',
            'difficulty_level': 'IH',
            'question_type': 'question',
            'audio_url': 'questions/english/IH/02. Television/02_Q1.mp3'
        },
        {
            'topic': '21. Shopping',
            'category': 'Shopping',
            'language': 'english',
            'text': 'Describe your shopping habits. Do you prefer online shopping or going to physical stores?',
            'difficulty': 'intermediate',
            'difficulty_level': 'IH',
            'question_type': 'question',
            'audio_url': 'questions/english/IH/21. Shopping/21_Q1.mp3'
        },
        {
            'topic': '25. Free Time',
            'category': 'Free Time',
            'language': 'english',
            'text': 'How do you usually spend your free time? What hobbies or activities do you enjoy?',
            'difficulty': 'intermediate',
            'difficulty_level': 'IH',
            'question_type': 'question',
            'audio_url': 'questions/english/IH/25. Free Time/25_Q1.mp3'
        },
        {
            'topic': '28. Banks',
            'category': 'Banks',
            'language': 'english',
            'text': 'Tell me about banking in your country. What services do banks typically offer?',
            'difficulty': 'intermediate',
            'difficulty_level': 'IH',
            'question_type': 'question',
            'audio_url': 'questions/english/IH/28. Banks/28_Q1.mp3'
        },
        
        # AL Level Questions
        {
            'topic': '01. Newspapers',
            'category': 'Newspapers',
            'language': 'english',
            'text': 'Analyze the role of newspapers in shaping public opinion. How do they influence society?',
            'difficulty': 'advanced',
            'difficulty_level': 'AL',
            'question_type': 'question',
            'audio_url': 'questions/english/AL/01. Newspapers/01_Q1.mp3'
        },
        {
            'topic': '02. Television',
            'category': 'Television',
            'language': 'english',
            'text': 'Evaluate the impact of television on culture and society. Has it been mostly positive or negative?',
            'difficulty': 'advanced',
            'difficulty_level': 'AL',
            'question_type': 'question',
            'audio_url': 'questions/english/AL/02. Television/02_Q1.mp3'
        },
        {
            'topic': '31. Role Play',
            'category': 'Role Play',
            'language': 'english',
            'text': "I'd like to give you a situation and ask you to act it out. You are at a hotel and need to check in. Go to the front desk and ask three or four questions about your stay.",
            'difficulty': 'advanced',
            'difficulty_level': 'AL',
            'question_type': 'question',
            'audio_url': 'questions/english/AL/31. Role Play/31_Q1.mp3'
        },
        {
            'topic': '32. Messages',
            'category': 'Messages',
            'language': 'english',
            'text': 'Compare different methods of communication (email, phone, text messages). When do you use each one?',
            'difficulty': 'advanced',
            'difficulty_level': 'AL',
            'question_type': 'question',
            'audio_url': 'questions/english/AL/32. Messages/32_Q1.mp3'
        },
        {
            'topic': '15. Bars',
            'category': 'Bars',
            'language': 'english',
            'text': 'Discuss the social aspects of bars and pubs. How do they function in your culture?',
            'difficulty': 'advanced',
            'difficulty_level': 'AL',
            'question_type': 'question',
            'audio_url': 'questions/english/AL/15. Bars/15_Q1.mp3'
        }
    ]
    
    created_count = 0
    for q_data in sample_questions:
        # Check if question already exists
        existing = Question.query.filter_by(
            topic=q_data['topic'],
            text=q_data['text']
        ).first()
        
        if not existing:
            question = Question(**q_data)
            db.session.add(question)
            created_count += 1
    
    db.session.commit()
    print(f"✅ Created {created_count} sample questions")
    return created_count

def create_admin_user():
    """Create admin user"""
    print("👤 Creating admin user...")
    
    # Check if admin user already exists
    admin_user = User.query.filter_by(username='admin').first()
    
    if admin_user:
        print("✅ Admin user already exists")
        return admin_user
    
    admin_user = User(
        username='admin',
        email='admin@opic-portal.com',
        name='Administrator',
        target_language='english',
        streak_count=0,
        last_active_date=date.today(),
        is_admin=True
    )
    admin_user.set_password('1qaz2wsx')
    
    db.session.add(admin_user)
    db.session.commit()
    
    print("✅ Admin user created")
    print("   Username: admin")
    print("   Password: 1qaz2wsx")
    return admin_user

def create_sample_user():
    """Create a sample regular user"""
    print("👤 Creating sample user...")
    
    # Check if sample user already exists
    sample_user = User.query.filter_by(username='testuser').first()
    
    if sample_user:
        print("✅ Sample user already exists")
        return sample_user
    
    sample_user = User(
        username='testuser',
        email='test@example.com',
        name='Test User',
        target_language='english',
        streak_count=5,
        last_active_date=date.today(),
        is_admin=False
    )
    sample_user.set_password('test123')
    
    db.session.add(sample_user)
    db.session.commit()
    
    print("✅ Sample user created")
    print("   Username: testuser")
    print("   Password: test123")
    return sample_user

def create_sample_responses():
    """Create sample responses for testing"""
    print("🎤 Creating sample responses...")
    
    # Get sample user and questions
    sample_user = User.query.filter_by(username='testuser').first()
    if not sample_user:
        print("⚠️  Sample user not found, skipping sample responses")
        return
    
    questions = Question.query.limit(3).all()
    if not questions:
        print("⚠️  No questions found, skipping sample responses")
        return
    
    created_count = 0
    for question in questions:
        # Check if response already exists
        existing = Response.query.filter_by(
            user_id=sample_user.id,
            question_id=question.id
        ).first()
        
        if not existing:
            response = Response(
                user_id=sample_user.id,
                question_id=question.id,
                audio_url=f'responses/sample_response_{question.id}.mp3',
                duration=30 + (question.id % 60)  # Random duration between 30-90 seconds
            )
            db.session.add(response)
            created_count += 1
    
    db.session.commit()
    print(f"✅ Created {created_count} sample responses")

def initialize_database():
    """Initialize the database with sample data"""
    print("🗄️  Initializing database...")
    
    # Create all tables
    db.create_all()
    print("✅ Database tables created")
    
    # Create sample data
    create_admin_user()
    create_sample_user()
    create_sample_questions()
    create_sample_responses()
    
    # Print summary
    print("\n📊 Database Summary:")
    print(f"   Users: {User.query.count()}")
    print(f"   Questions: {Question.query.count()}")
    print(f"   Responses: {Response.query.count()}")
    print(f"   Surveys: {Survey.query.count()}")
    
    print("\n📋 Question Distribution:")
    levels = ['IM', 'IH', 'AL']
    for level in levels:
        count = Question.query.filter_by(difficulty_level=level).count()
        print(f"   {level}: {count} questions")
    
    print("\n🎉 Database initialization completed successfully!")

def main():
    """Main function"""
    print("🚀 OPIc Practice Portal - Database Initialization")
    print("=" * 60)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            initialize_database()
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
