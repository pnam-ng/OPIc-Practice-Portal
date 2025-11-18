"""
Migration Script: Remove legacy 'category' and 'difficulty' columns from questions table.

Usage:
    cd /path/to/opp
    python scripts/remove_question_category.py

The script is idempotent — if the columns were already removed, it simply exits.
"""
import os
import sys
import traceback

# Ensure the application package is importable when running standalone
# Get the absolute path to the project root (parent of scripts directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Remove any existing paths that might conflict
sys.path = [p for p in sys.path if not p.endswith('opp')]

# Add project root to the beginning of sys.path
sys.path.insert(0, PROJECT_ROOT)

# Verify we're in the correct directory
if not os.path.exists(os.path.join(PROJECT_ROOT, 'app', '__init__.py')):
    print(f"[ERROR] Cannot find Flask app at {PROJECT_ROOT}/app/__init__.py")
    print(f"[ERROR] Current directory: {os.getcwd()}")
    print(f"[ERROR] Script directory: {SCRIPT_DIR}")
    print(f"[ERROR] Project root: {PROJECT_ROOT}")
    print("\n[SOLUTION] Please run this script from the project root directory:")
    print(f"    cd {PROJECT_ROOT}")
    print(f"    python scripts/remove_question_category.py")
    sys.exit(1)

print(f"[INFO] Project root: {PROJECT_ROOT}")
print(f"[INFO] Importing Flask app from: {os.path.join(PROJECT_ROOT, 'app')}")

from sqlalchemy import text, inspect

try:
    from app import create_app, db  # noqa: E402
    print("[OK] Successfully imported Flask app")
except ImportError as e:
    print(f"[ERROR] Failed to import Flask app: {e}")
    print(f"[ERROR] sys.path: {sys.path}")
    print("\n[SOLUTION] Make sure you're running from the project root:")
    print(f"    cd {PROJECT_ROOT}")
    print(f"    python scripts/remove_question_category.py")
    sys.exit(1)


def remove_category_column():
    """Drop legacy columns from questions."""
    app = create_app()

    with app.app_context():
        try:
            # Check current table structure
            print("[INFO] Checking current table structure...")
            result = db.session.execute(text("PRAGMA table_info(questions)"))
            columns = [row[1] for row in result.fetchall()]
            
            print(f"[INFO] Current columns: {', '.join(columns)}")
            
            legacy_columns = {'category', 'difficulty'}
            columns_to_remove = legacy_columns.intersection(columns)

            if not columns_to_remove:
                print("[OK] Legacy columns already removed — no changes needed.")
                return

            print(f"[INFO] Found legacy columns to remove: {', '.join(columns_to_remove)}")
            print("[INFO] Starting migration...")
            
            # Count existing questions
            count_result = db.session.execute(text("SELECT COUNT(*) FROM questions"))
            question_count = count_result.scalar()
            print(f"[INFO] Found {question_count} questions to migrate")

            # Disable foreign keys temporarily
            db.session.execute(text("PRAGMA foreign_keys=OFF;"))
            
            # Create new table without legacy columns
            print("[INFO] Creating new table structure...")
            db.session.execute(text("""
                CREATE TABLE questions_new (
                    id INTEGER PRIMARY KEY,
                    topic VARCHAR(100) NOT NULL,
                    language VARCHAR(20) DEFAULT 'english',
                    text TEXT,
                    difficulty_level VARCHAR(10),
                    question_type VARCHAR(20) DEFAULT 'question',
                    audio_url VARCHAR(200),
                    created_at DATETIME,
                    updated_at DATETIME,
                    sample_answer_text TEXT,
                    sample_answer_audio_url VARCHAR(200)
                );
            """))

            # Copy data from old table to new table
            print("[INFO] Copying data to new table...")
            db.session.execute(text("""
                INSERT INTO questions_new (
                    id, topic, language, text, difficulty_level,
                    question_type, audio_url, created_at, updated_at,
                    sample_answer_text, sample_answer_audio_url
                )
                SELECT
                    id, topic, language, text, difficulty_level,
                    question_type, audio_url, created_at, updated_at,
                    sample_answer_text, sample_answer_audio_url
                FROM questions;
            """))

            # Verify data was copied
            verify_result = db.session.execute(text("SELECT COUNT(*) FROM questions_new"))
            new_count = verify_result.scalar()
            print(f"[INFO] Copied {new_count} questions to new table")
            
            if new_count != question_count:
                raise Exception(f"Data mismatch! Original: {question_count}, New: {new_count}")

            # Drop old table and rename new table
            print("[INFO] Replacing old table with new table...")
            db.session.execute(text("DROP TABLE questions;"))
            db.session.execute(text("ALTER TABLE questions_new RENAME TO questions;"))

            # Commit the transaction
            db.session.commit()
            
            # Re-enable foreign keys
            db.session.execute(text("PRAGMA foreign_keys=ON;"))
            
            print("[OK] Migration completed successfully!")
            print(f"[OK] Removed columns: {', '.join(columns_to_remove)}")
            print(f"[OK] Migrated {new_count} questions")

        except Exception as exc:
            print(f"\n[ERROR] Migration failed!")
            print(f"[ERROR] Error type: {type(exc).__name__}")
            print(f"[ERROR] Error message: {exc}")
            print("\n[ERROR] Full traceback:")
            traceback.print_exc()
            
            # Try to rollback
            try:
                db.session.rollback()
                print("\n[INFO] Transaction rolled back")
            except:
                print("\n[WARNING] Could not rollback transaction")
            
            # Try to re-enable foreign keys
            try:
                db.session.execute(text("PRAGMA foreign_keys=ON;"))
            except:
                pass
            
            sys.exit(1)


if __name__ == "__main__":
    remove_category_column()

