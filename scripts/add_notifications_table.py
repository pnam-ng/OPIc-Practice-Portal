"""
Database Migration Script - Add Notifications Table
This script adds the notifications table for mention notifications.
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from sqlalchemy import text

def add_notifications_table():
    """Add notifications table if it doesn't exist"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if the table already exists
            with db.engine.connect() as connection:
                result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'"))
                exists = result.fetchone() is not None
                
                if exists:
                    print("✓ Notifications table already exists")
                    return True
                
                # Create the notifications table
                print("Creating notifications table...")
                connection.execute(text("""
                    CREATE TABLE notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        actor_id INTEGER NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        comment_id INTEGER,
                        question_id INTEGER NOT NULL,
                        is_read BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (actor_id) REFERENCES users (id),
                        FOREIGN KEY (comment_id) REFERENCES comments (id),
                        FOREIGN KEY (question_id) REFERENCES questions (id)
                    )
                """))
                connection.commit()
                
                print("✓ Notifications table created successfully")
                
                # Create index for faster queries
                print("Creating indexes...")
                connection.execute(text("CREATE INDEX idx_notifications_user_id ON notifications(user_id)"))
                connection.execute(text("CREATE INDEX idx_notifications_is_read ON notifications(is_read)"))
                connection.commit()
                
                print("✓ Indexes created successfully")
                return True
                
        except Exception as e:
            print(f"✗ Error adding notifications table: {e}")
            return False

def main():
    """Main migration function"""
    print("\n" + "="*60)
    print("  Notifications Table Migration")
    print("="*60 + "\n")
    
    if add_notifications_table():
        print("\n✓ Migration completed successfully!\n")
        return 0
    else:
        print("\n✗ Migration failed!\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())


