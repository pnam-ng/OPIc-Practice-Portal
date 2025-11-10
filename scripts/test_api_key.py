#!/usr/bin/env python3
"""
Test script to verify API key is loaded correctly
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv

env_files = ['config.env', '.env', 'env']
loaded = False
for env_file in env_files:
    env_path = project_root / env_file
    if env_path.exists():
        load_dotenv(env_path)
        loaded = True
        print(f"✅ Loaded environment from: {env_file}")
        break

if not loaded:
    load_dotenv()
    print("⚠️  No env file found, using system environment variables")

# Check API key
api_key = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GEMINI_API_KEY")

if api_key:
    print(f"✅ API Key found: {api_key[:20]}...{api_key[-10:]}")
    print(f"   Length: {len(api_key)} characters")
else:
    print("❌ API Key NOT found")
    print("\nChecked:")
    print(f"  - GOOGLE_AI_API_KEY: {os.getenv('GOOGLE_AI_API_KEY')}")
    print(f"  - GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')}")

# Test importing chatbot service
print("\n--- Testing ChatbotService ---")
try:
    from app.services.chatbot_service import chatbot_service
    service_token = chatbot_service.api_token
    if service_token:
        print(f"✅ ChatbotService.api_token: {service_token[:20]}...{service_token[-10:]}")
    else:
        print("❌ ChatbotService.api_token: NOT SET")
except Exception as e:
    print(f"❌ Error importing ChatbotService: {e}")
    import traceback
    traceback.print_exc()

# Test Flask app context
print("\n--- Testing Flask App Context ---")
try:
    from app import create_app
    app = create_app()
    with app.app_context():
        from app.services.chatbot_service import chatbot_service
        service_token = chatbot_service.api_token
        config_key = app.config.get('GOOGLE_AI_API_KEY')
        print(f"✅ Flask config GOOGLE_AI_API_KEY: {bool(config_key)}")
        if service_token:
            print(f"✅ ChatbotService.api_token (in app context): {service_token[:20]}...{service_token[-10:]}")
        else:
            print("❌ ChatbotService.api_token (in app context): NOT SET")
except Exception as e:
    print(f"❌ Error testing Flask app: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Done ---")

