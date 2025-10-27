# OPIc Practice Portal - Setup Guide

This guide will help you set up the OPIc Practice Portal on your local machine for development and testing.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- **Python 3.8+** - [Download from python.org](https://python.org)
- **Git** - [Download from git-scm.com](https://git-scm.com)
- **Code Editor** - VS Code, PyCharm, or any preferred editor

### System Requirements
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: At least 2GB free space
- **OS**: Windows 10+, macOS 10.14+, or Linux

## 🚀 Quick Setup (Automated)

### Option 1: Windows Users
```bash
# Clone the repository
git clone <repository-url>
cd OPP

# Run automated setup
setup.bat
```

### Option 2: Cross-Platform
```bash
# Clone the repository
git clone <repository-url>
cd OPP

# Run automated setup
python setup.py
```

## 🔧 Manual Setup (Step-by-Step)

If you prefer to set up manually or the automated setup fails:

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd OPP
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy environment template
cp config.env.example .env

# Edit .env file (see Configuration section below)
```

### Step 5: Initialize Database with Sample Data
```bash
python scripts/init_db_with_samples.py
```

This will create:
- Database tables
- Admin user (admin/1qaz2wsx)
- Sample user (testuser/test123)
- Sample questions for all levels
- Sample responses for testing

### Step 7: Set Up Audio Files (Optional)
```bash
# Create audio directory structure
python scripts/audio_setup.py

# Note: Audio files are not included in the repository
# See AUDIO_SETUP.md for detailed instructions
```

### Step 8: Run the Application
```bash
python app.py
```

## ⚙️ Configuration

### Environment Variables (.env)
Create a `.env` file in the project root with the following variables:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///instance/opic_portal.db

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Optional: Email Configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Optional: External Services
LEMONFOX_API_KEY=your-lemonfox-api-key
OPENAI_API_KEY=your-openai-api-key
```

### Important Configuration Notes:
- **SECRET_KEY**: Generate a random string for production use
- **FLASK_ENV**: Set to `production` for production deployment
- **DATABASE_URL**: Use PostgreSQL URL for production
- **MAX_CONTENT_LENGTH**: Maximum file upload size (16MB default)

## 🗄️ Database Setup

### SQLite (Development)
The application uses SQLite by default for development. The database will be created automatically in the `instance/` folder.

### PostgreSQL (Production)
For production deployment, update the `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql://username:password@localhost/opic_portal
```

### Database Management Commands
```bash
# Initialize database with sample data
python scripts/init_db_with_samples.py

# Create admin user
python scripts/ensure_admin.py

# Reset admin password
python scripts/reset_admin.py

# Check database status
python scripts/inspect_db.py

# Analyze topics
python scripts/inspect_topics.py
```

## 🎵 Audio Files Setup

### Audio File Structure
The application expects audio files to be organized as follows:
```
uploads/questions/english/
├── IM/                          # Intermediate-Mid level
│   ├── 01. Newspapers/
│   │   ├── 01_Q1.mp3
│   │   ├── 01_Q2.mp3
│   │   └── ...
│   ├── 02. Television/
│   └── ...
├── IH/                          # Intermediate-High level
└── AL/                          # Advanced-Low level
```

### Audio File Requirements
- **Format**: MP3 files
- **Quality**: 128kbps or higher recommended
- **Naming**: Follow the pattern `XX_QY.mp3` where XX is topic number, Y is question number
- **Size**: Keep files under 5MB for optimal performance

## 🚀 Running the Application

### Development Mode
```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Run the application
python app.py
```

### Using Batch Files (Windows)
```bash
# Run setup
setup.bat

# Start application
run.bat
```

### Production Mode
```bash
# Set production environment
export FLASK_ENV=production  # Linux/macOS
set FLASK_ENV=production    # Windows

# Run with production settings
python app.py
```

## 🌐 Accessing the Application

Once running, the application will be available at:
- **Local**: http://localhost:5000
- **Network**: http://your-ip:5000

### Default Accounts
- **Admin Account**:
  - Username: `admin`
  - Password: `1qaz2wsx`

### User Registration
Regular users can register through the web interface at `/register`

## 🔧 Development Tools

### Useful Scripts
- `init_db.py` - Initialize database and create tables
- `ensure_admin.py` - Create admin user if it doesn't exist
- `reset_admin.py` - Reset admin password
- `inspect_db.py` - Check database status and statistics
- `inspect_topics.py` - Analyze topic distribution
- `tts_generator.py` - Generate text-to-speech audio files

### Database Inspection
```bash
# Check database status
python inspect_db.py

# Analyze topic distribution
python inspect_topics.py

# Check specific questions
python -c "from app import create_app; from app.models import Question; app = create_app(); app.app_context().push(); print(f'Total questions: {Question.query.count()}')"
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Python Not Found
```bash
# Check Python installation
python --version

# If not found, install Python 3.8+ from python.org
```

#### 2. Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows
python -m venv venv
```

#### 3. Database Not Found
```bash
# Initialize database
python init_db.py
```

#### 4. Admin User Not Working
```bash
# Reset admin password
python reset_admin.py
```

#### 5. Audio Files Not Playing
- Check file paths in `uploads/questions/`
- Verify audio file permissions
- Ensure files are in correct format (MP3)

#### 6. Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 7. Port Already in Use
```bash
# Kill process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS:
lsof -ti:5000 | xargs kill -9
```

### Debug Mode
Enable debug mode for detailed error information:
```env
FLASK_ENV=development
FLASK_DEBUG=True
```

### Log Files
Check application logs for errors:
- Console output when running `python app.py`
- Browser developer console for frontend errors

## 📱 Mobile Development

### PWA Features
The application includes Progressive Web App features:
- Service worker for offline functionality
- Web app manifest
- Installable on mobile devices
- Responsive design

### Mobile Testing
- Test on actual devices for audio recording
- Use Chrome DevTools device emulation
- Test touch interactions and responsive design

## 🔒 Security Considerations

### Development Security
- Never commit `.env` files to version control
- Use strong SECRET_KEY in production
- Regularly update dependencies
- Use HTTPS in production

### Production Security
- Set `FLASK_ENV=production`
- Use environment variables for sensitive data
- Enable CSRF protection
- Use secure database connections
- Implement proper file upload validation

## 📊 Performance Optimization

### Database Optimization
- Index frequently queried fields
- Use database connection pooling
- Optimize queries with proper joins

### File Optimization
- Compress audio files
- Use CDN for static assets
- Implement caching strategies

### Application Optimization
- Use background tasks for heavy operations
- Implement proper error handling
- Monitor application performance

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment
1. Set up production server
2. Install Python and dependencies
3. Configure environment variables
4. Set up reverse proxy (nginx)
5. Configure SSL certificates
6. Set up database
7. Deploy application files

## 📞 Support

### Getting Help
1. Check this setup guide
2. Review the main README.md
3. Check the troubleshooting section
4. Create an issue in the repository

### Useful Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)

---

**Happy Coding! 🎤**
