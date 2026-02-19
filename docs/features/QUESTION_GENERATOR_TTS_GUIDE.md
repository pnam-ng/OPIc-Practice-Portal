# Question Generator & TTS Audio System

This document explains how the AI-powered question generation and TTS (Text-to-Speech) audio system works in the OPIc Practice Portal.

## Table of Contents
- [Overview](#overview)
- [Question Generator Service](#question-generator-service)
- [TTS Audio Service](#tts-audio-service)
- [Triggers & Automation](#triggers--automation)
- [CLI Scripts](#cli-scripts)
- [Admin API Endpoints](#admin-api-endpoints)

---

## Overview

The system has two main components:
1. **Question Generator** - Uses Google Gemini AI to generate OPIc practice questions
2. **TTS Audio Service** - Uses Microsoft Edge TTS to generate spoken audio for questions

### Automatic Audio Generation
When new questions are generated, TTS audio is **automatically created** for:
- The question text (`audio_url`)
- The sample answer (`sample_answer_audio_url`)

---

## Question Generator Service

**Location:** `app/services/question_generator.py`

### Key Methods

| Method | Description |
|--------|-------------|
| `generate_question(topic, level, question_type, existing_questions)` | Generate a new question using AI |
| `generate_variation(question, variation_type)` | Create a variation of an existing question |
| `save_generated_question(...)` | Save question to DB and auto-generate TTS audio |
| `get_next_question(user_id, topic, level)` | Get next question using intelligent rotation |

### Level-Specific Complexity

Questions are generated with complexity appropriate to each level:

| Level | Name | Complexity | Question Style | Response Time |
|-------|------|------------|----------------|---------------|
| **IM** | Intermediate-Mid | Simple | Direct, basic questions. "What", "Where", "When" | 30-60 seconds |
| **IH** | Intermediate-High | Moderate | Compound questions with reasons. "How", "Why", "Describe" | 60-90 seconds |
| **AL** | Advanced-Low | Complex | Hypothetical scenarios, analysis, multi-part questions | 90-120 seconds |

#### IM (Simplest) Examples:
- "Tell me about restaurants."
- "Do you like restaurants? Why?"
- "What is restaurants like in your country?"

#### IH (Moderate) Examples:
- "Tell me about a memorable experience at a restaurant. Why was it special?"
- "Compare restaurants now and 10 years ago. What has changed and why?"
- "What are your thoughts on restaurants? Share your perspective and reasoning."

#### AL (Most Complex) Examples:
- "If you were to open a restaurant, what concept would you choose and how would you make it different from existing restaurants? Consider current trends and customer preferences."
- "Compare and contrast how different generations view restaurants. What causes these differences and what might bridge the gap?"
- "Critically evaluate the current state of restaurants in your country. What are their strengths, weaknesses, and potential improvements?"

### Question Types
- `general` - Describe or explain the topic
- `experience` - Personal experience/story questions
- `comparison` - Compare two things or time periods
- `roleplay` - Scenario-based questions
- `opinion` - Opinion/viewpoint questions

### Variation Types
- `rephrase` - Same question with different wording
- `followup` - Deeper exploration question
- `perspective` - Different point of view
- `timeshift` - Past/present/future variation

### Example Usage in Code
```python
from app.services.question_generator import question_generator

# Generate a new question
result = question_generator.generate_question(
    topic="14. Restaurants",
    level="IH",
    question_type="experience",
    existing_questions=["What restaurants do you like?"]
)

# Save to database (TTS audio auto-generated in background)
if result:
    question = question_generator.save_generated_question(
        topic="14. Restaurants",
        level="IH",
        text=result['text'],
        sample_answer=result.get('sample_answer'),
        keywords=result.get('keywords'),
        auto_generate_audio=True  # Default: True
    )
```

---

## TTS Audio Service

**Location:** `app/services/tts_service.py`

### Key Methods

| Method | Description |
|--------|-------------|
| `scan_missing_audio()` | Find questions with text but no audio |
| `generate_missing_audio(...)` | Batch generate audio for all missing items |
| `generate_missing_audio_for_topic(topic, ...)` | Generate for specific topic only |
| `generate_audio(text, output_path, voice_key)` | Generate single audio file |
| `generate_audio_standalone(...)` | Same as above, but works without Flask context |

### Available Voices

| Key | Voice Name | Description |
|-----|------------|-------------|
| `ava` | en-US-AvaNeural | **Default** - Female, OPIc interviewer style |
| `jenny` | en-US-JennyNeural | Female alternative |
| `guy` | en-US-GuyNeural | Male option |
| `aria` | en-US-AriaNeural | Female option |

### Audio File Naming Convention
- Questions: `q_{question_id}_{timestamp}.mp3`
- Sample Answers: `sa_{question_id}_{timestamp}.mp3`

### Audio Storage Location
- Files saved to: `/uploads/questions/`
- Database stores URL path: `/uploads/questions/q_1234_1768022343261.mp3`

---

## Triggers & Automation

### 1. On App Startup / Restart

When the Flask app starts, a **background thread** automatically:
1. Waits 10 seconds (to let server initialize)
2. Scans for all questions/sample answers missing audio
3. Generates TTS audio for all missing items
4. Logs progress to console

**Console Output Example:**
```
[OK] Chatbot blueprint registered successfully
[TTS] Background audio generation thread started (will run in 10 seconds)
[TTS] Found 586 items missing audio. Starting background generation...
[TTS]   - Questions: 190
[TTS]   - Sample answers: 396
✓ Generated question audio for question #1002
✓ Generated sample answer audio for question #1002
...
[TTS] ✓ Generation complete!
[TTS]   - Success: 586
[TTS]   - Failed: 0
[TTS]   - Skipped: 0
```

**Code Location:** `app/__init__.py` → `_start_background_tts_generator()`

### 2. After Question Generation

When `save_generated_question()` is called, it:
1. Saves the question to database
2. Spawns a **background thread** to generate TTS audio
3. Updates `audio_url` and `sample_answer_audio_url` in database

**This happens automatically** - no manual intervention needed.

**Code Location:** `app/services/question_generator.py` → `_generate_audio_for_question()`

### 3. Manual Trigger via Script

```bash
# Scan only (see what's missing)
python scripts/generate_missing_audio.py --scan

# Generate all missing audio
python scripts/generate_missing_audio.py

# Generate with limit
python scripts/generate_missing_audio.py --limit 50

# Generate for specific topic
python scripts/generate_missing_audio.py --topic "14. Restaurants"

# Use different voice
python scripts/generate_missing_audio.py --voice jenny
```

### 4. Manual Trigger via Admin API

```bash
# Scan for missing audio
GET /admin/tts/scan

# Batch generate
POST /admin/tts/generate
Content-Type: application/json
{
    "voice": "ava",
    "generate_questions": true,
    "generate_sample_answers": true,
    "limit": 100,
    "topic": "14. Restaurants"  # optional
}

# Generate for single question
POST /admin/tts/generate-single/1234
Content-Type: application/json
{
    "voice": "ava",
    "type": "question"  # or "sample_answer"
}
```

---

## CLI Scripts

### 1. generate_missing_audio.py

**Purpose:** Scan and generate TTS audio for questions missing voice

```bash
# Show help
python scripts/generate_missing_audio.py --help

# Options:
#   --scan          Only scan, don't generate
#   --limit N       Limit to N items
#   --questions     Only question audio
#   --answers       Only sample answer audio
#   --topic TOPIC   Filter by topic
#   --voice VOICE   Voice: ava, jenny, guy, aria
```

### 2. batch_generate_questions.py

**Purpose:** Generate AI questions for all topics

```bash
# Generate 3 questions per topic (default)
python scripts/batch_generate_questions.py generate

# Generate 5 questions per topic
python scripts/batch_generate_questions.py generate --count 5

# Skip variations
python scripts/batch_generate_questions.py generate --no-variations

# Import from JSON backup
python scripts/batch_generate_questions.py import data/questions.json
```

### 3. generate_questions.py

**Purpose:** Generate questions for specific topic

```bash
# Generate 5 questions for a topic
python scripts/generate_questions.py generate -t "14. Restaurants" -l IH -c 5

# Generate variations
python scripts/generate_questions.py variations -t "14. Restaurants" -l IH

# List all topics
python scripts/generate_questions.py list

# Show statistics
python scripts/generate_questions.py stats
```

---

## Admin API Endpoints

### TTS Audio Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/tts/scan` | GET | Scan for questions missing audio |
| `/admin/tts/generate` | POST | Batch generate missing audio |
| `/admin/tts/generate-single/<id>` | POST | Generate audio for single question |

### Question Management (existing)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/questions/<id>/generate-audio` | POST | Generate audio for specific question |
| `/questions/generate-audio-preview` | POST | Generate preview audio (for testing) |

---

## Configuration

### Environment Variables

The system uses these environment variables (defined in `config.env`):

```bash
# Google Gemini API (for question generation)
GEMINI_API_KEY=your_api_key_here

# Optional: Custom voice (default: ava)
TTS_DEFAULT_VOICE=ava
```

### Disabling Auto-Generation

To disable automatic TTS generation on startup, you can modify `app/__init__.py`:

```python
# Comment out this line in create_app():
# _start_background_tts_generator(app)
```

To disable auto-generation after saving questions:

```python
question_generator.save_generated_question(
    ...,
    auto_generate_audio=False  # Disable TTS generation
)
```

---

## Database Fields

### Question Model

| Field | Type | Description |
|-------|------|-------------|
| `text` | Text | Question text |
| `audio_url` | String | Path to question audio file |
| `sample_answer_text` | Text | Sample answer text |
| `sample_answer_audio_url` | String | Path to sample answer audio |
| `is_generated` | Boolean | True if AI-generated |
| `generation_source` | String | 'gemini', 'template', 'manual' |
| `variation_type` | String | 'rephrase', 'followup', etc. |
| `parent_id` | Integer | Original question ID (for variations) |

---

## Troubleshooting

### TTS Not Working
1. Check edge-tts is installed: `pip install edge-tts==7.2.7`
2. Check network connectivity (edge-tts needs internet)
3. Check console logs for `[TTS]` messages

### Questions Not Generating
1. Check `GEMINI_API_KEY` is set in `config.env`
2. Check API quota isn't exceeded
3. Check console for error messages

### Audio Files Missing
1. Run `python scripts/generate_missing_audio.py --scan`
2. Run `python scripts/generate_missing_audio.py` to generate
3. Check `/uploads/questions/` directory permissions
