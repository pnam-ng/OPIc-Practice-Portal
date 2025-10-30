# AI Integration Plan for OPIc Practice Portal
**Using Free & Open-Source Pretrained Models**

---

## 🎯 Project Goals

1. **Automatic Speech Assessment**: Score user recordings based on OPIc criteria
2. **Real-time Feedback**: Provide constructive feedback on pronunciation, grammar, fluency
3. **Progress Tracking**: Track improvement over time with AI-generated insights
4. **Personalized Recommendations**: Suggest areas for improvement based on performance
5. **Zero Cloud Costs**: Use free open-source models hosted locally or on free tiers

---

## 🏗️ Architecture Overview

```
User Audio Recording (.webm)
       ↓
   [Frontend]
       ↓
   [Backend API]
       ↓
   ┌─────────────────┴────────────────┐
   ↓                                  ↓
[Speech-to-Text]              [Audio Analysis]
(Whisper - Local)             (Pronunciation)
   ↓                                  ↓
   └─────────────────┬────────────────┘
                     ↓
            [AI Scoring Engine]
            (Local LLM / Free API)
                     ↓
            ┌────────┴────────┐
            ↓                 ↓
      [Score/Rating]      [Feedback]
            ↓                 ↓
        [Database]        [User Display]
```

---

## 🆓 Free & Open-Source AI Stack

### 1. Speech-to-Text: **OpenAI Whisper** (Open-Source)
**License**: MIT  
**Cost**: FREE (runs locally)  
**Hardware**: CPU-friendly, GPU accelerates  
**Accuracy**: State-of-the-art (comparable to paid APIs)

**Models:**
| Model | Size | VRAM | Speed | Accuracy |
|-------|------|------|-------|----------|
| `tiny` | 39M | 1GB | Very Fast | Good |
| `base` | 74M | 1GB | Fast | Better |
| `small` | 244M | 2GB | Medium | Great |
| **`medium`** | 769M | 5GB | Slower | **Excellent** ⭐ |
| `large-v3` | 1550M | 10GB | Slowest | Best |

**Recommended**: `medium` (best balance of speed/accuracy)

**Implementation:**
```python
import whisper

# Load model once at startup
model = whisper.load_model("medium")

# Transcribe audio
result = model.transcribe("audio.webm")
transcript = result["text"]
language = result["language"]
```

**Advantages:**
- ✅ No API costs
- ✅ No internet required
- ✅ Privacy (data stays local)
- ✅ No rate limits
- ✅ Supports 99+ languages
- ✅ Returns timestamps for word-level analysis

---

### 2. Large Language Model (LLM): **Multiple Options**

#### **Option A: Ollama + Llama 3.1 (Recommended)**
**License**: Llama 3.1 License (Free for commercial use)  
**Cost**: FREE  
**Hardware**: 8GB RAM minimum (16GB recommended)

**Models Available:**
- `llama3.1:8b` - 8 billion parameters (4.7GB)
- `llama3.1:70b` - 70 billion parameters (40GB) - Best quality
- `qwen2.5:7b` - Alternative, good at reasoning
- `mistral:7b` - Fast, efficient

**Installation:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3.1:8b

# Run server
ollama serve
```

**Python Integration:**
```python
import ollama

response = ollama.chat(model='llama3.1:8b', messages=[
  {
    'role': 'user',
    'content': f'Analyze this English response: "{transcript}"'
  },
])
print(response['message']['content'])
```

**Advantages:**
- ✅ Completely free
- ✅ Runs locally
- ✅ No API keys needed
- ✅ Very fast on modern CPUs
- ✅ Easy to use
- ✅ Can switch models easily

---

#### **Option B: HuggingFace Inference API (Free Tier)**
**License**: Various (mostly open-source)  
**Cost**: FREE (with rate limits)  
**Hardware**: None (cloud-hosted)

**Available Models:**
- `meta-llama/Llama-3.1-8B-Instruct`
- `mistralai/Mistral-7B-Instruct-v0.2`
- `google/flan-t5-xxl`

**Implementation:**
```python
import requests

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-8B-Instruct"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}  # Free token

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

output = query({
    "inputs": f"Analyze this English response: {transcript}",
})
```

**Free Tier Limits:**
- 1000 requests/day
- Rate limit: 30 requests/min
- ✅ No credit card required

---

#### **Option C: Local Python Models (LangChain + Transformers)**
**License**: Apache 2.0  
**Cost**: FREE  
**Hardware**: 8-16GB RAM

**Implementation:**
```python
from transformers import pipeline

# Load once at startup
classifier = pipeline("text-classification", model="distilbert-base-uncased")
generator = pipeline("text-generation", model="gpt2")

# Analyze text
fluency_score = classifier(transcript)
feedback = generator(f"Improve this response: {transcript}", max_length=200)
```

---

### 3. Grammar Checking: **LanguageTool** (Open-Source)
**License**: LGPL  
**Cost**: FREE  
**Language**: Supports 25+ languages

**Installation:**
```bash
pip install language-tool-python
```

**Usage:**
```python
import language_tool_python

tool = language_tool_python.LanguageTool('en-US')
matches = tool.check(transcript)

grammar_errors = len(matches)
corrections = [match.replacements[0] for match in matches if match.replacements]
```

**Advantages:**
- ✅ Free and open-source
- ✅ Runs locally
- ✅ Very accurate for grammar
- ✅ Returns detailed error types

---

### 4. Pronunciation Analysis: **Phonemizer + editdistance**
**License**: GPL / MIT  
**Cost**: FREE

**Implementation:**
```python
from phonemizer import phonemize
import editdistance

# Expected pronunciation (from question or reference)
expected_text = "How are you doing today?"
expected_phonemes = phonemize(expected_text, language='en-us', backend='espeak')

# User's pronunciation (from Whisper transcription)
user_phonemes = phonemize(transcript, language='en-us', backend='espeak')

# Calculate pronunciation accuracy
distance = editdistance.eval(expected_phonemes, user_phonemes)
accuracy = max(0, 100 - (distance / len(expected_phonemes) * 100))
```

---

## 📊 Scoring System Implementation

### Python Scoring Engine

```python
import whisper
import ollama
import language_tool_python
from phonemizer import phonemize
import editdistance
import json

class OPicScoringEngine:
    def __init__(self):
        # Load models once at startup
        self.whisper_model = whisper.load_model("medium")
        self.grammar_tool = language_tool_python.LanguageTool('en-US')
        
    def analyze_audio(self, audio_path, question_text, reference_answer=None):
        """Main scoring function"""
        
        # 1. Transcribe audio
        result = self.whisper_model.transcribe(audio_path)
        transcript = result["text"]
        segments = result["segments"]
        
        # 2. Calculate word count and speaking duration
        word_count = len(transcript.split())
        duration = result["segments"][-1]["end"] if segments else 0
        words_per_minute = (word_count / duration * 60) if duration > 0 else 0
        
        # 3. Grammar analysis
        grammar_matches = self.grammar_tool.check(transcript)
        grammar_errors = len(grammar_matches)
        grammar_score = max(0, 100 - (grammar_errors * 5))
        
        # 4. Fluency analysis (based on pauses)
        pause_count = sum(1 for i in range(len(segments)-1) 
                         if segments[i+1]["start"] - segments[i]["end"] > 0.5)
        fluency_score = max(0, 100 - (pause_count * 3))
        
        # 5. Pronunciation (if reference available)
        pronunciation_score = 100  # Default
        if reference_answer:
            expected_phonemes = phonemize(reference_answer, language='en-us')
            user_phonemes = phonemize(transcript, language='en-us')
            distance = editdistance.eval(expected_phonemes, user_phonemes)
            pronunciation_score = max(0, 100 - (distance / len(expected_phonemes) * 50))
        
        # 6. Vocabulary richness
        unique_words = len(set(transcript.lower().split()))
        lexical_diversity = (unique_words / word_count * 100) if word_count > 0 else 0
        vocabulary_score = min(100, lexical_diversity * 2)
        
        # 7. LLM-based content analysis
        llm_analysis = ollama.chat(model='llama3.1:8b', messages=[{
            'role': 'system',
            'content': 'You are an English language assessor for OPIc tests. Provide brief feedback on content relevance, coherence, and task completion.'
        }, {
            'role': 'user',
            'content': f"""
Question: {question_text}
User's Answer: {transcript}

Analyze:
1. Did they answer the question directly?
2. Is the response coherent and well-organized?
3. Did they provide sufficient detail?

Provide a 1-2 sentence feedback.
"""
        }])
        
        content_feedback = llm_analysis['message']['content']
        
        # 8. Calculate final score (weighted average)
        final_score = (
            fluency_score * 0.25 +
            pronunciation_score * 0.25 +
            vocabulary_score * 0.25 +
            grammar_score * 0.25
        )
        
        # Map to OPIc levels
        if final_score >= 90: level = "AL" (Advanced Low)
        elif final_score >= 75: level = "IH" (Intermediate High)
        elif final_score >= 60: level = "IM" (Intermediate Mid)
        elif final_score >= 40: level = "IL" (Intermediate Low)
        else: level = "NH" (Novice High)
        
        return {
            'transcript': transcript,
            'final_score': round(final_score, 1),
            'estimated_level': level,
            'component_scores': {
                'fluency': round(fluency_score, 1),
                'pronunciation': round(pronunciation_score, 1),
                'vocabulary': round(vocabulary_score, 1),
                'grammar': round(grammar_score, 1)
            },
            'metrics': {
                'word_count': word_count,
                'duration_seconds': round(duration, 1),
                'words_per_minute': round(words_per_minute, 1),
                'grammar_errors': grammar_errors,
                'pause_count': pause_count,
                'lexical_diversity': round(lexical_diversity, 1)
            },
            'feedback': {
                'content_analysis': content_feedback,
                'grammar_corrections': [match.message for match in grammar_matches[:5]],
                'suggestions': self._generate_suggestions(final_score, fluency_score, 
                                                         grammar_score, vocabulary_score)
            }
        }
    
    def _generate_suggestions(self, overall, fluency, grammar, vocabulary):
        """Generate personalized suggestions"""
        suggestions = []
        
        if fluency < 70:
            suggestions.append("Practice speaking without long pauses. Try recording yourself daily.")
        if grammar < 70:
            suggestions.append("Review common grammar patterns. Focus on verb tenses and articles.")
        if vocabulary < 70:
            suggestions.append("Expand your vocabulary by reading and learning topic-specific words.")
        if overall < 60:
            suggestions.append("Practice answering similar questions to build confidence.")
            
        return suggestions
```

---

## 🗄️ Database Schema Updates

```python
# Add to models.py

class AIScore(db.Model):
    """Store AI-generated scores and feedback"""
    __tablename__ = 'ai_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('responses.id'), nullable=False)
    
    # Transcript
    transcript = db.Column(db.Text, nullable=False)
    
    # Overall Score
    final_score = db.Column(db.Float, nullable=False)
    estimated_level = db.Column(db.String(10))  # IL, IM, IH, AL
    
    # Component Scores
    fluency_score = db.Column(db.Float)
    pronunciation_score = db.Column(db.Float)
    vocabulary_score = db.Column(db.Float)
    grammar_score = db.Column(db.Float)
    
    # Metrics
    word_count = db.Column(db.Integer)
    duration_seconds = db.Column(db.Float)
    words_per_minute = db.Column(db.Float)
    grammar_errors = db.Column(db.Integer)
    pause_count = db.Column(db.Integer)
    
    # Feedback
    content_feedback = db.Column(db.Text)
    grammar_corrections = db.Column(db.JSON)
    suggestions = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    response = db.relationship('Response', backref=db.backref('ai_score', uselist=False))
```

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [x] Install and test Whisper locally
- [ ] Set up Ollama with Llama 3.1
- [ ] Create basic scoring service
- [ ] Add database tables
- [ ] Test transcription pipeline

### Phase 2: Core Scoring (Week 3-4)
- [ ] Implement grammar checking
- [ ] Add fluency metrics
- [ ] Calculate vocabulary scores
- [ ] Integrate LLM for content analysis
- [ ] Create scoring API endpoint

### Phase 3: Frontend Integration (Week 5-6)
- [ ] Add "Get AI Feedback" button
- [ ] Create results display UI
- [ ] Show component scores with charts
- [ ] Display suggestions
- [ ] Add loading states

### Phase 4: Enhancement (Week 7-8)
- [ ] Add pronunciation analysis
- [ ] Implement progress tracking
- [ ] Create improvement charts
- [ ] Add comparison features
- [ ] Optimize performance

### Phase 5: Polish & Deploy (Week 9-10)
- [ ] Add error handling
- [ ] Optimize model loading
- [ ] Add caching
- [ ] Create admin analytics
- [ ] Deploy and monitor

---

## 💰 Cost Comparison

### Open-Source Stack (This Plan)
| Component | Cost | Notes |
|-----------|------|-------|
| Whisper (local) | **$0/month** | One-time hardware cost |
| Ollama + Llama 3.1 | **$0/month** | Runs on same server |
| LanguageTool | **$0/month** | Open-source |
| Hosting (CPU/RAM) | **$10-20/month** | Slightly higher specs needed |
| **Total** | **$10-20/month** | ✅ Just hosting costs |

### Commercial APIs (Original Plan)
| Component | Cost | Notes |
|-----------|------|-------|
| OpenAI Whisper API | $0.006/min | $18/month for 3000 mins |
| GPT-4o-mini | $0.15/1M tokens | $30/month estimated |
| Hosting | $5/month | Basic VPS |
| **Total** | **$50-100/month** | ❌ Scales with usage |

**Savings**: **$30-80/month** or **60-80% reduction**

---

## 🖥️ Hardware Requirements

### Minimum Specs (Single User Testing)
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 10GB SSD
- **GPU**: None required (CPU works)

### Recommended Specs (Production - 10-50 concurrent users)
- **CPU**: 8+ cores (Intel i7 / AMD Ryzen 7+)
- **RAM**: 16GB
- **Storage**: 50GB SSD
- **GPU**: Optional (NVIDIA GPU with 6GB+ VRAM speeds up Whisper 3-5x)

### Cloud Options
1. **DigitalOcean Droplet**: $48/month (8 vCPUs, 16GB RAM)
2. **AWS EC2 t3.xlarge**: $0.1664/hour (~$120/month with reserved)
3. **Hetzner**: €31/month (8 vCPUs, 32GB RAM) - Best value
4. **Your own server**: One-time $500-1000 for hardware

---

## 📦 Installation Guide

### 1. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install openai-whisper
pip install ollama
pip install language-tool-python
pip install phonemizer
pip install editdistance
pip install torch  # For Whisper
```

### 2. Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg espeak-ng

# macOS
brew install ffmpeg espeak-ng

# Windows
# Download ffmpeg from https://ffmpeg.org/download.html
# Install to PATH
```

### 3. Install Ollama

```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

### 4. Pull AI Model

```bash
ollama pull llama3.1:8b
```

### 5. Test Setup

```python
# test_ai.py
import whisper
import ollama

print("Testing Whisper...")
model = whisper.load_model("base")
print("✓ Whisper loaded successfully")

print("Testing Ollama...")
response = ollama.chat(model='llama3.1:8b', messages=[{
    'role': 'user',
    'content': 'Say hello!'
}])
print(f"✓ Ollama response: {response['message']['content']}")
```

---

## 🎨 UI Mockup for AI Feedback

```
┌─────────────────────────────────────────────────┐
│ Your Response                                   │
│ ┌─────────────────────────────────────────────┐ │
│ │ 🎤 [Audio Player]                     02:15 │ │
│ │ [▶️ Play] [⏸️ Pause] [⬇️ Download]          │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ [🤖 Get AI Feedback] (Loading...)              │
├─────────────────────────────────────────────────┤
│ AI Analysis & Feedback                          │
│                                                 │
│ Overall Score: 78/100 🎯                        │
│ Estimated Level: Intermediate High (IH)        │
│                                                 │
│ Component Scores:                               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│ Fluency         ████████░░ 82/100              │
│ Pronunciation   ███████░░░ 75/100              │
│ Vocabulary      ████████░░ 80/100              │
│ Grammar         ███████░░░ 74/100              │
│                                                 │
│ 📝 Transcript:                                  │
│ "I really enjoy traveling because it gives     │
│ me opportunity to learn about new cultures..." │
│                                                 │
│ 💡 Feedback:                                    │
│ • Your response was relevant and well-organized│
│ • Good use of connecting words                 │
│ • Consider using more advanced vocabulary      │
│ • Watch out for article usage (a/an/the)       │
│                                                 │
│ 📊 Metrics:                                     │
│ • Words: 124 • Duration: 2:15 • WPM: 55        │
│ • Grammar errors: 3 • Pauses: 8                │
└─────────────────────────────────────────────────┘
```

---

## ✅ Advantages of Open-Source Approach

1. **Zero Cloud Costs** - No per-request fees
2. **Privacy** - Audio stays on your server
3. **No Rate Limits** - Process unlimited recordings
4. **Customizable** - Fine-tune models for OPIc specifically
5. **Offline Capable** - Works without internet
6. **Predictable Costs** - Fixed hosting, no surprises
7. **Full Control** - Own your data and models

---

## ⚠️ Limitations & Considerations

1. **Setup Complexity** - More technical setup required
2. **Hardware Needs** - Requires decent server specs
3. **Model Updates** - Manual updates vs automatic API improvements
4. **Support** - Community support vs commercial SLAs
5. **Initial Learning Curve** - More configuration needed

---

## 🎯 Recommended Tech Stack

**Final Recommendation:**

| Component | Solution | Reason |
|-----------|----------|--------|
| Speech-to-Text | **Whisper (medium)** | Best accuracy, free, proven |
| LLM Scoring | **Ollama + Llama 3.1:8b** | Fast, free, easy to use |
| Grammar Check | **LanguageTool** | Accurate, open-source |
| Pronunciation | **Phonemizer** | Simple, effective |
| Backend | **Python + Flask** | Already in use |
| Queue System | **Celery + Redis** | For async processing |

---

## 📚 Additional Resources

- [Whisper Documentation](https://github.com/openai/whisper)
- [Ollama Documentation](https://ollama.com/docs)
- [Llama 3.1 Model Card](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct)
- [LanguageTool API](https://languagetool.org/http-api/)
- [Phonemizer Guide](https://github.com/bootphon/phonemizer)

---

**Status**: ✅ Ready to Implement  
**Estimated Setup Time**: 1-2 weeks  
**Maintenance**: Low (quarterly model updates)  
**Cost**: $10-20/month hosting only

---

**Next Steps:**
1. Test Whisper transcription quality with sample OPIc recordings
2. Install Ollama and test scoring prompts
3. Create prototype scoring endpoint
4. Build frontend UI for displaying results
5. Gather user feedback and iterate

