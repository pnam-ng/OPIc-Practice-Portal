"""
Migration script to add thumbnail_path column to tips table
Run this script to add the thumbnail_path column to the existing tips table
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Tip

def add_thumbnail_column():
    """Add thumbnail_path column to tips table"""
    app = create_app()
    
    with app.app_context():
        try:
            # SQLAlchemy will handle the migration automatically when we access the model
            # But we'll use raw SQL to add the column if it doesn't exist
            from sqlalchemy import inspect, text
            
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('tips')]
            
            if 'thumbnail_path' not in columns:
                # Add the column using raw SQL
                db.session.execute(text('ALTER TABLE tips ADD COLUMN thumbnail_path VARCHAR(300)'))
                db.session.commit()
                print("✓ thumbnail_path column added successfully")
            else:
                print("✓ thumbnail_path column already exists")
            
            # Optionally generate thumbnails for existing tips
            tips_without_thumbnails = Tip.query.filter_by(thumbnail_path=None).all()
            if tips_without_thumbnails:
                print(f"\nFound {len(tips_without_thumbnails)} tips without thumbnails")
                print("To generate thumbnails for existing tips, run: python scripts/generate_tip_thumbnails.py")
            else:
                print("\n✓ All tips have thumbnails")
                
        except Exception as e:
            print(f"✗ Error adding thumbnail_path column: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == '__main__':
    add_thumbnail_column()




