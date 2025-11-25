# OPIc Practice Portal

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A robust, production-ready web application designed to simulate the OPIc (Oral Proficiency Interview - Computer) testing environment. Built with Flask and modern web standards, this platform provides users with a realistic practice interface featuring real-time audio recording, playback, and automated AI evaluation.

The application is currently deployed and accessible at **[opic.duckdns.org](https://opic.duckdns.org)**.

It serves as a comprehensive tool for language learners, offering both a "Practice Mode" for targeted training and a "Test Mode" that mimics the actual exam conditions. The system leverages Progressive Web App (PWA) technology to deliver a native-app-like experience across desktop and mobile devices, complete with offline capabilities and background synchronization.

## Main Functions

*   **Realistic Test Simulation**: "Test Mode" replicates the actual OPIc exam flow, including strict timing, question progression, and a self-assessment survey to determine difficulty levels (1-6).
*   **AI-Powered Scoring & Feedback**: Integrates Google Gemini 2.5 Flash to provide instant, personalized evaluation of user responses, offering scores and actionable feedback on grammar, vocabulary, and fluency.
*   **Targeted Practice**: "Practice Mode" allows users to focus on specific topics or question types without the pressure of a full exam, facilitating repetitive training on weak areas.
*   **Real-Time Audio Visualization**: Features a dynamic waveform display during recording, giving users immediate visual feedback on their speech input.
*   **Progress Tracking**: A comprehensive dashboard tracks user performance over time, maintaining history of recordings, scores, and practice streaks.
*   **Cross-Platform PWA**: Fully installable as a native-like app on both desktop and mobile devices, with offline support for reviewing past sessions and cached content.

## Interesting Techniques

The codebase leverages several modern web APIs and patterns to handle rich media and offline states:

*   **[MediaStream Recording API](https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_Recording_API)**: Used in `templates/practice_mode/question.html` to capture user audio directly in the browser. This enables immediate playback and submission without server-side processing overhead during the recording phase, ensuring low latency.
*   **[Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)**: Implements real-time audio visualization on an HTML5 Canvas. The `AudioContext` analyzes the frequency data stream to render a dynamic waveform, providing visual feedback to the user during recording.
*   **[Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)**: Defined in `static/sw.js`, this enables a "stale-while-revalidate" caching strategy for static assets and offline fallback pages, ensuring the application remains functional in low-connectivity environments.
*   **[Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)**: Integrated into the Service Worker to handle background notifications, driving user engagement through "streak" reminders and social interactions.
*   **[HTML5 Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)**: utilized for rendering the real-time audio waveform visualization, optimizing performance by avoiding heavy DOM manipulation for high-frequency updates.

## Non-Obvious Technologies

Beyond the standard Flask stack, this project employs several specialized libraries:

*   **[Edge TTS](https://github.com/rany2/edge-tts)**: A Python library that interfaces with Microsoft Edge's online text-to-speech service. It provides high-quality, neural-sounding speech synthesis without requiring a paid API key, used here for generating natural-sounding question audio.
*   **[Google Gemini 2.5 Flash](https://deepmind.google/technologies/gemini/flash/)**: Utilized via the `google-generativeai` library for the AI scoring engine. The "Flash" variant is specifically chosen for its exceptional speed and high throughput, allowing for near-instantaneous feedback on user responses.
*   **[PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/)**: A high-performance PDF rendering library used to generate thumbnails and extract text from study materials, offering significantly better speed than pure-Python alternatives like PyPDF2.
*   **[Celery](https://docs.celeryq.dev/en/stable/)**: Distributed task queue used to offload heavy processing tasks (like audio conversion or complex AI scoring) from the main request/response cycle.

## External Libraries & Resources

*   **[Flask](https://flask.palletsprojects.com/)**: The core web framework.
*   **[SQLAlchemy](https://www.sqlalchemy.org/)**: ORM for database interactions.
*   **[Bootstrap 5](https://getbootstrap.com/)**: Frontend framework for responsive layout.
*   **[FontAwesome](https://fontawesome.com/)**: Icon set used throughout the UI.
*   **[Google Fonts](https://fonts.google.com/)**: Typography (e.g., 'Inter', 'Roboto').

## Project Structure

```text
OPP/
├── app/                        # Application factory and blueprints
│   ├── blueprints/             # Modular route definitions (admin, auth, practice)
│   ├── services/               # Business logic (AI scoring, TTS, Chatbot)
│   └── utils/                  # Helper functions
├── static/                     # Static assets served by Flask/Nginx
│   ├── js/                     # Frontend logic (including bootstrap bundle)
│   └── sw.js                   # Service Worker entry point
├── templates/                  # Jinja2 templates
│   ├── practice_mode/          # Interactive practice session templates
│   └── test_mode/              # Full mock test templates
├── scripts/                    # Maintenance and setup scripts
├── docs/                       # Detailed project documentation
├── requirements.txt            # Python dependencies
└── app.py                      # WSGI application entry point
```

### Key Directories

*   **`app/services/`**: Contains the core business logic isolated from the HTTP layer. `ai_service.py` encapsulates the logic for communicating with the Gemini API, including fallback strategies and prompt engineering.
*   **`app/blueprints/`**: Implements the "Blueprints" pattern to modularize the application into distinct functional areas (Admin, Auth, Practice Mode), making the codebase scalable and easier to maintain.
*   **`static/sw.js`**: The heart of the PWA implementation, handling cache management, fetch interception, and push events.

## How to Install and Run

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/opic-practice-portal.git
    cd opic-practice-portal
    ```

2.  **Set up the environment**:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Copy `config.env.example` to `config.env` and update the values, specifically your `GOOGLE_AI_API_KEY` and database URI.

5.  **Initialize the Database**:
    ```bash
    python scripts/init_db.py
    python scripts/ensure_admin.py
    ```

6.  **Run the Application**:
    ```bash
    # Development
    python app.py
    
    # Production
    gunicorn -c gunicorn_config.py app:app
    ```

## How to Use

1.  **Registration**: Create a new account to track your progress.
2.  **Self-Assessment**: Complete the initial survey to determine your OPIc proficiency level (1-6). This tailors the difficulty of practice questions.
3.  **Practice Mode**: Select specific topics to practice. Record your answers, listen to the playback, and view the AI-generated score and feedback.
4.  **Test Mode**: Take a full-length simulated exam. The system will guide you through a series of questions based on your level, strictly timing your responses.
5.  **Review**: Access your dashboard to view past performance, listen to previous recordings, and track your improvement over time.

## How to Contribute

We welcome contributions from the community! Here's how you can help:

1.  **Fork the Repository**: Create your own copy of the project.
2.  **Create a Branch**: Work on your feature or fix in a dedicated branch (`git checkout -b feature/AmazingFeature`).
3.  **Commit Changes**: Make sure your code follows the project's style and commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  **Push to Branch**: Push your branch to your fork (`git push origin feature/AmazingFeature`).
5.  **Open a Pull Request**: Submit a PR to the main repository for review.

Please ensure your code is well-documented and includes tests where appropriate.
