from flask import Blueprint, render_template, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Question, User, Response
from app.services.question_service import QuestionService
from sqlalchemy import desc
import os
import time
from werkzeug.utils import secure_filename
from flask import Response

questions_bp = Blueprint('questions', __name__)

@questions_bp.record
def record_services(setup_state):
    """Initialize services when blueprint is registered"""
    app = setup_state.app
    questions_bp.question_service = QuestionService(db)

def get_service():
    """Get question service instance"""
    if not hasattr(questions_bp, 'question_service'):
        questions_bp.question_service = QuestionService(db)
    return questions_bp.question_service

@questions_bp.route('/')
@login_required
def index():
    """
    List all questions with filtering and sorting
    Accessible by all logged-in users
    """
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filters
    topic = request.args.get('topic')
    level = request.args.get('level')
    search = request.args.get('search')
    
    # Sorting
    sort_key = request.args.get('sort', 'updated')
    sort_order = request.args.get('order', 'desc')
    
    # Base query
    query = Question.query
    
    # Apply filters
    if topic:
        query = query.filter(Question.topic == topic)
    if level:
        query = query.filter(Question.difficulty_level == level)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Question.text.ilike(search_term)) | 
            (Question.topic.ilike(search_term))
        )
        
    # Apply sorting
    sort_map = {
        'id': Question.id,
        'topic': Question.topic,
        'language': Question.language,
        'level': Question.difficulty_level,
        'type': Question.question_type,
        'updated': Question.updated_at,
        'created_at': Question.created_at
    }
    
    sort_col = sort_map.get(sort_key, Question.updated_at)
    
    if sort_order == 'desc':
        query = query.order_by(desc(sort_col))
    else:
        query = query.order_by(sort_col)
        
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    questions = pagination.items
    
    # Get unique topics for filter dropdown
    topics = db.session.query(Question.topic).distinct().order_by(Question.topic).all()
    topics = [t[0] for t in topics if t[0]]
    
    # Build sort controls
    current_args = {
        'topic': topic,
        'level': level,
        'search': search
    }
    # Clean None values
    current_args = {k: v for k, v in current_args.items() if v is not None}
    
    def toggle_order(key):
        return 'asc' if sort_key == key and sort_order == 'desc' else 'desc'
        
    sort_controls = {
        key: url_for('questions.index', sort=key, order=toggle_order(key), **current_args)
        for key in ['id', 'topic', 'language', 'level', 'type', 'updated']
    }
    
    # Helper for pagination URLs
    def page_url(p):
        args = request.args.copy()
        args['page'] = p
        return url_for('questions.index', **args)
        
    filter_options = {
        'levels': ['IM', 'IH', 'AL'],
        'question_types': ['question', 'answer']
    }
        
    return render_template('questions/index.html', 
                         questions=questions, 
                         pagination=pagination,
                         topics=topics,
                         current_filters=current_args,
                         filters=current_args,
                         sort={'key': sort_key, 'order': sort_order},
                         sort_controls=sort_controls,
                         page_url=page_url,
                         filter_options=filter_options,
                         is_admin=current_user.is_admin)

@questions_bp.route('/api', methods=['GET', 'POST'])
@login_required
def questions_api():
    """API endpoint for creating questions"""
    service = get_service()
    
    if request.method == 'POST':
        # Only admins can create questions
        if not current_user.is_admin:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
        data = request.get_json()
        result = service.create_question(data)
        return jsonify(result)
        
    # GET not strictly needed here as index handles it, but kept for API consistency if needed
    return jsonify({'success': False, 'error': 'Method not allowed'}), 405

@questions_bp.route('/api/<int:question_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def question_detail_api(question_id):
    """API endpoint for managing specific questions"""
    service = get_service()
    
    # READ - Available to all users
    if request.method == 'GET':
        question = service.get_question(question_id)
        if not question:
            return jsonify({'success': False, 'error': 'Question not found'}), 404
        return jsonify({'success': True, 'question': question.to_dict()})
    
    # WRITE/DELETE - Admin only
    if not current_user.is_admin:
         return jsonify({'success': False, 'error': 'Unauthorized'}), 403
         
    if request.method == 'PUT':
        data = request.get_json()
        result = service.update_question(question_id, data)
        return jsonify(result)
        
    elif request.method == 'DELETE':
        result = service.delete_question(question_id)
        return jsonify(result)

@questions_bp.route('/import', methods=['POST'])
@login_required
def import_questions():
    """Bulk import questions from CSV/Excel"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
        
    auto_generate_audio = request.form.get('auto_generate_audio') == 'true'
    
    try:
        import pandas as pd
        from app.services.tts_service import TTSService
        
        # Determine file type
        filename = secure_filename(file.filename)
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        else:
            return jsonify({'success': False, 'error': 'Invalid file type. Use CSV or Excel.'}), 400
            
        # Validate columns
        required_cols = ['topic', 'text']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return jsonify({'success': False, 'error': f'Missing required columns: {", ".join(missing_cols)}'}), 400
            
        # Initialize TTS if needed
        tts_service = None
        if auto_generate_audio:
            tts_service = TTSService()
            
        success_count = 0
        errors = []
        
        # Process rows
        for index, row in df.iterrows():
            try:
                # Basic data
                topic = str(row['topic']).strip()
                text = str(row['text']).strip()
                
                if not topic or not text:
                    continue
                    
                # Optional fields with defaults
                language = str(row.get('language', 'english')).strip().lower()
                level = str(row.get('level', '')).strip().upper() or None
                q_type = str(row.get('type', 'question')).strip().lower()
                
                question = Question(
                    topic=topic,
                    text=text,
                    language=language,
                    difficulty_level=level,
                    question_type=q_type,
                    created_by=current_user.id
                )
                
                # Auto-generate Audio
                if auto_generate_audio and tts_service:
                    # Generate filename
                    filename = f"question_import_{int(time.time())}_{index}.mp3"
                    
                    # Resolve paths
                    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    upload_dir = os.path.join(base_dir, 'uploads', 'questions')
                    os.makedirs(upload_dir, exist_ok=True)
                    output_path = os.path.join(upload_dir, filename)
                    audio_url = f"/uploads/questions/{filename}"
                    
                    if tts_service.generate_audio(text, output_path, voice_key='ava'):
                        question.audio_url = audio_url
                
                db.session.add(question)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
                
        if success_count > 0:
            db.session.commit()
            
        return jsonify({
            'success': True,
            'message': f'Successfully imported {success_count} questions.',
            'errors': errors[:10]  # Limit error details
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f"Import failed: {str(e)}"}), 500


@questions_bp.route("/template")
@login_required
def get_import_template():
    """Download CSV template for bulk import"""
    csv_content = "topic,text,level,language,type\nExample Topic,This is an example question text.,IM,english,question"
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=questions_template.csv"}
    )


@questions_bp.route("/generate-audio-preview", methods=['POST'])
@login_required
def generate_audio_preview():
    """Generate TTS audio preview for new questions"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    data = request.get_json()
    text = data.get('text')

    if not text:
        return jsonify({'success': False, 'error': 'Text is required'}), 400

    from app.services.tts_service import TTSService
    tts_service = TTSService()
    
    # Use temporary filename or hash
    filename = f"preview_{int(time.time())}_{secure_filename(text[:20])}.mp3"
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    upload_dir = os.path.join(base_dir, 'uploads', 'questions')
    os.makedirs(upload_dir, exist_ok=True)
    
    output_path = os.path.join(upload_dir, filename)
    audio_url = f"/uploads/questions/{filename}"
    
    try:
        if tts_service.generate_audio(text, output_path, voice_key='ava'):
            return jsonify({'success': True, 'audio_url': audio_url})
        else:
            return jsonify({'success': False, 'error': 'Failed to generate audio'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@questions_bp.route("/<int:question_id>/generate-audio", methods=['POST'])
@login_required
def generate_question_audio(question_id):
    """Generate TTS audio for a question"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    question = Question.query.get(question_id)
    if not question:
        return jsonify({'success': False, 'error': 'Question not found'}), 404
        
    if not question.text:
        return jsonify({'success': False, 'error': 'Question has no text content'}), 400
        
    try:
        from app.services.tts_service import TTSService
        tts_service = TTSService()
        
        # Generate filename
        filename = f"question_{question.id}_{int(time.time())}.mp3"
        
        # Resolve paths
        # Use absolute path for saving file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        upload_dir = os.path.join(base_dir, 'uploads', 'questions')
        os.makedirs(upload_dir, exist_ok=True)
        output_path = os.path.join(upload_dir, filename)
        
        # URL path for database (relative to root)
        audio_url = f"/uploads/questions/{filename}"
        
        # Generate audio
        success = tts_service.generate_audio(question.text, output_path, voice_key='ava')
        
        if success:
            # Update question
            question.audio_url = audio_url
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': 'Audio generated successfully',
                'audio_url': audio_url
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to generate audio file'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
