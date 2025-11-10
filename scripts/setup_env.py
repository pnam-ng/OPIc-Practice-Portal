#!/usr/bin/env python3
"""
Setup environment variables for OPIc Practice Portal
Creates config.env from config.env.example if it doesn't exist
"""

import os
import secrets
from pathlib import Path

def generate_secret_key():
    """Generate a random secret key"""
    return secrets.token_hex(32)

def setup_env_file():
    """Setup config.env file"""
    project_root = Path(__file__).parent.parent
    config_example = project_root / 'config.env.example'
    config_file = project_root / 'config.env'
    
    if config_file.exists():
        print(f"✅ config.env already exists: {config_file}")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("Keeping existing config.env")
            return
    
    if not config_example.exists():
        print(f"❌ Error: {config_example} not found")
        return
    
    # Read example file
    with open(config_example, 'r') as f:
        content = f.read()
    
    # Generate secret key
    secret_key = generate_secret_key()
    content = content.replace('your-secret-key-here', secret_key)
    
    # Write config.env
    with open(config_file, 'w') as f:
        f.write(content)
    
    # Set permissions (read/write for owner only)
    os.chmod(config_file, 0o600)
    
    print(f"✅ Created config.env: {config_file}")
    print(f"✅ Generated SECRET_KEY: {secret_key[:20]}...")
    print()
    print("⚠️  IMPORTANT: Edit config.env and add your GOOGLE_AI_API_KEY")
    print("   Get your FREE API key at: https://aistudio.google.com/app/apikey")
    print()
    print("Next steps:")
    print("1. Edit config.env: nano config.env")
    print("2. Add your GOOGLE_AI_API_KEY")
    print("3. Restart the server")

if __name__ == '__main__':
    setup_env_file()

