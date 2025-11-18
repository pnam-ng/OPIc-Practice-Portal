"""
Migration script to add 'mode' column to responses table
Run this script once to update your existing database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from sqlalchemy import text

def add_mode_column():
    """Add mode column to responses table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('responses') 
                WHERE name='mode'
            """))
            
            count = result.fetchone()[0]
            
            if count > 0:
                print("✓ 'mode' column already exists in responses table")
                return
            
            # Add the column
            db.session.execute(text("""
                ALTER TABLE responses 
                ADD COLUMN mode VARCHAR(20) DEFAULT 'practice'
            """))
            
            db.session.commit()
            print("✓ Successfully added 'mode' column to responses table")
            print("✓ All existing responses defaulted to 'practice' mode")
            
        except Exception as e:
            print(f"✗ Error adding mode column: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    add_mode_column()












































