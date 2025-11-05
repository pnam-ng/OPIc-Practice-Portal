# app/blueprints/admin.py
from flask import Blueprint, render_template, request, abort, jsonify, Response, url_for, redirect
from werkzeug.utils import secure_filename
import os
import time
from flask_login import login_required, current_user
from sqlalchemy import or_, desc, asc, func
from app import db
from app.models import User, Response as UserResponse, Survey, Tip
from app.utils.pdf_thumbnail import generate_pdf_thumbnail, get_thumbnail_path

admin_bp = Blueprint("admin", __name__, template_folder="../../templates/admin")

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