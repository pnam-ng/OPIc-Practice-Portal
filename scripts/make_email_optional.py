"""
Database Migration Script: Make email column optional
Updates the users table to allow NULL email values
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def migrate_email_to_optional():
    """Make email column nullable in users table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if email column is already nullable
            # SQLite doesn't support ALTER COLUMN directly, so we'll check and handle gracefully
            result = db.session.execute(text("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name='users'
            """))
            
            table_sql = result.fetchone()
            if table_sql:
                sql = table_sql[0]
                # Check if email has nullable
                if 'email' in sql and 'NOT NULL' in sql:
                    print("[INFO] Email column is currently NOT NULL. Creating migration...")
                    
                    # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
                    # First, create a backup
                    print("[INFO] Backing up existing users...")
                    db.session.execute(text("""
                        CREATE TABLE IF NOT EXISTS users_backup AS 
                        SELECT * FROM users
                    """))
                    
                    # Create new table structure
                    print("[INFO] Recreating users table with nullable email...")
                    db.session.execute(text("""
                        CREATE TABLE users_new (
                            id INTEGER PRIMARY KEY,
                            username VARCHAR(80) NOT NULL UNIQUE,
                            email VARCHAR(120) UNIQUE,
                            password_hash VARCHAR(128),
                            name VARCHAR(100) NOT NULL,
                            target_language VARCHAR(20),
                            avatar VARCHAR(200),
                            streak_count INTEGER,
                            last_active_date DATE,
                            is_admin BOOLEAN,
                            created_at DATETIME,
                            updated_at DATETIME
                        )
                    """))
                    
                    # Copy data
                    print("[INFO] Copying data to new table...")
                    db.session.execute(text("""
                        INSERT INTO users_new 
                        SELECT * FROM users
                    """))
                    
                    # Drop old table
                    print("[INFO] Dropping old table...")
                    db.session.execute(text("DROP TABLE users"))
                    
                    # Rename new table
                    print("[INFO] Renaming new table...")
                    db.session.execute(text("ALTER TABLE users_new RENAME TO users"))
                    
                    # Drop backup
                    print("[INFO] Dropping backup table...")
                    db.session.execute(text("DROP TABLE IF EXISTS users_backup"))
                    
                    db.session.commit()
                    print("[OK] Migration completed successfully! Email column is now optional.")
                else:
                    print("[OK] Email column is already nullable. No migration needed.")
            else:
                print("[ERROR] Users table not found!")
                
        except Exception as e:
            print(f"[ERROR] Migration failed: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    migrate_email_to_optional()




