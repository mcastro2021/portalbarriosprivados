"""
Servicio de usuarios con patrón Repository
Separación de lógica de negocio de controladores
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from security import validate_input, REGISTER_SCHEMA
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    """Repository para operaciones de base de datos de usuarios"""
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        try:
            return User.query.get(user_id)
        except Exception as e:
            logger.error(f"Error obteniendo usuario por ID {user_id}: {e}")
            return None
    
    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        """Obtener usuario por username"""
        try:
            return User.query.filter_by(username=username).first()
        except Exception as e:
            logger.error(f"Error obteniendo usuario por username {username}: {e}")
            return None
    
    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """Obtener usuario por email"""
        try:
            return User.query.filter_by(email=email).first()
        except Exception as e:
            logger.error(f"Error obteniendo usuario por email {email}: {e}")
            return None
    
    @staticmethod
    def get_all(limit: int = None, offset: int = 0) -> List[User]:
        """Obtener todos los usuarios con paginación"""
        try:
            query = User.query
            if limit:
                query = query.limit(limit).offset(offset)
            return query.all()
        except Exception as e:
            logger.error(f"Error obteniendo usuarios: {e}")
            return []
    
    @staticmethod
    def get_by_role(role: str) -> List[User]:
        """Obtener usuarios por rol"""
        try:
            return User.query.filter_by(role=role).all()
        except Exception as e:
            logger.error(f"Error obteniendo usuarios por rol {role}: {e}")
            return []
    
    @staticmethod
    def create(user_data: Dict[str, Any]) -> Optional[User]:
        """Crear nuevo usuario"""
        try:
            user = User(**user_data)
            db.session.add(user)
            db.session.commit()
            logger.info(f"Usuario creado: {user.username}")
            return user
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creando usuario: {e}")
            return None
    
    @staticmethod
    def update(user: User, user_data: Dict[str, Any]) -> bool:
        """Actualizar usuario"""
        try:
            for key, value in user_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Usuario actualizado: {user.username}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error actualizando usuario {user.username}: {e}")
            return False
    
    @staticmethod
    def delete(user: User) -> bool:
        """Eliminar usuario (soft delete)"""
        try:
            user.is_active = False
            user.deleted_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Usuario desactivado: {user.username}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error eliminando usuario {user.username}: {e}")
            return False
    
    @staticmethod
    def count() -> int:
        """Contar usuarios activos"""
        try:
            return User.query.filter_by(is_active=True).count()
        except Exception as e:
            logger.error(f"Error contando usuarios: {e}")
            return 0

class UserService:
    """Servicio de lógica de negocio para usuarios"""
    
    def __init__(self):
        self.repository = UserRepository()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Autenticar usuario"""
        try:
            user = self.repository.get_by_username(username)
            
            if user and user.check_password(password) and user.is_active:
                # Actualizar último login
                user.last_login = datetime.utcnow()
                db.session.commit()
                logger.info(f"Usuario autenticado: {username}")
                return user
            
            logger.warning(f"Intento de autenticación fallido para: {username}")
            return None
        except Exception as e:
            logger.error(f"Error en autenticación: {e}")
            return None
    
    def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Registrar nuevo usuario"""
        try:
            # Validar datos de entrada
            is_valid, error_message = validate_input(user_data, REGISTER_SCHEMA)
            if not is_valid:
                return {'success': False, 'error': error_message}
            
            # Verificar si el usuario ya existe
            if self.repository.get_by_username(user_data['username']):
                return {'success': False, 'error': 'El nombre de usuario ya está en uso'}
            
            if self.repository.get_by_email(user_data['email']):
                return {'success': False, 'error': 'El email ya está registrado'}
            
            # Hash de la contraseña
            user_data['password_hash'] = generate_password_hash(user_data['password'])
            del user_data['password']
            
            # Valores por defecto
            user_data.update({
                'role': 'resident',
                'is_active': True,
                'email_verified': False,
                'created_at': datetime.utcnow()
            })
            
            # Crear usuario
            user = self.repository.create(user_data)
            if user:
                logger.info(f"Usuario registrado exitosamente: {user.username}")
                return {
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'name': user.name,
                        'role': user.role
                    }
                }
            else:
                return {'success': False, 'error': 'Error al crear el usuario'}
                
        except Exception as e:
            logger.error(f"Error en registro de usuario: {e}")
            return {'success': False, 'error': 'Error interno del servidor'}
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtener perfil de usuario"""
        try:
            user = self.repository.get_by_id(user_id)
            if user and user.is_active:
                return {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'name': user.name,
                    'role': user.role,
                    'address': user.address,
                    'phone': user.phone,
                    'emergency_contact': user.emergency_contact,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
            return None
        except Exception as e:
            logger.error(f"Error obteniendo perfil de usuario {user_id}: {e}")
            return None
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar perfil de usuario"""
        try:
            user = self.repository.get_by_id(user_id)
            if not user or not user.is_active:
                return {'success': False, 'error': 'Usuario no encontrado'}
            
            # Campos permitidos para actualización
            allowed_fields = ['name', 'address', 'phone', 'emergency_contact']
            update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
            
            if self.repository.update(user, update_data):
                return {'success': True, 'message': 'Perfil actualizado correctamente'}
            else:
                return {'success': False, 'error': 'Error al actualizar el perfil'}
                
        except Exception as e:
            logger.error(f"Error actualizando perfil de usuario {user_id}: {e}")
            return {'success': False, 'error': 'Error interno del servidor'}
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
        """Cambiar contraseña de usuario"""
        try:
            user = self.repository.get_by_id(user_id)
            if not user or not user.is_active:
                return {'success': False, 'error': 'Usuario no encontrado'}
            
            # Verificar contraseña actual
            if not user.check_password(current_password):
                return {'success': False, 'error': 'Contraseña actual incorrecta'}
            
            # Validar nueva contraseña
            if len(new_password) < 6:
                return {'success': False, 'error': 'La nueva contraseña debe tener al menos 6 caracteres'}
            
            # Actualizar contraseña
            user.password_hash = generate_password_hash(new_password)
            user.updated_at = datetime.utcnow()
            
            if self.repository.update(user, {}):
                logger.info(f"Contraseña cambiada para usuario: {user.username}")
                return {'success': True, 'message': 'Contraseña cambiada correctamente'}
            else:
                return {'success': False, 'error': 'Error al cambiar la contraseña'}
                
        except Exception as e:
            logger.error(f"Error cambiando contraseña de usuario {user_id}: {e}")
            return {'success': False, 'error': 'Error interno del servidor'}
    
    def get_users_list(self, page: int = 1, per_page: int = 20, role: str = None) -> Dict[str, Any]:
        """Obtener lista de usuarios con paginación"""
        try:
            offset = (page - 1) * per_page
            
            if role:
                users = self.repository.get_by_role(role)
            else:
                users = self.repository.get_all(per_page, offset)
            
            total = self.repository.count()
            
            return {
                'success': True,
                'users': [
                    {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'name': user.name,
                        'role': user.role,
                        'is_active': user.is_active,
                        'created_at': user.created_at.isoformat() if user.created_at else None,
                        'last_login': user.last_login.isoformat() if user.last_login else None
                    }
                    for user in users if user.is_active
                ],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
        except Exception as e:
            logger.error(f"Error obteniendo lista de usuarios: {e}")
            return {'success': False, 'error': 'Error interno del servidor'}

# Instancia global del servicio
user_service = UserService()

# Exportar también las clases para uso directo
__all__ = ['UserService', 'UserRepository', 'user_service']
