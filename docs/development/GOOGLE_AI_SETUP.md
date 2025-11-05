# Google AI Studio (Gemini) Setup Guide

## ✅ COMPLETELY FREE - No Credit Card Required!

Google AI Studio provides **free access** to Gemini models with generous rate limits (60 requests/minute). Perfect for OPIc practice portal AI scoring!

## Step 1: Get Your Free API Key

1. Visit **Google AI Studio**: https://aistudio.google.com/app/apikey
2. Sign in with your Google account (Gmail)
3. Click **"Create API Key"**
4. Select **"Create API key in new project"** (or choose existing project)
5. Copy your API key (starts with `AIza...`)

**No credit card required!** 🎉

## Step 2: Configure Your `.env` File

Add your API key to your `.env` file:

```env
GOOGLE_AI_API_KEY=AIzaSyC...your-api-key-here...
```

Or use the alternative name:

```env
GEMINI_API_KEY=AIzaSyC...your-api-key-here...
```

## Step 3: Restart Your Flask App

After adding the API key, restart your Flask application for it to load the new environment variable.

## Step 4: Test the Integration

The AI service will automatically use Google AI Studio (Gemini) when you request AI feedback on a practice response.

### Manual Test (Optional)

You can test the API key by running:

```bash
python -c "from app.services.ai_service import ai_service; print('Provider:', ai_service.api_provider); print('Model:', ai_service.model); print('Health check:', ai_service.health_check())"
```

## Model Details

- **Model**: `gemini-2.5-flash`
- **Free Tier**: 60 requests/minute
- **No Credit Card**: Required ✅
- **Cost**: $0 (completely free!)

## Rate Limits

- **60 requests per minute** (free tier)
- If you hit the limit, the app will automatically retry after a short wait

## Troubleshooting

### API Key Not Working?

1. **Check your `.env` file** - Make sure `GOOGLE_AI_API_KEY` is set correctly
2. **Restart Flask** - Environment variables are loaded at startup
3. **Verify the key** - Visit https://aistudio.google.com/app/apikey to see your keys
4. **Check logs** - Look for error messages in `logs/output.log.txt`

### Getting 403 Errors?

- **API key invalid** - Regenerate your key at https://aistudio.google.com/app/apikey
- **Quota exceeded** - Wait a minute and try again (60 requests/minute limit)

### Getting 429 Errors (Rate Limited)?

This is normal! The free tier has a 60 requests/minute limit. The app will automatically retry after waiting.

## Benefits of Google AI Studio

✅ **100% Free** - No credit card, no payment required  
✅ **Reliable** - Google's infrastructure  
✅ **Fast** - `gemini-2.5-flash` is optimized for speed  
✅ **Good Quality** - Excellent instruction following  
✅ **Easy Setup** - Just get API key and add to `.env`

## Alternative: Hugging Face (Not Recommended)

Hugging Face Inference API is also free, but:
- ❌ Most models return 404 (not available on free tier)
- ❌ `facebook/bart-large` returns raw embeddings (not text)
- ❌ Not suitable for text generation tasks

**Recommendation**: Use Google AI Studio (Gemini) - it's the best free option!

---

**Ready to go?** Just add your `GOOGLE_AI_API_KEY` to `.env` and restart Flask! 🚀







