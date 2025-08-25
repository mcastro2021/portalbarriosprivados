"""
API v1 para el Portal Barrio Privado
Implementa REST API estándar con versionado
"""

from flask import Blueprint
from .auth import auth_bp
from .users import users_bp
from .notifications import notifications_bp
from .dashboard import dashboard_bp

# Crear blueprint principal para API v1
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Registrar blueprints de módulos
api_v1.register_blueprint(auth_bp)
api_v1.register_blueprint(users_bp)
api_v1.register_blueprint(notifications_bp)
api_v1.register_blueprint(dashboard_bp)

@api_v1.route('/health')
def health_check():
    """Health check para API v1"""
    from datetime import datetime
    return {
        'status': 'healthy',
        'version': '1.0',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': [
            '/auth/login',
            '/auth/register',
            '/users/profile',
            '/users/list',
            '/notifications',
            '/dashboard/stats'
        ]
    }
