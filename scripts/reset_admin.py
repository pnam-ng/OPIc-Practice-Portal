#!/usr/bin/env python3
"""
Utility script to reset the admin user's password.
Password should be provided via environment variable or prompt.
"""

import os
import getpass
from app import create_app, db
from app.models import User


def main():
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username='admin').first()
        if not user:
            print('NO_ADMIN_FOUND')
            return
        
        # Get password from environment or prompt
        password = os.environ.get('ADMIN_PASSWORD')
        if not password:
            password = getpass.getpass('Enter new admin password (min 6 characters): ')
            if len(password) < 6:
                print('Error: Password must be at least 6 characters long.')
                return
            confirm = getpass.getpass('Confirm password: ')
            if password != confirm:
                print('Error: Passwords do not match.')
                return
        
        user.set_password(password)
        db.session.commit()
        print('RESET_OK')


if __name__ == '__main__':
    main()



