# OPIc Practice Portal 🎤

A comprehensive web application for practicing OPIc (Oral Proficiency Interview - computer) speaking tests. Built with Flask, featuring audio recording, AI feedback (planned), and a complete practice/test mode system.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🎯 Core Functionality
- **Practice Mode**: Practice individual questions with immediate feedback
- **Test Mode**: Full 12-question simulated OPIc test
- **Audio Recording**: Browser-based audio recording with waveform visualization
- **Audio Playback**: Listen to questions and your responses
- **Comment System**: Community feedback and discussion on practice responses
- **Notification System**: Real-time notifications for comments, replies, and mentions
- **User Profiles**: Customizable profiles with avatar upload
- **Activity Tracking**: Track your practice history and streaks

### 👨‍💼 Admin Features
- User management
- Question management
- Comment moderation (pin, delete)
- System analytics
- Database management tools

### 🎨 UI/UX
- Responsive design (desktop, tablet, mobile)
- Dark mode support
- Real-time waveform visualization during recording
- Progress tracking and streaks
- Congratulations pages after completion

### 🔒 Security
- User authentication (register, login, logout)
- Password reset functionality
- Session management
- Admin role-based access control

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/opic-practice-portal.git
cd opic-practice-portal
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy example config
copy config.env.example config.env

# Edit config.env with your settings
notepad config.env
```

5. **Initialize database**
```bash
python scripts/init_db.py
python scripts/ensure_admin.py  # Create admin account
```

6. **Run the application**
```bash
# Development
python app.py

# Production (with Gunicorn)
gunicorn -c gunicorn_config.py app:app
```

7. **Access the application**

**Local Development:**
```
http://localhost:5000
```

**Production (Internal Network):**
```
https://107.98.150.22:8080/
```

**Public Access (via ngrok tunnel):**
```
https://bit.ly/srvopic
```

**Default Admin Credentials:**
- Email: `admin@example.com`
- Password: `admin123` (change immediately!)

## 🌐 Deployment & Access

This application is deployed with multiple access points:

### Internal Network Access
For users within the company network:
- **URL**: `https://107.98.150.22:8080/`
- **Use Case**: Direct access for internal users
- **Protocol**: HTTPS with SSL certificates

### Public Access (ngrok Tunnel)
For external users and testing:
- **Short URL**: `https://bit.ly/srvopic`
- **Full URL**: Via ngrok secure tunnel
- **Use Case**: Remote access, demos, external testing
- **Benefits**: 
  - No firewall configuration needed
  - HTTPS by default
  - Easy sharing with QR code or short link

### Local Development
For developers:
- **URL**: `http://localhost:5000`
- **Use Case**: Development and testing

## 📁 Project Structure

```
OPP/
├── app/                    # Main application code
│   ├── blueprints/        # Route blueprints
│   │   ├── admin.py       # Admin routes
│   │   ├── auth.py        # Authentication
│   │   ├── comments.py    # Comment system
│   │   ├── main.py        # Main routes
│   │   ├── notifications.py # Notifications
│   │   ├── practice_mode.py # Practice routes
│   │   └── test_mode.py   # Test routes
│   ├── controllers/       # Business logic
│   ├── services/          # Service layer
│   └── models.py          # Database models
├── templates/             # Jinja2 templates
│   ├── admin/
│   ├── auth/
│   ├── main/
│   ├── practice_mode/
│   └── test_mode/
├── static/                # Static assets
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript
│   ├── avatars/          # Default avatars
│   └── icons/            # PWA icons
├── scripts/               # Utility scripts
│   ├── init_db.py        # Initialize database
│   ├── ensure_admin.py   # Create admin user
│   └── README.md         # Scripts documentation
├── docs/                  # Documentation
│   ├── setup/            # Setup guides
│   ├── features/         # Feature documentation
│   ├── development/      # Development docs
│   └── sessions/         # Session summaries
├── instance/              # Instance-specific files
│   └── opic_portal.db    # SQLite database
├── uploads/               # User uploads
│   ├── avatars/          # User avatars
│   ├── questions/        # Question audio
│   └── responses/        # User responses
├── config.env.example     # Example configuration
├── requirements.txt       # Python dependencies
├── app.py                 # Application entry point
├── Dockerfile             # Docker configuration
└── README.md             # This file
```

## 📚 Documentation

- [Setup Guide](docs/setup/SETUP_GUIDE.md) - Detailed installation instructions
- [Database Solution](docs/setup/DATABASE_SOLUTION.md) - Database architecture
- [Audio Setup](docs/setup/AUDIO_SETUP.md) - Audio file management
- [Admin Features](docs/features/ADMIN_FEATURES_GUIDE.md) - Admin panel guide
- [Comments System](docs/features/COMMENTS_SYSTEM_GUIDE.md) - Comment system documentation
- [AI Integration Plan](docs/development/AI_INTEGRATION_PLAN_OPENSOURCE.md) - Future AI features

## 🎯 Usage

### For Students

1. **Register an account**
2. **Choose Practice Mode** to practice individual questions
3. **Or Test Mode** for a full simulated test
4. **Record your response** (must play question first)
5. **Review your recordings** and get community feedback
6. **Track your progress** in the activity timeline

### For Admins

1. Login with admin credentials
2. Access admin panel from profile dropdown
3. Manage users, questions, and comments
4. View system statistics
5. Moderate community content

## 🛠️ Technology Stack

- **Backend**: Flask 2.3+
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Audio**: Web Audio API, MediaRecorder
- **Authentication**: Flask-Login
- **ORM**: SQLAlchemy
- **Deployment**: Gunicorn, Docker
- **Public Tunnel**: ngrok (for external access)

## 🔮 Planned Features

- [ ] AI-powered speech scoring (using open-source models)
- [ ] Pronunciation analysis
- [ ] Grammar checking
- [ ] Automated transcript generation
- [ ] Progress analytics dashboard
- [ ] Peer review system
- [ ] Mobile app (PWA)

See [AI Integration Plan](docs/development/AI_INTEGRATION_PLAN_OPENSOURCE.md) for details.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OPIc test format by ACTFL
- Bootstrap for UI components
- FontAwesome for icons
- OpenAI Whisper for future AI integration

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🔐 Security

If you discover a security vulnerability, please email security@example.com instead of opening a public issue.

---

**Made with ❤️ for OPIc learners**
