#!/usr/bin/env python3
"""Ensure an admin user exists. Password should be set via environment variable or prompt."""
import os
import getpass
from app import create_app, db
from app.models import User


def main() -> None:
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username='admin').first()
        
        # Get password from environment or prompt
        password = os.environ.get('ADMIN_PASSWORD')
        if not password:
            password = getpass.getpass('Enter admin password (min 6 characters): ')
            if len(password) < 6:
                print('Error: Password must be at least 6 characters long.')
                return
        
        if user is None:
            user = User(
                username='admin',
                email='admin@opic-portal.com',
                name='Administrator',
                target_language='english',
                is_admin=True,
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print('CREATED')
        else:
            user.set_password(password)
            db.session.commit()
            print('RESET')


if __name__ == '__main__':
    main()





