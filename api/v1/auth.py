"""
API v1 - Autenticación
Endpoints para login, registro y gestión de tokens
"""

from flask import Blueprint, request, jsonify
from security import jwt_required, validate_input, LOGIN_SCHEMA, REGISTER_SCHEMA
from services.user_service import user_service
from security import security_manager
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login de usuario con JWT"""
    try:
        data = request.get_json()
        
        # Validar datos de entrada
        is_valid, error_message = validate_input(data, LOGIN_SCHEMA)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # Autenticar usuario
        auth_result = security_manager.authenticate_user(username, password)
        
        if auth_result:
            user = auth_result['user']
            token = auth_result['token']
            
            logger.info(f"Login exitoso para usuario: {username}")
            
            return jsonify({
                'success': True,
                'message': 'Login exitoso',
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'role': user.role,
                    'email': user.email
                }
            }), 200
        else:
            logger.warning(f"Login fallido para usuario: {username}")
            return jsonify({
                'success': False,
                'error': 'Credenciales inválidas'
            }), 401
            
    except Exception as e:
        logger.error(f"Error en login: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registro de nuevo usuario"""
    try:
        data = request.get_json()
        
        # Validar datos de entrada
        is_valid, error_message = validate_input(data, REGISTER_SCHEMA)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Registrar usuario
        result = user_service.register_user(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error en registro: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    """Logout de usuario (invalidar token)"""
    try:
        # En una implementación más robusta, aquí se invalidaría el token
        # Por ahora, solo devolvemos éxito
        logger.info(f"Logout exitoso para usuario: {request.current_user.username}")
        
        return jsonify({
            'success': True,
            'message': 'Logout exitoso'
        }), 200
        
    except Exception as e:
        logger.error(f"Error en logout: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required
def refresh_token():
    """Renovar token JWT"""
    try:
        user = request.current_user
        
        # Generar nuevo token
        new_token = security_manager.generate_token(user)
        
        logger.info(f"Token renovado para usuario: {user.username}")
        
        return jsonify({
            'success': True,
            'token': new_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'role': user.role,
                'email': user.email
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error renovando token: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required
def get_current_user():
    """Obtener información del usuario actual"""
    try:
        user = request.current_user
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'role': user.role,
                'email': user.email,
                'address': user.address,
                'phone': user.phone,
                'emergency_contact': user.emergency_contact,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo usuario actual: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
