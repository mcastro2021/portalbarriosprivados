import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
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
from routes import auth, visits, reservations, news, maintenance, expenses, classifieds, security, chatbot, smart_maintenance, user_management, camera_security, broadcast_communications

def create_app(config_name='default'):
    """Factory function para crear la aplicación Flask"""
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate = Migrate(app, db)
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
    
    # Importar y registrar blueprint de admin
    from routes import admin
    app.register_blueprint(admin.bp)
    
    # Importar y registrar blueprint de notificaciones de expensas
    from routes import expense_notifications
    app.register_blueprint(expense_notifications.bp)
    app.register_blueprint(camera_security.bp)
    app.register_blueprint(broadcast_communications.bp)
    
    # Rutas principales
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
                if new_password:
                    current_user.set_password(new_password)
                
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
    
    @app.route('/api/stats')
    @login_required
    def api_stats():
        """API para estadísticas del dashboard"""
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
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
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
            
            # Crear algunos datos de ejemplo
            create_sample_data()
            
            db.session.commit()
            print("Base de datos inicializada con usuario admin (admin/admin123)")

def create_sample_data():
    """Crear datos de ejemplo"""
    # Crear algunos usuarios de ejemplo
    users_data = [
        {
            'username': 'residente1',
            'email': 'residente1@barrioprivado.com',
            'name': 'Juan Pérez',
            'role': 'resident',
            'address': 'Manzana A, Casa 1',
            'phone': '+54 9 11 1234-5678'
        },
        {
            'username': 'seguridad1',
            'email': 'seguridad@barrioprivado.com',
            'name': 'Carlos Rodríguez',
            'role': 'security',
            'phone': '+54 9 11 8765-4321'
        },
        {
            'username': 'mantenimiento1',
            'email': 'mantenimiento@barrioprivado.com',
            'name': 'Roberto García',
            'role': 'maintenance',
            'phone': '+54 9 11 5555-1234'
        }
    ]
    
    for user_data in users_data:
        if not User.query.filter_by(username=user_data['username']).first():
            user = User(**user_data)
            user.set_password('password123')
            user.email_verified = True
            user.is_active = True
            db.session.add(user)
    
    # Crear algunas noticias de ejemplo
    news_data = [
        {
            'title': 'Bienvenidos al Portal del Barrio',
            'content': 'Este es el portal oficial de nuestro barrio cerrado. Aquí podrán gestionar visitas, reservar espacios, consultar expensas y mucho más.',
            'category': 'general',
            'is_important': True
        },
        {
            'title': 'Mantenimiento Programado - Piscina',
            'content': 'El próximo lunes se realizará mantenimiento en la piscina. Estará cerrada de 8:00 a 16:00 hs.',
            'category': 'mantenimiento',
            'is_important': True
        }
    ]
    
    admin = User.query.filter_by(username='admin').first()
    for news_item_data in news_data:
        if not News.query.filter_by(title=news_item_data['title']).first():
            news_item = News(**news_item_data, author_id=admin.id)
            db.session.add(news_item)
    
    # Crear datos del mapa del barrio
    map_data = [
        {
            'block_name': 'Manzana A',
            'street_name': 'Calle Principal',
            'block_number': 1,
            'total_houses': 12,
            'occupied_houses': 10,
            'description': 'Primera manzana del barrio'
        },
        {
            'block_name': 'Manzana B',
            'street_name': 'Calle Secundaria',
            'block_number': 2,
            'total_houses': 15,
            'occupied_houses': 12,
            'description': 'Segunda manzana del barrio'
        }
    ]
    
    for map_item_data in map_data:
        if not NeighborhoodMap.query.filter_by(block_name=map_item_data['block_name']).first():
            map_item = NeighborhoodMap(**map_item_data)
            map_item.set_coordinates(-34.6037, -58.3816)  # Coordenadas de ejemplo (Buenos Aires)
            db.session.add(map_item)

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
        
        # Crear usuario admin si no existe (para primera ejecución)
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
            print("✅ Usuario administrador creado automáticamente")
        
        # Crear usuario mcastro2025 si no existe (usuario permanente)
        mcastro = User.query.filter_by(username='mcastro2025').first()
        if not mcastro:
            mcastro = User(
                username='mcastro2025',
                email='mcastro2025@tejas4.com',
                name='Manuel Castro',
                role='admin',
                is_active=True,
                email_verified=True,
                address='Tejas 4 - Casa Principal'
            )
            mcastro.set_password('mcastro2025')
            db.session.add(mcastro)
            db.session.commit()
            print("✅ Usuario mcastro2025 creado automáticamente")
        else:
            # Asegurar que esté activo
            if not mcastro.is_active:
                mcastro.is_active = True
                db.session.commit()
                print("✅ Usuario mcastro2025 reactivado automáticamente")
    except Exception as e:
        print(f"⚠️ Error inicializando BD: {e}")
        pass  # No fallar si ya existe

if __name__ == '__main__':
    if SOCKETIO_AVAILABLE and SocketIO:
        socketio = SocketIO(app)
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    else:
        app.run(debug=True, host='0.0.0.0', port=5000) 