"""
API v1 para el Portal Barrio Privado
Implementa REST API estándar con versionado
"""

from flask import Blueprint

# Crear blueprint principal para API v1
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Registrar blueprints de módulos de manera segura
try:
    from .auth import auth_bp
    api_v1.register_blueprint(auth_bp)
    print("✅ API v1 auth registrado")
except ImportError as e:
    print(f"⚠️ No se pudo importar auth_bp: {e}")

try:
    from .users import users_bp
    api_v1.register_blueprint(users_bp)
    print("✅ API v1 users registrado")
except ImportError as e:
    print(f"⚠️ No se pudo importar users_bp: {e}")

try:
    from .notifications import notifications_bp
    api_v1.register_blueprint(notifications_bp)
    print("✅ API v1 notifications registrado")
except ImportError as e:
    print(f"⚠️ No se pudo importar notifications_bp: {e}")

try:
    from .dashboard import dashboard_bp
    api_v1.register_blueprint(dashboard_bp)
    print("✅ API v1 dashboard registrado")
except ImportError as e:
    print(f"⚠️ No se pudo importar dashboard_bp: {e}")

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
