#!/usr/bin/env python3
"""Add meaning_vi and meaning_ko columns to the vocabulary table."""
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'opic_portal.db')

def add_columns():
    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check existing columns
    cursor.execute("PRAGMA table_info(vocabulary)")
    columns = [col[1] for col in cursor.fetchall()]

    added = []
    for col_name in ['meaning_vi', 'meaning_ko']:
        if col_name not in columns:
            cursor.execute(f"ALTER TABLE vocabulary ADD COLUMN {col_name} TEXT")
            added.append(col_name)
            print(f"Added column: {col_name}")
        else:
            print(f"Column already exists: {col_name}")

    conn.commit()
    conn.close()

    if added:
        print(f"\nMigration complete. Added {len(added)} column(s).")
    else:
        print("\nNo changes needed — columns already exist.")
    return True

if __name__ == '__main__':
    add_columns()
