# OPIc Practice Portal - Migration Checklist

Use this checklist to ensure a complete migration to Oracle Cloud VM.

## ✅ Pre-Migration Checklist

### Preparation
- [ ] Backup current database: `instance/opic_portal.db`
- [ ] Backup uploads directory: `uploads/`
- [ ] Note down environment variables (API keys, secrets)
- [ ] Verify all voice files are present in `uploads/questions/`
- [ ] Verify PDF files are present in `files/`
- [ ] Check application is working correctly on current machine

### Create Migration Package
- [ ] Run migration script: `python scripts/migrate_project.py`
- [ ] Or run batch file: `create_migration_package.bat` (Windows)
- [ ] Verify package was created: `opic_portal_migration_*.zip` or `*.tar.gz`
- [ ] Check package size (should be several GB if audio files included)
- [ ] Verify `MIGRATION_SETUP_INSTRUCTIONS.md` was created

## ✅ Transfer Checklist

### Transfer Package
- [ ] Get Oracle Cloud VM IP address
- [ ] Get SSH credentials (username, key file)
- [ ] Transfer package using SCP/SFTP/Cloud Storage
- [ ] Verify package was transferred successfully
- [ ] Check package size on VM matches local size

## ✅ Setup on Oracle Cloud VM Checklist

### System Setup
- [ ] Connect to VM via SSH: `ssh ubuntu@your-vm-ip`
- [ ] Update system packages: `sudo apt update && sudo apt upgrade`
- [ ] Install Python 3.8+: `sudo apt install -y python3 python3-pip python3-venv`
- [ ] Install build tools: `sudo apt install -y build-essential python3-dev`

### Extract Package
- [ ] Navigate to home directory: `cd ~`
- [ ] Extract package: `unzip opic_portal_migration_*.zip` or `tar -xzf *.tar.gz`
- [ ] Navigate to extracted directory: `cd opic_portal_migration_*`
- [ ] Verify all files were extracted

### Virtual Environment
- [ ] Create virtual environment: `python3 -m venv venv`
- [ ] Activate virtual environment: `source venv/bin/activate`
- [ ] Upgrade pip: `pip install --upgrade pip`
- [ ] Install requirements: `pip install -r requirements.txt`
- [ ] Install AI requirements: `pip install -r requirements-ai.txt` (if using AI)

### Configuration
- [ ] Copy config example: `cp config.env.example config.env`
- [ ] Edit config file: `nano config.env`
- [ ] Set `SECRET_KEY` to a random string
- [ ] Set `GOOGLE_AI_API_KEY` (if using AI features)
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Save and exit editor

### Verify Files
- [ ] Check database exists: `ls -lh instance/opic_portal.db`
- [ ] Check database size (should match original)
- [ ] Check uploads directory: `ls -R uploads/`
- [ ] Verify question audio files: `ls -lh uploads/questions/english/IM/`
- [ ] Verify response files: `ls -lh uploads/responses/`
- [ ] Verify avatar files: `ls -lh uploads/avatars/`
- [ ] Verify PDF files: `ls -lh files/`

### Permissions
- [ ] Set uploads permissions: `chmod -R 755 uploads/`
- [ ] Set instance permissions: `chmod -R 755 instance/`
- [ ] Set files permissions: `chmod -R 755 files/`
- [ ] Set static permissions: `chmod -R 755 static/`
- [ ] Create logs directory: `mkdir -p logs`
- [ ] Set logs permissions: `chmod -R 755 logs/`

### Test Application
- [ ] Start application: `python app.py`
- [ ] Check for errors in console
- [ ] Access application: `http://your-vm-ip:5000`
- [ ] Test user registration
- [ ] Test user login
- [ ] Test practice mode
- [ ] Test test mode
- [ ] Test audio playback
- [ ] Test PDF viewing
- [ ] Test AI chatbot (if configured)
- [ ] Test comment system
- [ ] Test avatar upload

## ✅ Production Setup Checklist

### Gunicorn Setup
- [ ] Install gunicorn: `pip install gunicorn`
- [ ] Test gunicorn: `gunicorn -c gunicorn_config.py app:app`
- [ ] Verify application works with gunicorn

### Supervisor Setup (Optional)
- [ ] Install supervisor: `sudo apt install -y supervisor`
- [ ] Create supervisor config: `sudo nano /etc/supervisor/conf.d/opic-portal.conf`
- [ ] Configure supervisor (see MIGRATION_SETUP_INSTRUCTIONS.md)
- [ ] Reload supervisor: `sudo supervisorctl reread && sudo supervisorctl update`
- [ ] Start application: `sudo supervisorctl start opic-portal`
- [ ] Check status: `sudo supervisorctl status opic-portal`

### Nginx Setup (Optional)
- [ ] Install nginx: `sudo apt install -y nginx`
- [ ] Create nginx config: `sudo nano /etc/nginx/sites-available/opic-portal`
- [ ] Configure nginx (see MIGRATION_SETUP_INSTRUCTIONS.md)
- [ ] Enable site: `sudo ln -s /etc/nginx/sites-available/opic-portal /etc/nginx/sites-enabled/`
- [ ] Test config: `sudo nginx -t`
- [ ] Restart nginx: `sudo systemctl restart nginx`

### SSL Setup (Optional)
- [ ] Install certbot: `sudo apt install -y certbot python3-certbot-nginx`
- [ ] Obtain certificate: `sudo certbot --nginx -d your-domain.com`
- [ ] Verify SSL works: `https://your-domain.com`
- [ ] Test auto-renewal: `sudo certbot renew --dry-run`

### Firewall Setup
- [ ] Allow HTTP: `sudo ufw allow 80/tcp`
- [ ] Allow HTTPS: `sudo ufw allow 443/tcp`
- [ ] Allow SSH: `sudo ufw allow 22/tcp`
- [ ] Enable firewall: `sudo ufw enable`
- [ ] Check status: `sudo ufw status`

## ✅ Post-Migration Checklist

### Functionality Tests
- [ ] User registration works
- [ ] User login works
- [ ] Password reset works (if configured)
- [ ] Practice mode works
- [ ] Test mode works
- [ ] Audio recording works
- [ ] Audio playback works
- [ ] PDF viewing works
- [ ] AI chatbot works (if configured)
- [ ] AI scoring works (if configured)
- [ ] Comment system works
- [ ] Avatar upload works
- [ ] Notifications work
- [ ] Admin panel accessible
- [ ] Admin features work

### Data Verification
- [ ] All users migrated (check user count)
- [ ] All questions migrated (check question count)
- [ ] All responses migrated (check response count)
- [ ] All comments migrated (check comment count)
- [ ] All audio files play correctly
- [ ] All PDF files accessible
- [ ] All avatars display correctly

### Performance Tests
- [ ] Application starts quickly
- [ ] Pages load quickly
- [ ] Audio files load quickly
- [ ] Database queries are fast
- [ ] No memory leaks
- [ ] No error logs

### Security Checks
- [ ] Changed default admin password
- [ ] Using strong SECRET_KEY
- [ ] HTTPS enabled (if applicable)
- [ ] Firewall configured
- [ ] Environment variables secure
- [ ] File permissions correct
- [ ] No sensitive data in logs

### Backup Strategy
- [ ] Database backup configured
- [ ] Uploads backup configured
- [ ] Backup schedule set up
- [ ] Backup location configured
- [ ] Test backup restoration

### Monitoring
- [ ] Log monitoring set up
- [ ] Error tracking configured
- [ ] Performance monitoring set up
- [ ] Uptime monitoring configured
- [ ] Alert system configured

## ✅ Final Verification

### Complete System Test
- [ ] Run full test suite (if available)
- [ ] Test all user workflows
- [ ] Test all admin workflows
- [ ] Test edge cases
- [ ] Test error handling
- [ ] Test recovery procedures

### Documentation
- [ ] Update deployment documentation
- [ ] Update server IP/domain in docs
- [ ] Update environment variables in docs
- [ ] Document any custom configurations
- [ ] Document backup procedures
- [ ] Document monitoring procedures

### Handoff
- [ ] Verify all team members have access
- [ ] Share credentials securely
- [ ] Share documentation
- [ ] Schedule training (if needed)
- [ ] Set up support channels

## 🎉 Migration Complete!

Once all items are checked, your migration is complete!

### Next Steps
1. Monitor application for first few days
2. Set up regular backups
3. Monitor performance
4. Update documentation as needed
5. Plan for future updates

---

**Migration Date**: _______________
**Migrated By**: _______________
**Oracle Cloud VM IP**: _______________
**Domain**: _______________

---

For detailed instructions, see:
- `MIGRATION_GUIDE.md` - Complete migration guide
- `MIGRATION_SETUP_INSTRUCTIONS.md` - Detailed setup instructions


