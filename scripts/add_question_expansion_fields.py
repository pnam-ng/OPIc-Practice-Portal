#!/usr/bin/env python3
"""
Database Migration Script: Add Question Expansion Fields
Adds fields for question variations and creates question_sessions table
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def get_db_path():
    """Get the database file path"""
    instance_path = os.path.join(project_root, 'instance')
    db_path = os.path.join(instance_path, 'opic_portal.db')
    return db_path


def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def table_exists(cursor, table_name):
    """Check if a table exists"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None


def migrate_questions_table(cursor):
    """Add new columns to questions table for variation support"""
    print("📝 Migrating questions table...")
    
    columns_to_add = [
        ("parent_id", "INTEGER REFERENCES questions(id)"),
        ("variation_type", "VARCHAR(20)"),
        ("is_generated", "BOOLEAN DEFAULT 0"),
        ("generation_source", "VARCHAR(50)"),
        ("keywords", "JSON"),
    ]
    
    added_count = 0
    for column_name, column_def in columns_to_add:
        if not column_exists(cursor, 'questions', column_name):
            cursor.execute(f"ALTER TABLE questions ADD COLUMN {column_name} {column_def}")
            print(f"   ✅ Added column: {column_name}")
            added_count += 1
        else:
            print(f"   ⏭️  Column already exists: {column_name}")
    
    return added_count


def create_question_sessions_table(cursor):
    """Create question_sessions table for tracking question rotation"""
    print("📝 Creating question_sessions table...")
    
    if table_exists(cursor, 'question_sessions'):
        print("   ⏭️  Table already exists: question_sessions")
        return False
    
    cursor.execute("""
        CREATE TABLE question_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            question_id INTEGER NOT NULL REFERENCES questions(id),
            topic VARCHAR(100) NOT NULL,
            difficulty_level VARCHAR(10) NOT NULL,
            round_number INTEGER DEFAULT 1,
            shown_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            was_answered BOOLEAN DEFAULT 0
        )
    """)
    
    # Create index for faster queries
    cursor.execute("""
        CREATE INDEX idx_user_topic_level_round 
        ON question_sessions(user_id, topic, difficulty_level, round_number)
    """)
    
    print("   ✅ Created table: question_sessions")
    print("   ✅ Created index: idx_user_topic_level_round")
    return True


def run_migration():
    """Run the database migration"""
    print("🚀 Starting Database Migration: Question Expansion")
    print("=" * 60)
    
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        print("   Please run init_db_with_samples.py first")
        sys.exit(1)
    
    print(f"📂 Database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Run migrations
        questions_changes = migrate_questions_table(cursor)
        sessions_created = create_question_sessions_table(cursor)
        
        # Commit changes
        conn.commit()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Migration Summary:")
        print(f"   - Questions table columns added: {questions_changes}")
        print(f"   - Question sessions table created: {'Yes' if sessions_created else 'Already exists'}")
        
        # Verify
        print("\n📋 Verifying migration...")
        cursor.execute("PRAGMA table_info(questions)")
        question_columns = [row[1] for row in cursor.fetchall()]
        print(f"   Questions columns: {', '.join(question_columns)}")
        
        cursor.execute("SELECT COUNT(*) FROM question_sessions")
        session_count = cursor.fetchone()[0]
        print(f"   Question sessions records: {session_count}")
        
        print("\n🎉 Migration completed successfully!")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_migration()
