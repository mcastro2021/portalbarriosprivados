from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

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
