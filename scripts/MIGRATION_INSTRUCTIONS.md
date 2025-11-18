# Migration Script Instructions

## Running `remove_question_category.py` on Remote Server

### Problem
If you get an error like:
```
cannot import the name 'create_app' from 'app' (/home/ubuntu/app.py)
```

This means Python is importing the wrong `app.py` file.

### Solution

**Step 1: Navigate to the correct project directory**
```bash
cd /home/ubuntu/opp
```

**Step 2: Verify you're in the right location**
```bash
ls -la
# You should see: app/, scripts/, templates/, static/, etc.
```

**Step 3: Run the migration script**
```bash
python scripts/remove_question_category.py
```

### Alternative: Run with explicit Python path

If the above doesn't work, try:

```bash
cd /home/ubuntu/opp
python3 scripts/remove_question_category.py
```

Or use the full path:

```bash
cd /home/ubuntu/opp
/usr/bin/python3 scripts/remove_question_category.py
```

### What the Script Does

1. **Checks** if legacy columns (`category`, `difficulty`) exist in the `questions` table
2. **If they exist**: Creates a new table without those columns, copies data, and replaces the old table
3. **If they don't exist**: Exits with "already removed" message

### Expected Output (Success)

```
[INFO] Project root: /home/ubuntu/opp
[INFO] Importing Flask app from: /home/ubuntu/opp/app
[OK] Successfully imported Flask app
[INFO] Checking current table structure...
[INFO] Current columns: id, topic, category, difficulty, language, text, ...
[INFO] Found legacy columns to remove: category, difficulty
[INFO] Starting migration...
[INFO] Found 1234 questions to migrate
[INFO] Creating new table structure...
[INFO] Copying data to new table...
[INFO] Copied 1234 questions to new table
[INFO] Replacing old table with new table...
[OK] Migration completed successfully!
[OK] Removed columns: category, difficulty
[OK] Migrated 1234 questions
```

### Expected Output (Already Done)

```
[INFO] Project root: /home/ubuntu/opp
[INFO] Importing Flask app from: /home/ubuntu/opp/app
[OK] Successfully imported Flask app
[INFO] Checking current table structure...
[INFO] Current columns: id, topic, language, text, difficulty_level, ...
[OK] Legacy columns already removed — no changes needed.
```

### Troubleshooting

**Error: "Cannot find Flask app at /path/app/__init__.py"**
- Make sure you're running from the project root (`/home/ubuntu/opp`)
- Check that the `app/` directory exists with `ls -la app/`

**Error: "No module named 'flask'"**
- Activate your virtual environment first:
  ```bash
  source venv/bin/activate  # or wherever your venv is
  python scripts/remove_question_category.py
  ```

**Error: Database is locked**
- Stop the Flask application first
- Make sure no other processes are accessing the database

### Backup Recommendation

Before running any migration, it's good practice to backup your database:

```bash
# For SQLite
cp instance/opic_portal.db instance/opic_portal.db.backup

# For PostgreSQL
pg_dump your_database > backup.sql
```

### After Migration

1. Restart your Flask application
2. Test that questions still load correctly
3. Verify that the admin question management still works
