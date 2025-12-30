
import sys
import os

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Question

app = create_app()

with app.app_context():
    print("--- Database Debug: Questions ---")
    total_questions = Question.query.count()
    print(f"Total Questions: {total_questions}")
    
    print("\n--- Difficulty Levels ---")
    levels = db.session.query(Question.difficulty_level, db.func.count(Question.id))\
        .group_by(Question.difficulty_level).all()
    
    for level, count in levels:
        print(f"Level '{level}': {count} questions")
        
    print("\n--- Topics by Level ---")
    # check a few common levels like IM, IH, AL
    for target_level in ['IM', 'IH', 'AL', 'NM', 'NH']:
        topics = db.session.query(Question.topic)\
            .filter(Question.difficulty_level == target_level)\
            .distinct().all()
        clean_topics = [t[0] for t in topics if t[0]]
        print(f"Level '{target_level}' Topics ({len(clean_topics)}): {clean_topics[:5]}...")

    print("\n--- First 5 Questions Sample ---")
    questions = Question.query.limit(5).all()
    for q in questions:
        print(f"ID: {q.id}, Topic: {q.topic}, Level: {q.difficulty_level}, Lang: {q.language}")
