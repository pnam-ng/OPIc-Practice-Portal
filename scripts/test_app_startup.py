"""
Test Application Startup
Tests if the Flask app can start without errors after migration
"""
import os
import sys

# Ensure the application package is importable
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

def test_app_startup():
    """Test if the app can start successfully"""
    print("=" * 60)
    print("TESTING APPLICATION STARTUP")
    print("=" * 60)
    print()
    
    try:
        print("[1] Importing Flask app...")
        from app import create_app, db
        print("    ✓ Import successful")
        print()
        
        print("[2] Creating app instance...")
        app = create_app()
        print("    ✓ App created successfully")
        print()
        
        print("[3] Testing database connection...")
        with app.app_context():
            from sqlalchemy import text
            result = db.session.execute(text("SELECT 1"))
            result.scalar()
            print("    ✓ Database connection OK")
        print()
        
        print("[4] Testing Question model...")
        with app.app_context():
            from app.models import Question
            questions = Question.query.limit(1).all()
            if questions:
                q = questions[0]
                print(f"    ✓ Question model OK")
                print(f"    Sample: ID={q.id}, Topic={q.topic}, Level={q.difficulty_level}")
            else:
                print("    ⚠️  No questions found in database")
        print()
        
        print("[5] Testing User model...")
        with app.app_context():
            from app.models import User
            users = User.query.limit(1).all()
            if users:
                u = users[0]
                print(f"    ✓ User model OK")
                print(f"    Sample: ID={u.id}, Username={u.username}")
            else:
                print("    ⚠️  No users found in database")
        print()
        
        print("[6] Testing Response model...")
        with app.app_context():
            from app.models import Response
            responses = Response.query.limit(1).all()
            if responses:
                r = responses[0]
                print(f"    ✓ Response model OK")
                print(f"    Sample: ID={r.id}, User={r.user_id}, Question={r.question_id}")
            else:
                print("    ⚠️  No responses found in database")
        print()
        
        print("[7] Testing routes registration...")
        with app.app_context():
            routes = []
            for rule in app.url_map.iter_rules():
                if rule.endpoint not in ['static']:
                    routes.append(str(rule))
            print(f"    ✓ {len(routes)} routes registered")
            print(f"    Sample routes:")
            for route in routes[:5]:
                print(f"    - {route}")
        print()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED - APP SHOULD START SUCCESSFULLY")
        print("=" * 60)
        print()
        print("If you're still getting 500 errors, check:")
        print("1. Application logs (gunicorn/flask logs)")
        print("2. Make sure to restart the application after migration")
        print("3. Check file permissions on database file")
        
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ TEST FAILED")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        print("Full traceback:")
        import traceback
        traceback.print_exc()
        print()
        sys.exit(1)

if __name__ == "__main__":
    test_app_startup()
