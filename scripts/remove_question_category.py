"""
Migration Script: Remove legacy 'category' and 'difficulty' columns from questions table.

Usage:
    python scripts/remove_question_category.py

The script is idempotent — if the columns were already removed, it simply exits.
"""
import os
import sys

from sqlalchemy import text

# Ensure the application package is importable when running standalone
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app import create_app, db  # noqa: E402


def remove_category_column():
    """Drop legacy columns from questions."""
    app = create_app()

    with app.app_context():
        result = db.session.execute(text("PRAGMA table_info(questions)"))
        columns = [row[1] for row in result.fetchall()]
        legacy_columns = {'category', 'difficulty'}

        if legacy_columns.isdisjoint(columns):
            print("[OK] Legacy columns already removed — no changes needed.")
            return

        print("[INFO] Removing legacy columns from questions table...")
        db.session.execute(text("PRAGMA foreign_keys=OFF;"))
        db.session.execute(text("BEGIN TRANSACTION;"))

        try:
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

            db.session.execute(text("DROP TABLE questions;"))
            db.session.execute(text("ALTER TABLE questions_new RENAME TO questions;"))

            db.session.execute(text("COMMIT;"))
            print("[OK] Migration completed successfully.")

        except Exception as exc:
            print(f"[ERROR] Migration failed: {exc}")
            db.session.execute(text("ROLLBACK;"))
            raise

        finally:
            db.session.execute(text("PRAGMA foreign_keys=ON;"))


if __name__ == "__main__":
    remove_category_column()

