# Gunicorn Troubleshooting Guide

## Permission Errors

### Error: 'logs/error.log' isn't writable [PermissionError(13, 'Permission denied')]

**Cause**: The `logs` directory doesn't exist or doesn't have write permissions.

**Solution**:

```bash
# Create logs directory
mkdir -p logs

# Set proper permissions
chmod 755 logs

# Or if you need to fix existing directory
sudo chmod 755 logs
sudo chown $USER:$USER logs
```

**Alternative**: If you can't create the logs directory, Gunicorn will automatically fall back to stdout/stderr for logging.

### Error: Cannot write PID file

**Solution**: Same as above - ensure logs directory is writable, or Gunicorn will skip creating the PID file.

## Other Common Issues

### Error: Address already in use

**Cause**: Port 5000 is already in use by another process.

**Solution**:
```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill the process
sudo kill -9 <PID>

# Or use a different port
gunicorn wsgi:application --bind 0.0.0.0:8000
```

### Error: Module not found

**Cause**: Virtual environment not activated or dependencies not installed.

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify wsgi.py exists
ls -la wsgi.py
```

### Error: Failed to find attribute 'app' in 'app'

**Cause**: Using `app:app` instead of `wsgi:application`.

**Solution**: Always use `wsgi:application`:
```bash
gunicorn wsgi:application --bind 0.0.0.0:5000
```

### Error: Worker timeout

**Cause**: Requests taking too long to process.

**Solution**: Increase timeout in `gunicorn_config.py`:
```python
timeout = 300  # 5 minutes instead of 2 minutes
```

### Error: Too many workers

**Cause**: System doesn't have enough resources.

**Solution**: Reduce number of workers in `gunicorn_config.py`:
```python
workers = 2  # Instead of CPU count * 2 + 1
```

## Debugging

### Check Gunicorn status
```bash
# Check if Gunicorn is running
ps aux | grep gunicorn

# Check logs (if writable)
tail -f logs/error.log
tail -f logs/access.log
```

### Test application directly
```bash
# Test with Python Flask development server
python app.py

# Test WSGI import
python -c "from wsgi import application; print('OK')"
```

### Enable debug mode
```bash
# Run with debug logging
gunicorn wsgi:application --bind 0.0.0.0:5000 --log-level debug
```

## Quick Fixes

### Quick permission fix
```bash
cd ~/opp
mkdir -p logs instance uploads
chmod -R 755 logs instance uploads
```

### Quick test
```bash
# Test if everything works
python -c "from wsgi import application; print('Application loaded successfully')"
gunicorn wsgi:application --bind 127.0.0.1:5000 --workers 1
```

## Getting Help

If you're still experiencing issues:

1. Check the error logs (stdout/stderr if logs directory is not writable)
2. Verify all dependencies are installed
3. Check file permissions
4. Verify database file exists and is readable
5. Check environment variables are set correctly

For more information, see [GUNICORN_SETUP.md](GUNICORN_SETUP.md).

