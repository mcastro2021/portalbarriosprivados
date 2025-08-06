import os
from datetime import timedelta

class Config:
    """Configuración base de la aplicación"""
    
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///barrio_cerrado.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de archivos
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    # Configuración de email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Configuración de MercadoPago
    MERCADOPAGO_ACCESS_TOKEN = os.environ.get('MERCADOPAGO_ACCESS_TOKEN')
    MERCADOPAGO_PUBLIC_KEY = os.environ.get('MERCADOPAGO_PUBLIC_KEY')
    
    # Configuración de WhatsApp (Twilio)
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # Configuración de OpenAI (Chatbot)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Configuración de Redis (para Celery y cache)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    
    # Configuración de seguridad
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Configuración de paginación
    ITEMS_PER_PAGE = 10
    
    # Configuración de notificaciones
    NOTIFICATION_EMAIL_ENABLED = os.environ.get('NOTIFICATION_EMAIL_ENABLED', 'True').lower() == 'true'
    NOTIFICATION_WHATSAPP_ENABLED = os.environ.get('NOTIFICATION_WHATSAPP_ENABLED', 'False').lower() == 'true'
    NOTIFICATION_PUSH_ENABLED = os.environ.get('NOTIFICATION_PUSH_ENABLED', 'True').lower() == 'true'
    
    # Configuración del barrio
    BARRIO_NAME = os.environ.get('BARRIO_NAME', 'Barrio Privado')
    BARRIO_ADDRESS = os.environ.get('BARRIO_ADDRESS', 'Dirección del Barrio')
    BARRIO_PHONE = os.environ.get('BARRIO_PHONE', '+54 9 11 1234-5678')
    BARRIO_EMAIL = os.environ.get('BARRIO_EMAIL', 'info@barrioprivado.com')
    
    # Configuración de espacios comunes
    COMMON_SPACES = {
        'quincho_1': {
            'name': 'Quincho Principal',
            'capacity': 50,
            'description': 'Quincho con parrilla y terraza',
            'price_per_hour': 0,
            'max_hours': 8,
            'advance_booking_days': 30
        },
        'quincho_2': {
            'name': 'Quincho Pequeño',
            'capacity': 20,
            'description': 'Quincho ideal para reuniones íntimas',
            'price_per_hour': 0,
            'max_hours': 6,
            'advance_booking_days': 30
        },
        'sum': {
            'name': 'SUM (Salón de Usos Múltiples)',
            'capacity': 100,
            'description': 'Salón para eventos grandes',
            'price_per_hour': 0,
            'max_hours': 12,
            'advance_booking_days': 60
        },
        'cancha_futbol': {
            'name': 'Cancha de Fútbol',
            'capacity': 22,
            'description': 'Cancha de fútbol 11 con iluminación',
            'price_per_hour': 0,
            'max_hours': 4,
            'advance_booking_days': 7
        },
        'cancha_tenis': {
            'name': 'Cancha de Tenis',
            'capacity': 4,
            'description': 'Cancha de tenis con superficie profesional',
            'price_per_hour': 0,
            'max_hours': 2,
            'advance_booking_days': 7
        },
        'piscina': {
            'name': 'Piscina',
            'capacity': 30,
            'description': 'Piscina con solárium',
            'price_per_hour': 0,
            'max_hours': 6,
            'advance_booking_days': 7
        },
        'coworking': {
            'name': 'Espacio Coworking',
            'capacity': 15,
            'description': 'Sala de trabajo compartido',
            'price_per_hour': 0,
            'max_hours': 8,
            'advance_booking_days': 1
        }
    }
    
    # Configuración de categorías de noticias
    NEWS_CATEGORIES = [
        'general',
        'mantenimiento',
        'seguridad',
        'eventos',
        'obras',
        'cortes',
        'emergencias',
        'anuncios'
    ]
    
    # Configuración de categorías de clasificados
    CLASSIFIED_CATEGORIES = [
        'compra_venta',
        'servicios',
        'eventos',
        'alquiler',
        'empleo',
        'mascotas',
        'otros'
    ]
    
    # Configuración de prioridades de mantenimiento
    MAINTENANCE_PRIORITIES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente')
    ]
    
    # Configuración de estados de mantenimiento
    MAINTENANCE_STATUSES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado')
    ]

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    
    @classmethod
    def init_app(cls, app):
        pass

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = True
    
    # Configuración de base de datos para producción
    @classmethod
    def init_app(cls, app):
        # Configuración específica para producción
        import logging
        from logging.handlers import RotatingFileHandler
        
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

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    
    @classmethod
    def init_app(cls, app):
        pass

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 