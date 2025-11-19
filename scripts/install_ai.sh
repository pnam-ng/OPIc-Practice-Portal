#!/bin/bash
# Quick AI Setup Script for Linux/macOS
# This script installs AI dependencies for OPIc Practice Portal

echo "============================================"
echo "OPIc AI Integration - Quick Setup"
echo "============================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run this script from the OPP directory"
    echo "or create a venv first: python -m venv venv"
    exit 1
fi

echo "Step 1: Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Step 2: Installing system dependencies..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux - Installing ffmpeg..."
    sudo apt-get update
    sudo apt-get install -y ffmpeg
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS - Installing ffmpeg with Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install ffmpeg
fi

echo ""
echo "Step 3: Installing AI dependencies..."
pip install -r requirements-ai.txt

echo ""
echo "Step 4: Installing CPU-optimized PyTorch..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo ""
echo "Step 5: Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama already installed!"
fi

echo ""
echo "Step 6: Pulling AI model..."
ollama pull llama3.1:8b

echo ""
echo "Step 7: Creating test script..."
cat > test_ai_quick.py << 'EOF'
import whisper
import ollama

print("Testing AI Setup...")
print("1. Loading Whisper small model...")
model = whisper.load_model("small")
print("   ✓ Whisper loaded!")

print("2. Testing Ollama...")
try:
    response = ollama.chat(model='llama3.1:8b', messages=[{'role': 'user', 'content': 'Say hello!'}])
    print(f"   ✓ Ollama works: {response['message']['content']}")
except Exception as e:
    print(f"   ✗ Ollama error: {e}")
    print("   Make sure Ollama is running: ollama serve")

print("Setup complete!")
EOF

echo ""
echo "============================================"
echo "Installation Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Start Ollama: ollama serve &"
echo "2. Test the setup: python test_ai_quick.py"
echo "3. Read the guide: docs/development/QUICK_AI_SETUP.md"
echo ""



