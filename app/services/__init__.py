"""
Services package for OPIc Practice Portal
Contains business logic and service classes following OOP principles
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
import time

from app import db
from app.models import User, Question, Response, Survey


class BaseService(ABC):
    """Base service class with common functionality"""
    
    def __init__(self):
        self.db = db
    
    def commit(self):
        """Commit database changes"""
        try:
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            current_app.logger.error(f"Database commit failed: {e}")
            return False
    
    def rollback(self):
        """Rollback database changes"""
        self.db.session.rollback()


class UserService(BaseService):
    """Service class for user-related operations"""
    
    def create_user(self, username: str, email: str = None, name: str = None, password: str = None, 
                   target_language: str = 'english') -> Optional[User]:
        """Create a new user"""
        try:
            # Check if user already exists
            if self.get_user_by_username(username):
                raise ValueError("Username already exists")
            
            # Check email only if provided (email is optional)
            if email and email.strip():
                if self.get_user_by_email(email):
                    raise ValueError("Email already registered")
            
            # Create new user (email can be None/empty)
            user = User(
                username=username,
                email=email if email and email.strip() else None,
                name=name,
                target_language=target_language
            )
            user.set_password(password)
            
            self.db.session.add(user)
            if self.commit():
                return user
            return None
            
        except ValueError as ve:
            # Re-raise ValueError for username/email already exists
            current_app.logger.warning(f"User creation failed: {ve}")
            self.rollback()
            raise
        except Exception as e:
            # Handle database integrity errors (concurrent registrations)
            error_msg = str(e).lower()
            current_app.logger.error(f"Error creating user: {e}")
            self.rollback()
            
            # Check for duplicate username/email in error message
            if 'unique' in error_msg or 'duplicate' in error_msg:
                if 'username' in error_msg:
                    raise ValueError("Username already exists. Please choose another.")
                elif 'email' in error_msg:
                    raise ValueError("Email already registered. Please use another email.")
                else:
                    raise ValueError("This account already exists. Please try a different username or email.")
            
            # For other database errors, return None
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email (only if email is provided)"""
        if not email or not email.strip():
            return None
        return User.query.filter_by(email=email).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return User.query.get(user_id)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = self.get_user_by_username(username)
        if user and user.check_password(password):
            return user
        return None
    
    def update_user_streak(self, user: User) -> bool:
        """Update user's streak count"""
        try:
            user.update_streak()
            return self.commit()
        except Exception as e:
            current_app.logger.error(f"Error updating streak: {e}")
            self.rollback()
            return False
    
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        user = self.get_user_by_id(user_id)
        if not user:
            return {}
        
        total_responses = Response.query.filter_by(user_id=user_id).count()
        practice_responses_count = Response.query.filter_by(user_id=user_id, mode='practice').count()
        test_responses_count = Response.query.filter_by(user_id=user_id, mode='test').count()
        recent_responses = Response.query.filter_by(user_id=user_id)\
            .order_by(Response.created_at.desc()).limit(5).all()
        
        return {
            'user': user,
            'total_responses': total_responses,
            'practice_responses_count': practice_responses_count,
            'test_responses_count': test_responses_count,
            'recent_responses': recent_responses,
            'streak_count': user.streak_count,
            'target_language': user.target_language
        }


class QuestionService(BaseService):
    """Service class for question-related operations"""
    
    def get_question_by_id(self, question_id: int) -> Optional[Question]:
        """Get question by ID"""
        return Question.query.get(question_id)
    
    def get_questions_by_topic(self, topic: str, language: str = 'english') -> List[Question]:
        """Get questions by topic and language"""
        return Question.query.filter_by(topic=topic, language=language).all()
    
    def get_questions_by_difficulty(self, difficulty: str, language: str = 'english') -> List[Question]:
        """Get questions by difficulty level"""
        return Question.query.filter_by(difficulty=difficulty, language=language).all()
    
    def get_random_questions(self, count: int = 1, language: str = 'english') -> List[Question]:
        """Get random questions"""
        return Question.query.filter_by(language=language)\
            .order_by(db.func.random()).limit(count).all()
    
    def get_all_topics(self, language: str = 'english', level: str = None) -> List[str]:
        """Get all available topics sorted alphabetically, optionally filtered by level"""
        query = db.session.query(Question.topic)\
            .filter_by(language=language)
        
        # Filter by level if specified
        if level:
            query = query.filter_by(difficulty_level=level)
        
        topics = query.distinct().all()
        
        # Process topics: remove number prefixes and deduplicate
        processed_topics = set()
        for topic_tuple in topics:
            if topic_tuple[0]:
                topic = topic_tuple[0]
                # Remove number prefix (e.g., "01. Newspapers" -> "Newspapers")
                if '. ' in topic:
                    topic_name = topic.split('. ', 1)[1]
                else:
                    topic_name = topic
                processed_topics.add(topic_name)
        
        # Sort and return
        return sorted(list(processed_topics))
    
    def get_all_questions_count(self) -> int:
        """Get total count of all questions"""
        return Question.query.count()
    
    def get_questions_by_topic_and_level(self, topic: str, language: str = 'english', level: str = None) -> List[Question]:
        """Get questions by topic, language, and difficulty level"""
        # Search for questions where topic matches with or without number prefix
        # For example, if user selects "Food", match both "Food" and "12. Food"
        base_query = Question.query.filter_by(language=language)
        
        if level:
            base_query = base_query.filter_by(difficulty_level=level)
        
        # Match either exact topic or topic with number prefix
        questions = base_query.filter(
            db.or_(
                Question.topic == topic,
                Question.topic.like(f'%. {topic}')
            )
        ).all()
        
        return questions
    
    def get_random_questions_by_level(self, count: int = 1, language: str = 'english', level: str = None) -> List[Question]:
        """Get random questions filtered by level"""
        query = Question.query.filter_by(language=language)
        if level:
            query = query.filter_by(difficulty_level=level)
        return query.order_by(db.func.random()).limit(count).all()


class ResponseService(BaseService):
    """Service class for response-related operations"""
    
    def create_response(self, user_id: int, question_id: int, audio_url: str, 
                       duration: float = None, mode: str = 'practice') -> Optional[Response]:
        """Create a new response"""
        try:
            response = Response(
                user_id=user_id,
                question_id=question_id,
                audio_url=audio_url,
                duration=duration,
                mode=mode
            )
            
            self.db.session.add(response)
            if self.commit():
                return response
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error creating response: {e}")
            self.rollback()
            return None
    
    def get_user_responses(self, user_id: int, limit: int = None) -> List[Response]:
        """Get user's responses"""
        query = Response.query.filter_by(user_id=user_id)\
            .order_by(Response.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_response_by_id(self, response_id: int) -> Optional[Response]:
        """Get response by ID"""
        return Response.query.get(response_id)


class SurveyService(BaseService):
    """Service class for survey-related operations"""
    
    def create_survey(self, user_id: int, answers: Dict[str, Any]) -> Optional[Survey]:
        """Create a new survey"""
        try:
            survey = Survey(
                user_id=user_id,
                answers=answers
            )
            
            self.db.session.add(survey)
            if self.commit():
                return survey
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error creating survey: {e}")
            self.rollback()
            return None
    
    def get_user_survey(self, user_id: int) -> Optional[Survey]:
        """Get user's latest survey"""
        return Survey.query.filter_by(user_id=user_id)\
            .order_by(Survey.created_at.desc()).first()
    
    def update_survey(self, survey_id: int, answers: Dict[str, Any]) -> bool:
        """Update existing survey"""
        try:
            survey = Survey.query.get(survey_id)
            if survey:
                survey.answers = answers
                return self.commit()
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error updating survey: {e}")
            self.rollback()
            return False


class AuthService(BaseService):
    """Service class for authentication operations"""
    
    def __init__(self):
        super().__init__()
        self.user_service = UserService()
    
    def register_user(self, username: str, email: str, name: str, password: str) -> Dict[str, Any]:
        """Register a new user"""
        try:
            user = self.user_service.create_user(username, email, name, password)
            if user:
                return {
                    'success': True,
                    'message': 'Registration successful! Please log in.',
                    'user': user
                }
            else:
                return {
                    'success': False,
                    'message': 'Registration failed. Please try again.'
                }
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }
        except Exception as e:
            current_app.logger.error(f"Registration error: {e}")
            return {
                'success': False,
                'message': 'An unexpected error occurred.'
            }
    
    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user login"""
        try:
            user = self.user_service.authenticate_user(username, password)
            if user:
                return {
                    'success': True,
                    'message': 'Login successful!',
                    'user': user
                }
            else:
                return {
                    'success': False,
                    'message': 'Invalid username or password'
                }
        except Exception as e:
            current_app.logger.error(f"Login error: {e}")
            return {
                'success': False,
                'message': 'An unexpected error occurred.'
            }
