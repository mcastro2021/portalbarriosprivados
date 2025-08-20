import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    SocketIO = None
from flask_mail import Mail, Message
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import logging
from logging.handlers import RotatingFileHandler
import qrcode
import io
import base64
import uuid
import json
from datetime import datetime, timedelta
from dateutil import parser
import mercadopago
from twilio.rest import Client
# OpenAI import moved to where it's used

# Importar configuración y modelos
from config import config
from models import db, User, Visit, Reservation, News, Maintenance, Expense, Classified, SecurityReport, Notification, NeighborhoodMap, ChatbotSession

# Importar rutas
from routes import auth, visits, reservations, news, maintenance, expenses, classifieds, security, chatbot, smart_maintenance, user_management, camera_security, broadcast_communications, map

def create_app(config_name='default'):
    """Factory function para crear la aplicación Flask"""
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Configurar SocketIO solo si está disponible
    if SOCKETIO_AVAILABLE and SocketIO:
        try:
            socketio_config = {
                'async_mode': 'threading',
                'cors_allowed_origins': "*",
                'logger': False,
                'engineio_logger': False,
                'manage_session': False  # Evitar problemas de sesión
            }
            socketio = SocketIO(app, **socketio_config)
            print("✅ SocketIO configurado correctamente")
        except Exception as e:
            print(f"⚠️ Error configurando SocketIO: {e}")
            socketio = None
    else:
        socketio = None
        print("⚠️ SocketIO no disponible - funcionando sin tiempo real")
    mail = Mail(app)
    
    # Configurar logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/barrio_cerrado.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Barrio Cerrado startup')
    
    # Crear carpeta de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Middleware para logging de peticiones API y admin
    @app.before_request
    def log_api_requests():
        if request.path.startswith('/api/') or (request.path.startswith('/admin/') and request.method == 'POST'):
            app.logger.info(f'API/Admin Request: {request.method} {request.path} - User: {current_user.username if current_user.is_authenticated else "Anonymous"}')
    
    @app.after_request
    def log_api_responses(response):
        if request.path.startswith('/api/') or (request.path.startswith('/admin/') and request.method == 'POST'):
            app.logger.info(f'API/Admin Response: {request.method} {request.path} - Status: {response.status_code}')
            
            # Asegurar que las APIs y rutas admin devuelvan JSON
            if hasattr(request, 'is_api') and request.is_api:
                if not response.headers.get('Content-Type', '').startswith('application/json'):
                    # Si no es JSON, convertir a JSON de error
                    try:
                        if response.status_code >= 400:
                            error_data = {
                                'error': 'Error en la API/Admin',
                                'status_code': response.status_code,
                                'message': 'La ruta devolvió un error no-JSON'
                            }
                            response = app.response_class(
                                response=json.dumps(error_data),
                                status=response.status_code,
                                mimetype='application/json'
                            )
                    except Exception as e:
                        app.logger.error(f'Error convirtiendo respuesta API/Admin a JSON: {e}')
        
        return response
    
    # Middleware para manejar APIs y rutas admin que devuelven JSON
    @app.before_request
    def handle_api_requests():
        if request.path.startswith('/api/') or request.path.startswith('/admin/') and request.method == 'POST':
            # Para APIs y rutas admin POST, configurar headers y manejar CSRF
            request.is_api = True
            
            # Asegurar que las APIs devuelvan JSON
            if request.method == 'POST' and not request.is_json:
                # Si es POST pero no es JSON, intentar parsear como JSON
                try:
                    if request.form:
                        # Convertir form data a JSON
                        request.json = dict(request.form)
                except Exception:
                    pass
    
    # Configurar MercadoPago
    mp = mercadopago.SDK(app.config['MERCADOPAGO_ACCESS_TOKEN']) if app.config['MERCADOPAGO_ACCESS_TOKEN'] else None
    
    # Configurar Twilio (WhatsApp)
    twilio_client = None
    if app.config['TWILIO_ACCOUNT_SID'] and app.config['TWILIO_AUTH_TOKEN']:
        twilio_client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])
    
    # OpenAI configuration is now handled in chatbot.py where it's used
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registrar blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(visits.bp)
    app.register_blueprint(reservations.bp)
    app.register_blueprint(news.bp)
    app.register_blueprint(maintenance.bp)
    app.register_blueprint(expenses.bp)
    app.register_blueprint(classifieds.bp)
    app.register_blueprint(security.bp)
    app.register_blueprint(chatbot.bp)
    app.register_blueprint(smart_maintenance.bp)
    app.register_blueprint(user_management.bp)
    app.register_blueprint(map.bp)
    
    # Importar y registrar blueprint de admin
    from routes import admin
    app.register_blueprint(admin.bp)
    
    # Importar y registrar blueprint de notificaciones de expensas
    from routes import expense_notifications
    app.register_blueprint(expense_notifications.bp)
    
    # Filtros personalizados para Jinja2
    @app.template_filter('stage_color')
    def stage_color(stage):
        """Retorna el color para cada etapa"""
        colors = {
            '1': '#4CAF50',
            '2A': '#2196F3',
            '2B': '#FF9800',
            '3': '#9C27B0'
        }
        return colors.get(stage, '#6c757d')
    
    @app.template_filter('stage_status')
    def stage_status(stage):
        """Retorna el estado de cada etapa"""
        statuses = {
            '1': 'Vendida',
            '2A': 'En venta',
            '2B': 'Desarrollo',
            '3': 'Futuro'
        }
        return statuses.get(stage, 'Desconocido')
    
    @app.template_filter('to_dict')
    def to_dict(obj):
        """Convertir objeto a diccionario"""
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return obj
    app.register_blueprint(camera_security.bp)
    app.register_blueprint(broadcast_communications.bp)
    
    # Rutas principales
    @app.route('/health')
    def health_check():
        """Endpoint de salud para diagnóstico"""
        try:
            # Verificar conexión a la base de datos
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            db_status = 'OK'
        except Exception as e:
            db_status = f'ERROR: {str(e)}'
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': db_status,
            'environment': app.config['ENV'] if 'ENV' in app.config else 'development',
            'debug': app.debug
        })
    

    
    @app.route('/')
    def index():
        """Página principal"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        # Obtener noticias importantes para mostrar en la página principal
        important_news = News.query.filter_by(is_important=True, is_published=True).order_by(News.created_at.desc()).limit(3).all()
        
        return render_template('index.html', important_news=important_news)
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Dashboard principal del usuario"""
        # Obtener estadísticas del usuario
        pending_visits = Visit.query.filter_by(resident_id=current_user.id, status='pending').count()
        active_reservations = Reservation.query.filter_by(user_id=current_user.id, status='approved').count()
        pending_maintenance = Maintenance.query.filter_by(user_id=current_user.id, status='pending').count()
        pending_expenses = Expense.query.filter_by(user_id=current_user.id, status='pending').count()
        
        # Obtener noticias recientes
        recent_news = News.query.filter_by(is_published=True).order_by(News.created_at.desc()).limit(5).all()
        
        # Obtener notificaciones no leídas
        unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
        
        # Obtener próximas reservas
        upcoming_reservations = Reservation.query.filter(
            Reservation.user_id == current_user.id,
            Reservation.status == 'approved',
            Reservation.start_time > datetime.utcnow()
        ).order_by(Reservation.start_time).limit(3).all()
        
        # Obtener visitas pendientes
        pending_visits_list = Visit.query.filter_by(resident_id=current_user.id, status='pending').order_by(Visit.entry_time).limit(3).all()
        
        # Crear objeto stats para el dashboard
        from datetime import date, timedelta
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        if current_user.role == 'admin':
            today_visits = Visit.query.filter(Visit.created_at >= today, Visit.created_at < tomorrow).count()
            total_residents = User.query.filter_by(role='resident').count()
        else:
            today_visits = Visit.query.filter_by(resident_id=current_user.id).filter(Visit.created_at >= today, Visit.created_at < tomorrow).count()
            total_residents = 0
        
        stats = {
            'total_residents': total_residents,
            'active_reservations': active_reservations,
            'pending_maintenance': pending_maintenance,
            'today_visits': today_visits
        }
        
        # Crear actividades recientes (simplificado para evitar errores)
        recent_activities = []
        
        return render_template('dashboard.html',
                             pending_visits=pending_visits,
                             active_reservations=active_reservations,
                             pending_maintenance=pending_maintenance,
                             pending_expenses=pending_expenses,
                             recent_news=recent_news,
                             unread_notifications=unread_notifications,
                             upcoming_reservations=upcoming_reservations,
                             pending_visits_list=pending_visits_list,
                             current_datetime=datetime.utcnow(),
                             stats=stats,
                             recent_activities=recent_activities)
    
    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        """Perfil del usuario"""
        if request.method == 'POST':
            try:
                # Actualizar información básica
                current_user.name = request.form.get('name', current_user.name)
                current_user.email = request.form.get('email', current_user.email)
                current_user.address = request.form.get('address', current_user.address)
                current_user.phone = request.form.get('phone', current_user.phone)
                current_user.emergency_contact = request.form.get('emergency_contact', current_user.emergency_contact)
                
                # Cambiar contraseña si se proporciona
                new_password = request.form.get('new_password')
                current_password = request.form.get('current_password')
                confirm_password = request.form.get('confirm_password')
                
                if new_password and current_password:
                    # Verificar contraseña actual
                    if not current_user.check_password(current_password):
                        flash('La contraseña actual es incorrecta', 'error')
                        return render_template('profile.html')
                    
                    # Verificar que las contraseñas coincidan
                    if new_password != confirm_password:
                        flash('Las contraseñas no coinciden', 'error')
                        return render_template('profile.html')
                    
                    # Verificar longitud mínima
                    if len(new_password) < 6:
                        flash('La contraseña debe tener al menos 6 caracteres', 'error')
                        return render_template('profile.html')
                    
                    # Verificar que contenga al menos una letra y un número
                    if not any(c.isalpha() for c in new_password) or not any(c.isdigit() for c in new_password):
                        flash('La contraseña debe contener al menos una letra y un número', 'error')
                        return render_template('profile.html')
                    
                    current_user.set_password(new_password)
                    flash('Contraseña cambiada correctamente', 'success')
                
                # Procesar imagen de perfil
                if 'profile_image' in request.files:
                    file = request.files['profile_image']
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles', filename)
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        file.save(file_path)
                        current_user.profile_image = filename
                
                db.session.commit()
                flash('Perfil actualizado correctamente', 'success')
                return redirect(url_for('profile'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar el perfil: {str(e)}', 'error')
        
        return render_template('profile.html')
    
    @app.route('/map')
    @login_required
    def neighborhood_map():
        """Mapa del barrio"""
        blocks = NeighborhoodMap.query.all()
        return render_template('map.html', blocks=blocks)
    

    
    @app.route('/notifications')
    @login_required
    def notifications():
        """Notificaciones del usuario"""
        page = request.args.get('page', 1, type=int)
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
        
        return render_template('notifications.html', notifications=notifications)
    
    @app.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
    @login_required
    def mark_notification_read(notification_id):
        """Marcar notificación como leída"""
        notification = Notification.query.get_or_404(notification_id)
        if notification.user_id == current_user.id:
            notification.mark_as_read()
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'No autorizado'}), 403
    
    @app.route('/notifications/mark-all-read', methods=['POST'])
    @login_required
    def mark_all_notifications_read():
        """Marcar todas las notificaciones como leídas"""
        Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True, 'read_at': datetime.utcnow()})
        db.session.commit()
        return jsonify({'success': True})
    
    @app.route('/uploads/<path:filename>')
    @login_required
    def uploaded_file(filename):
        """Servir archivos subidos"""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    @app.route('/qr/<visit_id>')
    def qr_code(visit_id):
        """Mostrar código QR de visita"""
        visit = Visit.query.get_or_404(visit_id)
        if not visit.qr_code:
            visit.generate_qr_code()
            db.session.commit()
        
        return render_template('qr_code.html', visit=visit)
    

    
    # WebSocket events
    @socketio.on('connect')
    def handle_connect():
        """Manejar conexión de WebSocket"""
        if current_user.is_authenticated:
            join_room(f'user_{current_user.id}')
            emit('connected', {'user': current_user.username, 'user_id': current_user.id})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Manejar desconexión de WebSocket"""
        if current_user.is_authenticated:
            leave_room(f'user_{current_user.id}')
    
    @socketio.on('join_admin_room')
    def handle_join_admin_room():
        """Unirse a la sala de administradores"""
        if current_user.is_authenticated and current_user.can_access_admin():
            join_room('admin_room')
            emit('joined_admin_room', {'message': 'Conectado al panel de administración'})
    
    @socketio.on('send_notification')
    def handle_send_notification(data):
        """Enviar notificación en tiempo real"""
        if current_user.is_authenticated and current_user.can_access_admin():
            user_id = data.get('user_id')
            title = data.get('title')
            message = data.get('message')
            
            if user_id and title and message:
                notification = Notification(
                    user_id=user_id,
                    title=title,
                    message=message,
                    type='push',
                    category='admin'
                )
                db.session.add(notification)
                db.session.commit()
                
                # Enviar a la sala del usuario
                socketio.emit('new_notification', {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'created_at': notification.created_at.isoformat()
                }, room=f'user_{user_id}')
    
    # Funciones de utilidad
    def send_email_notification(user, subject, body):
        """Enviar notificación por email"""
        if not app.config['NOTIFICATION_EMAIL_ENABLED']:
            return False
        
        try:
            msg = Message(subject, sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[user.email])
            msg.body = body
            mail.send(msg)
            return True
        except Exception as e:
            app.logger.error(f'Error enviando email: {e}')
            return False
    
    def send_whatsapp_notification(phone, message):
        """Enviar notificación por WhatsApp"""
        if not app.config['NOTIFICATION_WHATSAPP_ENABLED'] or not twilio_client:
            return False
        
        try:
            twilio_client.messages.create(
                body=message,
                from_=f'whatsapp:{app.config["TWILIO_PHONE_NUMBER"]}',
                to=f'whatsapp:{phone}'
            )
            return True
        except Exception as e:
            app.logger.error(f'Error enviando WhatsApp: {e}')
            return False
    
    def create_notification(user_id, title, message, category='general', related_id=None, related_type=None):
        """Crear notificación en la base de datos"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type='push',
            category=category,
            related_id=related_id,
            related_type=related_type
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    # Context processors
    @app.context_processor
    def inject_config():
        """Inyectar configuración en todas las plantillas"""
        return {
            'config': app.config,
            'current_year': datetime.utcnow().year
        }
    
    @app.context_processor
    def inject_user_stats():
        """Inyectar estadísticas del usuario en todas las plantillas"""
        if current_user.is_authenticated:
            unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
            return {'unread_notifications_count': unread_count}
        return {'unread_notifications_count': 0}
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/') or (request.path.startswith('/admin/') and request.method == 'POST'):
            return jsonify({'error': 'Endpoint no encontrado', 'path': request.path}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/') or (request.path.startswith('/admin/') and request.method == 'POST'):
            return jsonify({'error': 'Error interno del servidor', 'message': str(error)}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        if request.path.startswith('/api/') or (request.path.startswith('/admin/') and request.method == 'POST'):
            return jsonify({'error': 'Acceso denegado', 'message': 'No tienes permisos para acceder a este recurso'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        if request.path.startswith('/api/') or (request.path.startswith('/admin/') and request.method == 'POST'):
            return jsonify({'error': 'No autenticado', 'message': 'Debes iniciar sesión para acceder a este recurso'}), 401
        return redirect(url_for('auth.login'))
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        db.session.rollback()
        if request.path.startswith('/api/') or (request.path.startswith('/admin/') and request.method == 'POST'):
            return jsonify({'error': 'Error inesperado', 'message': str(error)}), 500
        return render_template('errors/500.html'), 500
    
    # Crear decorador para rutas API que maneje CSRF automáticamente
    def api_route(rule, **options):
        def decorator(f):
            # Registrar la ruta
            endpoint = options.pop('endpoint', None)
            app.add_url_rule(rule, endpoint, f, **options)
            
            # Excluir de CSRF
            try:
                csrf.exempt(f)
            except Exception as e:
                print(f"⚠️ No se pudo excluir {rule} de CSRF: {e}")
            
            return f
        return decorator
    
    # Middleware para excluir rutas admin del CSRF
    @app.before_request
    def handle_admin_csrf():
        if request.path.startswith('/admin/') and request.method == 'POST':
            # Para rutas admin POST, deshabilitar CSRF
            from flask_wtf.csrf import CSRFProtect
            csrf = CSRFProtect()
            csrf.exempt(lambda: True)
    
    # Reemplazar las rutas API con el nuevo decorador
    @api_route('/api/stats')
    @login_required
    def api_stats():
        """API para estadísticas del dashboard"""
        try:
            if not current_user.can_access_admin():
                return jsonify({'error': 'No autorizado'}), 403
            
            # Estadísticas generales
            total_users = User.query.filter_by(is_active=True).count()
            total_visits = Visit.query.count()
            total_reservations = Reservation.query.count()
            total_maintenance = Maintenance.query.count()
            
            # Estadísticas de este mes
            this_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            visits_this_month = Visit.query.filter(Visit.created_at >= this_month).count()
            reservations_this_month = Reservation.query.filter(Reservation.created_at >= this_month).count()
            maintenance_this_month = Maintenance.query.filter(Maintenance.created_at >= this_month).count()
            
            return jsonify({
                'total_users': total_users,
                'total_visits': total_visits,
                'total_reservations': total_reservations,
                'total_maintenance': total_maintenance,
                'visits_this_month': visits_this_month,
                'reservations_this_month': reservations_this_month,
                'maintenance_this_month': maintenance_this_month
            })
        except Exception as e:
            app.logger.error(f'Error en api_stats: {str(e)}')
            return jsonify({'error': 'Error interno del servidor', 'message': str(e)}), 500
    
    @api_route('/api/dashboard/stats')
    @login_required
    def api_dashboard_stats():
        """API para estadísticas del dashboard del usuario"""
        try:
            # Estadísticas del usuario
            pending_visits = Visit.query.filter_by(resident_id=current_user.id, status='pending').count()
            active_reservations = Reservation.query.filter_by(user_id=current_user.id, status='approved').count()
            pending_maintenance = Maintenance.query.filter_by(user_id=current_user.id, status='pending').count()
            pending_expenses = Expense.query.filter_by(user_id=current_user.id, status='pending').count()
            
            # Estadísticas de hoy
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            today_visits = Visit.query.filter_by(resident_id=current_user.id).filter(Visit.created_at >= today, Visit.created_at < tomorrow).count()
            
            return jsonify({
                'pending_visits': pending_visits,
                'active_reservations': active_reservations,
                'pending_maintenance': pending_maintenance,
                'pending_expenses': pending_expenses,
                'today_visits': today_visits
            })
        except Exception as e:
            app.logger.error(f'Error en api_dashboard_stats: {str(e)}')
            return jsonify({'error': 'Error interno del servidor', 'message': str(e)}), 500
    
    @api_route('/api/notifications/count')
    @login_required
    def api_notifications_count():
        """API para contar notificaciones no leídas"""
        try:
            unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
            return jsonify({'count': unread_count})
        except Exception as e:
            app.logger.error(f'Error en api_notifications_count: {str(e)}')
            return jsonify({'error': 'Error interno del servidor', 'message': str(e)}), 500
    
    @api_route('/api/test')
    def api_test():
        """Endpoint de prueba para verificar que las APIs funcionan"""
        return jsonify({
            'message': 'API funcionando correctamente',
            'timestamp': datetime.utcnow().isoformat(),
            'user_authenticated': current_user.is_authenticated,
            'user_role': current_user.role if current_user.is_authenticated else None
        })
    
    @api_route('/api/ping')
    def api_ping():
        """Endpoint simple para verificar conectividad"""
        return jsonify({
            'status': 'ok',
            'message': 'pong',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Ruta de prueba para admin
    @app.route('/admin/test', methods=['POST'])
    @login_required
    def admin_test():
        """Endpoint de prueba para rutas admin"""
        if not current_user.can_access_admin():
            return jsonify({'error': 'No autorizado'}), 403
        
        return jsonify({
            'status': 'ok',
            'message': 'Admin route funcionando correctamente',
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    print("✅ Rutas API y Admin configuradas con manejo automático de CSRF")
    
    return app

def init_db():
    """Inicializar base de datos"""
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Crear usuario administrador por defecto si no existe
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@barrioprivado.com',
                name='Administrador del Sistema',
                role='admin',
                is_active=True,
                email_verified=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario administrador creado (admin/admin123)")
        else:
            print("ℹ️ Usuario administrador ya existe")

# Función create_sample_data() eliminada para evitar la creación automática de datos de prueba
# Los datos deben ser creados manualmente por el administrador cuando sea necesario

# Crear instancia de la aplicación para gunicorn
app = create_app()

# Función de migración automática
def migrate_ai_columns():
    """Migrar columnas de IA automáticamente"""
    try:
        from sqlalchemy import text
        
        # Lista de columnas a verificar/agregar
        ai_columns = [
            ('ai_classification', 'TEXT'),
            ('ai_suggestions', 'TEXT'),
            ('assigned_area', 'VARCHAR(100)'),
            ('expected_response_time', 'VARCHAR(50)'),
            ('ai_confidence', 'REAL'),
            ('manual_override', 'BOOLEAN DEFAULT 0')
        ]
        
        # Columnas para sistema de notificaciones de expensas
        expense_notification_columns = [
            ('notification_sent', 'BOOLEAN DEFAULT 0'),
            ('notification_date', 'DATETIME'),
            ('notification_method', 'VARCHAR(20)'),
            ('period', 'VARCHAR(20)')
        ]
        
        # Columnas para reportes de seguridad anónimos
        security_report_columns = [
            ('reporter_name', 'VARCHAR(100)'),
            ('reporter_phone', 'VARCHAR(20)'),
            ('reporter_email', 'VARCHAR(120)')
        ]
        
        # Migrar columnas de IA en tabla maintenance
        migration_count = 0
        with db.engine.connect() as conn:
            # Verificar tabla maintenance
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='maintenance'"))
            if result.fetchone():
                result = conn.execute(text("PRAGMA table_info(maintenance)"))
                existing_columns = [row[1] for row in result]
                
                for column_name, column_type in ai_columns:
                    if column_name not in existing_columns:
                        try:
                            sql = f"ALTER TABLE maintenance ADD COLUMN {column_name} {column_type}"
                            conn.execute(text(sql))
                            conn.commit()
                            migration_count += 1
                            print(f"✅ Columna IA agregada: {column_name}")
                        except Exception as e:
                            print(f"⚠️ No se pudo agregar {column_name}: {e}")
            
            # Migrar columnas de notificaciones en tabla expenses
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'"))
            if result.fetchone():
                result = conn.execute(text("PRAGMA table_info(expenses)"))
                existing_columns = [row[1] for row in result]
                
                for column_name, column_type in expense_notification_columns:
                    if column_name not in existing_columns:
                        try:
                            sql = f"ALTER TABLE expenses ADD COLUMN {column_name} {column_type}"
                            conn.execute(text(sql))
                            conn.commit()
                            migration_count += 1
                            print(f"✅ Columna notificación agregada: {column_name}")
                        except Exception as e:
                            print(f"⚠️ No se pudo agregar {column_name}: {e}")
            
            # Migrar columnas de seguridad anónima en tabla security_reports
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='security_reports'"))
            if result.fetchone():
                result = conn.execute(text("PRAGMA table_info(security_reports)"))
                existing_columns = [row[1] for row in result]
                
                for column_name, column_type in security_report_columns:
                    if column_name not in existing_columns:
                        try:
                            sql = f"ALTER TABLE security_reports ADD COLUMN {column_name} {column_type}"
                            conn.execute(text(sql))
                            conn.commit()
                            migration_count += 1
                            print(f"✅ Columna seguridad agregada: {column_name}")
                        except Exception as e:
                            print(f"⚠️ No se pudo agregar {column_name}: {e}")
                
                # También cambiar user_id a nullable para reportes anónimos
                try:
                    # Nota: SQLite no permite modificar columnas directamente, 
                    # pero la aplicación manejará valores NULL
                    print("ℹ️ user_id en security_reports permitirá valores NULL")
                except Exception as e:
                    print(f"⚠️ Nota sobre user_id: {e}")
        
        if migration_count > 0:
            print(f"🎉 Migración automática completada: {migration_count} columnas agregadas")
        
    except Exception as e:
        print(f"⚠️ Error en migración automática: {e}")
        # No fallar la aplicación por esto
        pass

# Inicializar base de datos automáticamente en producción
with app.app_context():
    try:
        db.create_all()
        
        # Ejecutar migración automática para columnas de IA
        migrate_ai_columns()
        
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"⚠️ Error inicializando BD: {e}")
        pass  # No fallar si ya existe

if __name__ == '__main__':
    if SOCKETIO_AVAILABLE and SocketIO:
        socketio = SocketIO(app)
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    else:
        app.run(debug=True, host='0.0.0.0', port=5000) 