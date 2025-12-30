from app.models import Question
from sqlalchemy.exc import SQLAlchemyError

class QuestionService:
    def __init__(self, db):
        self.db = db

    def get_question(self, question_id):
        """Get a question by ID"""
        return Question.query.get(question_id)

    def create_question(self, data):
        """Create a new question"""
        try:
            question = Question(
                topic=data.get('topic'),
                text=data.get('text'),
                language=data.get('language', 'english').lower(),
                difficulty_level=data.get('difficulty_level'),
                question_type=data.get('question_type', 'question'),
                audio_url=data.get('audio_url'),
                sample_answer_text=data.get('sample_answer_text'),
                sample_answer_audio_url=data.get('sample_answer_audio_url')
            )
            self.db.session.add(question)
            self.db.session.commit()
            return {'success': True, 'question': question.to_dict()}
        except SQLAlchemyError as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}

    def update_question(self, question_id, data):
        """Update an existing question"""
        try:
            question = self.get_question(question_id)
            if not question:
                return {'success': False, 'error': 'Question not found'}

            if 'topic' in data:
                question.topic = data['topic']
            if 'text' in data:
                question.text = data['text']
            if 'language' in data:
                question.language = data['language'].lower()
            if 'difficulty_level' in data:
                question.difficulty_level = data['difficulty_level']
            if 'question_type' in data:
                question.question_type = data['question_type']
            if 'audio_url' in data:
                question.audio_url = data['audio_url']
            if 'sample_answer_text' in data:
                question.sample_answer_text = data['sample_answer_text']
            if 'sample_answer_audio_url' in data:
                question.sample_answer_audio_url = data['sample_answer_audio_url']

            self.db.session.commit()
            return {'success': True, 'question': question.to_dict()}
        except SQLAlchemyError as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}

    def delete_question(self, question_id):
        """Delete a question"""
        try:
            question = self.get_question(question_id)
            if not question:
                return {'success': False, 'error': 'Question not found'}

            self.db.session.delete(question)
            self.db.session.commit()
            return {'success': True, 'message': 'Question deleted'}
        except SQLAlchemyError as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}
