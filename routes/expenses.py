from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Expense, User
from datetime import datetime, timedelta
import mercadopago

bp = Blueprint('expenses', __name__, url_prefix='/expenses')

@bp.route('/')
@login_required
def index():
    """Mostrar expensas del usuario"""
    page = request.args.get('page', 1, type=int)
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    # Calcular estadísticas
    total_pending = Expense.query.filter_by(user_id=current_user.id, status='pending').count()
    total_paid = Expense.query.filter_by(user_id=current_user.id, status='paid').count()
    total_overdue = Expense.query.filter_by(user_id=current_user.id, status='overdue').count()
    
    return render_template('expenses/index.html', 
                         expenses=expenses,
                         total_pending=total_pending,
                         total_paid=total_paid,
                         total_overdue=total_overdue)

@bp.route('/pay/<int:expense_id>')
@login_required
def pay(expense_id):
    """Página de pago de expensa"""
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        flash('No tienes permiso para acceder a esta expensa', 'error')
        return redirect(url_for('expenses.index'))
    
    if expense.status != 'pending':
        flash('Esta expensa ya ha sido procesada', 'info')
        return redirect(url_for('expenses.index'))
    
    return render_template('expenses/payment.html', expense=expense)

@bp.route('/create_preference/<int:expense_id>', methods=['POST'])
@login_required
def create_preference(expense_id):
    """Crear preferencia de pago en MercadoPago"""
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        # Configurar MercadoPago (requiere configuración en variables de entorno)
        mp = mercadopago.SDK(current_app.config['MERCADOPAGO_ACCESS_TOKEN'])
        
        preference_data = {
            "items": [
                {
                    "title": f"Expensa {expense.get_month_display()}",
                    "quantity": 1,
                    "unit_price": float(expense.get_total_amount()),
                    "currency_id": "ARS"
                }
            ],
            "payer": {
                "name": current_user.name,
                "email": current_user.email
            },
            "back_urls": {
                "success": url_for('expenses.payment_success', expense_id=expense.id, _external=True),
                "failure": url_for('expenses.payment_failure', expense_id=expense.id, _external=True),
                "pending": url_for('expenses.payment_pending', expense_id=expense.id, _external=True)
            },
            "auto_return": "approved",
            "external_reference": str(expense.id)
        }
        
        preference_response = mp.preference().create(preference_data)
        preference = preference_response["response"]
        
        # Guardar ID de preferencia
        expense.mercadopago_preference_id = preference["id"]
        db.session.commit()
        
        return jsonify({
            'preference_id': preference["id"],
            'init_point': preference["init_point"]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/payment_success/<int:expense_id>')
@login_required
def payment_success(expense_id):
    """Página de éxito de pago"""
    expense = Expense.query.get_or_404(expense_id)
    return render_template('expenses/payment_success.html', expense=expense)

@bp.route('/payment_failure/<int:expense_id>')
@login_required
def payment_failure(expense_id):
    """Página de fallo de pago"""
    expense = Expense.query.get_or_404(expense_id)
    return render_template('expenses/payment_failure.html', expense=expense)

@bp.route('/payment_pending/<int:expense_id>')
@login_required
def payment_pending(expense_id):
    """Página de pago pendiente"""
    expense = Expense.query.get_or_404(expense_id)
    return render_template('expenses/payment_pending.html', expense=expense)

@bp.route('/webhook', methods=['POST'])
def webhook():
    """Webhook para notificaciones de MercadoPago"""
    try:
        data = request.get_json()
        
        if data.get('type') == 'payment':
            payment_id = data.get('data', {}).get('id')
            
            # Procesar notificación de pago
            # Aquí iría la lógica para actualizar el estado de la expensa
            
        return '', 200
        
    except Exception as e:
        return str(e), 500