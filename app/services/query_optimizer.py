"""
Servicio de optimización de consultas de base de datos
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from flask import current_app
from sqlalchemy import func, text
from sqlalchemy.orm import joinedload, selectinload, subqueryload
from models import db, User, Visit, Reservation, News, Maintenance, Expense, Notification
from app.services.cache_service import CacheService, cached


class QueryOptimizer:
    """Optimizador de consultas de base de datos"""
    
    @staticmethod
    @cached(expire=300, key_prefix="dashboard_stats")
    def get_dashboard_stats_optimized(user_id: int) -> Dict[str, Any]:
        """
        Obtener estadísticas del dashboard con consultas optimizadas
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Dict con estadísticas optimizadas
        """
        try:
            # Una sola consulta para obtener todas las estadísticas
            stats_query = db.session.query(
                # Visitas pendientes
                func.count(Visit.id).filter(
                    Visit.resident_id == user_id,
                    Visit.status == 'pending'
                ).label('pending_visits'),
                
                # Reservas activas
                func.count(Reservation.id).filter(
                    Reservation.user_id == user_id,
                    Reservation.status == 'approved'
                ).label('active_reservations'),
                
                # Mantenimientos pendientes
                func.count(Maintenance.id).filter(
                    Maintenance.user_id == user_id,
                    Maintenance.status == 'pending'
                ).label('pending_maintenance'),
                
                # Gastos pendientes
                func.count(Expense.id).filter(
                    Expense.user_id == user_id,
                    Expense.status == 'pending'
                ).label('pending_expenses'),
                
                # Notificaciones no leídas
                func.count(Notification.id).filter(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                ).label('unread_notifications')
            ).first()
            
            # Visitas de hoy (consulta separada optimizada)
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            today_visits = db.session.query(func.count(Visit.id)).filter(
                Visit.resident_id == user_id,
                Visit.created_at >= today,
                Visit.created_at < tomorrow
            ).scalar()
            
            return {
                'pending_visits': stats_query.pending_visits or 0,
                'active_reservations': stats_query.active_reservations or 0,
                'pending_maintenance': stats_query.pending_maintenance or 0,
                'pending_expenses': stats_query.pending_expenses or 0,
                'unread_notifications': stats_query.unread_notifications or 0,
                'today_visits': today_visits or 0
            }
            
        except Exception as e:
            current_app.logger.error(f'Error en dashboard stats optimizado: {e}')
            return {
                'pending_visits': 0,
                'active_reservations': 0,
                'pending_maintenance': 0,
                'pending_expenses': 0,
                'unread_notifications': 0,
                'today_visits': 0
            }
    
    @staticmethod
    @cached(expire=600, key_prefix="admin_stats")
    def get_admin_stats_optimized() -> Dict[str, Any]:
        """
        Obtener estadísticas de administrador con consultas optimizadas
        
        Returns:
            Dict con estadísticas de administrador
        """
        try:
            # Consulta optimizada con subconsultas
            this_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Estadísticas generales en una sola consulta
            general_stats = db.session.query(
                func.count(User.id).filter(User.is_active == True).label('total_users'),
                func.count(Visit.id).label('total_visits'),
                func.count(Reservation.id).label('total_reservations'),
                func.count(Maintenance.id).label('total_maintenance')
            ).select_from(
                User.outerjoin(Visit, Visit.resident_id == User.id)
                    .outerjoin(Reservation, Reservation.user_id == User.id)
                    .outerjoin(Maintenance, Maintenance.user_id == User.id)
            ).first()
            
            # Estadísticas del mes actual
            monthly_stats = db.session.query(
                func.count(Visit.id).filter(Visit.created_at >= this_month).label('visits_this_month'),
                func.count(Reservation.id).filter(Reservation.created_at >= this_month).label('reservations_this_month'),
                func.count(Maintenance.id).filter(Maintenance.created_at >= this_month).label('maintenance_this_month')
            ).first()
            
            # Estadísticas por rol
            role_stats = db.session.query(
                User.role,
                func.count(User.id).label('count')
            ).filter(User.is_active == True).group_by(User.role).all()
            
            role_counts = {role: count for role, count in role_stats}
            
            return {
                'total_users': general_stats.total_users or 0,
                'total_visits': general_stats.total_visits or 0,
                'total_reservations': general_stats.total_reservations or 0,
                'total_maintenance': general_stats.total_maintenance or 0,
                'visits_this_month': monthly_stats.visits_this_month or 0,
                'reservations_this_month': monthly_stats.reservations_this_month or 0,
                'maintenance_this_month': monthly_stats.maintenance_this_month or 0,
                'residents_count': role_counts.get('resident', 0),
                'admins_count': role_counts.get('admin', 0),
                'security_count': role_counts.get('security', 0)
            }
            
        except Exception as e:
            current_app.logger.error(f'Error en admin stats optimizado: {e}')
            return {}
    
    @staticmethod
    def get_user_activities_optimized(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtener actividades de usuario con eager loading
        
        Args:
            user_id: ID del usuario
            limit: Límite de actividades
            
        Returns:
            Lista de actividades optimizada
        """
        try:
            activities = []
            
            # Visitas recientes con eager loading
            recent_visits = db.session.query(Visit).options(
                selectinload(Visit.resident)
            ).filter(
                Visit.resident_id == user_id
            ).order_by(
                Visit.created_at.desc()
            ).limit(limit // 3).all()
            
            for visit in recent_visits:
                activities.append({
                    'type': 'visit',
                    'title': f'Visita de {visit.visitor_name}',
                    'description': f'Estado: {visit.status}',
                    'timestamp': visit.created_at,
                    'icon': 'fas fa-user-friends',
                    'color': 'primary' if visit.status == 'approved' else 'warning',
                    'id': visit.id
                })
            
            # Reservas recientes con eager loading
            recent_reservations = db.session.query(Reservation).options(
                selectinload(Reservation.user)
            ).filter(
                Reservation.user_id == user_id
            ).order_by(
                Reservation.created_at.desc()
            ).limit(limit // 3).all()
            
            for reservation in recent_reservations:
                activities.append({
                    'type': 'reservation',
                    'title': f'Reserva de {reservation.space_name}',
                    'description': f'Estado: {reservation.status}',
                    'timestamp': reservation.created_at,
                    'icon': 'fas fa-calendar-check',
                    'color': 'success' if reservation.status == 'approved' else 'info',
                    'id': reservation.id
                })
            
            # Mantenimientos recientes con eager loading
            recent_maintenance = db.session.query(Maintenance).options(
                selectinload(Maintenance.user)
            ).filter(
                Maintenance.user_id == user_id
            ).order_by(
                Maintenance.created_at.desc()
            ).limit(limit // 3).all()
            
            for maintenance in recent_maintenance:
                activities.append({
                    'type': 'maintenance',
                    'title': f'Reclamo: {maintenance.title}',
                    'description': f'Estado: {maintenance.status}',
                    'timestamp': maintenance.created_at,
                    'icon': 'fas fa-tools',
                    'color': 'danger' if maintenance.priority == 'urgent' else 'secondary',
                    'id': maintenance.id
                })
            
            # Ordenar por timestamp y limitar
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            return activities[:limit]
            
        except Exception as e:
            current_app.logger.error(f'Error en actividades optimizadas: {e}')
            return []
    
    @staticmethod
    def get_notifications_optimized(user_id: int, page: int = 1, per_page: int = 10, unread_only: bool = False):
        """
        Obtener notificaciones con paginación optimizada
        
        Args:
            user_id: ID del usuario
            page: Página actual
            per_page: Elementos por página
            unread_only: Solo no leídas
            
        Returns:
            Objeto de paginación optimizado
        """
        try:
            query = db.session.query(Notification).filter(
                Notification.user_id == user_id
            )
            
            if unread_only:
                query = query.filter(Notification.is_read == False)
            
            # Usar índices para optimizar ordenamiento
            notifications = query.order_by(
                Notification.created_at.desc()
            ).paginate(
                page=page,
                per_page=per_page,
                error_out=False,
                max_per_page=50  # Límite máximo para evitar consultas muy grandes
            )
            
            return notifications
            
        except Exception as e:
            current_app.logger.error(f'Error en notificaciones optimizadas: {e}')
            return None
    
    @staticmethod
    @cached(expire=1800, key_prefix="recent_news")
    def get_recent_news_optimized(limit: int = 5) -> List[News]:
        """
        Obtener noticias recientes con cache
        
        Args:
            limit: Límite de noticias
            
        Returns:
            Lista de noticias optimizada
        """
        try:
            return db.session.query(News).filter(
                News.is_published == True
            ).order_by(
                News.created_at.desc()
            ).limit(limit).all()
            
        except Exception as e:
            current_app.logger.error(f'Error en noticias optimizadas: {e}')
            return []
    
    @staticmethod
    def get_upcoming_reservations_optimized(user_id: int, limit: int = 3) -> List[Reservation]:
        """
        Obtener próximas reservas con consulta optimizada
        
        Args:
            user_id: ID del usuario
            limit: Límite de reservas
            
        Returns:
            Lista de reservas optimizada
        """
        try:
            return db.session.query(Reservation).options(
                selectinload(Reservation.user)
            ).filter(
                Reservation.user_id == user_id,
                Reservation.status == 'approved',
                Reservation.start_time > datetime.utcnow()
            ).order_by(
                Reservation.start_time
            ).limit(limit).all()
            
        except Exception as e:
            current_app.logger.error(f'Error en reservas optimizadas: {e}')
            return []
    
    @staticmethod
    def get_pending_visits_optimized(user_id: int, limit: int = 3) -> List[Visit]:
        """
        Obtener visitas pendientes con consulta optimizada
        
        Args:
            user_id: ID del usuario
            limit: Límite de visitas
            
        Returns:
            Lista de visitas optimizada
        """
        try:
            return db.session.query(Visit).options(
                selectinload(Visit.resident)
            ).filter(
                Visit.resident_id == user_id,
                Visit.status == 'pending'
            ).order_by(
                Visit.entry_time
            ).limit(limit).all()
            
        except Exception as e:
            current_app.logger.error(f'Error en visitas optimizadas: {e}')
            return []
    
    @staticmethod
    def optimize_database():
        """
        Ejecutar optimizaciones de base de datos
        
        Returns:
            Dict con resultados de optimización
        """
        try:
            results = {}
            
            # Analizar tablas (SQLite)
            if 'sqlite' in str(db.engine.url):
                db.session.execute(text('ANALYZE'))
                results['analyze'] = 'completed'
            
            # Vacuum para SQLite
            if 'sqlite' in str(db.engine.url):
                db.session.execute(text('VACUUM'))
                results['vacuum'] = 'completed'
            
            # Reindexar
            if 'sqlite' in str(db.engine.url):
                db.session.execute(text('REINDEX'))
                results['reindex'] = 'completed'
            
            db.session.commit()
            
            current_app.logger.info('Optimización de base de datos completada')
            return results
            
        except Exception as e:
            current_app.logger.error(f'Error en optimización de BD: {e}')
            return {'error': str(e)}
    
    @staticmethod
    def get_query_performance_stats() -> Dict[str, Any]:
        """
        Obtener estadísticas de rendimiento de consultas
        
        Returns:
            Dict con estadísticas de rendimiento
        """
        try:
            stats = {}
            
            # Contar registros por tabla
            tables = [
                ('users', User),
                ('visits', Visit),
                ('reservations', Reservation),
                ('news', News),
                ('maintenance', Maintenance),
                ('expenses', Expense),
                ('notifications', Notification)
            ]
            
            for table_name, model in tables:
                count = db.session.query(func.count(model.id)).scalar()
                stats[f'{table_name}_count'] = count
            
            # Estadísticas de cache
            cache_stats = CacheService.get_stats()
            stats['cache'] = cache_stats
            
            # Información de la base de datos
            if 'sqlite' in str(db.engine.url):
                # Para SQLite, obtener información de la base de datos
                db_info = db.session.execute(text('PRAGMA database_list')).fetchall()
                stats['database_info'] = [dict(row) for row in db_info]
            
            return stats
            
        except Exception as e:
            current_app.logger.error(f'Error obteniendo stats de rendimiento: {e}')
            return {'error': str(e)}
    
    @staticmethod
    def create_indexes():
        """
        Crear índices para optimizar consultas frecuentes
        
        Returns:
            Dict con resultados de creación de índices
        """
        try:
            indexes = [
                # Índices para visitas
                'CREATE INDEX IF NOT EXISTS idx_visits_resident_status ON visits(resident_id, status)',
                'CREATE INDEX IF NOT EXISTS idx_visits_created_at ON visits(created_at)',
                
                # Índices para reservas
                'CREATE INDEX IF NOT EXISTS idx_reservations_user_status ON reservations(user_id, status)',
                'CREATE INDEX IF NOT EXISTS idx_reservations_start_time ON reservations(start_time)',
                
                # Índices para mantenimiento
                'CREATE INDEX IF NOT EXISTS idx_maintenance_user_status ON maintenance(user_id, status)',
                'CREATE INDEX IF NOT EXISTS idx_maintenance_priority ON maintenance(priority)',
                
                # Índices para notificaciones
                'CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read)',
                'CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at)',
                
                # Índices para usuarios
                'CREATE INDEX IF NOT EXISTS idx_users_active_role ON users(is_active, role)',
                'CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)',
                
                # Índices para noticias
                'CREATE INDEX IF NOT EXISTS idx_news_published_created ON news(is_published, created_at)'
            ]
            
            created_count = 0
            for index_sql in indexes:
                try:
                    db.session.execute(text(index_sql))
                    created_count += 1
                except Exception as e:
                    current_app.logger.warning(f'Error creando índice: {e}')
            
            db.session.commit()
            
            return {
                'indexes_created': created_count,
                'total_attempted': len(indexes),
                'status': 'completed'
            }
            
        except Exception as e:
            current_app.logger.error(f'Error creando índices: {e}')
            return {'error': str(e)}
