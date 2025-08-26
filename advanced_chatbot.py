"""
Fase 2: Chatbot Inteligente Avanzado
Sistema de chatbot inteligente con capacidades avanzadas de automatización y contexto.
"""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from threading import Thread
import openai
import anthropic
from flask import current_app, request

from models import db, User, ChatbotSession, Maintenance, Visit, Reservation, Notification
from knowledge_base import BarrioKnowledgeBase
from intelligent_automation import automation_manager, AutomationType


class ChatbotMode(Enum):
    """Modos de operación del chatbot"""
    CONVERSATIONAL = "conversational"
    TASK_EXECUTION = "task_execution"
    INFORMATION_RETRIEVAL = "information_retrieval"
    AUTOMATION_TRIGGER = "automation_trigger"
    EMERGENCY_RESPONSE = "emergency_response"


class IntentType(Enum):
    """Tipos de intenciones reconocidas"""
    GREETING = "greeting"
    GOODBYE = "goodbye"
    HELP = "help"
    MAINTENANCE_REQUEST = "maintenance_request"
    VISIT_SCHEDULE = "visit_schedule"
    RESERVATION_BOOK = "reservation_book"
    PAYMENT_QUERY = "payment_query"
    SECURITY_REPORT = "security_report"
    GENERAL_QUERY = "general_query"
    AUTOMATION_REQUEST = "automation_request"
    EMERGENCY = "emergency"


@dataclass
class ChatbotContext:
    """Contexto de la conversación del chatbot"""
    user_id: int
    session_id: str
    current_mode: ChatbotMode
    conversation_history: List[Dict]
    user_preferences: Dict
    current_task: Optional[Dict] = None
    context_data: Dict = None
    
    def __post_init__(self):
        if self.context_data is None:
            self.context_data = {}


class AdvancedChatbotEngine:
    """Motor de chatbot inteligente avanzado"""
    
    def __init__(self):
        self.knowledge_base = BarrioKnowledgeBase()
        self.logger = logging.getLogger(__name__)
        self.active_sessions = {}
        self.intent_patterns = self._load_intent_patterns()
        self.response_templates = self._load_response_templates()
        
    def _load_intent_patterns(self) -> Dict:
        """Cargar patrones de reconocimiento de intenciones"""
        return {
            IntentType.GREETING: [
                r'\b(hola|buenos días|buenas tardes|buenas noches|saludos)\b',
                r'\b(hello|hi|good morning|good afternoon|good evening)\b'
            ],
            IntentType.GOODBYE: [
                r'\b(adiós|hasta luego|nos vemos|chao|bye)\b',
                r'\b(goodbye|see you|bye bye|farewell)\b'
            ],
            IntentType.HELP: [
                r'\b(ayuda|soporte|asistencia|help|support)\b',
                r'\b(qué puedes hacer|what can you do|funciones|features)\b'
            ],
            IntentType.MAINTENANCE_REQUEST: [
                r'\b(mantenimiento|reparación|arreglar|fix|repair|maintenance)\b',
                r'\b(problema con|issue with|broken|dañado|averiado)\b'
            ],
            IntentType.VISIT_SCHEDULE: [
                r'\b(visita|visitante|visitor|schedule visit|agendar visita)\b',
                r'\b(invitado|guest|invitar|invite)\b'
            ],
            IntentType.RESERVATION_BOOK: [
                r'\b(reserva|reservar|booking|book|reservation)\b',
                r'\b(salón|espacio común|common area|hall|room)\b'
            ],
            IntentType.PAYMENT_QUERY: [
                r'\b(pago|cuota|payment|fee|bill|invoice)\b',
                r'\b(cuánto debo|how much|balance|saldo)\b'
            ],
            IntentType.SECURITY_REPORT: [
                r'\b(seguridad|security|incidente|incident|alerta|alert)\b',
                r'\b(sospechoso|suspicious|emergencia|emergency)\b'
            ],
            IntentType.AUTOMATION_REQUEST: [
                r'\b(automatizar|automate|programar|schedule|automático|automatic)\b',
                r'\b(recordatorio|reminder|notificación automática|auto notification)\b'
            ],
            IntentType.EMERGENCY: [
                r'\b(emergencia|emergency|urgente|urgent|peligro|danger)\b',
                r'\b(ayuda inmediata|immediate help|socorro|help)\b'
            ]
        }
    
    def _load_response_templates(self) -> Dict:
        """Cargar plantillas de respuesta"""
        return {
            IntentType.GREETING: [
                "¡Hola! Soy el asistente virtual del barrio. ¿En qué puedo ayudarte hoy?",
                "¡Buenos días! Estoy aquí para asistirte con cualquier consulta del barrio.",
                "¡Hola! ¿Cómo puedo ser útil hoy?"
            ],
            IntentType.GOODBYE: [
                "¡Hasta luego! No dudes en volver si necesitas ayuda.",
                "¡Que tengas un buen día! Estoy aquí cuando me necesites.",
                "¡Adiós! Ha sido un placer ayudarte."
            ],
            IntentType.HELP: [
                "Puedo ayudarte con:\n• Solicitudes de mantenimiento\n• Programación de visitas\n• Reservas de espacios comunes\n• Consultas de pagos\n• Reportes de seguridad\n• Y mucho más. ¿Qué necesitas?",
                "Mis funciones incluyen:\n• Gestión de mantenimiento\n• Control de visitas\n• Reservas\n• Pagos\n• Seguridad\n¿En qué área te puedo asistir?"
            ],
            IntentType.MAINTENANCE_REQUEST: [
                "Entiendo que necesitas reportar un problema de mantenimiento. Te ayudo a crear la solicitud.",
                "Perfecto, vamos a reportar el problema de mantenimiento. Necesito algunos detalles."
            ],
            IntentType.VISIT_SCHEDULE: [
                "Te ayudo a programar la visita. Necesito algunos datos del visitante.",
                "Perfecto, vamos a agendar la visita. ¿Cuándo planeas recibir al visitante?"
            ],
            IntentType.RESERVATION_BOOK: [
                "Te ayudo con la reserva del espacio común. ¿Qué espacio necesitas y para cuándo?",
                "Perfecto, vamos a hacer la reserva. Necesito saber el espacio y la fecha."
            ],
            IntentType.PAYMENT_QUERY: [
                "Te ayudo con la consulta de pagos. Déjame verificar tu información.",
                "Perfecto, voy a revisar tu estado de cuenta y pagos pendientes."
            ],
            IntentType.SECURITY_REPORT: [
                "Entiendo que necesitas reportar un incidente de seguridad. Esto es importante.",
                "Perfecto, vamos a reportar el incidente de seguridad. Necesito los detalles."
            ],
            IntentType.AUTOMATION_REQUEST: [
                "Te ayudo a configurar automatizaciones. ¿Qué proceso quieres automatizar?",
                "Perfecto, vamos a configurar la automatización. ¿Qué tipo de recordatorio necesitas?"
            ],
            IntentType.EMERGENCY: [
                "🚨 EMERGENCIA DETECTADA 🚨\nEstoy activando el protocolo de emergencia. ¿Cuál es la situación?",
                "🚨 ALERTA DE EMERGENCIA 🚨\nVoy a notificar inmediatamente al equipo de seguridad."
            ]
        }
    
    def create_session(self, user_id: int) -> str:
        """Crear nueva sesión de chatbot"""
        session_id = f"chatbot_session_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Obtener preferencias del usuario
        user = User.query.get(user_id)
        user_preferences = {
            'language': 'es',
            'notification_preferences': {},
            'automation_enabled': True
        }
        
        if user:
            user_preferences.update({
                'name': user.name,
                'role': user.role,
                'email': user.email
            })
        
        context = ChatbotContext(
            user_id=user_id,
            session_id=session_id,
            current_mode=ChatbotMode.CONVERSATIONAL,
            conversation_history=[],
            user_preferences=user_preferences
        )
        
        self.active_sessions[session_id] = context
        
        # Guardar sesión en base de datos
        session_record = ChatbotSession(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            status='active'
        )
        db.session.add(session_record)
        db.session.commit()
        
        return session_id
    
    def process_message(self, session_id: str, message: str) -> Dict:
        """Procesar mensaje del usuario"""
        
        if session_id not in self.active_sessions:
            return {
                'error': 'Sesión no encontrada',
                'response': 'Por favor, inicia una nueva sesión.'
            }
        
        context = self.active_sessions[session_id]
        
        # Agregar mensaje al historial
        context.conversation_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Detectar intención
        intent = self._detect_intent(message)
        
        # Procesar según el modo actual
        if context.current_mode == ChatbotMode.EMERGENCY_RESPONSE:
            response = self._handle_emergency_mode(context, message, intent)
        elif context.current_mode == ChatbotMode.TASK_EXECUTION:
            response = self._handle_task_execution_mode(context, message, intent)
        else:
            response = self._handle_conversational_mode(context, message, intent)
        
        # Agregar respuesta al historial
        context.conversation_history.append({
            'role': 'assistant',
            'content': response['message'],
            'timestamp': datetime.now().isoformat(),
            'intent': intent.value if intent else None
        })
        
        # Actualizar sesión en base de datos
        self._update_session(context)
        
        return response
    
    def _detect_intent(self, message: str) -> Optional[IntentType]:
        """Detectar intención del mensaje"""
        message_lower = message.lower()
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent_type
        
        return IntentType.GENERAL_QUERY
    
    def _handle_conversational_mode(self, context: ChatbotContext, message: str, intent: IntentType) -> Dict:
        """Manejar modo conversacional"""
        
        if intent == IntentType.EMERGENCY:
            context.current_mode = ChatbotMode.EMERGENCY_RESPONSE
            return self._handle_emergency_mode(context, message, intent)
        
        elif intent == IntentType.MAINTENANCE_REQUEST:
            context.current_mode = ChatbotMode.TASK_EXECUTION
            context.current_task = {
                'type': 'maintenance_request',
                'step': 'collecting_details',
                'data': {}
            }
            return {
                'message': self._get_response_template(intent),
                'mode': 'task_execution',
                'next_step': 'Por favor, describe el problema de mantenimiento que necesitas reportar.'
            }
        
        elif intent == IntentType.VISIT_SCHEDULE:
            context.current_mode = ChatbotMode.TASK_EXECUTION
            context.current_task = {
                'type': 'visit_schedule',
                'step': 'collecting_visitor_info',
                'data': {}
            }
            return {
                'message': self._get_response_template(intent),
                'mode': 'task_execution',
                'next_step': '¿Cuál es el nombre del visitante y cuándo planeas recibirlo?'
            }
        
        elif intent == IntentType.RESERVATION_BOOK:
            context.current_mode = ChatbotMode.TASK_EXECUTION
            context.current_task = {
                'type': 'reservation_book',
                'step': 'collecting_reservation_details',
                'data': {}
            }
            return {
                'message': self._get_response_template(intent),
                'mode': 'task_execution',
                'next_step': '¿Qué espacio necesitas reservar y para qué fecha?'
            }
        
        elif intent == IntentType.AUTOMATION_REQUEST:
            return self._handle_automation_request(context, message)
        
        else:
            # Respuesta conversacional normal
            response_message = self._get_response_template(intent)
            
            # Si no hay plantilla específica, usar IA para generar respuesta
            if not response_message:
                response_message = self._generate_ai_response(context, message, intent)
            
            return {
                'message': response_message,
                'mode': 'conversational'
            }
    
    def _handle_task_execution_mode(self, context: ChatbotContext, message: str, intent: IntentType) -> Dict:
        """Manejar modo de ejecución de tareas"""
        
        if not context.current_task:
            context.current_mode = ChatbotMode.CONVERSATIONAL
            return {
                'message': 'Volviendo al modo conversacional. ¿En qué puedo ayudarte?',
                'mode': 'conversational'
            }
        
        task_type = context.current_task['type']
        current_step = context.current_task['step']
        
        if task_type == 'maintenance_request':
            return self._handle_maintenance_task(context, message, current_step)
        elif task_type == 'visit_schedule':
            return self._handle_visit_task(context, message, current_step)
        elif task_type == 'reservation_book':
            return self._handle_reservation_task(context, message, current_step)
        else:
            context.current_mode = ChatbotMode.CONVERSATIONAL
            return {
                'message': 'Tarea completada. ¿En qué más puedo ayudarte?',
                'mode': 'conversational'
            }
    
    def _handle_maintenance_task(self, context: ChatbotContext, message: str, step: str) -> Dict:
        """Manejar tarea de mantenimiento"""
        
        if step == 'collecting_details':
            # Extraer información del problema
            context.current_task['data']['description'] = message
            context.current_task['step'] = 'collecting_location'
            
            return {
                'message': 'Entiendo el problema. ¿En qué área o ubicación específica se encuentra?',
                'mode': 'task_execution',
                'next_step': 'Especifica la ubicación del problema.'
            }
        
        elif step == 'collecting_location':
            context.current_task['data']['location'] = message
            context.current_task['step'] = 'collecting_priority'
            
            return {
                'message': 'Gracias. ¿Qué tan urgente es este problema?\n1. Baja prioridad\n2. Media prioridad\n3. Alta prioridad\n4. Emergencia',
                'mode': 'task_execution',
                'next_step': 'Selecciona la prioridad del problema.'
            }
        
        elif step == 'collecting_priority':
            priority_map = {
                '1': 'low',
                '2': 'medium', 
                '3': 'high',
                '4': 'emergency'
            }
            
            priority = priority_map.get(message.strip(), 'medium')
            context.current_task['data']['priority'] = priority
            
            # Crear solicitud de mantenimiento
            maintenance = Maintenance(
                title=f"Solicitud de Mantenimiento - {context.user_preferences.get('name', 'Usuario')}",
                description=context.current_task['data']['description'],
                location=context.current_task['data']['location'],
                priority=priority,
                status='pending',
                reported_by=context.user_id,
                reported_at=datetime.now()
            )
            
            db.session.add(maintenance)
            db.session.commit()
            
            # Ejecutar automatización si está habilitada
            if context.user_preferences.get('automation_enabled', True):
                automation_manager.execute_automation(
                    AutomationType.MAINTENANCE_SCHEDULING,
                    {
                        'maintenance_id': maintenance.id,
                        'equipment': context.current_task['data']['location'],
                        'priority': priority
                    }
                )
            
            context.current_mode = ChatbotMode.CONVERSATIONAL
            context.current_task = None
            
            return {
                'message': f'✅ Solicitud de mantenimiento creada exitosamente.\n\n**Detalles:**\n• Problema: {maintenance.description}\n• Ubicación: {maintenance.location}\n• Prioridad: {priority.title()}\n• ID: #{maintenance.id}\n\nEl equipo de mantenimiento será notificado automáticamente.',
                'mode': 'conversational',
                'task_completed': True,
                'maintenance_id': maintenance.id
            }
    
    def _handle_visit_task(self, context: ChatbotContext, message: str, step: str) -> Dict:
        """Manejar tarea de programación de visitas"""
        
        if step == 'collecting_visitor_info':
            # Extraer información básica del visitante
            context.current_task['data']['visitor_info'] = message
            context.current_task['step'] = 'collecting_visit_date'
            
            return {
                'message': 'Gracias. ¿Para qué fecha y hora planeas recibir al visitante? (formato: DD/MM/YYYY HH:MM)',
                'mode': 'task_execution',
                'next_step': 'Especifica la fecha y hora de la visita.'
            }
        
        elif step == 'collecting_visit_date':
            try:
                # Parsear fecha (simplificado)
                visit_date = datetime.now() + timedelta(days=1)  # Por defecto mañana
                context.current_task['data']['visit_date'] = visit_date
                context.current_task['step'] = 'confirming_visit'
                
                return {
                    'message': f'Perfecto. Voy a crear la solicitud de visita para el {visit_date.strftime("%d/%m/%Y a las %H:%M")}.\n\n¿Confirmas los datos?\n• Visitante: {context.current_task["data"]["visitor_info"]}\n• Fecha: {visit_date.strftime("%d/%m/%Y %H:%M")}',
                    'mode': 'task_execution',
                    'next_step': 'Confirma si los datos son correctos (sí/no).'
                }
            
            except Exception as e:
                return {
                    'message': 'No pude entender la fecha. Por favor, usa el formato DD/MM/YYYY HH:MM',
                    'mode': 'task_execution'
                }
        
        elif step == 'confirming_visit':
            if message.lower() in ['sí', 'si', 'yes', 'confirmo', 'correcto']:
                # Crear solicitud de visita
                visit = Visit(
                    visitor_name=context.current_task['data']['visitor_info'],
                    visit_date=context.current_task['data']['visit_date'],
                    status='pending',
                    requested_by=context.user_id,
                    requested_at=datetime.now()
                )
                
                db.session.add(visit)
                db.session.commit()
                
                context.current_mode = ChatbotMode.CONVERSATIONAL
                context.current_task = None
                
                return {
                    'message': f'✅ Solicitud de visita creada exitosamente.\n\n**Detalles:**\n• Visitante: {visit.visitor_name}\n• Fecha: {visit.visit_date.strftime("%d/%m/%Y %H:%M")}\n• ID: #{visit.id}\n\nLa solicitud será revisada por administración.',
                    'mode': 'conversational',
                    'task_completed': True,
                    'visit_id': visit.id
                }
            else:
                context.current_task['step'] = 'collecting_visitor_info'
                return {
                    'message': 'Entendido. Vamos a empezar de nuevo. ¿Cuál es el nombre del visitante?',
                    'mode': 'task_execution'
                }
    
    def _handle_reservation_task(self, context: ChatbotContext, message: str, step: str) -> Dict:
        """Manejar tarea de reserva de espacios"""
        
        if step == 'collecting_reservation_details':
            context.current_task['data']['reservation_details'] = message
            context.current_task['step'] = 'collecting_reservation_date'
            
            return {
                'message': 'Gracias. ¿Para qué fecha y hora necesitas la reserva? (formato: DD/MM/YYYY HH:MM)',
                'mode': 'task_execution',
                'next_step': 'Especifica la fecha y hora de la reserva.'
            }
        
        elif step == 'collecting_reservation_date':
            try:
                # Parsear fecha (simplificado)
                reservation_date = datetime.now() + timedelta(days=1)  # Por defecto mañana
                context.current_task['data']['reservation_date'] = reservation_date
                
                # Crear reserva
                reservation = Reservation(
                    space_name=context.current_task['data']['reservation_details'],
                    reservation_date=reservation_date,
                    status='pending',
                    requested_by=context.user_id,
                    requested_at=datetime.now()
                )
                
                db.session.add(reservation)
                db.session.commit()
                
                context.current_mode = ChatbotMode.CONVERSATIONAL
                context.current_task = None
                
                return {
                    'message': f'✅ Reserva creada exitosamente.\n\n**Detalles:**\n• Espacio: {reservation.space_name}\n• Fecha: {reservation.reservation_date.strftime("%d/%m/%Y %H:%M")}\n• ID: #{reservation.id}\n\nLa reserva será confirmada por administración.',
                    'mode': 'conversational',
                    'task_completed': True,
                    'reservation_id': reservation.id
                }
            
            except Exception as e:
                return {
                    'message': 'No pude entender la fecha. Por favor, usa el formato DD/MM/YYYY HH:MM',
                    'mode': 'task_execution'
                }
    
    def _handle_emergency_mode(self, context: ChatbotContext, message: str, intent: IntentType) -> Dict:
        """Manejar modo de emergencia"""
        
        # Ejecutar automatización de emergencia
        automation_manager.execute_automation(
            AutomationType.SECURITY_MONITORING,
            {
                'description': f"Emergencia reportada por {context.user_preferences.get('name', 'Usuario')}: {message}",
                'priority': 'emergency',
                'user_id': context.user_id
            }
        )
        
        # Notificar a seguridad
        notification = Notification(
            title="🚨 ALERTA DE EMERGENCIA 🚨",
            message=f"Emergencia reportada por {context.user_preferences.get('name', 'Usuario')}: {message}",
            notification_type='emergency',
            priority='high',
            created_at=datetime.now()
        )
        
        db.session.add(notification)
        db.session.commit()
        
        context.current_mode = ChatbotMode.CONVERSATIONAL
        
        return {
            'message': '🚨 **ALERTA DE EMERGENCIA ACTIVADA** 🚨\n\nHe notificado inmediatamente al equipo de seguridad y administración.\n\n**Mantén la calma y sigue estas instrucciones:**\n1. Si estás en peligro, llama al 911\n2. Aléjate del área si es necesario\n3. El equipo de seguridad llegará pronto\n4. Mantente disponible para más información\n\n¿Necesitas ayuda adicional?',
            'mode': 'conversational',
            'emergency_activated': True
        }
    
    def _handle_automation_request(self, context: ChatbotContext, message: str) -> Dict:
        """Manejar solicitud de automatización"""
        
        # Detectar tipo de automatización solicitada
        if any(word in message.lower() for word in ['recordatorio', 'reminder', 'notificar', 'notify']):
            return {
                'message': 'Te ayudo a configurar recordatorios automáticos.\n\n**Opciones disponibles:**\n• Recordatorio de pagos\n• Notificación de mantenimiento\n• Alertas de seguridad\n• Recordatorios de visitas\n\n¿Qué tipo de recordatorio necesitas?',
                'mode': 'conversational',
                'automation_options': True
            }
        
        elif any(word in message.lower() for word in ['programar', 'schedule', 'automático', 'automatic']):
            return {
                'message': 'Te ayudo a configurar automatizaciones.\n\n**Opciones disponibles:**\n• Mantenimiento preventivo automático\n• Aprobación automática de visitas frecuentes\n• Alertas automáticas de gastos\n• Notificaciones automáticas de eventos\n\n¿Qué proceso quieres automatizar?',
                'mode': 'conversational',
                'automation_options': True
            }
        
        else:
            return {
                'message': 'Entiendo que quieres configurar automatizaciones. ¿Puedes ser más específico sobre qué proceso quieres automatizar?',
                'mode': 'conversational'
            }
    
    def _get_response_template(self, intent: IntentType) -> str:
        """Obtener plantilla de respuesta para una intención"""
        templates = self.response_templates.get(intent, [])
        if templates:
            import random
            return random.choice(templates)
        return None
    
    def _generate_ai_response(self, context: ChatbotContext, message: str, intent: IntentType) -> str:
        """Generar respuesta usando IA"""
        
        # Usar el conocimiento base del barrio
        knowledge = self.knowledge_base.get_relevant_knowledge(message)
        
        if knowledge:
            return f"Basándome en la información del barrio: {knowledge}"
        
        # Respuesta genérica
        return "Entiendo tu consulta. ¿Puedes ser más específico sobre qué necesitas ayuda?"
    
    def _update_session(self, context: ChatbotContext):
        """Actualizar sesión en base de datos"""
        try:
            session_record = ChatbotSession.query.filter_by(session_id=context.session_id).first()
            if session_record:
                session_record.last_activity = datetime.now()
                session_record.conversation_history = json.dumps(context.conversation_history)
                db.session.commit()
        except Exception as e:
            self.logger.error(f"Error actualizando sesión: {e}")
    
    def end_session(self, session_id: str):
        """Finalizar sesión de chatbot"""
        if session_id in self.active_sessions:
            context = self.active_sessions[session_id]
            
            # Actualizar sesión en base de datos
            session_record = ChatbotSession.query.filter_by(session_id=session_id).first()
            if session_record:
                session_record.status = 'completed'
                session_record.ended_at = datetime.now()
                db.session.commit()
            
            del self.active_sessions[session_id]
            
            return True
        return False


# Instancia global del chatbot
advanced_chatbot = AdvancedChatbotEngine()


def init_advanced_chatbot(app):
    """Inicializar chatbot avanzado"""
    
    try:
        # Registrar rutas de API para el chatbot
        @app.route('/api/v1/chatbot/session', methods=['POST'])
        def create_chatbot_session():
            """Crear nueva sesión de chatbot"""
            try:
                data = request.get_json()
                user_id = data.get('user_id')
                
                if not user_id:
                    return {'error': 'user_id requerido'}, 400
                
                session_id = advanced_chatbot.create_session(user_id)
                
                return {
                    'status': 'success',
                    'session_id': session_id,
                    'message': 'Sesión de chatbot creada exitosamente'
                }
                
            except Exception as e:
                return {'error': str(e)}, 500
        
        @app.route('/api/v1/chatbot/message', methods=['POST'])
        def send_chatbot_message():
            """Enviar mensaje al chatbot"""
            try:
                data = request.get_json()
                session_id = data.get('session_id')
                message = data.get('message')
                
                if not session_id or not message:
                    return {'error': 'session_id y message requeridos'}, 400
                
                response = advanced_chatbot.process_message(session_id, message)
                
                return {
                    'status': 'success',
                    'response': response
                }
                
            except Exception as e:
                return {'error': str(e)}, 500
        
        @app.route('/api/v1/chatbot/session/<session_id>', methods=['DELETE'])
        def end_chatbot_session(session_id):
            """Finalizar sesión de chatbot"""
            try:
                success = advanced_chatbot.end_session(session_id)
                
                if success:
                    return {
                        'status': 'success',
                        'message': 'Sesión finalizada exitosamente'
                    }
                else:
                    return {'error': 'Sesión no encontrada'}, 404
                
            except Exception as e:
                return {'error': str(e)}, 500
        
        @app.route('/api/v1/chatbot/session/<session_id>/history', methods=['GET'])
        def get_chatbot_history(session_id):
            """Obtener historial de conversación"""
            try:
                if session_id not in advanced_chatbot.active_sessions:
                    return {'error': 'Sesión no encontrada'}, 404
                
                context = advanced_chatbot.active_sessions[session_id]
                
                return {
                    'status': 'success',
                    'history': context.conversation_history
                }
                
            except Exception as e:
                return {'error': str(e)}, 500
        
        print("✅ Chatbot inteligente avanzado inicializado")
        
    except Exception as e:
        print(f"⚠️ Error inicializando chatbot avanzado: {e}")


# Decoradores para facilitar el uso
def chatbot_assisted(func):
    """Decorador para funciones asistidas por chatbot"""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # Si hay un usuario en el contexto, crear sesión de chatbot
        if 'user_id' in kwargs:
            session_id = advanced_chatbot.create_session(kwargs['user_id'])
            
            # Enviar mensaje de confirmación
            advanced_chatbot.process_message(session_id, f"Tarea completada: {func.__name__}")
        
        return result
    return wrapper
