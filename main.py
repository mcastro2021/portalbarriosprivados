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
# Importar dependencias opcionales
try:
    import mercadopago
    MERCADOPAGO_AVAILABLE = True
except ImportError:
    MERCADOPAGO_AVAILABLE = False
    mercadopago = None

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None

# OpenAI import moved to where it's used

# Importar configuración y modelos
try:
    from config import config
    print("✅ Configuración principal importada")
except ImportError:
    try:
        from config_simple import config
        print("✅ Configuración simplificada importada")
    except ImportError:
        print("⚠️ No se pudo importar configuración")
        # Configuración mínima de emergencia
        class EmergencyConfig:
            SECRET_KEY = 'emergency-secret-key'
            SQLALCHEMY_DATABASE_URI = 'sqlite:///barrio_cerrado.db'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            UPLOAD_FOLDER = 'uploads'
            DEBUG = False
            ENV = 'production'
            
            @staticmethod
            def init_app(app):
                pass
        
        config = {
            'development': EmergencyConfig,
            'production': EmergencyConfig,
            'testing': EmergencyConfig,
            'default': EmergencyConfig
        }
from models import db, User, Visit, Reservation, News, Maintenance, Expense, Classified, SecurityReport, Notification, NeighborhoodMap, ChatbotSession

# Inicializar login_manager
login_manager = LoginManager()

# Importar rutas de manera segura
try:
    from routes import auth
    print("✅ Ruta auth importada")
except ImportError as e:
    print(f"⚠️ No se pudo importar auth: {e}")
    auth = None

try:
    from routes import visits, reservations, news, maintenance, expenses, classifieds, security, chatbot, smart_maintenance, user_management, camera_security, broadcast_communications, map
    print("✅ Rutas adicionales importadas")
except ImportError as e:
    print(f"⚠️ No se pudieron importar algunas rutas: {e}")
    visits = reservations = news = maintenance = expenses = classifieds = security = chatbot = smart_maintenance = user_management = camera_security = broadcast_communications = map = None

# Importar nuevas mejoras de manera segura
try:
    from security import security_manager
    print("✅ Security manager importado")
except ImportError as e:
    print(f"⚠️ No se pudo importar security_manager: {e}")
    security_manager = None

try:
    from api.v1 import api_v1
    print("✅ API v1 importada")
except ImportError as e:
    print(f"⚠️ No se pudo importar api_v1: {e}")
    api_v1 = None

def ensure_2fa_columns():
    """Asegurar que las columnas de 2FA existan en la base de datos"""
    try:
        from sqlalchemy import text
        
        # Verificar qué columnas ya existen
        result = db.session.execute(text("PRAGMA table_info(users)"))
        existing_columns = [row[1] for row in result.fetchall()]
        
        # Columnas de 2FA que deben existir
        required_columns = [
            'two_factor_enabled',
            'two_factor_secret', 
            'two_factor_enabled_at',
            'two_factor_backup_codes'
        ]
        
        # Agregar columnas faltantes
        for column_name in required_columns:
            if column_name not in existing_columns:
                print(f"➕ Agregando columna faltante: {column_name}")
                
                if column_name == 'two_factor_enabled':
                    sql = "ALTER TABLE users ADD COLUMN two_factor_enabled BOOLEAN DEFAULT FALSE"
                elif column_name == 'two_factor_secret':
                    sql = "ALTER TABLE users ADD COLUMN two_factor_secret VARCHAR(32)"
                elif column_name == 'two_factor_enabled_at':
                    sql = "ALTER TABLE users ADD COLUMN two_factor_enabled_at TIMESTAMP"
                elif column_name == 'two_factor_backup_codes':
                    sql = "ALTER TABLE users ADD COLUMN two_factor_backup_codes TEXT"
                
                db.session.execute(text(sql))
                print(f"✅ Columna {column_name} agregada exitosamente")
        
        db.session.commit()
        print("✅ Verificación de columnas 2FA completada")
        
    except Exception as e:
        print(f"⚠️ Error verificando columnas 2FA: {e}")
        db.session.rollback()

def create_app(config_name=None):
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    try:
        app.config.from_object(config[config_name])
    except KeyError:
        print(f"⚠️ Configuración '{config_name}' no encontrada, usando desarrollo")
        app.config.from_object(config['development'])
    
    # Inicializar extensiones básicas
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configurar login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registrar blueprints de manera segura
    try:
        from routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp)
        print("✅ Blueprint auth registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar auth blueprint: {e}")
    
    try:
        from routes.main import bp as main_bp
        app.register_blueprint(main_bp)
        print("✅ Blueprint main registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar main blueprint: {e}")
    
    try:
        from routes.admin import bp as admin_bp
        app.register_blueprint(admin_bp)
        print("✅ Blueprint admin registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar admin blueprint: {e}")
    
    try:
        from routes.api import bp as api_bp
        app.register_blueprint(api_bp)
        print("✅ Blueprint api registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar api blueprint: {e}")
    
    # Registrar blueprints de rutas principales
    try:
        from routes.visits import bp as visits_bp
        app.register_blueprint(visits_bp)
        print("✅ Blueprint visits registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar visits blueprint: {e}")
    
    try:
        from routes.reservations import bp as reservations_bp
        app.register_blueprint(reservations_bp)
        print("✅ Blueprint reservations registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar reservations blueprint: {e}")
    
    try:
        from routes.news import bp as news_bp
        app.register_blueprint(news_bp)
        print("✅ Blueprint news registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar news blueprint: {e}")
    
    try:
        from routes.maintenance import bp as maintenance_bp
        app.register_blueprint(maintenance_bp)
        print("✅ Blueprint maintenance registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar maintenance blueprint: {e}")
    
    try:
        from routes.expenses import bp as expenses_bp
        app.register_blueprint(expenses_bp)
        print("✅ Blueprint expenses registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar expenses blueprint: {e}")
    
    try:
        from routes.classifieds import bp as classifieds_bp
        app.register_blueprint(classifieds_bp)
        print("✅ Blueprint classifieds registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar classifieds blueprint: {e}")
    
    try:
        from routes.security import bp as security_bp
        app.register_blueprint(security_bp)
        print("✅ Blueprint security registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar security blueprint: {e}")
    
    try:
        from routes.map import bp as map_bp
        app.register_blueprint(map_bp)
        print("✅ Blueprint map registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar map blueprint: {e}")
    
    # Registrar blueprints adicionales
    try:
        from routes.user_management import bp as user_management_bp
        app.register_blueprint(user_management_bp)
        print("✅ Blueprint user_management registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar user_management blueprint: {e}")
    
    try:
        from routes.broadcast_communications import bp as broadcast_communications_bp
        app.register_blueprint(broadcast_communications_bp)
        print("✅ Blueprint broadcast_communications registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar broadcast_communications blueprint: {e}")
    
    try:
        from routes.expense_notifications import bp as expense_notifications_bp
        app.register_blueprint(expense_notifications_bp)
        print("✅ Blueprint expense_notifications registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar expense_notifications blueprint: {e}")
    
    try:
        from routes.chatbot import bp as chatbot_bp
        app.register_blueprint(chatbot_bp)
        print("✅ Blueprint chatbot registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar chatbot blueprint: {e}")
    
    try:
        from routes.camera_security import bp as camera_security_bp
        app.register_blueprint(camera_security_bp)
        print("✅ Blueprint camera_security registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar camera_security blueprint: {e}")
    
    try:
        from routes.smart_maintenance import bp as smart_maintenance_bp
        app.register_blueprint(smart_maintenance_bp)
        print("✅ Blueprint smart_maintenance registrado")
    except Exception as e:
        print(f"⚠️ No se pudo registrar smart_maintenance blueprint: {e}")
    
    # Intentar registrar blueprints de API v1 si existen
    try:
        from api.v1 import api_v1
        app.register_blueprint(api_v1, url_prefix='/api/v1')
        print("✅ API v1 registrada exitosamente")
    except Exception as e:
        print(f"⚠️ No se pudo registrar API v1: {e}")
    
    # Intentar inicializar security manager si existe
    try:
        from security import SecurityManager
        security_manager = SecurityManager(app)
        app.security_manager = security_manager
        print("✅ Security manager inicializado exitosamente")
    except Exception as e:
        print(f"⚠️ No se pudo inicializar security manager: {e}")
    
    # Verificar y migrar columnas de 2FA al crear la aplicación
    with app.app_context():
        try:
            ensure_2fa_columns()
        except Exception as e:
            print(f"⚠️ Error en migración de columnas 2FA: {e}")
    
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
# Usar configuración de producción en Render
config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name)

# Asegurar que socketio esté disponible para gunicorn
if SOCKETIO_AVAILABLE and SocketIO:
    try:
        socketio_config = {
            'async_mode': 'threading',
            'cors_allowed_origins': "*",
            'logger': False,
            'engineio_logger': False,
            'manage_session': False
        }
        socketio = SocketIO(app, **socketio_config)
    except Exception as e:
        print(f"⚠️ Error configurando SocketIO para producción: {e}")
        socketio = None
else:
    socketio = None

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
