#!/bin/bash
# Start Gunicorn server for OPIc Practice Portal

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start Gunicorn using wsgi.py
# Option 1: Using config file (recommended)
gunicorn -c gunicorn_config.py wsgi:application

# Option 2: Direct command (if config file has issues)
# gunicorn wsgi:application --bind 0.0.0.0:5000 --workers 4 --timeout 120

