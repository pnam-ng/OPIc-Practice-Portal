# OPIc Practice Portal - Project Structure

This document outlines the complete project structure and architecture of the OPIc Practice Portal Flask application.

## 📁 Project Root Structure

```
OPP/
├── 📁 app/                          # Main application package
│   ├── __init__.py                  # Application factory and initialization
│   ├── models.py                    # Database models (User, Question, Response, Survey)
│   ├── 📁 blueprints/              # Flask blueprints for modular routing
│   │   ├── auth.py                 # Authentication routes
│   │   ├── main.py                 # Main application routes
│   │   ├── admin.py                # Admin routes
│   │   ├── test_mode.py            # Test mode routes
│   │   └── practice_mode.py        # Practice mode routes
│   ├── 📁 controllers/              # Controller layer (MVC pattern)
│   │   └── __init__.py             # All controllers (Auth, Main, TestMode, PracticeMode)
│   └── 📁 services/                 # Service layer (Business logic)
│       └── __init__.py             # All services (User, Auth, Question, Response, Survey)
├── 📁 templates/                    # Jinja2 templates
│   ├── 📁 auth/
│   │   ├── login.html              # Login page with dark mode support
│   │   └── register.html           # Registration page
│   ├── 📁 main/
│   │   ├── index.html              # Landing page with CTA buttons
│   │   ├── dashboard.html          # User dashboard with streak tracking
│   │   ├── history.html            # Practice history timeline
│   │   └── profile.html            # User profile management
│   ├── 📁 test_mode/
│   │   ├── survey.html             # Initial survey for personalization
│   │   ├── survey_topics.html      # Topic selection survey
│   │   ├── self_assessment.html    # Self-assessment page
│   │   ├── questions.html          # Test questions interface
│   │   ├── congratulations.html    # Completion page
│   │   └── index.html              # Test mode entry
│   ├── 📁 practice_mode/
│   │   ├── index.html              # Practice mode selection
│   │   └── question.html           # Practice question interface
│   ├── 📁 admin/
│   │   └── user_list.html          # Admin user management
│   ├── base.html                   # Main base template with dark mode
│   └── opic_base.html              # Alternative base template
├── 📁 static/                       # Static files
│   ├── 📁 css/                     # Stylesheets (Bootstrap, Font Awesome)
│   ├── 📁 js/                      # JavaScript files (Bootstrap bundle)
│   ├── 📁 icons/                   # PWA icons (multiple sizes)
│   ├── 📁 webfonts/                # Font Awesome webfonts
│   ├── favicon.ico                 # Browser favicon
│   ├── microphone.png              # Microphone icon
│   ├── manifest.json               # PWA manifest
│   └── sw.js                       # Service worker
├── 📁 scripts/                     # Utility scripts (organized)
│   ├── init_db_with_samples.py    # Initialize database with sample data
│   ├── init_db.py                  # Basic database initialization
│   ├── ensure_admin.py             # Create admin user
│   ├── reset_admin.py              # Reset admin password
│   ├── inspect_db.py               # Database inspection
│   ├── inspect_topics.py           # Topic analysis
│   ├── audio_setup.py              # Audio directory setup
│   ├── db_export_import.py         # Database export/import
│   ├── tts_generator.py            # Text-to-speech generator
│   ├── add_mode_column.py          # Database migration utility
│   └── README.md                   # Scripts documentation
├── 📁 instance/                     # Instance folder (not in git)
│   └── opic_portal.db              # SQLite database (excluded from git)
├── 📁 uploads/                      # File uploads (not in git)
│   ├── 📁 responses/               # User audio recordings (excluded from git)
│   └── 📁 questions/               # Question audio files (excluded from git)
│       └── 📁 english/             # Organized by language
│           ├── 📁 IM/              # Intermediate-Mid (20 topic folders)
│           ├── 📁 IH/              # Intermediate-High (30 topic folders)
│           └── 📁 AL/              # Advanced-Low (32 topic folders)
├── 📁 transcription_backups/        # Transcription backup JSON files
├── 📁 OPIC Multicampus_AL/          # AL level audio source files (backup)
├── 📁 OPIC_Voices/                 # Original audio files (backup)
├── 📁 OPIC_Voices_Organized/       # Organized audio files (backup)
├── 📁 question_data/                # Additional audio backup
├── 📁 venv/                        # Python virtual environment (not in git)
├── 📁 ssl/                          # SSL certificates (optional, not in git)
├── 📄 app.py                        # Application entry point
├── 📄 setup.py                      # Automated setup script (cross-platform)
├── 📄 setup.bat                     # Windows setup batch file
├── 📄 run.bat                       # Windows run batch file
├── 📄 gunicorn_config.py            # Gunicorn production config
├── 📄 requirements.txt              # Python dependencies
├── 📄 requirements-dev.txt          # Development dependencies
├── 📄 config.env.example            # Environment variables template
├── 📄 .env                          # Environment variables (not in git)
├── 📄 .gitignore                    # Git ignore rules
├── 📄 README.md                     # Project documentation
├── 📄 SETUP_GUIDE.md               # Detailed setup instructions
├── 📄 PROJECT_STRUCTURE.md          # This file
├── 📄 AUDIO_SETUP.md               # Audio file setup guide
├── 📄 DATABASE_SOLUTION.md         # Database distribution strategy
├── 📄 CI_CD_GUIDE.md               # CI/CD setup guide
├── 📄 FUTURE_IMPLEMENTATION.md     # Future features roadmap
├── 📄 Dockerfile                    # Docker configuration
├── 📄 docker-compose.yml            # Docker Compose for development
└── 📄 docker-compose.prod.yml       # Docker Compose for production
```

**Note**: Files and folders marked with "not in git" are excluded via `.gitignore` for size or security reasons.

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

### 🎨 Dark Mode & Theme System
- **Full Dark Theme Support** - GitHub-inspired dark mode with proper contrast
- **Theme Persistence** - User preference saved in localStorage
- **Smooth Transitions** - Animated theme switching with rotation effect
- **Comprehensive Coverage** - All components styled (cards, forms, tables, modals, alerts, badges)
- **Mobile Optimized** - Dark mode toggle properly aligned on all devices
- **Custom Scrollbars** - Themed scrollbars for better aesthetics
- **Color Variables** - CSS custom properties for easy theme management

### 📱 Mobile-First Responsive Design
- **Touch-Friendly** - 44px minimum touch targets (iOS standards)
- **Responsive Navbar** - Floating overlay menu on mobile with backdrop
- **Optimized Layouts** - Cards, buttons, and forms adapt to screen size
- **PWA Install Banner** - Full-width mobile layout with stacked buttons
- **Button Positioning** - Important CTAs moved to prominent positions
- **Font Sizing** - Prevents zoom on iOS (16px minimum for inputs)
- **Smooth Scrolling** - Enhanced navigation experience

### 🔔 Notification System
- **Daily Streak Reminders** - Scheduled notifications at 8 PM
- **Browser Notifications** - Web Notification API integration
- **Permission Management** - User-controlled notification settings
- **Service Worker Integration** - Background notification support
- **Mobile Friendly** - Enable notifications button on mobile dashboard

### 🔐 Authentication System
- User registration and login
- Password hashing with Werkzeug
- Session management with Flask-Login
- Flash message system with themed alerts
- Password change functionality
- Username validation (letters, numbers, underscores, dots)
- Remember me functionality (30-day sessions)

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
- **Daily Streak System** - Automatic streak counting and maintenance
- **Streak Status Indicators** - Visual fire animations for active streaks
- **At-Risk Warnings** - Alerts when streak is about to break
- **Response History** - Complete timeline of practice sessions
- **Statistics Dashboard** - Total responses, questions, and language progress
- **Recent Activity Table** - Last 10 practice sessions with audio playback
- **Achievement Tracking** - Progress bars and milestone indicators
- **User Activity Monitoring** - Last active date tracking

### 🎵 Audio Features
- Question audio playback
- Voice recording with Web Audio API
- Audio file storage and management
- Transcription integration
- Multi-level audio organization

### 👨‍💼 Admin Dashboard
- **Question Management** - Full CRUD operations for questions
- **User Management** - View, edit, delete users
- **TTS Audio Generation** - Generate audio files from text
- **System Statistics** - User counts, question counts, response analytics
- **Database Inspection** - Real-time database status and health checks
- **Topic Analysis** - View question distribution by topic and level
- **Bulk Operations** - Import/export questions and data
- **Survey Management** - View and manage user surveys

### 🌐 Multi-Level Support
- **IM (Intermediate-Mid)** - 20 topics, 400+ questions
- **IH (Intermediate-High)** - 30 topics, 600+ questions  
- **AL (Advanced-Low)** - 32 topics, 640+ questions
- Dynamic topic filtering
- Level-specific question organization

## Quick Start Guide

### Prerequisites
- Python 3.8+
- pip
- Git

### Automated Setup (Recommended)
```bash
# Clone the repository
git clone https://github.sec.samsung.net/your-org/OPP.git
cd OPP

# Windows
setup.bat

# macOS/Linux
python setup.py
```

### Manual Installation
```bash
# Clone the repository
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

# Set up environment variables
cp config.env.example .env
# Edit .env with your configuration (optional)

# Initialize database with sample data
python scripts/init_db_with_samples.py

# Set up audio directory structure
python scripts/audio_setup.py

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

## CSS Architecture & Styling

### Theme System
```css
/* CSS Custom Properties for Theming */
:root {
  --bg-primary, --bg-secondary, --bg-card
  --text-primary, --text-secondary, --text-muted
  --border-color, --shadow, --navbar-bg
  --input-bg, --dropdown-bg, --modal-bg
}

[data-theme="dark"] {
  /* Dark mode color overrides */
  /* GitHub-inspired dark palette */
}
```

### Responsive Breakpoints
- **Mobile First**: Base styles for mobile devices
- **≤ 576px**: Small phones (compact UI, reduced padding)
- **≤ 768px**: Tablets and large phones (optimized layouts)
- **≤ 991px**: Small tablets (navbar collapse, menu overlay)
- **≥ 992px**: Desktop (full navigation, hover effects)

### Component Styling
- **Cards**: Themed with shadows, hover effects, smooth transitions
- **Buttons**: Touch-friendly sizing (44px min), haptic feedback
- **Forms**: 16px font size to prevent iOS zoom, themed inputs
- **Tables**: Responsive with horizontal scroll, themed rows
- **Modals**: Themed with dark mode support
- **Alerts**: Colored backgrounds for success/error/warning/info
- **Badges**: Level indicators, status tags

### Animation System
- **Theme Toggle**: 360° rotation animation
- **Streak Fire**: Pulsing glow effect for active streaks
- **Page Transitions**: Fade-in effects, loading spinners
- **Hover Effects**: Scale transforms, shadow enhancements
- **Smooth Scrolling**: Anchor link animations

## Development Notes

### Database Management
All database scripts are located in the `scripts/` folder:
- Use `scripts/init_db_with_samples.py` to initialize database with sample data
- Use `scripts/ensure_admin.py` to create admin user
- Use `scripts/reset_admin.py` to reset admin password
- Use `scripts/inspect_db.py` to check database status
- Use `scripts/inspect_topics.py` to analyze topic distribution
- Use `scripts/db_export_import.py` to export/import database

**Important**: The database file (`instance/opic_portal.db`) is excluded from Git. See [DATABASE_SOLUTION.md](DATABASE_SOLUTION.md) for distribution strategy.

### Audio Management
- Audio files are organized by level and topic in `uploads/questions/english/`
- Transcription backups are stored in `transcription_backups/`
- Original files are preserved in backup folders (`OPIC_Voices/`, `OPIC Multicampus_AL/`, etc.)
- Active files follow structure: `uploads/questions/english/{level}/{topic}/`

**Important**: Audio files are excluded from Git due to size. See [AUDIO_SETUP.md](AUDIO_SETUP.md) for setup instructions.

### Multi-Level Support
- Questions are categorized by OPIc levels (IM, IH, AL)
- Topics are dynamically filtered by level
- Each level has different topic distributions:
  - IM: 20 topics
  - IH: 30 topics
  - AL: 32 topics
- Level-specific question organization with numbered prefixes

## Network Configuration & Access

### Network Binding
The application is configured to bind to `0.0.0.0:5000`, allowing access from:
- **Localhost**: `http://localhost:5000`
- **LAN**: `http://LOCAL_IP:5000` (e.g., `http://192.168.50.222:5000`)
- **WAN**: Via port forwarding or ngrok

### Access Methods

#### 1. Local Development (Localhost)
```bash
python app.py
# Access: http://localhost:5000
```

#### 2. LAN Access (Same Network)
**Requirements:**
- Windows Firewall rule to allow port 5000
- Local IP address of the host machine

**Setup Windows Firewall:**
```powershell
# Run as Administrator
netsh advfirewall firewall add rule name="Flask App Port 5000" dir=in action=allow protocol=TCP localport=5000
```

**Find Local IP:**
```bash
# Windows
ipconfig

# Look for "IPv4 Address" under active network adapter
# Example: 192.168.50.222
```

**Access from LAN devices:**
- `http://192.168.50.222:5000`
- `https://192.168.50.222:5000` (with SSL)

#### 3. WAN Access via ngrok (Internet)

**Install ngrok:**
- Download from: https://ngrok.com/download
- Extract and add to PATH

**Run ngrok:**
```bash
ngrok http 5000
```

**Output:**
```
Forwarding: https://renee-ontogenic-attributively.ngrok-free.dev -> http://localhost:5000
```

**Important Notes:**
- ngrok URL works for internet/WAN access
- LAN devices should use local IP, not ngrok URL (NAT hairpinning issue)
- Free tier includes ngrok browser warning (handled by app header)

**ngrok Configuration in app.py:**
```python
@app.after_request
def add_ngrok_header(response):
    """Add header to bypass ngrok browser warning on free tier"""
    response.headers['ngrok-skip-browser-warning'] = 'true'
    return response
```

#### 4. WAN Access via Port Forwarding

**Router Configuration:**
1. Log into router admin panel (usually 192.168.1.1 or 192.168.0.1)
2. Navigate to "Port Forwarding" or "Virtual Server"
3. Add new rule:
   - Service Name: `Flask App` or `OPIc Portal`
   - External Port: `8080` (or your choice)
   - Internal IP: `192.168.50.222` (your local IP)
   - Internal Port: `5000`
   - Protocol: `TCP`
4. Save and apply

**Find Public IP:**
```bash
# Visit: https://whatismyip.com
# Or use command:
curl ifconfig.me
```

**Access:**
- External: `http://YOUR_PUBLIC_IP:8080`
- Example: `http://203.0.113.45:8080`

**Security Considerations:**
- Use HTTPS in production
- Consider VPN for secure access
- Use strong authentication
- Keep software updated

### SSL/HTTPS Configuration

**Why HTTPS is Required:**
- Browsers block microphone access over HTTP (except localhost)
- Required for Web Audio API over network
- Improved security for user data

**Generate Self-Signed Certificates:**
```bash
# Create ssl directory
mkdir ssl

# Generate certificate (valid for 365 days)
openssl req -x509 -newkey rsa:4096 -nodes -out ssl/cert.pem -keyout ssl/key.pem -days 365
```

**Application Detection:**
The app automatically detects SSL certificates:

```python
if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
    # Run with HTTPS
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=(ssl_cert, ssl_key))
else:
    # Run without HTTPS
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Browser Security Warning:**
- Self-signed certificates trigger browser warnings
- Click "Advanced" → "Proceed to [site]" to continue
- For production, use Let's Encrypt or commercial certificates

### Network Troubleshooting

#### Issue: LAN devices cannot connect

**Diagnosis:**
```bash
# From LAN device, test connectivity
ping 192.168.50.222

# Test port
telnet 192.168.50.222 5000
# Or
curl http://192.168.50.222:5000
```

**Solutions:**
1. Check Windows Firewall rules
2. Verify app is running and bound to `0.0.0.0`
3. Check antivirus software
4. Verify network connectivity

#### Issue: ngrok URL not working from LAN

**Explanation:**
- This is expected behavior (NAT hairpinning/loopback)
- Router blocks traffic that exits and re-enters same network

**Solutions:**
1. **Use local IP for LAN devices** (Recommended)
   - LAN: `http://192.168.50.222:5000`
   - WAN: `https://your-subdomain.ngrok-free.dev`

2. **Enable NAT Hairpinning on router** (If supported)
   - Also called: NAT Loopback, NAT Reflection
   - Look in router settings under WAN or Advanced
   - Not all routers support this

3. **Edit hosts file** (Advanced)
   - Windows: `C:\Windows\System32\drivers\etc\hosts`
   - Linux/Mac: `/etc/hosts`
   - Add: `192.168.50.222  your-subdomain.ngrok-free.dev`
   - Limitations: Won't work with HTTPS (certificate mismatch)

#### Issue: Microphone not working

**Solutions:**
1. Generate and use SSL certificates
2. Access via HTTPS
3. Accept browser security warning
4. Grant microphone permissions in browser

#### Issue: Port forwarding not working

**Checklist:**
- [ ] Router port forwarding configured correctly
- [ ] Windows Firewall allows the port
- [ ] ISP doesn't block incoming connections (some residential ISPs do)
- [ ] Using correct public IP address
- [ ] Dynamic DNS configured (if IP changes frequently)

## JavaScript Features & Interactions

### Dark Mode System (`base.html`)
- **Theme Persistence**: localStorage.getItem/setItem for theme preference
- **Instant Application**: Theme applied before page render to prevent flash
- **Smooth Toggle**: 360° rotation animation on theme switch
- **Icon Update**: Dynamic moon/sun icon switching

### Notification System
- **Permission Management**: Browser Notification API integration
- **Daily Reminders**: Scheduled at 8 PM using setTimeout calculations
- **Streak Status Check**: Monitors `data-streak-status` attribute
- **Service Worker**: Background notification support

### PWA Features
- **Installation Prompt**: beforeinstallprompt event handling
- **Install Banner**: Dynamic banner creation with slideUp animations
- **Dismiss Functionality**: localStorage-based dismissal tracking
- **Install Success**: Confirmation message after installation

### Navigation & UX
- **Mobile Menu**: Auto-close on link click or outside tap
- **Smooth Scrolling**: CSS scroll-behavior with JavaScript fallback
- **Loading States**: Page transition loaders with 3s timeout fallbacks
- **Touch Feedback**: Scale(0.95) animations on button press
- **Double-Tap Prevention**: Prevents accidental zoom on mobile

### Audio System
- **Web Audio API**: Recording and playback functionality
- **Duration Tracking**: Automatic recording time calculation
- **Playback Controls**: Play/pause with visual feedback
- **File Upload**: FormData with progress indication

## Deployment

### Development
```bash
python app.py
# Access: http://localhost:5000
# With SSL: https://localhost:5000
```

### Production with Docker
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Production with Gunicorn
```bash
gunicorn -c gunicorn_config.py app:app
```

### Environment Setup
- Copy `config.env.example` to `.env`
- Configure environment variables
- Set up database connection
- Configure file upload paths
- Generate SSL certificates for HTTPS (required for microphone access)
- Configure firewall rules for network access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.