# Project Cleanup Plan for GitHub

## Current Issues:
1. ❌ Too many root-level documentation files (20+ MD files)
2. ❌ Multiple database files (opic_portal.db in root and instance/)
3. ❌ Old audio folders (OPIC_Voices, OPIC Multicampus_AL, etc.)
4. ❌ Many .bat files for ngrok/testing
5. ❌ Transcription backups in root
6. ❌ SSL folder
7. ❌ Files folder with HTML/PDF
8. ❌ Logs folder in root

## Proposed Structure:

```
OPP/
├── app/                    # Main application code ✅
│   ├── blueprints/
│   ├── controllers/
│   ├── services/
│   └── models.py
├── templates/              # HTML templates ✅
├── static/                 # Static assets ✅
│   ├── css/
│   ├── js/
│   ├── avatars/           # Default avatars only
│   └── icons/
├── scripts/               # Database & utility scripts ✅
│   └── README.md
├── docs/                  # Documentation (NEW)
│   ├── setup/
│   │   ├── SETUP_GUIDE.md
│   │   ├── DATABASE_SOLUTION.md
│   │   └── AUDIO_SETUP.md
│   ├── features/
│   │   ├── ADMIN_FEATURES_GUIDE.md
│   │   ├── COMMENTS_SYSTEM_GUIDE.md
│   │   ├── AVATAR_FEATURE_GUIDE.md
│   │   └── PASSWORD_RESET_FIX.md
│   ├── development/
│   │   ├── AI_INTEGRATION_PLAN_OPENSOURCE.md
│   │   ├── FUTURE_IMPLEMENTATION.md
│   │   └── CI_CD_GUIDE.md
│   └── sessions/
│       └── SESSION_10_SUMMARY.md
├── tests/                 # Unit tests (NEW)
├── instance/              # Instance-specific files (gitignored) ✅
│   └── opic_portal.db
├── uploads/               # User uploads (gitignored) ✅
│   ├── avatars/
│   ├── questions/
│   └── responses/
├── logs/                  # Logs (gitignored)
├── .github/               # GitHub workflows (restore)
├── config.env.example     # ✅
├── requirements.txt       # ✅
├── requirements-dev.txt   # ✅
├── app.py                 # ✅
├── gunicorn_config.py     # ✅
├── Dockerfile             # ✅
├── docker-compose.yml     # ✅
├── .gitignore             # ✅
├── README.md              # Main readme ✅
└── LICENSE                # (NEW - add license)
```

## Files to DELETE:
- ❌ opic_portal.db (keep only in instance/)
- ❌ All ngrok .bat files (10+ files)
- ❌ test_*.bat files
- ❌ run_*.bat files (except run.bat)
- ❌ OPIC_Voices/ (old, should be in uploads/)
- ❌ OPIC Multicampus_AL/ (old)
- ❌ OPIC_Voices_Organized/ (old)
- ❌ question_data/ (old)
- ❌ transcription_backups/ (or move to gitignore)
- ❌ files/ (or move to docs/resources/)
- ❌ ssl/ (should be gitignored)
- ❌ add_comments_tables.bat
- ❌ __pycache__/ folders

## Files to MOVE to docs/:
All .md files except README.md:
- ADMIN_FEATURES_GUIDE.md → docs/features/
- AI_INTEGRATION_PLAN*.md → docs/development/
- AVATAR_*.md → docs/features/
- COMMENTS_SYSTEM_*.md → docs/features/
- SETUP_GUIDE.md → docs/setup/
- AUDIO_SETUP.md → docs/setup/
- DATABASE_SOLUTION.md → docs/setup/
- etc.

## Files to UPDATE:
- .gitignore - Add more exclusions
- README.md - Update with new structure
- PROJECT_STRUCTURE.md - Update documentation

