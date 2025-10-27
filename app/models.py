from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100), nullable=False)
    target_language = db.Column(db.String(20), default='english')
    streak_count = db.Column(db.Integer, default=0)
    last_active_date = db.Column(db.Date, default=date.today)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    responses = db.relationship('Response', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    surveys = db.relationship('Survey', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_streak(self):
        """Update user's streak count based on last active date"""
        today = date.today()
        yesterday = date.fromordinal(today.toordinal() - 1)
        
        if self.last_active_date == yesterday:
            # Consecutive day
            self.streak_count += 1
        elif self.last_active_date != today:
            # Streak broken
            self.streak_count = 1
        
        self.last_active_date = today
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))  # New field for organized topics
    language = db.Column(db.String(20), default='english')
    text = db.Column(db.Text, nullable=True)  # Changed to nullable for transcription
    difficulty = db.Column(db.Enum('beginner', 'intermediate', 'advanced', name='difficulty'), nullable=True)
    difficulty_level = db.Column(db.String(10))  # New field: IM, IH, AL
    question_type = db.Column(db.String(20), default='question')  # New field: question or answer
    audio_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    responses = db.relationship('Response', backref='question', lazy='dynamic')
    
    def __repr__(self):
        text_preview = self.text[:50] if self.text else 'No text'
        return f'<Question {self.id}: {text_preview}...>'

class Response(db.Model):
    __tablename__ = 'responses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    audio_url = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.Float)  # Duration in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Response {self.id} by User {self.user_id}>'

class Survey(db.Model):
    __tablename__ = 'surveys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answers = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Survey {self.id} by User {self.user_id}>'

