#!/usr/bin/env python3
"""
Batch Question Generator - Generate questions for all topics
Exports to both database and JSON file for reuse
"""

import os
import sys
import time
import json
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Load environment variables from env file
try:
    from dotenv import load_dotenv
    env_files = ['config.env', '.env', 'env']
    for env_file in env_files:
        env_path = os.path.join(project_root, env_file)
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"[OK] Loaded environment from: {env_file}")
            break
except ImportError:
    print("[WARN] python-dotenv not installed, using system environment")



def generate_for_all_topics(questions_per_topic=3, include_variations=True, export_json=True):
    """Generate questions for all topics across all levels"""
    from app import create_app, db
    from app.models import Question
    from app.services.question_generator import QuestionGeneratorService
    from sqlalchemy import func
    
    app = create_app()
    
    with app.app_context():
        generator = QuestionGeneratorService()
        
        # Get all unique topic/level combinations
        topic_levels = db.session.query(
            Question.topic,
            Question.difficulty_level,
            func.count(Question.id).label('count')
        ).group_by(
            Question.topic,
            Question.difficulty_level
        ).order_by(
            Question.difficulty_level,
            Question.topic
        ).all()
        
        print(f"\n🚀 Batch Question Generation")
        print(f"=" * 60)
        print(f"📊 Found {len(topic_levels)} topic/level combinations")
        print(f"🎯 Generating {questions_per_topic} questions per topic")
        if include_variations:
            print(f"🔄 Also generating 1 variation per topic")
        if export_json:
            print(f"💾 Will export to JSON file")
        print(f"=" * 60)
        
        total_generated = 0
        total_variations = 0
        failed_topics = []
        
        # JSON export data
        json_data = {
            'generated_at': datetime.now().isoformat(),
            'questions_per_topic': questions_per_topic,
            'questions': []
        }
        
        for i, (topic, level, existing_count) in enumerate(topic_levels):
            print(f"\n[{i+1}/{len(topic_levels)}] {topic} ({level}) - {existing_count} existing")
            
            # Get existing question texts
            existing_questions = Question.query.filter_by(
                topic=topic,
                difficulty_level=level
            ).all()
            existing_texts = [q.text for q in existing_questions if q.text]
            
            # Generate new questions
            question_types = ['general', 'experience', 'comparison', 'roleplay', 'opinion']
            generated_count = 0
            
            for j in range(questions_per_topic):
                q_type = question_types[j % len(question_types)]
                print(f"   [{j+1}/{questions_per_topic}] Generating {q_type}...", end=" ", flush=True)
                
                try:
                    result = generator.generate_question(
                        topic=topic,
                        level=level,
                        question_type=q_type,
                        existing_questions=existing_texts
                    )
                    
                    if result and result.get('text'):
                        # Save to database
                        question = generator.save_generated_question(
                            topic=topic,
                            level=level,
                            text=result['text'],
                            sample_answer=result.get('sample_answer'),
                            keywords=result.get('keywords'),
                            generation_source='ai'
                        )
                        
                        if question:
                            print("✅")
                            generated_count += 1
                            existing_texts.append(result['text'])
                            
                            # Add to JSON export
                            json_data['questions'].append({
                                'id': question.id,
                                'topic': topic,
                                'difficulty_level': level,
                                'question_type': q_type,
                                'text': result['text'],
                                'sample_answer': result.get('sample_answer', ''),
                                'keywords': result.get('keywords', []),
                                'is_generated': True,
                                'generation_source': 'ai'
                            })
                        else:
                            print("❌ (save failed)")
                    else:
                        print("❌ (generation failed)")
                        
                except Exception as e:
                    print(f"❌ (error: {str(e)[:50]})")
                
                # Rate limiting - wait 1 second between API calls
                time.sleep(1)
            
            total_generated += generated_count
            
            # Generate 1 variation for this topic
            if include_variations and existing_questions:
                print(f"   [VAR] Creating variation...", end=" ", flush=True)
                try:
                    import random
                    originals = [q for q in existing_questions if q.text and not q.is_generated]
                    if originals:
                        original = random.choice(originals)
                        var_type = random.choice(['rephrase', 'followup', 'perspective', 'timeshift'])
                        new_text = generator.generate_variation(original, var_type)
                        
                        if new_text:
                            question = generator.save_generated_question(
                                topic=topic,
                                level=level,
                                text=new_text,
                                parent_id=original.id,
                                variation_type=var_type,
                                generation_source='ai'
                            )
                            if question:
                                print(f"✅ ({var_type})")
                                total_variations += 1
                                
                                # Add to JSON export
                                json_data['questions'].append({
                                    'id': question.id,
                                    'topic': topic,
                                    'difficulty_level': level,
                                    'question_type': 'variation',
                                    'variation_type': var_type,
                                    'parent_id': original.id,
                                    'text': new_text,
                                    'is_generated': True,
                                    'generation_source': 'ai'
                                })
                            else:
                                print("❌")
                        else:
                            print("❌")
                    else:
                        print("⏭️ (no original questions)")
                        
                except Exception as e:
                    print(f"❌ (error)")
                
                time.sleep(1)
            
            if generated_count == 0:
                failed_topics.append(f"{topic} ({level})")
        
        # Export to JSON
        if export_json and json_data['questions']:
            export_dir = os.path.join(project_root, 'data', 'generated_questions')
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            json_path = os.path.join(export_dir, f'questions_{timestamp}.json')
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Exported to: {json_path}")
        
        # Summary
        print(f"\n" + "=" * 60)
        print(f"📊 SUMMARY")
        print(f"=" * 60)
        print(f"✅ New questions generated: {total_generated}")
        print(f"🔄 Variations generated: {total_variations}")
        print(f"📝 Total new content: {total_generated + total_variations}")
        
        if failed_topics:
            print(f"\n⚠️ Failed topics ({len(failed_topics)}):")
            for topic in failed_topics[:10]:
                print(f"   - {topic}")
        
        # Show new totals
        new_total = Question.query.count()
        generated_total = Question.query.filter_by(is_generated=True).count()
        print(f"\n📈 Database now has:")
        print(f"   Total questions: {new_total}")
        print(f"   AI-generated: {generated_total}")
        
        return json_data


def import_from_json(json_path):
    """Import questions from a JSON file"""
    from app import create_app, db
    from app.models import Question
    
    app = create_app()
    
    with app.app_context():
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        imported = 0
        skipped = 0
        
        print(f"\n📥 Importing from: {json_path}")
        print(f"   Questions in file: {len(data.get('questions', []))}")
        
        for q in data.get('questions', []):
            # Check if question already exists (by text)
            existing = Question.query.filter_by(text=q['text']).first()
            if existing:
                skipped += 1
                continue
            
            question = Question(
                topic=q['topic'],
                difficulty_level=q['difficulty_level'],
                text=q['text'],
                sample_answer_text=q.get('sample_answer', ''),
                keywords=q.get('keywords', []),
                is_generated=q.get('is_generated', True),
                generation_source=q.get('generation_source', 'json_import'),
                parent_id=q.get('parent_id'),
                variation_type=q.get('variation_type'),
                language='english',
                question_type='question'
            )
            db.session.add(question)
            imported += 1
        
        db.session.commit()
        
        print(f"\n✅ Imported: {imported}")
        print(f"⏭️ Skipped (duplicates): {skipped}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch generate/import questions')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate new questions')
    gen_parser.add_argument('--count', '-c', type=int, default=3, 
                           help='Questions per topic (default: 3)')
    gen_parser.add_argument('--no-variations', action='store_true',
                           help='Skip generating variations')
    gen_parser.add_argument('--no-json', action='store_true',
                           help='Skip JSON export')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import questions from JSON')
    import_parser.add_argument('file', help='Path to JSON file')
    
    args = parser.parse_args()
    
    if args.command == 'generate' or args.command is None:
        generate_for_all_topics(
            questions_per_topic=getattr(args, 'count', 3),
            include_variations=not getattr(args, 'no_variations', False),
            export_json=not getattr(args, 'no_json', False)
        )
    elif args.command == 'import':
        import_from_json(args.file)

