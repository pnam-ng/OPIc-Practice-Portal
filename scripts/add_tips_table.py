"""
Migration script to add tips table
Run this script to create the tips table in the database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Tip

def create_tips_table():
    """Create the tips table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create the table
            db.create_all()
            print("✓ Tips table created successfully")
            
            # Check if table exists and has correct structure
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            if 'tips' in inspector.get_table_names():
                print("✓ Tips table verified")
                
                # Optionally, add default tip if table is empty
                existing_tip = Tip.query.filter_by(filename='secrets-from-an-opic-rater.pdf').first()
                if not existing_tip:
                    default_tip = Tip(
                        title='OPIc Rater Guidelines',
                        description='Learn about OPIc test evaluation criteria, scoring guidelines, and what raters look for in responses.',
                        filename='secrets-from-an-opic-rater.pdf',
                        category='Test Preparation',
                        display_order=1,
                        is_active=True
                    )
                    db.session.add(default_tip)
                    db.session.commit()
                    print("✓ Default tip added successfully")
                else:
                    print("✓ Default tip already exists")
            else:
                print("✗ Tips table not found")
                
        except Exception as e:
            print(f"✗ Error creating tips table: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_tips_table()



