# Database Distribution Solution

## 🎯 Problem Solved

**Issue**: You don't want to push the database to GitHub, but your colleague needs to run the application with data.

**Solution**: Database is excluded from Git, but automatically created with sample data when your colleague sets up the project.

## 🚀 How It Works

### 1. Database Excluded from Git
- `instance/` folder is in `.gitignore`
- Database files (`*.db`, `*.sqlite`) are excluded
- No database files are pushed to GitHub

### 2. Automatic Database Creation
When your colleague runs the setup:
```bash
python setup.py
# or
python init_db_with_samples.py
```

The system automatically creates:
- ✅ **Database tables** (all required tables)
- ✅ **Admin user** (admin/1qaz2wsx)
- ✅ **Sample user** (testuser/test123)
- ✅ **Sample questions** (15 questions across all levels)
- ✅ **Sample responses** (for testing)

### 3. Ready to Use
Your colleague gets a fully functional application with:
- Working authentication system
- Sample questions for testing
- All features functional
- No manual database setup required

## 📊 Sample Data Included

### Questions (15 total)
- **IM Level**: 5 questions (Newspapers, Television, Internet, Phones, Music)
- **IH Level**: 5 questions (Newspapers, Television, Shopping, Free Time, Banks)
- **AL Level**: 5 questions (Newspapers, Television, Role Play, Messages, Bars)

### Users (2 total)
- **Admin**: admin/1qaz2wsx (full access)
- **Sample User**: testuser/test123 (regular user with sample responses)

### Responses (3 total)
- Sample audio responses linked to testuser
- Different durations for testing

## 🔄 Advanced Options

### Option 1: Share Full Database (Optional)
If you want to share your complete database with 1000+ questions:

```bash
# Export your database
python scripts/db_export_import.py export

# This creates: database_exports/opic_portal_export_YYYYMMDD_HHMMSS.sql
# Share this file with your colleague

# Your colleague imports it:
python scripts/db_export_import.py import database_exports/opic_portal_export_YYYYMMDD_HHMMSS.sql
```

### Option 2: Database Backup/Restore
```bash
# List available exports
python scripts/db_export_import.py list

# Import specific export
python scripts/db_export_import.py import <filename>
```

## 🎵 Audio Files Solution

### Problem
Audio files (MP3s) are large and shouldn't be in Git.

### Solution
1. **Audio files excluded** from Git (in `.gitignore`)
2. **Directory structure created** automatically (`python audio_setup.py`)
3. **Database contains file paths** but files are optional
4. **Application works without audio** (questions show text, audio just won't play)

### For Full Functionality
Your colleague can:
1. **Test without audio** (everything works except audio playback)
2. **Add sample audio files** manually for testing
3. **Get audio files separately** (via file sharing, cloud storage, etc.)
4. **Use audio setup script**: `python scripts/audio_setup.py`

## 📋 Setup Process for Your Colleague

### Automated Setup (Recommended)
```bash
git clone <repository-url>
cd OPP
python setup.py
```

This automatically:
- ✅ Creates virtual environment
- ✅ Installs dependencies
- ✅ Sets up environment variables
- ✅ Creates database with sample data
- ✅ Creates admin and sample users
- ✅ Sets up audio directory structure
- ✅ Ready to run!

### Manual Setup
```bash
git clone <repository-url>
cd OPP
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp config.env.example .env
python scripts/init_db_with_samples.py
python scripts/audio_setup.py
python app.py
```

## 🎯 Benefits

### For You (Repository Owner)
- ✅ **Small repository size** (no database, no audio files)
- ✅ **Fast Git operations** (clone, push, pull)
- ✅ **No GitHub limits** issues
- ✅ **Clean repository** with only code

### For Your Colleague
- ✅ **Easy setup** (one command)
- ✅ **Working application** immediately
- ✅ **Sample data** for testing
- ✅ **All features functional**
- ✅ **No manual database setup**

### For Development
- ✅ **Consistent environment** (same sample data for everyone)
- ✅ **Easy testing** (known users and questions)
- ✅ **No data conflicts** (each developer has their own database)
- ✅ **Version control friendly** (only code changes tracked)

## 🔧 Customization

### Adding More Sample Data
Edit `init_db_with_samples.py` to add more questions:

```python
sample_questions = [
    {
        'topic': 'XX. Topic Name',
        'category': 'Topic Name',
        'language': 'english',
        'text': 'Your question text here',
        'difficulty': 'intermediate',
        'difficulty_level': 'IM',
        'question_type': 'question',
        'audio_url': 'questions/english/IM/XX. Topic Name/XX_Q1.mp3'
    },
    # Add more questions...
]
```

### Database Migration
If you need to update the database schema:
1. Make changes to `app/models.py`
2. Update `init_db_with_samples.py` if needed
3. Your colleague runs setup again (database will be recreated)

## 📞 Support

### Common Issues
1. **Database not created**: Run `python init_db_with_samples.py`
2. **No questions showing**: Check database initialization
3. **Audio not playing**: Add audio files or test with text-only
4. **Users can't login**: Check if admin user was created

### Verification Commands
```bash
# Check database status
python inspect_db.py

# Check topics
python inspect_topics.py

# Verify users
python -c "from app import create_app; from app.models import User; app = create_app(); app.app_context().push(); print(f'Users: {User.query.count()}')"
```

---

**Result**: Your colleague gets a fully functional OPIc Practice Portal without you needing to push large files to GitHub! 🎉
