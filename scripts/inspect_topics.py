from app import create_app
from app.services import QuestionService


def main() -> None:
    app = create_app()
    with app.app_context():
        qs = QuestionService()
        topics = qs.get_all_topics('english')
        count = qs.get_all_questions_count()
        print('questions_count=', count)
        print('topics_english=', topics)


if __name__ == '__main__':
    main()





