#!/usr/bin/env python3
"""
Reorganize project files for git commit
Moves deployment documentation to docs/deployment/
"""

import os
import shutil
from pathlib import Path

# Project root
project_root = Path(__file__).parent.parent

# Files to move to docs/deployment/
files_to_move = [
    'MIGRATION_GUIDE.md',
    'MIGRATION_CHECKLIST.md',
    'MIGRATION_QUICK_START.md',
    'MIGRATION_SETUP_INSTRUCTIONS.md',
    'GUNICORN_SETUP.md',
    'QUICK_START_SERVER.md',
]

# Create docs/deployment directory
deployment_dir = project_root / 'docs' / 'deployment'
deployment_dir.mkdir(parents=True, exist_ok=True)

# Move files
moved_files = []
for filename in files_to_move:
    src = project_root / filename
    dst = deployment_dir / filename
    
    if src.exists():
        try:
            shutil.move(str(src), str(dst))
            moved_files.append(filename)
            print(f"✅ Moved {filename} to docs/deployment/")
        except Exception as e:
            print(f"❌ Failed to move {filename}: {e}")
    else:
        print(f"⚠️  File not found: {filename}")

print(f"\n📦 Moved {len(moved_files)} files to docs/deployment/")

# Move summary.md to docs/sessions/ if it exists
summary_src = project_root / 'summary.md'
summary_dst = project_root / 'docs' / 'sessions' / 'SESSION_CURRENT_SUMMARY.md'

if summary_src.exists():
    try:
        # Check if docs/summary.md is different (keep the more complete one)
        docs_summary = project_root / 'docs' / 'summary.md'
        if docs_summary.exists():
            # Root summary.md is a session summary, move it to sessions
            shutil.move(str(summary_src), str(summary_dst))
            print(f"✅ Moved summary.md to docs/sessions/SESSION_CURRENT_SUMMARY.md")
        else:
            # No docs/summary.md, move root one there
            shutil.move(str(summary_src), str(docs_summary))
            print(f"✅ Moved summary.md to docs/summary.md")
    except Exception as e:
        print(f"❌ Failed to move summary.md: {e}")

print("\n✨ File reorganization complete!")

