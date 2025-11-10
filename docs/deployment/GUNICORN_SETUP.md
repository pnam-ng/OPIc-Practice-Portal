# Gunicorn Setup Guide

## Problem

When running `gunicorn --bind 0.0.0.0:5000 app:app`, you may get this error:
```
Failed to find attribute 'app' in 'app'.
```

This happens because Python's import system prefers the `app/` package directory over the `app.py` file, and `app/__init__.py` doesn't export an `app` instance.

## Solution

Use the `wsgi.py` file as the WSGI entry point instead of `app:app`.

## Quick Start

### Option 1: Using Gunicorn Config File (Recommended)

```bash
gunicorn -c gunicorn_config.py wsgi:application
```

### Option 2: Direct Command

```bash
gunicorn wsgi:application --bind 0.0.0.0:5000 --workers 4 --timeout 120
```

### Option 3: Using Startup Script

```bash
chmod +x start_gunicorn.sh
./start_gunicorn.sh
```

## What is wsgi.py?

The `wsgi.py` file is a WSGI entry point that:
1. Explicitly imports `app.py` (avoiding conflicts with `app/` package)
2. Exports the Flask application as `application` (standard WSGI interface)
3. Works seamlessly with Gunicorn

## Verification

After starting Gunicorn, you should see:
```
[INFO] Starting gunicorn 22.0.0
[INFO] Listening at: http://0.0.0.0:5000
[INFO] Using worker: sync
[INFO] Booting worker with pid: XXXX
✅ Gunicorn server is ready to handle requests
```

## Troubleshooting

### Error: "Failed to find attribute 'app' in 'app'"

**Solution**: Use `wsgi:application` instead of `app:app`

```bash
# Wrong
gunicorn app:app --bind 0.0.0.0:5000

# Correct
gunicorn wsgi:application --bind 0.0.0.0:5000
```

### Error: "ModuleNotFoundError: No module named 'app'"

**Solution**: Make sure you're in the project root directory and virtual environment is activated

```bash
cd /path/to/opic-portal
source venv/bin/activate
gunicorn wsgi:application --bind 0.0.0.0:5000
```

### Error: "ImportError: cannot import name 'db' from 'app'"

**Solution**: This indicates a circular import issue. The `wsgi.py` file handles this correctly.

### Error: "Permission denied" for logs directory

**Solution**: Create logs directory with proper permissions

```bash
mkdir -p logs
chmod 755 logs
```

## Production Deployment

For production, use the gunicorn config file:

```bash
gunicorn -c gunicorn_config.py wsgi:application
```

This will:
- Use optimal worker configuration
- Enable logging to files
- Set proper timeouts
- Configure process management

## Running as a Service

### Using Supervisor

Create `/etc/supervisor/conf.d/opic-portal.conf`:

```ini
[program:opic-portal]
command=/path/to/venv/bin/gunicorn -c gunicorn_config.py wsgi:application
directory=/path/to/opic-portal
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/path/to/opic-portal/logs/gunicorn.log
```

Then:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start opic-portal
```

### Using Systemd

Create `/etc/systemd/system/opic-portal.service`:

```ini
[Unit]
Description=OPIc Practice Portal Gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/path/to/opic-portal
ExecStart=/path/to/venv/bin/gunicorn -c gunicorn_config.py wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable opic-portal
sudo systemctl start opic-portal
```

## Testing

After starting Gunicorn, test the application:

```bash
# Test locally
curl http://localhost:5000

# Test from network
curl http://your-server-ip:5000
```

## Logs

Check Gunicorn logs:

```bash
# Access logs
tail -f logs/access.log

# Error logs
tail -f logs/error.log

# Combined
tail -f logs/access.log logs/error.log
```

## Performance Tuning

### Worker Configuration

Edit `gunicorn_config.py`:

```python
# For CPU-bound applications
workers = multiprocessing.cpu_count() * 2 + 1

# For I/O-bound applications (like web apps)
workers = multiprocessing.cpu_count() * 4 + 1
worker_class = 'gevent'  # Requires: pip install gevent
```

### Timeout Settings

```python
timeout = 120  # Increase for long-running requests
keepalive = 5  # Keep connections alive
```

## Security

1. **Run as non-root user**: Set `user` and `group` in config
2. **Bind to specific interface**: Use `127.0.0.1` if behind reverse proxy
3. **Use reverse proxy**: Nginx or Apache in front of Gunicorn
4. **Enable HTTPS**: Use SSL certificates with reverse proxy
5. **Firewall**: Only allow necessary ports

## Next Steps

1. Set up Nginx reverse proxy
2. Configure SSL certificates
3. Set up process management (Supervisor/Systemd)
4. Configure log rotation
5. Set up monitoring

---

For more information, see:
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Flask Deployment Options](https://flask.palletsprojects.com/en/latest/deploying/)

