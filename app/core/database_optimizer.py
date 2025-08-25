"""
Optimizador de base de datos
Proporciona optimizaciones de consultas, índices y rendimiento
"""

from sqlalchemy import text, inspect, Index
from sqlalchemy.orm import joinedload, selectinload, contains_eager
from flask import current_app
from models import db
from datetime import datetime, timedelta
import time
from functools import wraps
from collections import defaultdict

class DatabaseOptimizer:
    """Optimizador de base de datos"""
    
    def __init__(self, app=None):
        self.app = app
        self.query_stats = defaultdict(list)
        self.slow_query_threshold = 1.0  # segundos
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar optimizador con la aplicación"""
        self.app = app
        
        # Configurar logging de consultas lentas
        self.setup_query_logging()
        
        # Crear índices optimizados
        self.create_optimized_indexes()
        
        print("✅ Optimizador de base de datos inicializado")
    
    def setup_query_logging(self):
        """Configurar logging de consultas"""
        @self.app.before_request
        def before_request():
            db.session.info['query_start_time'] = time.time()
        
        @self.app.after_request
        def after_request(response):
            if hasattr(db.session.info, 'query_start_time'):
                duration = time.time() - db.session.info['query_start_time']
                if duration > self.slow_query_threshold:
                    current_app.logger.warning(f"Slow query detected: {duration:.2f}s")
            return response
    
    def create_optimized_indexes(self):
        """Crear índices optimizados para mejorar rendimiento"""
        try:
            with db.engine.connect() as conn:
                # Índices para tabla users
                self._create_index_if_not_exists(conn, 'users', 'idx_users_email', ['email'])
                self._create_index_if_not_exists(conn, 'users', 'idx_users_username', ['username'])
                self._create_index_if_not_exists(conn, 'users', 'idx_users_role_active', ['role', 'is_active'])
                self._create_index_if_not_exists(conn, 'users', 'idx_users_created_at', ['created_at'])
                
                # Índices para tabla visits
                self._create_index_if_not_exists(conn, 'visits', 'idx_visits_resident_status', ['resident_id', 'status'])
                self._create_index_if_not_exists(conn, 'visits', 'idx_visits_entry_time', ['entry_time'])
                self._create_index_if_not_exists(conn, 'visits', 'idx_visits_created_at', ['created_at'])
                self._create_index_if_not_exists(conn, 'visits', 'idx_visits_qr_code_id', ['qr_code_id'])
                
                # Índices para tabla reservations
                self._create_index_if_not_exists(conn, 'reservations', 'idx_reservations_user_status', ['user_id', 'status'])
                self._create_index_if_not_exists(conn, 'reservations', 'idx_reservations_space_time', ['space_type', 'start_time'])
                self._create_index_if_not_exists(conn, 'reservations', 'idx_reservations_start_time', ['start_time'])
                self._create_index_if_not_exists(conn, 'reservations', 'idx_reservations_created_at', ['created_at'])
                
                # Índices para tabla maintenance
                self._create_index_if_not_exists(conn, 'maintenance', 'idx_maintenance_user_status', ['user_id', 'status'])
                self._create_index_if_not_exists(conn, 'maintenance', 'idx_maintenance_priority_status', ['priority', 'status'])
                self._create_index_if_not_exists(conn, 'maintenance', 'idx_maintenance_created_at', ['created_at'])
                self._create_index_if_not_exists(conn, 'maintenance', 'idx_maintenance_assigned_to', ['assigned_to'])
                
                # Índices para tabla expenses
                self._create_index_if_not_exists(conn, 'expenses', 'idx_expenses_user_status', ['user_id', 'status'])
                self._create_index_if_not_exists(conn, 'expenses', 'idx_expenses_month', ['month'])
                self._create_index_if_not_exists(conn, 'expenses', 'idx_expenses_due_date', ['due_date'])
                self._create_index_if_not_exists(conn, 'expenses', 'idx_expenses_created_at', ['created_at'])
                
                # Índices para tabla news
                self._create_index_if_not_exists(conn, 'news', 'idx_news_published', ['is_published', 'published_at'])
                self._create_index_if_not_exists(conn, 'news', 'idx_news_category', ['category'])
                self._create_index_if_not_exists(conn, 'news', 'idx_news_important', ['is_important'])
                
                # Índices para tabla notifications
                self._create_index_if_not_exists(conn, 'notifications', 'idx_notifications_user_read', ['user_id', 'is_read'])
                self._create_index_if_not_exists(conn, 'notifications', 'idx_notifications_created_at', ['created_at'])
                self._create_index_if_not_exists(conn, 'notifications', 'idx_notifications_category', ['category'])
                
                # Índices para tabla security_reports
                self._create_index_if_not_exists(conn, 'security_reports', 'idx_security_user_status', ['user_id', 'status'])
                self._create_index_if_not_exists(conn, 'security_reports', 'idx_security_severity', ['severity'])
                self._create_index_if_not_exists(conn, 'security_reports', 'idx_security_created_at', ['created_at'])
                
                # Índices para tabla classifieds
                self._create_index_if_not_exists(conn, 'classifieds', 'idx_classifieds_user_active', ['user_id', 'is_active'])
                self._create_index_if_not_exists(conn, 'classifieds', 'idx_classifieds_category', ['category'])
                self._create_index_if_not_exists(conn, 'classifieds', 'idx_classifieds_created_at', ['created_at'])
                
                conn.commit()
                print("✅ Índices optimizados creados")
                
        except Exception as e:
            current_app.logger.error(f"Error creando índices: {str(e)}")
    
    def _create_index_if_not_exists(self, conn, table_name, index_name, columns):
        """Crear índice si no existe"""
        try:
            # Verificar si el índice ya existe
            result = conn.execute(text(f"""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='{index_name}'
            """))
            
            if not result.fetchone():
                columns_str = ', '.join(columns)
                sql = f"CREATE INDEX {index_name} ON {table_name} ({columns_str})"
                conn.execute(text(sql))
                print(f"✅ Índice creado: {index_name}")
            else:
                print(f"ℹ️ Índice ya existe: {index_name}")
                
        except Exception as e:
            print(f"⚠️ Error creando índice {index_name}: {str(e)}")
    
    def analyze_query_performance(self):
        """Analizar rendimiento de consultas"""
        try:
            with db.engine.connect() as conn:
                # Obtener estadísticas de tablas
                tables = ['users', 'visits', 'reservations', 'maintenance', 
                         'expenses', 'news', 'notifications', 'security_reports', 'classifieds']
                
                stats = {}
                for table in tables:
                    try:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.scalar()
                        stats[table] = {'count': count}
                        
                        # Obtener información de índices
                        result = conn.execute(text(f"""
                            SELECT name FROM sqlite_master 
                            WHERE type='index' AND tbl_name='{table}'
                        """))
                        indexes = [row[0] for row in result.fetchall()]
                        stats[table]['indexes'] = indexes
                        
                    except Exception as e:
                        stats[table] = {'error': str(e)}
                
                return stats
                
        except Exception as e:
            current_app.logger.error(f"Error analizando rendimiento: {str(e)}")
            return {}
    
    def optimize_database(self):
        """Ejecutar optimizaciones de base de datos"""
        try:
            with db.engine.connect() as conn:
                # VACUUM para SQLite (reorganizar y compactar)
                conn.execute(text("VACUUM"))
                
                # ANALYZE para actualizar estadísticas
                conn.execute(text("ANALYZE"))
                
                print("✅ Optimización de base de datos completada")
                return True
                
        except Exception as e:
            current_app.logger.error(f"Error optimizando base de datos: {str(e)}")
            return False

class OptimizedQuery:
    """Clase para consultas optimizadas comunes"""
    
    @staticmethod
    def get_user_with_stats(user_id):
        """Obtener usuario con estadísticas optimizado"""
        from models import User, Visit, Reservation, Maintenance, Expense
        
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return None
        
        # Usar subconsultas para evitar N+1
        stats = {
            'visits_count': db.session.query(Visit).filter_by(resident_id=user_id).count(),
            'reservations_count': db.session.query(Reservation).filter_by(user_id=user_id).count(),
            'maintenance_count': db.session.query(Maintenance).filter_by(user_id=user_id).count(),
            'expenses_count': db.session.query(Expense).filter_by(user_id=user_id).count()
        }
        
        return user, stats
    
    @staticmethod
    def get_recent_visits(user_id, limit=10):
        """Obtener visitas recientes optimizado"""
        from models import Visit, User
        
        return db.session.query(Visit)\
            .options(joinedload(Visit.resident))\
            .filter_by(resident_id=user_id)\
            .order_by(Visit.created_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_dashboard_data(user_id):
        """Obtener datos del dashboard optimizado"""
        from models import Visit, Reservation, Maintenance, Expense, News, Notification
        
        # Una sola consulta para cada tipo de dato
        pending_visits = db.session.query(Visit)\
            .filter_by(resident_id=user_id, status='pending')\
            .count()
        
        active_reservations = db.session.query(Reservation)\
            .filter_by(user_id=user_id, status='approved')\
            .count()
        
        pending_maintenance = db.session.query(Maintenance)\
            .filter_by(user_id=user_id, status='pending')\
            .count()
        
        pending_expenses = db.session.query(Expense)\
            .filter_by(user_id=user_id, status='pending')\
            .count()
        
        # Noticias recientes con eager loading
        recent_news = db.session.query(News)\
            .options(joinedload(News.author))\
            .filter_by(is_published=True)\
            .order_by(News.created_at.desc())\
            .limit(5)\
            .all()
        
        # Notificaciones no leídas
        unread_notifications = db.session.query(Notification)\
            .filter_by(user_id=user_id, is_read=False)\
            .order_by(Notification.created_at.desc())\
            .limit(5)\
            .all()
        
        return {
            'pending_visits': pending_visits,
            'active_reservations': active_reservations,
            'pending_maintenance': pending_maintenance,
            'pending_expenses': pending_expenses,
            'recent_news': recent_news,
            'unread_notifications': unread_notifications
        }
    
    @staticmethod
    def get_admin_dashboard_data():
        """Obtener datos del dashboard de admin optimizado"""
        from models import User, Visit, Reservation, Maintenance, Expense
        
        # Estadísticas generales con una sola consulta cada una
        total_users = db.session.query(User).filter_by(is_active=True).count()
        total_visits = db.session.query(Visit).count()
        total_reservations = db.session.query(Reservation).count()
        total_maintenance = db.session.query(Maintenance).count()
        
        # Estadísticas de este mes
        this_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        visits_this_month = db.session.query(Visit)\
            .filter(Visit.created_at >= this_month).count()
        
        reservations_this_month = db.session.query(Reservation)\
            .filter(Reservation.created_at >= this_month).count()
        
        maintenance_this_month = db.session.query(Maintenance)\
            .filter(Maintenance.created_at >= this_month).count()
        
        return {
            'total_users': total_users,
            'total_visits': total_visits,
            'total_reservations': total_reservations,
            'total_maintenance': total_maintenance,
            'visits_this_month': visits_this_month,
            'reservations_this_month': reservations_this_month,
            'maintenance_this_month': maintenance_this_month
        }
    
    @staticmethod
    def get_paginated_results(query, page, per_page=10):
        """Obtener resultados paginados optimizado"""
        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
            max_per_page=100
        )

# Decorador para optimización automática de consultas
def optimize_query(f):
    """Decorador para optimizar consultas automáticamente"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            
            # Registrar tiempo de consulta
            duration = time.time() - start_time
            if hasattr(current_app, 'db_optimizer'):
                current_app.db_optimizer.query_stats[f.__name__].append(duration)
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error in optimized query {f.__name__}: {str(e)}")
            raise
    
    return decorated_function

# Funciones de utilidad para optimización
def bulk_insert(model_class, data_list, batch_size=1000):
    """Inserción masiva optimizada"""
    try:
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            db.session.bulk_insert_mappings(model_class, batch)
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in bulk insert: {str(e)}")
        return False

def bulk_update(model_class, data_list, batch_size=1000):
    """Actualización masiva optimizada"""
    try:
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            db.session.bulk_update_mappings(model_class, batch)
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in bulk update: {str(e)}")
        return False

def execute_raw_query(sql, params=None):
    """Ejecutar consulta SQL raw optimizada"""
    try:
        with db.engine.connect() as conn:
            if params:
                result = conn.execute(text(sql), params)
            else:
                result = conn.execute(text(sql))
            
            return result.fetchall()
            
    except Exception as e:
        current_app.logger.error(f"Error executing raw query: {str(e)}")
        return []

# Instancia global del optimizador
database_optimizer = DatabaseOptimizer()
