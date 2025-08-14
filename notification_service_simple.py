"""
Sistema de notificaciones simplificado para evitar problemas de importación
"""

import requests
from datetime import datetime, timedelta
from flask import current_app
import json

class NotificationService:
    """Servicio simplificado de notificaciones"""
    
    def __init__(self):
        self.whatsapp_config = self._load_whatsapp_config()
    
    def _load_whatsapp_config(self):
        """Cargar configuración de WhatsApp"""
        return {
            'api_url': current_app.config.get('WHATSAPP_API_URL', 'https://graph.facebook.com/v17.0'),
            'api_token': current_app.config.get('WHATSAPP_API_TOKEN'),
            'phone_number_id': current_app.config.get('WHATSAPP_PHONE_ID')
        }
    
    def send_expense_notification(self, user, expense, method='whatsapp'):
        """Enviar notificación de expensa (solo WhatsApp por ahora)"""
        try:
            if method in ['whatsapp', 'both']:
                return self._send_expense_whatsapp(user, expense)
            elif method == 'email':
                return True, "Email temporalmente deshabilitado - usar WhatsApp"
            else:
                return False, "Método no soportado"
        except Exception as e:
            return False, str(e)
    
    def _send_expense_whatsapp(self, user, expense):
        """Enviar expensa por WhatsApp"""
        if not self.whatsapp_config['api_token'] or not hasattr(user, 'phone') or not user.phone:
            return False, "Configuración de WhatsApp no disponible o usuario sin teléfono"
        
        try:
            # Formatear número de teléfono
            phone = self._format_phone_number(user.phone)
            
            # Mensaje de WhatsApp
            message = self._generate_expense_whatsapp_message(user, expense)
            
            # Simular envío exitoso por ahora
            print(f"📱 WhatsApp simulado para {user.username}: {message[:50]}...")
            return True, "WhatsApp simulado exitosamente (configurar API real)"
                
        except Exception as e:
            return False, f"Error enviando WhatsApp: {str(e)}"
    
    def _generate_expense_whatsapp_message(self, user, expense):
        """Generar mensaje de WhatsApp para expensa"""
        period = getattr(expense, 'period', None) or getattr(expense, 'month', 'Mes actual')
        amount = getattr(expense, 'amount', 0)
        due_date = getattr(expense, 'due_date', None)
        due_date_str = due_date.strftime('%d/%m/%Y') if due_date else 'No especificada'
        user_address = getattr(user, 'address', None) or 'No especificada'
        
        return f"""🏠 *BARRIO TEJAS 4*
📧 *Expensa {period}*

Hola *{user.name}*! 👋

💰 *Monto:* ${amount:,.0f}
📅 *Vence:* {due_date_str}
🏠 *Dirección:* {user_address}

💳 *Formas de Pago:*
• Transferencia: CBU 1234567890123456789012
• Online: https://tudominio.com/expenses
• Efectivo: Administración (Lun-Vie 9-17hs)

📞 *Consultas:*
• Tel: +54 11 4444-5555
• Email: administracion@tejas4.com

¡Gracias por mantener nuestro barrio al día! ✅

_Mensaje automático - No responder_"""
    
    def _format_phone_number(self, phone):
        """Formatear número de teléfono para WhatsApp"""
        if not phone:
            return None
            
        # Remover espacios, guiones y otros caracteres
        clean_phone = ''.join(filter(str.isdigit, str(phone)))
        
        # Agregar código de país si no lo tiene
        if len(clean_phone) == 10 and clean_phone.startswith('11'):
            clean_phone = '54' + clean_phone
        elif len(clean_phone) == 11 and clean_phone.startswith('011'):
            clean_phone = '54' + clean_phone[1:]
        elif not clean_phone.startswith('54'):
            clean_phone = '54' + clean_phone
        
        return clean_phone
    
    def send_bulk_expense_notifications(self, expenses_data, method='whatsapp'):
        """Enviar notificaciones masivas de expensas"""
        results = {
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        for user, expense in expenses_data:
            try:
                success, message = self.send_expense_notification(user, expense, method)
                
                if success:
                    results['success'] += 1
                    results['details'].append(f"✅ {user.username}: {message}")
                else:
                    results['failed'] += 1
                    results['details'].append(f"❌ {user.username}: {message}")
                    
            except Exception as e:
                results['failed'] += 1
                results['details'].append(f"❌ {user.username}: Error - {str(e)}")
        
        return results

def test_whatsapp_config():
    """Probar configuración de WhatsApp"""
    try:
        service = NotificationService()
        if not service.whatsapp_config['api_token']:
            return False, "WhatsApp no configurado"
        return True, "Configuración de WhatsApp OK (simulada)"
    except Exception as e:
        return False, str(e)

def test_email_config():
    """Probar configuración de email"""
    return True, "Email temporalmente deshabilitado - usar WhatsApp"
