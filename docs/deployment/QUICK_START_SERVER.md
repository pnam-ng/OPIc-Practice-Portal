# Quick Start - Running on Oracle Cloud VM

## ✅ Fix for Gunicorn Error

If you get this error:
```
Failed to find attribute 'app' in 'app'.
```

**Solution**: Use `wsgi:application` instead of `app:app`

## 🚀 Start the Server

### Method 1: Using WSGI (Recommended)

```bash
gunicorn wsgi:application --bind 0.0.0.0:5000
```

### Method 2: Using Config File

```bash
gunicorn -c gunicorn_config.py wsgi:application
```

### Method 3: Using Startup Script

```bash
chmod +x start_gunicorn.sh
./start_gunicorn.sh
```

## 📝 Complete Setup Steps

1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Create logs directory**:
   ```bash
   mkdir -p logs
   ```

3. **Start Gunicorn**:
   ```bash
   gunicorn wsgi:application --bind 0.0.0.0:5000 --workers 4 --timeout 120
   ```

4. **Verify it's running**:
   ```bash
   curl http://localhost:5000
   ```

## 🔍 Troubleshooting

### Check if wsgi.py exists
```bash
ls -la wsgi.py
```

### Test import
```bash
python -c "from wsgi import application; print('OK')"
```

### Check logs
```bash
tail -f logs/error.log
```

### Check if port is in use
```bash
sudo lsof -i :5000
```

## 📚 More Information

See `GUNICORN_SETUP.md` for detailed documentation.

