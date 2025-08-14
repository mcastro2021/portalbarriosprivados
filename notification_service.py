"""
Sistema de notificaciones por Email y WhatsApp para expensas
"""

import smtplib
import requests
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime, timedelta
from flask import current_app
import json

class NotificationService:
    """Servicio de notificaciones por email y WhatsApp"""
    
    def __init__(self):
        self.email_config = None
        self.whatsapp_config = None
        self._load_config()
    
    def _load_config(self):
        """Cargar configuración desde variables de entorno"""
        try:
            # Configuración Email
            self.email_config = {
                'smtp_server': current_app.config.get('SMTP_SERVER', 'smtp.gmail.com'),
                'smtp_port': current_app.config.get('SMTP_PORT', 587),
                'email': current_app.config.get('SMTP_EMAIL'),
                'password': current_app.config.get('SMTP_PASSWORD'),
                'from_name': current_app.config.get('SMTP_FROM_NAME', 'Barrio Privado')
            }
            
            # Configuración WhatsApp (usando API de WhatsApp Business)
            self.whatsapp_config = {
                'api_url': current_app.config.get('WHATSAPP_API_URL'),
                'api_token': current_app.config.get('WHATSAPP_API_TOKEN'),
                'phone_number_id': current_app.config.get('WHATSAPP_PHONE_ID')
            }
            
        except Exception as e:
            print(f"⚠️ Error cargando configuración de notificaciones: {e}")
    
    def send_expense_notification(self, user, expense, method='email'):
        """Enviar notificación de expensa"""
        try:
            if method == 'email':
                return self._send_expense_email(user, expense)
            elif method == 'whatsapp':
                return self._send_expense_whatsapp(user, expense)
            else:
                return False, "Método no soportado"
        except Exception as e:
            return False, str(e)
    
    def _send_expense_email(self, user, expense):
        """Enviar expensa por email"""
        if not self.email_config['email'] or not self.email_config['password']:
            return False, "Configuración de email no disponible"
        
        try:
            # Crear mensaje
            msg = MimeMultipart('alternative')
            msg['Subject'] = f"Expensa {expense.period} - Barrio Tejas 4"
            msg['From'] = f"{self.email_config['from_name']} <{self.email_config['email']}>"
            msg['To'] = user.email
            
            # Contenido HTML
            html_content = self._generate_expense_email_html(user, expense)
            html_part = MimeText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Enviar email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['email'], self.email_config['password'])
                server.send_message(msg)
            
            return True, "Email enviado exitosamente"
            
        except Exception as e:
            return False, f"Error enviando email: {str(e)}"
    
    def _send_expense_whatsapp(self, user, expense):
        """Enviar expensa por WhatsApp"""
        if not self.whatsapp_config['api_token'] or not user.phone:
            return False, "Configuración de WhatsApp no disponible o usuario sin teléfono"
        
        try:
            # Formatear número de teléfono
            phone = self._format_phone_number(user.phone)
            
            # Mensaje de WhatsApp
            message = self._generate_expense_whatsapp_message(user, expense)
            
            # Enviar via API de WhatsApp Business
            headers = {
                'Authorization': f'Bearer {self.whatsapp_config["api_token"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'messaging_product': 'whatsapp',
                'to': phone,
                'type': 'text',
                'text': {'body': message}
            }
            
            response = requests.post(
                f"{self.whatsapp_config['api_url']}/{self.whatsapp_config['phone_number_id']}/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return True, "WhatsApp enviado exitosamente"
            else:
                return False, f"Error API WhatsApp: {response.status_code}"
                
        except Exception as e:
            return False, f"Error enviando WhatsApp: {str(e)}"
    
    def _generate_expense_email_html(self, user, expense):
        """Generar contenido HTML para email de expensa"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Expensa {expense.period}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; }}
        .expense-details {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .amount {{ font-size: 2em; font-weight: bold; color: #667eea; text-align: center; margin: 20px 0; }}
        .due-date {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #6c757d; }}
        .btn {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 Barrio Tejas 4</h1>
            <h2>Expensa {expense.period}</h2>
        </div>
        
        <div class="content">
            <p>Estimado/a <strong>{user.name}</strong>,</p>
            
            <p>Le enviamos el detalle de su expensa correspondiente al período <strong>{expense.period}</strong>:</p>
            
            <div class="expense-details">
                <h3>📋 Detalles de la Expensa</h3>
                <table width="100%" style="border-collapse: collapse;">
                    <tr>
                        <td><strong>Período:</strong></td>
                        <td>{expense.period}</td>
                    </tr>
                    <tr>
                        <td><strong>Dirección:</strong></td>
                        <td>{user.address or 'No especificada'}</td>
                    </tr>
                    <tr>
                        <td><strong>Fecha de Emisión:</strong></td>
                        <td>{expense.created_at.strftime('%d/%m/%Y') if expense.created_at else 'N/A'}</td>
                    </tr>
                    <tr>
                        <td><strong>Fecha de Vencimiento:</strong></td>
                        <td>{expense.due_date.strftime('%d/%m/%Y') if expense.due_date else 'N/A'}</td>
                    </tr>
                </table>
            </div>
            
            <div class="amount">
                💰 ${expense.amount:,.0f}
            </div>
            
            <div class="due-date">
                <strong>⚠️ Fecha de Vencimiento:</strong> {expense.due_date.strftime('%d de %B de %Y') if expense.due_date else 'No especificada'}
                <br>
                <small>Le recordamos abonar antes de la fecha de vencimiento para evitar recargos.</small>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://tudominio.com/expenses" class="btn">💳 Pagar Online</a>
            </div>
            
            <h4>💳 Formas de Pago:</h4>
            <ul>
                <li><strong>Transferencia Bancaria:</strong> CBU 1234567890123456789012</li>
                <li><strong>Pago Online:</strong> Desde el portal web</li>
                <li><strong>Efectivo:</strong> En administración (Lun-Vie 9-17hs)</li>
            </ul>
            
            <p><strong>📞 Consultas:</strong></p>
            <ul>
                <li>Email: administracion@tejas4.com</li>
                <li>Teléfono: +54 11 4444-5555</li>
                <li>WhatsApp: +54 9 11 4444-5555</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Este es un email automático del sistema de Barrio Tejas 4</p>
            <p>Si tiene alguna consulta, no dude en contactarnos</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _generate_expense_whatsapp_message(self, user, expense):
        """Generar mensaje de WhatsApp para expensa"""
        due_date_str = expense.due_date.strftime('%d/%m/%Y') if expense.due_date else 'No especificada'
        
        return f"""🏠 *BARRIO TEJAS 4*
📧 *Expensa {expense.period}*

Hola *{user.name}*! 👋

💰 *Monto:* ${expense.amount:,.0f}
📅 *Vence:* {due_date_str}
🏠 *Dirección:* {user.address or 'No especificada'}

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
        # Remover espacios, guiones y otros caracteres
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Agregar código de país si no lo tiene
        if len(clean_phone) == 10 and clean_phone.startswith('11'):
            clean_phone = '54' + clean_phone
        elif len(clean_phone) == 11 and clean_phone.startswith('011'):
            clean_phone = '54' + clean_phone[1:]
        elif not clean_phone.startswith('54'):
            clean_phone = '54' + clean_phone
        
        return clean_phone
    
    def send_bulk_expense_notifications(self, expenses_data, method='email'):
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

class ExpenseNotificationScheduler:
    """Programador de notificaciones de expensas"""
    
    @staticmethod
    def get_pending_notifications():
        """Obtener expensas pendientes de notificación"""
        from models import Expense, User
        from datetime import datetime, timedelta
        
        # Expensas que vencen en 7 días
        upcoming_due = datetime.now() + timedelta(days=7)
        
        pending_expenses = Expense.query.join(User).filter(
            Expense.status == 'pending',
            Expense.due_date <= upcoming_due,
            Expense.notification_sent != True  # Agregar este campo al modelo
        ).all()
        
        return [(expense.user, expense) for expense in pending_expenses]
    
    @staticmethod
    def mark_notification_sent(expense_id):
        """Marcar notificación como enviada"""
        from models import db, Expense
        
        expense = Expense.query.get(expense_id)
        if expense:
            expense.notification_sent = True
            expense.notification_date = datetime.now()
            db.session.commit()

# Funciones de utilidad para administradores
def test_email_config():
    """Probar configuración de email"""
    try:
        service = NotificationService()
        if not service.email_config['email']:
            return False, "Email no configurado"
        return True, "Configuración de email OK"
    except Exception as e:
        return False, str(e)

def test_whatsapp_config():
    """Probar configuración de WhatsApp"""
    try:
        service = NotificationService()
        if not service.whatsapp_config['api_token']:
            return False, "WhatsApp no configurado"
        return True, "Configuración de WhatsApp OK"
    except Exception as e:
        return False, str(e)
