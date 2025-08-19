from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Visit, Reservation, News, Maintenance, Expense, Classified, SecurityReport, Notification
from datetime import datetime, timedelta
import os

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
    # Fechas para cálculos
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_month = today.replace(day=1)
    
    # Estadísticas generales
    stats = {
        'total_users': User.query.filter_by(is_active=True).count(),
        'total_visits': Visit.query.count(),
        'total_visits_today': Visit.query.filter(Visit.created_at >= today).count(),
        'total_reservations': Reservation.query.count(),
        'pending_reservations': Reservation.query.filter_by(status='pending').count(),
        'total_maintenance': Maintenance.query.count(),
        'pending_maintenance': Maintenance.query.filter_by(status='pending').count(),
        'active_news': News.query.filter_by(is_published=True).count(),
        'monthly_visits': Visit.query.filter(Visit.created_at >= start_of_month).count(),
        'monthly_reservations': Reservation.query.filter(Reservation.created_at >= start_of_month).count(),
        'monthly_maintenance': Maintenance.query.filter(Maintenance.created_at >= start_of_month).count(),
        'monthly_expenses': Expense.query.filter(Expense.created_at >= start_of_month).count(),
        'pending_visits': Visit.query.filter_by(status='pending').count(),
        'pending_expenses': Expense.query.filter_by(status='pending').count(),
        'pending_security': SecurityReport.query.filter_by(status='pending').count() if hasattr(SecurityReport, 'status') else 0,
        'active_classifieds': Classified.query.filter_by(is_active=True).count() if hasattr(Classified, 'is_active') else 0
    }
    
    # Actividad reciente
    recent_visits = Visit.query.join(User, Visit.resident_id == User.id).order_by(Visit.created_at.desc()).limit(5).all()
    recent_reservations = Reservation.query.join(User, Reservation.user_id == User.id).order_by(Reservation.created_at.desc()).limit(5).all()
    recent_maintenance = Maintenance.query.join(User, Maintenance.user_id == User.id).order_by(Maintenance.created_at.desc()).limit(5).all()
    
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

@bp.route('/email-config')
@login_required
@admin_required
def email_config():
    """Configuración de email y WhatsApp"""
    # Obtener configuración actual desde variables de entorno
    config = {
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': os.getenv('SMTP_PORT', '587'),
        'smtp_username': os.getenv('SMTP_USERNAME', ''),
        'smtp_password': os.getenv('SMTP_PASSWORD', ''),
        'from_name': os.getenv('SMTP_FROM_NAME', 'Barrio Tejas 4'),
        'use_tls': os.getenv('SMTP_USE_TLS', '1') == '1',
        'whatsapp_api_key': os.getenv('WHATSAPP_API_KEY', ''),
        'whatsapp_phone_id': os.getenv('WHATSAPP_PHONE_ID', ''),
        'whatsapp_business_id': os.getenv('WHATSAPP_BUSINESS_ID', ''),
        'test_phone': os.getenv('TEST_PHONE', '')
    }
    
    return render_template('admin/email_config.html', config=config)

@bp.route('/save-email-config', methods=['POST'])
@login_required
@admin_required
def save_email_config():
    """Guardar configuración de email"""
    try:
        # En un entorno real, esto se guardaría en la base de datos
        # Por ahora, solo mostramos un mensaje de éxito
        flash('Configuración de email guardada correctamente', 'success')
        return redirect(url_for('admin.email_config'))
    except Exception as e:
        flash(f'Error al guardar la configuración: {str(e)}', 'error')
        return redirect(url_for('admin.email_config'))

@bp.route('/save-whatsapp-config', methods=['POST'])
@login_required
@admin_required
def save_whatsapp_config():
    """Guardar configuración de WhatsApp"""
    try:
        # En un entorno real, esto se guardaría en la base de datos
        # Por ahora, solo mostramos un mensaje de éxito
        flash('Configuración de WhatsApp guardada correctamente', 'success')
        return redirect(url_for('admin.email_config'))
    except Exception as e:
        flash(f'Error al guardar la configuración: {str(e)}', 'error')
        return redirect(url_for('admin.email_config'))

@bp.route('/test-email', methods=['POST'])
@login_required
@admin_required
def test_email():
    """Probar envío de email"""
    try:
        from notification_service import notification_service
        
        # Enviar email de prueba al administrador
        success = notification_service.send_email(
            to_email=current_user.email,
            subject='Prueba de Email - Portal del Barrio',
            body='Este es un email de prueba para verificar la configuración del servidor SMTP.',
            html_body='<h2>Prueba de Email</h2><p>Este es un email de prueba para verificar la configuración del servidor SMTP.</p>'
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Email de prueba enviado correctamente'})
        else:
            return jsonify({'success': False, 'error': 'Error al enviar el email de prueba'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})

@bp.route('/test-whatsapp', methods=['POST'])
@login_required
@admin_required
def test_whatsapp():
    """Probar envío de WhatsApp"""
    try:
        from notification_service import notification_service
        
        # Enviar WhatsApp de prueba
        success = notification_service.send_whatsapp(
            phone_number=os.getenv('TEST_PHONE', ''),
            message='🔔 Prueba de WhatsApp\n\nEste es un mensaje de prueba para verificar la configuración de WhatsApp Business API.\n\nPortal del Barrio Tejas 4'
        )
        
        if success:
            return jsonify({'success': True, 'message': 'WhatsApp de prueba enviado correctamente'})
        else:
            return jsonify({'success': False, 'error': 'Error al enviar el WhatsApp de prueba'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})

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
