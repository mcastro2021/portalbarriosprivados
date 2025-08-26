"""
Módulo de seguridad para el Portal Barrio Privado
Implementa JWT, CORS, rate limiting y validación robusta
"""

import os
import time
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from flask_cors import CORS
from werkzeug.security import check_password_hash
from models import User
import redis
import logging

# Configurar logging
logger = logging.getLogger(__name__)

class SecurityManager:
    """Gestor centralizado de seguridad"""
    
    def __init__(self, app=None):
        self.app = app
        self.redis_client = None
        self.jwt_secret = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.jwt_algorithm = 'HS256'
        self.jwt_expiration = 24 * 60 * 60  # 24 horas
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar extensiones de seguridad"""
        self.app = app
        
        # Configurar CORS
        CORS(app, resources={
            r"/api/*": {
                "origins": ["https://portalbarriosprivados.onrender.com", "http://localhost:3000"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "supports_credentials": True
            }
        })
        
        # Configurar Redis para rate limiting (opcional)
        try:
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
            self.redis_client = redis.from_url(redis_url)
            # Test de conexión
            self.redis_client.ping()
            logger.info("✅ Redis conectado para rate limiting")
        except Exception as e:
            logger.warning(f"⚠️ Rate limiting no disponible: {e}")
            self.redis_client = None
        
        # Registrar middleware de seguridad
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Middleware ejecutado antes de cada request"""
        # Log de requests
        logger.info(f"{request.method} {request.path} - {request.remote_addr}")
        
        # Rate limiting para APIs
        if request.path.startswith('/api/'):
            self.check_rate_limit()
    
    def after_request(self, response):
        """Middleware ejecutado después de cada request"""
        # Headers de seguridad
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    def check_rate_limit(self):
        """Verificar rate limiting"""
        if not self.redis_client:
            return  # Si Redis no está disponible, no aplicar rate limiting
        
        client_ip = request.remote_addr
        key = f"rate_limit:{client_ip}"
        
        try:
            current = self.redis_client.get(key)
            if current and int(current) > 100:  # 100 requests por minuto
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)  # 1 minuto
            pipe.execute()
        except Exception as e:
            logger.warning(f"Rate limiting no disponible: {e}")
            # No fallar la aplicación si Redis no está disponible
    
    def generate_token(self, user):
        """Generar JWT token para usuario"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(seconds=self.jwt_expiration),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_token(self, token):
        """Verificar JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def authenticate_user(self, username, password):
        """Autenticar usuario y devolver token"""
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            return {
                'user': user,
                'token': self.generate_token(user)
            }
        
        return None

# Decoradores de seguridad
def jwt_required(f):
    """Decorador para requerir JWT token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Obtener token del header Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token requerido'}), 401
        
        # Verificar token
        payload = current_app.security_manager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        # Obtener usuario
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({'error': 'Usuario no válido'}), 401
        
        # Agregar usuario al request
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function

def role_required(required_role):
    """Decorador para requerir rol específico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Autenticación requerida'}), 401
            
            if request.current_user.role != required_role and request.current_user.role != 'admin':
                return jsonify({'error': 'Permisos insuficientes'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorador para requerir rol de administrador"""
    return role_required('admin')(f)

# Validación de entrada
def validate_input(data, schema):
    """Validar datos de entrada según esquema"""
    try:
        # Validación básica - se puede expandir con Marshmallow
        for field, rules in schema.items():
            if field not in data:
                if rules.get('required', False):
                    return False, f"Campo '{field}' es requerido"
                continue
            
            value = data[field]
            
            # Validar tipo
            if 'type' in rules:
                if not isinstance(value, rules['type']):
                    return False, f"Campo '{field}' debe ser de tipo {rules['type'].__name__}"
            
            # Validar longitud
            if 'min_length' in rules and len(str(value)) < rules['min_length']:
                return False, f"Campo '{field}' debe tener al menos {rules['min_length']} caracteres"
            
            if 'max_length' in rules and len(str(value)) > rules['max_length']:
                return False, f"Campo '{field}' debe tener máximo {rules['max_length']} caracteres"
            
            # Validar valores permitidos
            if 'allowed_values' in rules and value not in rules['allowed_values']:
                return False, f"Campo '{field}' debe ser uno de: {rules['allowed_values']}"
        
        return True, None
    except Exception as e:
        return False, f"Error de validación: {str(e)}"

# Esquemas de validación comunes
LOGIN_SCHEMA = {
    'username': {'required': True, 'type': str, 'min_length': 3, 'max_length': 50},
    'password': {'required': True, 'type': str, 'min_length': 6, 'max_length': 100}
}

REGISTER_SCHEMA = {
    'username': {'required': True, 'type': str, 'min_length': 3, 'max_length': 50},
    'email': {'required': True, 'type': str, 'max_length': 100},
    'password': {'required': True, 'type': str, 'min_length': 6, 'max_length': 100},
    'name': {'required': True, 'type': str, 'min_length': 2, 'max_length': 100}
}

# Instancia global
security_manager = SecurityManager()
