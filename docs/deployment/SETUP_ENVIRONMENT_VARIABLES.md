# Setting Up Environment Variables on Oracle Cloud VM

## Quick Setup

### Supported Environment File Names

The application will automatically load environment variables from (in order):
1. `config.env` (preferred)
2. `.env`
3. `env`

**If you already have an `env` file, it will work!** Just restart Gunicorn after making changes.

### Step 1: Check if you already have an env file

```bash
cd ~/opp
ls -la | grep -E "(config.env|\.env|^env$)"
```

### Step 2: Create or edit environment file

**If you have an `env` file:**
```bash
nano env
```

**If you need to create a new file:**
```bash
cp config.env.example config.env
nano config.env
```

### Step 3: Set Required Variables

At minimum, you need:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-this-to-random-string
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration
DATABASE_URL=sqlite:///instance/opic_portal.db

# Google AI Studio (Gemini) Configuration - REQUIRED for AI features
# Get your FREE API key: https://aistudio.google.com/app/apikey
GOOGLE_AI_API_KEY=your-google-ai-api-key-here

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
```

### Step 4: Generate Secret Key

```bash
# Generate a random secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and use it as your `SECRET_KEY`.

### Step 5: Get Google AI API Key

1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key
5. Add it to `config.env` as `GOOGLE_AI_API_KEY`

### Step 6: Verify Environment Variables

```bash
# Test if variables are loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv('config.env'); print('GOOGLE_AI_API_KEY:', 'SET' if os.getenv('GOOGLE_AI_API_KEY') else 'NOT SET')"
```

### Step 7: Restart Gunicorn

```bash
# If running with Gunicorn, restart it
pkill -f gunicorn
gunicorn -c gunicorn_config.py wsgi:application
```

## Alternative: Using System Environment Variables

If you prefer to use system environment variables instead of config.env:

### Option 1: Export in shell session

```bash
export GOOGLE_AI_API_KEY=your-api-key-here
export SECRET_KEY=your-secret-key-here
gunicorn -c gunicorn_config.py wsgi:application
```

### Option 2: Add to ~/.bashrc or ~/.profile

```bash
# Add to ~/.bashrc
echo 'export GOOGLE_AI_API_KEY=your-api-key-here' >> ~/.bashrc
echo 'export SECRET_KEY=your-secret-key-here' >> ~/.bashrc
source ~/.bashrc
```

### Option 3: Use systemd service (for production)

Create `/etc/systemd/system/opic-portal.service`:

```ini
[Unit]
Description=OPIc Practice Portal
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/opp
Environment="GOOGLE_AI_API_KEY=your-api-key-here"
Environment="SECRET_KEY=your-secret-key-here"
Environment="FLASK_ENV=production"
ExecStart=/home/ubuntu/opp/venv/bin/gunicorn -c gunicorn_config.py wsgi:application
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

## Verification

### Check if API key is loaded

```bash
# Test in Python
python -c "
from dotenv import load_dotenv
import os
load_dotenv('config.env')
api_key = os.getenv('GOOGLE_AI_API_KEY')
if api_key:
    print(f'✅ API key is set: {api_key[:10]}...')
else:
    print('❌ API key is NOT set')
"
```

### Test chatbot endpoint

```bash
# Test chatbot (requires authentication)
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## Troubleshooting

### Error: Chatbot API key not configured

**Solution**: Make sure `GOOGLE_AI_API_KEY` is set in `config.env` and the file is in the project root.

### Error: Environment variables not loading

**Solution**: 
1. Check if `python-dotenv` is installed: `pip install python-dotenv`
2. Verify `config.env` file exists in project root
3. Check file permissions: `chmod 644 config.env`

### Error: API key invalid

**Solution**:
1. Verify API key is correct (no extra spaces)
2. Check if API key is enabled in Google AI Studio
3. Verify you're using the correct API key (not a placeholder)

## Security Notes

1. **Never commit config.env to git** - It's already in `.gitignore`
2. **Use strong SECRET_KEY** - Generate a random 32+ character string
3. **Restrict file permissions** - `chmod 600 config.env` (only owner can read/write)
4. **Don't share API keys** - Keep them private and secure

## Complete Example config.env

```env
# Flask Configuration
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration
DATABASE_URL=sqlite:///instance/opic_portal.db

# Google AI Studio (Gemini) Configuration
GOOGLE_AI_API_KEY=AIzaSyCxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
ALLOWED_EXTENSIONS={'mp3', 'wav', 'webm', 'ogg', 'm4a'}

# Audio Configuration
AUDIO_SAMPLE_RATE=44100
AUDIO_CHANNELS=1
AUDIO_FORMAT=webm
```

## Next Steps

After setting up environment variables:

1. ✅ Restart Gunicorn server
2. ✅ Test chatbot functionality
3. ✅ Verify AI features work
4. ✅ Check application logs for any errors

For more information, see:
- [Gunicorn Setup](GUNICORN_SETUP.md)
- [Migration Guide](MIGRATION_GUIDE.md)

