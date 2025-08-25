from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

users_bp = Blueprint('users', __name__)

@users_bp.route('/users/profile', methods=['GET'])
@login_required
def get_profile():
    """Obtener perfil del usuario actual"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'name': current_user.name,
        'role': current_user.role,
        'is_active': current_user.is_active
    })

@users_bp.route('/users/profile', methods=['PUT'])
@login_required
def update_profile():
    """Actualizar perfil del usuario"""
    data = request.get_json()
    
    if data.get('name'):
        current_user.name = data['name']
    if data.get('email'):
        current_user.email = data['email']
    
    from models import db
    db.session.commit()
    
    return jsonify({'message': 'Perfil actualizado correctamente'})
