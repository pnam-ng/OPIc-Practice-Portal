@echo off
REM Quick AI Setup Script for Windows
REM This script installs AI dependencies for OPIc Practice Portal

echo ============================================
echo OPIc AI Integration - Quick Setup
echo ============================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run this script from the OPP directory
    echo or create a venv first: python -m venv venv
    pause
    exit /b 1
)

echo Step 1: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 2: Installing AI dependencies...
pip install -r requirements-ai.txt

echo.
echo Step 3: Installing CPU-optimized PyTorch...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo Step 4: Checking Ollama installation...
where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Ollama not found!
    echo Please install Ollama manually:
    echo 1. Download from: https://ollama.com/download/windows
    echo 2. Run OllamaSetup.exe
    echo 3. Then run: ollama pull llama3.1:8b
    echo.
) else (
    echo Ollama found! Pulling model...
    ollama pull llama3.1:8b
)

echo.
echo Step 5: Creating test script...
(
echo import whisper
echo import ollama
echo.
echo print^("Testing AI Setup..."^)
echo print^("1. Loading Whisper small model..."^)
echo model = whisper.load_model^("small"^)
echo print^("   ✓ Whisper loaded!"^)
echo.
echo print^("2. Testing Ollama..."^)
echo try:
echo     response = ollama.chat^(model='llama3.1:8b', messages=[{'role': 'user', 'content': 'Say hello!'}]^)
echo     print^(f"   ✓ Ollama works: {response['message']['content']}"^)
echo except Exception as e:
echo     print^(f"   ✗ Ollama error: {e}"^)
echo     print^("   Make sure Ollama is running: ollama serve"^)
echo.
echo print^("Setup complete!"^)
) > test_ai_quick.py

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Make sure Ollama is running: ollama serve
echo 2. Test the setup: python test_ai_quick.py
echo 3. Read the guide: docs\development\QUICK_AI_SETUP.md
echo.
pause



