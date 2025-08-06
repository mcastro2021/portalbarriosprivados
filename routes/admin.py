from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, User, Visit, Reservation, News, Maintenance, Expense, Classified, SecurityReport, Notification
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.before_request
@login_required
def require_admin():
    """Verificar que el usuario sea administrador"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para acceder al panel de administración', 'error')
        return redirect(url_for('dashboard'))

@bp.route('/')
def index():
    """Dashboard de administración"""
    # Estadísticas generales
    stats = {
        'total_users': User.query.filter_by(is_active=True).count(),
        'total_visits': Visit.query.count(),
        'total_reservations': Reservation.query.count(),
        'total_maintenance': Maintenance.query.count(),
        'total_expenses': Expense.query.count(),
        'total_classifieds': Classified.query.filter_by(is_active=True).count(),
        'total_security_reports': SecurityReport.query.count()
    }
    
    # Estadísticas de este mes
    this_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_stats = {
        'visits_this_month': Visit.query.filter(Visit.created_at >= this_month).count(),
        'reservations_this_month': Reservation.query.filter(Reservation.created_at >= this_month).count(),
        'maintenance_this_month': Maintenance.query.filter(Maintenance.created_at >= this_month).count(),
        'expenses_this_month': Expense.query.filter(Expense.created_at >= this_month).count()
    }
    
    # Elementos pendientes
    pending_items = {
        'pending_visits': Visit.query.filter_by(status='pending').count(),
        'pending_reservations': Reservation.query.filter_by(status='pending').count(),
        'pending_maintenance': Maintenance.query.filter_by(status='pending').count(),
        'pending_expenses': Expense.query.filter_by(status='pending').count(),
        'security_reports': SecurityReport.query.filter_by(status='reported').count()
    }
    
    # Actividad reciente
    recent_activities = []
    
    # Últimas visitas
    recent_visits = Visit.query.order_by(Visit.created_at.desc()).limit(5).all()
    for visit in recent_visits:
        recent_activities.append({
            'type': 'visit',
            'title': f'Nueva visita: {visit.visitor_name}',
            'description': f'Residente: {visit.resident.name}',
            'time': visit.created_at,
            'status': visit.status
        })
    
    # Últimas reservas
    recent_reservations = Reservation.query.order_by(Reservation.created_at.desc()).limit(5).all()
    for reservation in recent_reservations:
        recent_activities.append({
            'type': 'reservation',
            'title': f'Nueva reserva: {reservation.space_name}',
            'description': f'Usuario: {reservation.user.name}',
            'time': reservation.created_at,
            'status': reservation.status
        })
    
    # Ordenar actividades por tiempo
    recent_activities.sort(key=lambda x: x['time'], reverse=True)
    recent_activities = recent_activities[:10]
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         monthly_stats=monthly_stats,
                         pending_items=pending_items,
                         recent_activities=recent_activities)

@bp.route('/users')
def users():
    """Gestión de usuarios"""
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role', '')
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    
    if search:
        query = query.filter(
            (User.name.contains(search)) |
            (User.username.contains(search)) |
            (User.email.contains(search))
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('admin/users.html',
                         users=users,
                         current_role=role,
                         current_status=status,
                         current_search=search)

@bp.route('/users/new', methods=['GET', 'POST'])
def new_user():
    """Crear nuevo usuario"""
    if request.method == 'POST':
        try:
            user = User(
                username=request.form.get('username'),
                email=request.form.get('email'),
                name=request.form.get('name'),
                role=request.form.get('role', 'resident'),
                address=request.form.get('address'),
                phone=request.form.get('phone'),
                emergency_contact=request.form.get('emergency_contact'),
                is_active=bool(request.form.get('is_active')),
                email_verified=bool(request.form.get('email_verified'))
            )
            user.set_password(request.form.get('password'))
            
            db.session.add(user)
            db.session.commit()
            
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'error')
    
    return render_template('admin/new_user.html')

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """Editar usuario"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            user.username = request.form.get('username')
            user.email = request.form.get('email')
            user.name = request.form.get('name')
            user.role = request.form.get('role')
            user.address = request.form.get('address')
            user.phone = request.form.get('phone')
            user.emergency_contact = request.form.get('emergency_contact')
            user.is_active = bool(request.form.get('is_active'))
            user.email_verified = bool(request.form.get('email_verified'))
            
            # Cambiar contraseña si se proporciona
            new_password = request.form.get('new_password')
            if new_password:
                user.set_password(new_password)
            
            db.session.commit()
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar usuario: {str(e)}', 'error')
    
    return render_template('admin/edit_user.html', user=user)

@bp.route('/users/<int:user_id>/toggle_status', methods=['POST'])
def toggle_user_status(user_id):
    """Activar/desactivar usuario"""
    user = User.query.get_or_404(user_id)
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activado' if user.is_active else 'desactivado'
        return jsonify({
            'success': True,
            'message': f'Usuario {status} exitosamente',
            'is_active': user.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/reservations')
def reservations():
    """Gestión de reservas"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    space_type = request.args.get('space_type', '')
    
    query = Reservation.query
    
    if status:
        query = query.filter_by(status=status)
    
    if space_type:
        query = query.filter_by(space_type=space_type)
    
    reservations = query.order_by(Reservation.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('admin/reservations.html',
                         reservations=reservations,
                         current_status=status,
                         current_space_type=space_type)

@bp.route('/reservations/<int:reservation_id>/approve', methods=['POST'])
def approve_reservation(reservation_id):
    """Aprobar reserva"""
    reservation = Reservation.query.get_or_404(reservation_id)
    
    try:
        reservation.status = 'approved'
        reservation.approved_by = current_user.id
        reservation.approved_at = datetime.utcnow()
        reservation.admin_notes = request.json.get('notes', '')
        
        db.session.commit()
        
        # Crear notificación para el usuario
        notification = Notification(
            user_id=reservation.user_id,
            title='Reserva Aprobada',
            message=f'Tu reserva de {reservation.space_name} ha sido aprobada',
            category='reservation',
            related_id=reservation.id,
            related_type='reservation'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reserva aprobada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/reservations/<int:reservation_id>/reject', methods=['POST'])
def reject_reservation(reservation_id):
    """Rechazar reserva"""
    reservation = Reservation.query.get_or_404(reservation_id)
    
    try:
        reservation.status = 'rejected'
        reservation.admin_notes = request.json.get('notes', '')
        
        db.session.commit()
        
        # Crear notificación para el usuario
        notification = Notification(
            user_id=reservation.user_id,
            title='Reserva Rechazada',
            message=f'Tu reserva de {reservation.space_name} ha sido rechazada',
            category='reservation',
            related_id=reservation.id,
            related_type='reservation'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reserva rechazada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/maintenance')
def maintenance():
    """Gestión de mantenimiento"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    
    query = Maintenance.query
    
    if status:
        query = query.filter_by(status=status)
    
    if priority:
        query = query.filter_by(priority=priority)
    
    maintenance_requests = query.order_by(Maintenance.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('admin/maintenance.html',
                         maintenance_requests=maintenance_requests,
                         current_status=status,
                         current_priority=priority)

@bp.route('/settings')
def settings():
    """Configuraciones del sistema"""
    return render_template('admin/settings.html')

@bp.route('/reports')
def reports():
    """Reportes y estadísticas"""
    # Datos para gráficos
    
    # Visitas por mes (últimos 6 meses)
    visits_by_month = []
    for i in range(6):
        start_date = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        end_date = start_date.replace(month=start_date.month+1) if start_date.month < 12 else start_date.replace(year=start_date.year+1, month=1)
        
        count = Visit.query.filter(
            Visit.created_at >= start_date,
            Visit.created_at < end_date
        ).count()
        
        visits_by_month.append({
            'month': start_date.strftime('%B %Y'),
            'count': count
        })
    
    visits_by_month.reverse()
    
    # Reservas por espacio
    reservations_by_space = db.session.query(
        Reservation.space_type,
        func.count(Reservation.id).label('count')
    ).group_by(Reservation.space_type).all()
    
    return render_template('admin/reports.html',
                         visits_by_month=visits_by_month,
                         reservations_by_space=reservations_by_space)

@bp.route('/broadcast', methods=['GET', 'POST'])
def broadcast():
    """Enviar notificaciones masivas"""
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            message = request.form.get('message')
            target_role = request.form.get('target_role', 'all')
            
            # Obtener usuarios objetivo
            if target_role == 'all':
                users = User.query.filter_by(is_active=True).all()
            else:
                users = User.query.filter_by(role=target_role, is_active=True).all()
            
            # Crear notificaciones
            for user in users:
                notification = Notification(
                    user_id=user.id,
                    title=title,
                    message=message,
                    category='admin',
                    type='push'
                )
                db.session.add(notification)
            
            db.session.commit()
            
            flash(f'Notificación enviada a {len(users)} usuarios', 'success')
            return redirect(url_for('admin.broadcast'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al enviar notificación: {str(e)}', 'error')
    
    return render_template('admin/broadcast.html')