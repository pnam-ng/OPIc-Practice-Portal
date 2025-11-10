"""
WSGI entry point for Gunicorn
This file is used by Gunicorn to serve the Flask application in production.

The issue: Python's import system prefers the app/ package over app.py file.
Solution: Use runpy to execute app.py and get the app instance.

Usage:
    gunicorn -c gunicorn_config.py wsgi:application
    or
    gunicorn wsgi:application --bind 0.0.0.0:5000
"""

import os
import sys
import runpy
from dotenv import load_dotenv

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables BEFORE importing app
# Try multiple common environment file names
env_files = ['config.env', '.env', 'env']
loaded = False
for env_file in env_files:
    env_path = os.path.join(project_root, env_file)
    if os.path.exists(env_path):
        load_dotenv(env_path)
        loaded = True
        print(f"✅ Loaded environment from: {env_file}")
        break

if not loaded:
    # Try default load_dotenv() behavior
    load_dotenv()
    print("⚠️  No env file found, using system environment variables")

# Temporarily modify __name__ to prevent app.py's __main__ block from running
original_name = __name__
try:
    # Execute app.py and get the 'app' variable
    # runpy.run_path executes the file and returns its globals
    app_globals = runpy.run_path(
        os.path.join(project_root, 'app.py'),
        run_name='__wsgi__'  # Use a different name so __main__ block doesn't run
    )
    app = app_globals['app']
except KeyError:
    # If 'app' variable not found, try creating it using create_app
    import traceback
    print("Warning: 'app' variable not found in app.py")
    print("Trying to create app using create_app function...")
    traceback.print_exc()
    
    # Fallback: import create_app from app package
    try:
        from app import create_app
        app = create_app()
    except Exception as e:
        print(f"Error: Could not create app: {e}")
        import traceback
        traceback.print_exc()
        raise
except Exception as e:
    # Any other error
    import traceback
    print(f"Error loading app.py: {e}")
    traceback.print_exc()
    raise

# WSGI application interface (required by Gunicorn)
application = app

if __name__ == "__main__":
    print("Starting development server via WSGI...")
    app.run(host='0.0.0.0', port=5000, debug=False)

