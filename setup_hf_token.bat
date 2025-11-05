@echo off
echo ========================================
echo Hugging Face API Token Setup
echo ========================================
echo.
echo This script will help you add your Hugging Face API token.
echo.
echo Step 1: Get your token from https://huggingface.co/settings/tokens
echo Step 2: Paste it below when prompted
echo.
set /p HF_TOKEN="Enter your Hugging Face API token (starts with hf_): "

if "%HF_TOKEN%"=="" (
    echo Error: Token cannot be empty!
    pause
    exit /b 1
)

echo.
echo Adding token to .env file...
echo HUGGINGFACE_API_KEY=%HF_TOKEN% > .env
echo.
echo ✅ Token added successfully!
echo.
echo Your .env file has been created/updated.
echo You can now restart your Flask app to use the Hugging Face API.
echo.
pause








