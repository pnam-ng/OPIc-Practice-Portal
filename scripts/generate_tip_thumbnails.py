"""
Script to generate thumbnails for existing tips
Run this script to generate thumbnails for tips that don't have them yet
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Tip
from app.utils.pdf_thumbnail import generate_pdf_thumbnail, get_thumbnail_path

def generate_all_thumbnails():
    """Generate thumbnails for all tips that don't have them"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get all tips without thumbnails
            tips = Tip.query.filter((Tip.thumbnail_path == None) | (Tip.thumbnail_path == '')).all()
            
            if not tips:
                print("✓ All tips already have thumbnails")
                return
            
            print(f"Found {len(tips)} tips without thumbnails")
            
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            files_dir = os.path.join(base_dir, 'files')
            
            success_count = 0
            error_count = 0
            
            for tip in tips:
                try:
                    file_path = os.path.join(files_dir, tip.filename)
                    
                    if not os.path.exists(file_path):
                        print(f"✗ File not found for tip '{tip.title}': {tip.filename}")
                        error_count += 1
                        continue
                    
                    # Generate thumbnail
                    thumbnail_full_path = get_thumbnail_path(tip.filename, base_dir)
                    
                    if generate_pdf_thumbnail(file_path, thumbnail_full_path):
                        # Store relative path for database
                        tip.thumbnail_path = os.path.join('static', 'thumbnails', os.path.basename(thumbnail_full_path))
                        db.session.commit()
                        print(f"✓ Generated thumbnail for: {tip.title}")
                        success_count += 1
                    else:
                        print(f"✗ Failed to generate thumbnail for: {tip.title}")
                        error_count += 1
                        
                except Exception as e:
                    print(f"✗ Error processing tip '{tip.title}': {e}")
                    error_count += 1
                    db.session.rollback()
            
            print(f"\n✓ Successfully generated {success_count} thumbnails")
            if error_count > 0:
                print(f"✗ Failed to generate {error_count} thumbnails")
                
        except Exception as e:
            print(f"✗ Error generating thumbnails: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == '__main__':
    generate_all_thumbnails()




