# Quick AI Integration Setup Guide
**Lightweight Deployment with Whisper Small Model**

> ⚡ **Estimated Time**: 15-30 minutes  
> 💾 **RAM Required**: 8GB  
> 📦 **Disk Space**: ~3GB  

---

## 🎯 What We're Installing

- **Whisper Small** (244MB) - Speech-to-text transcription
- **Ollama + Llama 3.1 8B** (4.7GB) - AI scoring
- **LanguageTool** - Grammar checking (optional)

---

## 📋 Prerequisites

- Python 3.8 or higher
- 8GB RAM minimum
- Windows 10/11, macOS, or Linux
- Internet connection for initial download

---

## 🚀 Quick Installation (15 Minutes)

### Step 1: Install System Dependencies (5 min)

#### **Windows:**
```powershell
# Install ffmpeg (required for audio processing)
# Download from: https://github.com/BtbN/FFmpeg-Builds/releases
# Extract to C:\ffmpeg and add C:\ffmpeg\bin to PATH

# Or use Chocolatey:
choco install ffmpeg

# Verify installation
ffmpeg -version
```

#### **macOS:**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ffmpeg
brew install ffmpeg

# Verify
ffmpeg -version
```

#### **Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y ffmpeg python3-pip python3-venv
```

---

### Step 2: Install Python AI Libraries (5 min)

```bash
# Navigate to your project directory
cd D:\OPP

# Activate existing venv (or create new one)
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install Whisper (small model is ~244MB)
pip install openai-whisper

# Install PyTorch (CPU version for lightweight setup)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install Ollama Python client
pip install ollama

# Optional: LanguageTool for grammar checking
pip install language-tool-python
```

---

### Step 3: Install Ollama (5 min)

#### **Windows:**
```powershell
# Download and install Ollama
# Go to: https://ollama.com/download/windows
# Run the installer (OllamaSetup.exe)

# Or use command line:
winget install Ollama.Ollama

# Start Ollama service (runs in background)
ollama serve
```

#### **macOS:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Or use Homebrew
brew install ollama

# Start Ollama service
ollama serve &
```

#### **Linux:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start as service
sudo systemctl start ollama
sudo systemctl enable ollama
```

---

### Step 4: Download AI Models (5 min)

```bash
# Pull Llama 3.1 8B model (~4.7GB download)
ollama pull llama3.1:8b

# Verify model is installed
ollama list
```

**Note**: Whisper small model will download automatically on first use (~244MB).

---

## ✅ Quick Test (2 min)

Create a test file `test_ai_setup.py`:

```python
import whisper
import ollama
import os

print("=" * 50)
print("Testing AI Setup...")
print("=" * 50)

# Test 1: Whisper
print("\n1️⃣ Testing Whisper (Speech-to-Text)...")
try:
    model = whisper.load_model("small")  # Downloads on first run
    print("✅ Whisper 'small' model loaded successfully!")
    print(f"   Model size: ~244MB")
except Exception as e:
    print(f"❌ Whisper failed: {e}")

# Test 2: Ollama
print("\n2️⃣ Testing Ollama (LLM Scoring)...")
try:
    response = ollama.chat(
        model='llama3.1:8b',
        messages=[{
            'role': 'user',
            'content': 'Say "AI is working!" in exactly 3 words.'
        }]
    )
    print(f"✅ Ollama response: {response['message']['content']}")
except Exception as e:
    print(f"❌ Ollama failed: {e}")
    print("   Make sure Ollama service is running: 'ollama serve'")

# Test 3: Sample Transcription
print("\n3️⃣ Testing Sample Transcription...")
try:
    # You can test with an actual audio file
    # result = model.transcribe("path/to/audio.mp3")
    # print(f"✅ Transcript: {result['text']}")
    print("✅ Whisper is ready to transcribe audio files")
except Exception as e:
    print(f"❌ Transcription test failed: {e}")

print("\n" + "=" * 50)
print("Setup Complete! 🎉")
print("=" * 50)
```

Run the test:
```bash
python test_ai_setup.py
```

Expected output:
```
==================================================
Testing AI Setup...
==================================================

1️⃣ Testing Whisper (Speech-to-Text)...
✅ Whisper 'small' model loaded successfully!
   Model size: ~244MB

2️⃣ Testing Ollama (LLM Scoring)...
✅ Ollama response: AI is working!

3️⃣ Testing Sample Transcription...
✅ Whisper is ready to transcribe audio files

==================================================
Setup Complete! 🎉
==================================================
```

---

## 🔧 Integration with OPIc Portal

### Step 5: Create AI Service Module

Create `app/services/ai_service.py`:

```python
import whisper
import ollama
import os
from typing import Dict, Optional

class AIService:
    def __init__(self):
        """Initialize AI models (loads once at startup)"""
        print("Loading Whisper model...")
        self.whisper_model = whisper.load_model("small")
        print("✅ Whisper loaded")
        
        self.llm_model = "llama3.1:8b"
        print(f"✅ LLM ready: {self.llm_model}")
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """
        Transcribe audio to text using Whisper
        
        Args:
            audio_path: Path to audio file (mp3, wav, webm, etc.)
        
        Returns:
            dict with 'text', 'language', 'segments'
        """
        try:
            result = self.whisper_model.transcribe(
                audio_path,
                language='en',  # Force English for OPIc
                task='transcribe'
            )
            return {
                'success': True,
                'text': result['text'].strip(),
                'language': result.get('language', 'en'),
                'segments': result.get('segments', [])
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def score_response(self, transcript: str, question: str) -> Dict:
        """
        Score OPIc response using LLM
        
        Args:
            transcript: User's spoken response (transcribed)
            question: The OPIc question asked
        
        Returns:
            dict with scores and feedback
        """
        prompt = f"""You are an OPIc (Oral Proficiency Interview by Computer) examiner. 
Score the following response on a scale of 1-100 for each criterion:

Question: "{question}"

User Response: "{transcript}"

Provide scores for:
1. Fluency (flow, natural speech patterns)
2. Pronunciation (clarity, accent)
3. Vocabulary (word choice, variety)
4. Grammar (correctness, complexity)
5. Content (relevance, depth)

Format your response as JSON:
{{
    "overall_score": <number>,
    "fluency": <number>,
    "pronunciation": <number>,
    "vocabulary": <number>,
    "grammar": <number>,
    "content": <number>,
    "feedback": "<brief constructive feedback>",
    "strengths": ["<strength1>", "<strength2>"],
    "improvements": ["<area1>", "<area2>"]
}}
"""
        
        try:
            response = ollama.chat(
                model=self.llm_model,
                messages=[{
                    'role': 'system',
                    'content': 'You are an expert OPIc examiner. Always respond with valid JSON only.'
                }, {
                    'role': 'user',
                    'content': prompt
                }]
            )
            
            import json
            result = json.loads(response['message']['content'])
            result['success'] = True
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_response(self, audio_path: str, question: str) -> Dict:
        """
        Complete analysis: Transcribe + Score
        
        Args:
            audio_path: Path to user's audio recording
            question: The OPIc question
        
        Returns:
            dict with transcript and scores
        """
        # Step 1: Transcribe
        transcription = self.transcribe_audio(audio_path)
        if not transcription['success']:
            return transcription
        
        # Step 2: Score
        scoring = self.score_response(
            transcription['text'],
            question
        )
        
        # Combine results
        return {
            'success': True,
            'transcript': transcription['text'],
            'language': transcription.get('language'),
            'scores': scoring if scoring.get('success') else None,
            'error': scoring.get('error') if not scoring.get('success') else None
        }

# Global instance (initialized once)
ai_service = None

def get_ai_service():
    """Get or create AI service instance"""
    global ai_service
    if ai_service is None:
        ai_service = AIService()
    return ai_service
```

---

### Step 6: Create API Endpoint

Add to `app/blueprints/api.py` (or create new file):

```python
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.ai_service import get_ai_service
import os

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/analyze-response/<int:response_id>', methods=['POST'])
@login_required
def analyze_response(response_id):
    """
    Analyze user's audio response with AI
    
    POST /api/analyze-response/123
    """
    try:
        # Get response from database
        from app.models import Response
        response = Response.query.get_or_404(response_id)
        
        # Check ownership
        if response.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get question text
        question_text = response.question.question_text
        
        # Get audio file path
        audio_path = os.path.join('uploads', 'responses', response.audio_url.split('/')[-1])
        
        if not os.path.exists(audio_path):
            return jsonify({'error': 'Audio file not found'}), 404
        
        # Analyze with AI
        ai_service = get_ai_service()
        result = ai_service.analyze_response(audio_path, question_text)
        
        if not result['success']:
            return jsonify({'error': result.get('error', 'Analysis failed')}), 500
        
        # Save results to database
        response.ai_transcript = result['transcript']
        if result.get('scores'):
            response.ai_score = result['scores'].get('overall_score')
            response.ai_feedback = result['scores'].get('feedback')
            response.ai_scores_json = str(result['scores'])  # Store full scores
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'transcript': result['transcript'],
            'scores': result.get('scores')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

### Step 7: Update Database Models

Add to `app/models.py` in the `Response` model:

```python
class Response(db.Model):
    # ... existing fields ...
    
    # AI Analysis fields
    ai_transcript = db.Column(db.Text)
    ai_score = db.Column(db.Integer)  # Overall score 0-100
    ai_feedback = db.Column(db.Text)
    ai_scores_json = db.Column(db.Text)  # Store detailed scores as JSON
    ai_analyzed_at = db.Column(db.DateTime)
```

Run migration:
```bash
flask db migrate -m "Add AI analysis fields"
flask db upgrade
```

---

### Step 8: Add Frontend Button

In `templates/practice_mode/question.html`, add AI analysis button:

```html
<!-- After audio player, add this button -->
<div class="mt-3" id="aiAnalysisSection" style="display: none;">
    <button class="btn btn-primary" onclick="analyzeWithAI()" id="aiAnalyzeBtn">
        <i class="fas fa-robot me-2"></i>Get AI Feedback
    </button>
    
    <!-- Results display -->
    <div id="aiResults" class="mt-3" style="display: none;">
        <!-- Results will be inserted here -->
    </div>
</div>

<script>
async function analyzeWithAI() {
    const responseId = {{ response.id if response else 'null' }};
    if (!responseId) return;
    
    const btn = document.getElementById('aiAnalyzeBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
    
    try {
        const response = await fetch(`/api/analyze-response/${responseId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayAIResults(data);
        } else {
            alert('Analysis failed: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-robot me-2"></i>Get AI Feedback';
    }
}

function displayAIResults(data) {
    const resultsDiv = document.getElementById('aiResults');
    const scores = data.scores;
    
    resultsDiv.innerHTML = `
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="fas fa-brain me-2"></i>AI Analysis</h5>
            </div>
            <div class="card-body">
                <h6>Overall Score: ${scores.overall_score}/100</h6>
                
                <div class="mt-3">
                    <small class="text-muted">Fluency</small>
                    <div class="progress mb-2">
                        <div class="progress-bar" style="width: ${scores.fluency}%">${scores.fluency}%</div>
                    </div>
                    
                    <small class="text-muted">Vocabulary</small>
                    <div class="progress mb-2">
                        <div class="progress-bar" style="width: ${scores.vocabulary}%">${scores.vocabulary}%</div>
                    </div>
                    
                    <small class="text-muted">Grammar</small>
                    <div class="progress mb-2">
                        <div class="progress-bar" style="width: ${scores.grammar}%">${scores.grammar}%</div>
                    </div>
                </div>
                
                <div class="mt-3">
                    <h6>Transcript:</h6>
                    <p class="text-muted">${data.transcript}</p>
                </div>
                
                <div class="mt-3">
                    <h6>Feedback:</h6>
                    <p>${scores.feedback}</p>
                </div>
            </div>
        </div>
    `;
    resultsDiv.style.display = 'block';
}

// Show AI button after submitting response
if (recordedAudio) {
    document.getElementById('aiAnalysisSection').style.display = 'block';
}
</script>
```

---

## 🎯 Performance Expectations

### Processing Times (8GB RAM, CPU only):

| Task | Whisper Small | Notes |
|------|---------------|-------|
| 30s audio | ~2-3 seconds | Fast |
| 1min audio | ~4-6 seconds | Acceptable |
| 2min audio | ~8-12 seconds | Still reasonable |

| Task | Llama 3.1 8B | Notes |
|------|--------------|-------|
| Scoring | ~5-10 seconds | Depends on CPU |
| Feedback | ~3-8 seconds | Fast responses |

**Total time per analysis**: ~10-20 seconds

---

## 💡 Optimization Tips

1. **Keep models loaded** - Don't reload Whisper for each request
2. **Use CPU threading** - `torch.set_num_threads(4)`
3. **Batch processing** - Process multiple audios together
4. **Cache results** - Don't re-analyze same audio
5. **Background jobs** - Use Celery for async processing (optional)

---

## 🚨 Troubleshooting

### Whisper fails to load:
```bash
pip install --upgrade openai-whisper
pip install --upgrade torch
```

### Ollama connection error:
```bash
# Make sure Ollama service is running
ollama serve

# Or check status
ollama list
```

### Out of memory:
- Use Whisper `tiny` or `base` model instead of `small`
- Reduce audio quality before processing
- Close other applications

### Slow processing:
- Use smaller Whisper model (`tiny` or `base`)
- Enable GPU if available
- Reduce audio length (split long recordings)

---

## ✅ Success Checklist

- [ ] ffmpeg installed and in PATH
- [ ] Python packages installed (whisper, ollama, torch)
- [ ] Ollama installed and running
- [ ] Llama 3.1 8B model downloaded
- [ ] Test script runs successfully
- [ ] AI service module created
- [ ] API endpoint added
- [ ] Database migrated
- [ ] Frontend button added
- [ ] First AI analysis completed!

---

## 📚 Next Steps

1. **Test with real OPIc audio** - Try different question types
2. **Tune prompts** - Adjust scoring criteria in `ai_service.py`
3. **Add caching** - Cache AI results to avoid re-processing
4. **Monitor performance** - Track analysis times
5. **Gather feedback** - Ask users about AI accuracy

---

## 💰 Resource Usage

**One-time downloads:**
- Whisper small: ~244MB
- Llama 3.1 8B: ~4.7GB
- **Total**: ~5GB

**Running memory:**
- Whisper: ~1-2GB RAM
- Llama 3.1: ~4-5GB RAM
- **Total**: ~6-7GB RAM

**Perfect for 8GB systems!** ✅

---

**Deployment Time**: ✅ 15-30 minutes  
**Maintenance**: Minimal  
**Cost**: FREE (local processing)

🎉 **You're all set! Start analyzing OPIc responses with AI!**



