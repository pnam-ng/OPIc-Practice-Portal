import sys
import os
import json
import pandas as pd
from sqlalchemy import func

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Question

def import_questions(file_path):
    app = create_app()
    with app.app_context():
        print(f"Importing questions from {file_path}...")
        
        questions_to_add = []
        
        if file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    questions_to_add = data
                elif isinstance(data, dict) and 'questions' in data:
                    questions_to_add = data['questions']
        
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            questions_to_add = df.to_dict('records')
            
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
            questions_to_add = df.to_dict('records')
            
        else:
            print("Unsupported file format. Use JSON, CSV, or Excel.")
            return

        added_count = 0
        skipped_count = 0
        
        for q_data in questions_to_add:
            # Normalize keys
            topic = q_data.get('topic')
            text = q_data.get('text')
            
            if not topic or not text:
                print(f"Skipping invalid row: {q_data}")
                continue
            
            topic = str(topic).strip()
            text = str(text).strip()

            # Check for duplicates
            exists = Question.query.filter(
                func.lower(Question.text) == text.lower(),
                func.lower(Question.topic) == topic.lower()
            ).first()
            
            if exists:
                print(f"Skipping duplicate: {text[:30]}...")
                skipped_count += 1
                continue
                
            new_q = Question(
                topic=topic,
                text=text,
                language=str(q_data.get('language', 'english')).lower(),
                difficulty_level=str(q_data.get('difficulty_level', 'IM')).upper(),
                question_type=str(q_data.get('question_type', 'question')).lower(),
                audio_url=q_data.get('audio_url'),
                sample_answer_text=q_data.get('sample_answer_text'),
                sample_answer_audio_url=q_data.get('sample_answer_audio_url')
            )
            db.session.add(new_q)
            added_count += 1
            
        try:
            db.session.commit()
            print(f"Successfully imported {added_count} questions. Skipped {skipped_count} duplicates.")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to database: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_questions.py <file_path>")
    else:
        import_questions(sys.argv[1])
