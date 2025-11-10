#!/usr/bin/env python3
"""
Migration Script for OPIc Practice Portal
Creates a migration package with all necessary files for deployment to a new server.

This script:
1. Creates a migration package excluding unnecessary files
2. Includes database, uploads, files, and all source code
3. Generates setup instructions for the new server
"""

import os
import shutil
import tarfile
import zipfile
import json
from pathlib import Path
from datetime import datetime

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Directories and files to EXCLUDE from migration
EXCLUDE_PATTERNS = [
    # Python cache
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.Python',
    
    # Virtual environment
    'venv/',
    '.venv/',
    'env/',
    '.env/',
    'ENV/',
    
    # IDE
    '.vscode/',
    '.idea/',
    '*.swp',
    '*.swo',
    '*~',
    
    # OS files
    '.DS_Store',
    'Thumbs.db',
    'ehthumbs.db',
    'Desktop.ini',
    
    # Logs
    'logs/',
    '*.log',
    
    # Temporary files
    'tmp/',
    'temp/',
    
    # Git
    '.git/',
    '.gitignore',
    '.gitattributes',
    
    # Documentation backups (optional - uncomment if you don't want to migrate)
    # 'transcription_backups/',
    
    # Old backup folders (if you want to exclude them)
    # 'OPIC_Voices/',
    # 'OPIC Multicampus_AL/',
    # 'OPIC_Voices_Organized/',
    # 'question_data/',
]

# Directories and files to INCLUDE (even if they match exclude patterns)
INCLUDE_ALWAYS = [
    'instance/opic_portal.db',  # Database must be included
    'uploads/',  # All uploads must be included
    'files/',  # PDF files must be included
    'static/',  # Static files must be included
    'templates/',  # Templates must be included
    'app/',  # Application code must be included
    'scripts/',  # Scripts must be included
    'docs/',  # Documentation
    'config.env.example',
    'requirements.txt',
    'requirements-ai.txt',
    'requirements-dev.txt',
    'app.py',
    'setup.py',
    'setup.bat',
    'setup_hf_token.bat',
    'install_ai.bat',
    'install_ai.sh',
    'gunicorn_config.py',
    'Dockerfile',
    'docker-compose.yml',
    'docker-compose.prod.yml',
    'README.md',
    'PROJECT_STRUCTURE.md',
    'LICENSE',
    '.env.example',  # Include example config
]

def should_exclude(path, root_path):
    """Check if a file or directory should be excluded"""
    rel_path = os.path.relpath(path, root_path)
    rel_path_normalized = rel_path.replace('\\', '/')
    
    # Check if it's in the always include list
    for include_pattern in INCLUDE_ALWAYS:
        if rel_path_normalized.startswith(include_pattern) or rel_path_normalized == include_pattern:
            return False
    
    # Check exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        # Remove trailing slash for directory patterns
        pattern_clean = pattern.rstrip('/')
        
        # Check if path matches pattern
        if pattern_clean in rel_path_normalized.split('/'):
            return True
        if pattern_clean in rel_path_normalized.split('\\'):
            return True
        # Check wildcard patterns
        if '*' in pattern:
            import fnmatch
            if fnmatch.fnmatch(rel_path_normalized, pattern):
                return True
            if fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
    
    return False

def get_file_size_mb(path):
    """Get file size in MB"""
    if os.path.isfile(path):
        return os.path.getsize(path) / (1024 * 1024)
    elif os.path.isdir(path):
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.isfile(filepath):
                    total += os.path.getsize(filepath)
        return total / (1024 * 1024)
    return 0

def create_migration_package(output_format='zip'):
    """Create a migration package with all necessary files"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    package_name = f'opic_portal_migration_{timestamp}'
    
    if output_format == 'zip':
        package_path = PROJECT_ROOT / f'{package_name}.zip'
        archive = zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED)
    elif output_format == 'tar':
        package_path = PROJECT_ROOT / f'{package_name}.tar.gz'
        archive = tarfile.open(package_path, 'w:gz')
    else:
        raise ValueError(f"Unsupported format: {output_format}")
    
    # Statistics
    stats = {
        'files_included': 0,
        'files_excluded': 0,
        'total_size_mb': 0,
        'directories': []
    }
    
    print("📦 Creating migration package...")
    print(f"📁 Source: {PROJECT_ROOT}")
    print(f"📦 Output: {package_path}")
    print("\n🔍 Scanning files...")
    
    # Walk through project directory
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), PROJECT_ROOT)]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip the migration package itself
            if file_path == str(package_path):
                continue
            
            if should_exclude(file_path, PROJECT_ROOT):
                stats['files_excluded'] += 1
                continue
            
            # Get relative path for archive
            arcname = os.path.relpath(file_path, PROJECT_ROOT)
            
            try:
                if output_format == 'zip':
                    archive.write(file_path, arcname)
                else:
                    archive.add(file_path, arcname=arcname)
                
                stats['files_included'] += 1
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                stats['total_size_mb'] += file_size
                
                if stats['files_included'] % 100 == 0:
                    print(f"  ✓ Processed {stats['files_included']} files...")
                    
            except Exception as e:
                print(f"  ⚠️  Warning: Could not add {arcname}: {e}")
                stats['files_excluded'] += 1
    
    archive.close()
    
    # Get final package size
    package_size_mb = os.path.getsize(package_path) / (1024 * 1024)
    
    print(f"\n✅ Migration package created successfully!")
    print(f"📦 Package: {package_path}")
    print(f"📊 Package size: {package_size_mb:.2f} MB")
    print(f"📁 Files included: {stats['files_included']}")
    print(f"🚫 Files excluded: {stats['files_excluded']}")
    print(f"💾 Total content size: {stats['total_size_mb']:.2f} MB")
    
    return package_path, stats, package_size_mb

def generate_migration_info(package_path, stats, package_size_mb):
    """Generate migration information file"""
    
    info = {
        'package_name': os.path.basename(package_path),
        'package_size_mb': round(package_size_mb, 2),
        'created_at': datetime.now().isoformat(),
        'files_included': stats['files_included'],
        'files_excluded': stats['files_excluded'],
        'database_included': True,
        'uploads_included': True,
        'migration_steps': [
            '1. Transfer the migration package to the Oracle Cloud VM',
            '2. Extract the package on the VM',
            '3. Install Python 3.8+ and required dependencies',
            '4. Create virtual environment and install requirements',
            '5. Set up environment variables (config.env)',
            '6. Verify database file exists in instance/ directory',
            '7. Verify uploads directory structure',
            '8. Run the application',
            '9. Test the application functionality'
        ]
    }
    
    info_path = PROJECT_ROOT / f'{os.path.splitext(os.path.basename(package_path))[0]}_info.json'
    
    with open(info_path, 'w') as f:
        json.dump(info, f, indent=2)
    
    print(f"\n📄 Migration info saved: {info_path}")
    
    return info_path

def generate_setup_instructions():
    """Generate setup instructions for Oracle Cloud VM"""
    
    instructions = """# OPIc Practice Portal - Migration Setup Instructions for Oracle Cloud VM

## Prerequisites

1. **Oracle Cloud VM** with:
   - Ubuntu 20.04 LTS or later (recommended)
   - At least 2 GB RAM
   - At least 10 GB disk space
   - Python 3.8+ installed
   - SSH access configured

2. **Required Software**:
   - Python 3.8+
   - pip
   - git (optional)
   - nginx (for production, optional)
   - supervisor (for process management, optional)

## Step 1: Transfer Migration Package

### Option A: Using SCP (Recommended)
```bash
# From your local machine
scp opic_portal_migration_*.zip ubuntu@your-vm-ip:/home/ubuntu/

# Or using Windows PowerShell
scp opic_portal_migration_*.zip ubuntu@your-vm-ip:/home/ubuntu/
```

### Option B: Using SFTP
```bash
# Connect via SFTP
sftp ubuntu@your-vm-ip

# Upload file
put opic_portal_migration_*.zip /home/ubuntu/

# Exit
exit
```

### Option C: Using Cloud Storage
1. Upload package to Oracle Cloud Object Storage
2. Download on VM using `curl` or `wget`

## Step 2: Connect to Oracle Cloud VM

```bash
ssh ubuntu@your-vm-ip
```

## Step 3: Extract Migration Package

```bash
# Navigate to home directory
cd ~

# Extract the package
unzip opic_portal_migration_*.zip

# Or if using tar.gz
tar -xzf opic_portal_migration_*.tar.gz

# Navigate to extracted directory
cd opic_portal_migration_*
```

## Step 4: Install System Dependencies

```bash
# Update package list
sudo apt update

# Install Python and pip (if not already installed)
sudo apt install -y python3 python3-pip python3-venv

# Install additional system dependencies (if needed)
sudo apt install -y build-essential python3-dev libpq-dev
```

## Step 5: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

## Step 6: Install Python Dependencies

```bash
# Install base requirements
pip install -r requirements.txt

# Install AI requirements (optional, if using AI features)
pip install -r requirements-ai.txt

# Install dev requirements (optional, for development)
# pip install -r requirements-dev.txt
```

## Step 7: Set Up Environment Variables

```bash
# Copy example config
cp config.env.example config.env

# Edit config file
nano config.env
```

### Required Environment Variables:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-this
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration
DATABASE_URL=sqlite:///instance/opic_portal.db

# Google AI Studio (Gemini) Configuration
GOOGLE_AI_API_KEY=your-google-ai-api-key

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=uploads
ALLOWED_EXTENSIONS={'mp3', 'wav', 'webm', 'ogg', 'm4a'}

# Audio Configuration
AUDIO_SAMPLE_RATE=44100
AUDIO_CHANNELS=1
AUDIO_FORMAT=webm
```

**Important**: 
- Change `SECRET_KEY` to a random string
- Add your `GOOGLE_AI_API_KEY` if using AI features
- For production, consider using PostgreSQL instead of SQLite

## Step 8: Verify Database and Files

```bash
# Check if database exists
ls -lh instance/opic_portal.db

# Check uploads directory structure
ls -R uploads/

# Check files directory (PDFs)
ls -lh files/

# Verify directory permissions
chmod -R 755 uploads/
chmod -R 755 instance/
```

## Step 9: Set Up Directory Permissions

```bash
# Ensure proper permissions
chmod -R 755 uploads/
chmod -R 755 instance/
chmod -R 755 static/
chmod -R 755 files/

# Create necessary directories if they don't exist
mkdir -p uploads/avatars
mkdir -p uploads/questions
mkdir -p uploads/responses
mkdir -p uploads/comments
mkdir -p instance
mkdir -p logs
```

## Step 10: Test the Application

```bash
# Run the application in development mode
python app.py

# Or use gunicorn for production
gunicorn -c gunicorn_config.py app:app
```

### Access the Application

- **Local**: http://localhost:5000
- **Network**: http://your-vm-ip:5000

## Step 11: Set Up Production Server (Optional)

### Using Gunicorn

```bash
# Install gunicorn (if not already installed)
pip install gunicorn

# Run with gunicorn
gunicorn -c gunicorn_config.py app:app --bind 0.0.0.0:5000
```

### Using Supervisor (Process Management)

```bash
# Install supervisor
sudo apt install -y supervisor

# Create supervisor configuration
sudo nano /etc/supervisor/conf.d/opic-portal.conf
```

Add the following configuration:

```ini
[program:opic-portal]
command=/home/ubuntu/opic_portal_migration_*/venv/bin/gunicorn -c gunicorn_config.py app:app
directory=/home/ubuntu/opic_portal_migration_*
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/ubuntu/opic_portal_migration_*/logs/gunicorn.log
```

```bash
# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start opic-portal
```

### Using Nginx (Reverse Proxy)

```bash
# Install nginx
sudo apt install -y nginx

# Create nginx configuration
sudo nano /etc/nginx/sites-available/opic-portal
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static {
        alias /home/ubuntu/opic_portal_migration_*/static;
    }

    # Uploads
    location /uploads {
        alias /home/ubuntu/opic_portal_migration_*/uploads;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/opic-portal /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## Step 12: Set Up SSL Certificate (Optional)

### Using Let's Encrypt (Free SSL)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
```

## Step 13: Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH (if not already allowed)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## Step 14: Verify Migration

### Check Database
```bash
# Verify database has data
python scripts/inspect_db.py
```

### Check Files
```bash
# Verify uploads directory
ls -lh uploads/questions/english/
ls -lh uploads/responses/
ls -lh uploads/avatars/

# Verify PDF files
ls -lh files/
```

### Test Application
1. Access the application in browser
2. Register a new user or login with existing admin account
3. Test practice mode
4. Test test mode
5. Verify audio files play correctly
6. Verify PDF files are accessible

## Troubleshooting

### Database Issues
```bash
# Check database file permissions
ls -l instance/opic_portal.db

# Fix permissions if needed
chmod 644 instance/opic_portal.db
```

### File Permission Issues
```bash
# Fix uploads directory permissions
chmod -R 755 uploads/
chown -R ubuntu:ubuntu uploads/
```

### Port Already in Use
```bash
# Check what's using port 5000
sudo lsof -i :5000

# Kill the process if needed
sudo kill -9 <PID>
```

### Application Won't Start
```bash
# Check logs
tail -f logs/app.log

# Check Python version
python3 --version

# Verify virtual environment is activated
which python
```

## Post-Migration Checklist

- [ ] Database migrated successfully
- [ ] All uploads directory files present
- [ ] PDF files in files/ directory
- [ ] Environment variables configured
- [ ] Application starts without errors
- [ ] Audio files play correctly
- [ ] PDF files are accessible
- [ ] User authentication works
- [ ] Admin panel accessible
- [ ] AI features work (if configured)
- [ ] SSL certificate configured (if using HTTPS)
- [ ] Firewall configured
- [ ] Process management set up (supervisor/systemd)
- [ ] Logs directory writable
- [ ] Backup strategy in place

## Additional Notes

1. **Database Backup**: Regularly backup the database file:
   ```bash
   cp instance/opic_portal.db instance/opic_portal.db.backup
   ```

2. **File Backups**: Backup uploads directory regularly:
   ```bash
   tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
   ```

3. **Log Rotation**: Set up log rotation for application logs

4. **Monitoring**: Consider setting up monitoring for the application

5. **Updates**: Keep the system and dependencies updated:
   ```bash
   sudo apt update && sudo apt upgrade
   pip install --upgrade -r requirements.txt
   ```

## Support

If you encounter any issues during migration, check:
- Application logs: `logs/app.log`
- Gunicorn logs: `logs/gunicorn.log`
- System logs: `journalctl -u opic-portal`
- Nginx logs: `/var/log/nginx/error.log`

## Security Recommendations

1. Change default admin password after migration
2. Use strong SECRET_KEY
3. Enable HTTPS in production
4. Regularly update dependencies
5. Set up firewall rules
6. Use environment variables for sensitive data
7. Regular backups
8. Monitor application logs

---

**Migration completed successfully!** 🎉
"""
    
    instructions_path = PROJECT_ROOT / 'MIGRATION_SETUP_INSTRUCTIONS.md'
    
    with open(instructions_path, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"📖 Setup instructions saved: {instructions_path}")
    
    return instructions_path

def main():
    """Main function"""
    print("=" * 60)
    print("OPIc Practice Portal - Migration Package Creator")
    print("=" * 60)
    print()
    
    # Ask user for format
    print("Select package format:")
    print("1. ZIP (recommended for Windows)")
    print("2. TAR.GZ (recommended for Linux)")
    
    choice = input("Enter choice (1 or 2, default: 1): ").strip()
    
    if choice == '2':
        output_format = 'tar'
        print("\n📦 Creating TAR.GZ package...")
    else:
        output_format = 'zip'
        print("\n📦 Creating ZIP package...")
    
    # Create migration package
    package_path, stats, package_size_mb = create_migration_package(output_format)
    
    # Generate migration info
    info_path = generate_migration_info(package_path, stats, package_size_mb)
    
    # Generate setup instructions
    instructions_path = generate_setup_instructions()
    
    print("\n" + "=" * 60)
    print("✅ Migration package created successfully!")
    print("=" * 60)
    print(f"\n📦 Package: {package_path}")
    print(f"📄 Info: {info_path}")
    print(f"📖 Instructions: {instructions_path}")
    print(f"\n💡 Next steps:")
    print(f"   1. Transfer {os.path.basename(package_path)} to Oracle Cloud VM")
    print(f"   2. Follow instructions in MIGRATION_SETUP_INSTRUCTIONS.md")
    print(f"   3. Extract and set up on the new server")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()


