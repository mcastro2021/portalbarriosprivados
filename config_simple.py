"""
Configuración simplificada para evitar problemas de dependencias
"""

import os
from datetime import timedelta

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///barrio_cerrado.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ITEMS_PER_PAGE = 20
    
    # Configuración de seguridad
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Configuración de email (opcional)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Configuración de notificaciones
    NOTIFICATION_EMAIL_ENABLED = os.environ.get('NOTIFICATION_EMAIL_ENABLED', 'false').lower() == 'true'
    NOTIFICATION_WHATSAPP_ENABLED = os.environ.get('NOTIFICATION_WHATSAPP_ENABLED', 'false').lower() == 'true'
    
    # Configuración de servicios externos (opcional)
    MERCADOPAGO_ACCESS_TOKEN = os.environ.get('MERCADOPAGO_ACCESS_TOKEN')
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # Configuración de IA (opcional)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    
    # Configuración de Redis (opcional)
    REDIS_URL = os.environ.get('REDIS_URL')
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    ENV = 'production'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log a syslog en producción
        import logging
        from logging.handlers import SysLogHandler
        if not app.debug and not app.testing:
            if os.environ.get('LOGGING_TO_STDOUT'):
                stream_handler = logging.StreamHandler()
                stream_handler.setLevel(logging.INFO)
                app.logger.addHandler(stream_handler)
            else:
                if not app.logger.handlers:
                    syslog_handler = SysLogHandler()
                    syslog_handler.setLevel(logging.WARNING)
                    app.logger.addHandler(syslog_handler)

class TestingConfig(Config):
    """Configuración de testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
