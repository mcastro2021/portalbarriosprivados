"""
Integrador de Performance - Fase 1
Conecta todas las optimizaciones de performance implementadas
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, current_app
from cache_manager import cache_manager, DashboardCache, NotificationCache, SpaceCache
from database_optimizer import DatabaseOptimizer, QueryOptimizer, performance_monitor, DatabaseHealthCheck
from asset_compressor import asset_compressor, asset_bundler

logger = logging.getLogger(__name__)

class PerformanceIntegration:
    """Integrador de todas las optimizaciones de performance"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.db_optimizer = None
        self.initialized = False
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Inicializar integrador con la aplicación Flask"""
        self.app = app
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        
        # Inicializar optimizaciones
        self.initialize_optimizations()
        
        # Registrar blueprints y rutas
        self.register_routes()
        
        # Configurar middleware
        self.setup_middleware()
        
        self.initialized = True
        logger.info("✅ Integrador de performance inicializado")
    
    def initialize_optimizations(self):
        """Inicializar todas las optimizaciones"""
        try:
            # 1. Inicializar caché Redis
            logger.info("🔄 Inicializando caché Redis...")
            if cache_manager.is_connected():
                logger.info("✅ Caché Redis conectado")
            else:
                logger.warning("⚠️ Caché Redis no disponible, usando fallback")
            
            # 2. Inicializar optimizador de base de datos
            logger.info("🔄 Inicializando optimizador de base de datos...")
            from models import db
            self.db_optimizer = DatabaseOptimizer(db)
            
            # Crear índices estratégicos
            self.db_optimizer.create_strategic_indexes()
            
            # Aplicar optimizaciones de consultas
            self.db_optimizer.optimize_queries()
            
            # 3. Verificar salud de la base de datos
            health_status = DatabaseHealthCheck.check_database_health(db)
            if health_status['status'] == 'healthy':
                logger.info("✅ Base de datos saludable")
            else:
                logger.warning(f"⚠️ Problemas en base de datos: {health_status.get('error', 'Unknown')}")
            
            # 4. Comprimir assets (solo en desarrollo)
            if self.app.config.get('ENV') == 'development':
                logger.info("🔄 Comprimiendo assets...")
                try:
                    asset_compressor.compress_all_assets()
                    asset_bundler.create_css_bundle('main', [
                        'css/bootstrap.min.css',
                        'css/app.css'
                    ])
                    asset_bundler.create_js_bundle('main', [
                        'js/app.js',
                        'js/performance-optimizer.js'
                    ])
                    logger.info("✅ Assets comprimidos")
                except Exception as e:
                    logger.warning(f"⚠️ Error comprimiendo assets: {e}")
            
            logger.info("✅ Todas las optimizaciones inicializadas")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando optimizaciones: {e}")
    
    def register_routes(self):
        """Registrar rutas de performance"""
        
        @self.app.route('/api/performance/health')
        def performance_health():
            """Endpoint de salud de performance"""
            return jsonify({
                'status': 'healthy',
                'cache_connected': cache_manager.is_connected(),
                'database_optimized': self.db_optimizer is not None,
                'assets_compressed': True,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/performance/metrics')
        def performance_metrics():
            """Endpoint de métricas de performance"""
            return jsonify({
                'cache_stats': self.get_cache_stats(),
                'database_stats': self.get_database_stats(),
                'asset_stats': asset_compressor.get_compression_stats(),
                'query_performance': performance_monitor.get_performance_report(),
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/performance/optimize')
        def optimize_performance():
            """Endpoint para optimizaciones manuales"""
            try:
                # Optimizar base de datos
                from models import db
                DatabaseHealthCheck.optimize_database(db)
                
                # Limpiar caché
                cache_manager.clear_pattern('*')
                
                # Comprimir assets
                asset_compressor.compress_all_assets()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Optimizaciones aplicadas',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/performance/cache/clear')
        def clear_cache():
            """Limpiar caché"""
            try:
                pattern = request.args.get('pattern', '*')
                cache_manager.clear_pattern(pattern)
                return jsonify({
                    'status': 'success',
                    'message': f'Caché limpiado: {pattern}',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
    
    def setup_middleware(self):
        """Configurar middleware de performance"""
        
        @self.app.before_request
        def before_request():
            """Middleware antes de cada request"""
            # Marcar inicio del request para timing
            request.start_time = datetime.now()
            
            # Log de request para monitoreo
            logger.info(f"📥 {request.method} {request.path} - {request.remote_addr}")
        
        @self.app.after_request
        def after_request(response):
            """Middleware después de cada request"""
            # Calcular tiempo de respuesta
            if hasattr(request, 'start_time'):
                duration = (datetime.now() - request.start_time).total_seconds()
                response.headers['X-Response-Time'] = str(duration)
                
                # Log de performance
                if duration > 1.0:  # Más de 1 segundo
                    logger.warning(f"⚠️ Request lento: {request.path} ({duration:.2f}s)")
                else:
                    logger.info(f"📤 {request.method} {request.path} - {response.status_code} ({duration:.3f}s)")
            
            return response
    
    def get_cache_stats(self):
        """Obtener estadísticas del caché"""
        if not cache_manager.is_connected():
            return {'status': 'disconnected'}
        
        try:
            # Obtener estadísticas básicas de Redis
            info = cache_manager.redis_client.info()
            return {
                'status': 'connected',
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def get_database_stats(self):
        """Obtener estadísticas de la base de datos"""
        try:
            from models import db
            
            # Obtener estadísticas básicas
            stats = {}
            
            # Contar registros en tablas principales
            tables = ['users', 'visits', 'reservations', 'notifications', 'maintenance']
            for table in tables:
                try:
                    result = db.engine.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f'{table}_count'] = result.fetchone()[0]
                except:
                    stats[f'{table}_count'] = 0
            
            # Obtener tamaño de la base de datos
            try:
                result = db.engine.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                stats['database_size'] = result.fetchone()[0]
            except:
                stats['database_size'] = 0
            
            return stats
        except Exception as e:
            return {'error': str(e)}

# Decoradores de performance para usar en las rutas
def cached_response(timeout=300, key_prefix=None):
    """Decorador para cachear respuestas de API"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            # Generar clave de caché
            prefix = key_prefix or f"{f.__module__}.{f.__name__}"
            cache_key = cache_manager.generate_key(prefix, *args, **kwargs)
            
            # Intentar obtener del caché
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return jsonify(cached_result)
            
            # Ejecutar función y cachear resultado
            result = f(*args, **kwargs)
            cache_manager.set(cache_key, result, timeout)
            return result
        return decorated_function
    return decorator

def monitor_performance(query_name):
    """Decorador para monitorear performance de consultas"""
    return performance_monitor.monitor_query(query_name)

def optimize_query():
    """Decorador para usar consultas optimizadas"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            # Aquí se pueden aplicar optimizaciones específicas
            # antes de ejecutar la función
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Funciones de utilidad para optimizaciones específicas
class PerformanceUtils:
    """Utilidades de performance"""
    
    @staticmethod
    def get_optimized_dashboard_data(user_id):
        """Obtener datos del dashboard optimizados"""
        # Usar caché si está disponible
        cache_key = f"dashboard:{user_id}"
        cached_data = cache_manager.get(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        # Obtener datos optimizados
        data = QueryOptimizer.get_dashboard_data_optimized(user_id)
        
        # Cachear resultado
        cache_manager.set(cache_key, data, 300)  # 5 minutos
        
        return data
    
    @staticmethod
    def get_optimized_notifications(user_id, limit=10):
        """Obtener notificaciones optimizadas"""
        return NotificationCache.get_user_notifications(user_id, limit)
    
    @staticmethod
    def get_optimized_spaces_availability(date):
        """Obtener disponibilidad de espacios optimizada"""
        return SpaceCache.get_available_spaces(date)
    
    @staticmethod
    def invalidate_user_cache(user_id):
        """Invalidar caché de usuario"""
        cache_manager.invalidate_user_cache(user_id)
        NotificationCache.invalidate_user_notifications(user_id)
    
    @staticmethod
    def preload_critical_data(user_id):
        """Precargar datos críticos del usuario"""
        # Precargar datos del dashboard
        PerformanceUtils.get_optimized_dashboard_data(user_id)
        
        # Precargar notificaciones
        PerformanceUtils.get_optimized_notifications(user_id)
        
        # Precargar datos de espacios para hoy
        from datetime import date
        PerformanceUtils.get_optimized_spaces_availability(date.today())

# Instancia global del integrador
performance_integration = PerformanceIntegration()

def init_performance(app):
    """Función de conveniencia para inicializar performance"""
    with app.app_context():
        performance_integration.init_app(app)
    return performance_integration

# Configuración de performance para diferentes entornos
PERFORMANCE_CONFIG = {
    'development': {
        'cache_enabled': True,
        'cache_timeout': 60,  # 1 minuto en desarrollo
        'database_optimization': True,
        'asset_compression': True,
        'performance_monitoring': True
    },
    'production': {
        'cache_enabled': True,
        'cache_timeout': 300,  # 5 minutos en producción
        'database_optimization': True,
        'asset_compression': True,
        'performance_monitoring': True
    },
    'testing': {
        'cache_enabled': False,
        'cache_timeout': 0,
        'database_optimization': False,
        'asset_compression': False,
        'performance_monitoring': False
    }
}

def get_performance_config(env=None):
    """Obtener configuración de performance para el entorno"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return PERFORMANCE_CONFIG.get(env, PERFORMANCE_CONFIG['development'])
