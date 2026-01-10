#!/usr/bin/env python
"""
Script to auto-generate TTS audio for questions that have text but no voice.
This script scans the database for questions/sample answers missing audio and
generates them using edge-tts.

Usage:
    python scripts/generate_missing_audio.py [options]

Options:
    --scan          Only scan and show what's missing (don't generate)
    --limit N       Limit generation to N items
    --questions     Only generate question audio (not sample answers)
    --answers       Only generate sample answer audio (not questions)
    --topic TOPIC   Only process questions from a specific topic
    --voice VOICE   Voice to use (ava, jenny, guy, aria). Default: ava
"""

import os
import sys
import argparse

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():
    parser = argparse.ArgumentParser(description='Generate missing TTS audio for questions')
    parser.add_argument('--scan', action='store_true', help='Only scan and show missing items')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of items to process')
    parser.add_argument('--questions', action='store_true', help='Only generate question audio')
    parser.add_argument('--answers', action='store_true', help='Only generate sample answer audio')
    parser.add_argument('--topic', type=str, default=None, help='Filter by topic')
    parser.add_argument('--voice', type=str, default='ava', 
                        choices=['ava', 'jenny', 'guy', 'aria'],
                        help='Voice to use for TTS')
    
    args = parser.parse_args()
    
    # Determine what to generate
    generate_questions = True
    generate_sample_answers = True
    
    if args.questions and not args.answers:
        generate_sample_answers = False
    elif args.answers and not args.questions:
        generate_questions = False
    
    # Create Flask app context
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from app.services.tts_service import TTSService
        
        tts = TTSService()
        
        print("=" * 60)
        print("TTS Audio Generator for OPIc Practice Portal")
        print("=" * 60)
        
        if args.scan:
            # Scan only mode
            print("\n🔍 Scanning for questions with missing audio...\n")
            missing = tts.scan_missing_audio(include_sample_answer=True)
            
            print(f"Questions missing audio: {len(missing['questions'])}")
            print(f"Sample answers missing audio: {len(missing['sample_answers'])}")
            print(f"Total missing: {missing['total_missing']}")
            
            if missing['questions']:
                print("\n📌 Questions without audio:")
                for q in missing['questions'][:10]:  # Show first 10
                    print(f"  - ID #{q['id']} | {q['topic']} | {q['level']} | {q['text']}")
                if len(missing['questions']) > 10:
                    print(f"  ... and {len(missing['questions']) - 10} more")
            
            if missing['sample_answers']:
                print("\n📌 Sample answers without audio:")
                for q in missing['sample_answers'][:10]:  # Show first 10
                    print(f"  - ID #{q['id']} | {q['topic']} | {q['level']} | {q['text']}")
                if len(missing['sample_answers']) > 10:
                    print(f"  ... and {len(missing['sample_answers']) - 10} more")
            
            return
        
        # Generation mode
        print(f"\n🎙️ Voice: {args.voice}")
        print(f"📂 Generate questions: {generate_questions}")
        print(f"📂 Generate sample answers: {generate_sample_answers}")
        if args.limit:
            print(f"🔢 Limit: {args.limit}")
        if args.topic:
            print(f"📁 Topic: {args.topic}")
        
        print("\n" + "-" * 60)
        
        def progress_callback(current, total, message):
            percent = (current / total) * 100 if total > 0 else 0
            print(f"[{current}/{total}] {percent:.1f}% - {message}")
        
        if args.topic:
            # Generate for specific topic
            print(f"\n🚀 Starting generation for topic: {args.topic}...\n")
            result = tts.generate_missing_audio_for_topic(
                topic=args.topic,
                voice_key=args.voice,
                generate_questions=generate_questions,
                generate_sample_answers=generate_sample_answers
            )
        else:
            # Generate for all
            print("\n🚀 Starting generation for all missing audio...\n")
            result = tts.generate_missing_audio(
                voice_key=args.voice,
                generate_questions=generate_questions,
                generate_sample_answers=generate_sample_answers,
                limit=args.limit,
                progress_callback=progress_callback
            )
        
        # Print results
        print("\n" + "=" * 60)
        print("📊 RESULTS")
        print("=" * 60)
        print(f"✅ Successfully generated: {result['success_count']}")
        print(f"❌ Failed: {result['failed_count']}")
        print(f"⏭️ Skipped: {result['skipped_count']}")
        
        if result['failed_count'] > 0:
            print("\n⚠️ Failed items:")
            for detail in result['details']:
                if detail['status'] == 'failed':
                    reason = detail.get('reason', 'Unknown error')
                    print(f"  - Question #{detail['question_id']} ({detail['type']}): {reason}")


if __name__ == '__main__':
    main()
