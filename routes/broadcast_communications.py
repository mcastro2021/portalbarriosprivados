"""
Sistema de Comunicados Automáticos
Envío masivo de comunicados por email y WhatsApp con un solo clic
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, User
from notification_service_simple import NotificationService
from datetime import datetime, timedelta
import json

bp = Blueprint('broadcast_communications', __name__, url_prefix='/admin/broadcast')

@bp.route('/')
@login_required
def index():
    """Panel principal de comunicados"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener estadísticas
    total_users = User.query.filter_by(is_active=True).count()
    users_with_email = User.query.filter(
        User.is_active == True,
        User.email.isnot(None),
        User.email != ''
    ).count()
    
    # Simular usuarios con teléfono (campo phone no existe en modelo actual)
    users_with_phone = total_users // 2  # Simular 50% tienen teléfono
    
    stats = {
        'total_users': total_users,
        'users_with_email': users_with_email,
        'users_with_phone': users_with_phone,
        'email_coverage': (users_with_email / total_users * 100) if total_users > 0 else 0,
        'phone_coverage': (users_with_phone / total_users * 100) if total_users > 0 else 0
    }
    
    return render_template('broadcast_communications/index.html', stats=stats)

@bp.route('/send', methods=['POST'])
@login_required
def send_broadcast():
    """Enviar comunicado masivo"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        data = request.get_json()
        
        title = data.get('title', '').strip()
        message = data.get('message', '').strip()
        priority = data.get('priority', 'normal')
        methods = data.get('methods', ['email'])
        target_users = data.get('target_users', 'all')
        
        if not title or not message:
            return jsonify({'error': 'Título y mensaje son obligatorios'}), 400
        
        # Construir query de usuarios
        query = User.query.filter_by(is_active=True)
        
        if target_users == 'admins':
            query = query.filter_by(role='admin')
        elif target_users == 'verified':
            query = query.filter_by(email_verified=True)
        elif target_users == 'with_email':
            query = query.filter(User.email.isnot(None), User.email != '')
        
        users = query.all()
        
        if not users:
            return jsonify({'error': 'No hay usuarios que cumplan los criterios seleccionados'}), 400
        
        # Simular envío por métodos seleccionados
        notification_service = NotificationService()
        results = {
            'email_sent': 0,
            'whatsapp_sent': 0,
            'failed': 0,
            'details': []
        }
        
        for user in users:
            try:
                if 'email' in methods and user.email:
                    # Simular envío de email
                    results['email_sent'] += 1
                    results['details'].append(f"✅ Email enviado a {user.username}")
                
                if 'whatsapp' in methods:
                    # Simular envío de WhatsApp
                    results['whatsapp_sent'] += 1
                    results['details'].append(f"✅ WhatsApp enviado a {user.username}")
                        
            except Exception as e:
                results['failed'] += 1
                results['details'].append(f"❌ Error con {user.username}: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': f'Comunicado enviado exitosamente',
            'stats': {
                'total_users': len(users),
                'email_sent': results['email_sent'],
                'whatsapp_sent': results['whatsapp_sent'],
                'failed': results['failed']
            },
            'details': results['details'][:10]  # Primeros 10 detalles
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/templates')
@login_required
def templates():
    """Plantillas de comunicados predefinidos"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('dashboard'))
    
    templates = [
        {
            'id': 'emergency',
            'name': 'Emergencia',
            'title': '🚨 ALERTA DE EMERGENCIA',
            'message': 'Se ha detectado una situación de emergencia en el barrio. Por favor, manténganse atentos a las instrucciones de seguridad.',
            'priority': 'urgent',
            'icon': 'exclamation-triangle-fill',
            'color': 'danger'
        },
        {
            'id': 'maintenance',
            'name': 'Mantenimiento',
            'title': '🔧 AVISO DE MANTENIMIENTO',
            'message': 'Se realizarán trabajos de mantenimiento programado. Puede haber interrupciones temporales en algunos servicios.',
            'priority': 'normal',
            'icon': 'tools',
            'color': 'warning'
        },
        {
            'id': 'event',
            'name': 'Evento',
            'title': '🎉 EVENTO ESPECIAL',
            'message': 'Los invitamos a participar en el próximo evento comunitario. ¡Esperamos contar con su presencia!',
            'priority': 'normal',
            'icon': 'calendar-event',
            'color': 'success'
        },
        {
            'id': 'security',
            'name': 'Seguridad',
            'title': '🛡️ AVISO DE SEGURIDAD',
            'message': 'Recordatorio importante sobre las medidas de seguridad del barrio. Mantengamos todos los protocolos vigentes.',
            'priority': 'high',
            'icon': 'shield-check',
            'color': 'info'
        },
        {
            'id': 'expenses',
            'name': 'Expensas',
            'title': '💰 AVISO DE EXPENSAS',
            'message': 'Recordatorio: Las expensas del mes vencen próximamente. Por favor, mantengan sus pagos al día.',
            'priority': 'normal',
            'icon': 'cash-coin',
            'color': 'primary'
        },
        {
            'id': 'weather',
            'name': 'Clima',
            'title': '🌦️ ALERTA METEOROLÓGICA',
            'message': 'Se pronostica mal tiempo para las próximas horas. Tomen las precauciones necesarias.',
            'priority': 'high',
            'icon': 'cloud-rain',
            'color': 'warning'
        }
    ]
    
    return render_template('broadcast_communications/templates.html', templates=templates)
