# Hugging Face API Setup Guide

This guide will help you set up Hugging Face Inference API for AI-powered OPIc scoring.

**Current Model:** `facebook/bart-large` (available on free tier)

## Prerequisites

1. **Hugging Face Account**: You need a free Hugging Face account at https://huggingface.co

## Step 1: Get Your API Token

1. Go to https://huggingface.co/settings/tokens
2. Click "New token" 
3. Name it (e.g., "OPIc Portal API")
4. Select "Read" access (that's all you need)
5. Click "Generate token"
6. **Copy the token immediately** - you won't be able to see it again!

## Step 2: Add Token to Your Environment

### Option A: Using .env file (Recommended)

1. Create or edit `.env` file in your project root (same directory as `app.py`)
2. Add this line:
   ```
   HUGGINGFACE_API_KEY=your_token_here
   ```
   Replace `your_token_here` with the token you copied.

### Option B: Using config.env

1. Copy `config.env.example` to `config.env`
2. Edit `config.env` and add:
   ```
   HUGGINGFACE_API_KEY=your_token_here
   ```
3. Make sure your app loads this file

### Option C: Set Environment Variable Directly

**Windows (PowerShell):**
```powershell
$env:HUGGINGFACE_API_KEY="your_token_here"
```

**Windows (Command Prompt):**
```cmd
set HUGGINGFACE_API_KEY=your_token_here
```

**Linux/Mac:**
```bash
export HUGGINGFACE_API_KEY="your_token_here"
```

## Step 3: Install Dependencies

Make sure `requests` is installed:

```bash
pip install requests==2.32.3
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Step 4: Test the Integration

1. Start your Flask app:
   ```bash
   python app.py
   ```

2. Navigate to practice mode and complete a question

3. On the congratulations page, click "Get AI Feedback"

4. The AI should now use Hugging Face API instead of Ollama!

## Current Model

The app is configured to use: **`facebook/bart-large`**

This model is:
- ✅ Available on Hugging Face free Inference API
- ✅ Free to use (within rate limits)
- ✅ Works with your existing Hugging Face API token
- ✅ Fast and reliable

**Note:** Most other models (Mistral, GPT-2, Flan-T5, etc.) are NOT available on the free Inference API. Only `facebook/bart-large` works on the free tier. To use other models, you would need:
- Hugging Face PRO subscription, or
- Use a different API service (Together AI, Groq, etc.)

## Rate Limits

The free Hugging Face API has rate limits:
- Some models may have a short queue (typically < 20 seconds)
- The app automatically handles model loading with retry logic
- If you get rate-limited, wait a few minutes before trying again

## Troubleshooting

### "HUGGINGFACE_API_KEY not found"
- Make sure your token is set in `.env` or environment variable
- Restart your Flask app after setting the token
- Check that the token starts with `hf_`

### "Model is loading..."
- This is normal! The model needs to load when first called
- The app will automatically wait and retry
- First call may take 20-30 seconds

### "Rate limit exceeded"
- You've hit the free tier rate limit
- Wait a few minutes before trying again
- Consider upgrading to a paid Hugging Face plan for higher limits

### "Request timeout"
- Check your internet connection
- The model might be under heavy load
- Try again in a few moments

## Benefits of Hugging Face API

✅ **No Local RAM Required** - No need to run Ollama locally  
✅ **No Model Downloads** - Models run in the cloud  
✅ **Always Updated** - Latest model versions automatically  
✅ **Works Anywhere** - No need for powerful hardware  
✅ **Free Tier Available** - Perfect for testing and small deployments  

## Next Steps

1. ✅ Get your API token
2. ✅ Add it to `.env` file
3. ✅ Restart your app
4. ✅ Test AI feedback feature
5. 🎉 Enjoy cloud-based AI scoring!

