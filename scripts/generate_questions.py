#!/usr/bin/env python3
"""
Question Generator Script for OPIc Practice Portal
Generates new questions using AI for specified topics and levels
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def get_existing_questions(topic: str, level: str) -> list:
    """Get list of existing question texts for a topic/level"""
    from app.models import Question
    questions = Question.query.filter_by(
        topic=topic,
        difficulty_level=level
    ).all()
    return [q.text for q in questions if q.text]


def generate_questions_for_topic(topic: str, level: str, count: int = 5, 
                                 question_types: list = None):
    """Generate questions for a specific topic and level"""
    from app.services.question_generator import question_generator
    from app.models import Question
    from app import db
    
    if question_types is None:
        question_types = ['general', 'experience', 'comparison', 'roleplay', 'opinion']
    
    print(f"\n📝 Generating {count} questions for {topic} ({level})...")
    
    existing = get_existing_questions(topic, level)
    print(f"   Existing questions: {len(existing)}")
    
    generated = []
    type_index = 0
    
    for i in range(count):
        q_type = question_types[type_index % len(question_types)]
        type_index += 1
        
        print(f"   [{i+1}/{count}] Generating {q_type} question...", end=" ")
        
        result = question_generator.generate_question(
            topic=topic,
            level=level,
            question_type=q_type,
            existing_questions=existing + [q['text'] for q in generated]
        )
        
        if result and result.get('text'):
            # Save to database
            question = question_generator.save_generated_question(
                topic=topic,
                level=level,
                text=result['text'],
                sample_answer=result.get('sample_answer'),
                keywords=result.get('keywords'),
                generation_source='gemini'
            )
            
            if question:
                generated.append({
                    'id': question.id,
                    'text': result['text'],
                    'type': q_type
                })
                print("✅")
            else:
                print("❌ (save failed)")
        else:
            print("❌ (generation failed)")
    
    return generated


def generate_variations_for_topic(topic: str, level: str, max_variations: int = 10):
    """Generate variations for existing questions in a topic"""
    from app.services.question_generator import question_generator
    from app.models import Question
    
    print(f"\n🔄 Generating variations for {topic} ({level})...")
    
    # Get original questions (not already variations)
    originals = Question.query.filter_by(
        topic=topic,
        difficulty_level=level,
        parent_id=None,
        is_generated=False
    ).limit(max_variations).all()
    
    print(f"   Found {len(originals)} original questions")
    
    variation_types = ['rephrase', 'followup', 'perspective', 'timeshift']
    generated = []
    
    for i, original in enumerate(originals):
        if len(generated) >= max_variations:
            break
        
        # Pick a random variation type
        import random
        var_type = random.choice(variation_types)
        
        print(f"   [{i+1}/{len(originals)}] Creating {var_type} variation...", end=" ")
        
        new_text = question_generator.generate_variation(original, var_type)
        
        if new_text:
            question = question_generator.save_generated_question(
                topic=topic,
                level=level,
                text=new_text,
                parent_id=original.id,
                variation_type=var_type,
                generation_source='gemini'
            )
            
            if question:
                generated.append({
                    'id': question.id,
                    'text': new_text,
                    'type': var_type,
                    'parent_id': original.id
                })
                print("✅")
            else:
                print("❌ (save failed)")
        else:
            print("❌ (generation failed)")
    
    return generated


def list_topics():
    """List all available topics grouped by level"""
    from app.models import Question
    from sqlalchemy import func
    from app import db
    
    print("\n📋 Available Topics:\n")
    
    for level in ['IM', 'IH', 'AL']:
        topics = db.session.query(
            Question.topic,
            func.count(Question.id).label('count')
        ).filter_by(
            difficulty_level=level
        ).group_by(Question.topic).order_by(Question.topic).all()
        
        print(f"  {level} Level ({len(topics)} topics):")
        for topic, count in topics:
            print(f"    - {topic}: {count} questions")
        print()


def show_stats():
    """Show question statistics"""
    from app.models import Question
    from sqlalchemy import func
    from app import db
    
    print("\n📊 Question Statistics:\n")
    
    # Overall stats
    total = Question.query.count()
    generated = Question.query.filter_by(is_generated=True).count()
    original = total - generated
    
    print(f"  Total Questions: {total}")
    print(f"  Original: {original}")
    print(f"  AI-Generated: {generated}")
    
    # By level
    print("\n  By Level:")
    for level in ['IM', 'IH', 'AL']:
        count = Question.query.filter_by(difficulty_level=level).count()
        gen_count = Question.query.filter_by(difficulty_level=level, is_generated=True).count()
        print(f"    {level}: {count} ({gen_count} generated)")
    
    # By variation type
    variation_stats = db.session.query(
        Question.variation_type,
        func.count(Question.id)
    ).filter(Question.variation_type.isnot(None)).group_by(Question.variation_type).all()
    
    if variation_stats:
        print("\n  By Variation Type:")
        for var_type, count in variation_stats:
            print(f"    {var_type}: {count}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate OPIc questions using AI')
    parser.add_argument('action', choices=['generate', 'variations', 'list', 'stats'],
                       help='Action to perform')
    parser.add_argument('--topic', '-t', type=str, help='Topic name')
    parser.add_argument('--level', '-l', type=str, choices=['IM', 'IH', 'AL'],
                       help='Difficulty level')
    parser.add_argument('--count', '-c', type=int, default=5,
                       help='Number of questions to generate')
    parser.add_argument('--types', type=str, nargs='+',
                       choices=['general', 'experience', 'comparison', 'roleplay', 'opinion'],
                       help='Question types to generate')
    
    args = parser.parse_args()
    
    # Create Flask app context
    from app import create_app
    app = create_app()
    
    with app.app_context():
        if args.action == 'list':
            list_topics()
        
        elif args.action == 'stats':
            show_stats()
        
        elif args.action == 'generate':
            if not args.topic or not args.level:
                print("❌ Error: --topic and --level are required for 'generate' action")
                sys.exit(1)
            
            generated = generate_questions_for_topic(
                topic=args.topic,
                level=args.level,
                count=args.count,
                question_types=args.types
            )
            
            print(f"\n✅ Generated {len(generated)} questions")
            for q in generated:
                print(f"   [{q['id']}] {q['text'][:60]}...")
        
        elif args.action == 'variations':
            if not args.topic or not args.level:
                print("❌ Error: --topic and --level are required for 'variations' action")
                sys.exit(1)
            
            generated = generate_variations_for_topic(
                topic=args.topic,
                level=args.level,
                max_variations=args.count
            )
            
            print(f"\n✅ Generated {len(generated)} variations")
            for q in generated:
                print(f"   [{q['id']}] ({q['type']}) {q['text'][:50]}...")


if __name__ == "__main__":
    main()
