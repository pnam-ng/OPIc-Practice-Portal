"""
Database Migration Script - Add Avatar Column to Users Table
This script adds the avatar column to the users table for existing databases.
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db
from app.models import User
from sqlalchemy import text

def add_avatar_column():
    """Add avatar column to users table if it doesn't exist"""
    try:
        # Check if the column already exists
        with db.engine.connect() as connection:
            result = connection.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            
            if 'avatar' in columns:
                print("✓ Avatar column already exists in users table")
                return True
            
            # Add the avatar column
            print("Adding avatar column to users table...")
            connection.execute(text("ALTER TABLE users ADD COLUMN avatar VARCHAR(200) DEFAULT 'default1.svg'"))
            connection.commit()
            
            print("✓ Avatar column added successfully")
            
            # Update existing users to have the default avatar
            print("Updating existing users with default avatar...")
            connection.execute(text("UPDATE users SET avatar = 'default1.svg' WHERE avatar IS NULL"))
            connection.commit()
            
            print("✓ Existing users updated with default avatar")
            return True
            
    except Exception as e:
        print(f"✗ Error adding avatar column: {e}")
        return False

def main():
    """Main migration function"""
    print("\n" + "="*60)
    print("Database Migration: Add Avatar Column")
    print("="*60 + "\n")
    
    # Import app to get database context
    from app import create_app
    app = create_app()
    
    print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}\n")
    
    with app.app_context():
        success = add_avatar_column()
        
        if success:
            print("\n" + "="*60)
            print("✓ Migration completed successfully!")
            print("="*60 + "\n")
            return 0
        else:
            print("\n" + "="*60)
            print("✗ Migration failed!")
            print("="*60 + "\n")
            return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

