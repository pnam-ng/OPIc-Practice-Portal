"""
Script to add AI-related fields to Response model
Run this after updating the model to add transcript, ai_score, ai_feedback, and ai_data columns
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Response
from flask import current_app

def add_ai_fields():
    """Add AI-related columns to responses table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('responses')]
            
            columns_to_add = {
                'transcript': 'TEXT',
                'ai_score': 'INTEGER',
                'ai_feedback': 'TEXT',
                'ai_data': 'TEXT'
            }
            
            missing_columns = {col: col_type for col, col_type in columns_to_add.items() 
                             if col not in existing_columns}
            
            if not missing_columns:
                print("[OK] All AI fields already exist in responses table")
                return
            
            print(f"Adding {len(missing_columns)} missing AI field(s) to responses table...")
            
            # Add missing columns
            for col_name, col_type in missing_columns.items():
                try:
                    db.session.execute(db.text(f"ALTER TABLE responses ADD COLUMN {col_name} {col_type}"))
                    print(f"  [OK] Added {col_name} column")
                except Exception as e:
                    print(f"  [WARNING] Could not add {col_name}: {e}")
            
            # Commit changes
            db.session.commit()
            print("\n[SUCCESS] Successfully added AI fields to responses table!")
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Error adding AI fields: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    add_ai_fields()

