"""
OPIc Practice Portal - Main Application
Flask application following OOP principles with proper separation of concerns
"""

import os
from flask import Flask, send_from_directory
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from celery import Celery
from dotenv import load_dotenv

# Load environment variables (optional)
try:
    load_dotenv()
except:
    pass

# Initialize extensions
from app import db
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///opic_portal.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
    # Session configuration - Keep user logged in
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 30  # 30 days in seconds
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['REMEMBER_COOKIE_DURATION'] = 86400 * 30  # 30 days
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'responses'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'questions'), exist_ok=True)
    
    # Import models after db is initialized
    with app.app_context():
        from app.models import User, Question, Response, Survey
        
        # Configure login manager user loader
        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(User, int(user_id))
    
    # Register blueprints
    register_blueprints(app)

    # Serve uploaded files (question/response audio)
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    return app


def register_blueprints(app):
    """Register application blueprints"""
    from app.blueprints.auth import auth_bp
    from app.blueprints.main import main_bp
    from app.blueprints.test_mode import test_mode_bp
    from app.blueprints.practice_mode import practice_mode_bp
    from app.blueprints.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(test_mode_bp, url_prefix='/test')
    app.register_blueprint(practice_mode_bp, url_prefix='/practice')
    app.register_blueprint(admin_bp, url_prefix='/admin')

def create_celery(app=None):
    """Create Celery instance"""
    celery = Celery(
        app.import_name if app else 'opic_portal',
        backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        broker=os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    )
    
    if app:
        celery.conf.update(app.config)
        
        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
    
    return celery


# Create app instance
app = create_app()
celery = create_celery(app)

if __name__ == '__main__':
    # Check if SSL certificates exist
    import os
    ssl_cert = 'ssl/cert.pem'
    ssl_key = 'ssl/key.pem'
    
    if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        # Run with HTTPS (required for microphone/camera access over network)
        print("Starting server with HTTPS...")
        print("Access at: https://10.84.206.173:5000")
        print("Or: https://localhost:5000")
        print("\nNote: You may see a security warning. Click 'Advanced' and 'Proceed' to continue.")
        app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=(ssl_cert, ssl_key))
    else:
        # Run without HTTPS (localhost only)
        print("WARNING: Running without HTTPS. Microphone will only work on localhost.")
        print("To enable HTTPS, run: python generate_ssl_cert.py")
        app.run(host='0.0.0.0', port=5000, debug=True)