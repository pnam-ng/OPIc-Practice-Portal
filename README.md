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
- Real-time progress tracking

### 📝 Test Mode
- Survey-based question selection
- Personalized test experience
- Audio recording and playback
- Progress tracking
- Congratulations page with results

### 🔐 User Management
- User registration and authentication
- Password management
- Daily streak tracking with notifications
- Activity history and statistics
- Profile customization

### 🎨 UI/UX Features
- **Dark Mode** - Full dark theme support with smooth transitions
- **Responsive Design** - Mobile-first approach with optimized layouts
- **PWA Support** - Install as native app on mobile devices
- **Touch-Friendly** - Optimized buttons and interactions for mobile
- **Notifications** - Daily streak reminders (8 PM)
- **Loading Animations** - Smooth page transitions

### 👨‍💼 Admin Features
- Question management (CRUD operations)
- User administration
- Database inspection tools
- System statistics and analytics
- TTS audio generation

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

### Automated Setup (Recommended)

#### Windows Users
   ```bash
git clone https://github.sec.samsung.net/your-org/OPP.git
cd OPP
setup.bat
   ```

#### macOS/Linux Users
   ```bash
git clone https://github.sec.samsung.net/your-org/OPP.git
cd OPP
python setup.py
```

The setup script will:
- Create and activate a virtual environment
- Install all dependencies
- Copy `.env` configuration file
- Initialize the database with sample data
- Create audio directory structure
- Set up admin and sample users

### Manual Setup
   ```bash
# Clone repository
git clone https://github.sec.samsung.net/your-org/OPP.git
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
# Edit .env with your configuration (optional)

# Initialize database with sample data
python scripts/init_db_with_samples.py

# Set up audio directory structure
python scripts/audio_setup.py

# Run application
python app.py
```

### Running the Application

#### Windows
   ```bash
run.bat
   ```

#### macOS/Linux
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## 🌐 Deployment & Access

### Local Development
The application runs on `http://localhost:5000` by default.

For detailed information about:
- Network access (LAN/WAN)
- SSL/HTTPS setup
- Firewall configuration
- Production deployment

Please refer to [SETUP_GUIDE.md](SETUP_GUIDE.md)

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
│   ├── blueprints/        # Flask blueprints (routes)
│   ├── controllers/       # MVC controllers
│   ├── services/          # Business logic
│   └── models.py          # Database models
├── templates/             # HTML templates (Jinja2)
├── static/                # Static assets (CSS, JS, icons)
├── scripts/               # Utility scripts
│   ├── init_db_with_samples.py  # Database initialization
│   ├── audio_setup.py           # Audio directory setup
│   ├── db_export_import.py      # Database backup/restore
│   └── ...                      # Other utilities
├── uploads/               # File uploads (not in git)
│   ├── questions/         # Audio files (not in git)
│   └── responses/         # User recordings (not in git)
├── instance/              # SQLite database (not in git)
├── app.py                 # Application entry point
├── setup.py               # Automated setup script
├── setup.bat              # Windows setup script
├── run.bat                # Windows run script
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

For complete project structure, see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 🎵 Audio Files

### Important Note
Audio files and the database are **not included in the Git repository** due to size constraints.

- **Audio files**: See [AUDIO_SETUP.md](AUDIO_SETUP.md) for setup instructions
- **Database**: See [DATABASE_SOLUTION.md](DATABASE_SOLUTION.md) for distribution strategy

The setup script creates the necessary directory structure. You'll need to:
1. Obtain audio files separately (from colleague or shared drive)
2. Place them in `uploads/questions/english/` following the directory structure

## 🔧 Development

### Utility Scripts

All utility scripts are located in the `scripts/` folder. See [scripts/README.md](scripts/README.md) for detailed documentation.

Key scripts:
- `init_db_with_samples.py` - Initialize database with sample data
- `audio_setup.py` - Create audio directory structure
- `db_export_import.py` - Export/import database for distribution
- `inspect_db.py` - Check database status and statistics
- `reset_admin.py` - Reset admin password

### Database Management
```bash
# Initialize fresh database with sample data
python scripts/init_db_with_samples.py

# Export database for sharing
python scripts/db_export_import.py export

# Import database from SQL file
python scripts/db_export_import.py import database_backup.sql

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

1. **ModuleNotFoundError when running scripts**
   ```bash
   # Make sure you're in the project root directory
   cd D:\OPP
   # Activate virtual environment first
   venv\Scripts\activate
   # Then run the script
   python scripts/init_db_with_samples.py
   ```

2. **Database not found**
   ```bash
   python scripts/init_db_with_samples.py
   ```

3. **Admin user not working**
   ```bash
   python scripts/reset_admin.py
   ```

4. **Audio files not playing**
   - Check file paths in `uploads/questions/`
   - Verify audio files are placed correctly (see AUDIO_SETUP.md)
   - Run `python scripts/audio_setup.py` to create directory structure

5. **Import errors**
   ```bash
   pip install -r requirements.txt
   ```

For more troubleshooting, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 📚 Documentation

- **[Setup Guide](SETUP_GUIDE.md)** - Detailed setup instructions (network, SSL, deployment)
- **[Project Structure](PROJECT_STRUCTURE.md)** - Complete project documentation
- **[Audio Setup](AUDIO_SETUP.md)** - Audio file setup instructions
- **[Database Solution](DATABASE_SOLUTION.md)** - Database distribution strategy
- **[Scripts README](scripts/README.md)** - Utility scripts documentation
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
- Web app manifest for installation
- Installable on mobile devices (iOS & Android)
- Responsive design optimized for all screen sizes
- Touch-friendly interface with haptic feedback
- Native app-like experience
- Install banner with dismiss functionality
- Home screen icons and splash screens

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
- ✅ Dynamic topic filtering by level
- ✅ Enhanced security features
- ✅ PWA capabilities with offline support
- ✅ Comprehensive admin tools
- ✅ Automated setup scripts
- ✅ Complete documentation
- ✅ Database and audio file distribution solution
- ✅ Organized utility scripts in `scripts/` folder
- ✅ Cleaned up unnecessary documentation files

---

**Happy Practicing! 🎤**

> **Note**: For detailed setup instructions, troubleshooting, and advanced configuration, please refer to the [Setup Guide](SETUP_GUIDE.md).