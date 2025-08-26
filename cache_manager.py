"""
Sistema de Caché Inteligente con Redis
Optimización de performance para consultas frecuentes
"""

import redis
import json
import pickle
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Gestor de caché inteligente con Redis"""
    
    def __init__(self, redis_url=None):
        self.redis_url = redis_url or current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        self.redis_client = None
        self.default_timeout = 300  # 5 minutos
        self.connect()
    
    def connect(self):
        """Conectar a Redis"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=False)
            self.redis_client.ping()
            logger.info("✅ Conectado a Redis exitosamente")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo conectar a Redis: {e}")
            self.redis_client = None
    
    def is_connected(self):
        """Verificar si Redis está conectado"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def generate_key(self, prefix, *args, **kwargs):
        """Generar clave única para caché"""
        key_parts = [prefix]
        
        # Agregar argumentos posicionales
        for arg in args:
            key_parts.append(str(arg))
        
        # Agregar argumentos nombrados ordenados
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        
        # Crear hash para claves largas
        key_string = ":".join(key_parts)
        if len(key_string) > 250:
            return f"{prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"
        
        return key_string
    
    def get(self, key, default=None):
        """Obtener valor del caché"""
        if not self.is_connected():
            return default
        
        try:
            value = self.redis_client.get(key)
            if value is None:
                return default
            
            # Intentar deserializar como JSON primero
            try:
                return json.loads(value.decode('utf-8'))
            except:
                # Si falla JSON, usar pickle
                return pickle.loads(value)
        except Exception as e:
            logger.error(f"Error al obtener caché para {key}: {e}")
            return default
    
    def set(self, key, value, timeout=None):
        """Establecer valor en caché"""
        if not self.is_connected():
            return False
        
        try:
            timeout = timeout or self.default_timeout
            
            # Intentar serializar como JSON primero
            try:
                serialized = json.dumps(value, default=str).encode('utf-8')
            except:
                # Si falla JSON, usar pickle
                serialized = pickle.dumps(value)
            
            return self.redis_client.setex(key, timeout, serialized)
        except Exception as e:
            logger.error(f"Error al establecer caché para {key}: {e}")
            return False
    
    def delete(self, key):
        """Eliminar clave del caché"""
        if not self.is_connected():
            return False
        
        try:
            return self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error al eliminar caché para {key}: {e}")
            return False
    
    def clear_pattern(self, pattern):
        """Eliminar todas las claves que coincidan con un patrón"""
        if not self.is_connected():
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Error al limpiar patrón {pattern}: {e}")
            return False
    
    def invalidate_user_cache(self, user_id):
        """Invalidar caché relacionado con un usuario"""
        patterns = [
            f"user:{user_id}:*",
            f"dashboard:{user_id}:*",
            f"notifications:{user_id}:*",
            f"visits:user:{user_id}:*",
            f"reservations:user:{user_id}:*"
        ]
        
        for pattern in patterns:
            self.clear_pattern(pattern)
    
    def get_or_set(self, key, callback, timeout=None):
        """Obtener del caché o ejecutar callback y guardar"""
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Ejecutar callback y guardar resultado
        value = callback()
        self.set(key, value, timeout)
        return value

# Instancia global del caché
cache_manager = CacheManager()

def cached(timeout=None, key_prefix=None):
    """Decorador para cachear resultados de funciones"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave única
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = cache_manager.generate_key(prefix, *args, **kwargs)
            
            # Intentar obtener del caché
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern):
    """Decorador para invalidar caché después de operaciones"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cache_manager.clear_pattern(pattern)
            return result
        return wrapper
    return decorator

# Funciones de utilidad para caché específico
class DashboardCache:
    """Caché específico para datos del dashboard"""
    
    @staticmethod
    @cached(timeout=300, key_prefix="dashboard")
    def get_user_dashboard_data(user_id):
        """Obtener datos del dashboard de usuario"""
        from models import Visit, Reservation, Notification, Maintenance
        
        return {
            'pending_visits': Visit.query.filter_by(user_id=user_id, status='pending').count(),
            'upcoming_reservations': Reservation.query.filter_by(user_id=user_id, status='confirmed').count(),
            'unread_notifications': Notification.query.filter_by(user_id=user_id, is_read=False).count(),
            'active_maintenance': Maintenance.query.filter_by(user_id=user_id, status='in_progress').count(),
            'total_expenses': 0,  # TODO: Implementar cálculo de expensas
            'last_activity': datetime.now().isoformat()
        }
    
    @staticmethod
    @cached(timeout=600, key_prefix="admin_dashboard")
    def get_admin_dashboard_data():
        """Obtener datos del dashboard de administrador"""
        from models import User, Visit, Reservation, Maintenance, SecurityReport
        
        return {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'pending_visits': Visit.query.filter_by(status='pending').count(),
            'today_reservations': Reservation.query.filter(
                Reservation.start_time >= datetime.now().date()
            ).count(),
            'open_maintenance': Maintenance.query.filter_by(status='open').count(),
            'security_incidents': SecurityReport.query.filter(
                SecurityReport.created_at >= datetime.now() - timedelta(days=7)
            ).count()
        }

class NotificationCache:
    """Caché específico para notificaciones"""
    
    @staticmethod
    @cached(timeout=60, key_prefix="notifications")
    def get_user_notifications(user_id, limit=10):
        """Obtener notificaciones de usuario"""
        from models import Notification
        
        return Notification.query.filter_by(user_id=user_id)\
            .order_by(Notification.created_at.desc())\
            .limit(limit).all()
    
    @staticmethod
    def invalidate_user_notifications(user_id):
        """Invalidar caché de notificaciones de usuario"""
        cache_manager.clear_pattern(f"notifications:user:{user_id}:*")

class SpaceCache:
    """Caché específico para espacios comunes"""
    
    @staticmethod
    @cached(timeout=1800, key_prefix="spaces")  # 30 minutos
    def get_available_spaces(date):
        """Obtener espacios disponibles para una fecha"""
        from models import Reservation, Space
        
        # Obtener reservas existentes para la fecha
        existing_reservations = Reservation.query.filter(
            Reservation.date == date,
            Reservation.status.in_(['confirmed', 'pending'])
        ).all()
        
        # Calcular disponibilidad
        spaces = Space.query.all()
        availability = {}
        
        for space in spaces:
            space_reservations = [r for r in existing_reservations if r.space_id == space.id]
            availability[space.id] = {
                'space': space,
                'reserved_hours': [r.start_time.hour for r in space_reservations],
                'available': True
            }
        
        return availability
