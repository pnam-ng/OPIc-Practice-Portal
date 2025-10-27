# OPIc Practice Portal

A comprehensive web application for practicing OPIc (Oral Proficiency Interview - computer) speaking tests. This portal provides both practice and test modes with multi-level support (IM, IH, AL) and audio recording capabilities.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Features

### 🎯 Multi-Level Support
- **IM (Intermediate-Mid)** - 20 topics, 400+ questions
- **IH (Intermediate-High)** - 30 topics, 600+ questions  
- **AL (Advanced-Low)** - 32 topics, 640+ questions

### 🏃 Practice Mode
- Topic-based practice sessions
- Random question mode
- Dynamic topic filtering by level
- Audio question playback
- Voice recording capabilities

### 📝 Test Mode
- Survey-based question selection
- Personalized test experience
- Audio recording and playback
- Progress tracking

### 🔐 User Management
- User registration and authentication
- Password management
- Progress tracking and streaks
- Activity history

### 👨‍💼 Admin Features
- Question management
- User administration
- Database inspection tools
- System statistics

## 🛠️ Technology Stack

- **Backend**: Flask 3.1.2, SQLAlchemy 2.0.44
- **Frontend**: Bootstrap 5, JavaScript, Web Audio API
- **Database**: SQLite (development), PostgreSQL (production)
- **Audio**: MP3 playback, Web Audio recording
- **PWA**: Progressive Web App support

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git

### Automated Setup

#### Windows Users
```bash
git clone <repository-url>
cd OPP
setup.bat
```

#### Cross-Platform
```bash
git clone <repository-url>
cd OPP
python setup.py
```

### Manual Setup
```bash
# Clone repository
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

# Configure environment
cp config.env.example .env
# Edit .env with your configuration

# Initialize database
python init_db.py

# Create admin user
python ensure_admin.py

# Run application
python app.py
```

The application will be available at `http://localhost:5000`

## 📋 Configuration

### Environment Variables (.env)
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/opic_portal.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

### Default Accounts
- **Admin Account**:
  - Username: `admin`
  - Password: `1qaz2wsx`
- **Sample User Account**:
  - Username: `testuser`
  - Password: `test123`

## 📁 Project Structure

```
OPP/
├── app/                    # Main application package
│   ├── blueprints/        # Flask blueprints
│   ├── controllers/       # MVC controllers
│   ├── services/         # Business logic
│   └── models.py         # Database models
├── templates/             # HTML templates
├── static/               # Static assets (CSS, JS, icons)
├── uploads/              # Audio files and user uploads
├── instance/             # SQLite database
├── transcription_backups/ # Transcription backup files
├── app.py                # Application entry point
├── init_db.py            # Database initialization
├── setup.py              # Automated setup script
├── setup.bat             # Windows setup script
├── run.bat               # Windows run script
└── requirements.txt      # Python dependencies
```

## 🎵 Audio Features

### Question Audio
- Questions include audio files for listening practice
- Audio files are organized by topic and difficulty level
- Supports MP3 format
- **Note**: Audio files are not included in the repository due to size

### Voice Recording
- Users can record their responses
- Web Audio API integration
- Audio files are stored in `uploads/responses/`

### Audio Setup
See [AUDIO_SETUP.md](AUDIO_SETUP.md) for instructions on setting up audio files.

## 🔧 Development

### Utility Scripts
- `scripts/init_db_with_samples.py` - Initialize database with sample data
- `scripts/ensure_admin.py` - Create admin user if it doesn't exist
- `scripts/reset_admin.py` - Reset admin password
- `scripts/inspect_db.py` - Check database status and statistics
- `scripts/inspect_topics.py` - Analyze topic distribution
- `scripts/audio_setup.py` - Create audio directory structure
- `scripts/db_export_import.py` - Export/import database
- `scripts/tts_generator.py` - Generate text-to-speech audio files

### Database Management
```bash
# Initialize database with sample data
python scripts/init_db_with_samples.py

# Create admin user
python scripts/ensure_admin.py

# Reset admin password
python scripts/reset_admin.py

# Check database status
python scripts/inspect_db.py
```

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production with Docker
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🐛 Troubleshooting

### Common Issues

1. **Database not found**
   ```bash
   python init_db.py
   ```

2. **Admin user not working**
   ```bash
   python reset_admin.py
   ```

3. **Audio files not playing**
   - Check file paths in `uploads/questions/`
   - Verify audio file permissions

4. **Import errors**
   ```bash
   pip install -r requirements.txt
   ```

### Debug Mode
Set `FLASK_ENV=development` in `.env` for debug information.

## 📚 Documentation

- **[Setup Guide](SETUP_GUIDE.md)** - Detailed setup instructions
- **[Project Structure](PROJECT_STRUCTURE.md)** - Complete project documentation
- **[CI/CD Guide](CI_CD_GUIDE.md)** - Deployment and CI/CD guide
- **[Future Implementation](FUTURE_IMPLEMENTATION.md)** - Roadmap and future features

## 🔒 Security Features

- Password hashing with Werkzeug
- CSRF protection
- SQL injection prevention
- XSS protection
- Secure session management
- File upload validation
- Direct question access prevention

## 📱 PWA Support

The application includes Progressive Web App features:
- Service worker for offline functionality
- Web app manifest
- Installable on mobile devices
- Responsive design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For issues and questions:
1. Check the [Setup Guide](SETUP_GUIDE.md)
2. Review the [troubleshooting section](#-troubleshooting)
3. Create an issue in the repository

## 🔄 Recent Updates

- ✅ Multi-level question organization (IM, IH, AL)
- ✅ Dynamic topic filtering
- ✅ Enhanced security features
- ✅ PWA capabilities
- ✅ Comprehensive admin tools
- ✅ Automated setup scripts
- ✅ Complete documentation

---

**Happy Practicing! 🎤**

> **Note**: For detailed setup instructions, troubleshooting, and advanced configuration, please refer to the [Setup Guide](SETUP_GUIDE.md).