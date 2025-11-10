# Quick Fix: Chatbot API Key Error

## Problem
Error: `Chatbot API key not configured. Please contact administrator.`

## Solution

### If you already have an env file:

The application will automatically load from:
1. `config.env` (preferred)
2. `.env` 
3. `env` (your current file)

**Your `env` file should work!** Just restart Gunicorn:

```bash
# Restart Gunicorn to reload environment variables
pkill -f gunicorn
gunicorn -c gunicorn_config.py wsgi:application
```

### Verify your env file has the API key:

```bash
# Check if API key is in your env file
grep GOOGLE_AI_API_KEY env
```

### If you need to create a new env file:

```bash
# 1. Navigate to project directory
cd ~/opp

# 2. Create config.env from example (optional)
cp config.env.example config.env

# 3. Or create/edit your existing env file
nano env
```

### In your env file, make sure you have:

```env
GOOGLE_AI_API_KEY=your-api-key-here
```

### Get your FREE API key:

1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the API key
5. Paste it in config.env

### Restart Gunicorn:

```bash
# Stop current Gunicorn
pkill -f gunicorn

# Start again
gunicorn -c gunicorn_config.py wsgi:application
```

## Verify it works:

1. Refresh your browser
2. Try the chatbot
3. It should work now!

## Alternative: Quick Setup Script

```bash
# Run the setup script
python scripts/setup_env.py

# Then edit config.env to add your API key
nano config.env
```

## Need Help?

See [SETUP_ENVIRONMENT_VARIABLES.md](docs/deployment/SETUP_ENVIRONMENT_VARIABLES.md) for detailed instructions.

