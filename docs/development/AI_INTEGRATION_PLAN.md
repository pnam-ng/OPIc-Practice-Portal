# AI Integration Plan for OPIc Practice Portal
**AI-Powered Speech Scoring & Feedback System**

---

## 🎯 Project Goals

1. **Automatic Speech Assessment**: Score user recordings based on OPIc criteria
2. **Real-time Feedback**: Provide constructive feedback on pronunciation, grammar, fluency
3. **Progress Tracking**: Track improvement over time with AI-generated insights
4. **Personalized Recommendations**: Suggest areas for improvement based on performance

---

## 🏗️ Architecture Overview

```
User Audio Recording
       ↓
   [Frontend]
       ↓
   [Backend API]
       ↓
   ┌─────────────┴─────────────┐
   ↓                           ↓
[Speech-to-Text]         [Audio Analysis]
(Transcription)          (Pronunciation)
   ↓                           ↓
   └─────────────┬─────────────┘
                 ↓
          [AI Scoring Engine]
          (GPT-4 / Claude)
                 ↓
          ┌──────┴──────┐
          ↓             ↓
    [Score/Rating]  [Feedback]
          ↓             ↓
      [Database]    [User Display]
```

---

## 🤖 AI Services & Models

### Option 1: OpenAI Stack (Recommended)
**Pros**: Best quality, comprehensive features, great documentation
**Cost**: Moderate to high

| Service | Purpose | Pricing |
|---------|---------|---------|
| **Whisper API** | Speech-to-Text transcription | $0.006/minute |
| **GPT-4o** | Content scoring, grammar analysis | $5/1M input tokens, $15/1M output |
| **GPT-4o-mini** | Quick feedback, suggestions | $0.15/1M input, $0.60/1M output |

**Use Cases:**
- Whisper: Transcribe audio to text
- GPT-4o: Comprehensive scoring (fluency, coherence, vocabulary)
- GPT-4o-mini: Real-time suggestions, quick grammar checks

### Option 2: Google Cloud + Gemini
**Pros**: Good transcription, competitive pricing, multimodal
**Cost**: Lower than OpenAI

| Service | Purpose | Pricing |
|---------|---------|---------|
| **Google Speech-to-Text** | Transcription | $0.006/15 seconds |
| **Gemini 1.5 Flash** | Fast scoring & feedback | $0.075/1M input, $0.30/1M output |
| **Gemini 1.5 Pro** | Deep analysis | $1.25/1M input, $5/1M output |

### Option 3: Hybrid Approach (Cost-Optimized)
**Pros**: Best balance of cost and quality
**Cost**: Low to moderate

- **Whisper (self-hosted)**: Free transcription
- **Groq (Llama 3.1)**: Free tier, very fast inference
- **OpenAI GPT-4o-mini**: For detailed feedback when needed

---

## 📊 Scoring Criteria (Based on OPIc Standards)

### 1. **Fluency & Coherence** (25%)
- Speaking pace and rhythm
- Natural flow without long pauses
- Logical idea connection
- Discourse markers usage

### 2. **Pronunciation** (25%)
- Clarity and intelligibility
- Word stress and intonation
- Individual sound accuracy
- Accent (if relevant)

### 3. **Vocabulary & Lexical Resource** (25%)
- Range of vocabulary
- Appropriateness of word choice
- Collocations and idioms
- Topic-specific terminology

### 4. **Grammar & Accuracy** (25%)
- Sentence structure variety
- Grammatical accuracy
- Tense usage
- Complex structures

### Overall Score Scale:
- **Novice Low (NL)**: 1-2 points
- **Novice Mid (NM)**: 3-4 points
- **Novice High (NH)**: 5-6 points
- **Intermediate Low (IL)**: 7-8 points
- **Intermediate Mid (IM)**: 9-10 points
- **Intermediate High (IH)**: 11-12 points
- **Advanced Low (AL)**: 13-14 points
- **Advanced Mid (AM)**: 15-16 points
- **Advanced High (AH)**: 17-18 points

---

## 🗄️ Database Schema Changes

### New Table: `ai_assessments`
```sql
CREATE TABLE ai_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    
    -- Transcription
    transcription TEXT,
    transcription_confidence FLOAT,
    word_count INTEGER,
    speaking_duration FLOAT,
    
    -- Scores (0-100)
    overall_score FLOAT,
    fluency_score FLOAT,
    pronunciation_score FLOAT,
    vocabulary_score FLOAT,
    grammar_score FLOAT,
    
    -- OPIc Level Estimation
    estimated_level VARCHAR(10),  -- 'IL', 'IM', 'IH', 'AL', etc.
    
    -- Detailed Feedback
    strengths TEXT,  -- JSON array
    weaknesses TEXT,  -- JSON array
    suggestions TEXT,  -- JSON array
    
    -- AI Metadata
    ai_model VARCHAR(50),
    processing_time FLOAT,
    tokens_used INTEGER,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);
```

### New Table: `ai_progress_tracking`
```sql
CREATE TABLE ai_progress_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    
    -- Aggregated daily scores
    avg_overall_score FLOAT,
    avg_fluency_score FLOAT,
    avg_pronunciation_score FLOAT,
    avg_vocabulary_score FLOAT,
    avg_grammar_score FLOAT,
    
    -- Level progression
    current_estimated_level VARCHAR(10),
    responses_analyzed INTEGER,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, date)
);
```

### Update Existing Table: `responses`
```sql
ALTER TABLE responses ADD COLUMN ai_scored BOOLEAN DEFAULT FALSE;
ALTER TABLE responses ADD COLUMN transcription TEXT;
```

---

## 🔧 Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Goal**: Set up AI infrastructure and basic transcription

**Tasks:**
1. ✅ Set up OpenAI API account and get API key
2. ✅ Install required packages: `openai`, `python-dotenv`
3. ✅ Create `/app/services/ai_service.py`
4. ✅ Implement basic Whisper transcription
5. ✅ Create database migration for new tables
6. ✅ Store API keys in environment variables

**Deliverables:**
- Audio files can be transcribed to text
- Transcriptions stored in database
- Basic error handling

**Code Structure:**
```python
# app/services/ai_service.py
class AIService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def transcribe_audio(self, audio_file_path):
        """Transcribe audio using Whisper API"""
        pass
    
    def analyze_transcription(self, transcription, question_text):
        """Get AI feedback on transcription"""
        pass
```

### Phase 2: Basic Scoring (Week 3-4)
**Goal**: Implement AI-powered scoring system

**Tasks:**
1. ✅ Create GPT-4 prompt for OPIc scoring
2. ✅ Implement scoring function in `AIService`
3. ✅ Create assessment model and repository
4. ✅ Add scoring endpoint to API
5. ✅ Test scoring accuracy with sample recordings

**Deliverables:**
- AI generates scores for all 4 criteria
- Scores stored in `ai_assessments` table
- Basic feedback text generated

**Prompt Template:**
```python
SCORING_PROMPT = """
You are an expert OPIc (Oral Proficiency Interview - computer) examiner.
Analyze this English speaking response and provide detailed scoring.

Question: {question_text}
User's Response (transcribed): {transcription}
Speaking Duration: {duration} seconds
Word Count: {word_count}

Evaluate based on:
1. Fluency & Coherence (0-100)
2. Pronunciation (0-100) 
3. Vocabulary & Lexical Resource (0-100)
4. Grammar & Accuracy (0-100)

Provide response in JSON format:
{{
    "fluency_score": X,
    "pronunciation_score": X,
    "vocabulary_score": X,
    "grammar_score": X,
    "overall_score": X,
    "estimated_level": "IM",
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "suggestions": ["suggestion1", "suggestion2"]
}}
"""
```

### Phase 3: UI Integration (Week 5-6)
**Goal**: Display AI feedback to users

**Tasks:**
1. ✅ Create feedback card component in question page
2. ✅ Add "Get AI Feedback" button
3. ✅ Show loading state while processing
4. ✅ Display scores with progress bars
5. ✅ Show detailed feedback in expandable sections
6. ✅ Add feedback to history page

**UI Mockup:**
```
┌─────────────────────────────────────────────┐
│  🤖 AI Feedback & Assessment                │
├─────────────────────────────────────────────┤
│  Overall Score: 78/100                      │
│  Estimated Level: Intermediate Mid (IM)     │
│                                             │
│  Fluency & Coherence:   ████████░░ 82/100  │
│  Pronunciation:         ███████░░░ 75/100  │
│  Vocabulary:           ████████░░ 80/100  │
│  Grammar & Accuracy:   ███████░░░ 73/100  │
│                                             │
│  ✅ Strengths:                              │
│  • Good use of transitional phrases         │
│  • Clear pronunciation of most words        │
│                                             │
│  ⚠️ Areas for Improvement:                  │
│  • Work on past tense consistency           │
│  • Reduce filler words ("um", "like")      │
│                                             │
│  💡 Suggestions:                            │
│  • Practice using more varied vocabulary    │
│  • Record yourself and listen back          │
└─────────────────────────────────────────────┘
```

### Phase 4: Advanced Features (Week 7-8)
**Goal**: Progress tracking and advanced analytics

**Tasks:**
1. ✅ Implement progress tracking over time
2. ✅ Create progress visualization charts
3. ✅ Add comparative analytics (vs. previous attempts)
4. ✅ Generate weekly/monthly progress reports
5. ✅ Personalized learning recommendations

**Features:**
- Line chart showing score trends over time
- Radar chart for 4 scoring dimensions
- Achievement badges for milestones
- Weak point identification across multiple responses
- Recommended questions based on weak areas

### Phase 5: Optimization & Polish (Week 9-10)
**Goal**: Performance optimization and user experience

**Tasks:**
1. ✅ Implement caching for repeated transcriptions
2. ✅ Add batch processing for test mode
3. ✅ Optimize API calls (use mini model for simple tasks)
4. ✅ Add pronunciation highlighting (word-level feedback)
5. ✅ Implement retry logic for API failures
6. ✅ Add admin dashboard for AI usage monitoring

---

## 💰 Cost Estimation

### Per Recording Analysis (Avg. 2-minute response):

**Transcription (Whisper API):**
- 2 minutes × $0.006/min = **$0.012**

**Scoring (GPT-4o-mini):**
- Input: ~500 tokens (transcription + prompt)
- Output: ~300 tokens (JSON feedback)
- Cost: ~$0.0003
- **Total: $0.0003**

**Total per recording: ~$0.013 (~1.3¢)**

### Monthly Cost Estimates:

| User Activity | Recordings/Month | Cost/Month |
|--------------|------------------|------------|
| 100 users, 10 recordings each | 1,000 | $13 |
| 500 users, 10 recordings each | 5,000 | $65 |
| 1,000 users, 20 recordings each | 20,000 | $260 |

**Ways to Reduce Costs:**
1. Offer AI feedback as premium feature (paid users only)
2. Limit free tier to 5 assessments/month
3. Use free credits from providers (OpenAI gives $5 free)
4. Self-host Whisper model (free but requires GPU)
5. Cache common feedback patterns

---

## 🔒 Security & Privacy Considerations

### Data Privacy:
1. **User Consent**: Add consent checkbox for AI analysis
2. **Data Retention**: Delete audio files after 30 days (configurable)
3. **Anonymization**: Don't send user PII to AI services
4. **Compliance**: GDPR-compliant data handling

### API Security:
1. Store API keys in environment variables (never commit)
2. Implement rate limiting (max 10 requests/minute/user)
3. Add request validation and sanitization
4. Monitor API usage and set spending limits
5. Implement fallback for API failures

### Code Example:
```python
# .env
OPENAI_API_KEY=sk-...
MAX_AI_REQUESTS_PER_USER_PER_DAY=20
AI_FEEDBACK_ENABLED=True
```

---

## 📱 User Experience Flow

### Practice Mode with AI Feedback:

```
1. User records answer
   ↓
2. User clicks "Submit" or "Next"
   ↓
3. Audio saved to database
   ↓
4. User sees their recording in history
   ↓
5. User clicks "Get AI Feedback" button
   ↓
6. Loading spinner shows (~5-10 seconds)
   ↓
7. AI feedback card appears with:
   - Overall score
   - 4 category scores
   - Transcription
   - Strengths/Weaknesses
   - Actionable suggestions
   ↓
8. User can view feedback anytime in history
```

### Test Mode with AI Feedback:

```
1. User completes entire test (12 questions)
   ↓
2. Congratulations page shows
   ↓
3. "Generate AI Report" button available
   ↓
4. Background processing (1-2 minutes for all 12)
   ↓
5. Comprehensive report generated:
   - Overall test score
   - Individual question scores
   - Strongest/weakest areas
   - Level estimation
   - Study plan recommendations
```

---

## 🎨 Frontend Components to Add

### 1. AI Feedback Card Component
**File**: `templates/components/ai_feedback.html`
```html
<div class="ai-feedback-card">
    <div class="score-overview">
        <!-- Overall score circle -->
    </div>
    <div class="score-breakdown">
        <!-- 4 progress bars -->
    </div>
    <div class="transcription">
        <!-- Audio transcription with word highlighting -->
    </div>
    <div class="feedback-sections">
        <!-- Strengths, Weaknesses, Suggestions -->
    </div>
</div>
```

### 2. Progress Chart Component
**File**: `templates/components/progress_chart.html`
- Line chart for score trends
- Radar chart for 4 dimensions
- Using Chart.js or similar

### 3. Get Feedback Button
```html
<button class="btn btn-ai" onclick="requestAIFeedback(responseId)">
    <i class="fas fa-robot"></i> Get AI Feedback
</button>
```

---

## 🧪 Testing Strategy

### 1. Unit Tests
- Test AI service functions independently
- Mock API responses
- Test scoring logic

### 2. Integration Tests
- Test full flow: upload → transcribe → score
- Test database operations
- Test API error handling

### 3. Quality Assurance
- Test with various accents and speaking speeds
- Validate scoring consistency
- Compare AI scores with human evaluator scores

### 4. Performance Tests
- Test API latency
- Test concurrent requests
- Monitor token usage

---

## 📈 Success Metrics

### Technical Metrics:
- ✅ API response time < 10 seconds
- ✅ Transcription accuracy > 90%
- ✅ API failure rate < 1%
- ✅ Cost per assessment < $0.02

### User Metrics:
- ✅ User satisfaction with feedback quality
- ✅ Repeat usage rate (users requesting multiple feedbacks)
- ✅ Improvement in scores over time
- ✅ User retention increase

---

## 🚀 Quick Start Implementation

### Minimal Viable Product (MVP) - 1 Week Sprint:

**Day 1-2: Setup**
```bash
pip install openai python-dotenv
```

**Day 3-4: Core Service**
```python
# app/services/ai_service.py
# Implement transcribe_audio() and score_response()
```

**Day 5-6: Basic UI**
```html
<!-- Add "Get AI Feedback" button -->
<!-- Display transcription and scores -->
```

**Day 7: Testing & Polish**
```python
# Test with real recordings
# Fix bugs
# Deploy to production
```

---

## 🎯 Recommended Next Steps

### Immediate (This Week):
1. ✅ Get OpenAI API key
2. ✅ Set up `.env` file with API credentials
3. ✅ Create database migration script
4. ✅ Install required packages

### Short Term (Next 2 Weeks):
1. ✅ Implement basic transcription service
2. ✅ Create scoring prompt and test it
3. ✅ Add UI button for AI feedback

### Medium Term (Next Month):
1. ✅ Full scoring system with all 4 criteria
2. ✅ Progress tracking dashboard
3. ✅ History page integration

### Long Term (Next Quarter):
1. ✅ Advanced analytics and insights
2. ✅ Personalized study recommendations
3. ✅ Pronunciation word-level feedback
4. ✅ Comparative analytics vs. other users

---

## 📚 Resources & Documentation

### APIs & Services:
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [OpenAI GPT-4 API](https://platform.openai.com/docs/guides/gpt)
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text)
- [Gemini API](https://ai.google.dev/docs)

### OPIc Standards:
- [ACTFL Proficiency Guidelines](https://www.actfl.org/resources/actfl-proficiency-guidelines-2012)
- [OPIc Test Format](https://www.languagetesting.com/opic)

### Python Libraries:
```txt
openai>=1.0.0
python-dotenv>=1.0.0
pydub>=0.25.1  # Audio processing
numpy>=1.24.0  # Audio analysis
```

---

## ⚠️ Potential Challenges & Solutions

### Challenge 1: Audio Quality
**Problem**: Poor audio quality affects transcription accuracy
**Solution**: 
- Add audio quality check before sending to API
- Provide feedback to user about recording quality
- Use noise reduction preprocessing

### Challenge 2: API Latency
**Problem**: Users wait too long for feedback
**Solution**:
- Show progress indicators
- Process in background with notifications
- Cache common responses

### Challenge 3: Cost Management
**Problem**: Unexpected high costs
**Solution**:
- Set hard spending limits in OpenAI dashboard
- Implement usage quotas per user
- Monitor daily spending with alerts

### Challenge 4: Scoring Consistency
**Problem**: AI scores may vary for similar responses
**Solution**:
- Use temperature=0 for consistent outputs
- Implement scoring calibration based on feedback
- Average multiple API calls for important assessments

---

## 🎉 Expected Outcomes

After full implementation, users will:
1. ✅ Get instant, detailed feedback on their speaking
2. ✅ Track improvement over time with visualizations
3. ✅ Receive personalized study recommendations
4. ✅ Build confidence through objective assessment
5. ✅ Prepare more effectively for actual OPIc test

**This will make your platform the most comprehensive OPIc practice tool available!**

---

*Document created: October 30, 2025*
*Ready for implementation - Let's build this! 🚀*

