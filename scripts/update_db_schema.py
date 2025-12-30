import sys
import os
from sqlalchemy import text

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def update_schema():
    app = create_app()
    with app.app_context():
        print("Checking database schema...")
        
        # Check if users table exists
        inspector = db.inspect(db.engine)
        if 'users' not in inspector.get_table_names():
            print("Error: 'users' table not found. Please initialize the database first.")
            return

        columns = [col['name'] for col in inspector.get_columns('users')]
        
        # Add current_level if missing
        if 'current_level' not in columns:
            print("Adding 'current_level' column to users table...")
            try:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN current_level VARCHAR(10) DEFAULT 'IM'"))
                    conn.commit()
                print("Successfully added 'current_level'.")
            except Exception as e:
                print(f"Error adding 'current_level': {e}")
        else:
            print("'current_level' column already exists.")

        # Add target_level if missing
        if 'target_level' not in columns:
            print("Adding 'target_level' column to users table...")
            try:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN target_level VARCHAR(10) DEFAULT 'AL'"))
                    conn.commit()
                print("Successfully added 'target_level'.")
            except Exception as e:
                print(f"Error adding 'target_level': {e}")
        else:
            print("'target_level' column already exists.")
            
        print("Schema update check complete.")

if __name__ == "__main__":
    update_schema()
