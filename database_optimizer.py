"""
Optimizador de Base de Datos
Índices estratégicos y consultas optimizadas para mejor performance
"""

from sqlalchemy import Index, text
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Optimizador de consultas y rendimiento de base de datos"""
    
    def __init__(self, db):
        self.db = db
    
    def create_strategic_indexes(self):
        """Crear índices estratégicos para mejorar performance"""
        indexes = [
            # Índices para usuarios
            Index('idx_users_email', 'users.email'),
            Index('idx_users_username', 'users.username'),
            Index('idx_users_role_active', 'users.role', 'users.is_active'),
            Index('idx_users_created_at', 'users.created_at'),
            
            # Índices para visitas
            Index('idx_visits_resident_date', 'visits.resident_id', 'visits.entry_time'),
            Index('idx_visits_status_date', 'visits.status', 'visits.entry_time'),
            Index('idx_visits_visitor_name', 'visits.visitor_name'),
            
            # Índices para reservas
            Index('idx_reservations_user_date', 'reservations.user_id', 'reservations.start_time'),
            Index('idx_reservations_space_date', 'reservations.space_id', 'reservations.start_time'),
            Index('idx_reservations_status_date', 'reservations.status', 'reservations.start_time'),
            
            # Índices para notificaciones
            Index('idx_notifications_user_read', 'notifications.user_id', 'notifications.is_read'),
            Index('idx_notifications_created_at', 'notifications.created_at'),
            Index('idx_notifications_type_user', 'notifications.type', 'notifications.user_id'),
            
            # Índices para mantenimiento
            Index('idx_maintenance_user_status', 'maintenance.user_id', 'maintenance.status'),
            Index('idx_maintenance_priority_date', 'maintenance.priority', 'maintenance.created_at'),
            Index('idx_maintenance_category_status', 'maintenance.category', 'maintenance.status'),
            
            # Índices para noticias
            Index('idx_news_category_date', 'news.category', 'news.created_at'),
            Index('idx_news_author_date', 'news.author_id', 'news.created_at'),
            Index('idx_news_published_date', 'news.is_published', 'news.created_at'),
            
            # Índices para reportes de seguridad
            Index('idx_security_reports_date', 'security_reports.created_at'),
            Index('idx_security_reports_type_date', 'security_reports.type', 'security_reports.created_at'),
            Index('idx_security_reports_user_date', 'security_reports.user_id', 'security_reports.created_at'),
            
            # Índices para expensas
            Index('idx_expenses_user_month', 'expenses.user_id', 'expenses.month'),
            Index('idx_expenses_status_date', 'expenses.status', 'expenses.due_date'),
            Index('idx_expenses_amount_status', 'expenses.amount', 'expenses.status'),
            
            # Índices para clasificados
            Index('idx_classifieds_category_date', 'classifieds.category', 'classifieds.created_at'),
            Index('idx_classifieds_author_status', 'classifieds.author_id', 'classifieds.status'),
            Index('idx_classifieds_title_search', 'classifieds.title'),
        ]
        
        try:
            for index in indexes:
                index.create(self.db.engine, checkfirst=True)
            logger.info("✅ Índices estratégicos creados exitosamente")
        except Exception as e:
            logger.error(f"❌ Error creando índices: {e}")
    
    def optimize_queries(self):
        """Configurar optimizaciones de consultas"""
        # Configurar opciones de conexión
        self.db.engine.execute(text("""
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=NORMAL;
            PRAGMA cache_size=10000;
            PRAGMA temp_store=MEMORY;
        """))
        logger.info("✅ Optimizaciones de consultas aplicadas")

class QueryOptimizer:
    """Optimizador de consultas específicas"""
    
    @staticmethod
    def get_user_with_relations(user_id):
        """Obtener usuario con relaciones optimizadas"""
        from models import User
        
        return User.query.options(
            joinedload(User.visits),
            joinedload(User.reservations),
            joinedload(User.notifications),
            joinedload(User.maintenance_requests)
        ).filter_by(id=user_id).first()
    
    @staticmethod
    def get_dashboard_data_optimized(user_id):
        """Obtener datos del dashboard con consultas optimizadas"""
        from models import Visit, Reservation, Notification, Maintenance
        
        # Usar subconsultas para evitar N+1 queries
        dashboard_data = {}
        
        # Consulta optimizada para visitas pendientes
        pending_visits = Visit.query.filter_by(
            user_id=user_id, 
            status='pending'
        ).count()
        
        # Consulta optimizada para reservas próximas
        upcoming_reservations = Reservation.query.filter(
            Reservation.user_id == user_id,
            Reservation.status == 'confirmed',
            Reservation.start_time >= datetime.now()
        ).count()
        
        # Consulta optimizada para notificaciones no leídas
        unread_notifications = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
        
        # Consulta optimizada para mantenimiento activo
        active_maintenance = Maintenance.query.filter(
            Maintenance.user_id == user_id,
            Maintenance.status.in_(['open', 'in_progress'])
        ).count()
        
        return {
            'pending_visits': pending_visits,
            'upcoming_reservations': upcoming_reservations,
            'unread_notifications': unread_notifications,
            'active_maintenance': active_maintenance
        }
    
    @staticmethod
    def get_visits_with_pagination(user_id, page=1, per_page=20):
        """Obtener visitas con paginación optimizada"""
        from models import Visit
        
        return Visit.query.filter_by(user_id=user_id)\
            .order_by(Visit.entry_time.desc())\
            .paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
    
    @staticmethod
    def get_reservations_with_availability(date, space_id=None):
        """Obtener reservas con disponibilidad optimizada"""
        from models import Reservation, Space
        
        query = Reservation.query.filter(
            Reservation.date == date,
            Reservation.status.in_(['confirmed', 'pending'])
        )
        
        if space_id:
            query = query.filter(Reservation.space_id == space_id)
        
        return query.all()
    
    @staticmethod
    def get_notifications_batch(user_ids, limit=10):
        """Obtener notificaciones para múltiples usuarios de forma optimizada"""
        from models import Notification
        
        return Notification.query.filter(
            Notification.user_id.in_(user_ids)
        ).order_by(Notification.created_at.desc())\
         .limit(limit).all()

class PerformanceMonitor:
    """Monitor de performance de consultas"""
    
    def __init__(self):
        self.query_times = {}
        self.slow_queries = []
    
    def monitor_query(self, query_name):
        """Decorador para monitorear tiempo de consultas"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = datetime.now()
                result = func(*args, **kwargs)
                end_time = datetime.now()
                
                execution_time = (end_time - start_time).total_seconds()
                self.query_times[query_name] = execution_time
                
                # Registrar consultas lentas
                if execution_time > 1.0:  # Más de 1 segundo
                    self.slow_queries.append({
                        'query': query_name,
                        'time': execution_time,
                        'timestamp': datetime.now()
                    })
                    logger.warning(f"⚠️ Consulta lenta detectada: {query_name} ({execution_time:.2f}s)")
                
                return result
            return wrapper
        return decorator
    
    def get_performance_report(self):
        """Generar reporte de performance"""
        return {
            'query_times': self.query_times,
            'slow_queries': self.slow_queries,
            'average_time': sum(self.query_times.values()) / len(self.query_times) if self.query_times else 0
        }

# Instancia global del monitor
performance_monitor = PerformanceMonitor()

class DatabaseHealthCheck:
    """Verificación de salud de la base de datos"""
    
    @staticmethod
    def check_database_health(db):
        """Verificar salud general de la base de datos"""
        try:
            # Verificar conexión
            db.engine.execute(text("SELECT 1"))
            
            # Verificar tablas principales
            tables = ['users', 'visits', 'reservations', 'notifications']
            missing_tables = []
            
            for table in tables:
                try:
                    db.engine.execute(text(f"SELECT COUNT(*) FROM {table}"))
                except:
                    missing_tables.append(table)
            
            # Verificar índices
            indexes = db.engine.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_%'
            """)).fetchall()
            
            return {
                'status': 'healthy',
                'connection': True,
                'missing_tables': missing_tables,
                'indexes_count': len(indexes),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    @staticmethod
    def optimize_database(db):
        """Ejecutar optimizaciones de base de datos"""
        try:
            # VACUUM para optimizar espacio
            db.engine.execute(text("VACUUM"))
            
            # ANALYZE para actualizar estadísticas
            db.engine.execute(text("ANALYZE"))
            
            # Reindexar
            db.engine.execute(text("REINDEX"))
            
            logger.info("✅ Optimizaciones de base de datos completadas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error optimizando base de datos: {e}")
            return False
