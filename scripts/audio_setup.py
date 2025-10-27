#!/usr/bin/env python3
"""
Audio Setup Script for OPIc Practice Portal
Creates the required audio file directory structure
"""

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
    
    print("🎵 Creating audio file directory structure...")
    print("=" * 50)
    
    total_dirs = 0
    for level in levels:
        print(f"\n📁 Creating {level} level directories...")
        for topic in topics[level]:
            topic_path = base_path / level / topic
            topic_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {topic}")
            total_dirs += 1
    
    print(f"\n🎉 Audio directory structure created successfully!")
    print(f"📁 Base path: {base_path.absolute()}")
    print(f"📊 Total directories: {total_dirs}")
    print(f"📊 Levels: {len(levels)}")
    print(f"📊 Topics per level: {[len(topics[level]) for level in levels]}")
    
    print(f"\n📋 Next steps:")
    print(f"1. Add MP3 audio files to the appropriate directories")
    print(f"2. Follow naming convention: XX_QY.mp3 (e.g., 01_Q1.mp3)")
    print(f"3. Ensure file paths match database entries")
    print(f"4. Test audio playback in the application")
    
    print(f"\n📖 For detailed instructions, see AUDIO_SETUP.md")

def check_existing_files():
    """Check for existing audio files"""
    base_path = Path("uploads/questions/english")
    
    if not base_path.exists():
        print("❌ Audio directory structure not found!")
        return False
    
    total_files = 0
    levels = ["IM", "IH", "AL"]
    
    print("🔍 Checking for existing audio files...")
    print("=" * 40)
    
    for level in levels:
        level_path = base_path / level
        if level_path.exists():
            level_files = list(level_path.rglob("*.mp3"))
            print(f"📁 {level}: {len(level_files)} MP3 files")
            total_files += len(level_files)
        else:
            print(f"📁 {level}: Directory not found")
    
    print(f"\n📊 Total audio files found: {total_files}")
    
    if total_files > 0:
        print("✅ Audio files detected!")
        return True
    else:
        print("⚠️  No audio files found. You may need to add them manually.")
        return False

def main():
    """Main function"""
    print("🎵 OPIc Practice Portal - Audio Setup")
    print("=" * 50)
    
    # Check if structure already exists
    if check_existing_files():
        print("\n🤔 Audio files already exist. Do you want to recreate the structure?")
        response = input("Type 'yes' to recreate, or press Enter to skip: ").strip().lower()
        if response not in ['yes', 'y']:
            print("✅ Keeping existing structure.")
            return
    
    # Create the structure
    create_audio_structure()

if __name__ == "__main__":
    main()
