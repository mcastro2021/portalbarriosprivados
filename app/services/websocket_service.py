"""
Servicio de WebSockets robusto para tiempo real
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import current_app, request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room, disconnect
from collections import defaultdict
import uuid

try:
    from flask_socketio import SocketIO
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    SocketIO = None


class WebSocketService:
    """Servicio para manejo de WebSockets en tiempo real"""
    
    _socketio = None
    _connected_users = {}  # {session_id: user_info}
    _user_sessions = defaultdict(set)  # {user_id: {session_ids}}
    _room_members = defaultdict(set)  # {room: {session_ids}}
    _message_queue = defaultdict(list)  # {user_id: [messages]}
    
    @classmethod
    def init_app(cls, app, socketio_instance=None):
        """Inicializar servicio WebSocket con la aplicación"""
        if not SOCKETIO_AVAILABLE:
            app.logger.warning("⚠️ SocketIO no disponible - WebSockets deshabilitados")
            return False
        
        try:
            if socketio_instance:
                cls._socketio = socketio_instance
            else:
                cls._socketio = SocketIO(
                    app,
                    async_mode='threading',
                    cors_allowed_origins="*",
                    logger=False,
                    engineio_logger=False,
                    manage_session=False,
                    ping_timeout=60,
                    ping_interval=25
                )
            
            # Registrar event handlers
            cls._register_handlers()
            
            app.logger.info("✅ WebSocket service inicializado correctamente")
            return True
            
        except Exception as e:
            app.logger.error(f"❌ Error inicializando WebSocket service: {e}")
            return False
    
    @classmethod
    def _register_handlers(cls):
        """Registrar manejadores de eventos WebSocket"""
        
        @cls._socketio.on('connect')
        def handle_connect(auth=None):
            """Manejar nueva conexión WebSocket"""
            try:
                session_id = request.sid
                user_info = {
                    'session_id': session_id,
                    'user_id': current_user.id if current_user.is_authenticated else None,
                    'username': current_user.username if current_user.is_authenticated else 'Anonymous',
                    'role': current_user.role if current_user.is_authenticated else 'guest',
                    'connected_at': datetime.utcnow(),
                    'ip_address': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', 'Unknown')
                }
                
                cls._connected_users[session_id] = user_info
                
                if current_user.is_authenticated:
                    cls._user_sessions[current_user.id].add(session_id)
                    
                    # Unirse a sala personal
                    join_room(f'user_{current_user.id}')
                    
                    # Unirse a sala de rol
                    join_room(f'role_{current_user.role}')
                    
                    # Enviar mensajes en cola
                    cls._send_queued_messages(current_user.id)
                
                # Emitir confirmación de conexión
                emit('connected', {
                    'session_id': session_id,
                    'user_id': user_info['user_id'],
                    'username': user_info['username'],
                    'timestamp': user_info['connected_at'].isoformat(),
                    'server_time': datetime.utcnow().isoformat()
                })
                
                # Log conexión
                current_app.logger.info(f'WebSocket conectado: {user_info["username"]} ({session_id})')
                
                return True
                
            except Exception as e:
                current_app.logger.error(f'Error en conexión WebSocket: {e}')
                return False
        
        @cls._socketio.on('disconnect')
        def handle_disconnect():
            """Manejar desconexión WebSocket"""
            try:
                session_id = request.sid
                user_info = cls._connected_users.get(session_id)
                
                if user_info:
                    user_id = user_info['user_id']
                    
                    # Remover de salas
                    if user_id:
                        cls._user_sessions[user_id].discard(session_id)
                        leave_room(f'user_{user_id}')
                        leave_room(f'role_{user_info["role"]}')
                    
                    # Remover de todas las salas personalizadas
                    for room, members in cls._room_members.items():
                        if session_id in members:
                            members.discard(session_id)
                            leave_room(room)
                    
                    # Remover de usuarios conectados
                    del cls._connected_users[session_id]
                    
                    # Log desconexión
                    current_app.logger.info(f'WebSocket desconectado: {user_info["username"]} ({session_id})')
                
            except Exception as e:
                current_app.logger.error(f'Error en desconexión WebSocket: {e}')
        
        @cls._socketio.on('join_room')
        def handle_join_room(data):
            """Unirse a una sala específica"""
            try:
                if not current_user.is_authenticated:
                    emit('error', {'message': 'Autenticación requerida'})
                    return
                
                room = data.get('room')
                if not room:
                    emit('error', {'message': 'Nombre de sala requerido'})
                    return
                
                # Validar permisos para unirse a la sala
                if not cls._can_join_room(current_user, room):
                    emit('error', {'message': 'Sin permisos para unirse a esta sala'})
                    return
                
                session_id = request.sid
                join_room(room)
                cls._room_members[room].add(session_id)
                
                emit('joined_room', {
                    'room': room,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                # Notificar a otros miembros de la sala
                emit('user_joined', {
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=room, include_self=False)
                
            except Exception as e:
                current_app.logger.error(f'Error uniéndose a sala: {e}')
                emit('error', {'message': 'Error uniéndose a la sala'})
        
        @cls._socketio.on('leave_room')
        def handle_leave_room(data):
            """Salir de una sala específica"""
            try:
                room = data.get('room')
                if not room:
                    return
                
                session_id = request.sid
                leave_room(room)
                cls._room_members[room].discard(session_id)
                
                emit('left_room', {
                    'room': room,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                # Notificar a otros miembros
                if current_user.is_authenticated:
                    emit('user_left', {
                        'user_id': current_user.id,
                        'username': current_user.username,
                        'timestamp': datetime.utcnow().isoformat()
                    }, room=room)
                
            except Exception as e:
                current_app.logger.error(f'Error saliendo de sala: {e}')
        
        @cls._socketio.on('ping')
        def handle_ping():
            """Responder a ping para mantener conexión"""
            emit('pong', {'timestamp': datetime.utcnow().isoformat()})
        
        @cls._socketio.on('message')
        def handle_message(data):
            """Manejar mensaje genérico"""
            try:
                if not current_user.is_authenticated:
                    emit('error', {'message': 'Autenticación requerida'})
                    return
                
                message_type = data.get('type', 'general')
                content = data.get('content', '')
                target = data.get('target')  # user_id, room, etc.
                
                # Procesar según tipo de mensaje
                cls._process_message(message_type, content, target)
                
            except Exception as e:
                current_app.logger.error(f'Error procesando mensaje: {e}')
                emit('error', {'message': 'Error procesando mensaje'})
    
    @classmethod
    def _can_join_room(cls, user, room):
        """Verificar si un usuario puede unirse a una sala"""
        # Salas públicas
        public_rooms = ['general', 'announcements']
        if room in public_rooms:
            return True
        
        # Salas de administrador
        admin_rooms = ['admin', 'admin_notifications']
        if room in admin_rooms:
            return user.can_access_admin()
        
        # Salas de seguridad
        security_rooms = ['security', 'security_alerts']
        if room in security_rooms:
            return user.role in ['admin', 'security']
        
        # Salas privadas (user_X)
        if room.startswith('user_'):
            try:
                target_user_id = int(room.split('_')[1])
                return user.id == target_user_id or user.can_access_admin()
            except (ValueError, IndexError):
                return False
        
        return False
    
    @classmethod
    def _process_message(cls, message_type, content, target):
        """Procesar mensaje según su tipo"""
        try:
            message_data = {
                'id': str(uuid.uuid4()),
                'type': message_type,
                'content': content,
                'sender': {
                    'id': current_user.id,
                    'username': current_user.username,
                    'name': current_user.name
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if message_type == 'notification':
                cls._send_notification_message(message_data, target)
            elif message_type == 'chat':
                cls._send_chat_message(message_data, target)
            elif message_type == 'system':
                cls._send_system_message(message_data, target)
            else:
                # Mensaje general
                emit('message', message_data)
                
        except Exception as e:
            current_app.logger.error(f'Error procesando mensaje tipo {message_type}: {e}')
    
    @classmethod
    def _send_notification_message(cls, message_data, target):
        """Enviar mensaje de notificación"""
        if target:
            if isinstance(target, int):
                # Enviar a usuario específico
                cls.send_to_user(target, 'notification', message_data)
            elif isinstance(target, str):
                # Enviar a sala específica
                cls.send_to_room(target, 'notification', message_data)
        else:
            # Broadcast a todos los usuarios autenticados
            cls.broadcast_to_authenticated('notification', message_data)
    
    @classmethod
    def _send_chat_message(cls, message_data, target):
        """Enviar mensaje de chat"""
        if target:
            cls.send_to_room(target, 'chat_message', message_data)
    
    @classmethod
    def _send_system_message(cls, message_data, target):
        """Enviar mensaje del sistema"""
        if target:
            cls.send_to_room(target, 'system_message', message_data)
        else:
            cls.broadcast('system_message', message_data)
    
    @classmethod
    def _send_queued_messages(cls, user_id):
        """Enviar mensajes en cola para un usuario"""
        if user_id in cls._message_queue:
            messages = cls._message_queue[user_id]
            for message in messages:
                cls.send_to_user(user_id, message['event'], message['data'])
            # Limpiar cola
            del cls._message_queue[user_id]
    
    @classmethod
    def send_to_user(cls, user_id, event, data):
        """Enviar mensaje a un usuario específico"""
        if not cls._socketio:
            # Agregar a cola si WebSocket no está disponible
            cls._message_queue[user_id].append({
                'event': event,
                'data': data,
                'timestamp': datetime.utcnow()
            })
            return False
        
        try:
            room = f'user_{user_id}'
            cls._socketio.emit(event, data, room=room)
            return True
        except Exception as e:
            current_app.logger.error(f'Error enviando mensaje a usuario {user_id}: {e}')
            return False
    
    @classmethod
    def send_to_room(cls, room, event, data):
        """Enviar mensaje a una sala específica"""
        if not cls._socketio:
            return False
        
        try:
            cls._socketio.emit(event, data, room=room)
            return True
        except Exception as e:
            current_app.logger.error(f'Error enviando mensaje a sala {room}: {e}')
            return False
    
    @classmethod
    def broadcast(cls, event, data):
        """Broadcast mensaje a todos los usuarios conectados"""
        if not cls._socketio:
            return False
        
        try:
            cls._socketio.emit(event, data, broadcast=True)
            return True
        except Exception as e:
            current_app.logger.error(f'Error en broadcast: {e}')
            return False
    
    @classmethod
    def broadcast_to_authenticated(cls, event, data):
        """Broadcast solo a usuarios autenticados"""
        if not cls._socketio:
            return False
        
        try:
            # Enviar a todas las salas de usuarios autenticados
            for user_id in cls._user_sessions.keys():
                cls.send_to_user(user_id, event, data)
            return True
        except Exception as e:
            current_app.logger.error(f'Error en broadcast a autenticados: {e}')
            return False
    
    @classmethod
    def broadcast_to_role(cls, role, event, data):
        """Broadcast a usuarios con un rol específico"""
        if not cls._socketio:
            return False
        
        try:
            room = f'role_{role}'
            cls._socketio.emit(event, data, room=room)
            return True
        except Exception as e:
            current_app.logger.error(f'Error en broadcast a rol {role}: {e}')
            return False
    
    @classmethod
    def get_connected_users(cls):
        """Obtener lista de usuarios conectados"""
        return {
            'total': len(cls._connected_users),
            'authenticated': len(cls._user_sessions),
            'users': [
                {
                    'session_id': info['session_id'],
                    'user_id': info['user_id'],
                    'username': info['username'],
                    'role': info['role'],
                    'connected_at': info['connected_at'].isoformat()
                }
                for info in cls._connected_users.values()
            ]
        }
    
    @classmethod
    def get_room_members(cls, room):
        """Obtener miembros de una sala"""
        session_ids = cls._room_members.get(room, set())
        members = []
        
        for session_id in session_ids:
            user_info = cls._connected_users.get(session_id)
            if user_info:
                members.append({
                    'session_id': session_id,
                    'user_id': user_info['user_id'],
                    'username': user_info['username'],
                    'role': user_info['role']
                })
        
        return members
    
    @classmethod
    def disconnect_user(cls, user_id, reason="Desconectado por administrador"):
        """Desconectar un usuario específico"""
        if not cls._socketio:
            return False
        
        try:
            session_ids = cls._user_sessions.get(user_id, set()).copy()
            for session_id in session_ids:
                cls._socketio.emit('force_disconnect', {
                    'reason': reason,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=session_id)
                cls._socketio.disconnect(session_id)
            
            return len(session_ids) > 0
        except Exception as e:
            current_app.logger.error(f'Error desconectando usuario {user_id}: {e}')
            return False
    
    @classmethod
    def get_stats(cls):
        """Obtener estadísticas del servicio WebSocket"""
        return {
            'connected_users': len(cls._connected_users),
            'authenticated_users': len(cls._user_sessions),
            'active_rooms': len(cls._room_members),
            'queued_messages': sum(len(queue) for queue in cls._message_queue.values()),
            'socketio_available': cls._socketio is not None
        }
