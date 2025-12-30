import sys
import os

# Add project root to python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app, db
from app.services import UserService

app = create_app()
with app.app_context():
    user_service = UserService()
    username = 'test_reg_fix_3' # Changed to avoid unique constraint if previous attempts failed silently
    email = 'test_fix_3@example.com'
    name = 'Test Fix'
    password = 'password123'
    
    print(f"Attempting to register user: {username}")
    try:
        # Check if user already exists and delete if so
        existing_user = user_service.get_user_by_username(username)
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
            print(f"Deleted existing user {username}")

        user = user_service.create_user(
            username=username,
            email=email,
            name=name,
            password=password
        )
        if user:
            print("✅ Successfully created user!")
            # Clean up
            db.session.delete(user)
            db.session.commit()
            print("✅ Cleaned up test user.")
        else:
            print("❌ Failed to create user (returned None).")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
