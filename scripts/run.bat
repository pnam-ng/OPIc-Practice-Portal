@echo off
echo ============================================================
echo    OPIc Practice Portal - HTTP Server
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to set up the environment.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy config.env.example to .env and configure it.
    pause
)

REM Run the application
echo Starting Flask application...
python app.py

pause
