"""
Servicio de seguridad y rate limiting
"""

import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
import hashlib
import ipaddress


class SecurityService:
    """Servicio para manejo de seguridad y rate limiting"""
    
    # Almacenamiento en memoria para rate limiting (en producción usar Redis)
    _rate_limit_storage = defaultdict(deque)
    _failed_attempts = defaultdict(list)
    _blocked_ips = set()
    
    @classmethod
    def rate_limit(cls, max_requests=60, window_seconds=60, per='ip'):
        """
        Decorador para rate limiting
        
        Args:
            max_requests: Número máximo de requests
            window_seconds: Ventana de tiempo en segundos
            per: 'ip' o 'user' para limitar por IP o usuario
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Determinar clave para rate limiting
                if per == 'ip':
                    key = cls._get_client_ip()
                elif per == 'user':
                    key = getattr(request, 'jwt_user_id', cls._get_client_ip())
                else:
                    key = cls._get_client_ip()
                
                # Verificar si está bloqueado
                if cls._is_blocked(key):
                    return jsonify({
                        'error': 'IP bloqueada temporalmente por exceso de requests',
                        'retry_after': 300  # 5 minutos
                    }), 429
                
                # Verificar rate limit
                current_time = time.time()
                requests_queue = cls._rate_limit_storage[key]
                
                # Limpiar requests antiguos
                while requests_queue and requests_queue[0] < current_time - window_seconds:
                    requests_queue.popleft()
                
                # Verificar límite
                if len(requests_queue) >= max_requests:
                    cls._record_failed_attempt(key)
                    return jsonify({
                        'error': 'Rate limit excedido',
                        'max_requests': max_requests,
                        'window_seconds': window_seconds,
                        'retry_after': window_seconds
                    }), 429
                
                # Registrar request actual
                requests_queue.append(current_time)
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    @classmethod
    def _get_client_ip(cls):
        """Obtener IP real del cliente"""
        # Verificar headers de proxy
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr or '127.0.0.1'
    
    @classmethod
    def _record_failed_attempt(cls, key):
        """Registrar intento fallido"""
        current_time = time.time()
        cls._failed_attempts[key].append(current_time)
        
        # Limpiar intentos antiguos (últimos 10 minutos)
        cls._failed_attempts[key] = [
            attempt for attempt in cls._failed_attempts[key]
            if attempt > current_time - 600
        ]
        
        # Bloquear si hay muchos intentos fallidos
        if len(cls._failed_attempts[key]) >= 10:
            cls._blocked_ips.add(key)
            current_app.logger.warning(f'IP bloqueada por rate limiting: {key}')
    
    @classmethod
    def _is_blocked(cls, key):
        """Verificar si una IP está bloqueada"""
        return key in cls._blocked_ips
    
    @classmethod
    def unblock_ip(cls, ip):
        """Desbloquear IP manualmente"""
        cls._blocked_ips.discard(ip)
        if ip in cls._failed_attempts:
            del cls._failed_attempts[ip]
        if ip in cls._rate_limit_storage:
            del cls._rate_limit_storage[ip]
    
    @classmethod
    def get_security_stats(cls):
        """Obtener estadísticas de seguridad"""
        current_time = time.time()
        
        # Limpiar datos antiguos
        active_ips = 0
        for ip, requests in cls._rate_limit_storage.items():
            # Limpiar requests antiguos
            while requests and requests[0] < current_time - 3600:  # 1 hora
                requests.popleft()
            if requests:
                active_ips += 1
        
        return {
            'active_ips': active_ips,
            'blocked_ips': len(cls._blocked_ips),
            'failed_attempts': sum(len(attempts) for attempts in cls._failed_attempts.values()),
            'total_tracked_ips': len(cls._rate_limit_storage)
        }
    
    @staticmethod
    def validate_ip_address(ip):
        """Validar formato de dirección IP"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_safe_redirect_url(url):
        """Verificar si una URL es segura para redirección"""
        if not url:
            return False
        
        # Solo permitir URLs relativas o del mismo dominio
        if url.startswith('/'):
            return True
        
        # Verificar que no sea una URL externa maliciosa
        dangerous_schemes = ['javascript:', 'data:', 'vbscript:', 'file:']
        for scheme in dangerous_schemes:
            if url.lower().startswith(scheme):
                return False
        
        return False  # Por seguridad, rechazar URLs externas
    
    @staticmethod
    def log_security_event(event_type, details, severity='info'):
        """Registrar evento de seguridad"""
        timestamp = datetime.utcnow().isoformat()
        ip = SecurityService._get_client_ip()
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        log_entry = {
            'timestamp': timestamp,
            'event_type': event_type,
            'severity': severity,
            'ip': ip,
            'user_agent': user_agent,
            'details': details
        }
        
        if severity in ['warning', 'error', 'critical']:
            current_app.logger.warning(f'Security Event: {log_entry}')
        else:
            current_app.logger.info(f'Security Event: {log_entry}')
        
        return log_entry
