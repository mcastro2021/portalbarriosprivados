from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Visit, Reservation, News, Maintenance, Expense, Classified, SecurityReport, Notification
from datetime import datetime, timedelta

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorador que requiere permisos de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_access_admin():
            flash('No tienes permisos para acceder a esta página.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def dashboard():
    """Panel de administración principal"""
    # Estadísticas generales
    stats = {
        'total_users': User.query.filter_by(is_active=True).count(),
        'total_visits_today': Visit.query.filter(
            Visit.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count(),
        'pending_reservations': Reservation.query.filter_by(status='pending').count(),
        'pending_maintenance': Maintenance.query.filter_by(status='pending').count(),
        'active_news': News.query.filter_by(is_published=True).count()
    }
    
    # Actividad reciente
    recent_visits = Visit.query.order_by(Visit.created_at.desc()).limit(5).all()
    recent_reservations = Reservation.query.order_by(Reservation.created_at.desc()).limit(5).all()
    recent_maintenance = Maintenance.query.order_by(Maintenance.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_visits=recent_visits,
                         recent_reservations=recent_reservations,
                         recent_maintenance=recent_maintenance)

@bp.route('/reports')
@login_required
@admin_required
def reports():
    """Reportes y estadísticas"""
    # Datos para reportes básicos
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # Visitas por mes
    monthly_visits = Visit.query.filter(
        Visit.created_at >= start_date
    ).count()
    
    # Reservas por mes
    monthly_reservations = Reservation.query.filter(
        Reservation.created_at >= start_date
    ).count()
    
    # Mantenimientos por mes
    monthly_maintenance = Maintenance.query.filter(
        Maintenance.created_at >= start_date
    ).count()
    
    return render_template('admin/reports.html',
                         monthly_visits=monthly_visits,
                         monthly_reservations=monthly_reservations,
                         monthly_maintenance=monthly_maintenance)

@bp.route('/settings')
@login_required
@admin_required
def settings():
    """Configuraciones del sistema"""
    return render_template('admin/settings.html')

@bp.route('/users')
@login_required
@admin_required
def users():
    """Gestión de usuarios"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page, per_page=20, error_out=False
    )
    return jsonify({
        'users': [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None
        } for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    })

@bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Activar/desactivar usuario"""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'error': 'No puedes desactivar tu propia cuenta'}), 400
    
    user.is_active = not user.is_active
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Usuario {"activado" if user.is_active else "desactivado"} correctamente',
        'is_active': user.is_active
    })

# Rutas adicionales para templates existentes
@bp.route('/reservations')
@login_required
@admin_required
def reservations():
    """Gestión de reservas (redirige a reservations)"""
    return redirect(url_for('reservations.index'))

@bp.route('/maintenance')
@login_required
@admin_required
def maintenance():
    """Gestión de mantenimiento (redirige a maintenance)"""
    return redirect(url_for('maintenance.index'))

@bp.route('/broadcast')
@login_required
@admin_required
def broadcast():
    """Sistema de notificaciones masivas"""
    flash('Función de notificaciones masivas en desarrollo', 'info')
    return redirect(url_for('admin.dashboard'))
