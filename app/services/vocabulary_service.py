"""
Vocabulary Service - Business logic for vocabulary feature
Includes Free Dictionary API integration and spaced repetition
"""

import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from flask import current_app
from app import db
from app.models import Vocabulary, UserVocabulary, WordOfDay


class VocabularyService:
    """Service for vocabulary operations"""
    
    FREE_DICT_API = "https://api.dictionaryapi.dev/api/v2/entries/en"
    
    def __init__(self):
        self.cache = {}  # Simple in-memory cache
    
    # ==================== Word Lookup ====================
    
    def lookup_word(self, word: str) -> Optional[Dict]:
        """
        Look up word from Free Dictionary API
        Returns definition, IPA, audio URL, examples
        """
        word = word.lower().strip()
        
        # Check cache
        if word in self.cache:
            return self.cache[word]
        
        try:
            response = requests.get(
                f"{self.FREE_DICT_API}/{word}",
                timeout=10
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            if not data or len(data) == 0:
                return None
            
            entry = data[0]
            result = {
                'word': entry.get('word', word),
                'ipa': entry.get('phonetic', ''),
                'audio_url': None,
                'definitions': [],
            }
            
            # Get audio URL
            for phonetic in entry.get('phonetics', []):
                if phonetic.get('audio'):
                    result['audio_url'] = phonetic['audio']
                    if not result['ipa'] and phonetic.get('text'):
                        result['ipa'] = phonetic['text']
                    break
            
            # Get definitions by part of speech
            for meaning in entry.get('meanings', []):
                pos = meaning.get('partOfSpeech', '')
                for defn in meaning.get('definitions', [])[:2]:
                    result['definitions'].append({
                        'part_of_speech': pos,
                        'definition': defn.get('definition', ''),
                        'example': defn.get('example', '')
                    })
            
            # Cache result
            self.cache[word] = result
            return result
            
        except Exception as e:
            current_app.logger.error(f"Dictionary API error: {e}")
            return None
    
    # ==================== Vocabulary CRUD ====================
    
    def get_vocabulary(self, topic: str = None, pos: str = None, 
                       search: str = None, limit: int = 50, offset: int = 0,
                       topic_only: bool = True) -> List[Vocabulary]:
        """Get vocabulary list with filters. By default only shows words with topics."""
        query = Vocabulary.query
        
        if topic:
            query = query.filter(Vocabulary.topic == topic)
        elif topic_only:
            # Only show words that have a topic assigned
            query = query.filter(Vocabulary.topic.isnot(None))
        
        if pos:
            query = query.filter(Vocabulary.part_of_speech == pos)
        
        if search:
            query = query.filter(Vocabulary.word.ilike(f"%{search}%"))
        
        # Order by: words with definitions first, then alphabetically
        return query.order_by(
            Vocabulary.definition.isnot(None).desc(),
            Vocabulary.word
        ).offset(offset).limit(limit).all()
    
    def get_word_by_id(self, vocab_id: int) -> Optional[Vocabulary]:
        """Get single vocabulary by ID"""
        return Vocabulary.query.get(vocab_id)
    
    def search_vocabulary(self, query: str, limit: int = 20) -> List[Vocabulary]:
        """Search vocabulary by word"""
        return Vocabulary.query.filter(
            Vocabulary.word.ilike(f"%{query}%")
        ).limit(limit).all()
    
    def add_vocabulary(self, word: str, ipa: str = None, definition: str = None,
                       part_of_speech: str = None, topic: str = None,
                       meaning_vi: str = None, meaning_ko: str = None) -> Optional[Vocabulary]:
        """Add new vocabulary word"""
        # Check if exists
        existing = Vocabulary.query.filter_by(word=word.lower()).first()
        if existing:
            return existing
        
        # Lookup if no IPA provided
        if not ipa or not definition:
            lookup = self.lookup_word(word)
            if lookup:
                ipa = ipa or lookup.get('ipa')
                if lookup.get('definitions'):
                    definition = definition or lookup['definitions'][0].get('definition')
                    part_of_speech = part_of_speech or lookup['definitions'][0].get('part_of_speech')
        
        vocab = Vocabulary(
            word=word.lower(),
            ipa=ipa,
            definition=definition,
            meaning_vi=meaning_vi,
            meaning_ko=meaning_ko,
            part_of_speech=part_of_speech,
            topic=topic
        )
        db.session.add(vocab)
        db.session.commit()
        return vocab
    
    # ==================== User Vocabulary ====================
    
    def get_user_vocabulary(self, user_id: int, status: str = None,
                            favorites_only: bool = False) -> List[UserVocabulary]:
        """Get user's vocabulary list"""
        query = UserVocabulary.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if favorites_only:
            query = query.filter_by(is_favorite=True)
        
        return query.order_by(UserVocabulary.created_at.desc()).all()
    
    def add_to_user_vocabulary(self, user_id: int, vocabulary_id: int) -> Optional[UserVocabulary]:
        """Add word to user's vocabulary list"""
        # Check existing
        existing = UserVocabulary.query.filter_by(
            user_id=user_id, vocabulary_id=vocabulary_id
        ).first()
        
        if existing:
            return existing
        
        user_vocab = UserVocabulary(
            user_id=user_id,
            vocabulary_id=vocabulary_id,
            status='new'
        )
        db.session.add(user_vocab)
        db.session.commit()
        return user_vocab
    
    def toggle_favorite(self, user_id: int, vocabulary_id: int) -> bool:
        """Toggle favorite status for a word"""
        user_vocab = UserVocabulary.query.filter_by(
            user_id=user_id, vocabulary_id=vocabulary_id
        ).first()
        
        if not user_vocab:
            # Create new entry with favorite
            user_vocab = UserVocabulary(
                user_id=user_id,
                vocabulary_id=vocabulary_id,
                is_favorite=True,
                status='new'
            )
            db.session.add(user_vocab)
        else:
            user_vocab.is_favorite = not user_vocab.is_favorite
        
        db.session.commit()
        return user_vocab.is_favorite
    
    def update_last_viewed(self, user_id: int, vocabulary_id: int):
        """Update last viewed timestamp"""
        user_vocab = UserVocabulary.query.filter_by(
            user_id=user_id, vocabulary_id=vocabulary_id
        ).first()
        
        if user_vocab:
            user_vocab.last_viewed_at = datetime.utcnow()
            db.session.commit()
    
    # ==================== Spaced Repetition ====================
    
    def get_due_reviews(self, user_id: int, limit: int = 10) -> List[UserVocabulary]:
        """Get words due for review (spaced repetition)"""
        now = datetime.utcnow()
        return UserVocabulary.query.filter(
            UserVocabulary.user_id == user_id,
            UserVocabulary.status != 'mastered',
            (UserVocabulary.next_review <= now) | (UserVocabulary.next_review.is_(None))
        ).order_by(UserVocabulary.next_review).limit(limit).all()
    
    def record_review(self, user_id: int, vocabulary_id: int, correct: bool) -> UserVocabulary:
        """Record review result and calculate next review date"""
        user_vocab = UserVocabulary.query.filter_by(
            user_id=user_id, vocabulary_id=vocabulary_id
        ).first()
        
        if not user_vocab:
            user_vocab = self.add_to_user_vocabulary(user_id, vocabulary_id)
        
        user_vocab.review_count += 1
        if correct:
            user_vocab.correct_count += 1
        
        # Calculate next review (simple spaced repetition)
        # Intervals: 1 day, 3 days, 7 days, 14 days, 30 days
        intervals = [1, 3, 7, 14, 30]
        correct_streak = user_vocab.correct_count
        
        if correct:
            interval_idx = min(correct_streak - 1, len(intervals) - 1)
            days = intervals[max(0, interval_idx)]
            user_vocab.next_review = datetime.utcnow() + timedelta(days=days)
            
            # Update status
            if correct_streak >= 5:
                user_vocab.status = 'mastered'
            elif correct_streak >= 2:
                user_vocab.status = 'learning'
        else:
            # Reset on incorrect
            user_vocab.next_review = datetime.utcnow() + timedelta(hours=1)
            user_vocab.status = 'learning'
        
        db.session.commit()
        return user_vocab
    
    # ==================== Word of the Day ====================
    
    def get_word_of_day(self) -> Optional[Dict]:
        """Get today's word of the day"""
        wod = WordOfDay.get_today()
        if wod:
            return wod.to_dict()
        return None
    
    # ==================== Topic Mapping ====================
    
    def get_topics(self) -> List[str]:
        """Get list of vocabulary topics"""
        topics = db.session.query(Vocabulary.topic).distinct().filter(
            Vocabulary.topic.isnot(None)
        ).all()
        return [t[0] for t in topics if t[0]]
    
    def get_stats(self, user_id: int = None) -> Dict:
        """Get vocabulary statistics"""
        stats = {
            'total_words': Vocabulary.query.count(),
            'with_definitions': Vocabulary.query.filter(
                Vocabulary.definition.isnot(None)
            ).count(),
            'with_audio': Vocabulary.query.filter(
                Vocabulary.audio_url.isnot(None)
            ).count()
        }
        
        if user_id:
            stats['user_total'] = UserVocabulary.query.filter_by(user_id=user_id).count()
            stats['user_favorites'] = UserVocabulary.query.filter_by(
                user_id=user_id, is_favorite=True
            ).count()
            stats['user_mastered'] = UserVocabulary.query.filter_by(
                user_id=user_id, status='mastered'
            ).count()
        
        return stats
