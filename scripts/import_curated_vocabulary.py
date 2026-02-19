#!/usr/bin/env python3
"""
Import curated vocabulary from vocabulary_data.json into the database.

Usage:
  python scripts/import_curated_vocabulary.py fresh    # Clear existing + import all
  python scripts/import_curated_vocabulary.py update   # Update/add without clearing
  python scripts/import_curated_vocabulary.py stats    # Show statistics only
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'vocabulary_data.json')


def load_vocab_data():
    """Load vocabulary data from JSON file."""
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found")
        sys.exit(1)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def show_stats():
    """Show statistics about the vocabulary data."""
    data = load_vocab_data()
    topics = data.get('topics', {})

    print(f"\nVocabulary Data v{data.get('version', '?')}")
    print(f"{'='*50}")

    total_words = 0
    missing_vi = 0
    missing_ko = 0

    for topic_name in sorted(topics.keys()):
        words = topics[topic_name].get('words', [])
        count = len(words)
        total_words += count

        vi_count = sum(1 for w in words if w.get('meaning_vi'))
        ko_count = sum(1 for w in words if w.get('meaning_ko'))
        missing_vi += count - vi_count
        missing_ko += count - ko_count

        vi_status = 'OK' if vi_count == count else f'{vi_count}/{count}'
        ko_status = 'OK' if ko_count == count else f'{ko_count}/{count}'

        print(f"  {topic_name:30s} {count:3d} words  VI:{vi_status:5s}  KO:{ko_status:5s}")

    print(f"{'='*50}")
    print(f"  Total: {total_words} words across {len(topics)} topics")
    if missing_vi:
        print(f"  Missing Vietnamese: {missing_vi}")
    if missing_ko:
        print(f"  Missing Korean: {missing_ko}")


def import_vocabulary(mode='update'):
    """Import vocabulary from JSON into database."""
    from app import create_app
    from app.models import db, Vocabulary

    app = create_app()

    with app.app_context():
        data = load_vocab_data()
        topics = data.get('topics', {})

        if mode == 'fresh':
            count = Vocabulary.query.filter_by(source='curated').count()
            if count > 0:
                print(f"Clearing {count} existing curated words...")
                Vocabulary.query.filter_by(source='curated').delete()
                db.session.commit()

        added = 0
        updated = 0
        skipped = 0

        for topic_name, topic_data in topics.items():
            for word_entry in topic_data.get('words', []):
                word = word_entry['word'].strip().lower()

                existing = Vocabulary.query.filter_by(word=word).first()
                if existing:
                    # Update existing word with new data
                    changed = False
                    if word_entry.get('definition') and existing.definition != word_entry['definition']:
                        existing.definition = word_entry['definition']
                        changed = True
                    if word_entry.get('meaning_vi') and existing.meaning_vi != word_entry.get('meaning_vi'):
                        existing.meaning_vi = word_entry['meaning_vi']
                        changed = True
                    if word_entry.get('meaning_ko') and existing.meaning_ko != word_entry.get('meaning_ko'):
                        existing.meaning_ko = word_entry['meaning_ko']
                        changed = True
                    if word_entry.get('pos') and existing.part_of_speech != word_entry.get('pos'):
                        existing.part_of_speech = word_entry['pos']
                        changed = True
                    if word_entry.get('example') and existing.example_sentence != word_entry.get('example'):
                        existing.example_sentence = word_entry['example']
                        changed = True
                    if existing.topic != topic_name:
                        existing.topic = topic_name
                        changed = True

                    if changed:
                        updated += 1
                    else:
                        skipped += 1
                else:
                    vocab = Vocabulary(
                        word=word,
                        definition=word_entry.get('definition'),
                        meaning_vi=word_entry.get('meaning_vi'),
                        meaning_ko=word_entry.get('meaning_ko'),
                        part_of_speech=word_entry.get('pos'),
                        example_sentence=word_entry.get('example'),
                        topic=topic_name,
                        source='curated'
                    )
                    db.session.add(vocab)
                    added += 1

        db.session.commit()
        print(f"\nImport complete:")
        print(f"  Added:   {added}")
        print(f"  Updated: {updated}")
        print(f"  Skipped: {skipped} (no changes)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_curated_vocabulary.py [fresh|update|stats]")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == 'stats':
        show_stats()
    elif mode in ('fresh', 'update'):
        import_vocabulary(mode)
    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python import_curated_vocabulary.py [fresh|update|stats]")
        sys.exit(1)
