"""
Manejo centralizado de errores
"""

import traceback
from datetime import datetime
from flask import jsonify, render_template, request, current_app
from werkzeug.exceptions import HTTPException
import logging


class ErrorHandler:
    """Manejador centralizado de errores"""
    
    @staticmethod
    def register_error_handlers(app):
        """Registrar manejadores de error en la aplicación"""
        
        @app.errorhandler(400)
        def bad_request(error):
            return ErrorHandler._handle_error(error, 400, 'Solicitud inválida')
        
        @app.errorhandler(401)
        def unauthorized(error):
            return ErrorHandler._handle_error(error, 401, 'No autorizado')
        
        @app.errorhandler(403)
        def forbidden(error):
            return ErrorHandler._handle_error(error, 403, 'Acceso denegado')
        
        @app.errorhandler(404)
        def not_found(error):
            return ErrorHandler._handle_error(error, 404, 'Recurso no encontrado')
        
        @app.errorhandler(405)
        def method_not_allowed(error):
            return ErrorHandler._handle_error(error, 405, 'Método no permitido')
        
        @app.errorhandler(429)
        def rate_limit_exceeded(error):
            return ErrorHandler._handle_error(error, 429, 'Rate limit excedido')
        
        @app.errorhandler(500)
        def internal_server_error(error):
            return ErrorHandler._handle_error(error, 500, 'Error interno del servidor')
        
        @app.errorhandler(Exception)
        def handle_unexpected_error(error):
            return ErrorHandler._handle_error(error, 500, 'Error inesperado')
    
    @staticmethod
    def _handle_error(error, status_code, default_message):
        """Manejar error de forma centralizada"""
        
        # Registrar error
        ErrorHandler._log_error(error, status_code)
        
        # Determinar si es una request API
        is_api_request = (
            request.path.startswith('/api/') or
            request.headers.get('Content-Type', '').startswith('application/json') or
            request.headers.get('Accept', '').startswith('application/json')
        )
        
        # Preparar respuesta
        if is_api_request:
            return ErrorHandler._create_api_error_response(error, status_code, default_message)
        else:
            return ErrorHandler._create_web_error_response(error, status_code, default_message)
    
    @staticmethod
    def _log_error(error, status_code):
        """Registrar error en logs"""
        timestamp = datetime.utcnow().isoformat()
        ip = request.remote_addr or 'Unknown'
        user_agent = request.headers.get('User-Agent', 'Unknown')
        path = request.path
        method = request.method
        
        error_details = {
            'timestamp': timestamp,
            'status_code': status_code,
            'ip': ip,
            'user_agent': user_agent,
            'path': path,
            'method': method,
            'error': str(error),
            'traceback': traceback.format_exc() if status_code >= 500 else None
        }
        
        if status_code >= 500:
            current_app.logger.error(f'Server Error: {error_details}')
        elif status_code >= 400:
            current_app.logger.warning(f'Client Error: {error_details}')
        else:
            current_app.logger.info(f'Request Info: {error_details}')
    
    @staticmethod
    def _create_api_error_response(error, status_code, default_message):
        """Crear respuesta de error para API"""
        
        # Determinar mensaje de error
        if isinstance(error, HTTPException):
            message = error.description or default_message
        else:
            message = str(error) if current_app.debug else default_message
        
        response_data = {
            'error': True,
            'status_code': status_code,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'path': request.path
        }
        
        # En modo debug, incluir más detalles
        if current_app.debug and status_code >= 500:
            response_data['traceback'] = traceback.format_exc()
        
        return jsonify(response_data), status_code
    
    @staticmethod
    def _create_web_error_response(error, status_code, default_message):
        """Crear respuesta de error para web"""
        
        # Mapear códigos de estado a templates
        template_map = {
            400: 'errors/400.html',
            401: 'errors/401.html', 
            403: 'errors/403.html',
            404: 'errors/404.html',
            405: 'errors/405.html',
            429: 'errors/429.html',
            500: 'errors/500.html'
        }
        
        template = template_map.get(status_code, 'errors/500.html')
        
        # Determinar mensaje
        if isinstance(error, HTTPException):
            message = error.description or default_message
        else:
            message = default_message
        
        try:
            return render_template(template, 
                                 error_code=status_code,
                                 error_message=message,
                                 timestamp=datetime.utcnow()), status_code
        except Exception:
            # Fallback si no existe el template
            return render_template('errors/500.html',
                                 error_code=status_code,
                                 error_message=message,
                                 timestamp=datetime.utcnow()), status_code


class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    
    def __init__(self, message, field=None, code=None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(self.message)


class BusinessLogicError(Exception):
    """Excepción personalizada para errores de lógica de negocio"""
    
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class SecurityError(Exception):
    """Excepción personalizada para errores de seguridad"""
    
    def __init__(self, message, severity='warning'):
        self.message = message
        self.severity = severity
        super().__init__(self.message)
