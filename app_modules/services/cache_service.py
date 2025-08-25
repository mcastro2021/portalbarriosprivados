"""
Servicio de cache con Redis
"""

import json
import pickle
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Optional, Union
from flask import current_app

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


class CacheService:
    """Servicio de cache con Redis y fallback en memoria"""
    
    _redis_client = None
    _memory_cache = {}
    _memory_cache_expiry = {}
    
    @classmethod
    def init_app(cls, app):
        """Inicializar servicio de cache con la aplicación"""
        if REDIS_AVAILABLE and app.config.get('REDIS_URL'):
            try:
                cls._redis_client = redis.from_url(
                    app.config['REDIS_URL'],
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                # Test connection
                cls._redis_client.ping()
                app.logger.info("✅ Redis cache inicializado correctamente")
            except Exception as e:
                app.logger.warning(f"⚠️ Error conectando a Redis: {e}. Usando cache en memoria")
                cls._redis_client = None
        else:
            app.logger.info("ℹ️ Redis no disponible. Usando cache en memoria")
    
    @classmethod
    def _is_redis_available(cls):
        """Verificar si Redis está disponible"""
        if not cls._redis_client:
            return False
        try:
            cls._redis_client.ping()
            return True
        except:
            return False
    
    @classmethod
    def set(cls, key: str, value: Any, expire: int = 3600) -> bool:
        """
        Guardar valor en cache
        
        Args:
            key: Clave del cache
            value: Valor a guardar
            expire: Tiempo de expiración en segundos (default: 1 hora)
        
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            if cls._is_redis_available():
                # Usar Redis
                if isinstance(value, (dict, list)):
                    serialized_value = json.dumps(value, default=str)
                else:
                    serialized_value = str(value)
                
                result = cls._redis_client.setex(key, expire, serialized_value)
                return result
            else:
                # Usar cache en memoria
                cls._memory_cache[key] = value
                cls._memory_cache_expiry[key] = datetime.utcnow() + timedelta(seconds=expire)
                return True
                
        except Exception as e:
            current_app.logger.error(f'Error guardando en cache {key}: {e}')
            return False
    
    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        """
        Obtener valor del cache
        
        Args:
            key: Clave del cache
        
        Returns:
            Valor del cache o None si no existe/expiró
        """
        try:
            if cls._is_redis_available():
                # Usar Redis
                value = cls._redis_client.get(key)
                if value is None:
                    return None
                
                # Intentar deserializar JSON
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            else:
                # Usar cache en memoria
                if key not in cls._memory_cache:
                    return None
                
                # Verificar expiración
                if key in cls._memory_cache_expiry:
                    if datetime.utcnow() > cls._memory_cache_expiry[key]:
                        del cls._memory_cache[key]
                        del cls._memory_cache_expiry[key]
                        return None
                
                return cls._memory_cache[key]
                
        except Exception as e:
            current_app.logger.error(f'Error obteniendo del cache {key}: {e}')
            return None
    
    @classmethod
    def delete(cls, key: str) -> bool:
        """
        Eliminar valor del cache
        
        Args:
            key: Clave del cache
        
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            if cls._is_redis_available():
                result = cls._redis_client.delete(key)
                return result > 0
            else:
                if key in cls._memory_cache:
                    del cls._memory_cache[key]
                if key in cls._memory_cache_expiry:
                    del cls._memory_cache_expiry[key]
                return True
                
        except Exception as e:
            current_app.logger.error(f'Error eliminando del cache {key}: {e}')
            return False
    
    @classmethod
    def exists(cls, key: str) -> bool:
        """
        Verificar si existe una clave en el cache
        
        Args:
            key: Clave del cache
        
        Returns:
            bool: True si existe
        """
        try:
            if cls._is_redis_available():
                return cls._redis_client.exists(key) > 0
            else:
                if key not in cls._memory_cache:
                    return False
                
                # Verificar expiración
                if key in cls._memory_cache_expiry:
                    if datetime.utcnow() > cls._memory_cache_expiry[key]:
                        del cls._memory_cache[key]
                        del cls._memory_cache_expiry[key]
                        return False
                
                return True
                
        except Exception as e:
            current_app.logger.error(f'Error verificando existencia en cache {key}: {e}')
            return False
    
    @classmethod
    def clear_pattern(cls, pattern: str) -> int:
        """
        Eliminar todas las claves que coincidan con un patrón
        
        Args:
            pattern: Patrón de búsqueda (ej: "user:*")
        
        Returns:
            int: Número de claves eliminadas
        """
        try:
            if cls._is_redis_available():
                keys = cls._redis_client.keys(pattern)
                if keys:
                    return cls._redis_client.delete(*keys)
                return 0
            else:
                # Para cache en memoria, usar coincidencia simple
                import fnmatch
                keys_to_delete = []
                for key in cls._memory_cache.keys():
                    if fnmatch.fnmatch(key, pattern):
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    del cls._memory_cache[key]
                    if key in cls._memory_cache_expiry:
                        del cls._memory_cache_expiry[key]
                
                return len(keys_to_delete)
                
        except Exception as e:
            current_app.logger.error(f'Error eliminando patrón del cache {pattern}: {e}')
            return 0
    
    @classmethod
    def get_stats(cls) -> dict:
        """
        Obtener estadísticas del cache
        
        Returns:
            dict: Estadísticas del cache
        """
        try:
            if cls._is_redis_available():
                info = cls._redis_client.info()
                return {
                    'type': 'redis',
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory': info.get('used_memory_human', '0B'),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0)
                }
            else:
                # Limpiar cache expirado antes de contar
                current_time = datetime.utcnow()
                expired_keys = []
                for key, expiry in cls._memory_cache_expiry.items():
                    if current_time > expiry:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    if key in cls._memory_cache:
                        del cls._memory_cache[key]
                    del cls._memory_cache_expiry[key]
                
                return {
                    'type': 'memory',
                    'total_keys': len(cls._memory_cache),
                    'expired_keys_cleaned': len(expired_keys)
                }
                
        except Exception as e:
            current_app.logger.error(f'Error obteniendo estadísticas del cache: {e}')
            return {'type': 'error', 'message': str(e)}


def cached(expire: int = 3600, key_prefix: str = ""):
    """
    Decorador para cachear resultados de funciones
    
    Args:
        expire: Tiempo de expiración en segundos
        key_prefix: Prefijo para la clave del cache
    
    Usage:
        @cached(expire=1800, key_prefix="user_stats")
        def get_user_stats(user_id):
            return expensive_calculation(user_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave del cache
            cache_key = f"{key_prefix}:{func.__name__}"
            if args:
                cache_key += f":{':'.join(str(arg) for arg in args)}"
            if kwargs:
                cache_key += f":{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"
            
            # Intentar obtener del cache
            cached_result = CacheService.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y guardar resultado
            result = func(*args, **kwargs)
            CacheService.set(cache_key, result, expire)
            
            return result
        
        return wrapper
    return decorator


def cache_invalidate(key_pattern: str):
    """
    Decorador para invalidar cache después de ejecutar una función
    
    Args:
        key_pattern: Patrón de claves a invalidar
    
    Usage:
        @cache_invalidate("user_stats:*")
        def update_user_profile(user_id, data):
            # Actualizar perfil
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            CacheService.clear_pattern(key_pattern)
            return result
        
        return wrapper
    return decorator
