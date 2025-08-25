"""
Servicio de gestión de usuarios
"""

from datetime import datetime, timedelta
from flask import current_app
from models import db, User, Notification
from sqlalchemy import func
from app.core.error_handler import ValidationError, BusinessLogicError


class UserService:
    """Servicio para gestión de usuarios"""
    
    @staticmethod
    def get_user_stats(user_id):
        """Obtener estadísticas de un usuario específico"""
        try:
            from models import Visit, Reservation, Maintenance, Expense
            
            user = User.query.get(user_id)
            if not user:
                raise ValidationError("Usuario no encontrado")
            
            # Estadísticas básicas
            pending_visits = Visit.query.filter_by(resident_id=user_id, status='pending').count()
            active_reservations = Reservation.query.filter_by(user_id=user_id, status='approved').count()
            pending_maintenance = Maintenance.query.filter_by(user_id=user_id, status='pending').count()
            pending_expenses = Expense.query.filter_by(user_id=user_id, status='pending').count()
            
            # Estadísticas de hoy
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            today_visits = Visit.query.filter_by(resident_id=user_id).filter(
                Visit.created_at >= today, 
                Visit.created_at < tomorrow
            ).count()
            
            # Notificaciones no leídas
            unread_notifications = Notification.query.filter_by(
                user_id=user_id, 
                is_read=False
            ).count()
            
            return {
                'pending_visits': pending_visits,
                'active_reservations': active_reservations,
                'pending_maintenance': pending_maintenance,
                'pending_expenses': pending_expenses,
                'today_visits': today_visits,
                'unread_notifications': unread_notifications
            }
            
        except Exception as e:
            current_app.logger.error(f'Error obteniendo estadísticas de usuario {user_id}: {e}')
            raise BusinessLogicError(f'Error obteniendo estadísticas: {str(e)}')
    
    @staticmethod
    def get_admin_stats():
        """Obtener estadísticas generales para administradores"""
        try:
            from models import Visit, Reservation, Maintenance, Expense
            
            # Estadísticas generales
            total_users = User.query.filter_by(is_active=True).count()
            total_visits = Visit.query.count()
            total_reservations = Reservation.query.count()
            total_maintenance = Maintenance.query.count()
            
            # Estadísticas de este mes
            this_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            visits_this_month = Visit.query.filter(Visit.created_at >= this_month).count()
            reservations_this_month = Reservation.query.filter(Reservation.created_at >= this_month).count()
            maintenance_this_month = Maintenance.query.filter(Maintenance.created_at >= this_month).count()
            
            # Estadísticas por rol
            residents_count = User.query.filter_by(role='resident', is_active=True).count()
            admins_count = User.query.filter_by(role='admin', is_active=True).count()
            security_count = User.query.filter_by(role='security', is_active=True).count()
            
            return {
                'total_users': total_users,
                'total_visits': total_visits,
                'total_reservations': total_reservations,
                'total_maintenance': total_maintenance,
                'visits_this_month': visits_this_month,
                'reservations_this_month': reservations_this_month,
                'maintenance_this_month': maintenance_this_month,
                'residents_count': residents_count,
                'admins_count': admins_count,
                'security_count': security_count
            }
            
        except Exception as e:
            current_app.logger.error(f'Error obteniendo estadísticas de admin: {e}')
            raise BusinessLogicError(f'Error obteniendo estadísticas: {str(e)}')
    
    @staticmethod
    def get_user_activities(user_id, limit=10):
        """Obtener actividades recientes de un usuario"""
        try:
            from models import Visit, Reservation, Maintenance, News
            
            activities = []
            
            # Visitas recientes
            recent_visits = Visit.query.filter_by(resident_id=user_id).order_by(
                Visit.created_at.desc()
            ).limit(limit//4).all()
            
            for visit in recent_visits:
                activities.append({
                    'type': 'visit',
                    'title': f'Visita de {visit.visitor_name}',
                    'description': f'Estado: {visit.status}',
                    'timestamp': visit.created_at,
                    'icon': 'fas fa-user-friends',
                    'color': 'primary' if visit.status == 'approved' else 'warning'
                })
            
            # Reservas recientes
            recent_reservations = Reservation.query.filter_by(user_id=user_id).order_by(
                Reservation.created_at.desc()
            ).limit(limit//4).all()
            
            for reservation in recent_reservations:
                activities.append({
                    'type': 'reservation',
                    'title': f'Reserva de {reservation.space_name}',
                    'description': f'Estado: {reservation.status}',
                    'timestamp': reservation.created_at,
                    'icon': 'fas fa-calendar-check',
                    'color': 'success' if reservation.status == 'approved' else 'info'
                })
            
            # Mantenimientos recientes
            recent_maintenance = Maintenance.query.filter_by(user_id=user_id).order_by(
                Maintenance.created_at.desc()
            ).limit(limit//4).all()
            
            for maintenance in recent_maintenance:
                activities.append({
                    'type': 'maintenance',
                    'title': f'Reclamo: {maintenance.title}',
                    'description': f'Estado: {maintenance.status}',
                    'timestamp': maintenance.created_at,
                    'icon': 'fas fa-tools',
                    'color': 'danger' if maintenance.priority == 'urgent' else 'secondary'
                })
            
            # Ordenar por timestamp y limitar
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            return activities[:limit]
            
        except Exception as e:
            current_app.logger.error(f'Error obteniendo actividades de usuario {user_id}: {e}')
            return []
    
    @staticmethod
    def update_user_profile(user_id, profile_data):
        """Actualizar perfil de usuario con validación"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValidationError("Usuario no encontrado")
            
            # Validar email si se está cambiando
            if 'email' in profile_data and profile_data['email'] != user.email:
                existing_user = User.query.filter_by(email=profile_data['email']).first()
                if existing_user and existing_user.id != user_id:
                    raise ValidationError("El email ya está en uso por otro usuario")
            
            # Actualizar campos permitidos
            allowed_fields = ['name', 'email', 'phone', 'address', 'emergency_contact']
            for field in allowed_fields:
                if field in profile_data:
                    setattr(user, field, profile_data[field])
            
            # Marcar como modificado
            user.updated_at = datetime.utcnow()
            
            db.session.commit()
            return user
            
        except ValidationError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error actualizando perfil de usuario {user_id}: {e}')
            raise BusinessLogicError(f'Error actualizando perfil: {str(e)}')
    
    @staticmethod
    def get_user_notifications(user_id, page=1, per_page=10, unread_only=False):
        """Obtener notificaciones de usuario con paginación"""
        try:
            query = Notification.query.filter_by(user_id=user_id)
            
            if unread_only:
                query = query.filter_by(is_read=False)
            
            notifications = query.order_by(
                Notification.created_at.desc()
            ).paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return notifications
            
        except Exception as e:
            current_app.logger.error(f'Error obteniendo notificaciones de usuario {user_id}: {e}')
            raise BusinessLogicError(f'Error obteniendo notificaciones: {str(e)}')
    
    @staticmethod
    def mark_notification_read(user_id, notification_id):
        """Marcar notificación como leída"""
        try:
            notification = Notification.query.filter_by(
                id=notification_id, 
                user_id=user_id
            ).first()
            
            if not notification:
                raise ValidationError("Notificación no encontrada")
            
            notification.mark_as_read()
            db.session.commit()
            
            return notification
            
        except ValidationError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error marcando notificación {notification_id} como leída: {e}')
            raise BusinessLogicError(f'Error marcando notificación: {str(e)}')
    
    @staticmethod
    def mark_all_notifications_read(user_id):
        """Marcar todas las notificaciones como leídas"""
        try:
            updated_count = Notification.query.filter_by(
                user_id=user_id, 
                is_read=False
            ).update({
                'is_read': True, 
                'read_at': datetime.utcnow()
            })
            
            db.session.commit()
            return updated_count
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error marcando todas las notificaciones como leídas para usuario {user_id}: {e}')
            raise BusinessLogicError(f'Error marcando notificaciones: {str(e)}')
    
    @staticmethod
    def create_notification(user_id, title, message, category='general', related_id=None, related_type=None):
        """Crear nueva notificación para usuario"""
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type='push',
                category=category,
                related_id=related_id,
                related_type=related_type
            )
            
            db.session.add(notification)
            db.session.commit()
            
            return notification
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creando notificación para usuario {user_id}: {e}')
            raise BusinessLogicError(f'Error creando notificación: {str(e)}')
