"""
Database Health Check Script
Checks the database structure and identifies any issues after migration
"""
import os
import sys

# Ensure the application package is importable
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import text
from app import create_app, db

def check_database():
    """Check database health after migration"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=" * 60)
            print("DATABASE HEALTH CHECK")
            print("=" * 60)
            print()
            
            # Check questions table structure
            print("[1] Checking questions table structure...")
            result = db.session.execute(text("PRAGMA table_info(questions)"))
            columns = [(row[1], row[2]) for row in result.fetchall()]
            print(f"    Columns found: {len(columns)}")
            for col_name, col_type in columns:
                print(f"    - {col_name}: {col_type}")
            print()
            
            # Check for legacy columns
            column_names = [col[0] for col in columns]
            if 'category' in column_names or 'difficulty' in column_names:
                print("    ⚠️  WARNING: Legacy columns still exist!")
                print("    Run: python scripts/remove_question_category.py")
            else:
                print("    ✓ No legacy columns found")
            print()
            
            # Check questions count
            print("[2] Checking questions table data...")
            result = db.session.execute(text("SELECT COUNT(*) FROM questions"))
            count = result.scalar()
            print(f"    Total questions: {count}")
            
            if count > 0:
                # Sample a question
                result = db.session.execute(text("SELECT id, topic, difficulty_level FROM questions LIMIT 1"))
                sample = result.fetchone()
                print(f"    Sample question: ID={sample[0]}, Topic={sample[1]}, Level={sample[2]}")
            print()
            
            # Check responses table
            print("[3] Checking responses table...")
            result = db.session.execute(text("SELECT COUNT(*) FROM responses"))
            count = result.scalar()
            print(f"    Total responses: {count}")
            print()
            
            # Check foreign key integrity
            print("[4] Checking foreign key integrity...")
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM responses 
                WHERE question_id NOT IN (SELECT id FROM questions)
            """))
            orphaned = result.scalar()
            if orphaned > 0:
                print(f"    ⚠️  WARNING: {orphaned} orphaned responses found!")
            else:
                print(f"    ✓ All responses have valid question references")
            print()
            
            # Check indexes
            print("[5] Checking indexes...")
            result = db.session.execute(text("PRAGMA index_list(questions)"))
            indexes = result.fetchall()
            if indexes:
                print(f"    Indexes found: {len(indexes)}")
                for idx in indexes:
                    print(f"    - {idx[1]}")
            else:
                print("    ⚠️  No indexes found (may affect performance)")
            print()
            
            # Try to query questions (simulate what the app does)
            print("[6] Testing typical queries...")
            try:
                result = db.session.execute(text("""
                    SELECT id, topic, difficulty_level, language 
                    FROM questions 
                    WHERE language = 'english' 
                    LIMIT 5
                """))
                questions = result.fetchall()
                print(f"    ✓ Successfully queried {len(questions)} questions")
            except Exception as e:
                print(f"    ✗ Query failed: {e}")
            print()
            
            print("=" * 60)
            print("HEALTH CHECK COMPLETE")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n[ERROR] Health check failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    check_database()
