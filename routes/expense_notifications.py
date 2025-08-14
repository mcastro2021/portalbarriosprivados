"""
Rutas para el sistema de notificaciones de expensas
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Expense, User
try:
    from notification_service import NotificationService, test_email_config, test_whatsapp_config
except ImportError:
    # Usar versión simplificada si hay problemas de importación
    from notification_service_simple import NotificationService, test_whatsapp_config
    def test_email_config():
        return True, "Email temporalmente deshabilitado"
from datetime import datetime
import json

bp = Blueprint('expense_notifications', __name__, url_prefix='/admin/expense-notifications')

@bp.route('/')
@login_required
def index():
    """Panel principal de notificaciones de expensas"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('dashboard'))
    
    # Estadísticas de notificaciones (con manejo de errores)
    try:
        total_expenses = Expense.query.filter_by(status='pending').count()
        notifications_sent = Expense.query.filter_by(notification_sent=True).count()
        pending_notifications = total_expenses - notifications_sent
    except Exception as e:
        print(f"⚠️ Error consultando notificaciones: {e}")
        # Valores por defecto si no existen las columnas
        total_expenses = Expense.query.count()
        notifications_sent = 0
        pending_notifications = total_expenses
    
    # Expensas recientes (con manejo de errores)
    try:
        recent_expenses = Expense.query.join(User).filter(
            Expense.status == 'pending'
        ).order_by(Expense.created_at.desc()).limit(10).all()
    except Exception as e:
        print(f"⚠️ Error consultando expensas: {e}")
        recent_expenses = Expense.query.order_by(Expense.created_at.desc()).limit(10).all()
    
    stats = {
        'total_expenses': total_expenses,
        'notifications_sent': notifications_sent,
        'pending_notifications': pending_notifications,
        'notification_rate': (notifications_sent / total_expenses * 100) if total_expenses > 0 else 0
    }
    
    return render_template('expense_notifications/index.html', 
                         stats=stats, 
                         recent_expenses=recent_expenses)

@bp.route('/send-notification', methods=['POST'])
@login_required
def send_notification():
    """Enviar notificación individual"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        data = request.get_json()
        expense_id = data.get('expense_id')
        method = data.get('method', 'email')  # 'email', 'whatsapp', 'both'
        
        expense = Expense.query.get_or_404(expense_id)
        user = expense.user
        
        service = NotificationService()
        
        if method == 'both':
            # Enviar por ambos métodos
            email_success, email_msg = service.send_expense_notification(user, expense, 'email')
            whatsapp_success, whatsapp_msg = service.send_expense_notification(user, expense, 'whatsapp')
            
            if email_success or whatsapp_success:
                expense.notification_sent = True
                expense.notification_date = datetime.now()
                expense.notification_method = method
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': f'Notificación enviada. Email: {email_msg}, WhatsApp: {whatsapp_msg}'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Error en ambos métodos. Email: {email_msg}, WhatsApp: {whatsapp_msg}'
                })
        
        else:
            # Enviar por un método específico
            success, message = service.send_expense_notification(user, expense, method)
            
            if success:
                expense.notification_sent = True
                expense.notification_date = datetime.now()
                expense.notification_method = method
                db.session.commit()
            
            return jsonify({
                'success': success,
                'message': message
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/send-bulk', methods=['POST'])
@login_required
def send_bulk_notifications():
    """Enviar notificaciones masivas"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        data = request.get_json()
        method = data.get('method', 'email')
        expense_ids = data.get('expense_ids', [])
        
        if not expense_ids:
            # Si no se especifican IDs, enviar a todas las expensas pendientes
            expenses = Expense.query.filter_by(
                status='pending',
                notification_sent=False
            ).all()
        else:
            expenses = Expense.query.filter(Expense.id.in_(expense_ids)).all()
        
        if not expenses:
            return jsonify({'error': 'No hay expensas para procesar'}), 400
        
        # Preparar datos para envío masivo
        expenses_data = [(expense.user, expense) for expense in expenses]
        
        service = NotificationService()
        results = service.send_bulk_expense_notifications(expenses_data, method)
        
        # Marcar como enviadas las exitosas
        for expense in expenses:
            if any(f"✅ {expense.user.username}" in detail for detail in results['details']):
                expense.notification_sent = True
                expense.notification_date = datetime.now()
                expense.notification_method = method
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Proceso completado: {results["success"]} exitosas, {results["failed"]} fallidas',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/test-config', methods=['POST'])
@login_required
def test_config():
    """Probar configuración de notificaciones"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        data = request.get_json()
        service_type = data.get('service_type', 'email')
        
        if service_type == 'email':
            success, message = test_email_config()
        elif service_type == 'whatsapp':
            success, message = test_whatsapp_config()
        else:
            return jsonify({'error': 'Tipo de servicio no válido'}), 400
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/send-test', methods=['POST'])
@login_required
def send_test_notification():
    """Enviar notificación de prueba"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        data = request.get_json()
        method = data.get('method', 'email')
        
        # Crear expensa de prueba
        from datetime import datetime, timedelta
        
        test_expense = type('TestExpense', (), {
            'period': 'PRUEBA - Agosto 2025',
            'amount': 85000,
            'due_date': datetime.now() + timedelta(days=10),
            'created_at': datetime.now()
        })()
        
        service = NotificationService()
        success, message = service.send_expense_notification(current_user, test_expense, method)
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Configuración de notificaciones"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Guardar configuración (esto se haría en variables de entorno)
        flash('Configuración guardada (implementar guardado en variables de entorno)', 'info')
    
    return render_template('expense_notifications/settings.html')

@bp.route('/history')
@login_required
def history():
    """Historial de notificaciones enviadas"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener historial de notificaciones
    notifications = Expense.query.join(User).filter(
        Expense.notification_sent == True
    ).order_by(Expense.notification_date.desc()).limit(100).all()
    
    return render_template('expense_notifications/history.html', notifications=notifications)
