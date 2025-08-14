"""
Rutas para el sistema de notificaciones de expensas - VERSION SIMPLIFICADA
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime

# Importar modelos de manera segura
try:
    from models import db, Expense, User
    MODELS_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Error importando modelos: {e}")
    MODELS_AVAILABLE = False

# Importar servicio de notificaciones de manera segura
try:
    from notification_service_simple import NotificationService
    NOTIFICATION_SERVICE_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Error importando notification service: {e}")
    NOTIFICATION_SERVICE_AVAILABLE = False

bp = Blueprint('expense_notifications', __name__, url_prefix='/admin/expense-notifications')

@bp.route('/alive')
def alive():
    """Ruta de test sin autenticación ni dependencias"""
    return "<h1>✅ Blueprint VIVO!</h1><p>Esta ruta funciona sin @login_required</p>"

@bp.route('/test')
@login_required
def test():
    """Ruta de prueba simple"""
    try:
        # Test básico sin base de datos
        html = f"""
        <h1>✅ Blueprint de expense_notifications funciona!</h1>
        <p>URL: /admin/expense-notifications/test</p>
        <p>Usuario actual: {current_user.username}</p>
        <p>¿Es admin?: {current_user.can_access_admin()}</p>
        <p>Datetime: {datetime.now()}</p>
        <a href="/admin/expense-notifications/">Ir al index</a>
        """
        return html
    except Exception as e:
        return f"<h1>❌ Error en test: {e}</h1>"

@bp.route('/test-db')
@login_required  
def test_db():
    """Test de base de datos"""
    try:
        from models import Expense, User
        total_expenses = Expense.query.count()
        total_users = User.query.count()
        
        html = f"""
        <h1>✅ Test de Base de Datos</h1>
        <p>Total expensas: {total_expenses}</p>
        <p>Total usuarios: {total_users}</p>
        <a href="/admin/expense-notifications/">Ir al index</a>
        """
        return html
    except Exception as e:
        return f"<h1>❌ Error en test-db: {e}</h1>"

@bp.route('/')
@login_required
def index():
    """Panel principal de notificaciones de expensas - VERSION ULTRA SIMPLE"""
    try:
        print("🔍 DEBUG: Iniciando función index() - VERSION SIMPLE")
        
        # Test ultra básico - solo verificar permisos
        if not hasattr(current_user, 'can_access_admin'):
            return "❌ ERROR: Usuario no tiene método can_access_admin"
        
        if not current_user.can_access_admin():
            return "❌ ERROR: Usuario sin permisos de admin"
        
        print("✅ DEBUG: Usuario tiene permisos de admin")
        
        # No usar base de datos - solo valores estáticos
        stats = {
            'total_expenses': 25,
            'notifications_sent': 0,
            'pending_notifications': 25,
            'notification_rate': 0
        }
        
        recent_expenses = []  # Lista vacía
        
        print("🔍 DEBUG: Renderizando template de prueba...")
        return render_template('expense_notifications/test.html', 
                             stats=stats, 
                             recent_expenses=recent_expenses)
    
    except Exception as e:
        print(f"❌ DEBUG: Error general en index(): {e}")
        import traceback
        print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
        return f"<h1>❌ Error en index(): {e}</h1><pre>{traceback.format_exc()}</pre>"

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
