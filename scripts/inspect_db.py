from app import create_app, db
from app.models import User


def main():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        print(f"Total users: {len(users)}")
        for u in users:
            print(f"- id={u.id} username={u.username} email={u.email} is_admin={u.is_admin}")


if __name__ == '__main__':
    main()





