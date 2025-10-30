# Audio Files Distribution Guide

## 🎵 Audio Files Setup

The audio files are **NOT included** in the GitHub repository due to their large size. You'll need to set them up separately.

## 📁 Required Audio File Structure

Create the following directory structure in your project:

```
uploads/questions/english/
├── IM/                          # Intermediate-Mid level
│   ├── 01. Newspapers/
│   │   ├── 01_Q1.mp3
│   │   ├── 01_Q2.mp3
│   │   └── ...
│   ├── 02. Television/
│   ├── 03. Internet/
│   └── ... (20 topics total)
├── IH/                          # Intermediate-High level
│   ├── 01. Newspapers/
│   ├── 02. Television/
│   └── ... (30 topics total)
└── AL/                          # Advanced-Low level
    ├── 01. Newspapers/
    ├── 02. Television/
    └── ... (32 topics total)
```

## 🚀 Quick Setup Options

### Option 1: Download from Backup Folders
If you have access to the original project, copy the audio files from:
- `question_data/voices/` → `uploads/questions/english/`
- `OPIC_Voices_Organized/` → `uploads/questions/english/`
- `OPIC Multicampus_AL/` → `uploads/questions/english/AL/`

### Option 2: Use Sample Audio Files
For testing purposes, you can create a few sample audio files:

```bash
# Create directory structure
mkdir -p uploads/questions/english/IM/01.\ Newspapers
mkdir -p uploads/questions/english/IH/01.\ Newspapers  
mkdir -p uploads/questions/english/AL/01.\ Newspapers

# Add sample audio files (you can use any MP3 files for testing)
# Place MP3 files in the appropriate directories
```

### Option 3: Generate TTS Audio
Use the built-in TTS generator to create audio files:

```bash
python tts_generator.py
```

## 📊 Expected File Counts

- **IM Level**: ~400 questions across 20 topics
- **IH Level**: ~600 questions across 30 topics  
- **AL Level**: ~640 questions across 32 topics
- **Total**: ~1,640 audio files

## 🔧 Audio File Requirements

### File Format
- **Format**: MP3
- **Bitrate**: 128kbps or higher
- **Sample Rate**: 44.1kHz recommended

### Naming Convention
- **Pattern**: `XX_QY.mp3`
- **XX**: Topic number (01, 02, 03, etc.)
- **Y**: Question number (1, 2, 3, etc.)
- **Example**: `01_Q1.mp3`, `01_Q2.mp3`, `02_Q1.mp3`

### File Size
- **Recommended**: Under 5MB per file
- **Maximum**: 10MB per file
- **Total Size**: Approximately 2-3GB for all files

## 🛠️ Setup Script

Create a setup script to help with audio file organization:

```python
# audio_setup.py
import os
from pathlib import Path

def create_audio_structure():
    """Create the required audio file directory structure"""
    base_path = Path("uploads/questions/english")
    
    levels = ["IM", "IH", "AL"]
    topics = {
        "IM": ["01. Newspapers", "02. Television", "03. Internet", "04. Phones + Technology", 
               "05. Music", "06. Movies", "07. Industry", "08. Housing 1", "09. Housing 2",
               "10. Furniture + Recycling", "11. Work", "12. Food", "13. Health",
               "14. Restaurants", "15. Bars", "16. Gatherings", "17. Domestic Trips",
               "18. Oversea Trips", "19. Geography", "20. Parks + Walking"],
        "IH": ["01. Newspapers", "02. Television", "03. Internet", "04. Phones + Technology",
               "05. Music", "06. Movies", "07. Industry", "08. Housing 1", "09. Housing 2",
               "10. Furniture + Recycling", "11. Work", "12. Food", "13. Health",
               "14. Restaurants", "15. Bars", "16. Gatherings", "17. Domestic Trips",
               "18. Oversea Trips", "19. Geography", "20. Parks + Walking",
               "21. Shopping", "22. Fashion", "23. Holidays", "24. Family + Friends",
               "25. Free Time", "26. Weather", "27. Transportation", "28. Banks",
               "29. Hotels", "30. Appointment"],
        "AL": ["01. Newspapers", "02. Television", "03. Internet", "04. Phones + Technology",
               "05. Music", "06. Movies", "07. Industry", "08. Housing 1", "09. Housing 2",
               "10. Furniture + Recycling", "11. Work", "12. Food", "13. Health",
               "14. Restaurants", "15. Bars", "16. Gatherings", "17. Domestic Trips",
               "18. Oversea Trips", "19. Geography", "20. Parks + Walking",
               "21. Shopping", "22. Fashion", "23. Holidays", "24. Family + Friends",
               "25. Free Time", "26. Weather", "27. Transportation", "28. Banks",
               "29. Hotels", "30. Appointment", "31. Role Play", "32. Messages"]
    }
    
    for level in levels:
        for topic in topics[level]:
            topic_path = base_path / level / topic
            topic_path.mkdir(parents=True, exist_ok=True)
            print(f"Created: {topic_path}")
    
    print(f"\n✅ Audio directory structure created!")
    print(f"📁 Base path: {base_path.absolute()}")
    print(f"📊 Total directories: {sum(len(topics[level]) for level in levels)}")

if __name__ == "__main__":
    create_audio_structure()
```

## 🚨 Important Notes

### Database vs Files
- The database contains **question text** and **file paths**
- Audio files must match the paths stored in the database
- If audio files are missing, questions will show but audio won't play

### Testing Without Audio
You can test the application without audio files:
1. Questions will display with text
2. Audio playback will fail gracefully
3. Recording functionality will still work
4. All other features will function normally

### Production Deployment
For production deployment:
1. Upload audio files to your server
2. Ensure proper file permissions
3. Consider using CDN for audio delivery
4. Implement audio file compression

## 📞 Support

If you need help with audio file setup:
1. Check the database for expected file paths
2. Verify directory structure matches database entries
3. Test with a few sample files first
4. Contact the project maintainer for audio file access

---

**Note**: Audio files are essential for the full functionality of the OPIc Practice Portal. Without them, users can only see question text but cannot listen to the audio questions.
