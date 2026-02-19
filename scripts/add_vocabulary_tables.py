#!/usr/bin/env python3
"""
Database Migration Script - Add Vocabulary Tables
Creates vocabulary, user_vocabulary, and word_of_day tables
"""

import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Load environment
try:
    from dotenv import load_dotenv
    env_files = ['config.env', '.env', 'env']
    for env_file in env_files:
        env_path = os.path.join(project_root, env_file)
        if os.path.exists(env_path):
            load_dotenv(env_path)
            break
except ImportError:
    pass


def run_migration():
    """Create vocabulary tables"""
    from app import create_app, db
    from app.models import Vocabulary, UserVocabulary, WordOfDay
    import sqlite3
    
    app = create_app()
    
    with app.app_context():
        # Get database path
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            if not db_path.startswith('/'):
                db_path = os.path.join(project_root, 'instance', db_path)
        else:
            db_path = os.path.join(project_root, 'instance', 'opic_portal.db')
        
        print(f"Database path: {db_path}")
        
        # Check existing tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"Existing tables: {existing_tables}")
        
        # Create vocabulary table
        if 'vocabulary' not in existing_tables:
            print("\n📝 Creating vocabulary table...")
            cursor.execute('''
                CREATE TABLE vocabulary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word VARCHAR(100) NOT NULL UNIQUE,
                    ipa VARCHAR(200),
                    definition TEXT,
                    part_of_speech VARCHAR(50),
                    example_sentence TEXT,
                    audio_url VARCHAR(500),
                    image_url VARCHAR(500),
                    topic VARCHAR(100),
                    difficulty_level VARCHAR(10),
                    source VARCHAR(50) DEFAULT 'ipa-dict',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX idx_vocabulary_word ON vocabulary(word)')
            cursor.execute('CREATE INDEX idx_vocabulary_topic ON vocabulary(topic)')
            print("✅ vocabulary table created")
        else:
            print("⏭️ vocabulary table already exists")
        
        # Create user_vocabulary table
        if 'user_vocabulary' not in existing_tables:
            print("\n📝 Creating user_vocabulary table...")
            cursor.execute('''
                CREATE TABLE user_vocabulary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    vocabulary_id INTEGER NOT NULL,
                    is_favorite BOOLEAN DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'new',
                    review_count INTEGER DEFAULT 0,
                    correct_count INTEGER DEFAULT 0,
                    next_review DATETIME,
                    last_viewed_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (vocabulary_id) REFERENCES vocabulary(id),
                    UNIQUE (user_id, vocabulary_id)
                )
            ''')
            cursor.execute('CREATE INDEX idx_user_vocab_status ON user_vocabulary(user_id, status)')
            print("✅ user_vocabulary table created")
        else:
            print("⏭️ user_vocabulary table already exists")
        
        # Create word_of_day table
        if 'word_of_day' not in existing_tables:
            print("\n📝 Creating word_of_day table...")
            cursor.execute('''
                CREATE TABLE word_of_day (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vocabulary_id INTEGER NOT NULL,
                    date DATE NOT NULL UNIQUE,
                    image_url VARCHAR(500),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vocabulary_id) REFERENCES vocabulary(id)
                )
            ''')
            cursor.execute('CREATE INDEX idx_wod_date ON word_of_day(date)')
            print("✅ word_of_day table created")
        else:
            print("⏭️ word_of_day table already exists")
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 50)
        print("✅ Migration complete!")
        print("=" * 50)
        
        # Verify tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        print("\nAll tables:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}")
        conn.close()


if __name__ == "__main__":
    run_migration()
