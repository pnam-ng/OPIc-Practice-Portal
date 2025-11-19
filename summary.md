# OPIc Practice Portal - Project Summary

**Date:** November 19, 2025
**Status:** Active Development - Phase: AI Integration (Open Source)

---

## 📋 Project Overview
The **OPIc Practice Portal** is a Flask-based web application designed to help users prepare for the OPIc (Oral Proficiency Interview - computer) English test. It features a realistic test environment, practice modes, and is currently evolving to include an AI-powered scoring and feedback engine.

## 🛠 Technical Stack

### Backend
- **Framework:** Flask 3.1.2
- **Database:** SQLAlchemy (SQLite for dev, PostgreSQL ready)
- **Auth:** Flask-Login
- **Async Tasks:** Celery + Redis (Planned/Optional)
- **PDF Processing:** PyMuPDF (for Tips/Resources)

### Frontend
- **Styling:** Bootstrap 5 + Custom Dark Mode
- **Interactivity:** Vanilla JavaScript
- **Audio:** Web Audio API (Recording & Playback)

### AI & Machine Learning (New Stack)
*Transitioning from paid APIs to local Open-Source models.*
- **Speech-to-Text:** OpenAI Whisper (Local, `medium` model recommended)
- **LLM:** Ollama + Llama 3.1 (8B parameters)
- **Grammar:** LanguageTool (Python wrapper)
- **Pronunciation:** Phonemizer + editdistance

---

## 🧩 Key Features & Current Status

### ✅ Completed Features
1.  **Authentication System**: Login, Register, Password Reset, Admin roles.
2.  **Dark Mode**: Full system-wide dark mode with persistence.
3.  **Test Mode**: Realistic OPIc simulation with surveys and timed questions.
4.  **Practice Mode**: Topic-based practice with difficulty levels (IM, IH, AL).
5.  **Recording Restrictions**: Users must listen to the question before recording (implemented in Session 10).
6.  **Admin Dashboard**: User management, Question CRUD, Tips management.
7.  **Tips & Resources**: PDF viewer with thumbnail generation.
8.  **Notifications**: Daily streak reminders, browser notifications.

### 🚧 In Progress / Next Steps (AI Integration)
We are currently implementing a **Local AI Scoring Engine** to replace the original plan of using paid APIs.

**Immediate Tasks:**
1.  **Environment Setup**: Install `openai-whisper`, `ollama`, `language-tool-python`.
2.  **Backend Implementation**:
    - Create `OPicScoringEngine` class.
    - Implement `AIScore` database model.
    - Integrate Whisper for transcription.
    - Integrate Ollama for content feedback.
3.  **Frontend Integration**:
    - Add "Get AI Feedback" button.
    - Create detailed results view (Fluency, Grammar, Vocabulary, Content).

---

## 💡 Recent Decisions & Context

### 1. Shift to Open-Source AI
**Decision:** We decided to use **Local Open-Source Models** instead of paid APIs (OpenAI/Google).
**Reasoning:**
-   **Cost:** Reduces estimated monthly cost from ~$50-100 (API fees) to ~$10-20 (VPS hosting).
-   **Privacy:** User audio and data remain on the server.
-   **Control:** No rate limits or dependency on external service uptime.

### 2. Recording UX Improvement
**Decision:** Disabled the "Record" button until the question audio has been played.
**Reasoning:** Prevents users from skipping the listening component, ensuring a realistic test practice experience.

---

## 📂 Important Files & Documentation

-   **`PROJECT_STRUCTURE.md`**: Detailed map of the codebase and features.
-   **`docs/development/AI_INTEGRATION_PLAN_OPENSOURCE.md`**: Comprehensive guide for the upcoming AI implementation.
-   **`docs/sessions/SESSION_10_SUMMARY.md`**: Summary of the most recent work (Recording restrictions).
-   **`requirements-ai.txt`**: List of dependencies for the new AI stack.

---

## ❓ Unresolved Questions / Pending Actions
-   **Hardware Verification**: Need to confirm the hosting environment (or local dev machine) supports the RAM requirements for Whisper (Medium) + Ollama (Llama 3.1). Recommended: 16GB RAM.
-   **Grammar Tool Integration**: Need to verify `language-tool-python` performance and Java dependencies on the target environment.

This summary is prepared to facilitate a seamless continuation of work in a new session.
