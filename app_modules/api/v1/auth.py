"""
API de autenticación v1
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, current_user
from datetime import datetime, timedelta
from models import db, User
from app_modules.services.auth_service import AuthService
from app_modules.services.security_service import SecurityService
from app_modules.core.error_handler import ValidationError, BusinessLogicError

auth_bp = Blueprint('auth_api', __name__)


@auth_bp.route('/login', methods=['POST'])
@SecurityService.rate_limit(max_requests=5, window_seconds=300, per='ip')
def login():
    """
    Iniciar sesión y obtener token JWT
    
    Body:
    {
        "username": "usuario",
        "password": "contraseña",
        "remember_me": false
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos'}), 400
        
        username = data.get('username')
        password = data.get('password')
        remember_me = data.get('remember_me', False)
        
        if not username or not password:
            return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
        
        # Sanitizar entrada
        username = AuthService.sanitize_input(username)
        
        # Buscar usuario
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            SecurityService.log_security_event(
                'failed_login',
                {'username': username},
                'warning'
            )
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Cuenta desactivada'}), 401
        
        # Generar token JWT
        expires_in = 86400 if remember_me else 3600  # 24h o 1h
        token = AuthService.generate_jwt_token(
            user_id=user.id,
            role=user.role,
            expires_in=expires_in
        )
        
        if not token:
            return jsonify({'error': 'Error generando token'}), 500
        
        # Login para sesión web (opcional)
        login_user(user, remember=remember_me)
        
        # Log successful login
        SecurityService.log_security_event(
            'successful_login',
            {'user_id': user.id, 'username': user.username},
            'info'
        )
        
        return jsonify({
            'success': True,
            'token': token,
            'expires_in': expires_in,
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'Error en login API: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500


@auth_bp.route('/logout', methods=['POST'])
@AuthService.jwt_required
def logout():
    """Cerrar sesión"""
    try:
        # Logout de sesión web
        logout_user()
        
        # Log logout
        SecurityService.log_security_event(
            'logout',
            {'user_id': getattr(request, 'jwt_user_id', None)},
            'info'
        )
        
        return jsonify({
            'success': True,
            'message': 'Sesión cerrada correctamente'
        })
        
    except Exception as e:
        current_app.logger.error(f'Error en logout API: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500


@auth_bp.route('/register', methods=['POST'])
@SecurityService.rate_limit(max_requests=3, window_seconds=3600, per='ip')
def register():
    """
    Registrar nuevo usuario
    
    Body:
    {
        "username": "usuario",
        "email": "email@ejemplo.com",
        "password": "contraseña",
        "name": "Nombre Completo",
        "phone": "+54911234567",
        "address": "Dirección"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos'}), 400
        
        # Validar campos requeridos
        required_fields = ['username', 'email', 'password', 'name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} requerido'}), 400
        
        username = AuthService.sanitize_input(data['username'])
        email = AuthService.sanitize_input(data['email'])
        password = data['password']
        name = AuthService.sanitize_input(data['name'])
        
        # Validar email
        if not AuthService.validate_email(email):
            return jsonify({'error': 'Formato de email inválido'}), 400
        
        # Validar contraseña
        is_valid, message = AuthService.validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Verificar si usuario ya existe
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            return jsonify({'error': 'Usuario o email ya existe'}), 409
        
        # Crear nuevo usuario
        user = User(
            username=username,
            email=email,
            name=name,
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            role='resident',  # Por defecto
            is_active=True,
            email_verified=False
        )
        
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Log registration
        SecurityService.log_security_event(
            'user_registration',
            {'user_id': user.id, 'username': user.username, 'email': user.email},
            'info'
        )
        
        return jsonify({
            'success': True,
            'message': 'Usuario registrado correctamente',
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error en registro API: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@AuthService.jwt_required
def change_password():
    """
    Cambiar contraseña del usuario autenticado
    
    Body:
    {
        "current_password": "contraseña_actual",
        "new_password": "nueva_contraseña"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos'}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Contraseña actual y nueva requeridas'}), 400
        
        # Obtener usuario
        user = User.query.get(request.jwt_user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Verificar contraseña actual
        if not user.check_password(current_password):
            return jsonify({'error': 'Contraseña actual incorrecta'}), 400
        
        # Validar nueva contraseña
        is_valid, message = AuthService.validate_password(new_password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Cambiar contraseña
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log password change
        SecurityService.log_security_event(
            'password_change',
            {'user_id': user.id, 'username': user.username},
            'info'
        )
        
        return jsonify({
            'success': True,
            'message': 'Contraseña cambiada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error cambiando contraseña API: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500


@auth_bp.route('/profile', methods=['GET'])
@AuthService.jwt_required
def get_profile():
    """Obtener perfil del usuario autenticado"""
    try:
        user = User.query.get(request.jwt_user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'address': user.address,
                'role': user.role,
                'is_active': user.is_active,
                'email_verified': user.email_verified,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'Error obteniendo perfil API: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500


@auth_bp.route('/profile', methods=['PUT'])
@AuthService.jwt_required
def update_profile():
    """
    Actualizar perfil del usuario autenticado
    
    Body:
    {
        "name": "Nuevo Nombre",
        "phone": "+54911234567",
        "address": "Nueva Dirección",
        "emergency_contact": "Contacto de Emergencia"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos'}), 400
        
        user = User.query.get(request.jwt_user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Campos actualizables
        updatable_fields = ['name', 'phone', 'address', 'emergency_contact']
        
        for field in updatable_fields:
            if field in data:
                sanitized_value = AuthService.sanitize_input(data[field])
                setattr(user, field, sanitized_value)
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Perfil actualizado correctamente',
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'address': user.address,
                'role': user.role
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error actualizando perfil API: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500


@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """
    Verificar validez de token JWT
    
    Body:
    {
        "token": "jwt_token_here"
    }
    """
    try:
        data = request.get_json()
        if not data or not data.get('token'):
            return jsonify({'error': 'Token requerido'}), 400
        
        token = data['token']
        payload = AuthService.verify_jwt_token(token)
        
        if 'error' in payload:
            return jsonify({'valid': False, 'error': payload['error']}), 401
        
        # Verificar que el usuario aún existe y está activo
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({'valid': False, 'error': 'Usuario no válido'}), 401
        
        return jsonify({
            'valid': True,
            'payload': {
                'user_id': payload['user_id'],
                'role': payload['role'],
                'exp': payload['exp'],
                'iat': payload['iat']
            },
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'role': user.role
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'Error verificando token API: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500
