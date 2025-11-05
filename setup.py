#!/usr/bin/env python3
"""
OPIc Practice Portal - Setup Script
Automated setup for local development environment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def setup_virtual_environment():
    """Create and activate virtual environment"""
    if not os.path.exists("venv"):
        return run_command("python -m venv venv", "Creating virtual environment")
    else:
        print("✅ Virtual environment already exists")
        return True

def install_dependencies():
    """Install Python dependencies"""
    # Determine the correct pip command based on OS
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
    
    return run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies")

def setup_environment():
    """Set up environment variables"""
    if not os.path.exists(".env"):
        if os.path.exists("config.env.example"):
            shutil.copy("config.env.example", ".env")
            print("✅ Created .env file from template")
            print("📝 Please edit .env file with your configuration")
        else:
            print("⚠️  config.env.example not found, creating basic .env")
            with open(".env", "w") as f:
                f.write("""FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///instance/opic_portal.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
""")
    else:
        print("✅ .env file already exists")

def initialize_database():
    """Initialize the database with sample data"""
    # Determine the correct python command based on OS
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "venv/bin/python"
    
    return run_command(f"{python_cmd} scripts/init_db_with_samples.py", "Initializing database with sample data")

def create_admin_user():
    """Create admin user"""
    # Determine the correct python command based on OS
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "venv/bin/python"
    
    return run_command(f"{python_cmd} ensure_admin.py", "Creating admin user")

def setup_audio_structure():
    """Set up audio file directory structure"""
    # Determine the correct python command based on OS
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "venv/bin/python"
    
    return run_command(f"{python_cmd} scripts/audio_setup.py", "Creating audio directory structure")

def main():
    """Main setup function"""
    print("🚀 OPIc Practice Portal - Setup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Initialize database with sample data
    if not initialize_database():
        print("⚠️  Database initialization failed, but continuing...")
    
    # Set up audio structure
    if not setup_audio_structure():
        print("⚠️  Audio structure setup failed, but continuing...")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Activate virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source venv/bin/activate")
    print("3. Run the application:")
    print("   python app.py")
    print("\n🌐 The application will be available at http://localhost:5000")
    print("👤 Admin user setup:")
    print("   Run 'python scripts/ensure_admin.py' to create admin user")
    print("   Password will be prompted or set via ADMIN_PASSWORD environment variable")
    print("\n🎵 Audio Files:")
    print("   Audio files are not included in the repository")
    print("   See AUDIO_SETUP.md for instructions on adding audio files")

if __name__ == "__main__":
    main()
