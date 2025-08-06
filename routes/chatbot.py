from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, ChatbotSession, User, Visit, Reservation, News, Maintenance, Expense
import openai
import uuid
from datetime import datetime
import json

bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

@bp.route('/')
@login_required
def index():
    """Página principal del chatbot"""
    return render_template('chatbot/index.html')

@bp.route('/chat', methods=['POST'])
@login_required
def chat():
    """Procesar mensaje del chatbot"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        # Obtener o crear sesión
        if session_id:
            session = ChatbotSession.query.filter_by(session_id=session_id).first()
        else:
            session = None
        
        if not session:
            session = ChatbotSession(
                session_id=str(uuid.uuid4()),
                user_id=current_user.id,
                context=json.dumps({
                    'user_name': current_user.name,
                    'user_role': current_user.role,
                    'conversation_history': []
                })
            )
            db.session.add(session)
            db.session.commit()
        
        # Procesar mensaje
        response = process_message(message, session)
        
        # Actualizar historial de conversación
        context = session.get_context_dict()
        context['conversation_history'].append({
            'user': message,
            'bot': response,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Mantener solo los últimos 10 intercambios
        if len(context['conversation_history']) > 10:
            context['conversation_history'] = context['conversation_history'][-10:]
        
        session.set_context(context)
        session.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'response': response,
            'session_id': session.session_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_message(message, session):
    """Procesar mensaje y generar respuesta"""
    message_lower = message.lower()
    
    # Respuestas basadas en palabras clave
    if any(word in message_lower for word in ['hola', 'hello', 'hi', 'buenas']):
        return f"¡Hola {current_user.name}! Soy el asistente virtual del barrio. ¿En qué puedo ayudarte hoy? Puedo ayudarte con visitas, reservas, expensas, noticias y más."
    
    elif any(word in message_lower for word in ['visita', 'visitor', 'invitado']):
        return handle_visits_query(message_lower)
    
    elif any(word in message_lower for word in ['reserva', 'quincho', 'sum', 'cancha', 'espacio']):
        return handle_reservations_query(message_lower)
    
    elif any(word in message_lower for word in ['expensa', 'pago', 'deuda', 'factura']):
        return handle_expenses_query(message_lower)
    
    elif any(word in message_lower for word in ['noticia', 'comunicado', 'aviso', 'información']):
        return handle_news_query(message_lower)
    
    elif any(word in message_lower for word in ['mantenimiento', 'reclamo', 'problema', 'arreglo']):
        return handle_maintenance_query(message_lower)
    
    elif any(word in message_lower for word in ['ayuda', 'help', 'funciones', 'que puedes hacer']):
        return get_help_message()
    
    else:
        # Respuesta genérica o usar OpenAI si está configurado
        return handle_general_query(message, session)

def handle_visits_query(message):
    """Manejar consultas sobre visitas"""
    pending_visits = Visit.query.filter_by(resident_id=current_user.id, status='pending').count()
    active_visits = Visit.query.filter_by(resident_id=current_user.id, status='active').count()
    
    if 'pendiente' in message or 'pending' in message:
        if pending_visits > 0:
            return f"Tienes {pending_visits} visita{'s' if pending_visits > 1 else ''} pendiente{'s' if pending_visits > 1 else ''}. Puedes verlas en la sección de Visitas."
        else:
            return "No tienes visitas pendientes en este momento."
    
    elif 'activa' in message or 'active' in message:
        if active_visits > 0:
            return f"Tienes {active_visits} visita{'s' if active_visits > 1 else ''} activa{'s' if active_visits > 1 else ''} en este momento."
        else:
            return "No tienes visitas activas en este momento."
    
    else:
        return f"Información sobre tus visitas:\n• Visitas pendientes: {pending_visits}\n• Visitas activas: {active_visits}\n\nPuedes registrar nuevas visitas en la sección correspondiente."

def handle_reservations_query(message):
    """Manejar consultas sobre reservas"""
    pending_reservations = Reservation.query.filter_by(user_id=current_user.id, status='pending').count()
    approved_reservations = Reservation.query.filter_by(user_id=current_user.id, status='approved').count()
    
    if 'pendiente' in message:
        return f"Tienes {pending_reservations} reserva{'s' if pending_reservations > 1 else ''} pendiente{'s' if pending_reservations > 1 else ''} de aprobación."
    
    elif 'aprobada' in message or 'confirmada' in message:
        return f"Tienes {approved_reservations} reserva{'s' if approved_reservations > 1 else ''} aprobada{'s' if approved_reservations > 1 else ''}."
    
    else:
        return f"Estado de tus reservas:\n• Pendientes: {pending_reservations}\n• Aprobadas: {approved_reservations}\n\nPuedes hacer nuevas reservas en la sección de Espacios Comunes."

def handle_expenses_query(message):
    """Manejar consultas sobre expensas"""
    pending_expenses = Expense.query.filter_by(user_id=current_user.id, status='pending').count()
    overdue_expenses = Expense.query.filter_by(user_id=current_user.id, status='overdue').count()
    
    if 'pendiente' in message or 'debo' in message:
        if pending_expenses > 0:
            return f"Tienes {pending_expenses} expensa{'s' if pending_expenses > 1 else ''} pendiente{'s' if pending_expenses > 1 else ''} de pago."
        else:
            return "¡Excelente! No tienes expensas pendientes de pago."
    
    elif 'vencida' in message or 'atrasada' in message:
        if overdue_expenses > 0:
            return f"Tienes {overdue_expenses} expensa{'s' if overdue_expenses > 1 else ''} vencida{'s' if overdue_expenses > 1 else ''}. Te recomiendo pagarlas cuanto antes."
        else:
            return "No tienes expensas vencidas."
    
    else:
        return f"Estado de tus expensas:\n• Pendientes: {pending_expenses}\n• Vencidas: {overdue_expenses}\n\nPuedes pagar tus expensas en la sección correspondiente."

def handle_news_query(message):
    """Manejar consultas sobre noticias"""
    recent_news = News.query.filter_by(is_published=True).order_by(News.created_at.desc()).limit(3).all()
    important_news = News.query.filter_by(is_published=True, is_important=True).count()
    
    if 'importante' in message or 'urgent' in message:
        return f"Hay {important_news} noticia{'s' if important_news > 1 else ''} importante{'s' if important_news > 1 else ''} publicada{'s' if important_news > 1 else ''}. Puedes verlas en la sección de Noticias."
    
    elif 'reciente' in message or 'nueva' in message:
        if recent_news:
            news_titles = '\n• '.join([news.title for news in recent_news])
            return f"Las noticias más recientes son:\n• {news_titles}"
        else:
            return "No hay noticias recientes en este momento."
    
    else:
        return f"Hay {len(recent_news)} noticias recientes y {important_news} importante{'s' if important_news > 1 else ''}. Puedes verlas todas en la sección de Noticias."

def handle_maintenance_query(message):
    """Manejar consultas sobre mantenimiento"""
    pending_maintenance = Maintenance.query.filter_by(user_id=current_user.id, status='pending').count()
    in_progress_maintenance = Maintenance.query.filter_by(user_id=current_user.id, status='in_progress').count()
    
    if 'pendiente' in message:
        return f"Tienes {pending_maintenance} reclamo{'s' if pending_maintenance > 1 else ''} de mantenimiento pendiente{'s' if pending_maintenance > 1 else ''}."
    
    elif 'progreso' in message or 'proceso' in message:
        return f"Tienes {in_progress_maintenance} reclamo{'s' if in_progress_maintenance > 1 else ''} en progreso."
    
    else:
        return f"Estado de tus reclamos:\n• Pendientes: {pending_maintenance}\n• En progreso: {in_progress_maintenance}\n\nPuedes crear nuevos reclamos en la sección de Mantenimiento."

def get_help_message():
    """Mensaje de ayuda con funciones disponibles"""
    return """¡Hola! Soy tu asistente virtual. Puedo ayudarte con:

🏠 **Visitas**: Consultar estado de tus visitas pendientes y activas
📅 **Reservas**: Ver el estado de tus reservas de espacios comunes
💳 **Expensas**: Consultar expensas pendientes y vencidas
📢 **Noticias**: Informarte sobre las últimas noticias del barrio
🔧 **Mantenimiento**: Ver el estado de tus reclamos

Simplemente escribe lo que necesitas, por ejemplo:
• "¿Tengo visitas pendientes?"
• "¿Cuándo vence mi expensa?"
• "¿Hay noticias importantes?"
• "Estado de mis reclamos"

¡Pregúntame lo que necesites!"""

def handle_general_query(message, session):
    """Manejar consultas generales usando OpenAI si está disponible"""
    try:
        # Si OpenAI está configurado, usar GPT
        if hasattr(openai, 'api_key') and openai.api_key:
            context = session.get_context_dict()
            
            system_prompt = f"""Eres un asistente virtual para un barrio cerrado. 
            El usuario es {context.get('user_name')} con rol {context.get('user_role')}.
            Ayuda con consultas sobre: visitas, reservas, expensas, noticias, mantenimiento, seguridad.
            Responde de manera amigable y concisa en español."""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
    except Exception as e:
        pass
    
    # Respuesta por defecto
    return "Disculpa, no entendí tu consulta. ¿Podrías ser más específico? Puedo ayudarte con visitas, reservas, expensas, noticias y mantenimiento. Escribe 'ayuda' para ver todas mis funciones."

@bp.route('/clear_session', methods=['POST'])
@login_required
def clear_session():
    """Limpiar sesión del chatbot"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id:
            session = ChatbotSession.query.filter_by(session_id=session_id).first()
            if session and session.user_id == current_user.id:
                session.is_active = False
                db.session.commit()
        
        return jsonify({'success': True, 'message': 'Sesión limpiada'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500