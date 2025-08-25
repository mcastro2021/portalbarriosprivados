"""
Servicio de autenticación con JWT
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify
from flask_login import current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import re


class AuthService:
    """Servicio para manejo de autenticación y JWT"""
    
    @staticmethod
    def generate_jwt_token(user_id, role='user', expires_in=3600):
        """Generar token JWT para API"""
        try:
            payload = {
                'user_id': user_id,
                'role': role,
                'exp': datetime.utcnow() + timedelta(seconds=expires_in),
                'iat': datetime.utcnow(),
                'jti': secrets.token_urlsafe(16)  # JWT ID único
            }
            
            token = jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            
            return token
        except Exception as e:
            current_app.logger.error(f'Error generando JWT: {e}')
            return None
    
    @staticmethod
    def verify_jwt_token(token):
        """Verificar y decodificar token JWT"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            return {'error': 'Token expirado'}
        except jwt.InvalidTokenError:
            return {'error': 'Token inválido'}
        except Exception as e:
            current_app.logger.error(f'Error verificando JWT: {e}')
            return {'error': 'Error de verificación'}
    
    @staticmethod
    def jwt_required(f):
        """Decorador para requerir JWT en rutas API"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            
            # Buscar token en header Authorization
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(' ')[1]  # Bearer <token>
                except IndexError:
                    return jsonify({'error': 'Formato de token inválido'}), 401
            
            # Buscar token en query params (fallback)
            if not token:
                token = request.args.get('token')
            
            if not token:
                return jsonify({'error': 'Token requerido'}), 401
            
            # Verificar token
            payload = AuthService.verify_jwt_token(token)
            if 'error' in payload:
                return jsonify({'error': payload['error']}), 401
            
            # Añadir información del usuario al request
            request.jwt_user_id = payload['user_id']
            request.jwt_role = payload['role']
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    @staticmethod
    def admin_required(f):
        """Decorador para requerir rol admin"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'jwt_role') or request.jwt_role != 'admin':
                return jsonify({'error': 'Permisos de administrador requeridos'}), 403
            return f(*args, **kwargs)
        
        return decorated_function
    
    @staticmethod
    def validate_password(password):
        """Validar fortaleza de contraseña"""
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        if not re.search(r'[A-Z]', password):
            return False, "La contraseña debe contener al menos una mayúscula"
        
        if not re.search(r'[a-z]', password):
            return False, "La contraseña debe contener al menos una minúscula"
        
        if not re.search(r'\d', password):
            return False, "La contraseña debe contener al menos un número"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "La contraseña debe contener al menos un carácter especial"
        
        return True, "Contraseña válida"
    
    @staticmethod
    def hash_password(password):
        """Hash seguro de contraseña"""
        return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    @staticmethod
    def check_password(password_hash, password):
        """Verificar contraseña"""
        return check_password_hash(password_hash, password)
    
    @staticmethod
    def generate_secure_token():
        """Generar token seguro para reset de contraseña, etc."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_email(email):
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def sanitize_input(input_string):
        """Sanitizar entrada de usuario"""
        if not input_string:
            return ""
        
        # Remover caracteres peligrosos
        dangerous_chars = ['<', '>', '"', "'", '&', 'script', 'javascript:', 'onload', 'onerror']
        sanitized = str(input_string)
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
