# OPIc Practice Portal - Migration Guide

This guide will help you migrate your OPIc Practice Portal project from your current machine to an Oracle Cloud VM.

## 📋 Migration Overview

The migration process includes:
- ✅ **Database** (`instance/opic_portal.db`) - All user data, questions, responses, comments
- ✅ **Uploads** (`uploads/`) - Voice files, audio recordings, avatars, comments
- ✅ **PDF Files** (`files/`) - Study materials and resources
- ✅ **Source Code** - All application code, templates, static files
- ✅ **Configuration** - Environment configuration files
- ✅ **Scripts** - Utility and setup scripts

## 🚀 Quick Start

### Option 1: Automated Migration (Recommended)

1. **Run the migration script**:
   ```bash
   python scripts/migrate_project.py
   ```

2. **Select package format**:
   - ZIP (recommended for Windows)
   - TAR.GZ (recommended for Linux)

3. **Transfer the package** to Oracle Cloud VM:
   ```bash
   # Using SCP
   scp opic_portal_migration_*.zip ubuntu@your-vm-ip:/home/ubuntu/
   ```

4. **Follow setup instructions** in `MIGRATION_SETUP_INSTRUCTIONS.md`

### Option 2: Manual Migration

If you prefer to manually create the migration package:

1. **Create a new directory** for migration:
   ```bash
   mkdir opic_portal_migration
   cd opic_portal_migration
   ```

2. **Copy necessary files** (excluding venv, __pycache__, logs):
   ```bash
   # Copy source code
   cp -r app/ opic_portal_migration/
   cp -r templates/ opic_portal_migration/
   cp -r static/ opic_portal_migration/
   cp -r scripts/ opic_portal_migration/
   cp -r docs/ opic_portal_migration/
   
   # Copy database
   cp -r instance/ opic_portal_migration/
   
   # Copy uploads (voice files, audio, avatars)
   cp -r uploads/ opic_portal_migration/
   
   # Copy PDF files
   cp -r files/ opic_portal_migration/
   
   # Copy configuration files
   cp config.env.example opic_portal_migration/
   cp requirements.txt opic_portal_migration/
   cp requirements-ai.txt opic_portal_migration/
   cp app.py opic_portal_migration/
   cp setup.py opic_portal_migration/
   cp gunicorn_config.py opic_portal_migration/
   cp Dockerfile opic_portal_migration/
   cp docker-compose.yml opic_portal_migration/
   cp README.md opic_portal_migration/
   ```

3. **Create archive**:
   ```bash
   # ZIP format
   zip -r opic_portal_migration.zip opic_portal_migration/
   
   # Or TAR.GZ format
   tar -czf opic_portal_migration.tar.gz opic_portal_migration/
   ```

## 📦 What's Included in Migration Package

### ✅ Included Files

- **Application Code**: `app/`, `templates/`, `static/`
- **Database**: `instance/opic_portal.db`
- **Uploads**: 
  - `uploads/questions/` - Question audio files (voice files)
  - `uploads/responses/` - User response recordings
  - `uploads/avatars/` - User avatar images
  - `uploads/comments/` - Comment audio files
- **PDF Files**: `files/` - Study materials and resources
- **Scripts**: `scripts/` - Utility scripts
- **Documentation**: `docs/` - Project documentation
- **Configuration**: `config.env.example`, `requirements.txt`, etc.

### ❌ Excluded Files

- **Virtual Environment**: `venv/`, `.venv/` (will be recreated on new server)
- **Python Cache**: `__pycache__/`, `*.pyc` (will be regenerated)
- **Logs**: `logs/` (new logs will be created)
- **IDE Files**: `.vscode/`, `.idea/` (not needed on server)
- **Git Files**: `.git/`, `.gitignore` (not needed on server)
- **OS Files**: `.DS_Store`, `Thumbs.db` (system-specific)

## 🔄 Migration Steps

### Step 1: Prepare Migration Package

**On your current machine:**

1. Run the migration script:
   ```bash
   cd D:\OPP
   python scripts/migrate_project.py
   ```

2. The script will create:
   - `opic_portal_migration_YYYYMMDD_HHMMSS.zip` (or .tar.gz)
   - `opic_portal_migration_YYYYMMDD_HHMMSS_info.json`
   - `MIGRATION_SETUP_INSTRUCTIONS.md`

### Step 2: Transfer to Oracle Cloud VM

**Option A: Using SCP (Recommended)**
```bash
scp opic_portal_migration_*.zip ubuntu@your-vm-ip:/home/ubuntu/
```

**Option B: Using SFTP**
```bash
sftp ubuntu@your-vm-ip
put opic_portal_migration_*.zip /home/ubuntu/
exit
```

**Option C: Using Cloud Storage**
1. Upload to Oracle Cloud Object Storage
2. Download on VM using `curl` or `wget`

### Step 3: Set Up on Oracle Cloud VM

**On Oracle Cloud VM:**

1. **Connect to VM**:
   ```bash
   ssh ubuntu@your-vm-ip
   ```

2. **Extract package**:
   ```bash
   cd ~
   unzip opic_portal_migration_*.zip
   cd opic_portal_migration_*
   ```

3. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv
   ```

4. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements-ai.txt  # If using AI features
   ```

5. **Set up environment variables**:
   ```bash
   cp config.env.example config.env
   nano config.env
   ```

6. **Verify files**:
   ```bash
   # Check database
   ls -lh instance/opic_portal.db
   
   # Check uploads
   ls -R uploads/
   
   # Check PDF files
   ls -lh files/
   ```

7. **Set permissions**:
   ```bash
   chmod -R 755 uploads/
   chmod -R 755 instance/
   ```

8. **Run application**:
   ```bash
   python app.py
   # Or for production:
   gunicorn -c gunicorn_config.py app:app
   ```

## 📊 Migration Checklist

### Pre-Migration

- [ ] Backup current database
- [ ] Verify all uploads are present
- [ ] Check PDF files in `files/` directory
- [ ] Note down environment variables (API keys, etc.)
- [ ] Run migration script to create package

### During Migration

- [ ] Transfer package to Oracle Cloud VM
- [ ] Extract package on VM
- [ ] Install system dependencies
- [ ] Create virtual environment
- [ ] Install Python dependencies
- [ ] Set up environment variables
- [ ] Verify database file exists
- [ ] Verify uploads directory structure
- [ ] Verify PDF files are present
- [ ] Set proper file permissions

### Post-Migration

- [ ] Test application startup
- [ ] Verify database connectivity
- [ ] Test user login/registration
- [ ] Test audio file playback
- [ ] Test PDF file access
- [ ] Test practice mode
- [ ] Test test mode
- [ ] Verify AI features (if configured)
- [ ] Set up production server (gunicorn/nginx)
- [ ] Configure SSL certificate (optional)
- [ ] Set up firewall rules
- [ ] Set up process management (supervisor)
- [ ] Set up backup strategy

## 🔍 Verifying Migration

### Check Database

```bash
# Verify database file exists and has data
ls -lh instance/opic_portal.db

# Check database contents (optional)
python scripts/inspect_db.py
```

### Check Uploads

```bash
# Verify question audio files
ls -lh uploads/questions/english/IM/
ls -lh uploads/questions/english/IH/
ls -lh uploads/questions/english/AL/

# Verify user responses
ls -lh uploads/responses/

# Verify avatars
ls -lh uploads/avatars/

# Verify comments
ls -lh uploads/comments/
```

### Check PDF Files

```bash
# Verify PDF files
ls -lh files/
```

### Test Application

1. **Start application**:
   ```bash
   python app.py
   ```

2. **Access in browser**:
   - Local: `http://localhost:5000`
   - Network: `http://your-vm-ip:5000`

3. **Test features**:
   - User registration/login
   - Practice mode
   - Test mode
   - Audio playback
   - PDF viewing
   - AI chatbot (if configured)

## 🛠️ Troubleshooting

### Database Issues

**Problem**: Database file not found
```bash
# Solution: Verify database file exists
ls -lh instance/opic_portal.db

# If missing, check if it was included in migration package
```

**Problem**: Database permissions error
```bash
# Solution: Fix permissions
chmod 644 instance/opic_portal.db
chown ubuntu:ubuntu instance/opic_portal.db
```

### File Permission Issues

**Problem**: Cannot write to uploads directory
```bash
# Solution: Fix permissions
chmod -R 755 uploads/
chown -R ubuntu:ubuntu uploads/
```

### Audio File Issues

**Problem**: Audio files not playing
```bash
# Solution: Verify audio files exist
ls -R uploads/questions/english/

# Check file permissions
chmod -R 755 uploads/questions/
```

### Python Dependencies Issues

**Problem**: Import errors
```bash
# Solution: Reinstall dependencies
pip install --upgrade -r requirements.txt
pip install --upgrade -r requirements-ai.txt
```

## 📝 Important Notes

### Database

- The SQLite database file (`instance/opic_portal.db`) contains all user data
- Make sure to backup the database before migration
- For production, consider migrating to PostgreSQL

### Uploads

- Voice files in `uploads/questions/` are essential for the application
- User responses in `uploads/responses/` contain user recordings
- Avatar files in `uploads/avatars/` are user profile images
- Comment audio files in `uploads/comments/` are user-uploaded audio comments

### Environment Variables

- Copy `config.env.example` to `config.env`
- Update `SECRET_KEY` with a random string
- Add your `GOOGLE_AI_API_KEY` if using AI features
- For production, set `FLASK_ENV=production` and `FLASK_DEBUG=False`

### File Sizes

- The migration package may be large (several GB) due to audio files
- Consider using compression when transferring
- For very large packages, consider using cloud storage

## 🔐 Security Considerations

1. **Change default passwords** after migration
2. **Use strong SECRET_KEY** in production
3. **Enable HTTPS** for production deployment
4. **Set up firewall rules** to restrict access
5. **Regular backups** of database and uploads
6. **Update dependencies** regularly
7. **Monitor logs** for security issues

## 📞 Support

If you encounter issues during migration:

1. Check application logs: `logs/app.log`
2. Check system logs: `journalctl -u opic-portal`
3. Verify file permissions and ownership
4. Check database file integrity
5. Verify environment variables are set correctly

## 🎉 Post-Migration

After successful migration:

1. ✅ Test all application features
2. ✅ Set up production server (gunicorn + nginx)
3. ✅ Configure SSL certificate
4. ✅ Set up process management (supervisor)
5. ✅ Set up backup strategy
6. ✅ Monitor application performance
7. ✅ Update documentation with new server details

---

**Happy Migrating!** 🚀

For detailed setup instructions, see `MIGRATION_SETUP_INSTRUCTIONS.md`


