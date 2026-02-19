#!/usr/bin/env python3
"""
Import Vocabulary from ipa-dict
Downloads and imports English words with IPA pronunciation from GitHub
"""

import os
import sys
import requests

# Add project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Load environment
try:
    from dotenv import load_dotenv
    for f in ['config.env', '.env', 'env']:
        p = os.path.join(project_root, f)
        if os.path.exists(p):
            load_dotenv(p)
            break
except ImportError:
    pass

# URLs for ipa-dict data
IPA_DICT_URL = "https://raw.githubusercontent.com/open-dict-data/ipa-dict/master/data/en_US.txt"

# Common words to prioritize (more useful for OPIc practice)
PRIORITY_WORDS = [
    # General vocabulary
    'travel', 'vacation', 'holiday', 'restaurant', 'food', 'movie', 'music',
    'hobby', 'exercise', 'health', 'family', 'friend', 'work', 'job', 'career',
    'school', 'education', 'technology', 'internet', 'phone', 'computer',
    'house', 'apartment', 'neighborhood', 'city', 'country', 'weather',
    'shopping', 'clothes', 'fashion', 'sports', 'game', 'book', 'reading',
    # OPIc specific
    'describe', 'explain', 'compare', 'experience', 'memory', 'favorite',
    'typical', 'usually', 'sometimes', 'always', 'recently', 'nowadays',
    'opinion', 'think', 'believe', 'recommend', 'suggest', 'prefer',
    'change', 'improve', 'develop', 'problem', 'solution', 'challenge',
    # Adjectives
    'beautiful', 'interesting', 'exciting', 'boring', 'convenient', 'comfortable',
    'delicious', 'amazing', 'wonderful', 'terrible', 'difficult', 'easy',
    'popular', 'famous', 'traditional', 'modern', 'different', 'similar',
]


def download_ipa_dict():
    """Download ipa-dict data"""
    print(f"📥 Downloading ipa-dict from GitHub...")
    response = requests.get(IPA_DICT_URL, timeout=60)
    if response.status_code == 200:
        print(f"✅ Downloaded {len(response.text)} characters")
        return response.text
    else:
        print(f"❌ Failed to download: {response.status_code}")
        return None


def is_valid_word(word):
    """Check if word is valid for OPIc vocabulary (not a name or abbreviation)"""
    import re
    
    # Skip if too short
    if len(word) < 3:
        return False
    
    # Skip words with apostrophes (like a's, it's possessives)
    if "'" in word:
        return False
    
    # Skip words with dots (abbreviations)
    if '.' in word:
        return False
    
    # Skip words with numbers
    if any(c.isdigit() for c in word):
        return False
    
    # Skip all uppercase (abbreviations like AAA, ABC)
    if word.isupper() and len(word) <= 5:
        return False
    
    # Skip proper nouns (capitalized words that aren't at start)
    # Names like Aaberg, Aaron, Abdullah
    if word[0].isupper() and word[1:].islower():
        # Check if it's not a common word
        common_start = ['the', 'a', 'an', 'this', 'that', 'i', 'you', 'he', 'she', 'it', 'we', 'they']
        if word.lower() not in common_start:
            return False
    
    # Skip if looks like a name (mixed case patterns)
    if re.match(r'^[A-Z][a-z]+$', word):  # Capitalized like a name
        return False
    
    return True


def parse_ipa_dict(data):
    """Parse ipa-dict format: word\t/IPA/"""
    words = []
    for line in data.strip().split('\n'):
        if '\t' not in line:
            continue
        parts = line.split('\t')
        if len(parts) >= 2:
            word = parts[0].strip()
            ipa = parts[1].strip()
            
            # Use enhanced filtering
            if not is_valid_word(word):
                continue
            
            words.append({
                'word': word.lower(),  # Normalize to lowercase
                'ipa': ipa
            })
    return words


def import_vocabulary(limit=10000, priority_first=True):
    """Import vocabulary into database"""
    from app import create_app, db
    from app.models import Vocabulary
    
    app = create_app()
    
    with app.app_context():
        # Check existing count
        existing = Vocabulary.query.count()
        print(f"📊 Existing vocabulary: {existing}")
        
        if existing > 0:
            print("⏭️ Vocabulary already imported. Use --force to reimport.")
            return
        
        # Download and parse
        data = download_ipa_dict()
        if not data:
            return
        
        words = parse_ipa_dict(data)
        print(f"📝 Parsed {len(words)} words")
        
        # Prioritize common words
        priority_set = set(w.lower() for w in PRIORITY_WORDS)
        priority_words = [w for w in words if w['word'].lower() in priority_set]
        other_words = [w for w in words if w['word'].lower() not in priority_set]
        
        if priority_first:
            words = priority_words + other_words
        
        # Import with limit
        imported = 0
        batch = []
        batch_size = 500
        
        print(f"\n🚀 Importing up to {limit} words...")
        
        for word_data in words[:limit]:
            vocab = Vocabulary(
                word=word_data['word'],
                ipa=word_data['ipa'],
                source='ipa-dict'
            )
            batch.append(vocab)
            
            if len(batch) >= batch_size:
                db.session.add_all(batch)
                db.session.commit()
                imported += len(batch)
                print(f"   Imported {imported} words...")
                batch = []
        
        # Add remaining
        if batch:
            db.session.add_all(batch)
            db.session.commit()
            imported += len(batch)
        
        print(f"\n✅ Successfully imported {imported} words!")
        
        # Show sample
        print("\n📋 Sample vocabulary:")
        samples = Vocabulary.query.limit(5).all()
        for v in samples:
            print(f"   {v.word}: {v.ipa}")


def enrich_with_definitions(limit=100):
    """Enrich vocabulary with definitions from Free Dictionary API"""
    from app import create_app, db
    from app.models import Vocabulary
    import time
    
    app = create_app()
    
    with app.app_context():
        # Get words without definitions
        words = Vocabulary.query.filter(
            Vocabulary.definition.is_(None)
        ).limit(limit).all()
        
        print(f"📚 Enriching {len(words)} words with definitions...")
        
        for i, vocab in enumerate(words):
            try:
                url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{vocab.word}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        entry = data[0]
                        
                        # Get phonetic
                        if 'phonetic' in entry:
                            vocab.ipa = entry['phonetic']
                        
                        # Get audio
                        for phonetic in entry.get('phonetics', []):
                            if phonetic.get('audio'):
                                vocab.audio_url = phonetic['audio']
                                break
                        
                        # Get definition and part of speech
                        for meaning in entry.get('meanings', []):
                            vocab.part_of_speech = meaning.get('partOfSpeech')
                            definitions = meaning.get('definitions', [])
                            if definitions:
                                vocab.definition = definitions[0].get('definition')
                                vocab.example_sentence = definitions[0].get('example')
                            break
                        
                        db.session.commit()
                        print(f"   [{i+1}/{len(words)}] {vocab.word} ✅")
                else:
                    print(f"   [{i+1}/{len(words)}] {vocab.word} ⏭️")
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   [{i+1}/{len(words)}] {vocab.word} ❌ {e}")
        
        print("\n✅ Enrichment complete!")


def cleanup_invalid_words():
    """Remove invalid words from database"""
    from app import create_app
    from app import db
    from app.models import Vocabulary
    
    app = create_app()
    
    with app.app_context():
        # Get all words
        all_words = Vocabulary.query.all()
        print(f"📊 Total words: {len(all_words)}")
        
        deleted = 0
        for vocab in all_words:
            if not is_valid_word(vocab.word):
                db.session.delete(vocab)
                deleted += 1
        
        db.session.commit()
        print(f"🗑️ Deleted {deleted} invalid words")
        print(f"✅ Remaining: {Vocabulary.query.count()} words")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Import vocabulary data')
    parser.add_argument('command', choices=['import', 'enrich', 'stats', 'cleanup'],
                       help='Command to run')
    parser.add_argument('--limit', '-l', type=int, default=5000,
                       help='Limit number of words (default: 5000)')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Force reimport')
    
    args = parser.parse_args()
    
    if args.command == 'import':
        import_vocabulary(limit=args.limit)
    elif args.command == 'enrich':
        enrich_with_definitions(limit=args.limit)
    elif args.command == 'cleanup':
        cleanup_invalid_words()
    elif args.command == 'stats':
        from app import create_app
        from app.models import Vocabulary
        
        app = create_app()
        with app.app_context():
            total = Vocabulary.query.count()
            with_def = Vocabulary.query.filter(Vocabulary.definition.isnot(None)).count()
            with_audio = Vocabulary.query.filter(Vocabulary.audio_url.isnot(None)).count()
            with_topic = Vocabulary.query.filter(Vocabulary.topic.isnot(None)).count()
            print(f"📊 Vocabulary Stats:")
            print(f"   Total words: {total}")
            print(f"   With definitions: {with_def}")
            print(f"   With audio: {with_audio}")
            print(f"   With topics: {with_topic}")
