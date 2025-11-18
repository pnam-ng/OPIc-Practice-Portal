#!/bin/bash
# Wrapper script to run remove_question_category.py migration
# This ensures the script runs from the correct directory

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "=========================================="
echo "OPIc Migration: Remove Question Category"
echo "=========================================="
echo ""
echo "Project root: $PROJECT_ROOT"
echo ""

# Change to project root
cd "$PROJECT_ROOT" || {
    echo "[ERROR] Cannot change to project root: $PROJECT_ROOT"
    exit 1
}

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "[INFO] Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "[INFO] Activating virtual environment..."
    source .venv/bin/activate
else
    echo "[WARNING] No virtual environment found. Using system Python."
fi

# Check Python version
PYTHON_VERSION=$(python --version 2>&1)
echo "[INFO] Using: $PYTHON_VERSION"
echo ""

# Run the migration script
echo "[INFO] Running migration script..."
echo "=========================================="
echo ""

python scripts/remove_question_category.py

EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "[OK] Migration completed successfully!"
else
    echo "[ERROR] Migration failed with exit code: $EXIT_CODE"
fi
echo "=========================================="

exit $EXIT_CODE
