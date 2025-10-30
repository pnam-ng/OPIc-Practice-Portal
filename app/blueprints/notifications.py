from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Notification
import re

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')


@notifications_bp.route('/', methods=['GET'])
@login_required
def get_notifications():
    """Get all notifications for the current user"""
    try:
        from datetime import datetime, timedelta
        
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        read_only = request.args.get('read_only', 'false').lower() == 'true'
        
        print(f"[Notifications API] User {current_user.id} ({current_user.username}) requesting notifications (offset={offset}, limit={limit}, unread_only={unread_only}, read_only={read_only})")
        
        # Auto-delete notifications older than 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        deleted_count = Notification.query.filter(
            Notification.user_id == current_user.id,
            Notification.created_at < thirty_days_ago
        ).delete()
        if deleted_count > 0:
            db.session.commit()
            print(f"[Notifications API] Deleted {deleted_count} old notifications (>30 days)")
        
        # Base query
        query = Notification.query.filter_by(user_id=current_user.id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        elif read_only:
            query = query.filter_by(is_read=True)
        
        # Order by most recent first
        query = query.order_by(Notification.created_at.desc())
        
        # Get total count
        total = query.count()
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        
        # Paginate
        notifications = query.offset(offset).limit(limit).all()
        
        print(f"[Notifications API] Found {len(notifications)} notifications, {unread_count} unread, {total} total")
        
        return jsonify({
            'success': True,
            'notifications': [n.to_dict() for n in notifications],
            'total': total,
            'unread_count': unread_count,
            'has_more': (offset + limit) < total
        }), 200
        
    except Exception as e:
        print(f"[Notifications API] Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_as_read(notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return jsonify({'success': False, 'error': 'Notification not found'}), 404
        
        if notification.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        notification.is_read = True
        db.session.commit()
        
        # Get updated unread count
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        
        return jsonify({
            'success': True,
            'unread_count': unread_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@notifications_bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_as_read():
    """Mark all notifications as read"""
    try:
        Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
        db.session.commit()
        
        return jsonify({'success': True, 'unread_count': 0}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


def extract_mentions(text):
    """Extract @mentions from text"""
    # Find all @username patterns (supports dots, underscores, hyphens)
    mentions = re.findall(r'@([\w.-]+)', text)
    return list(set(mentions))  # Remove duplicates


def create_mention_notifications(comment, content):
    """Create notifications for mentioned users"""
    from app.models import User
    
    mentions = extract_mentions(content)
    print(f"[Mentions] Extracted mentions from content: {mentions}")
    
    if not mentions:
        print("[Mentions] No mentions found")
        return
    
    # Get users by username
    for username in mentions:
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"[Mentions] User @{username} not found")
            continue
            
        if user.id == current_user.id:
            print(f"[Mentions] Skipping self-mention for @{username}")
            continue
        
        # Check if notification already exists
        existing = Notification.query.filter_by(
            user_id=user.id,
            actor_id=current_user.id,
            type='mention',
            comment_id=comment.id
        ).first()
        
        if existing:
            print(f"[Mentions] Notification already exists for @{username}")
            continue
        
        notification = Notification(
            user_id=user.id,
            actor_id=current_user.id,
            type='mention',
            comment_id=comment.id,
            question_id=comment.question_id
        )
        db.session.add(notification)
        print(f"[Mentions] Created notification for user {user.id} (@{username})")
    
    try:
        db.session.commit()
        print("[Mentions] Notifications committed successfully")
    except Exception as e:
        db.session.rollback()
        print(f"[Mentions] Error creating notifications: {e}")

