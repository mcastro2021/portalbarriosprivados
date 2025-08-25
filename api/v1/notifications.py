"""
API v1 - Notificaciones
Endpoints para gestión de notificaciones
"""

from flask import Blueprint, request, jsonify
from security import jwt_required
from models import Notification, db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
@jwt_required
def get_notifications():
    """Obtener notificaciones del usuario"""
    try:
        user = request.current_user
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        notifications = Notification.query.filter_by(user_id=user.id)\
            .order_by(Notification.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'notifications': [
                {
                    'id': n.id,
                    'title': n.title,
                    'message': n.message,
                    'type': n.type,
                    'category': n.category,
                    'is_read': n.is_read,
                    'created_at': n.created_at.isoformat() if n.created_at else None,
                    'read_at': n.read_at.isoformat() if n.read_at else None
                }
                for n in notifications.items
            ],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': notifications.total,
                'pages': notifications.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo notificaciones: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@notifications_bp.route('/count', methods=['GET'])
@jwt_required
def get_notifications_count():
    """Obtener conteo de notificaciones no leídas"""
    try:
        user = request.current_user
        unread_count = Notification.query.filter_by(user_id=user.id, is_read=False).count()
        
        return jsonify({
            'success': True,
            'count': unread_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo conteo de notificaciones: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
@jwt_required
def mark_as_read(notification_id):
    """Marcar notificación como leída"""
    try:
        user = request.current_user
        notification = Notification.query.get_or_404(notification_id)
        
        if notification.user_id != user.id:
            return jsonify({
                'success': False,
                'error': 'No autorizado'
            }), 403
        
        notification.mark_as_read()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notificación marcada como leída'
        }), 200
        
    except Exception as e:
        logger.error(f"Error marcando notificación como leída: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@notifications_bp.route('/mark-all-read', methods=['POST'])
@jwt_required
def mark_all_as_read():
    """Marcar todas las notificaciones como leídas"""
    try:
        user = request.current_user
        
        Notification.query.filter_by(user_id=user.id, is_read=False)\
            .update({'is_read': True, 'read_at': datetime.utcnow()})
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Todas las notificaciones marcadas como leídas'
        }), 200
        
    except Exception as e:
        logger.error(f"Error marcando todas las notificaciones como leídas: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
