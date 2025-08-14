from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, ChatbotSession, User, Visit, Reservation, News, Maintenance, Expense
from openai import OpenAI
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
        
        # Extraer el texto del mensaje para el historial
        bot_response_text = response['message'] if isinstance(response, dict) else response
        
        context['conversation_history'].append({
            'user': message,
            'bot': bot_response_text,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Mantener solo los últimos 10 intercambios
        if len(context['conversation_history']) > 10:
            context['conversation_history'] = context['conversation_history'][-10:]
        
        session.set_context(context)
        session.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Estructurar respuesta
        if isinstance(response, dict):
            return jsonify({
                'response': response['message'],
                'redirect': {
                    'url': response['redirect_url'],
                    'title': response['redirect_title'],
                    'auto_redirect': response['auto_redirect'],
                    'delay': response['delay']
                },
                'session_id': session.session_id
            })
        else:
            return jsonify({
                'response': response,
                'session_id': session.session_id
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_message(message, session):
    """Procesar mensaje y generar respuesta"""
    message_lower = message.lower()
    
    # Detectar intención de redirección automática
    redirect_intent = detect_redirect_intent(message_lower)
    
    # Respuestas basadas en palabras clave
    if any(word in message_lower for word in ['hola', 'hello', 'hi', 'buenas']):
        return f"¡Hola {current_user.name}! Soy el asistente virtual del barrio. ¿En qué puedo ayudarte hoy? Puedo ayudarte con visitas, reservas, expensas, noticias y más."
    
    elif any(word in message_lower for word in ['visita', 'visitor', 'invitado']):
        return handle_visits_query(message_lower, redirect_intent)
    
    elif any(word in message_lower for word in ['reserva', 'quincho', 'sum', 'cancha', 'espacio']):
        return handle_reservations_query(message_lower, redirect_intent)
    
    elif any(word in message_lower for word in ['expensa', 'pago', 'deuda', 'factura']):
        return handle_expenses_query(message_lower, redirect_intent)
    
    elif any(word in message_lower for word in ['noticia', 'comunicado', 'aviso', 'información']):
        return handle_news_query(message_lower, redirect_intent)
    
    elif any(word in message_lower for word in ['mantenimiento', 'reclamo', 'problema', 'arreglo']):
        return handle_maintenance_query(message_lower, redirect_intent)
    
    elif any(word in message_lower for word in ['mapa', 'ubicación', 'donde', 'localización']):
        return handle_map_query(message_lower, redirect_intent)
    
    elif any(word in message_lower for word in ['perfil', 'mi cuenta', 'datos', 'información personal']):
        return handle_profile_query(message_lower, redirect_intent)
    
    elif any(word in message_lower for word in ['admin', 'administración', 'panel', 'gestión']):
        return handle_admin_query(message_lower, redirect_intent)
    
    elif any(word in message_lower for word in ['ayuda', 'help', 'funciones', 'que puedes hacer']):
        return get_help_message()
    
    else:
        # Respuesta genérica o usar OpenAI si está configurado
        return handle_general_query(message, session)

def detect_redirect_intent(message):
    """Detectar si el usuario quiere ser redirigido automáticamente"""
    redirect_keywords = [
        'ir a', 'llevar a', 'mostrar', 'ver', 'abrir', 'acceder', 'dirigir',
        'navegar', 'ir', 'entrar', 'quiero ir', 'necesito ir', 'me llevas',
        'redirect', 'go to', 'take me', 'show me', 'open'
    ]
    
    action_keywords = [
        'crear', 'registrar', 'nuevo', 'nueva', 'agregar', 'añadir',
        'hacer', 'programar', 'agendar', 'reservar', 'pagar',
        'create', 'new', 'add', 'make', 'register'
    ]
    
    # Detectar palabras que indican redirección o acción
    has_redirect_intent = any(keyword in message for keyword in redirect_keywords)
    has_action_intent = any(keyword in message for keyword in action_keywords)
    
    return has_redirect_intent or has_action_intent

def create_response_with_redirect(message, url, title):
    """Crear respuesta con redirección automática"""
    return {
        'type': 'redirect',
        'message': message,
        'redirect_url': url,
        'redirect_title': title,
        'auto_redirect': True,
        'delay': 2  # segundos antes de redireccionar
    }

def handle_visits_query(message, redirect_intent=False):
    """Manejar consultas sobre visitas"""
    pending_visits = Visit.query.filter_by(resident_id=current_user.id, status='pending').count()
    active_visits = Visit.query.filter_by(resident_id=current_user.id, status='active').count()
    
    # Detectar acciones específicas para redirección
    if 'nuevo' in message or 'crear' in message or 'registrar' in message:
        return create_response_with_redirect(
            "Te estoy llevando a registrar una nueva visita...",
            "/visits/new",
            "Registrar Nueva Visita"
        )
    
    if redirect_intent:
        return create_response_with_redirect(
            "Te estoy llevando a la sección de visitas...",
            "/visits",
            "Gestión de Visitas"
        )
    
    if 'pendiente' in message or 'pending' in message:
        if pending_visits > 0:
            response = f"Tienes {pending_visits} visita{'s' if pending_visits > 1 else ''} pendiente{'s' if pending_visits > 1 else ''}."
            if redirect_intent:
                return create_response_with_redirect(
                    response + " Te llevo allí...",
                    "/visits",
                    "Ver Visitas Pendientes"
                )
            return response + " Puedes verlas en la sección de Visitas."
        else:
            return "No tienes visitas pendientes en este momento."
    
    elif 'activa' in message or 'active' in message:
        if active_visits > 0:
            return f"Tienes {active_visits} visita{'s' if active_visits > 1 else ''} activa{'s' if active_visits > 1 else ''} en este momento."
        else:
            return "No tienes visitas activas en este momento."
    
    else:
        return f"Información sobre tus visitas:\n• Visitas pendientes: {pending_visits}\n• Visitas activas: {active_visits}\n\nPuedes registrar nuevas visitas en la sección correspondiente."

def handle_reservations_query(message, redirect_intent=False):
    """Manejar consultas sobre reservas"""
    pending_reservations = Reservation.query.filter_by(user_id=current_user.id, status='pending').count()
    approved_reservations = Reservation.query.filter_by(user_id=current_user.id, status='approved').count()
    
    # Detectar acciones específicas para redirección
    if 'nuevo' in message or 'crear' in message or 'reservar' in message or 'quincho' in message or 'cancha' in message:
        return create_response_with_redirect(
            "Te estoy llevando a hacer una nueva reserva...",
            "/reservations/new",
            "Nueva Reserva"
        )
    
    if 'calendario' in message or 'ver calendario' in message:
        return create_response_with_redirect(
            "Te muestro el calendario de reservas...",
            "/reservations/calendar",
            "Calendario de Reservas"
        )
    
    if redirect_intent:
        return create_response_with_redirect(
            "Te estoy llevando a la sección de reservas...",
            "/reservations",
            "Gestión de Reservas"
        )
    
    if 'pendiente' in message:
        return f"Tienes {pending_reservations} reserva{'s' if pending_reservations > 1 else ''} pendiente{'s' if pending_reservations > 1 else ''} de aprobación."
    
    elif 'aprobada' in message or 'confirmada' in message:
        return f"Tienes {approved_reservations} reserva{'s' if approved_reservations > 1 else ''} aprobada{'s' if approved_reservations > 1 else ''}."
    
    else:
        return f"Estado de tus reservas:\n• Pendientes: {pending_reservations}\n• Aprobadas: {approved_reservations}\n\nPuedes hacer nuevas reservas en la sección de Espacios Comunes."

def handle_expenses_query(message, redirect_intent=False):
    """Manejar consultas sobre expensas"""
    pending_expenses = Expense.query.filter_by(user_id=current_user.id, status='pending').count()
    overdue_expenses = Expense.query.filter_by(user_id=current_user.id, status='overdue').count()
    
    # Detectar acciones específicas para redirección
    if 'pagar' in message or 'pago' in message:
        return create_response_with_redirect(
            "Te estoy llevando a pagar tus expensas...",
            "/expenses",
            "Pagar Expensas"
        )
    
    if redirect_intent:
        return create_response_with_redirect(
            "Te estoy llevando a la sección de expensas...",
            "/expenses",
            "Estado de Expensas"
        )
    
    if 'pendiente' in message or 'debo' in message:
        if pending_expenses > 0:
            response = f"Tienes {pending_expenses} expensa{'s' if pending_expenses > 1 else ''} pendiente{'s' if pending_expenses > 1 else ''} de pago."
            if redirect_intent:
                return create_response_with_redirect(
                    response + " Te llevo a pagarlas...",
                    "/expenses",
                    "Pagar Expensas Pendientes"
                )
            return response
        else:
            return "¡Excelente! No tienes expensas pendientes de pago."
    
    elif 'vencida' in message or 'atrasada' in message:
        if overdue_expenses > 0:
            return f"Tienes {overdue_expenses} expensa{'s' if overdue_expenses > 1 else ''} vencida{'s' if overdue_expenses > 1 else ''}. Te recomiendo pagarlas cuanto antes."
        else:
            return "No tienes expensas vencidas."
    
    else:
        return f"Estado de tus expensas:\n• Pendientes: {pending_expenses}\n• Vencidas: {overdue_expenses}\n\nPuedes pagar tus expensas en la sección correspondiente."

def handle_news_query(message, redirect_intent=False):
    """Manejar consultas sobre noticias"""
    recent_news = News.query.filter_by(is_published=True).order_by(News.created_at.desc()).limit(3).all()
    important_news = News.query.filter_by(is_published=True, is_important=True).count()
    
    # Detectar acciones específicas para redirección
    if current_user.can_access_admin() and ('crear' in message or 'nueva' in message or 'publicar' in message):
        return create_response_with_redirect(
            "Te estoy llevando a crear una nueva noticia...",
            "/news/new",
            "Crear Nueva Noticia"
        )
    
    if redirect_intent:
        return create_response_with_redirect(
            "Te estoy llevando a la sección de noticias...",
            "/news",
            "Noticias del Barrio"
        )
    
    if 'importante' in message or 'urgent' in message:
        response = f"Hay {important_news} noticia{'s' if important_news > 1 else ''} importante{'s' if important_news > 1 else ''} publicada{'s' if important_news > 1 else ''}."
        if redirect_intent:
            return create_response_with_redirect(
                response + " Te muestro las noticias...",
                "/news",
                "Ver Noticias Importantes"
            )
        return response + " Puedes verlas en la sección de Noticias."
    
    elif 'reciente' in message or 'nueva' in message:
        if recent_news:
            news_titles = '\n• '.join([news.title for news in recent_news])
            return f"Las noticias más recientes son:\n• {news_titles}"
        else:
            return "No hay noticias recientes en este momento."
    
    else:
        return f"Hay {len(recent_news)} noticias recientes y {important_news} importante{'s' if important_news > 1 else ''}. Puedes verlas todas en la sección de Noticias."

def handle_maintenance_query(message, redirect_intent=False):
    """Manejar consultas sobre mantenimiento"""
    pending_maintenance = Maintenance.query.filter_by(user_id=current_user.id, status='pending').count()
    in_progress_maintenance = Maintenance.query.filter_by(user_id=current_user.id, status='in_progress').count()
    
    # Detectar acciones específicas para redirección
    if 'nuevo' in message or 'crear' in message or 'reclamo' in message or 'problema' in message:
        return create_response_with_redirect(
            "Te estoy llevando a crear un nuevo reclamo...",
            "/maintenance/new",
            "Nuevo Reclamo de Mantenimiento"
        )
    
    if redirect_intent:
        return create_response_with_redirect(
            "Te estoy llevando a la sección de mantenimiento...",
            "/maintenance",
            "Gestión de Mantenimiento"
        )
    
    if 'pendiente' in message:
        return f"Tienes {pending_maintenance} reclamo{'s' if pending_maintenance > 1 else ''} de mantenimiento pendiente{'s' if pending_maintenance > 1 else ''}."
    
    elif 'progreso' in message or 'proceso' in message:
        return f"Tienes {in_progress_maintenance} reclamo{'s' if in_progress_maintenance > 1 else ''} en progreso."
    
    else:
        return f"Estado de tus reclamos:\n• Pendientes: {pending_maintenance}\n• En progreso: {in_progress_maintenance}\n\nPuedes crear nuevos reclamos en la sección de Mantenimiento."

def handle_map_query(message, redirect_intent=False):
    """Manejar consultas sobre el mapa"""
    if redirect_intent or any(word in message for word in ['ir', 'ver', 'mostrar', 'ubicación']):
        return create_response_with_redirect(
            "Te estoy llevando al mapa interactivo del barrio...",
            "/map",
            "Mapa del Barrio"
        )
    
    return "El mapa interactivo te muestra la ubicación de las manzanas, casas y espacios comunes del barrio."

def handle_profile_query(message, redirect_intent=False):
    """Manejar consultas sobre el perfil"""
    if redirect_intent or any(word in message for word in ['ir', 'ver', 'mostrar', 'editar']):
        return create_response_with_redirect(
            "Te estoy llevando a tu perfil...",
            "/profile",
            "Mi Perfil"
        )
    
    return f"Hola {current_user.name}, puedes ver y editar tu información personal en tu perfil."

def handle_admin_query(message, redirect_intent=False):
    """Manejar consultas sobre administración"""
    if not current_user.can_access_admin():
        return "No tienes permisos para acceder a las funciones de administración."
    
    if redirect_intent or any(word in message for word in ['ir', 'ver', 'mostrar', 'panel']):
        return create_response_with_redirect(
            "Te estoy llevando al panel de administración...",
            "/admin/dashboard",
            "Panel de Administración"
        )
    
    return "Como administrador, puedes gestionar usuarios, contenido y configuraciones desde el panel de administración."

def get_help_message():
    """Mensaje de ayuda con funciones disponibles"""
    return """¡Hola! Soy tu asistente virtual con **redirección automática inteligente**. Puedo ayudarte con:

🏠 **Visitas**: Consultar estado y crear nuevas visitas
📅 **Reservas**: Ver estado y hacer nuevas reservas de espacios comunes  
💳 **Expensas**: Consultar expensas pendientes y realizar pagos
📢 **Noticias**: Ver las últimas noticias del barrio
🔧 **Mantenimiento**: Ver estado y crear nuevos reclamos
🗺️ **Mapa**: Navegar por el mapa interactivo del barrio
👤 **Perfil**: Gestionar tu información personal
⚙️ **Admin**: Panel de administración (solo administradores)

**🚀 REDIRECCIÓN AUTOMÁTICA:**
Uso palabras clave para llevarte directamente a donde necesitas:

**Ejemplos de comandos que me redirigen automáticamente:**
• "Quiero hacer una reserva" → Te llevo a Reservas
• "Ver mis expensas" → Te llevo a Expensas  
• "Registrar una nueva visita" → Te llevo a Nueva Visita
• "Mostrar el mapa" → Te llevo al Mapa
• "Ir a noticias" → Te llevo a Noticias
• "Crear reclamo" → Te llevo a Nuevo Reclamo
• "Ver mi perfil" → Te llevo a Perfil

**Palabras mágicas:** usa "ir a", "mostrar", "ver", "crear", "nuevo", "hacer" para activar la redirección automática.

¡Solo dime qué necesitas y te dirijo automáticamente! 🤖✨"""

def handle_general_query(message, session):
    """Manejar consultas generales usando OpenAI si está disponible"""
    try:
        # Si OpenAI está configurado, usar GPT
        from flask import current_app
        api_key = current_app.config.get('OPENAI_API_KEY')
        if api_key:
            client = OpenAI(api_key=api_key)
            context = session.get_context_dict()
            
            system_prompt = f"""Eres un asistente virtual para un barrio cerrado. 
            El usuario es {context.get('user_name')} con rol {context.get('user_role')}.
            Ayuda con consultas sobre: visitas, reservas, expensas, noticias, mantenimiento, seguridad.
            Responde de manera amigable y concisa en español."""
            
            response = client.chat.completions.create(
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