from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import Notification, db
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running'
    })

@bp.route('/user/profile')
@login_required
def user_profile():
    """Get current user profile"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'name': current_user.name,
        'email': current_user.email,
        'role': current_user.role
    })

@bp.route('/notifications/count')
@login_required
def notifications_count():
    """Get unread notifications count"""
    try:
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return jsonify({
            'success': True,
            'count': unread_count
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
