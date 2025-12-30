#!/usr/bin/env python3
"""
Production Script: Fix Email Constraint
========================================
This script fixes the 'email' column constraint in the 'users' table,
making it nullable to allow account creation without email.

USAGE:
------
1. Copy this script to the production server
2. Stop the application (Flask server)
3. Run: python fix_email_constraint_production.py
4. Restart the application

IMPORTANT:
----------
- Always backup your database before running this script
- Ensure no other processes are accessing the database
- The script will create an automatic backup before migration
"""

import sqlite3
import os
import sys
import shutil
from datetime import datetime

# ============================================================================
# CONFIGURATION - Modify these paths as needed for your server
# ============================================================================
DB_PATH = 'instance/opic_portal.db'  # Relative to script location or absolute path

# ============================================================================
# SCRIPT LOGIC - Do not modify below unless necessary
# ============================================================================

def get_db_path():
    """Resolve the database path."""
    # Try relative path first
    if os.path.exists(DB_PATH):
        return DB_PATH
    
    # Try relative to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_in_script_dir = os.path.join(script_dir, '..', 'instance', 'opic_portal.db')
    if os.path.exists(db_in_script_dir):
        return db_in_script_dir
    
    return None


def create_backup(db_path):
    """Create a timestamped backup of the database."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{db_path}.backup_{timestamp}"
    
    print(f"Creating backup at: {backup_path}")
    shutil.copy2(db_path, backup_path)
    print("Backup created successfully.")
    return backup_path


def check_email_column(cursor):
    """Check if email column exists and its current state."""
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    
    # Column info: (id, name, type, notnull, dflt_value, pk)
    email_col = next((c for c in columns if c[1] == 'email'), None)
    
    if email_col is None:
        return None, "Column not found"
    
    is_nullable = email_col[3] == 0  # notnull = 0 means nullable
    return email_col, "nullable" if is_nullable else "not nullable"


def migrate_email_column(cursor, conn):
    """Perform the migration to make email nullable."""
    
    # Disable foreign keys and start transaction
    cursor.execute("PRAGMA foreign_keys=OFF")
    cursor.execute("BEGIN TRANSACTION")
    
    try:
        # Create new table with nullable email
        print("Creating temporary table 'users_new'...")
        cursor.execute("""
        CREATE TABLE users_new (
            id INTEGER NOT NULL PRIMARY KEY, 
            username VARCHAR(80) NOT NULL UNIQUE, 
            email VARCHAR(120) UNIQUE, 
            password_hash VARCHAR(128), 
            name VARCHAR(100) NOT NULL, 
            target_language VARCHAR(20), 
            avatar VARCHAR(200), 
            streak_count INTEGER, 
            last_active_date DATE, 
            is_admin BOOLEAN, 
            created_at DATETIME, 
            updated_at DATETIME, 
            current_level VARCHAR(10), 
            target_level VARCHAR(10)
        )
        """)
        
        # Copy data from old table to new table
        print("Copying data from 'users' to 'users_new'...")
        cursor.execute("""
        INSERT INTO users_new (
            id, username, email, password_hash, name, target_language, 
            avatar, streak_count, last_active_date, is_admin, 
            created_at, updated_at, current_level, target_level
        ) 
        SELECT 
            id, username, email, password_hash, name, target_language, 
            avatar, streak_count, last_active_date, is_admin, 
            created_at, updated_at, current_level, target_level 
        FROM users
        """)
        
        # Get row count for verification
        cursor.execute("SELECT COUNT(*) FROM users")
        old_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users_new")
        new_count = cursor.fetchone()[0]
        
        if old_count != new_count:
            raise Exception(f"Row count mismatch! Old: {old_count}, New: {new_count}")
        
        print(f"Verified: {new_count} rows copied successfully.")
        
        # Drop old table and rename new table
        print("Swapping tables...")
        cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        
        # Commit transaction
        conn.commit()
        print("Migration committed successfully.")
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.execute("PRAGMA foreign_keys=ON")


def main():
    print("=" * 60)
    print("  Production Fix: Make 'email' Column Nullable")
    print("=" * 60)
    print()
    
    # Find database
    db_path = get_db_path()
    if db_path is None:
        print(f"ERROR: Database not found!")
        print(f"Tried: {DB_PATH}")
        print("\nPlease update the DB_PATH variable at the top of this script.")
        sys.exit(1)
    
    db_path = os.path.abspath(db_path)
    print(f"Database found: {db_path}")
    print(f"Database size: {os.path.getsize(db_path) / 1024:.2f} KB")
    print()
    
    # Confirmation prompt
    print("WARNING: This script will modify your database.")
    print("Make sure the Flask application is STOPPED before proceeding.")
    print()
    
    confirm = input("Type 'yes' to continue: ").strip().lower()
    if confirm != 'yes':
        print("Aborted by user.")
        sys.exit(0)
    print()
    
    # Create backup
    backup_path = create_backup(db_path)
    print()
    
    # Connect to database
    print("Connecting to database...")
    conn = sqlite3.connect(db_path, timeout=10)
    cursor = conn.cursor()
    
    try:
        # Check current state
        print("Checking 'email' column status...")
        email_col, status = check_email_column(cursor)
        
        if email_col is None:
            print(f"ERROR: {status}")
            sys.exit(1)
        
        print(f"Current status: email column is {status}")
        
        if status == "nullable":
            print()
            print("SUCCESS: 'email' column is already nullable.")
            print("No migration needed.")
            conn.close()
            sys.exit(0)
        
        print()
        print("Starting migration...")
        print("-" * 40)
        
        # Perform migration
        migrate_email_column(cursor, conn)
        
        print("-" * 40)
        print()
        
        # Verify result
        email_col, status = check_email_column(cursor)
        if status == "nullable":
            print("VERIFICATION PASSED: 'email' column is now nullable.")
        else:
            print(f"WARNING: Verification shows email is still {status}")
        
        print()
        print("=" * 60)
        print("  MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()
        print(f"Backup saved at: {backup_path}")
        print("You can now restart your Flask application.")
        
    except sqlite3.OperationalError as e:
        if "locked" in str(e).lower():
            print()
            print("ERROR: Database is locked!")
            print("Please stop the Flask server and any database tools.")
            print(f"\nBackup available at: {backup_path}")
        else:
            print(f"Database error: {e}")
        sys.exit(1)
        
    except Exception as e:
        print()
        print(f"ERROR: Migration failed - {e}")
        print(f"\nBackup available at: {backup_path}")
        print("Please restore from backup if needed.")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()
