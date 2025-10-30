"""
Database migration script to add comments and comment_likes tables
"""

import sys
import os

# Add parent directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models import Comment, CommentLike

def add_comments_tables():
    """Add comments and comment_likes tables to the database"""
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("Adding Comments Tables to Database")
        print("=" * 70)
        print()
        
        try:
            # Create tables
            print("Creating 'comments' table...")
            print("Creating 'comment_likes' table...")
            
            db.create_all()
            
            print()
            print("✅ Tables created successfully!")
            print()
            print("Tables added:")
            print("  - comments")
            print("  - comment_likes")
            print()
            print("Columns in 'comments':")
            print("  - id (Integer, Primary Key)")
            print("  - question_id (Integer, Foreign Key → questions.id)")
            print("  - user_id (Integer, Foreign Key → users.id)")
            print("  - parent_id (Integer, Foreign Key → comments.id, nullable)")
            print("  - content (Text)")
            print("  - is_edited (Boolean)")
            print("  - is_pinned (Boolean)")
            print("  - likes_count (Integer)")
            print("  - replies_count (Integer)")
            print("  - created_at (DateTime)")
            print("  - updated_at (DateTime)")
            print()
            print("Columns in 'comment_likes':")
            print("  - id (Integer, Primary Key)")
            print("  - comment_id (Integer, Foreign Key → comments.id)")
            print("  - user_id (Integer, Foreign Key → users.id)")
            print("  - created_at (DateTime)")
            print("  - UNIQUE(comment_id, user_id) - Prevents duplicate likes")
            print()
            print("=" * 70)
            print("Migration Complete!")
            print("=" * 70)
            
        except Exception as e:
            print(f"❌ Error creating tables: {str(e)}")
            print()
            print("If tables already exist, this is normal.")
            return False
        
        return True

if __name__ == '__main__':
    add_comments_tables()


