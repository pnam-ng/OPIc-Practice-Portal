import sqlite3
import os
import sys

# Define database path
db_path = 'instance/opic_portal.db'
if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    sys.exit(1)

# Connect to the database with a timeout to avoid indefinite hanging on locks
conn = sqlite3.connect(db_path, timeout=5)
cursor = conn.cursor()

try:
    print("Inspecting 'users' table schema...")
    
    # 1. Get current columns to ensure we preserve everything accurately
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    
    # Column info: (id, name, type, notnull, dflt_value, pk)
    email_col = next((c for c in columns if c[1] == 'email'), None)
    
    if email_col is None:
        print("Error: 'email' column not found in 'users' table.")
        sys.exit(1)
        
    if email_col[3] == 0:
        print("Success: 'email' column is already nullable. No migration needed.")
        conn.close()
        sys.exit(0)

    print("Starting migration to make 'email' nullable...")
    
    # 2. Disable foreign keys and start a transaction
    cursor.execute("PRAGMA foreign_keys=OFF")
    cursor.execute("BEGIN TRANSACTION")
    
    # 3. Create a new table with the same structure but 'email' is nullable
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
    
    # 4. Copy data from old table to new table
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
    
    # 5. Drop old table and rename new table
    print("Swapping tables...")
    cursor.execute("DROP TABLE users")
    cursor.execute("ALTER TABLE users_new RENAME TO users")
    
    # 6. Commit transaction
    conn.commit()
    print("Success: 'email' is now nullable.")
    
except sqlite3.OperationalError as e:
    conn.rollback()
    if "locked" in str(e).lower():
        print("Error: Database is locked. Please stop the Flask server and any other database tools.")
    else:
        print(f"Database error: {e}")
    sys.exit(1)
except Exception as e:
    conn.rollback()
    print(f"Migration failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    cursor.execute("PRAGMA foreign_keys=ON")
    conn.close()
