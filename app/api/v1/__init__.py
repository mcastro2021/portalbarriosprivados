"""
API REST v1
"""

from flask import Blueprint, jsonify
from datetime import datetime

# Crear blueprint para API v1
api_v1 = Blueprint('api_v1', __name__)

# Importar recursos de API
from .users import users_bp
from .auth import auth_bp
from .dashboard import dashboard_bp
from .notifications import notifications_bp

# Registrar blueprints de recursos
api_v1.register_blueprint(users_bp, url_prefix='/users')
api_v1.register_blueprint(auth_bp, url_prefix='/auth')
api_v1.register_blueprint(dashboard_bp, url_prefix='/dashboard')
api_v1.register_blueprint(notifications_bp, url_prefix='/notifications')

@api_v1.route('/')
def api_info():
    """Información de la API v1"""
    return jsonify({
        'name': 'Portal Barrios Privados API',
        'version': '1.0.0',
        'description': 'API REST para gestión de barrios privados',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': {
            'auth': '/api/v1/auth',
            'users': '/api/v1/users',
            'dashboard': '/api/v1/dashboard',
            'notifications': '/api/v1/notifications'
        },
        'documentation': '/api/v1/docs',
        'status': 'active'
    })

@api_v1.route('/health')
def health_check():
    """Health check de la API"""
    try:
        from models import db
        from sqlalchemy import text
        
        # Test database connection
        db.session.execute(text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'database': db_status,
        'services': {
            'cache': 'available',
            'auth': 'available',
            'notifications': 'available'
        }
    })

__all__ = ['api_v1']
