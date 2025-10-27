#!/usr/bin/env python3
"""Ensure an admin user exists with username=admin and password=1qaz2wsx."""
from app import create_app, db
from app.models import User


def main() -> None:
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username='admin').first()
        if user is None:
            user = User(
                username='admin',
                email='admin@opic-portal.com',
                name='Administrator',
                target_language='english',
                is_admin=True,
            )
            user.set_password('1qaz2wsx')
            db.session.add(user)
            db.session.commit()
            print('CREATED')
        else:
            user.set_password('1qaz2wsx')
            db.session.commit()
            print('RESET')


if __name__ == '__main__':
    main()





