from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import pytz

def now_hanoi():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(tz)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100), nullable=False)
    target_language = db.Column(db.String(20), default='english')
    avatar = db.Column(db.String(200), default='default1.svg')  # Avatar file path or default avatar name
    streak_count = db.Column(db.Integer, default=0)
    last_active_date = db.Column(db.Date, default=date.today)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=now_hanoi)
    updated_at = db.Column(db.DateTime, default=now_hanoi, onupdate=now_hanoi)
    
    # Relationships
    responses = db.relationship('Response', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    surveys = db.relationship('Survey', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_streak(self):
        """Update user's streak count based on last active date"""
        today = date.today()
        yesterday = date.fromordinal(today.toordinal() - 1)
        
        if self.last_active_date == yesterday:
            # Consecutive day - increment streak
            self.streak_count += 1
        elif self.last_active_date == today:
            # Already active today - don't change streak
            return
        else:
            # More than 1 day gap - reset streak to 1
            self.streak_count = 1
        
        self.last_active_date = today
        db.session.commit()
    
    def check_streak_status(self):
        """Check if user's streak is at risk"""
        today = date.today()
        
        if self.last_active_date == today:
            return 'active_today'  # User has practiced today
        elif self.last_active_date == date.fromordinal(today.toordinal() - 1):
            return 'at_risk'  # User practiced yesterday but not today
        else:
            return 'broken'  # Streak is broken (more than 1 day gap)
    
    def is_active_today(self):
        """Check if user has been active today"""
        return self.last_active_date == date.today()
    
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
    sample_answer_text = db.Column(db.Text, nullable=True)  # Sample answer transcription
    sample_answer_audio_url = db.Column(db.String(200), nullable=True)  # Sample answer audio path
    created_at = db.Column(db.DateTime, default=now_hanoi)
    updated_at = db.Column(db.DateTime, default=now_hanoi, onupdate=now_hanoi)
    
    # Relationships
    responses = db.relationship('Response', backref='question', lazy='dynamic')
    comments = db.relationship('Comment', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    
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
    mode = db.Column(db.String(20), default='practice')  # 'practice' or 'test'
    created_at = db.Column(db.DateTime, default=now_hanoi)
    
    def __repr__(self):
        return f'<Response {self.id} by User {self.user_id}>'

class Survey(db.Model):
    __tablename__ = 'surveys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answers = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=now_hanoi)
    
    def __repr__(self):
        return f'<Survey {self.id} by User {self.user_id}>'

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)  # For replies
    content = db.Column(db.Text, nullable=False)
    is_edited = db.Column(db.Boolean, default=False)
    is_pinned = db.Column(db.Boolean, default=False)  # Admins can pin helpful comments
    likes_count = db.Column(db.Integer, default=0)
    replies_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=now_hanoi)
    updated_at = db.Column(db.DateTime, default=now_hanoi, onupdate=now_hanoi)
    
    # Relationships
    likes = db.relationship('CommentLike', backref='comment', lazy='dynamic', cascade='all, delete-orphan')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), 
                             lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        content_preview = self.content[:30] if self.content else 'No content'
        reply_info = f" (reply to {self.parent_id})" if self.parent_id else ""
        return f'<Comment {self.id} by User {self.user_id}: {content_preview}...{reply_info}>'
    
    def to_dict(self, include_replies=False, current_user_id=None):
        """Convert comment to dictionary for JSON responses"""
        # Check if current user has liked this comment
        user_has_liked = False
        if current_user_id:
            user_has_liked = CommentLike.query.filter_by(
                comment_id=self.id, 
                user_id=current_user_id
            ).first() is not None
        
        data = {
            'id': self.id,
            'question_id': self.question_id,
            'user_id': self.user_id,
            'parent_id': self.parent_id,
            'username': self.author.username,
            'user_name': self.author.name,
            'user_avatar': self.author.avatar,
            'is_admin': self.author.is_admin,
            'content': self.content,
            'is_edited': self.is_edited,
            'is_pinned': self.is_pinned,
            'likes_count': self.likes_count,
            'replies_count': self.replies_count,
            'user_has_liked': user_has_liked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Include replies if requested
        if include_replies:
            data['replies'] = [reply.to_dict(include_replies=False, current_user_id=current_user_id) 
                              for reply in self.replies.order_by(Comment.created_at.asc()).all()]
        
        return data

class CommentLike(db.Model):
    __tablename__ = 'comment_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=now_hanoi)
    
    # Unique constraint to prevent duplicate likes
    __table_args__ = (db.UniqueConstraint('comment_id', 'user_id', name='unique_comment_like'),)
    
    def __repr__(self):
        return f'<CommentLike {self.id}: User {self.user_id} likes Comment {self.comment_id}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User receiving the notification
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User who triggered the notification
    type = db.Column(db.String(50), nullable=False)  # 'mention', 'reply', 'like', etc.
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=now_hanoi)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='notifications')
    actor = db.relationship('User', foreign_keys=[actor_id], backref='triggered_notifications')
    comment = db.relationship('Comment', backref='notifications')
    question = db.relationship('Question', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.type} for User {self.user_id}>'
    
    def to_dict(self):
        """Convert notification to dictionary for JSON responses"""
        return {
            'id': self.id,
            'type': self.type,
            'question_id': self.question_id,
            'comment_id': self.comment_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'actor': {
                'id': self.actor.id,
                'username': self.actor.username,
                'name': self.actor.name,
                'avatar': self.actor.avatar
            },
            'question_topic': self.question.topic if self.question else None,
            'comment_preview': self.comment.content[:100] if self.comment else None
        }
