#!/usr/bin/env python3
"""
Utility script to reset the admin user's password to 'admin123'.
"""

from app import create_app, db
from app.models import User


def main():
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username='admin').first()
        if not user:
            print('NO_ADMIN_FOUND')
            return
        user.set_password('admin123')
        db.session.commit()
        print('RESET_OK')


if __name__ == '__main__':
    main()



