from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Comment, CommentLike, Question, User
from datetime import datetime
import os
import time
from werkzeug.utils import secure_filename

comments_bp = Blueprint('comments', __name__, url_prefix='/api/comments')

# Import notification helper
from app.blueprints.notifications import create_mention_notifications


@comments_bp.route('/question/<int:question_id>', methods=['GET'])
@login_required
def get_comments(question_id):
    """Get all comments for a question"""
    try:
        sort_by = request.args.get('sort', 'recent')  # 'recent' or 'popular'
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 10))
        
        # Base query for top-level comments (no parent)
        query = Comment.query.filter_by(question_id=question_id, parent_id=None)
        
        # Sort (pinned comments always appear first)
        if sort_by == 'popular':
            query = query.order_by(Comment.is_pinned.desc(), Comment.likes_count.desc(), Comment.created_at.desc())
        else:  # recent
            query = query.order_by(Comment.is_pinned.desc(), Comment.created_at.desc())
        
        # Paginate
        total = query.count()
        comments = query.offset(offset).limit(limit).all()
        
        # Convert to dict and include replies
        comments_data = []
        for comment in comments:
            comment_dict = comment.to_dict(current_user_id=current_user.id)
            
            # Get replies for this comment
            replies = Comment.query.filter_by(parent_id=comment.id).order_by(Comment.created_at.asc()).all()
            comment_dict['replies'] = [reply.to_dict(current_user_id=current_user.id) for reply in replies]
            
            comments_data.append(comment_dict)
        
        return jsonify({
            'success': True,
            'comments': comments_data,
            'total': total,
            'has_more': (offset + limit) < total
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@comments_bp.route('/question/<int:question_id>', methods=['POST'])
@login_required
def post_comment(question_id):
    """Post a new comment with optional audio file"""
    try:
        # Support both JSON (old) and form-data (new with file upload)
        if request.is_json:
            data = request.get_json()
            content = data.get('content', '').strip()
            audio_file = None
        else:
            # Form data with file upload
            content = request.form.get('content', '').strip()
            audio_file = request.files.get('audio')
        
        if not content:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        # Validate content length
        if len(content) > 2200:
            return jsonify({'success': False, 'error': 'Comment is too long (max 2200 characters)'}), 400
        
        # Verify question exists
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'success': False, 'error': 'Question not found'}), 404
        
        # Handle audio file upload
        audio_url = None
        if audio_file and audio_file.filename:
            # Validate file type
            allowed_extensions = {'.webm', '.mp3', '.wav', '.ogg', '.m4a'}
            file_ext = os.path.splitext(audio_file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                return jsonify({'success': False, 'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400
            
            # Save audio file
            filename = secure_filename(f"comment_{current_user.id}_{question_id}_{int(time.time())}{file_ext}")
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'comments', filename)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            audio_file.save(upload_path)
            audio_url = f"uploads/comments/{filename}"
        
        # Create comment (supports UTF-8, emojis, special characters)
        comment = Comment(
            question_id=question_id,
            user_id=current_user.id,
            content=content,
            audio_url=audio_url
        )
        
        db.session.add(comment)
        db.session.commit()
        
        # Create notifications for mentions
        create_mention_notifications(comment, content)
        
        return jsonify({
            'success': True,
            'comment': comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error posting comment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@comments_bp.route('/<int:comment_id>/reply', methods=['POST'])
@login_required
def post_reply(comment_id):
    """Post a reply to a comment with optional audio file"""
    try:
        # Support both JSON (old) and form-data (new with file upload)
        if request.is_json:
            data = request.get_json()
            content = data.get('content', '').strip()
            audio_file = None
        else:
            # Form data with file upload
            content = request.form.get('content', '').strip()
            audio_file = request.files.get('audio')
        
        if not content:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        # Validate content length
        if len(content) > 2200:
            return jsonify({'success': False, 'error': 'Reply is too long (max 2200 characters)'}), 400
        
        # Verify parent comment exists
        parent_comment = Comment.query.get(comment_id)
        if not parent_comment:
            return jsonify({'success': False, 'error': 'Parent comment not found'}), 404
        
        # Handle audio file upload
        audio_url = None
        if audio_file and audio_file.filename:
            # Validate file type
            allowed_extensions = {'.webm', '.mp3', '.wav', '.ogg', '.m4a'}
            file_ext = os.path.splitext(audio_file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                return jsonify({'success': False, 'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400
            
            # Save audio file
            filename = secure_filename(f"reply_{current_user.id}_{comment_id}_{int(time.time())}{file_ext}")
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'comments', filename)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            audio_file.save(upload_path)
            audio_url = f"uploads/comments/{filename}"
        
        # Create reply (supports UTF-8, emojis, special characters)
        reply = Comment(
            question_id=parent_comment.question_id,
            user_id=current_user.id,
            parent_id=comment_id,
            content=content,
            audio_url=audio_url
        )
        
        db.session.add(reply)
        
        # Update parent's replies count
        parent_comment.replies_count += 1
        
        db.session.commit()
        
        # Create notifications for mentions
        create_mention_notifications(reply, content)
        
        # Create notification for the parent comment author (if not replying to self)
        if parent_comment.user_id != current_user.id:
            from app.models import Notification
            notification = Notification(
                user_id=parent_comment.user_id,
                actor_id=current_user.id,
                type='reply',
                comment_id=reply.id,
                question_id=reply.question_id
            )
            db.session.add(notification)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'comment': reply.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error posting reply: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@comments_bp.route('/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment(comment_id):
    """Like or unlike a comment"""
    try:
        from app.models import Notification
        
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'success': False, 'error': 'Comment not found'}), 404
        
        # Check if already liked
        existing_like = CommentLike.query.filter_by(
            comment_id=comment_id,
            user_id=current_user.id
        ).first()
        
        if existing_like:
            # Unlike
            db.session.delete(existing_like)
            comment.likes_count = max(0, comment.likes_count - 1)
            action = 'unliked'
            
            # Delete like notification
            Notification.query.filter_by(
                comment_id=comment_id,
                actor_id=current_user.id,
                type='like'
            ).delete()
        else:
            # Like
            like = CommentLike(
                comment_id=comment_id,
                user_id=current_user.id
            )
            db.session.add(like)
            comment.likes_count += 1
            action = 'liked'
            
            # Create notification (don't notify if user likes own comment)
            if comment.user_id != current_user.id:
                notification = Notification(
                    user_id=comment.user_id,
                    actor_id=current_user.id,
                    type='like',
                    comment_id=comment_id,
                    question_id=comment.question_id
                )
                db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'action': action,
            'likes_count': comment.likes_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@comments_bp.route('/<int:comment_id>', methods=['PUT'])
@login_required
def edit_comment(comment_id):
    """Edit a comment"""
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'success': False, 'error': 'Comment not found'}), 404
        
        # Check ownership
        if comment.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        comment.content = content
        comment.is_edited = True
        comment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'comment': comment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """Delete a comment"""
    try:
        from app.models import Notification
        
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'success': False, 'error': 'Comment not found'}), 404
        
        # Check ownership or admin
        if comment.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Delete related notifications first
        Notification.query.filter_by(comment_id=comment_id).delete()
        
        # If it's a reply, update parent's replies count
        if comment.parent_id:
            parent = Comment.query.get(comment.parent_id)
            if parent:
                parent.replies_count = max(0, parent.replies_count - 1)
        
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@comments_bp.route('/<int:comment_id>/pin', methods=['POST'])
@login_required
def toggle_pin(comment_id):
    """Pin or unpin a comment (admin only)"""
    try:
        if not current_user.is_admin:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'success': False, 'error': 'Comment not found'}), 404
        
        comment.is_pinned = not comment.is_pinned
        db.session.commit()
        
        action = 'pinned' if comment.is_pinned else 'unpinned'
        
        return jsonify({
            'success': True,
            'is_pinned': comment.is_pinned,
            'action': action
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


