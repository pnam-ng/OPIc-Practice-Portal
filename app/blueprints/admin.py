# app/blueprints/admin.py
from flask import Blueprint, render_template, request, abort, jsonify, Response, url_for, redirect
from werkzeug.utils import secure_filename
import os
import time
from flask_login import login_required, current_user
from sqlalchemy import or_, desc, asc, func
from app import db
from app.models import User, Response as UserResponse, Survey, Tip, Question
from app.utils.pdf_thumbnail import generate_pdf_thumbnail, get_thumbnail_path

admin_bp = Blueprint("admin", __name__, template_folder="../../templates/admin")

QUESTION_TYPES = {'question', 'answer'}
QUESTION_SORT_COLUMNS = {
    'id': Question.id,
    'topic': Question.topic,
    'language': Question.language,
    'level': Question.difficulty_level,
    'type': Question.question_type,
    'updated': Question.updated_at,
}
MAX_QUESTIONS_PER_PAGE = 200

# --- simple admin-only gate ---
def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not getattr(current_user, "is_admin", False):
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

# Helpers: common query base with aggregates
def base_user_query():
    # aggregate: total responses per user
    resp_count = db.session.query(
        UserResponse.user_id, func.count(UserResponse.id).label("responses_count")
    ).group_by(UserResponse.user_id).subquery()

    # aggregate: surveys per user
    survey_count = db.session.query(
        Survey.user_id, func.count(Survey.id).label("surveys_count")
    ).group_by(Survey.user_id).subquery()

    return (
        db.session.query(
            User,
            func.coalesce(resp_count.c.responses_count, 0).label("responses_count"),
            func.coalesce(survey_count.c.surveys_count, 0).label("surveys_count"),
        )
        .outerjoin(resp_count, resp_count.c.user_id == User.id)
        .outerjoin(survey_count, survey_count.c.user_id == User.id)
    )

@admin_bp.route("/tips", methods=['GET', 'POST'])
@login_required
@admin_required
def tips():
    """Manage tips/resources"""
    if request.method == 'POST':
        # Handle CRUD operations
        if request.is_json:
            data = request.get_json()
            action = data.get('action')
            # Extract form data from JSON
            title = data.get('title', '').strip()
            description = data.get('description', '').strip()
            filename = data.get('filename', '').strip()
            category = data.get('category', 'Test Preparation').strip()
            display_order = int(data.get('display_order', 0))
            is_active = data.get('is_active', True)
            tip_id = data.get('id')
        else:
            action = request.form.get('action')
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            filename = request.form.get('filename', '').strip()
            category = request.form.get('category', 'Test Preparation').strip()
            display_order = int(request.form.get('display_order', 0))
            # Checkbox: handle both 'true'/'false' strings and HTML checkbox behavior
            # When checkbox is checked, it sends 'true', when unchecked it sends 'false' (via hidden input or JS)
            is_active_value = request.form.get('is_active')
            if is_active_value is None:
                is_active = False  # Checkbox not present, default to False
            elif isinstance(is_active_value, str):
                # Handle string values: 'true', 'false', 'on', 'off', '1', '0'
                is_active_value_lower = is_active_value.lower().strip()
                is_active = is_active_value_lower in ('true', 'on', '1', 'yes')
            else:
                # Handle boolean or other types
                is_active = bool(is_active_value)
            tip_id = request.form.get('id')
        
        if action == 'create':
            # Create new tip
            
            if not title:
                return jsonify({'success': False, 'error': 'Title is required'}), 400
            
            # Resolve files dir
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            files_dir = os.path.join(base_dir, 'files')
            os.makedirs(files_dir, exist_ok=True)
            
            # Support PDF upload or existing filename reference
            file_path = None
            uploaded_pdf = request.files.get('pdf_file')
            if uploaded_pdf and uploaded_pdf.filename:
                pdf_name = secure_filename(uploaded_pdf.filename)
                if not pdf_name.lower().endswith('.pdf'):
                    return jsonify({'success': False, 'error': 'Uploaded file must be a PDF'}), 400
                saved_name = f"tip_{int(time.time())}_{pdf_name}"
                file_path = os.path.join(files_dir, saved_name)
                uploaded_pdf.save(file_path)
                filename = saved_name
            else:
                if not filename:
                    return jsonify({'success': False, 'error': 'Provide a filename or upload a PDF'}), 400
                file_path = os.path.join(files_dir, filename)
                if not os.path.exists(file_path):
                    return jsonify({'success': False, 'error': f'File {filename} not found in files directory'}), 400
            
            # Check if tip with same filename already exists
            existing = Tip.query.filter_by(filename=filename).first()
            if existing:
                return jsonify({'success': False, 'error': 'A tip with this filename already exists'}), 400
            
            # Handle optional thumbnail upload
            thumbnail_path = None
            uploaded_thumb = request.files.get('thumbnail')
            if uploaded_thumb and uploaded_thumb.filename:
                # Save uploaded image into static/thumbnails
                thumb_dir = os.path.join(base_dir, 'static', 'thumbnails')
                os.makedirs(thumb_dir, exist_ok=True)
                name, ext = os.path.splitext(secure_filename(uploaded_thumb.filename))
                ext = ext.lower() or '.png'
                thumb_filename = f"tip_{int(time.time())}_{secure_filename(name)}{ext}"
                dest_path = os.path.join(thumb_dir, thumb_filename)
                uploaded_thumb.save(dest_path)
                # Store using forward slashes for static URLs
                thumbnail_path = f'static/thumbnails/{thumb_filename}'
            else:
                # Auto-generate from PDF first page if no upload provided
                try:
                    thumbnail_full_path = get_thumbnail_path(filename, base_dir)
                    if generate_pdf_thumbnail(file_path, thumbnail_full_path):
                        thumbnail_path = f"static/thumbnails/{os.path.basename(thumbnail_full_path)}"
                except Exception as e:
                    # Continue without thumbnail
                    print(f"Warning: Failed to generate thumbnail: {e}")
            
            tip = Tip(
                title=title,
                description=description,
                filename=filename,
                thumbnail_path=thumbnail_path,
                category=category,
                display_order=display_order,
                created_by=current_user.id
            )
            
            try:
                db.session.add(tip)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Tip created successfully', 'tip': tip.to_dict()})
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'error': str(e)}), 500
        
        elif action == 'update':
            # Update existing tip
            if not tip_id:
                return jsonify({'success': False, 'error': 'Tip ID is required'}), 400
            
            tip = Tip.query.get(tip_id)
            if not tip:
                return jsonify({'success': False, 'error': 'Tip not found'}), 404
            
            if title:
                tip.title = title
            if description is not None:
                tip.description = description
            if category:
                tip.category = category
            if display_order is not None:
                tip.display_order = display_order
            # Always update is_active since we handle the checkbox state properly
            tip.is_active = is_active
            
            # Update filename if provided or new PDF uploaded
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            files_dir = os.path.join(base_dir, 'files')
            os.makedirs(files_dir, exist_ok=True)
            uploaded_pdf = request.files.get('pdf_file')
            new_filename = filename if filename else tip.filename
            if uploaded_pdf and uploaded_pdf.filename:
                pdf_name = secure_filename(uploaded_pdf.filename)
                if not pdf_name.lower().endswith('.pdf'):
                    return jsonify({'success': False, 'error': 'Uploaded file must be a PDF'}), 400
                saved_name = f"tip_{int(time.time())}_{pdf_name}"
                file_path = os.path.join(files_dir, saved_name)
                uploaded_pdf.save(file_path)
                new_filename = saved_name
            
            if new_filename and new_filename != tip.filename:
                # Check if new file exists
                file_path = os.path.join(files_dir, new_filename)
                if not os.path.exists(file_path):
                    return jsonify({'success': False, 'error': f'File {new_filename} not found in files directory'}), 400
                
                # Generate new thumbnail for the new filename
                # If new thumbnail uploaded, prioritize it; otherwise regenerate from PDF
                uploaded_thumb = request.files.get('thumbnail')
                if uploaded_thumb and uploaded_thumb.filename:
                    thumb_dir = os.path.join(base_dir, 'static', 'thumbnails')
                    os.makedirs(thumb_dir, exist_ok=True)
                    name, ext = os.path.splitext(secure_filename(uploaded_thumb.filename))
                    ext = ext.lower() or '.png'
                    thumb_filename = f"tip_{int(time.time())}_{secure_filename(name)}{ext}"
                    dest_path = os.path.join(thumb_dir, thumb_filename)
                    uploaded_thumb.save(dest_path)
                    tip.thumbnail_path = f'static/thumbnails/{thumb_filename}'
                else:
                    try:
                        thumbnail_full_path = get_thumbnail_path(new_filename, base_dir)
                        if generate_pdf_thumbnail(file_path, thumbnail_full_path):
                            tip.thumbnail_path = f"static/thumbnails/{os.path.basename(thumbnail_full_path)}"
                    except Exception as e:
                        print(f"Warning: Failed to generate thumbnail for updated tip: {e}")
                
                tip.filename = new_filename
            
            # If a new thumbnail is uploaded even when filename didn't change, save it
            else:
                uploaded_thumb_direct = request.files.get('thumbnail')
                if uploaded_thumb_direct and uploaded_thumb_direct.filename:
                    thumb_dir = os.path.join(base_dir, 'static', 'thumbnails')
                    os.makedirs(thumb_dir, exist_ok=True)
                    name, ext = os.path.splitext(secure_filename(uploaded_thumb_direct.filename))
                    ext = ext.lower() or '.png'
                    thumb_filename = f"tip_{int(time.time())}_{secure_filename(name)}{ext}"
                    dest_path = os.path.join(thumb_dir, thumb_filename)
                    uploaded_thumb_direct.save(dest_path)
                    tip.thumbnail_path = f'static/thumbnails/{thumb_filename}'
            
            try:
                db.session.commit()
                return jsonify({'success': True, 'message': 'Tip updated successfully', 'tip': tip.to_dict()})
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'error': str(e)}), 500
        
        elif action == 'delete':
            # Delete tip
            if not tip_id:
                return jsonify({'success': False, 'error': 'Tip ID is required'}), 400
            
            tip = Tip.query.get(tip_id)
            if not tip:
                return jsonify({'success': False, 'error': 'Tip not found'}), 404
            
            try:
                db.session.delete(tip)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Tip deleted successfully'})
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'error': str(e)}), 500
    
    # GET: Show tips management page or return single tip
    tip_id = request.args.get('id')
    if tip_id:
        # Return single tip as JSON (for edit form)
        tip = Tip.query.get(tip_id)
        if tip:
            return jsonify({'success': True, 'tip': tip.to_dict()})
        else:
            return jsonify({'success': False, 'error': 'Tip not found'}), 404
    
    tips = Tip.query.order_by(Tip.display_order, Tip.created_at.desc()).all()
    return render_template('admin/tips.html', tips=tips)

@admin_bp.route("/tips/api", methods=['GET'])
@login_required
@admin_required
def tips_api():
    """API endpoint to get tips list"""
    tips = Tip.query.filter_by(is_active=True).order_by(Tip.display_order, Tip.created_at.desc()).all()
    return jsonify({'success': True, 'tips': [tip.to_dict() for tip in tips]})


def _get_question_request_data():
    """Return request payload regardless of content type"""
    if request.is_json:
        return request.get_json(silent=True) or {}
    if request.form:
        return request.form.to_dict(flat=True)
    return {}


def _clean_str(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def _prepare_question_payload(data, *, partial: bool = False):
    """Normalize and validate question payload"""
    payload = {}
    provided_keys = set(data.keys())

    def key_requested(field):
        return not partial or field in provided_keys

    if key_requested('topic'):
        topic = _clean_str(data.get('topic'))
        if not topic:
            return None, 'Topic is required.'
        payload['topic'] = topic

    if key_requested('language'):
        language = _clean_str(data.get('language')) or 'english'
        payload['language'] = language.lower()

    if key_requested('difficulty_level'):
        level = _clean_str(data.get('difficulty_level'))
        payload['difficulty_level'] = level.upper() if level else None

    if key_requested('question_type'):
        q_type = _clean_str(data.get('question_type')) or 'question'
        q_type = q_type.lower()
        if q_type not in QUESTION_TYPES:
            return None, f"Question type must be one of: {', '.join(sorted(QUESTION_TYPES))}."
        payload['question_type'] = q_type

    if key_requested('text'):
        payload['text'] = _clean_str(data.get('text'))

    if key_requested('audio_url'):
        payload['audio_url'] = _clean_str(data.get('audio_url'))

    if key_requested('sample_answer_text'):
        payload['sample_answer_text'] = _clean_str(data.get('sample_answer_text'))

    if key_requested('sample_answer_audio_url'):
        payload['sample_answer_audio_url'] = _clean_str(data.get('sample_answer_audio_url'))

    # Enforce that new questions always contain text or audio
    if not partial:
        text_val = payload.get('text')
        audio_val = payload.get('audio_url')
        if not text_val and not audio_val:
            return None, 'Provide question text or an audio URL.'

    return payload, None


def _apply_question_filters(query, filters):
    """Apply common filters for question listings"""
    language = filters.get('language')
    if language and language.lower() != 'all':
        query = query.filter(Question.language == language.lower())

    topic = filters.get('topic')
    if topic:
        query = query.filter(Question.topic == topic)

    level = filters.get('level')
    if level:
        query = query.filter(Question.difficulty_level == level)

    q_type = filters.get('question_type')
    if q_type in QUESTION_TYPES:
        query = query.filter(Question.question_type == q_type)

    search = filters.get('q')
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                Question.topic.ilike(like),
                Question.text.ilike(like),
                Question.sample_answer_text.ilike(like)
            )
        )

    return query


def _collect_question_filter_options(language_filter):
    """Gather dropdown values for the management UI"""
    language_rows = db.session.query(Question.language).filter(Question.language.isnot(None)).distinct().all()
    languages = sorted({row[0] for row in language_rows if row[0]})

    topic_query = db.session.query(Question.topic).filter(Question.topic.isnot(None))
    level_query = db.session.query(Question.difficulty_level).filter(Question.difficulty_level.isnot(None))

    if language_filter and language_filter.lower() != 'all':
        topic_query = topic_query.filter(Question.language == language_filter.lower())
        level_query = level_query.filter(Question.language == language_filter.lower())

    topics = sorted({row[0] for row in topic_query.distinct().all() if row[0]})
    levels = sorted({row[0] for row in level_query.distinct().all() if row[0]})

    return {
        'languages': languages,
        'topics': topics,
        'levels': levels,
        'question_types': sorted(QUESTION_TYPES),
    }


def _apply_question_sort(query, sort_key, sort_order):
    """Apply sorting to the question query"""
    column = QUESTION_SORT_COLUMNS.get(sort_key, Question.updated_at)
    sort_order = 'asc' if sort_order == 'asc' else 'desc'
    
    ordered_column = column.asc() if sort_order == 'asc' else column.desc()
    
    if sort_key == 'updated':
        ordered_column = ordered_column.nullslast()
        secondary = Question.created_at.asc() if sort_order == 'asc' else Question.created_at.desc()
        return query.order_by(ordered_column, secondary)
    
    return query.order_by(ordered_column)


@admin_bp.route("/questions", methods=['GET'])
@login_required
@admin_required
def manage_questions():
    """Render the question management console"""
    filters = {
        'q': request.args.get('q', '').strip(),
        'topic': request.args.get('topic', '').strip(),
        'language': request.args.get('language', 'english').strip().lower() or 'english',
        'level': request.args.get('level', '').strip().upper(),
        'question_type': request.args.get('question_type', '').strip().lower(),
    }
    
    sort_key = (request.args.get('sort', 'updated') or 'updated').lower()
    if sort_key not in QUESTION_SORT_COLUMNS:
        sort_key = 'updated'
    
    sort_order = (request.args.get('order', 'desc') or 'desc').lower()
    if sort_order not in ('asc', 'desc'):
        sort_order = 'desc'

    try:
        page = max(int(request.args.get('page', 1)), 1)
    except (TypeError, ValueError):
        page = 1

    try:
        per_page = int(request.args.get('per_page', 50))
    except (TypeError, ValueError):
        per_page = 50

    per_page = max(10, min(per_page, MAX_QUESTIONS_PER_PAGE))

    query = _apply_question_filters(Question.query, filters)
    query = _apply_question_sort(query, sort_key, sort_order)
    total = query.count()
    questions = (
        query.offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    filter_options = _collect_question_filter_options(filters['language'])
    filter_options['languages'].insert(0, 'all')

    pages = (total + per_page - 1) // per_page

    base_sort_args = request.args.to_dict()
    
    def page_url(p):
        args = request.args.to_dict()
        args['page'] = p
        args['per_page'] = per_page
        return url_for('admin.manage_questions', **args)
    
    def build_sort_link(field):
        args = base_sort_args.copy()
        args.pop('page', None)
        args['sort'] = field
        if sort_key == field and sort_order == 'asc':
            args['order'] = 'desc'
        elif sort_key == field and sort_order == 'desc':
            args['order'] = 'asc'
        else:
            args['order'] = 'asc'
        return url_for('admin.manage_questions', **args)
    
    sort_controls = {field: build_sort_link(field) for field in QUESTION_SORT_COLUMNS.keys()}

    return render_template(
        "admin/questions.html",
        questions=questions,
        filters=filters,
        pagination={
            'page': page,
            'per_page': per_page,
            'pages': pages,
            'total': total,
        },
        filter_options=filter_options,
        stats={
            'total_questions': Question.query.count(),
            'showing': len(questions),
        },
        page_url=page_url,
        sort={
            'key': sort_key,
            'order': sort_order,
        },
        sort_controls=sort_controls,
        request_args=base_sort_args,
    )


@admin_bp.route("/questions/api", methods=['GET', 'POST'])
@login_required
@admin_required
def questions_api():
    """JSON API for question management"""
    if request.method == 'GET':
        filters = {
            'q': request.args.get('q', '').strip(),
            'topic': request.args.get('topic', '').strip(),
            'language': request.args.get('language', 'all').strip().lower(),
            'level': request.args.get('level', '').strip().upper(),
            'question_type': request.args.get('question_type', '').strip().lower(),
        }
        
        sort_key = (request.args.get('sort', 'updated') or 'updated').lower()
        if sort_key not in QUESTION_SORT_COLUMNS:
            sort_key = 'updated'
        
        sort_order = (request.args.get('order', 'desc') or 'desc').lower()
        if sort_order not in ('asc', 'desc'):
            sort_order = 'desc'

        try:
            page = max(int(request.args.get('page', 1)), 1)
        except (TypeError, ValueError):
            page = 1

        try:
            per_page = int(request.args.get('per_page', 50))
        except (TypeError, ValueError):
            per_page = 50

        per_page = max(10, min(per_page, MAX_QUESTIONS_PER_PAGE))

        query = _apply_question_filters(Question.query, filters)
        query = _apply_question_sort(query, sort_key, sort_order)
        total = query.count()
        questions = (
            query.offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return jsonify({
            'success': True,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page,
                'total': total,
            },
            'filters': filters,
            'sort': {
                'key': sort_key,
                'order': sort_order,
            },
            'questions': [question.to_dict() for question in questions],
        })

    # POST: create new question
    data = _get_question_request_data()
    payload, error = _prepare_question_payload(data)
    if error:
        return jsonify({'success': False, 'error': error}), 400

    try:
        question = Question(**payload)
        db.session.add(question)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Question created successfully.',
            'question': question.to_dict(),
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route("/questions/api/<int:question_id>", methods=['GET', 'PUT', 'DELETE'])
@login_required
@admin_required
def question_detail_api(question_id):
    """Retrieve, update, or delete a question"""
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'success': False, 'error': 'Question not found'}), 404

    if request.method == 'GET':
        return jsonify({'success': True, 'question': question.to_dict()})

    if request.method == 'DELETE':
        try:
            db.session.delete(question)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Question deleted successfully.'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    # PUT
    data = _get_question_request_data()
    payload, error = _prepare_question_payload(data, partial=False)
    if error:
        return jsonify({'success': False, 'error': error}), 400

    for field, value in payload.items():
        setattr(question, field, value)

    if not (question.text or question.audio_url):
        return jsonify({'success': False, 'error': 'Question must contain text or audio.'}), 400

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Question updated successfully.',
            'question': question.to_dict(),
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route("/questions/<int:question_id>/generate-audio", methods=['POST'])
@login_required
@admin_required
def generate_question_audio(question_id):
    """Generate TTS audio for a question"""
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


    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route("/questions/import", methods=['POST'])
@login_required
@admin_required
def import_questions():
    """Bulk import questions from CSV/Excel"""
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


@admin_bp.route("/questions/template")
@login_required
@admin_required
def get_import_template():
    """Download CSV template for bulk import"""
    csv_content = "topic,text,level,language,type\nExample Topic,This is an example question text.,IM,english,question"
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=questions_template.csv"}
    )


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    # --- filters ---
    q = request.args.get("q", "").strip()
    lang = request.args.get("lang", "").strip()
    sort = request.args.get("sort", "created_at")  # username|email|created_at|responses
    order = request.args.get("order", "desc")      # asc|desc
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 20)), 5), 100)

    qry = base_user_query()

    if q:
        like = f"%{q}%"
        qry = qry.filter(or_(User.username.ilike(like), User.email.ilike(like), User.name.ilike(like)))

    if lang:
        qry = qry.filter(User.target_language == lang)

    # sorting
    sort_col = {
        "username": User.username,
        "email": User.email,
        "responses": "responses_count",
        "created_at": User.created_at,
    }.get(sort, User.created_at)

    if sort == "responses":
        qry = qry.order_by(desc("responses_count") if order == "desc" else asc("responses_count"))
    else:
        qry = qry.order_by(desc(sort_col) if order == "desc" else asc(sort_col))

    # pagination
    total = qry.count()
    rows = qry.offset((page - 1) * per_page).limit(per_page).all()

    # build a lightweight view model
    users_vm = []
    for u, responses_count, surveys_count in rows:
        users_vm.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "name": u.name,
            "target_language": u.target_language,
            "streak_count": u.streak_count,
            "last_active_date": u.last_active_date,
            "is_admin": u.is_admin,
            "created_at": u.created_at,
            "responses_count": responses_count,
            "surveys_count": surveys_count,
        })

    # page URLs
    def page_url(p):
        args = request.args.to_dict()
        args["page"] = p
        return url_for("admin.users", **args)

    return render_template(
        "admin/user_list.html",
        users=users_vm,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
        page_url=page_url,
        q=q,
        lang=lang,
        sort=sort,
        order=order,
    )

# --- CSV export ---
@admin_bp.route("/users.csv")
@login_required
@admin_required
def users_csv():
    qry = base_user_query()
    q = request.args.get("q", "").strip()
    lang = request.args.get("lang", "").strip()
    if q:
        like = f"%{q}%"
        qry = qry.filter(or_(User.username.ilike(like), User.email.ilike(like), User.name.ilike(like)))
    if lang:
        qry = qry.filter(User.target_language == lang)

    def generate():
        yield "id,username,email,name,target_language,is_admin,streak_count,responses_count,surveys_count,created_at,last_active_date\n"
        for u, responses_count, surveys_count in qry.order_by(desc(User.created_at)).all():
            row = [
                str(u.id), u.username, u.email.replace(",", " "),
                (u.name or "").replace(",", " "),
                (u.target_language or ""), str(int(bool(u.is_admin))),
                str(u.streak_count or 0),
                str(responses_count or 0),
                str(surveys_count or 0),
                (u.created_at.isoformat() if u.created_at else ""),
                (u.last_active_date.isoformat() if u.last_active_date else "")
            ]
            yield ",".join(row) + "\n"

    return Response(generate(), mimetype="text/csv")

# --- JSON API (for future admin UI or AJAX tables) ---
@admin_bp.route("/api/users")
@login_required
@admin_required
def users_api():
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 20)), 5), 100)
    qry = base_user_query()
    total = qry.count()
    rows = qry.offset((page - 1) * per_page).limit(per_page).all()
    data = []
    for u, responses_count, surveys_count in rows:
        data.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "name": u.name,
            "target_language": u.target_language,
            "is_admin": u.is_admin,
            "streak_count": u.streak_count,
            "responses_count": responses_count,
            "surveys_count": surveys_count,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "last_active_date": u.last_active_date.isoformat() if u.last_active_date else None,
        })