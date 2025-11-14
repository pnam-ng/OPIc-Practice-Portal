"""
OPIc Practice Portal - Main Application
Flask application following OOP principles with proper separation of concerns
"""

import os
import html
from flask import Flask, send_from_directory
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_caching import Cache
from celery import Celery
from dotenv import load_dotenv

# Load environment variables (optional)
# Try to load environment file in order of preference
try:
    # Try multiple common environment file names
    env_files = ['config.env', '.env', 'env']
    loaded = False
    for env_file in env_files:
        if os.path.exists(env_file):
            load_dotenv(env_file)
            loaded = True
            break
    
    # If no file found, try default load_dotenv() behavior
    if not loaded:
        load_dotenv()
except Exception as e:
    # If dotenv is not available or fails, continue without it
    # Environment variables can still be set via system environment
    pass

# Initialize extensions
from app import db
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
cache = Cache()


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Basic Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///opic_portal.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
    # AI Configuration - Also store in Flask config for services to access
    app.config['GOOGLE_AI_API_KEY'] = os.environ.get('GOOGLE_AI_API_KEY') or os.environ.get('GEMINI_API_KEY')
    app.config['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_AI_API_KEY')
    
    # Database Connection Pooling (for production scalability)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 20,  # Number of connections to keep open
        'pool_recycle': 3600,  # Recycle connections after 1 hour
        'pool_pre_ping': True,  # Check connection health before using
        'max_overflow': 40,  # Additional connections when pool is full
        'pool_timeout': 30,  # Timeout for getting connection from pool
    }
    
    # Caching Configuration
    app.config['CACHE_TYPE'] = os.environ.get('CACHE_TYPE', 'simple')  # Use 'redis' in production
    app.config['CACHE_REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 minutes
    
    # Session configuration - Optimized for concurrent users
    app.config['SESSION_TYPE'] = 'filesystem'  # Use 'redis' in production
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 30  # 30 days in seconds
    
    # Auto-detect HTTPS: Check environment variable first, then auto-detect
    session_cookie_secure_env = os.environ.get('SESSION_COOKIE_SECURE', '').lower()
    if session_cookie_secure_env in ('true', 'false'):
        app.config['SESSION_COOKIE_SECURE'] = session_cookie_secure_env == 'true'
    else:
        # Auto-detect: Check if SSL certificates exist (indicates HTTPS)
        ssl_cert = 'ssl/cert.pem'
        ssl_key = 'ssl/key.pem'
        app.config['SESSION_COOKIE_SECURE'] = os.path.exists(ssl_cert) and os.path.exists(ssl_key)
    
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['REMEMBER_COOKIE_DURATION'] = 86400 * 30  # 30 days
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    
    # Performance optimizations
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache static files for 1 year
    app.config['JSON_SORT_KEYS'] = False  # Don't sort JSON keys (faster)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    cache.init_app(app)
    
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
    
    # Add Jinja2 filter to decode HTML entities
    def unescape_html_filter(text):
        """Decode HTML entities like &#39; to '"""
        if text is None:
            return ''
        return html.unescape(str(text))
    
    # Register the filter with Flask (recommended method)
    app.add_template_filter(unescape_html_filter, 'unescape_html')

    # Serve uploaded files (question/response audio)
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    # Add ngrok-skip-browser-warning header to all responses
    @app.after_request
    def add_ngrok_header(response):
        """Add header to bypass ngrok browser warning on free tier"""
        response.headers['ngrok-skip-browser-warning'] = 'true'
        return response
    
    # Middleware to handle HTTPS detection and session cookies
    @app.before_request
    def detect_https():
        """Detect HTTPS from request and ensure secure cookies are enabled"""
        from flask import request
        # Check if request is secure (HTTPS) - ProxyFix middleware makes request.is_secure work
        is_secure = request.is_secure
        
        # If we detect HTTPS, ensure secure cookies are enabled
        # Note: This needs to be set before session cookies are created
        if is_secure:
            app.config['SESSION_COOKIE_SECURE'] = True
            # For self-signed certs, we might need SameSite=None, but let's try Lax first
            # If issues persist, can change to: app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    
    # Trust proxy headers (for reverse proxies like nginx, load balancers)
    # This must be applied AFTER all app setup but BEFORE returning
    # This allows request.is_secure to work correctly behind proxies
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_port=1,
        x_prefix=1
    )
    
    return app


def register_blueprints(app):
    """Register application blueprints"""
    from app.blueprints.auth import auth_bp
    from app.blueprints.main import main_bp
    from app.blueprints.test_mode import test_mode_bp
    from app.blueprints.practice_mode import practice_mode_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.comments import comments_bp
    from app.blueprints.notifications import notifications_bp
    
    # Import chatbot blueprint (with error handling)
    try:
        from app.blueprints.chatbot import chatbot_bp
        app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')
        print("[OK] Chatbot blueprint registered successfully")
    except Exception as e:
        print(f"[ERROR] Failed to register chatbot blueprint: {e}")
        import traceback
        traceback.print_exc()
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(test_mode_bp, url_prefix='/test')
    app.register_blueprint(practice_mode_bp, url_prefix='/practice')
    app.register_blueprint(comments_bp)
    app.register_blueprint(notifications_bp)
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
        print("=" * 60)
        print("Starting server with HTTPS...")
        print("=" * 60)
        print()
        print("Access at: https://localhost:5000")
        print()
        print("Note: You may see a security warning.")
        print("   Click 'Advanced' and 'Proceed' to continue.")
        print("=" * 60)
        print()
        app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=(ssl_cert, ssl_key))
    else:
        # Run without HTTPS (localhost only)
        print("=" * 60)
        print("WARNING: Running without HTTPS")
        print("=" * 60)
        print()
        print("Microphone will only work on localhost.")
        print("To enable HTTPS, generate SSL certificates:")
        print()
        print("  mkdir ssl")
        print("  openssl req -x509 -newkey rsa:4096 -nodes \\")
        print("          -out ssl/cert.pem -keyout ssl/key.pem -days 365")
        print()
        print("Access at: http://localhost:5000")
        print("=" * 60)
        print()
        app.run(host='0.0.0.0', port=5000, debug=True)