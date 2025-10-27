# OPIc Practice Portal - Project Structure

This document outlines the complete project structure and architecture of the OPIc Practice Portal Flask application.

## 📁 Project Root Structure

```
OPP/
├── 📁 app/                          # Main application package
│   ├── __init__.py                  # Application factory and initialization
│   ├── models.py                    # Database models (User, Question, Response, Survey)
│   ├── 📁 blueprints/              # Flask blueprints for modular routing
│   │   ├── __init__.py
│   │   ├── auth.py                 # Authentication routes
│   │   ├── main.py                 # Main application routes
│   │   ├── test_mode.py            # Test mode routes
│   │   └── practice_mode.py        # Practice mode routes
│   ├── 📁 controllers/              # Controller layer (MVC pattern)
│   │   └── __init__.py             # All controllers (Auth, Main, TestMode, PracticeMode)
│   └── 📁 services/                 # Service layer (Business logic)
│       └── __init__.py             # All services (User, Auth, Question, Response, Survey)
├── 📁 templates/                    # Jinja2 templates
│   ├── 📁 auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── 📁 main/
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   └── history.html
│   ├── 📁 test_mode/
│   │   ├── survey.html
│   │   ├── questions.html
│   │   └── index.html
│   ├── 📁 practice_mode/
│   │   ├── index.html
│   │   └── question.html
│   ├── base.html
│   └── opic_base.html
├── 📁 static/                       # Static files
│   ├── 📁 css/                     # Stylesheets
│   ├── 📁 js/                      # JavaScript files
│   ├── 📁 icons/                   # PWA icons and favicon
│   ├── favicon.ico                 # Browser favicon
│   ├── manifest.json               # PWA manifest
│   └── sw.js                       # Service worker
├── 📁 scripts/                     # Utility scripts
│   ├── init_db_with_samples.py    # Initialize database with sample data
│   ├── ensure_admin.py             # Create admin user
│   ├── reset_admin.py              # Reset admin password
│   ├── inspect_db.py               # Database inspection
│   ├── inspect_topics.py           # Topic analysis
│   ├── audio_setup.py              # Audio directory setup
│   ├── db_export_import.py         # Database export/import
│   └── tts_generator.py            # Text-to-speech generator
├── 📁 instance/                     # Instance folder (SQLite database)
│   └── opic_portal.db
├── 📁 uploads/                      # File uploads
│   ├── 📁 responses/               # User audio recordings
│   └── 📁 questions/               # Question audio files (organized by level/topic)
│       └── 📁 english/
│           ├── 📁 IM/              # Intermediate-Mid level
│           ├── 📁 IH/              # Intermediate-High level
│           └── 📁 AL/              # Advanced-Low level
├── 📁 transcription_backups/        # Transcription backup files
├── 📁 question_data/                # Original audio files (backup)
├── 📁 OPIC_Voices/                 # Original unorganized audio files
├── 📁 OPIC_Voices_Organized/       # Organized audio files
├── 📁 OPIC Multicampus_AL/          # AL level specific files
├── 📁 venv/                        # Python virtual environment
├── 📄 app.py                        # Application entry point
├── 📄 init_db.py                    # Database initialization script
├── 📄 ensure_admin.py               # Ensure admin user exists
├── 📄 reset_admin.py                # Reset admin password
├── 📄 inspect_db.py                 # Database inspection utility
├── 📄 inspect_topics.py              # Topic inspection utility
├── 📄 tts_generator.py              # Text-to-Speech generator
├── 📄 requirements.txt              # Python dependencies
├── 📄 requirements-dev.txt          # Development dependencies
├── 📄 config.env.example            # Environment variables template
├── 📄 .env                          # Environment variables (not in git)
├── 📄 .gitignore                    # Git ignore rules
├── 📄 README.md                     # Project documentation
├── 📄 PROJECT_STRUCTURE.md          # This file
├── 📄 CI_CD_GUIDE.md               # CI/CD setup guide
├── 📄 FUTURE_IMPLEMENTATION.md     # Future features roadmap
├── 📄 Dockerfile                    # Docker configuration
├── 📄 docker-compose.yml            # Docker Compose for development
├── 📄 docker-compose.prod.yml       # Docker Compose for production
└── 📄 .github/                      # GitHub Actions workflows
    └── workflows/
        ├── ci.yml                   # Continuous Integration
        └── deploy.yml                # Continuous Deployment
```

## Technology Stack

### Backend
- **Flask 3.1.2** - Python web framework
- **SQLAlchemy 2.0.44** - ORM for database operations
- **Flask-Login 0.6.3** - User session management
- **Flask-Migrate 4.1.0** - Database migrations
- **Flask-WTF 1.2.2** - Form handling and CSRF protection
- **Flask-Admin 1.6.1** - Admin interface
- **Flask-Mail 0.10.0** - Email notifications
- **Celery 5.5.3** - Background task processing (optional)

### Database
- **SQLite** - Development database
- **PostgreSQL** - Production database (optional)
- **Alembic 1.17.0** - Database migration tool

### Frontend
- **Bootstrap 5.1.3** - CSS framework
- **Font Awesome 6.0.0** - Icons
- **JavaScript** - Client-side interactions
- **Web Audio API** - Audio recording and playback
- **PWA Support** - Progressive Web App features

### External Services
- **LemonFox.ai** - Audio transcription service
- **OpenAI TTS API** - Text-to-speech generation (optional)

### Development Tools
- **Python 3.14+** - Programming language
- **pip** - Package management
- **Git** - Version control
- **Docker** - Containerization
- **GitHub Actions** - CI/CD pipeline

## Key Features

### 🔐 Authentication System
- User registration and login
- Password hashing with Werkzeug
- Session management with Flask-Login
- Flash message system
- Password change functionality
- Username validation (letters, numbers, underscores, dots)

### 📊 Database Models
- **User**: Profile, streak tracking, preferences, admin status
- **Question**: Text, audio, difficulty levels (IM/IH/AL), topics, categories
- **Response**: User audio recordings with duration tracking
- **Survey**: Test personalization data

### 🎯 Test Mode
- Survey-based question selection
- Audio question playback
- Voice recording capabilities
- Progress tracking
- Multi-level support (IM, IH, AL)

### 🏃 Practice Mode
- Topic-based practice sessions
- Random question mode
- Difficulty level selection (IM, IH, AL)
- Dynamic topic filtering by level
- Flexible practice options
- Security-enhanced question access

### 📈 Progress Tracking
- Daily streak system
- Response history
- Statistics dashboard
- Achievement tracking
- User activity monitoring

### 🎵 Audio Features
- Question audio playback
- Voice recording with Web Audio API
- Audio file storage and management
- Transcription integration
- Multi-level audio organization

### 👨‍💼 Admin Dashboard
- Question management (CRUD)
- User management
- TTS audio generation
- System statistics
- Database inspection tools

### 🌐 Multi-Level Support
- **IM (Intermediate-Mid)** - 20 topics, 400+ questions
- **IH (Intermediate-High)** - 30 topics, 600+ questions  
- **AL (Advanced-Low)** - 32 topics, 640+ questions
- Dynamic topic filtering
- Level-specific question organization

## Quick Start Guide

### Prerequisites
- Python 3.14+
- pip
- Git

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd OPP

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp config.env.example .env
# Edit .env with your configuration

# Initialize database
python init_db.py

# Run the application
python app.py
```

### Environment Variables
Create a `.env` file with the following variables:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/opic_portal.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

## Database Schema

### Users Table
```sql
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- name
- target_language
- streak_count
- last_active_date
- is_admin
- created_at, updated_at
```

### Questions Table
```sql
- id (Primary Key)
- topic (with prefix, e.g., "01. Newspapers")
- category (clean topic name, e.g., "Newspapers")
- language
- text (transcribed question text)
- difficulty (beginner/intermediate/advanced)
- difficulty_level (IM/IH/AL)
- question_type (question/answer)
- audio_url
- created_at, updated_at
```

### Responses Table
```sql
- id (Primary Key)
- user_id (Foreign Key)
- question_id (Foreign Key)
- audio_url
- duration
- created_at
```

### Surveys Table
```sql
- id (Primary Key)
- user_id (Foreign Key)
- answers (JSON)
- created_at
```

## API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Login form submission
- `GET /register` - Registration page
- `POST /register` - Registration form submission
- `GET /logout` - User logout
- `POST /change-password` - Change user password

### Main Application
- `GET /` - Home page
- `GET /dashboard` - User dashboard (protected)
- `GET /history` - User activity history (protected)
- `GET /profile` - User profile page (protected)

### Test Mode
- `GET /test` - Test mode interface
- `GET /test/survey` - Test survey page
- `POST /test/survey` - Submit test survey
- `GET /test/questions` - Get test questions
- `POST /test/record/<question_id>` - Record audio response

### Practice Mode
- `GET /practice` - Practice mode interface
- `GET /practice/topics/<level>` - Get topics by level (AJAX)
- `POST /practice/start` - Start practice session
- `GET /practice/question/<question_id>` - Practice question page
- `POST /practice/record/<question_id>` - Record practice response

### Admin (if admin user)
- `GET /admin` - Admin dashboard
- Admin interface for managing questions and users

## Security Features

- Password hashing with Werkzeug
- CSRF protection with Flask-WTF
- SQL injection prevention with SQLAlchemy ORM
- XSS protection with Jinja2 auto-escaping
- Secure session management
- File upload validation
- Environment variable protection
- Direct question access prevention
- Session-based question authorization

## File Organization

### Audio Files Structure
```
uploads/questions/english/
├── IM/                          # Intermediate-Mid level
│   ├── 01. Newspapers/
│   ├── 02. Television/
│   ├── 03. Internet/
│   └── ...
├── IH/                          # Intermediate-High level
│   ├── 01. Newspapers/
│   ├── 02. Television/
│   └── ...
└── AL/                          # Advanced-Low level
    ├── 01. Newspapers/
    ├── 02. Television/
    └── ...
```

### Topic Organization
- Topics are organized by filename prefixes (01, 02, 03, etc.)
- Each prefix group contains related questions
- Topics are categorized by content analysis
- Clean topic names are used in UI (without prefixes)

## Development Notes

### Database Management
- Use `init_db.py` to initialize the database
- Use `ensure_admin.py` to create admin user
- Use `reset_admin.py` to reset admin password
- Use `inspect_db.py` to check database status
- Use `inspect_topics.py` to analyze topic distribution

### Audio Management
- Audio files are organized by level and topic
- Transcription backups are stored in `transcription_backups/`
- Original files are preserved in backup folders
- Active files are in `uploads/questions/`

### Multi-Level Support
- Questions are categorized by OPIc levels (IM, IH, AL)
- Topics are dynamically filtered by level
- Each level has different topic distributions
- Level-specific question organization

## Deployment

### Development
```bash
python app.py
```

### Production with Docker
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Setup
- Copy `config.env.example` to `.env`
- Configure environment variables
- Set up database connection
- Configure file upload paths

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.