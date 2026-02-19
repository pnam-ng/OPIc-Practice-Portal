#!/usr/bin/env python3
"""
Assign OPIc topics to vocabulary words
Maps words to topics based on keyword patterns
"""

import os
import sys

# Add project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# OPIc Topic -> Related Keywords mapping
# These topics match the existing question topics in the system
TOPIC_KEYWORDS = {
    # Housing topics
    'Housing': [
        'house', 'apartment', 'room', 'kitchen', 'bathroom', 'bedroom', 'living',
        'neighbor', 'neighborhood', 'rent', 'move', 'decorate', 'cozy',
        'comfortable', 'spacious', 'building', 'floor', 'balcony', 'garden',
        'home', 'residence', 'landlord', 'tenant', 'lease'
    ],
    'Furniture': [
        'furniture', 'sofa', 'couch', 'chair', 'table', 'desk', 'bed', 'cabinet',
        'shelf', 'drawer', 'wardrobe', 'closet', 'lamp', 'carpet', 'curtain',
        'mattress', 'pillow', 'blanket', 'mirror', 'decoration'
    ],
    
    # Food & Drink topics
    'Food': [
        'food', 'eat', 'cook', 'meal', 'breakfast', 'lunch', 'dinner',
        'delicious', 'tasty', 'dish', 'cuisine', 'hungry', 'appetite',
        'recipe', 'ingredient', 'vegetable', 'fruit', 'meat', 'snack'
    ],
    'Restaurants': [
        'restaurant', 'dine', 'dining', 'waiter', 'waitress', 'menu', 'order',
        'serve', 'chef', 'reservation', 'tip', 'course', 'appetizer', 'dessert'
    ],
    'Bars': [
        'bar', 'drink', 'beverage', 'alcohol', 'beer', 'wine', 'cocktail',
        'pub', 'nightclub', 'bartender', 'pour', 'toast'
    ],
    'Coffee shop': [
        'coffee', 'cafe', 'espresso', 'latte', 'cappuccino', 'tea', 'barista',
        'brew', 'caffeine', 'roast', 'blend'
    ],
    
    # Entertainment topics
    'Music': [
        'music', 'song', 'sing', 'singer', 'band', 'concert', 'album',
        'melody', 'rhythm', 'beat', 'genre', 'instrument', 'guitar', 'piano',
        'drum', 'listen', 'playlist', 'headphone', 'speaker'
    ],
    'Movies': [
        'movie', 'film', 'cinema', 'theater', 'actor', 'actress', 'director',
        'scene', 'plot', 'character', 'genre', 'comedy', 'drama', 'action',
        'horror', 'documentary', 'screen', 'premiere', 'subtitle'
    ],
    'Television': [
        'television', 'show', 'series', 'episode', 'channel', 'broadcast',
        'stream', 'news', 'program', 'commercial', 'remote', 'binge'
    ],
    
    # Technology topics
    'Internet': [
        'internet', 'online', 'website', 'browse', 'search', 'download',
        'upload', 'wifi', 'connection', 'network', 'social', 'media',
        'streaming', 'email', 'blog', 'viral', 'trending'
    ],
    'Phones + Technology': [
        'phone', 'smartphone', 'mobile', 'computer', 'laptop', 'tablet',
        'device', 'app', 'application', 'software', 'hardware', 'screen',
        'keyboard', 'technology', 'digital', 'gadget', 'battery', 'charger'
    ],
    
    # Health & Fitness topics
    'Health': [
        'health', 'healthy', 'doctor', 'hospital', 'medicine', 'sick',
        'illness', 'symptom', 'treatment', 'cure', 'pain', 'injury',
        'checkup', 'prescription', 'pharmacy', 'nurse', 'clinic'
    ],
    
    # Travel topics
    'Vacation': [
        'vacation', 'holiday', 'trip', 'travel', 'tour', 'tourist',
        'destination', 'resort', 'relax', 'leisure', 'getaway', 'escape'
    ],
    'Domestic Trips': [
        'domestic', 'local', 'countryside', 'province', 'city', 'town',
        'village', 'region', 'area', 'explore', 'discover'
    ],
    'Oversea Trips': [
        'overseas', 'abroad', 'international', 'foreign', 'passport',
        'visa', 'customs', 'flight', 'airport', 'luggage', 'immigration'
    ],
    'Hotels': [
        'hotel', 'motel', 'hostel', 'accommodation', 'reservation', 'booking',
        'check-in', 'check-out', 'lobby', 'reception', 'room', 'suite'
    ],
    
    # Outdoor topics
    'Park': [
        'park', 'garden', 'outdoor', 'nature', 'tree', 'flower', 'grass',
        'bench', 'fountain', 'picnic', 'playground', 'path', 'trail'
    ],
    'Geography': [
        'geography', 'mountain', 'river', 'lake', 'ocean', 'sea', 'beach',
        'island', 'forest', 'desert', 'valley', 'landscape', 'terrain'
    ],
    
    # Daily life topics
    'Shopping': [
        'shop', 'shopping', 'buy', 'purchase', 'store', 'mall', 'market',
        'price', 'expensive', 'cheap', 'discount', 'sale', 'bargain',
        'customer', 'cashier', 'receipt', 'refund', 'exchange'
    ],
    'Fashion': [
        'fashion', 'clothes', 'clothing', 'wear', 'outfit', 'style', 'trend',
        'brand', 'designer', 'shirt', 'pants', 'dress', 'suit', 'jacket',
        'shoes', 'accessories', 'jewelry', 'hat', 'bag'
    ],
    'Banks': [
        'bank', 'money', 'account', 'savings', 'deposit', 'withdraw',
        'transfer', 'loan', 'credit', 'debit', 'interest', 'atm', 'transaction'
    ],
    
    # Work & Social topics
    'Work': [
        'work', 'job', 'office', 'company', 'business', 'career', 'profession',
        'employee', 'employer', 'boss', 'manager', 'colleague', 'coworker',
        'meeting', 'project', 'deadline', 'salary', 'promotion'
    ],
    'Gatherings': [
        'gathering', 'party', 'celebration', 'event', 'occasion', 'invite',
        'guest', 'host', 'socialize', 'mingle', 'network'
    ],
    'Family and Friends': [
        'family', 'friend', 'relative', 'parent', 'child', 'sibling',
        'spouse', 'partner', 'relationship', 'bond', 'together'
    ],
    
    # Weather & Transport topics
    'Weather': [
        'weather', 'rain', 'sun', 'sunny', 'cloud', 'cloudy', 'snow', 'wind',
        'windy', 'hot', 'cold', 'warm', 'cool', 'temperature', 'humid',
        'storm', 'forecast', 'season', 'spring', 'summer', 'autumn', 'winter'
    ],
    'Transportation': [
        'transportation', 'transport', 'car', 'bus', 'train', 'subway', 'taxi',
        'drive', 'ride', 'bike', 'bicycle', 'traffic', 'road', 'street',
        'commute', 'vehicle', 'station', 'ticket', 'route', 'parking'
    ],
    
    # Free time & Hobbies
    'Free Time': [
        'hobby', 'leisure', 'pastime', 'recreation', 'relax', 'enjoy', 'fun',
        'read', 'book', 'game', 'sport', 'exercise', 'gym', 'fitness',
        'yoga', 'swim', 'run', 'walk', 'hike', 'camp'
    ],
    'Holidays': [
        'holiday', 'celebrate', 'celebration', 'festival', 'tradition',
        'custom', 'anniversary', 'birthday', 'christmas', 'thanksgiving'
    ]
}


def assign_topics():
    """Assign topics to vocabulary words based on keyword matching"""
    from app import create_app
    from app import db
    from app.models import Vocabulary
    
    app = create_app()
    
    with app.app_context():
        # Get all vocabulary without topics
        words = Vocabulary.query.filter(
            (Vocabulary.topic.is_(None)) | (Vocabulary.topic == '')
        ).all()
        
        print(f"📚 Found {len(words)} words without topics")
        
        # Create reverse mapping: keyword -> topic
        keyword_to_topic = {}
        for topic, keywords in TOPIC_KEYWORDS.items():
            for keyword in keywords:
                keyword_to_topic[keyword.lower()] = topic
        
        # Assign topics
        assigned = 0
        for vocab in words:
            word = vocab.word.lower()
            
            # Check if word matches any keyword
            if word in keyword_to_topic:
                vocab.topic = keyword_to_topic[word]
                assigned += 1
                continue
            
            # Check if word contains any keyword
            for keyword, topic in keyword_to_topic.items():
                if keyword in word or word in keyword:
                    vocab.topic = topic
                    assigned += 1
                    break
        
        db.session.commit()
        print(f"✅ Assigned topics to {assigned} words")
        
        # Print topic distribution
        print("\n📊 Topic distribution:")
        for topic in TOPIC_KEYWORDS.keys():
            count = Vocabulary.query.filter_by(topic=topic).count()
            if count > 0:
                print(f"   {topic}: {count}")
        
        no_topic = Vocabulary.query.filter(
            (Vocabulary.topic.is_(None)) | (Vocabulary.topic == '')
        ).count()
        print(f"   (No topic): {no_topic}")


def add_curated_vocabulary():
    """Add curated vocabulary for each topic"""
    from app import create_app
    from app import db
    from app.models import Vocabulary
    
    app = create_app()
    
    # Curated vocabulary with definitions - matching system topics
    CURATED_VOCAB = {
        'Housing': [
            ('apartment', 'a residence in a building', 'noun'),
            ('neighborhood', 'a district or community', 'noun'),
            ('spacious', 'having ample space', 'adjective'),
            ('cozy', 'comfortable and warm', 'adjective'),
        ],
        'Furniture': [
            ('sofa', 'a long upholstered seat', 'noun'),
            ('cabinet', 'a piece of furniture with shelves', 'noun'),
            ('comfortable', 'providing physical ease', 'adjective'),
        ],
        'Food': [
            ('delicious', 'highly pleasant to taste', 'adjective'),
            ('cuisine', 'a style of cooking', 'noun'),
            ('ingredient', 'a component of a recipe', 'noun'),
        ],
        'Restaurants': [
            ('reservation', 'an arrangement to book a table', 'noun'),
            ('appetizer', 'a small dish before a meal', 'noun'),
            ('waiter', 'a person who serves food', 'noun'),
        ],
        'Music': [
            ('melody', 'a sequence of musical notes', 'noun'),
            ('rhythm', 'a pattern of sounds', 'noun'),
            ('concert', 'a musical performance', 'noun'),
        ],
        'Movies': [
            ('director', 'a person who directs a film', 'noun'),
            ('plot', 'the main story of a film', 'noun'),
            ('premiere', 'the first showing of a film', 'noun'),
        ],
        'Internet': [
            ('browse', 'to look through information', 'verb'),
            ('streaming', 'transmitting data continuously', 'noun'),
            ('viral', 'spreading rapidly online', 'adjective'),
        ],
        'Phones + Technology': [
            ('application', 'a program for a specific task', 'noun'),
            ('efficient', 'achieving maximum productivity', 'adjective'),
            ('innovative', 'featuring new methods or ideas', 'adjective'),
        ],
        'Health': [
            ('symptom', 'a sign of a condition', 'noun'),
            ('treatment', 'medical care for illness', 'noun'),
            ('prescription', 'a doctor\'s written order', 'noun'),
        ],
        'Vacation': [
            ('destination', 'the place to which someone is going', 'noun'),
            ('relaxation', 'a state of being free from tension', 'noun'),
            ('memorable', 'worth remembering', 'adjective'),
        ],
        'Shopping': [
            ('discount', 'a reduction in price', 'noun'),
            ('bargain', 'a good deal', 'noun'),
            ('purchase', 'to buy something', 'verb'),
        ],
        'Work': [
            ('deadline', 'the latest time for completion', 'noun'),
            ('colleague', 'a person you work with', 'noun'),
            ('promotion', 'advancement to a higher position', 'noun'),
        ],
        'Weather': [
            ('forecast', 'a prediction of weather', 'noun'),
            ('temperature', 'the degree of heat or cold', 'noun'),
            ('humid', 'having high moisture in the air', 'adjective'),
        ],
        'Transportation': [
            ('commute', 'regular travel between home and work', 'noun'),
            ('traffic', 'vehicles moving on a road', 'noun'),
            ('convenient', 'easy to access or use', 'adjective'),
        ],
        'Free Time': [
            ('leisure', 'time free from work', 'noun'),
            ('recreation', 'activity for enjoyment', 'noun'),
            ('hobby', 'an activity done for pleasure', 'noun'),
        ],
    }
    
    with app.app_context():
        added = 0
        for topic, words in CURATED_VOCAB.items():
            for word, definition, pos in words:
                existing = Vocabulary.query.filter_by(word=word.lower()).first()
                if not existing:
                    vocab = Vocabulary(
                        word=word.lower(),
                        definition=definition,
                        part_of_speech=pos,
                        topic=topic,
                        source='curated'
                    )
                    db.session.add(vocab)
                    added += 1
                elif not existing.topic:
                    existing.topic = topic
                    existing.definition = existing.definition or definition
                    existing.part_of_speech = existing.part_of_speech or pos
        
        db.session.commit()
        print(f"✅ Added/updated {added} curated words")


def reset_topics():
    """Reset all vocabulary topics to null"""
    from app import create_app
    from app import db
    from app.models import Vocabulary
    
    app = create_app()
    
    with app.app_context():
        count = Vocabulary.query.filter(Vocabulary.topic.isnot(None)).count()
        Vocabulary.query.update({Vocabulary.topic: None})
        db.session.commit()
        print(f"🔄 Reset topics for {count} words")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Assign topics to vocabulary')
    parser.add_argument('command', choices=['assign', 'curated', 'all', 'reset', 'resync'],
                       help='Command to run')
    
    args = parser.parse_args()
    
    if args.command == 'assign':
        assign_topics()
    elif args.command == 'curated':
        add_curated_vocabulary()
    elif args.command == 'all':
        add_curated_vocabulary()
        assign_topics()
    elif args.command == 'reset':
        reset_topics()
    elif args.command == 'resync':
        # Full resync: reset + curated + assign
        reset_topics()
        add_curated_vocabulary()
        assign_topics()
