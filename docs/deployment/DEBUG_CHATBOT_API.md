# Debugging Chatbot API Issues

## Check Gunicorn Logs

The chatbot service now logs detailed information. Check the logs to see what's happening:

```bash
# Check error logs
tail -f logs/error.log

# Or if using stdout/stderr
# Check the terminal where Gunicorn is running
```

## Common Issues and Solutions

### 1. API Key Not Found

**Symptoms**: Log shows "API Key not found" or "Chatbot API key not configured"

**Solution**:
```bash
# Verify env file exists and has API key
cat env | grep GOOGLE_AI_API_KEY

# Restart Gunicorn
pkill -f gunicorn
gunicorn -c gunicorn_config.py wsgi:application
```

### 2. API Rate Limiting (429 Error)

**Symptoms**: Log shows "Rate limited" or status code 429

**Solution**: 
- The service automatically switches to fallback models
- Wait a few minutes and try again
- Consider upgrading your Google AI API quota

### 3. Quota Exceeded (403 Error)

**Symptoms**: Log shows "Quota exceeded" or "RPD" error

**Solution**:
- Check your Google AI API quota at https://aistudio.google.com/app/apikey
- The service automatically tries fallback models
- Wait for quota to reset (usually daily)

### 4. Invalid API Key (403 Error)

**Symptoms**: Log shows "Invalid API key" or 403 error without quota message

**Solution**:
- Verify API key is correct in `env` file
- Regenerate API key at https://aistudio.google.com/app/apikey
- Restart Gunicorn after updating

### 5. Network/Connection Error

**Symptoms**: Log shows "Connection error" or timeout

**Solution**:
- Check internet connectivity on the server
- Verify firewall allows outbound HTTPS connections
- Check if Google AI API is accessible: `curl https://generativelanguage.googleapis.com`

### 6. API Response Format Error

**Symptoms**: Log shows "No content in Gemini response" or unexpected response structure

**Solution**:
- This is usually a temporary API issue
- Try again in a few moments
- Check Google AI API status

## Test API Key Directly

```bash
# Test API key with curl
export GOOGLE_AI_API_KEY=$(grep GOOGLE_AI_API_KEY env | cut -d'=' -f2)
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GOOGLE_AI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "contents": [{
      "parts": [{
        "text": "Hello"
      }]
    }]
  }'
```

## Check Logs for Specific Errors

The enhanced logging will show:
- API URL being called
- Response status code
- Error messages from API
- API token presence
- Model being used

Look for lines like:
```
Gemini API response status: 200
Gemini API error: 403
Error response: {...}
```

## Verify Environment Variables in Gunicorn

```bash
# Check if Gunicorn can see the environment variables
python -c "
import os
from dotenv import load_dotenv
load_dotenv('env')
print('GOOGLE_AI_API_KEY:', 'SET' if os.getenv('GOOGLE_AI_API_KEY') else 'NOT SET')
"
```

## Restart Gunicorn

After making changes, always restart Gunicorn:

```bash
pkill -f gunicorn
gunicorn -c gunicorn_config.py wsgi:application
```

## Check API Key Validity

Visit https://aistudio.google.com/app/apikey and verify:
- API key is active
- Quota is not exceeded
- API key has proper permissions

## Next Steps

1. Check Gunicorn error logs
2. Look for specific error messages
3. Test API key directly with curl
4. Verify environment variables are loaded
5. Check Google AI API status

For more help, see the error logs with detailed diagnostic information.

