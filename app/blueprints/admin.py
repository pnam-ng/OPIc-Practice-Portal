# app/blueprints/admin.py
from flask import Blueprint, render_template, request, abort, jsonify, Response, url_for, redirect
from flask_login import login_required, current_user
from sqlalchemy import or_, desc, asc, func
from app import db
from app.models import User, Response as UserResponse, Survey

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