# 🤖 AI Integration - Quick Start

Welcome! This guide will help you add AI-powered speech analysis to your OPIc Practice Portal in **15-30 minutes**.

---

## 📦 What You're Getting

- **Speech-to-Text**: Automatic transcription of user responses using Whisper
- **AI Scoring**: Intelligent scoring based on fluency, vocabulary, grammar, and content
- **Instant Feedback**: Personalized suggestions for improvement
- **100% Free**: All models run locally, no API costs

---

## ⚡ Quick Installation

### Option 1: Automated Setup (Recommended)

#### **Windows:**
```powershell
# Run the installation script
.\install_ai.bat
```

#### **macOS/Linux:**
```bash
# Make script executable
chmod +x install_ai.sh

# Run the installation
./install_ai.sh
```

### Option 2: Manual Setup

Follow the detailed guide: **[docs/development/QUICK_AI_SETUP.md](docs/development/QUICK_AI_SETUP.md)**

---

## ✅ After Installation

### 1. Start Ollama Service

**Windows:**
```powershell
# Ollama should start automatically
# If not, run:
ollama serve
```

**macOS/Linux:**
```bash
ollama serve &
```

### 2. Test the Setup

```bash
python test_ai_quick.py
```

You should see:
```
Testing AI Setup...
1. Loading Whisper small model...
   ✓ Whisper loaded!
2. Testing Ollama...
   ✓ Ollama works: Hello! How can I help you today?
Setup complete!
```

---

## 🚀 Using AI in Your App

### Quick Test with Sample Audio

Create `test_ai_analysis.py`:

```python
from app.services.ai_service import get_ai_service

# Initialize AI
ai = get_ai_service()

# Test transcription
result = ai.transcribe_audio("path/to/your/audio.webm")
print(f"Transcript: {result['text']}")

# Test scoring
question = "Tell me about your favorite hobby"
scores = ai.score_response(result['text'], question)
print(f"Score: {scores['overall_score']}/100")
print(f"Feedback: {scores['feedback']}")
```

---

## 📊 Expected Performance

### With 8GB RAM (CPU only):

| Audio Length | Processing Time | Total Time |
|-------------|-----------------|------------|
| 30 seconds  | ~2-3 sec (STT) + ~5 sec (AI) | **~8 seconds** |
| 1 minute    | ~5-6 sec (STT) + ~5 sec (AI) | **~12 seconds** |
| 2 minutes   | ~10 sec (STT) + ~5 sec (AI) | **~16 seconds** |

✅ **Perfect for real-time feedback!**

---

## 💡 What's Installed

### Models Downloaded:
- **Whisper Small**: 244MB (downloads on first use)
- **Llama 3.1 8B**: 4.7GB

### Total Disk Space: ~5GB
### RAM Usage While Running: ~6-7GB

---

## 🎯 Next Steps

1. **✅ Verify Installation**
   ```bash
   python test_ai_quick.py
   ```

2. **📖 Read Full Guide**
   - Open: `docs/development/QUICK_AI_SETUP.md`
   - Complete integration steps
   - Add API endpoints
   - Update database
   - Add frontend UI

3. **🧪 Test with Real Audio**
   - Record a sample OPIc response
   - Run AI analysis
   - Check accuracy

4. **🎨 Customize**
   - Tune scoring prompts in `ai_service.py`
   - Adjust feedback messages
   - Add more scoring criteria

---

## 🚨 Troubleshooting

### "Ollama not found"
```bash
# Windows: Download from https://ollama.com/download
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh
```

### "Whisper fails to load"
```bash
pip install --upgrade openai-whisper torch
```

### "Out of memory"
Use smaller models:
- Change `"small"` to `"base"` or `"tiny"` in ai_service.py
- Restart Python to free memory

### "Slow processing"
- Close other applications
- Use smaller Whisper model
- Process shorter audio clips

---

## 📁 Files Created

```
OPP/
├── install_ai.bat              # Windows installer
├── install_ai.sh               # Mac/Linux installer
├── requirements-ai.txt         # AI dependencies
├── test_ai_quick.py           # Quick test script
├── AI_SETUP_README.md         # This file
└── docs/development/
    └── QUICK_AI_SETUP.md      # Detailed guide
```

---

## 🎓 Learning Resources

- **Whisper**: https://github.com/openai/whisper
- **Ollama**: https://ollama.com/docs
- **Llama 3.1**: https://huggingface.co/meta-llama

---

## 💰 Cost Comparison

| Solution | Monthly Cost |
|----------|--------------|
| Google Speech API | ~$0.006/15s = **$24/1000 requests** |
| OpenAI Whisper API | ~$0.006/min = **$36/1000 min** |
| **This Setup (Local)** | **$0** ✅ |

---

## ⏱️ Setup Time

- **Installation**: 15 minutes
- **Testing**: 5 minutes
- **Integration**: 30 minutes
- **Total**: ~50 minutes for complete AI functionality

---

## ✅ Success Checklist

- [ ] Ran installation script successfully
- [ ] Ollama service is running
- [ ] test_ai_quick.py passed all tests
- [ ] Whisper can transcribe audio
- [ ] Llama 3.1 can generate scores
- [ ] Ready to integrate into OPIc Portal!

---

## 🎉 Ready to Go!

Your AI system is now ready to:
1. ✅ Transcribe user speech to text
2. ✅ Score responses on multiple criteria
3. ✅ Provide constructive feedback
4. ✅ Help users improve their speaking skills

**Next**: Read `docs/development/QUICK_AI_SETUP.md` for full integration guide!

---

**Need Help?** Check the troubleshooting section or open an issue on GitHub.

**Happy Coding!** 🚀



