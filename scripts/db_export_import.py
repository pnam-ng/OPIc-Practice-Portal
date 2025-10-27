#!/usr/bin/env python3
"""
Database Export/Import Script for OPIc Practice Portal
Export database to SQL dump or import from SQL dump
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.models import User, Question, Response, Survey

def export_database():
    """Export database to SQL dump file"""
    print("📤 Exporting database...")
    
    # Create exports directory
    exports_dir = Path("database_exports")
    exports_dir.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_file = exports_dir / f"opic_portal_export_{timestamp}.sql"
    
    # Database file path
    db_file = Path("instance/opic_portal.db")
    
    if not db_file.exists():
        print("❌ Database file not found!")
        return False
    
    try:
        # Use sqlite3 to dump the database
        cmd = f'sqlite3 "{db_file}" ".dump" > "{export_file}"'
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        
        print(f"✅ Database exported to: {export_file}")
        print(f"📊 File size: {export_file.stat().st_size / 1024:.1f} KB")
        
        # Also create a summary
        create_export_summary(export_file)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Export failed: {e}")
        return False

def create_export_summary(export_file):
    """Create a summary of the exported database"""
    app = create_app()
    with app.app_context():
        summary_file = export_file.with_suffix('.summary.txt')
        
        with open(summary_file, 'w') as f:
            f.write("OPIc Practice Portal - Database Export Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Export File: {export_file.name}\n\n")
            
            f.write("Database Contents:\n")
            f.write(f"  Users: {User.query.count()}\n")
            f.write(f"  Questions: {Question.query.count()}\n")
            f.write(f"  Responses: {Response.query.count()}\n")
            f.write(f"  Surveys: {Survey.query.count()}\n\n")
            
            f.write("Question Distribution:\n")
            levels = ['IM', 'IH', 'AL']
            for level in levels:
                count = Question.query.filter_by(difficulty_level=level).count()
                f.write(f"  {level}: {count} questions\n")
            
            f.write("\nUser Accounts:\n")
            users = User.query.all()
            for user in users:
                f.write(f"  {user.username} ({'Admin' if user.is_admin else 'User'})\n")
        
        print(f"📋 Export summary created: {summary_file.name}")

def import_database(sql_file):
    """Import database from SQL dump file"""
    print(f"📥 Importing database from: {sql_file}")
    
    if not os.path.exists(sql_file):
        print(f"❌ Import file not found: {sql_file}")
        return False
    
    # Database file path
    db_file = Path("instance/opic_portal.db")
    
    # Backup existing database if it exists
    if db_file.exists():
        backup_file = db_file.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        db_file.rename(backup_file)
        print(f"💾 Existing database backed up to: {backup_file.name}")
    
    try:
        # Create instance directory
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Import the SQL dump
        cmd = f'sqlite3 "{db_file}" < "{sql_file}"'
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        
        print(f"✅ Database imported successfully!")
        
        # Verify import
        verify_import()
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Import failed: {e}")
        return False

def verify_import():
    """Verify the imported database"""
    app = create_app()
    with app.app_context():
        print("\n📊 Imported Database Summary:")
        print(f"  Users: {User.query.count()}")
        print(f"  Questions: {Question.query.count()}")
        print(f"  Responses: {Response.query.count()}")
        print(f"  Surveys: {Survey.query.count()}")
        
        print("\n📋 Question Distribution:")
        levels = ['IM', 'IH', 'AL']
        for level in levels:
            count = Question.query.filter_by(difficulty_level=level).count()
            print(f"  {level}: {count} questions")
        
        print("\n👤 User Accounts:")
        users = User.query.all()
        for user in users:
            print(f"  {user.username} ({'Admin' if user.is_admin else 'User'})")

def list_exports():
    """List available export files"""
    exports_dir = Path("database_exports")
    
    if not exports_dir.exists():
        print("📁 No exports directory found")
        return
    
    export_files = list(exports_dir.glob("*.sql"))
    
    if not export_files:
        print("📁 No export files found")
        return
    
    print("📁 Available export files:")
    for export_file in sorted(export_files, key=lambda x: x.stat().st_mtime, reverse=True):
        size = export_file.stat().st_size / 1024
        mtime = datetime.fromtimestamp(export_file.stat().st_mtime)
        print(f"  {export_file.name} ({size:.1f} KB, {mtime.strftime('%Y-%m-%d %H:%M')})")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("OPIc Practice Portal - Database Export/Import Tool")
        print("=" * 55)
        print("\nUsage:")
        print("  python db_export_import.py export          # Export database")
        print("  python db_export_import.py import <file>   # Import database")
        print("  python db_export_import.py list            # List exports")
        print("\nExamples:")
        print("  python db_export_import.py export")
        print("  python db_export_import.py import database_exports/opic_portal_export_20241201_143022.sql")
        print("  python db_export_import.py list")
        return
    
    command = sys.argv[1].lower()
    
    if command == "export":
        export_database()
    elif command == "import":
        if len(sys.argv) < 3:
            print("❌ Please specify the SQL file to import")
            return
        import_database(sys.argv[2])
    elif command == "list":
        list_exports()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
