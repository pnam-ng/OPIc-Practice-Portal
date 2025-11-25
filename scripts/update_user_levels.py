import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def update_user_levels():
    """
    Updates the 'users' table to include 'current_level' and 'target_level' columns.
    """
    print("Initializing application context...")
    app = create_app()
    
    with app.app_context():
        print("Checking database schema for 'users' table...")
        
        with db.engine.connect() as conn:
            # Check and add current_level
            try:
                print("Checking for 'current_level' column...")
                conn.execute(text("SELECT current_level FROM users LIMIT 1"))
                print("Column 'current_level' already exists.")
            except Exception:
                print("Column 'current_level' not found. Adding it...")
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN current_level VARCHAR(20)"))
                    print("Successfully added 'current_level' column.")
                except Exception as e:
                    print(f"Error adding 'current_level' column: {e}")

            # Check and add target_level
            try:
                print("Checking for 'target_level' column...")
                conn.execute(text("SELECT target_level FROM users LIMIT 1"))
                print("Column 'target_level' already exists.")
            except Exception:
                print("Column 'target_level' not found. Adding it...")
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN target_level VARCHAR(20)"))
                    print("Successfully added 'target_level' column.")
                except Exception as e:
                    print(f"Error adding 'target_level' column: {e}")
            
            conn.commit()
            print("Database schema update completed.")

if __name__ == "__main__":
    update_user_levels()
