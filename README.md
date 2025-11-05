# OPIc Practice Portal 🎤

A comprehensive web application for practicing OPIc (Oral Proficiency Interview - computer) speaking tests. Built with Flask, featuring audio recording, AI feedback (planned), and a complete practice/test mode system.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🎯 Core Functionality

#### Practice & Testing
- **Practice Mode**: Practice individual questions with immediate AI feedback
- **Test Mode**: Full simulated OPIc test (10-15 questions based on self-assessment level)
- **Self-Assessment**: Level-based test configuration (levels 1-6)
- **Progress Tracking**: Visual progress bars and completion tracking
- **Question History**: Review all practiced questions and responses

#### Audio Features
- **Browser-Based Recording**: High-quality audio recording using Web Audio API
- **Waveform Visualization**: Real-time waveform display during recording
- **Audio Playback**: Listen to questions and your recorded responses
- **Recording Controls**: Start, stop, pause, and playback controls
- **Format Support**: WebM format with automatic browser compatibility

#### AI-Powered Features (See [🤖 AI Features](#-ai-features) section below)
- **AI Chatbot**: Interactive assistant for OPIc guidance and tips
- **AI Scoring**: Automated response evaluation with detailed feedback
- **Smart Feedback**: Personalized suggestions based on performance
- **Conversation History**: Persistent chat history across sessions

#### Content & Resources
- **Tips & Resources**: Access PDF study materials and guides
- **PDF Viewer**: Inline PDF viewing with mobile-optimized interface
- **Thumbnail Preview**: Visual previews for PDF resources
- **Resource Management**: Admin-controlled content curation

#### Community & Social
- **Comment System**: Comment on practice responses with threaded replies
- **User Tagging**: Mention users with `@username` in comments
- **Like System**: Show appreciation for helpful comments
- **Comment Moderation**: Admin tools for pinning and managing comments
- **Activity Timeline**: Track your practice history and achievements

#### Notifications
- **Real-time Notifications**: Get notified about replies, mentions, and likes
- **Streak Reminders**: Daily browser notifications at 8 PM to maintain practice streaks
- **Notification Center**: Centralized notification management
- **Read/Unread Tracking**: Keep track of notification status
- **Auto-cleanup**: Notifications older than 30 days are automatically removed

#### User Management
- **User Profiles**: Customizable profiles with avatar upload and crop
- **Activity Tracking**: Track practice history, streaks, and statistics
- **Dashboard**: Personal dashboard with quick access to features
- **History View**: View all past practice sessions and test results

### 🤖 AI Features

#### AI Chatbot Service
- **Powered by Google Gemini**: Free tier AI chatbot with intelligent responses
- **Model Fallback System**: Automatic fallback to alternative models when rate limits are reached
  - Primary: `gemini-2.5-flash` (250 requests/day)
  - Fallback 1: `gemini-2.5-flash-lite` (1,000 requests/day)
  - Fallback 2: `gemini-2.0-flash` (200 requests/day)
  - Fallback 3: `gemini-2.0-flash-lite` (200 requests/day)
  - Fallback 4: `gemini-2.5-pro` (50 requests/day)
- **Auto Model Recovery**: Automatically reverts to primary model when available
- **Conversation Context**: Maintains conversation history for context-aware responses
- **Floating Widget**: Available on all pages as a floating chat bubble
- **Dedicated Chat Page**: Full-page chatbot interface
- **Synchronized History**: Chat history syncs between widget and main page
- **Persistent Storage**: Chat history saved in localStorage across sessions

#### AI Scoring Service
- **Automated Evaluation**: AI-powered scoring of OPIc responses
- **OPIc Criteria**: Evaluates based on official OPIc rater guidelines
- **Multi-factor Scoring**:
  - Grammar and accuracy (20 points)
  - Vocabulary range and usage (20 points)
  - Fluency and naturalness (20 points)
  - Content relevance and completeness (20 points)
  - Tone and prosody (20 points)
- **Personalized Feedback**: Detailed feedback in Vietnamese with specific examples
- **Strength Analysis**: Identifies specific strengths in responses
- **Improvement Suggestions**: Actionable suggestions for enhancement
- **Audio Analysis**: Analyzes pitch, speaking rate, pauses, and volume

#### AI Model Features
- **Rate Limit Handling**: Intelligent handling of API rate limits
- **Error Recovery**: Automatic retry with exponential backoff
- **Timeout Management**: 90-second timeout with graceful error handling
- **Free Tier Support**: Uses Google AI Studio free tier (no credit card required)
- **API Key Management**: Secure API key configuration via environment variables

### 📱 Progressive Web App (PWA) Features

#### Installation & Access
- **Install on Desktop**: One-click installation from browser
- **Install on Mobile**: Native app-like experience on iOS and Android
- **Install Prompt**: Automatic install banner for eligible devices
- **Manual Install Guide**: Step-by-step instructions for iOS and Android
- **App Icon**: Custom app icons for all device sizes (16x16 to 512x512)
- **Splash Screen**: Custom splash screen with app branding

#### Offline Capabilities
- **Service Worker**: Background service worker for offline functionality
- **Caching Strategy**: Intelligent caching of static assets and pages
- **Offline Pages**: Access cached pages when offline
- **Background Sync**: Automatic sync when connection is restored

#### App-like Experience
- **Standalone Mode**: Runs in standalone mode (no browser UI)
- **Full Screen**: Full-screen experience on mobile devices
- **Orientation Support**: Supports both portrait and landscape orientations
- **Theme Colors**: Custom theme colors matching app design
- **App Manifest**: Complete PWA manifest with all metadata

#### Mobile Optimizations
- **Touch Optimized**: Optimized for touch interactions
- **Responsive Design**: Perfect rendering on all screen sizes
- **Mobile Navigation**: Mobile-friendly navigation menu
- **Install Button**: Prominent install button in navigation bar (mobile)
- **iOS Support**: Special handling for iOS Safari installation

#### PWA Features Summary
- ✅ **Installable**: Can be installed on home screen/desktop
- ✅ **Offline Support**: Works offline with cached content
- ✅ **App-like UI**: Standalone app experience
- ✅ **Push Notifications**: Browser notification support
- ✅ **Auto-updates**: Service worker handles updates automatically
- ✅ **Fast Loading**: Optimized caching for instant loading

### 👨‍💼 Admin Features

#### User Management
- **User List**: View all users with detailed activity information
- **Activity Tracking**: Track user creation date, last active time, and practice history
- **User Details**: View individual user profiles and statistics
- **Admin Controls**: Create, update, and manage user accounts

#### Content Management
- **Question Management**: Full CRUD operations for questions
- **Question Categories**: Organize questions by topics and difficulty
- **Audio Management**: Upload and manage question audio files
- **Sample Answers**: Generate and manage sample answers for questions

#### Tips & Resources Management
- **PDF Upload**: Upload PDF study materials directly
- **Thumbnail Generation**: Automatic thumbnail generation from PDFs
- **Manual Thumbnails**: Option to upload custom thumbnails
- **Resource Organization**: Categorize and order resources
- **Active/Inactive Toggle**: Control resource visibility

#### Community Moderation
- **Comment Moderation**: Pin helpful comments, delete inappropriate content
- **User Management**: View and manage user interactions
- **Content Review**: Review and moderate community content

#### Analytics & Statistics
- **System Analytics**: View system-wide statistics
- **User Activity**: Track user engagement and activity
- **Database Management**: Tools for database maintenance and inspection

### 🎨 UI/UX Features

#### Design & Theming
- **Responsive Design**: Perfect rendering on desktop, tablet, and mobile
- **Dark Mode**: Full dark mode support with theme toggle
- **Modern UI**: Clean, modern interface with Bootstrap 5
- **Custom Styling**: Consistent color scheme and branding
- **Accessibility**: WCAG-compliant design elements

#### Interactive Elements
- **Real-time Waveform**: Live waveform visualization during recording
- **Progress Indicators**: Visual progress bars and completion tracking
- **Loading States**: Smooth loading animations and indicators
- **Toast Notifications**: Non-intrusive notification toasts
- **Modal Dialogs**: Clean modal dialogs for confirmations and forms

#### User Experience
- **Congratulations Pages**: Celebration pages after test completion
- **Streak Tracking**: Visual streak indicators and reminders
- **Activity Timeline**: Chronological view of practice history
- **Quick Actions**: Quick access buttons for common actions
- **Keyboard Shortcuts**: Efficient keyboard navigation support

#### Mobile Experience
- **Touch Gestures**: Optimized touch interactions
- **Mobile Navigation**: Collapsible mobile menu
- **Bottom Sheets**: Mobile-friendly bottom action sheets
- **Responsive Forms**: Mobile-optimized form inputs
- **Swipe Support**: Swipe gestures for navigation

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
python scripts/ensure_admin.py  # Create admin account (password will be prompted)
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


**Admin Setup:**
- Run `python scripts/ensure_admin.py` to create/reset admin user
- Password will be prompted or can be set via `ADMIN_PASSWORD` environment variable
- Default username: `admin`
- Email: `admin@opic-portal.com`

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
│   │   ├── chatbot.py     # Chatbot routes
│   │   ├── comments.py    # Comment system
│   │   ├── main.py        # Main routes (Tips, Dashboard, etc.)
│   │   ├── notifications.py # Notifications
│   │   ├── practice_mode.py # Practice routes
│   │   └── test_mode.py   # Test routes
│   ├── controllers/       # Business logic
│   ├── services/          # Service layer (AI, Chatbot, etc.)
│   ├── utils/             # Utility functions (PDF thumbnails, etc.)
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
│   ├── icons/            # PWA icons
│   ├── thumbnails/       # PDF thumbnails
│   └── galaxyAI.png      # Chatbot icon
├── scripts/               # Utility scripts
│   ├── init_db.py        # Initialize database
│   ├── ensure_admin.py   # Create admin user
│   └── README.md         # Scripts documentation
├── docs/                  # Documentation
│   ├── setup/            # Setup guides
│   ├── features/         # Feature documentation
│   ├── development/      # Development docs
│   └── sessions/         # Session summaries
├── files/                 # PDF resources (Tips)
│   └── *.pdf             # Study materials and guides
├── instance/              # Instance-specific files
│   └── opic_portal.db    # SQLite database
├── uploads/               # User uploads
│   ├── avatars/          # User avatars
│   ├── questions/        # Question audio
│   └── responses/        # User responses
├── config.env.example     # Example configuration
├── requirements.txt       # Python dependencies
├── requirements-ai.txt    # AI/ML dependencies (optional)
├── requirements-dev.txt   # Development dependencies (optional)
├── app.py                 # Application entry point
├── setup.py               # Automated setup script
├── setup.bat              # Windows setup batch file
├── install_ai.bat         # AI setup for Windows (optional)
├── install_ai.sh          # AI setup for Linux/macOS (optional)
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose (development)
├── docker-compose.prod.yml # Docker Compose (production)
└── README.md             # This file
```

## 📚 Documentation

- [Setup Guide](docs/setup/SETUP_GUIDE.md) - Detailed installation instructions
- [Database Solution](docs/setup/DATABASE_SOLUTION.md) - Database architecture
- [Audio Setup](docs/setup/AUDIO_SETUP.md) - Audio file management
- [Admin Features](docs/features/ADMIN_FEATURES_GUIDE.md) - Admin panel guide
- [Comments System](docs/features/COMMENTS_SYSTEM_GUIDE.md) - Comment system documentation with replies and tagging
- [AI Integration Plan](docs/development/AI_INTEGRATION_PLAN_OPENSOURCE.md) - AI features and setup
- [Quick AI Setup](docs/development/QUICK_AI_SETUP.md) - Quick guide for AI integration

## 🎯 Usage

### For Students

#### Getting Started
1. **Register an account** - Create your free account
2. **Install the App** (Optional) - Install as PWA for app-like experience
3. **Complete Self-Assessment** - Choose your level (1-6) for personalized test mode

#### Practice & Testing
4. **Practice Mode** - Practice individual questions with immediate AI feedback
5. **Test Mode** - Complete a full simulated OPIc test (10-15 questions based on level)
6. **Record Responses** - Use browser-based recording with waveform visualization
7. **Review Feedback** - Get AI-powered scoring and detailed feedback

#### Learning Resources
8. **AI Chatbot** - Get guidance and tips via floating chatbot widget or dedicated page
9. **Tips & Resources** - Browse PDF study materials and guides
10. **Community Interaction** - Comment, reply, and discuss with other learners

#### Engagement Features
11. **Notifications** - Get notified about replies, mentions, likes, and streak reminders
12. **Track Progress** - View your practice history and streaks in the activity timeline
13. **Maintain Streaks** - Daily practice reminders to maintain your streak

### 💬 Comment & Community Features

#### Commenting on Practice Responses
- **Post Comments**: Share feedback, tips, or questions on any practice response
- **Reply to Comments**: Engage in discussions by replying to comments
- **Tag Users**: Use `@username` to mention and notify other users in your comments
- **Like Comments**: Show appreciation by liking helpful comments
- **Pin Comments**: Admins can pin helpful comments for better visibility
- **Edit Comments**: Edit your own comments if you need to make corrections
- **Delete Comments**: Remove your own comments, or admins can moderate any comment

#### Comment Features:
- **Threaded Replies**: Nested reply structure for organized discussions
- **Auto-tagging**: Clicking "Reply" automatically tags the comment author
- **Character Limit**: Up to 2,200 characters per comment/reply
- **Emoji Support**: Full emoji and special character support
- **Sorting Options**: Sort by recent or popular (most liked)
- **Pagination**: Load more comments as you scroll

#### Notification System
- **Reply Notifications**: Get notified when someone replies to your comment
- **Mention Notifications**: Receive notifications when you're tagged with `@username`
- **Like Notifications**: Know when someone likes your comment
- **Streak Reminders**: Daily browser notifications at 8 PM if you haven't practiced (maintains your streak)
- **Notification Center**: View all notifications in one place
- **Mark as Read**: Mark notifications as read to keep track
- **Auto-cleanup**: Notifications older than 30 days are automatically removed

#### Streak Reminder Notifications
- **Daily Reminders**: Browser notifications at 8 PM if your streak is at risk
- **Permission-based**: Request notification permission once to enable reminders
- **Mobile-friendly**: Easy enable button on mobile dashboard
- **Action Buttons**: Quick access to "Start Practice" or "Start Test" from notifications

### For Admins

1. Login with admin credentials
2. Access admin panel from navigation menu
3. Manage users, questions, tips, and comments
4. Upload PDF resources and manage thumbnails
5. View system statistics and user activity
6. Moderate community content:
   - **Pin Comments**: Pin helpful comments to the top
   - **Delete Comments**: Remove inappropriate or spam comments
   - **User Management**: View and manage all user accounts

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 2.3+
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **API**: RESTful API design
- **Deployment**: Gunicorn, Docker

### Frontend
- **CSS Framework**: Bootstrap 5
- **JavaScript**: Vanilla JavaScript (ES6+)
- **Audio**: Web Audio API, MediaRecorder API
- **PWA**: Service Worker, Web App Manifest
- **Storage**: localStorage for client-side persistence

### AI & ML
- **Chatbot**: Google AI Studio (Gemini) - Free tier
- **Scoring**: Google AI Studio (Gemini) with OPIc rater guidelines
- **Models**: 
  - `gemini-2.5-flash` (primary)
  - `gemini-2.5-flash-lite` (fallback)
  - `gemini-2.0-flash` (fallback)
  - `gemini-2.5-pro` (fallback)
- **Fallback Logic**: Automatic model switching on rate limits
- **API Integration**: RESTful API calls with retry logic

### Media & Processing
- **PDF Processing**: PyMuPDF (fitz), Pillow for thumbnails
- **Audio Formats**: WebM, with browser compatibility
- **Image Processing**: Avatar upload and crop functionality

### PWA Technologies
- **Service Worker**: Background sync and offline support
- **Web App Manifest**: Complete PWA configuration
- **Push Notifications**: Browser notification API
- **Install Prompt**: Custom install prompt handling

### Deployment & Infrastructure
- **Web Server**: Gunicorn for production
- **Containerization**: Docker and Docker Compose
- **SSL/TLS**: HTTPS with SSL certificates
- **Public Access**: ngrok tunnel for external access

## 🔮 Feature Status

### ✅ Completed Features
- [x] **AI Chatbot** - Google Gemini integration with fallback models
- [x] **AI Scoring** - Automated response evaluation with detailed feedback
- [x] **Tips & Resources** - PDF system with thumbnails and inline viewing
- [x] **Community Comments** - Full comment system with replies and tagging
- [x] **Notifications** - Comprehensive notification system with streak reminders
- [x] **PWA Support** - Full Progressive Web App with offline capabilities
- [x] **User Profiles** - Customizable profiles with avatar upload
- [x] **Activity Tracking** - Complete history and streak tracking
- [x] **Dark Mode** - Full dark mode support
- [x] **Mobile Optimization** - Responsive design for all devices

### 🚧 Planned Features
- [ ] **Pronunciation Analysis** - Detailed pronunciation feedback
- [ ] **Grammar Checking** - Automated grammar error detection
- [ ] **Automated Transcription** - Speech-to-text for all recordings
- [ ] **Enhanced Analytics** - Advanced progress analytics dashboard
- [ ] **Peer Review System** - Peer-to-peer feedback system
- [ ] **Multi-language Support** - Support for additional languages
- [ ] **Export Data** - Export practice history and statistics

See [AI Integration Plan](docs/development/AI_INTEGRATION_PLAN_OPENSOURCE.md) for detailed AI roadmap.

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
