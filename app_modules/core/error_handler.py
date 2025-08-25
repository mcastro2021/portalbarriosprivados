"""
Sistema centralizado de manejo de errores
Proporciona manejo consistente de errores en toda la aplicación
"""

from flask import jsonify, render_template, request, current_app
from werkzeug.exceptions import HTTPException
import traceback
import logging
from datetime import datetime
import json

class CustomError(Exception):
    """Clase base para errores personalizados"""
    def __init__(self, message, status_code=500, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

class ValidationError(CustomError):
    """Error de validación de datos"""
    def __init__(self, message, field=None, payload=None):
        super().__init__(message, 400, payload)
        self.field = field

class BusinessLogicError(CustomError):
    """Error de lógica de negocio"""
    def __init__(self, message, payload=None):
        super().__init__(message, 422, payload)

class SecurityError(CustomError):
    """Error de seguridad"""
    def __init__(self, message, payload=None):
        super().__init__(message, 403, payload)

class AuthenticationError(CustomError):
    """Error de autenticación"""
    def __init__(self, message, payload=None):
        super().__init__(message, 401, payload)

class NotFoundError(CustomError):
    """Error de recurso no encontrado"""
    def __init__(self, message, payload=None):
        super().__init__(message, 404, payload)

class RateLimitError(CustomError):
    """Error de límite de velocidad"""
    def __init__(self, message, payload=None):
        super().__init__(message, 429, payload)

class ErrorHandler:
    """Manejador centralizado de errores"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar el manejador de errores con la aplicación Flask"""
        self.app = app
        
        # Registrar manejadores de errores
        app.errorhandler(CustomError)(self.handle_custom_error)
        app.errorhandler(ValidationError)(self.handle_validation_error)
        app.errorhandler(BusinessLogicError)(self.handle_business_logic_error)
        app.errorhandler(SecurityError)(self.handle_security_error)
        app.errorhandler(AuthenticationError)(self.handle_authentication_error)
        app.errorhandler(NotFoundError)(self.handle_not_found_error)
        app.errorhandler(RateLimitError)(self.handle_rate_limit_error)
        
        # Manejadores para errores HTTP estándar
        app.errorhandler(400)(self.handle_bad_request)
        app.errorhandler(401)(self.handle_unauthorized)
        app.errorhandler(403)(self.handle_forbidden)
        app.errorhandler(404)(self.handle_not_found)
        app.errorhandler(405)(self.handle_method_not_allowed)
        app.errorhandler(429)(self.handle_too_many_requests)
        app.errorhandler(500)(self.handle_internal_server_error)
        app.errorhandler(502)(self.handle_bad_gateway)
        app.errorhandler(503)(self.handle_service_unavailable)
        
        # Manejador general para excepciones no capturadas
        app.errorhandler(Exception)(self.handle_generic_exception)
    
    def is_api_request(self):
        """Determinar si la petición es para API"""
        return (request.path.startswith('/api/') or 
                request.headers.get('Content-Type', '').startswith('application/json') or
                request.headers.get('Accept', '').startswith('application/json'))
    
    def log_error(self, error, error_type="ERROR", extra_data=None):
        """Registrar error en logs"""
        try:
            error_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'error_type': error_type,
                'message': str(error),
                'path': request.path if request else 'N/A',
                'method': request.method if request else 'N/A',
                'user_agent': request.headers.get('User-Agent', 'N/A') if request else 'N/A',
                'remote_addr': request.remote_addr if request else 'N/A',
                'user_id': getattr(request, 'user_id', 'N/A') if request else 'N/A'
            }
            
            if extra_data:
                error_data.update(extra_data)
            
            # Log estructurado
            current_app.logger.error(f"{error_type}: {json.dumps(error_data)}")
            
            # Log del traceback para errores críticos
            if error_type in ['CRITICAL', 'INTERNAL_ERROR']:
                current_app.logger.error(f"Traceback: {traceback.format_exc()}")
                
        except Exception as e:
            # Fallback logging si falla el logging estructurado
            current_app.logger.error(f"Error logging failed: {str(e)}")
            current_app.logger.error(f"Original error: {str(error)}")
    
    def create_error_response(self, error, status_code, error_type="error"):
        """Crear respuesta de error consistente"""
        if self.is_api_request():
            # Respuesta JSON para APIs
            response_data = {
                'success': False,
                'error': {
                    'type': error_type,
                    'message': str(error),
                    'status_code': status_code,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
            # Agregar detalles adicionales si están disponibles
            if hasattr(error, 'payload') and error.payload:
                response_data['error']['details'] = error.payload
            
            if hasattr(error, 'field') and error.field:
                response_data['error']['field'] = error.field
            
            return jsonify(response_data), status_code
        else:
            # Respuesta HTML para navegador
            return render_template(f'errors/{status_code}.html', 
                                 error=error, 
                                 error_type=error_type), status_code
    
    def handle_custom_error(self, error):
        """Manejar errores personalizados"""
        self.log_error(error, "CUSTOM_ERROR", {
            'status_code': error.status_code,
            'payload': error.payload
        })
        return self.create_error_response(error, error.status_code, "custom_error")
    
    def handle_validation_error(self, error):
        """Manejar errores de validación"""
        self.log_error(error, "VALIDATION_ERROR", {
            'field': getattr(error, 'field', None),
            'payload': error.payload
        })
        return self.create_error_response(error, 400, "validation_error")
    
    def handle_business_logic_error(self, error):
        """Manejar errores de lógica de negocio"""
        self.log_error(error, "BUSINESS_LOGIC_ERROR", {
            'payload': error.payload
        })
        return self.create_error_response(error, 422, "business_logic_error")
    
    def handle_security_error(self, error):
        """Manejar errores de seguridad"""
        self.log_error(error, "SECURITY_ERROR", {
            'payload': error.payload,
            'severity': 'HIGH'
        })
        return self.create_error_response(error, 403, "security_error")
    
    def handle_authentication_error(self, error):
        """Manejar errores de autenticación"""
        self.log_error(error, "AUTHENTICATION_ERROR", {
            'payload': error.payload
        })
        return self.create_error_response(error, 401, "authentication_error")
    
    def handle_not_found_error(self, error):
        """Manejar errores de recurso no encontrado"""
        self.log_error(error, "NOT_FOUND_ERROR", {
            'payload': error.payload
        })
        return self.create_error_response(error, 404, "not_found_error")
    
    def handle_rate_limit_error(self, error):
        """Manejar errores de límite de velocidad"""
        self.log_error(error, "RATE_LIMIT_ERROR", {
            'payload': error.payload,
            'severity': 'MEDIUM'
        })
        return self.create_error_response(error, 429, "rate_limit_error")
    
    def handle_bad_request(self, error):
        """Manejar error 400"""
        self.log_error(error, "BAD_REQUEST")
        return self.create_error_response("Solicitud incorrecta", 400, "bad_request")
    
    def handle_unauthorized(self, error):
        """Manejar error 401"""
        self.log_error(error, "UNAUTHORIZED")
        return self.create_error_response("No autorizado", 401, "unauthorized")
    
    def handle_forbidden(self, error):
        """Manejar error 403"""
        self.log_error(error, "FORBIDDEN")
        return self.create_error_response("Acceso denegado", 403, "forbidden")
    
    def handle_not_found(self, error):
        """Manejar error 404"""
        self.log_error(error, "NOT_FOUND")
        return self.create_error_response("Recurso no encontrado", 404, "not_found")
    
    def handle_method_not_allowed(self, error):
        """Manejar error 405"""
        self.log_error(error, "METHOD_NOT_ALLOWED")
        return self.create_error_response("Método no permitido", 405, "method_not_allowed")
    
    def handle_too_many_requests(self, error):
        """Manejar error 429"""
        self.log_error(error, "TOO_MANY_REQUESTS", {'severity': 'MEDIUM'})
        return self.create_error_response("Demasiadas solicitudes", 429, "too_many_requests")
    
    def handle_internal_server_error(self, error):
        """Manejar error 500"""
        self.log_error(error, "INTERNAL_SERVER_ERROR", {'severity': 'CRITICAL'})
        return self.create_error_response("Error interno del servidor", 500, "internal_server_error")
    
    def handle_bad_gateway(self, error):
        """Manejar error 502"""
        self.log_error(error, "BAD_GATEWAY", {'severity': 'HIGH'})
        return self.create_error_response("Gateway incorrecto", 502, "bad_gateway")
    
    def handle_service_unavailable(self, error):
        """Manejar error 503"""
        self.log_error(error, "SERVICE_UNAVAILABLE", {'severity': 'HIGH'})
        return self.create_error_response("Servicio no disponible", 503, "service_unavailable")
    
    def handle_generic_exception(self, error):
        """Manejar excepciones genéricas no capturadas"""
        # No manejar errores HTTP que ya tienen sus propios manejadores
        if isinstance(error, HTTPException):
            return error
        
        self.log_error(error, "UNHANDLED_EXCEPTION", {
            'severity': 'CRITICAL',
            'exception_type': type(error).__name__
        })
        
        # En desarrollo, mostrar el error completo
        if current_app.debug:
            raise error
        
        return self.create_error_response("Error interno del servidor", 500, "unhandled_exception")

# Decoradores para manejo de errores
def handle_errors(f):
    """Decorador para manejar errores en rutas"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except CustomError:
            # Los errores personalizados se propagan para ser manejados por el error handler
            raise
        except Exception as e:
            # Convertir excepciones genéricas en errores personalizados
            current_app.logger.error(f"Unhandled exception in {f.__name__}: {str(e)}")
            raise CustomError(f"Error en {f.__name__}", 500)
    
    return decorated_function

def validate_json(required_fields=None):
    """Decorador para validar datos JSON"""
    def decorator(f):
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                raise ValidationError("Se requiere contenido JSON")
            
            data = request.get_json()
            if not data:
                raise ValidationError("Datos JSON vacíos")
            
            if required_fields:
                for field in required_fields:
                    if field not in data:
                        raise ValidationError(f"Campo requerido: {field}", field=field)
                    if not data[field]:
                        raise ValidationError(f"Campo no puede estar vacío: {field}", field=field)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_auth(f):
    """Decorador para requerir autenticación"""
    from functools import wraps
    from flask_login import current_user
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            raise AuthenticationError("Se requiere autenticación")
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(role):
    """Decorador para requerir rol específico"""
    def decorator(f):
        from functools import wraps
        from flask_login import current_user
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                raise AuthenticationError("Se requiere autenticación")
            
            if current_user.role != role:
                raise SecurityError(f"Se requiere rol: {role}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
