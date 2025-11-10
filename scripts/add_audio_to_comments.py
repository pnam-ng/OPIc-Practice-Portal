"""
Migration script to add audio_url column to comments table
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from sqlalchemy import text

def add_audio_column():
    """Add audio_url column to comments table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(comments)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'audio_url' in columns:
                print("✅ Column 'audio_url' already exists in comments table")
                return
            
            # Add the column
            db.session.execute(text("ALTER TABLE comments ADD COLUMN audio_url VARCHAR(200)"))
            db.session.commit()
            
            print("✅ Successfully added 'audio_url' column to comments table")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding column: {e}")
            raise

if __name__ == '__main__':
    add_audio_column()


