"""
Sistema avanzado de gestión de usuarios para administradores
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, User
from datetime import datetime
import json

bp = Blueprint('user_management', __name__, url_prefix='/admin/users')

@bp.route('/')
@login_required
def index():
    """Vista principal de gestión de usuarios"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener todos los usuarios con estadísticas
    users = User.query.all()
    
    # Estadísticas generales
    stats = {
        'total_users': len(users),
        'active_users': len([u for u in users if u.is_active]),
        'admin_users': len([u for u in users if u.role == 'admin']),
        'verified_users': len([u for u in users if u.email_verified]),
        'recent_users': len([u for u in users if u.created_at and 
                           (datetime.utcnow() - u.created_at).days <= 30])
    }
    
    # Filtros
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    
    # Aplicar filtros
    filtered_users = users
    
    if search:
        filtered_users = [u for u in filtered_users if 
                         search.lower() in (u.username or '').lower() or
                         search.lower() in (u.name or '').lower() or
                         search.lower() in (u.email or '').lower()]
    
    if role_filter:
        filtered_users = [u for u in filtered_users if u.role == role_filter]
    
    if status_filter == 'active':
        filtered_users = [u for u in filtered_users if u.is_active]
    elif status_filter == 'inactive':
        filtered_users = [u for u in filtered_users if not u.is_active]
    elif status_filter == 'verified':
        filtered_users = [u for u in filtered_users if u.email_verified]
    elif status_filter == 'unverified':
        filtered_users = [u for u in filtered_users if not u.email_verified]
    
    return render_template('user_management/index.html', 
                         users=filtered_users, 
                         stats=stats,
                         search=search,
                         role_filter=role_filter,
                         status_filter=status_filter)

@bp.route('/reset-password', methods=['POST'])
@login_required
def reset_password():
    """Resetear contraseña de un usuario"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        new_password = data.get('new_password', 'temp123456')
        
        user = User.query.get_or_404(user_id)
        
        # Permitir que admin se cambie su propia contraseña también
        if user_id != current_user.id and not current_user.can_access_admin():
            return jsonify({'error': 'No puedes cambiar la contraseña de otros usuarios'}), 403
        
        # Cambiar contraseña
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Contraseña de {user.username} resetada exitosamente',
            'new_password': new_password
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/generate-password', methods=['POST'])
@login_required
def generate_password():
    """Generar contraseña segura aleatoria"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    import secrets
    import string
    
    # Generar contraseña segura
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    
    return jsonify({
        'success': True,
        'password': password
    })

@bp.route('/toggle-status/<int:user_id>', methods=['POST'])
@login_required
def toggle_status(user_id):
    """Activar/desactivar usuario"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        
        # No permitir desactivarse a sí mismo
        if user_id == current_user.id:
            return jsonify({'error': 'No puedes desactivar tu propia cuenta'}), 400
        
        # Cambiar estado
        user.is_active = not user.is_active
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = 'activado' if user.is_active else 'desactivado'
        
        return jsonify({
            'success': True,
            'message': f'Usuario {user.username} {status} exitosamente',
            'new_status': user.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/change-role/<int:user_id>', methods=['POST'])
@login_required
def change_role(user_id):
    """Cambiar rol de usuario"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        data = request.get_json()
        new_role = data.get('new_role')
        
        if new_role not in ['user', 'admin', 'moderator']:
            return jsonify({'error': 'Rol inválido'}), 400
        
        user = User.query.get_or_404(user_id)
        
        # Verificación especial para cambios de rol de admin
        if user.role == 'admin' and new_role != 'admin':
            # Verificar que no sea el último admin
            admin_count = User.query.filter_by(role='admin', is_active=True).count()
            if admin_count <= 1:
                return jsonify({'error': 'No puedes quitar el rol de admin al último administrador'}), 400
        
        old_role = user.role
        user.role = new_role
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Rol de {user.username} cambiado de {old_role} a {new_role}',
            'new_role': new_role
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/verify-email/<int:user_id>', methods=['POST'])
@login_required
def verify_email(user_id):
    """Verificar email manualmente"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        
        user.email_verified = True
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Email de {user.username} verificado manualmente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/user-details/<int:user_id>')
@login_required
def user_details(user_id):
    """Obtener detalles completos de un usuario"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Estadísticas del usuario
    user_stats = {
        'total_visits': len(user.resident_visits) if hasattr(user, 'resident_visits') else 0,
        'total_reservations': len(user.reservations) if hasattr(user, 'reservations') else 0,
        'total_maintenance': len(user.maintenance_requests) if hasattr(user, 'maintenance_requests') else 0,
        'total_expenses': len(user.expenses) if hasattr(user, 'expenses') else 0,
        'last_login_str': user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'Nunca',
        'created_str': user.created_at.strftime('%d/%m/%Y %H:%M') if user.created_at else 'N/A',
        'days_since_creation': (datetime.utcnow() - user.created_at).days if user.created_at else 0
    }
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'is_active': user.is_active,
            'email_verified': user.email_verified,
            'phone': user.phone,
            'address': user.address,
            'created_at': user_stats['created_str'],
            'last_login': user_stats['last_login_str'],
            'days_since_creation': user_stats['days_since_creation']
        },
        'stats': user_stats
    })

@bp.route('/bulk-actions', methods=['POST'])
@login_required
def bulk_actions():
    """Acciones en lote para múltiples usuarios"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        data = request.get_json()
        user_ids = data.get('user_ids', [])
        action = data.get('action')
        
        if not user_ids or not action:
            return jsonify({'error': 'Faltan parámetros'}), 400
        
        users = User.query.filter(User.id.in_(user_ids)).all()
        results = []
        
        for user in users:
            try:
                if action == 'activate':
                    if user.id != current_user.id:  # No desactivarse a sí mismo
                        user.is_active = True
                        results.append(f'{user.username}: activado')
                    
                elif action == 'deactivate':
                    if user.id != current_user.id:  # No desactivarse a sí mismo
                        user.is_active = False
                        results.append(f'{user.username}: desactivado')
                    
                elif action == 'verify_email':
                    user.email_verified = True
                    results.append(f'{user.username}: email verificado')
                    
                elif action == 'reset_password':
                    temp_password = 'temp123456'
                    user.set_password(temp_password)
                    results.append(f'{user.username}: contraseña resetada')
                    
                user.updated_at = datetime.utcnow()
                
            except Exception as e:
                results.append(f'{user.username}: error - {str(e)}')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Acción {action} aplicada a {len(users)} usuarios',
            'results': results
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/export', methods=['GET'])
@login_required
def export_users():
    """Exportar lista de usuarios"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para esta acción', 'error')
        return redirect(url_for('user_management.index'))
    
    import csv
    from io import StringIO
    from flask import make_response
    
    # Obtener usuarios
    users = User.query.all()
    
    # Crear CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow(['ID', 'Username', 'Email', 'Nombre', 'Rol', 'Activo', 'Email Verificado', 
                    'Teléfono', 'Dirección', 'Creado', 'Último Login'])
    
    # Datos
    for user in users:
        writer.writerow([
            user.id,
            user.username,
            user.email,
            user.name,
            user.role,
            'Sí' if user.is_active else 'No',
            'Sí' if user.email_verified else 'No',
            user.phone or '',
            user.address or '',
            user.created_at.strftime('%d/%m/%Y %H:%M') if user.created_at else '',
            user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else ''
        ])
    
    # Crear respuesta
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=usuarios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response
