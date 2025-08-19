from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session
from flask_login import login_required, current_user
from models import db, Expense, User
from datetime import datetime, timedelta
import mercadopago
import requests
import json

bp = Blueprint('expenses', __name__, url_prefix='/expenses')

@bp.route('/')
@login_required
def index():
    """Página principal de expensas"""
    # Obtener expensas del usuario actual
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.created_at.desc()).all()
    
    # Configuración de API
    api_config = {
        'enabled': False,
        'base_url': 'https://propietarios.expensasonline.pro/api',
        'api_key': '',
        'username': '',
        'password': ''
    }
    
    return render_template('expenses/index.html', expenses=expenses, api_config=api_config)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Crear nueva expensa"""
    if request.method == 'POST':
        try:
            # Crear nueva expensa
            expense = Expense(
                user_id=current_user.id,
                description=request.form.get('description', ''),
                amount=float(request.form.get('amount', 0)),
                due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d') if request.form.get('due_date') else None,
                status='pending',
                month=request.form.get('month', ''),
                period=request.form.get('period', '')
            )
            
            db.session.add(expense)
            db.session.commit()
            
            flash('Expensa creada correctamente', 'success')
            return redirect(url_for('expenses.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la expensa: {str(e)}', 'error')
    
    return render_template('expenses/new.html')

@bp.route('/api-config', methods=['GET', 'POST'])
@login_required
def api_config():
    """Configuración de la API de expensasonline.pro"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('expenses.index'))
    
    if request.method == 'POST':
        try:
            # Guardar configuración de API
            api_config = {
                'enabled': request.form.get('api_enabled') == 'on',
                'base_url': request.form.get('api_base_url', 'https://propietarios.expensasonline.pro/api'),
                'api_key': request.form.get('api_key', ''),
                'username': request.form.get('api_username', ''),
                'password': request.form.get('api_password', '')
            }
            
            # Aquí podrías guardar la configuración en la base de datos
            # Por ahora, la guardamos en una variable de sesión
            session['expensasonline_config'] = api_config
            
            flash('Configuración de API guardada correctamente', 'success')
            return redirect(url_for('expenses.api_config'))
            
        except Exception as e:
            flash(f'Error al guardar la configuración: {str(e)}', 'error')
    
    # Obtener configuración actual
    api_config = session.get('expensasonline_config', {
        'enabled': False,
        'base_url': 'https://propietarios.expensasonline.pro/api',
        'api_key': '',
        'username': '',
        'password': ''
    })
    
    return render_template('expenses/api_config.html', api_config=api_config)

@bp.route('/sync', methods=['POST'])
@login_required
def sync_expenses():
    """Sincronizar expensas desde expensasonline.pro"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        api_config = session.get('expensasonline_config', {})
        
        if not api_config.get('enabled'):
            return jsonify({'error': 'API no está habilitada'}), 400
        
        # Intentar conectar con la API
        headers = {
            'Authorization': f'Bearer {api_config.get("api_key")}',
            'Content-Type': 'application/json'
        }
        
        # Datos de autenticación
        auth_data = {
            'username': api_config.get('username'),
            'password': api_config.get('password')
        }
        
        # Intentar autenticación
        auth_response = requests.post(
            f"{api_config.get('base_url')}/auth/login",
            json=auth_data,
            headers=headers,
            timeout=30
        )
        
        if auth_response.status_code != 200:
            return jsonify({
                'error': 'Error de autenticación con expensasonline.pro',
                'details': auth_response.text
            }), 400
        
        # Obtener token de autenticación
        auth_token = auth_response.json().get('token')
        
        if not auth_token:
            return jsonify({'error': 'No se pudo obtener el token de autenticación'}), 400
        
        # Actualizar headers con el token
        headers['Authorization'] = f'Bearer {auth_token}'
        
        # Obtener expensas
        expenses_response = requests.get(
            f"{api_config.get('base_url')}/expenses",
            headers=headers,
            timeout=30
        )
        
        if expenses_response.status_code != 200:
            return jsonify({
                'error': 'Error al obtener expensas de expensasonline.pro',
                'details': expenses_response.text
            }), 400
        
        expenses_data = expenses_response.json()
        
        # Procesar y guardar expensas
        synced_count = 0
        for expense_data in expenses_data.get('expenses', []):
            # Verificar si la expensa ya existe
            existing_expense = Expense.query.filter_by(
                external_id=expense_data.get('id'),
                user_id=current_user.id
            ).first()
            
            if not existing_expense:
                # Crear nueva expensa
                new_expense = Expense(
                    user_id=current_user.id,
                    description=expense_data.get('description', ''),
                    amount=expense_data.get('amount', 0),
                    month=expense_data.get('month', ''),
                    period=expense_data.get('period', ''),
                    due_date=datetime.strptime(expense_data.get('due_date'), '%Y-%m-%d') if expense_data.get('due_date') else None,
                    status=expense_data.get('status', 'pending'),
                    external_id=expense_data.get('id'),
                    external_data=json.dumps(expense_data)
                )
                db.session.add(new_expense)
                synced_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Se sincronizaron {synced_count} expensas correctamente',
            'synced_count': synced_count
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Error de conexión con expensasonline.pro',
            'details': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@bp.route('/test-connection', methods=['POST'])
@login_required
def test_connection():
    """Probar conexión con la API de expensasonline.pro"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        api_config = session.get('expensasonline_config', {})
        
        if not api_config.get('enabled'):
            return jsonify({'error': 'API no está habilitada'}), 400
        
        # Probar conexión básica
        test_response = requests.get(
            f"{api_config.get('base_url')}/health",
            timeout=10
        )
        
        if test_response.status_code == 200:
            return jsonify({
                'success': True,
                'message': 'Conexión exitosa con expensasonline.pro'
            })
        else:
            return jsonify({
                'error': 'No se pudo conectar con expensasonline.pro',
                'status_code': test_response.status_code
            }), 400
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Error de conexión',
            'details': str(e)
        }), 500

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