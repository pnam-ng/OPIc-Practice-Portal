@echo off
REM OPIc Practice Portal - Migration Package Creator (Windows)
REM This script creates a migration package for deploying to Oracle Cloud VM

echo ============================================================
echo OPIc Practice Portal - Migration Package Creator
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found. Running migration script...
echo.

REM Run the migration script
python scripts\migrate_project.py

echo.
echo ============================================================
echo Migration package creation completed!
echo ============================================================
echo.
echo Next steps:
echo 1. Transfer the migration package to Oracle Cloud VM
echo 2. Follow instructions in MIGRATION_SETUP_INSTRUCTIONS.md
echo.
pause


