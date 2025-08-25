"""
Sistema de logging avanzado
Proporciona logging estructurado, contextual y configurable
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime
from flask import request, g, current_app
from flask_login import current_user
import traceback
import uuid
from functools import wraps

class StructuredFormatter(logging.Formatter):
    """Formateador para logs estructurados en JSON"""
    
    def format(self, record):
        """Formatear registro de log como JSON estructurado"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Agregar información de contexto si está disponible
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        if hasattr(record, 'user_role'):
            log_data['user_role'] = record.user_role
        
        if hasattr(record, 'ip_address'):
            log_data['ip_address'] = record.ip_address
        
        if hasattr(record, 'user_agent'):
            log_data['user_agent'] = record.user_agent
        
        if hasattr(record, 'endpoint'):
            log_data['endpoint'] = record.endpoint
        
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        
        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code
        
        if hasattr(record, 'response_time'):
            log_data['response_time'] = record.response_time
        
        if hasattr(record, 'extra_data'):
            log_data['extra_data'] = record.extra_data
        
        # Agregar información de excepción si está presente
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data, ensure_ascii=False)

class ContextFilter(logging.Filter):
    """Filtro para agregar contexto automáticamente a los logs"""
    
    def filter(self, record):
        """Agregar información de contexto al registro"""
        # Agregar ID de request único
        if not hasattr(g, 'request_id'):
            g.request_id = str(uuid.uuid4())
        record.request_id = g.request_id
        
        # Agregar información del usuario si está autenticado
        try:
            if current_user and current_user.is_authenticated:
                record.user_id = current_user.id
                record.user_role = current_user.role
            else:
                record.user_id = 'anonymous'
                record.user_role = 'anonymous'
        except:
            record.user_id = 'unknown'
            record.user_role = 'unknown'
        
        # Agregar información de la request si está disponible
        try:
            if request:
                record.ip_address = request.remote_addr
                record.user_agent = request.headers.get('User-Agent', 'unknown')
                record.endpoint = request.endpoint
                record.method = request.method
        except:
            pass
        
        return True

class LoggingService:
    """Servicio centralizado de logging"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar el servicio de logging con la aplicación Flask"""
        self.app = app
        
        # Configurar logging basado en el entorno
        log_level = app.config.get('LOG_LEVEL', 'INFO')
        log_format = app.config.get('LOG_FORMAT', 'structured')  # 'structured' o 'standard'
        
        # Crear directorio de logs si no existe
        log_dir = app.config.get('LOG_DIR', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Configurar logger principal
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Limpiar handlers existentes
        logger.handlers.clear()
        
        # Configurar handler para archivo
        self._setup_file_handler(logger, log_dir, log_format)
        
        # Configurar handler para consola
        self._setup_console_handler(logger, log_format)
        
        # Configurar handler para errores críticos
        self._setup_error_handler(logger, log_dir, log_format)
        
        # Configurar filtros de contexto
        context_filter = ContextFilter()
        for handler in logger.handlers:
            handler.addFilter(context_filter)
        
        # Configurar logging para Flask
        app.logger.handlers = logger.handlers
        app.logger.setLevel(logger.level)
        
        # Configurar logging para Werkzeug (servidor de desarrollo)
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.handlers = logger.handlers
        werkzeug_logger.setLevel(logging.WARNING)
        
        # Registrar middleware para logging de requests
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        print(f"✅ Logging configurado - Nivel: {log_level}, Formato: {log_format}")
    
    def _setup_file_handler(self, logger, log_dir, log_format):
        """Configurar handler para archivo con rotación"""
        file_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'app.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        
        if log_format == 'structured':
            file_handler.setFormatter(StructuredFormatter())
        else:
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            ))
        
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    
    def _setup_console_handler(self, logger, log_format):
        """Configurar handler para consola"""
        console_handler = logging.StreamHandler(sys.stdout)
        
        if log_format == 'structured':
            console_handler.setFormatter(StructuredFormatter())
        else:
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s'
            ))
        
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)
    
    def _setup_error_handler(self, logger, log_dir, log_format):
        """Configurar handler específico para errores"""
        error_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'errors.log'),
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        
        if log_format == 'structured':
            error_handler.setFormatter(StructuredFormatter())
        else:
            error_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s\n%(pathname)s:%(lineno)d'
            ))
        
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)
    
    def _before_request(self):
        """Middleware ejecutado antes de cada request"""
        g.start_time = datetime.utcnow()
        g.request_id = str(uuid.uuid4())
        
        # Log de inicio de request
        current_app.logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'extra_data': {
                    'query_params': dict(request.args),
                    'content_type': request.content_type,
                    'content_length': request.content_length
                }
            }
        )
    
    def _after_request(self, response):
        """Middleware ejecutado después de cada request"""
        if hasattr(g, 'start_time'):
            response_time = (datetime.utcnow() - g.start_time).total_seconds()
            
            # Log de finalización de request
            log_level = logging.INFO
            if response.status_code >= 400:
                log_level = logging.WARNING
            if response.status_code >= 500:
                log_level = logging.ERROR
            
            current_app.logger.log(
                log_level,
                f"Request completed: {request.method} {request.path} - {response.status_code}",
                extra={
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'extra_data': {
                        'response_size': response.content_length
                    }
                }
            )
        
        return response
    
    @staticmethod
    def log_user_action(action, details=None, level=logging.INFO):
        """Registrar acción de usuario"""
        try:
            user_info = 'anonymous'
            if current_user and current_user.is_authenticated:
                user_info = f"{current_user.username} (ID: {current_user.id})"
            
            current_app.logger.log(
                level,
                f"User action: {action}",
                extra={
                    'extra_data': {
                        'user': user_info,
                        'action': action,
                        'details': details or {}
                    }
                }
            )
        except Exception as e:
            current_app.logger.error(f"Error logging user action: {str(e)}")
    
    @staticmethod
    def log_security_event(event_type, description, severity='medium', details=None):
        """Registrar evento de seguridad"""
        try:
            current_app.logger.warning(
                f"Security event: {event_type} - {description}",
                extra={
                    'extra_data': {
                        'event_type': event_type,
                        'severity': severity,
                        'description': description,
                        'details': details or {},
                        'user_id': current_user.id if current_user and current_user.is_authenticated else 'anonymous',
                        'ip_address': request.remote_addr if request else 'unknown'
                    }
                }
            )
        except Exception as e:
            current_app.logger.error(f"Error logging security event: {str(e)}")
    
    @staticmethod
    def log_business_event(event_type, description, details=None):
        """Registrar evento de negocio"""
        try:
            current_app.logger.info(
                f"Business event: {event_type} - {description}",
                extra={
                    'extra_data': {
                        'event_type': event_type,
                        'description': description,
                        'details': details or {},
                        'user_id': current_user.id if current_user and current_user.is_authenticated else 'anonymous'
                    }
                }
            )
        except Exception as e:
            current_app.logger.error(f"Error logging business event: {str(e)}")
    
    @staticmethod
    def log_performance_metric(metric_name, value, unit='ms', details=None):
        """Registrar métrica de rendimiento"""
        try:
            current_app.logger.info(
                f"Performance metric: {metric_name} = {value}{unit}",
                extra={
                    'extra_data': {
                        'metric_name': metric_name,
                        'value': value,
                        'unit': unit,
                        'details': details or {}
                    }
                }
            )
        except Exception as e:
            current_app.logger.error(f"Error logging performance metric: {str(e)}")

# Decoradores para logging automático
def log_function_call(include_args=False, include_result=False):
    """Decorador para registrar llamadas a funciones"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = datetime.utcnow()
            
            # Log de inicio
            log_data = {'function': f.__name__}
            if include_args:
                log_data['args'] = str(args)
                log_data['kwargs'] = str(kwargs)
            
            current_app.logger.debug(
                f"Function call started: {f.__name__}",
                extra={'extra_data': log_data}
            )
            
            try:
                result = f(*args, **kwargs)
                
                # Log de éxito
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                log_data['execution_time'] = execution_time
                log_data['status'] = 'success'
                
                if include_result:
                    log_data['result'] = str(result)
                
                current_app.logger.debug(
                    f"Function call completed: {f.__name__}",
                    extra={'extra_data': log_data}
                )
                
                return result
                
            except Exception as e:
                # Log de error
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                log_data['execution_time'] = execution_time
                log_data['status'] = 'error'
                log_data['error'] = str(e)
                
                current_app.logger.error(
                    f"Function call failed: {f.__name__} - {str(e)}",
                    extra={'extra_data': log_data},
                    exc_info=True
                )
                
                raise
        
        return decorated_function
    return decorator

def log_user_action_decorator(action_name):
    """Decorador para registrar acciones de usuario automáticamente"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                
                # Registrar acción exitosa
                LoggingService.log_user_action(
                    action_name,
                    {'function': f.__name__, 'status': 'success'}
                )
                
                return result
                
            except Exception as e:
                # Registrar acción fallida
                LoggingService.log_user_action(
                    action_name,
                    {'function': f.__name__, 'status': 'error', 'error': str(e)},
                    level=logging.ERROR
                )
                
                raise
        
        return decorated_function
    return decorator

def log_security_action(action_type):
    """Decorador para registrar acciones de seguridad"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                
                # Registrar acción de seguridad
                LoggingService.log_security_event(
                    action_type,
                    f"Security action completed: {f.__name__}",
                    'low',
                    {'function': f.__name__, 'status': 'success'}
                )
                
                return result
                
            except Exception as e:
                # Registrar fallo de seguridad
                LoggingService.log_security_event(
                    action_type,
                    f"Security action failed: {f.__name__} - {str(e)}",
                    'high',
                    {'function': f.__name__, 'status': 'error', 'error': str(e)}
                )
                
                raise
        
        return decorated_function
    return decorator

# Funciones de utilidad para logging
def get_logger(name):
    """Obtener logger configurado"""
    return logging.getLogger(name)

def log_exception(logger, message, exc_info=True):
    """Registrar excepción con contexto completo"""
    logger.error(message, exc_info=exc_info, extra={
        'extra_data': {
            'user_id': current_user.id if current_user and current_user.is_authenticated else 'anonymous',
            'request_path': request.path if request else 'unknown',
            'request_method': request.method if request else 'unknown'
        }
    })
