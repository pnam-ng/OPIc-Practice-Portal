# OPIc Practice Portal - Development Session Summary

**Date**: Current Session  
**Project**: OPIc Practice Portal (Flask + Python)  
**Location**: `D:\OPP`  
**Environment**: Windows 10/11, Python 3.8+, Flask 2.3+

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Session Tasks Completed](#session-tasks-completed)
3. [Technical Implementation Details](#technical-implementation-details)
4. [Code Changes & Snippets](#code-changes--snippets)
5. [Error Fixes & Solutions](#error-fixes--solutions)
6. [Key Decisions & Reasoning](#key-decisions--reasoning)
7. [Project Architecture](#project-architecture)
8. [Pending Tasks & Future Work](#pending-tasks--future-work)
9. [Important Notes & Constraints](#important-notes--constraints)

---

## Project Overview

**OPIc Practice Portal** is a comprehensive web application for practicing OPIc (Oral Proficiency Interview - computer) speaking tests. The application features:

- **Test Mode**: Full simulated OPIc test with dynamic question count (10-15 questions based on self-assessment level)
- **Practice Mode**: Practice individual questions with AI feedback
- **AI Chatbot**: Interactive assistant powered by Google Gemini
- **AI Scoring**: Automated response evaluation with detailed feedback
- **Comment System**: Community features with threaded replies and audio uploads
- **PWA Support**: Progressive Web App with offline capabilities
- **Dark Mode**: Full dark mode support throughout the application

### Tech Stack
- **Backend**: Flask (Python 3.8+), SQLAlchemy
- **Frontend**: Bootstrap 5, Vanilla JavaScript, Jinja2 templates
- **AI Services**: Google Gemini API (gemini-2.5-flash, fallback models)
- **Database**: SQLite (instance/opic_portal.db)
- **Deployment**: Gunicorn, served on `https://107.98.150.22:8080/`

---

## Session Tasks Completed

### 1. ✅ Test Mode: Dynamic Question Count Based on Self-Assessment Level
**Requirement**: The number of questions in test mode should depend on the self-assessment level selected by the user, with a maximum of 15 questions for levels 5 and 6.

**Implementation**:
- Modified `app/controllers/__init__.py` → `TestModeController.get_personalized_questions()`
- Updated `app/controllers/__init__.py` → `TestModeController.self_assessment()` to properly save the level
- Updated `templates/test_mode/self_assessment.html` to show question count badges on level cards

**Question Count Mapping**:
```python
question_count_map = {
    1: 10,  # Novice Low - 10 questions
    2: 10,  # Novice Mid - 10 questions
    3: 12,  # Novice High / Intermediate Low - 12 questions
    4: 12,  # Intermediate Mid - 12 questions
    5: 15,  # Intermediate High / Advanced Low - Maximum 15 questions
    6: 15   # Advanced Mid / Advanced High - Maximum 15 questions
}
```

### 2. ✅ Test Mode: Progress Bar Fix
**Requirement**: Progress bar should correctly display the current question progress in test mode.

**Implementation**:
- Fixed Jinja2 template logic in `templates/test_mode/questions.html`
- Added explicit type conversion (`current_question_index|int`, `total_questions|int`)
- Added division by zero check
- Applied `!important` flags to CSS to override conflicting styles
- Added `progress-bar-striped` and `progress-bar-animated` classes

**Key Fix**:
```html
{% if total_questions > 0 %}
    {% set progress_percent = (current_question_index|int / total_questions|int * 100)|round(1) %}
    {% if current_question_index >= total_questions %}
        {% set progress_percent = 100 %}
    {% endif %}
{% else %}
    {% set progress_percent = 0 %}
{% endif %}
```

### 3. ✅ Chatbot History Synchronization
**Requirement**: Chat history must be synchronized between the floating chatbot widget and the main chatbot page.

**Implementation**:
- Modified `templates/components/chatbot_widget.html`
- Modified `templates/main/chatbot.html`
- Implemented `localStorage` for persistent storage
- Added `window.addEventListener('storage')` for cross-tab synchronization
- Added custom `opic_chatbot_history_updated` event for same-tab synchronization

**Key Functions**:
- `loadConversationHistory()`: Loads history from localStorage
- `renderConversationHistory()`: Renders loaded history
- Dispatches custom events when history is updated

### 4. ✅ HTML Entity Decoding Fix
**Requirement**: Fix HTML entity encoding errors (e.g., `&#39;` instead of `'`) in question text and sample answers.

**Implementation**:
- Created custom Jinja2 filter `unescape_html` in `app/__init__.py` and `app.py`
- Applied filter to all question text displays:
  - `templates/practice_mode/question.html`
  - `templates/main/dashboard.html`
  - `templates/main/profile.html`
  - `templates/main/history.html`

**Filter Registration**:
```python
import html

def unescape_html_filter(text):
    """Decode HTML entities like &#39; to '"""
    if text is None:
        return ''
    return html.unescape(str(text))

app.add_template_filter(unescape_html_filter, 'unescape_html')
```

### 5. ✅ PDF Viewer Mobile Optimization
**Requirement**: Reorganize PDF viewer for mobile devices with better layout and scrolling.

**Implementation**:
- Modified `templates/main/tips.html`
- Added mobile-specific CSS for full-height modal
- Implemented vertical stacking for mobile (iframe + fallback button)
- Added responsive iframe height (50vh-70vh)
- Improved scrolling behavior with `-webkit-overflow-scrolling: touch`

### 6. ✅ Service Worker SSL Error Handling
**Requirement**: Handle SSL certificate errors gracefully during Service Worker registration.

**Implementation**:
- Modified `templates/base.html`
- Added specific error handling for `SecurityError` or messages containing "SSL" or "certificate"
- Logs warning instead of error and continues with PWA features

**Error Handling**:
```javascript
.catch(error => {
    if (error.name === 'SecurityError' || 
        error.message.includes('SSL') || 
        error.message.includes('certificate')) {
        console.warn('[PWA] Service Worker registration skipped due to SSL certificate issue:', error.message);
    } else {
        console.error('[PWA] Service Worker registration failed:', error);
    }
});
```

### 7. ✅ Chatbot Connection Error Handling
**Requirement**: Handle `ERR_CONNECTION_RESET` and `Failed to fetch` errors gracefully in the chatbot.

**Implementation**:
- Modified `templates/components/chatbot_widget.html`
- Modified `templates/main/chatbot.html`
- Modified `app/blueprints/chatbot.py`
- Added specific error messages for network failures

### 8. ✅ Chatbot Scrolling Behavior Fix
**Requirement**: Fix incorrect scrolling behavior where chat would scroll from top to bottom again even when already at the bottom.

**Implementation**:
- Removed `scroll-behavior: smooth` from CSS
- Changed all scroll operations to use `scrollTo({ top: scrollHeight, behavior: 'auto' })`
- Implemented "smart scroll" logic: only auto-scroll if user was already near bottom (within 5px tolerance)
- Used `DocumentFragment` for batching DOM updates during history rendering

**Smart Scroll Logic**:
```javascript
const isNearBottom = element.scrollHeight - element.scrollTop - element.clientHeight <= 5;
if (isNearBottom) {
    element.scrollTo({ top: element.scrollHeight, behavior: 'auto' });
}
```

### 9. ✅ AI Model Fallback System
**Requirement**: Implement fallback to alternative models when `gemini-2.5-flash` exceeds rate limits (250 RPD), and automatically switch back when available.

**Implementation**:
- Modified `app/services/chatbot_service.py`
- Modified `app/services/ai_service.py`
- Implemented fallback model system with automatic switching

**Model Priority**:
1. Primary: `gemini-2.5-flash` (250 requests/day)
2. Fallback 1: `gemini-2.5-flash-lite` (1,000 requests/day)
3. Fallback 2: `gemini-2.0-flash` (200 requests/day)
4. Fallback 3: `gemini-2.0-flash-lite` (200 requests/day)
5. Fallback 4: `gemini-2.5-pro` (50 requests/day)

**Key Methods**:
- `_switch_to_fallback_model()`: Switches to next fallback model
- `_try_switch_back_to_default()`: Attempts to switch back to primary model
- `_test_model_availability()`: Tests if a model is available

### 10. ✅ README.md Update
**Requirement**: Update README.md to highlight all functions, AI features, and PWA capabilities.

**Implementation**:
- Comprehensively updated `README.md`
- Added detailed AI Features section
- Added detailed PWA Features section
- Enhanced feature descriptions with checklists
- Organized technology stack by categories

### 11. ✅ Audio Upload in Comments
**Requirement**: Allow users to upload recording files in the comments section of practice mode.

**Implementation**:
- Added `audio_url` field to `Comment` model in `app/models.py`
- Created migration script `scripts/add_audio_to_comments.py`
- Modified `app/blueprints/comments.py` to handle audio file uploads
- Updated `templates/practice_mode/question.html` with file input fields and audio players

### 12. ✅ Audio Upload UI Optimization
**Requirement**: Optimize the UI of the audio upload in comments.

**Implementation**:
- Replaced default file input with custom styled button
- Added file preview with name and size display
- Added remove button to clear selection
- Added fade-in animation for preview
- Enhanced audio player styling with wrapper
- Added dark mode support
- Improved mobile responsiveness

**Key Features**:
- Custom upload button with hover effects
- File preview showing name and formatted size
- One-click remove functionality
- File type validation with user feedback
- Consistent styling with app design

---

## Technical Implementation Details

### Database Schema Changes

#### Comment Model (`app/models.py`)
```python
class Comment(db.Model):
    # ... existing fields ...
    audio_url = db.Column(db.String(200), nullable=True)
    
    def to_dict(self, current_user_id=None):
        return {
            # ... existing fields ...
            'audio_url': self.audio_url,
        }
```

### API Endpoints

#### Comments API (`app/blueprints/comments.py`)
- `POST /api/comments/post`: Accepts FormData with `audio` file
- `POST /api/comments/reply`: Accepts FormData with `audio` file
- File validation: `.webm`, `.mp3`, `.wav`, `.ogg`, `.m4a`
- Files saved to `uploads/comments/` with secure filename

### Frontend JavaScript Functions

#### Audio Upload Functions
```javascript
// Handle comment audio file selection
function handleCommentAudioChange(input)

// Handle reply audio file selection
function handleReplyAudioChange(commentId, input)

// Clear comment audio
function clearCommentAudio()

// Clear reply audio
function clearReplyAudio(commentId)

// Format file size for display
function formatFileSize(bytes)
```

#### Chatbot Functions
```javascript
// Load conversation history from localStorage
function loadConversationHistory()

// Render conversation history
function renderConversationHistory()

// Smart scroll to bottom
function scrollToBottom(force = false)
```

---

## Code Changes & Snippets

### Test Mode Controller (`app/controllers/__init__.py`)

```python
def self_assessment(self):
    """Handle self-assessment level submission"""
    if request.method == 'POST':
        level = request.form.get('level')
        if survey:
            # Update survey answers to include self-assessment level
            updated_answers = dict(survey.answers) if survey.answers else {}
            updated_answers['self_assessment_level'] = int(level)
            # Map level to difficulty string
            level_map = {
                1: 'IM', 2: 'IM', 3: 'IM',
                4: 'IH', 5: 'IH', 6: 'AL'
            }
            updated_answers['english_level'] = level_map.get(int(level), 'IM')
            survey.answers = updated_answers
            db.session.commit()

def get_personalized_questions(self, user_id, survey_answers, target_count=None):
    """Get personalized questions based on survey and self-assessment"""
    # Parse self-assessment level
    if isinstance(survey_answers, str):
        survey_answers = json.loads(survey_answers)
    self_assessment_level = survey_answers.get('self_assessment_level', 3)
    self_assessment_level = int(self_assessment_level)
    
    # Validate range
    if not (1 <= self_assessment_level <= 6):
        self_assessment_level = 3
    
    # Question count mapping
    question_count_map = {
        1: 10, 2: 10, 3: 12,
        4: 12, 5: 15, 6: 15
    }
    target_count = question_count_map.get(self_assessment_level, 12)
    
    if self_assessment_level in [5, 6]:
        target_count = min(target_count, 15)
```

### Comments Blueprint (`app/blueprints/comments.py`)

```python
@comments_bp.route('/post', methods=['POST'])
@login_required
def post_comment():
    """Post a new comment with optional audio file"""
    audio_file = request.files.get('audio')
    
    if audio_file and audio_file.filename:
        # Validate file type
        allowed_extensions = ['.webm', '.mp3', '.wav', '.ogg', '.m4a']
        file_ext = os.path.splitext(audio_file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'error': 'Invalid file type'})
        
        # Generate secure filename
        timestamp = int(time.time())
        secure_name = secure_filename(audio_file.filename)
        filename = f"{timestamp}_{secure_name}"
        
        # Save file
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'comments')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        audio_file.save(file_path)
        
        # Store relative path
        audio_url = f"uploads/comments/{filename}"
        comment.audio_url = audio_url
```

### Jinja2 Filter (`app/__init__.py` and `app.py`)

```python
import html

def create_app():
    # ... app initialization ...
    
    def unescape_html_filter(text):
        """Decode HTML entities like &#39; to '"""
        if text is None:
            return ''
        return html.unescape(str(text))
    
    # Register the filter
    app.add_template_filter(unescape_html_filter, 'unescape_html')
    
    return app
```

### AI Service Fallback (`app/services/chatbot_service.py`)

```python
class ChatbotService:
    def __init__(self):
        self.default_model = "gemini-2.5-flash"
        self.fallback_models = [
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-2.5-pro"
        ]
        self.current_model_index = 0
        self.last_model_check = time.time()
        self.model_check_interval = 300  # 5 minutes
    
    def _switch_to_fallback_model(self):
        """Switch to the next fallback model"""
        if self.current_model_index < len(self.fallback_models):
            self.current_model_index += 1
            model = self.fallback_models[self.current_model_index - 1]
            self._update_api_url(model)
            logger.info(f"Switched to fallback model: {model}")
    
    def _try_switch_back_to_default(self):
        """Try to switch back to default model if available"""
        if self.current_model_index > 0:
            # Test if default model is available
            if self._test_model_availability(self.default_model):
                self.current_model_index = 0
                self._update_api_url(self.default_model)
                logger.info(f"Switched back to default model: {self.default_model}")
```

### Chatbot Scrolling (`templates/components/chatbot_widget.html`)

```javascript
function addChatbotMessage(message, isUser = false) {
    // ... create message element ...
    
    // Smart scroll: only if user was already near bottom
    const isNearBottom = chatbotWindowBody.scrollHeight - 
                         chatbotWindowBody.scrollTop - 
                         chatbotWindowBody.clientHeight <= 5;
    
    if (isNearBottom) {
        chatbotWindowBody.scrollTo({ 
            top: chatbotWindowBody.scrollHeight, 
            behavior: 'auto' 
        });
    }
}
```

---

## Error Fixes & Solutions

### 1. TemplateAssertionError: No filter named 'unescape_html'
**Error**: Jinja2 couldn't find the `unescape_html` filter.

**Solution**:
- Registered filter using `app.add_template_filter()` instead of `@app.template_filter`
- Added filter registration in both `app/__init__.py` and `app.py` (entry point)
- Required server restart for changes to take effect

### 2. Service Worker SSL Certificate Error
**Error**: `SecurityError: Failed to register a ServiceWorker... An SSL certificate error occurred`

**Solution**:
- Added specific error handling for SSL/certificate errors
- Logs warning instead of error
- Continues with other PWA features (notification permissions)

### 3. Chatbot Connection Errors
**Error**: `net::ERR_CONNECTION_RESET` and `TypeError: Failed to fetch`

**Solution**:
- Added specific error handling in frontend JavaScript
- Improved error messages in `app/blueprints/chatbot.py`
- Added timeout handling and better logging

### 4. Chatbot Scrolling Issues
**Error**: Chat would scroll from top to bottom again even when already at bottom

**Solution**:
- Removed `scroll-behavior: smooth` CSS
- Changed to instant scrolling with `behavior: 'auto'`
- Implemented smart scroll logic (only scroll if near bottom)
- Used `DocumentFragment` for batch DOM updates

### 5. Progress Bar Not Working
**Error**: Progress bar remained empty even on question 3

**Solution**:
- Fixed Jinja2 type conversion (`|int` filters)
- Added division by zero check
- Applied `!important` flags to override conflicting CSS
- Added explicit style attributes

### 6. SQLAlchemy Not Detecting JSON Field Changes
**Error**: Changes to `survey.answers` JSON field not being saved

**Solution**:
- Created new dictionary instead of modifying existing one
- Ensured SQLAlchemy detects changes:
```python
updated_answers = dict(survey.answers) if survey.answers else {}
updated_answers['self_assessment_level'] = int(level)
survey.answers = updated_answers
```

---

## Key Decisions & Reasoning

### 1. Question Count Based on Self-Assessment Level
**Decision**: Levels 1-2 get 10 questions, 3-4 get 12, 5-6 get 15 (maximum).

**Reasoning**: Higher levels require more comprehensive assessment, but maximum of 15 prevents test fatigue.

### 2. Model Fallback System
**Decision**: Implement automatic fallback to alternative models when rate limits are hit.

**Reasoning**: Ensures chatbot remains available even when primary model hits rate limits. Free tier has strict limits, so fallback is essential.

### 3. localStorage for Chatbot History
**Decision**: Use `localStorage` instead of server-side storage for chat history.

**Reasoning**: Reduces server load, provides instant access, works offline. Syncs via `storage` events for cross-tab communication.

### 4. Custom Audio Upload UI
**Decision**: Replace default file input with custom styled button and preview.

**Reasoning**: Better UX, consistent with app design, provides visual feedback and file information.

### 5. HTML Entity Decoding
**Decision**: Use custom Jinja2 filter instead of JavaScript decoding.

**Reasoning**: Server-side processing is more reliable, works for all templates, handles edge cases better.

### 6. Smart Scroll Logic
**Decision**: Only auto-scroll if user is already near bottom (within 5px tolerance).

**Reasoning**: Prevents interruption when user is reading older messages, improves UX.

---

## Project Architecture

### File Structure
```
OPP/
├── app/
│   ├── __init__.py          # App factory, Jinja2 filters
│   ├── models.py             # Database models
│   ├── blueprints/          # Route handlers
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── admin.py
│   │   ├── chatbot.py
│   │   ├── comments.py
│   │   ├── notifications.py
│   │   ├── practice_mode.py
│   │   └── test_mode.py
│   ├── controllers/         # Business logic
│   │   └── __init__.py      # All controllers
│   └── services/            # External services
│       ├── ai_service.py    # AI scoring
│       └── chatbot_service.py  # Chatbot AI
├── templates/
│   ├── base.html
│   ├── main/
│   │   ├── dashboard.html
│   │   ├── chatbot.html
│   │   └── tips.html
│   ├── practice_mode/
│   │   └── question.html
│   ├── test_mode/
│   │   ├── self_assessment.html
│   │   └── questions.html
│   └── components/
│       └── chatbot_widget.html
├── scripts/
│   ├── add_audio_to_comments.py  # Migration script
│   └── ...
└── README.md
```

### Key Models

#### User Model
- Authentication, profile, avatar, preferences

#### Question Model
- Question text, audio URL, sample answer, topic, difficulty

#### Response Model
- User responses, audio URL, AI score, feedback

#### Comment Model
- Content, audio_url, likes, replies, mentions

#### Survey Model
- Background survey answers, self-assessment level

### Key Services

#### ChatbotService (`app/services/chatbot_service.py`)
- Google Gemini API integration
- Model fallback system
- Conversation history management
- Rate limit handling

#### AIService (`app/services/ai_service.py`)
- Response scoring
- Feedback generation
- Audio analysis
- Model fallback system

---

## Pending Tasks & Future Work

### Immediate Pending Tasks
- None explicitly pending from user
- All requested features have been implemented

### Potential Future Enhancements

1. **Audio Quality Improvements**
   - Noise reduction
   - Echo cancellation
   - Audio compression optimization

2. **Enhanced AI Features**
   - Voice-to-text transcription
   - Real-time pronunciation feedback
   - Advanced grammar checking

3. **Social Features**
   - User profiles with achievements
   - Leaderboards
   - Study groups

4. **Analytics Dashboard**
   - Progress charts
   - Performance trends
   - Detailed statistics

5. **Mobile App**
   - Native iOS/Android apps
   - Push notifications
   - Offline mode enhancements

6. **Admin Features**
   - Comment moderation tools
   - User management enhancements
   - Content analytics

---

## Important Notes & Constraints

### Environment Variables
Required environment variables:
- `GOOGLE_AI_API_KEY`: Google AI Studio API key
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)

### API Rate Limits
- **gemini-2.5-flash**: 250 requests/day (primary)
- **gemini-2.5-flash-lite**: 1,000 requests/day (fallback 1)
- **gemini-2.0-flash**: 200 requests/day (fallback 2)
- **gemini-2.0-flash-lite**: 200 requests/day (fallback 3)
- **gemini-2.5-pro**: 50 requests/day (fallback 4)

### Database Migrations
When adding new fields to models:
1. Create migration script in `scripts/` directory
2. Run migration script
3. Update model's `to_dict()` method if needed

### File Upload Constraints
- **Audio files**: Max size not explicitly set (should be added)
- **Supported formats**: `.webm`, `.mp3`, `.wav`, `.ogg`, `.m4a`
- **Storage location**: `uploads/comments/` for comment audio files

### Browser Compatibility
- Modern browsers with Web Audio API support
- Service Worker support (for PWA features)
- localStorage support (for chatbot history)

### SSL Certificate Issues
- Service Worker registration may fail on self-signed certificates
- Error is handled gracefully, PWA features continue to work

### Performance Considerations
- Chatbot history stored in localStorage (client-side)
- Large chat histories may impact performance
- Consider implementing history limits or pagination

### Security Considerations
- File uploads validated for type and secure filenames
- User authentication required for comments and uploads
- Admin moderation tools available

---

## Quick Reference: Key Functions

### Test Mode
- `TestModeController.self_assessment()`: Save self-assessment level
- `TestModeController.get_personalized_questions()`: Get questions based on level

### Chatbot
- `ChatbotService._call_gemini_api()`: Call Gemini API with fallback
- `ChatbotService._switch_to_fallback_model()`: Switch to fallback model
- `loadConversationHistory()`: Load chat history from localStorage
- `renderConversationHistory()`: Render chat history

### Comments
- `post_comment()`: Post comment with optional audio
- `post_reply()`: Post reply with optional audio
- `handleCommentAudioChange()`: Handle file selection
- `clearCommentAudio()`: Clear file selection

### Audio Upload
- `handleCommentAudioChange()`: Process comment audio file
- `handleReplyAudioChange()`: Process reply audio file
- `formatFileSize()`: Format bytes to readable size
- `clearCommentAudio()` / `clearReplyAudio()`: Clear selections

---

## Testing Checklist

### Test Mode
- [ ] Self-assessment level 1-6 saves correctly
- [ ] Question count matches level (10/12/15)
- [ ] Progress bar updates correctly
- [ ] Next button works after recording

### Chatbot
- [ ] History syncs between widget and main page
- [ ] History persists across sessions
- [ ] Fallback models activate on rate limit
- [ ] Auto-recovery to primary model works
- [ ] Scrolling behavior is correct

### Comments
- [ ] Audio upload works for comments
- [ ] Audio upload works for replies
- [ ] File preview displays correctly
- [ ] Remove button clears selection
- [ ] Audio player displays uploaded files

### UI/UX
- [ ] Dark mode works throughout
- [ ] Mobile responsive design
- [ ] PDF viewer works on mobile
- [ ] Progress bars display correctly
- [ ] Toast notifications work

---

## Contact & Support

For issues or questions:
- Check existing documentation in `docs/` directory
- Review code comments in modified files
- Check error logs in `logs/` directory

---

**End of Summary**

*This summary was generated to allow continuation of development work in a new session without losing context or technical details.*

