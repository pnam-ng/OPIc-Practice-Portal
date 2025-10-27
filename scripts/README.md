# Scripts Directory

This directory contains utility scripts for managing the OPIc Practice Portal.

## 📁 Scripts Overview

### Database Management
- **`init_db_with_samples.py`** - Initialize database with sample data (recommended for new setups)
- **`init_db.py`** - Initialize empty database (legacy)
- **`ensure_admin.py`** - Create admin user if it doesn't exist
- **`reset_admin.py`** - Reset admin password
- **`inspect_db.py`** - Check database status and statistics
- **`inspect_topics.py`** - Analyze topic distribution
- **`db_export_import.py`** - Export/import database (for sharing full database)

### Audio Management
- **`audio_setup.py`** - Create audio file directory structure
- **`tts_generator.py`** - Generate text-to-speech audio files

## 🚀 Quick Start

### For New Setup
```bash
# Initialize database with sample data
python scripts/init_db_with_samples.py

# Create audio directory structure
python scripts/audio_setup.py
```

### For Database Management
```bash
# Check database status
python scripts/inspect_db.py

# Reset admin password
python scripts/reset_admin.py

# Export database for sharing
python scripts/db_export_import.py export
```

## 📋 Usage Examples

### Database Initialization
```bash
# Create database with sample data (recommended)
python scripts/init_db_with_samples.py

# Create empty database (legacy)
python scripts/init_db.py
```

### User Management
```bash
# Create admin user
python scripts/ensure_admin.py

# Reset admin password
python scripts/reset_admin.py
```

### Database Inspection
```bash
# Check overall database status
python scripts/inspect_db.py

# Analyze topic distribution
python scripts/inspect_topics.py
```

### Database Export/Import
```bash
# Export database
python scripts/db_export_import.py export

# List available exports
python scripts/db_export_import.py list

# Import database
python scripts/db_export_import.py import <filename>
```

### Audio Setup
```bash
# Create audio directory structure
python scripts/audio_setup.py

# Generate TTS audio files
python scripts/tts_generator.py
```

## 🔧 Script Details

### init_db_with_samples.py
Creates database with:
- Admin user (admin/1qaz2wsx)
- Sample user (testuser/test123)
- 15 sample questions across all levels
- Sample responses for testing

### db_export_import.py
Database export/import tool:
- Export: Creates SQL dump file
- Import: Restores from SQL dump
- List: Shows available exports
- Includes summary files

### audio_setup.py
Creates audio directory structure:
- IM level: 20 topic directories
- IH level: 30 topic directories
- AL level: 32 topic directories
- Ready for MP3 file placement

### inspect_db.py
Database inspection tool:
- User count and details
- Question count by level
- Response statistics
- Database health check

### inspect_topics.py
Topic analysis tool:
- Topic distribution by level
- Question count per topic
- Topic organization verification

## 📞 Troubleshooting

### Common Issues
1. **Script not found**: Make sure you're in the project root directory
2. **Import errors**: Ensure virtual environment is activated
3. **Database errors**: Check if database exists and is accessible
4. **Permission errors**: Ensure write permissions for database and files

### Debug Mode
Most scripts support verbose output. Check script help:
```bash
python scripts/<script_name>.py --help
```

## 🔄 Integration

These scripts are integrated with:
- **setup.py** - Automated setup process
- **setup.bat** - Windows setup script
- **Documentation** - Referenced in README and guides

## 📝 Notes

- All scripts require Flask app context
- Database scripts create/use `instance/opic_portal.db`
- Audio scripts create directories in `uploads/questions/`
- Export files are saved in `database_exports/`
- Scripts are designed to be idempotent (safe to run multiple times)

---

**For detailed usage, see the main project documentation.**
