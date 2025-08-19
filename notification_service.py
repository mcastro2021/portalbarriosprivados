"""
Sistema de notificaciones por Email y WhatsApp para expensas
"""

import smtplib
import requests
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from flask import current_app
import logging

class NotificationService:
    """Servicio de notificaciones por email y WhatsApp"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.whatsapp_api_key = os.getenv('WHATSAPP_API_KEY', '')
        self.whatsapp_phone_id = os.getenv('WHATSAPP_PHONE_ID', '')
        self.whatsapp_business_id = os.getenv('WHATSAPP_BUSINESS_ID', '')
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def send_email(self, to_email, subject, body, html_body=None, attachments=None):
        """
        Enviar email usando SMTP
        
        Args:
            to_email (str): Email del destinatario
            subject (str): Asunto del email
            body (str): Cuerpo del email en texto plano
            html_body (str): Cuerpo del email en HTML (opcional)
            attachments (list): Lista de archivos adjuntos (opcional)
        
        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        try:
            if not all([self.smtp_username, self.smtp_password]):
                self.logger.error("Configuración de SMTP incompleta")
                return False
            
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Agregar cuerpo del mensaje
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Agregar archivos adjuntos
            if attachments:
                for attachment in attachments:
                    if os.path.exists(attachment):
                        with open(attachment, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(attachment)}'
                        )
                        msg.attach(part)
            
            # Conectar y enviar
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            self.logger.info(f"Email enviado exitosamente a {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al enviar email a {to_email}: {str(e)}")
            return False
    
    def send_whatsapp(self, phone_number, message, template_name=None, template_data=None):
        """
        Enviar mensaje de WhatsApp usando la API de Meta
        
        Args:
            phone_number (str): Número de teléfono con código de país (ej: 5491112345678)
            message (str): Mensaje a enviar
            template_name (str): Nombre de la plantilla (opcional)
            template_data (dict): Datos para la plantilla (opcional)
        
        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        try:
            if not all([self.whatsapp_api_key, self.whatsapp_phone_id]):
                self.logger.error("Configuración de WhatsApp incompleta")
                return False
            
            # Formatear número de teléfono
            if not phone_number.startswith('54'):
                phone_number = '54' + phone_number.lstrip('+')
            
            url = f"https://graph.facebook.com/v18.0/{self.whatsapp_phone_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.whatsapp_api_key}',
                'Content-Type': 'application/json'
            }
            
            if template_name and template_data:
                # Usar plantilla
                payload = {
                    'messaging_product': 'whatsapp',
                    'to': phone_number,
                    'type': 'template',
                    'template': {
                        'name': template_name,
                        'language': {
                            'code': 'es'
                        },
                        'components': []
                    }
                }
                
                # Agregar variables a la plantilla
                if template_data:
                    payload['template']['components'].append({
                        'type': 'body',
                        'parameters': [
                            {'type': 'text', 'text': str(value)} 
                            for value in template_data.values()
                        ]
                    })
            else:
                # Mensaje de texto simple
                payload = {
                    'messaging_product': 'whatsapp',
                    'to': phone_number,
                    'type': 'text',
                    'text': {
                        'body': message
                    }
                }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                self.logger.info(f"WhatsApp enviado exitosamente a {phone_number}")
                return True
            else:
                self.logger.error(f"Error al enviar WhatsApp: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error al enviar WhatsApp a {phone_number}: {str(e)}")
            return False
    
    def send_notification(self, user, notification_type, data, channels=None):
        """
        Enviar notificación por múltiples canales
        
        Args:
            user: Objeto usuario
            notification_type (str): Tipo de notificación
            data (dict): Datos de la notificación
            channels (list): Canales a usar ['email', 'whatsapp']
        
        Returns:
            dict: Resultado del envío por cada canal
        """
        if channels is None:
            channels = ['email']
        
        results = {}
        
        # Preparar contenido según el tipo de notificación
        content = self._prepare_content(notification_type, data)
        
        # Enviar por email
        if 'email' in channels and user.email:
            results['email'] = self.send_email(
                to_email=user.email,
                subject=content['subject'],
                body=content['text_body'],
                html_body=content['html_body']
            )
        
        # Enviar por WhatsApp
        if 'whatsapp' in channels and user.phone:
            results['whatsapp'] = self.send_whatsapp(
                phone_number=user.phone,
                message=content['whatsapp_body']
            )
        
        return results
    
    def _prepare_content(self, notification_type, data):
        """Preparar contenido según el tipo de notificación"""
        
        if notification_type == 'welcome':
            return {
                'subject': '¡Bienvenido al Portal del Barrio!',
                'text_body': f"""
Hola {data.get('name', 'Usuario')},

¡Bienvenido al portal oficial de nuestro barrio cerrado!

Tu cuenta ha sido creada exitosamente con las siguientes credenciales:
- Usuario: {data.get('username', '')}
- Email: {data.get('email', '')}

Para acceder al portal, visita: {data.get('portal_url', 'https://portalbarriosprivados.onrender.com')}

Si tienes alguna pregunta, no dudes en contactarnos.

Saludos,
Administración del Barrio
                """,
                'html_body': f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f8f9fa; }}
        .footer {{ text-align: center; padding: 20px; color: #666; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>¡Bienvenido al Portal del Barrio!</h1>
        </div>
        <div class="content">
            <h2>Hola {data.get('name', 'Usuario')},</h2>
            <p>¡Bienvenido al portal oficial de nuestro barrio cerrado!</p>
            <p>Tu cuenta ha sido creada exitosamente con las siguientes credenciales:</p>
            <ul>
                <li><strong>Usuario:</strong> {data.get('username', '')}</li>
                <li><strong>Email:</strong> {data.get('email', '')}</li>
            </ul>
            <p style="text-align: center;">
                <a href="{data.get('portal_url', 'https://portalbarriosprivados.onrender.com')}" class="btn">
                    Acceder al Portal
                </a>
            </p>
            <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
        </div>
        <div class="footer">
            <p>Saludos,<br>Administración del Barrio</p>
        </div>
    </div>
</body>
</html>
                """,
                'whatsapp_body': f"¡Hola {data.get('name', 'Usuario')}! 🏠\n\n¡Bienvenido al portal oficial de nuestro barrio cerrado!\n\nTu cuenta ha sido creada exitosamente.\n\nUsuario: {data.get('username', '')}\n\nPara acceder: {data.get('portal_url', 'https://portalbarriosprivados.onrender.com')}\n\n¡Esperamos verte pronto!"
            }
        
        elif notification_type == 'visit_approved':
            return {
                'subject': 'Visita Aprobada - Portal del Barrio',
                'text_body': f"""
Hola {data.get('resident_name', 'Usuario')},

Tu visita ha sido aprobada:

Visitante: {data.get('visitor_name', '')}
Fecha: {data.get('visit_date', '')}
Hora: {data.get('visit_time', '')}
Propósito: {data.get('purpose', '')}

Código QR: {data.get('qr_code', '')}

Recuerda que el visitante debe presentar este código QR en la entrada.

Saludos,
Seguridad del Barrio
                """,
                'html_body': f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #28a745; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f8f9fa; }}
        .qr-code {{ text-align: center; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Visita Aprobada</h1>
        </div>
        <div class="content">
            <h2>Hola {data.get('resident_name', 'Usuario')},</h2>
            <p>Tu visita ha sido aprobada:</p>
            <ul>
                <li><strong>Visitante:</strong> {data.get('visitor_name', '')}</li>
                <li><strong>Fecha:</strong> {data.get('visit_date', '')}</li>
                <li><strong>Hora:</strong> {data.get('visit_time', '')}</li>
                <li><strong>Propósito:</strong> {data.get('purpose', '')}</li>
            </ul>
            <div class="qr-code">
                <h3>Código QR:</h3>
                <p><strong>{data.get('qr_code', '')}</strong></p>
            </div>
            <p><strong>Importante:</strong> El visitante debe presentar este código QR en la entrada.</p>
        </div>
        <div class="footer">
            <p>Saludos,<br>Seguridad del Barrio</p>
        </div>
    </div>
</body>
</html>
                """,
                'whatsapp_body': f"✅ Visita Aprobada\n\nHola {data.get('resident_name', 'Usuario')}!\n\nTu visita ha sido aprobada:\n\n👤 Visitante: {data.get('visitor_name', '')}\n📅 Fecha: {data.get('visit_date', '')}\n🕐 Hora: {data.get('visit_time', '')}\n🎯 Propósito: {data.get('purpose', '')}\n\n📱 Código QR: {data.get('qr_code', '')}\n\n⚠️ El visitante debe presentar este código en la entrada."
            }
        
        elif notification_type == 'expense_due':
            return {
                'subject': 'Expensa Vencida - Portal del Barrio',
                'text_body': f"""
Hola {data.get('resident_name', 'Usuario')},

Tienes una expensa vencida:

Descripción: {data.get('description', '')}
Monto: ${data.get('amount', '0')}
Vencimiento: {data.get('due_date', '')}
Período: {data.get('period', '')}

Para realizar el pago, accede al portal: {data.get('portal_url', 'https://portalbarriosprivados.onrender.com')}

Saludos,
Administración del Barrio
                """,
                'html_body': f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #dc3545; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f8f9fa; }}
        .amount {{ font-size: 24px; color: #dc3545; font-weight: bold; text-align: center; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ Expensa Vencida</h1>
        </div>
        <div class="content">
            <h2>Hola {data.get('resident_name', 'Usuario')},</h2>
            <p>Tienes una expensa vencida:</p>
            <ul>
                <li><strong>Descripción:</strong> {data.get('description', '')}</li>
                <li><strong>Vencimiento:</strong> {data.get('due_date', '')}</li>
                <li><strong>Período:</strong> {data.get('period', '')}</li>
            </ul>
            <div class="amount">
                ${data.get('amount', '0')}
            </div>
            <p style="text-align: center;">
                <a href="{data.get('portal_url', 'https://portalbarriosprivados.onrender.com')}" class="btn">
                    Realizar Pago
                </a>
            </p>
        </div>
        <div class="footer">
            <p>Saludos,<br>Administración del Barrio</p>
        </div>
    </div>
</body>
</html>
                """,
                'whatsapp_body': f"⚠️ Expensa Vencida\n\nHola {data.get('resident_name', 'Usuario')}!\n\nTienes una expensa vencida:\n\n📋 Descripción: {data.get('description', '')}\n💰 Monto: ${data.get('amount', '0')}\n📅 Vencimiento: {data.get('due_date', '')}\n📊 Período: {data.get('period', '')}\n\n💳 Para pagar: {data.get('portal_url', 'https://portalbarriosprivados.onrender.com')}"
            }
        
        elif notification_type == 'maintenance_alert':
            return {
                'subject': 'Alerta de Mantenimiento - Portal del Barrio',
                'text_body': f"""
Hola {data.get('resident_name', 'Usuario')},

Se ha programado un mantenimiento:

Tipo: {data.get('type', '')}
Descripción: {data.get('description', '')}
Fecha: {data.get('date', '')}
Hora: {data.get('time', '')}
Duración: {data.get('duration', '')}

Afectará: {data.get('affected_areas', '')}

Por favor, ten en cuenta esta información.

Saludos,
Mantenimiento del Barrio
                """,
                'html_body': f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #ffc107; color: #333; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f8f9fa; }}
        .footer {{ text-align: center; padding: 20px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 Alerta de Mantenimiento</h1>
        </div>
        <div class="content">
            <h2>Hola {data.get('resident_name', 'Usuario')},</h2>
            <p>Se ha programado un mantenimiento:</p>
            <ul>
                <li><strong>Tipo:</strong> {data.get('type', '')}</li>
                <li><strong>Descripción:</strong> {data.get('description', '')}</li>
                <li><strong>Fecha:</strong> {data.get('date', '')}</li>
                <li><strong>Hora:</strong> {data.get('time', '')}</li>
                <li><strong>Duración:</strong> {data.get('duration', '')}</li>
            </ul>
            <p><strong>Afectará:</strong> {data.get('affected_areas', '')}</p>
            <p>Por favor, ten en cuenta esta información.</p>
        </div>
        <div class="footer">
            <p>Saludos,<br>Mantenimiento del Barrio</p>
        </div>
    </div>
</body>
</html>
                """,
                'whatsapp_body': f"🔧 Alerta de Mantenimiento\n\nHola {data.get('resident_name', 'Usuario')}!\n\nSe ha programado un mantenimiento:\n\n🔧 Tipo: {data.get('type', '')}\n📋 Descripción: {data.get('description', '')}\n📅 Fecha: {data.get('date', '')}\n🕐 Hora: {data.get('time', '')}\n⏱️ Duración: {data.get('duration', '')}\n\n📍 Afectará: {data.get('affected_areas', '')}\n\n⚠️ Por favor, ten en cuenta esta información."
            }
        
        else:
            # Notificación genérica
            return {
                'subject': data.get('subject', 'Notificación del Portal del Barrio'),
                'text_body': data.get('message', ''),
                'html_body': data.get('html_message', data.get('message', '')),
                'whatsapp_body': data.get('whatsapp_message', data.get('message', ''))
            }
    
    def send_bulk_notification(self, users, notification_type, data, channels=None):
        """
        Enviar notificación masiva a múltiples usuarios
        
        Args:
            users (list): Lista de objetos usuario
            notification_type (str): Tipo de notificación
            data (dict): Datos de la notificación
            channels (list): Canales a usar
        
        Returns:
            dict: Estadísticas del envío
        """
        stats = {
            'total_users': len(users),
            'email_sent': 0,
            'whatsapp_sent': 0,
            'errors': 0
        }
        
        for user in users:
            try:
                results = self.send_notification(user, notification_type, data, channels)
                
                if results.get('email'):
                    stats['email_sent'] += 1
                if results.get('whatsapp'):
                    stats['whatsapp_sent'] += 1
                    
            except Exception as e:
                self.logger.error(f"Error al enviar notificación a {user.email}: {str(e)}")
                stats['errors'] += 1
        
        return stats

# Instancia global del servicio
notification_service = NotificationService()
