# Deployment Guide

## Current Deployment Setup

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Users / Clients                          │
└────────────┬───────────────────────┬────────────────────────┘
             │                       │
      Internal Network          Public Internet
             │                       │
             ▼                       ▼
    ┌──────────────────┐    ┌──────────────────┐
    │  Internal Server │    │   ngrok Tunnel   │
    │  107.98.150.22   │    │  bit.ly/srvopic  │
    │  Port: 8080      │    │                  │
    │  Protocol: HTTPS │    │  Protocol: HTTPS │
    └────────┬─────────┘    └────────┬─────────┘
             │                       │
             └───────────┬───────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Flask Application │
              │   Gunicorn WSGI     │
              │   Port: 5000        │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │   SQLite Database   │
              │   instance/         │
              └─────────────────────┘
```

## Access Points

### 1. Internal Network Access
**URL**: `https://107.98.150.22:8080/`

**For**: Company employees on the internal network

**Setup**:
- Direct server access
- SSL/TLS enabled
- Firewall rules configured
- No external dependencies

**Advantages**:
- Fast access (local network)
- No bandwidth costs
- Direct connection
- Higher security

### 2. Public Access (ngrok)
**Short URL**: `https://bit.ly/srvopic`  
**Full URL**: Dynamically assigned by ngrok

**For**: External users, demos, remote testing

**Setup**:
```bash
# Install ngrok
# Windows: Download from https://ngrok.com/download

# Authenticate (one-time)
ngrok config add-authtoken YOUR_TOKEN

# Start tunnel
ngrok http 5000 --region us
```

**Advantages**:
- No port forwarding needed
- Automatic HTTPS
- Works behind firewalls
- Easy sharing via short URL
- Built-in request inspection
- No DNS configuration

**Service Configuration**:
```bash
# Install as Windows service (included scripts)
install_ngrok_service.bat

# Restart service
restart_ngrok_service.bat

# View logs
logs/ngrok_output.log
logs/ngrok_error.log
```

### 3. Local Development
**URL**: `http://localhost:5000`

**For**: Developers

**Setup**:
```bash
python app.py
```

## Deployment Methods

### Method 1: Direct Python (Development)
```bash
python app.py
```
- Simple and fast
- Auto-reload on code changes
- Single-threaded
- Not recommended for production

### Method 2: Gunicorn (Production)
```bash
gunicorn -c gunicorn_config.py app:app
```
- Production-ready
- Multi-worker support
- Better performance
- Automatic worker restart
- Recommended for production

### Method 3: Docker
```bash
# Build image
docker build -t opic-portal .

# Run container
docker run -d -p 5000:5000 \
  -v $(pwd)/instance:/app/instance \
  -v $(pwd)/uploads:/app/uploads \
  --name opic-portal \
  opic-portal

# With docker-compose
docker-compose up -d
```

## ngrok Configuration

### Basic Setup
```bash
# Start tunnel
ngrok http 5000

# With custom subdomain (paid plan)
ngrok http 5000 --subdomain opic-portal

# With custom domain (paid plan)
ngrok http 5000 --hostname opic.yourdomain.com
```

### Advanced Configuration
Create `ngrok.yml`:
```yaml
version: "2"
authtoken: YOUR_AUTH_TOKEN

tunnels:
  opic-portal:
    proto: http
    addr: 5000
    bind_tls: true
    inspect: true
    region: us
```

Then run:
```bash
ngrok start opic-portal
```

### As Windows Service
The project includes batch scripts for running ngrok as a service:

```bash
# Install service
install_ngrok_service.bat

# Start service
net start ngrok-opic

# Stop service
net stop ngrok-opic

# Restart service
restart_ngrok_service.bat

# Uninstall service
uninstall_ngrok_service.bat
```

## SSL/TLS Configuration

### For Internal Server (107.98.150.22:8080)
1. Generate SSL certificate:
```bash
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem -out cert.pem \
  -days 365 -nodes
```

2. Configure in `app.py`:
```python
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context=('cert.pem', 'key.pem')
    )
```

### For ngrok
SSL is automatic - ngrok provides HTTPS by default!

## Monitoring & Maintenance

### Check Application Status
```bash
# Check if running
curl http://localhost:5000/

# Check ngrok tunnel status
curl http://localhost:4040/api/tunnels
```

### View Logs
```bash
# Application logs
tail -f logs/output.log.txt
tail -f logs/error.log.txt

# ngrok logs
tail -f logs/ngrok_output.log
tail -f logs/ngrok_error.log
```

### Restart Services
```bash
# Restart Flask application
# Windows:
run.bat

# Linux:
./restart.sh

# Restart ngrok tunnel
restart_ngrok_service.bat
```

## Firewall Configuration

### Internal Server
Open ports:
- **8080**: HTTPS application access
- **5000**: Application port (if direct access needed)

### For ngrok
No firewall configuration needed! ngrok creates an outbound connection.

## Performance Optimization

### Gunicorn Workers
```python
# gunicorn_config.py
workers = 4  # (2 x CPU cores) + 1
worker_class = 'sync'
threads = 2
timeout = 120
```

### Database Optimization
```python
# For production, use PostgreSQL instead of SQLite
SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/opic_db'
```

### Caching (Future)
Consider adding Redis for:
- Session storage
- API rate limiting
- Cached queries

## Backup & Recovery

### Database Backup
```bash
# Backup SQLite database
cp instance/opic_portal.db backups/opic_portal_$(date +%Y%m%d).db

# Automated backup script
python scripts/db_export_import.py export backups/
```

### Restore Database
```bash
# Restore from backup
cp backups/opic_portal_20250130.db instance/opic_portal.db

# Or use import script
python scripts/db_export_import.py import backups/opic_portal_20250130.db
```

## Scaling Considerations

### Current Setup (Single Server)
- ✅ Suitable for 10-50 concurrent users
- ✅ SQLite is sufficient
- ✅ Single server deployment

### For Growth (100+ users)
1. **Migrate to PostgreSQL**
2. **Add load balancer**
3. **Multiple application servers**
4. **Separate file storage** (S3/Cloudinary)
5. **CDN for static files**
6. **Redis for caching**

## Troubleshooting

### ngrok Tunnel Not Starting
```bash
# Check ngrok status
ngrok diagnose

# Check auth token
ngrok config check

# View detailed logs
type logs\ngrok_error.log
```

### Internal Server Not Accessible
```bash
# Check if port is open
netstat -an | findstr :8080

# Check firewall
netsh advfirewall show currentprofile

# Test SSL certificate
openssl s_client -connect 107.98.150.22:8080
```

### Application Crashes
```bash
# Check error logs
type logs\error.log.txt

# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Security Checklist

- [x] HTTPS enabled on all endpoints
- [x] Admin password changed from default
- [x] Database backed up regularly
- [x] Logs monitored for errors
- [ ] Rate limiting implemented (future)
- [ ] CSRF protection enabled (future)
- [ ] Input sanitization reviewed
- [ ] File upload size limits configured

## Quick Reference

| Purpose | URL | Protocol | Access |
|---------|-----|----------|--------|
| Internal Users | `https://107.98.150.22:8080/` | HTTPS | Company Network |
| External Users | `https://bit.ly/srvopic` | HTTPS (ngrok) | Public Internet |
| Developers | `http://localhost:5000` | HTTP | Localhost Only |
| ngrok Inspector | `http://localhost:4040` | HTTP | Localhost Only |

---

**Last Updated**: 2025-01-30  
**Maintained By**: Development Team

