"""
Fase 2: Automatización Inteligente
Sistema de automatización inteligente para reducir trabajo manual y mejorar eficiencia operativa.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
from threading import Thread
import schedule
import time

from flask import current_app
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import joinedload

from models import db, User, Maintenance, Notification, Visit, Reservation, SecurityReport, Expense
from notification_service import NotificationService
from knowledge_base import BarrioKnowledgeBase


class AutomationType(Enum):
    """Tipos de automatización disponibles"""
    MAINTENANCE_SCHEDULING = "maintenance_scheduling"
    VISIT_APPROVAL = "visit_approval"
    EXPENSE_ALERTS = "expense_alerts"
    SECURITY_MONITORING = "security_monitoring"
    RESERVATION_OPTIMIZATION = "reservation_optimization"
    NOTIFICATION_SMART = "notification_smart"
    WORKFLOW_AUTOMATION = "workflow_automation"


class WorkflowStatus(Enum):
    """Estados de un workflow"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AutomationRule:
    """Regla de automatización"""
    id: str
    name: str
    description: str
    automation_type: AutomationType
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    priority: int = 1
    enabled: bool = True
    created_at: datetime = None
    last_executed: datetime = None
    execution_count: int = 0


class IntelligentWorkflowEngine:
    """Motor de workflows inteligentes"""
    
    def __init__(self):
        self.workflows = {}
        self.rules = []
        self.execution_history = []
        self.logger = logging.getLogger(__name__)
        
    def add_workflow(self, workflow_id: str, steps: List[Dict], conditions: Dict = None):
        """Agregar un nuevo workflow"""
        self.workflows[workflow_id] = {
            'steps': steps,
            'conditions': conditions or {},
            'status': WorkflowStatus.PENDING,
            'current_step': 0,
            'data': {},
            'created_at': datetime.now()
        }
        
    def execute_workflow(self, workflow_id: str, initial_data: Dict = None) -> bool:
        """Ejecutar un workflow"""
        if workflow_id not in self.workflows:
            self.logger.error(f"Workflow {workflow_id} no encontrado")
            return False
            
        workflow = self.workflows[workflow_id]
        workflow['status'] = WorkflowStatus.IN_PROGRESS
        workflow['data'] = initial_data or {}
        
        try:
            for i, step in enumerate(workflow['steps']):
                workflow['current_step'] = i
                
                # Verificar condiciones del paso
                if not self._evaluate_conditions(step.get('conditions', {}), workflow['data']):
                    self.logger.info(f"Condiciones no cumplidas para paso {i} del workflow {workflow_id}")
                    continue
                
                # Ejecutar acción del paso
                success = self._execute_step_action(step, workflow['data'])
                if not success:
                    workflow['status'] = WorkflowStatus.FAILED
                    return False
                    
            workflow['status'] = WorkflowStatus.COMPLETED
            self.execution_history.append({
                'workflow_id': workflow_id,
                'status': WorkflowStatus.COMPLETED,
                'executed_at': datetime.now(),
                'data': workflow['data']
            })
            return True
            
        except Exception as e:
            self.logger.error(f"Error ejecutando workflow {workflow_id}: {e}")
            workflow['status'] = WorkflowStatus.FAILED
            return False
    
    def _evaluate_conditions(self, conditions: Dict, data: Dict) -> bool:
        """Evaluar condiciones de un paso"""
        for condition in conditions:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            if field not in data:
                return False
                
            field_value = data[field]
            
            if operator == 'equals' and field_value != value:
                return False
            elif operator == 'not_equals' and field_value == value:
                return False
            elif operator == 'greater_than' and field_value <= value:
                return False
            elif operator == 'less_than' and field_value >= value:
                return False
            elif operator == 'contains' and value not in str(field_value):
                return False
                
        return True
    
    def _execute_step_action(self, step: Dict, data: Dict) -> bool:
        """Ejecutar acción de un paso"""
        action_type = step.get('action_type')
        
        try:
            if action_type == 'send_notification':
                return self._send_notification_action(step, data)
            elif action_type == 'create_record':
                return self._create_record_action(step, data)
            elif action_type == 'update_record':
                return self._update_record_action(step, data)
            elif action_type == 'call_api':
                return self._call_api_action(step, data)
            elif action_type == 'wait':
                return self._wait_action(step, data)
            else:
                self.logger.error(f"Tipo de acción no soportado: {action_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error ejecutando acción {action_type}: {e}")
            return False
    
    def _send_notification_action(self, step: Dict, data: Dict) -> bool:
        """Acción para enviar notificación"""
        notification_service = NotificationService()
        
        recipients = step.get('recipients', [])
        if isinstance(recipients, str) and recipients in data:
            recipients = data[recipients]
            
        message = step.get('message', '')
        # Reemplazar variables en el mensaje
        for key, value in data.items():
            message = message.replace(f"{{{key}}}", str(value))
            
        notification_service.send_notification(
            recipients=recipients,
            title=step.get('title', 'Notificación Automática'),
            message=message,
            notification_type=step.get('notification_type', 'info')
        )
        return True
    
    def _create_record_action(self, step: Dict, data: Dict) -> bool:
        """Acción para crear registro en base de datos"""
        model_name = step.get('model')
        fields = step.get('fields', {})
        
        # Mapear campos con datos del workflow
        record_data = {}
        for field, value in fields.items():
            if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                key = value[1:-1]
                record_data[field] = data.get(key)
            else:
                record_data[field] = value
        
        # Crear registro según el modelo
        if model_name == 'Maintenance':
            record = Maintenance(**record_data)
        elif model_name == 'Notification':
            record = Notification(**record_data)
        elif model_name == 'SecurityReport':
            record = SecurityReport(**record_data)
        else:
            self.logger.error(f"Modelo no soportado: {model_name}")
            return False
            
        db.session.add(record)
        db.session.commit()
        
        # Agregar ID del registro creado a los datos del workflow
        data[f'{model_name.lower()}_id'] = record.id
        return True
    
    def _update_record_action(self, step: Dict, data: Dict) -> bool:
        """Acción para actualizar registro"""
        model_name = step.get('model')
        record_id = step.get('record_id')
        fields = step.get('fields', {})
        
        # Obtener registro
        if model_name == 'Maintenance':
            record = Maintenance.query.get(record_id)
        elif model_name == 'User':
            record = User.query.get(record_id)
        else:
            self.logger.error(f"Modelo no soportado para actualización: {model_name}")
            return False
            
        if not record:
            self.logger.error(f"Registro no encontrado: {model_name} {record_id}")
            return False
        
        # Actualizar campos
        for field, value in fields.items():
            if hasattr(record, field):
                setattr(record, field, value)
                
        db.session.commit()
        return True
    
    def _call_api_action(self, step: Dict, data: Dict) -> bool:
        """Acción para llamar API externa"""
        # Implementar llamadas a APIs externas
        # Por ahora, simulamos éxito
        return True
    
    def _wait_action(self, step: Dict, data: Dict) -> bool:
        """Acción para esperar un tiempo"""
        wait_time = step.get('wait_time', 0)
        time.sleep(wait_time)
        return True


class SmartMaintenanceScheduler:
    """Programador inteligente de mantenimiento"""
    
    def __init__(self):
        self.scheduler = schedule.Scheduler()
        self.logger = logging.getLogger(__name__)
        self.workflow_engine = IntelligentWorkflowEngine()
        self._setup_default_workflows()
        
    def _setup_default_workflows(self):
        """Configurar workflows por defecto"""
        
        # Workflow para mantenimiento preventivo
        self.workflow_engine.add_workflow(
            'preventive_maintenance',
            steps=[
                {
                    'action_type': 'create_record',
                    'model': 'Maintenance',
                    'fields': {
                        'title': 'Mantenimiento Preventivo Programado',
                        'description': 'Mantenimiento preventivo automático para {equipment}',
                        'priority': 'medium',
                        'status': 'scheduled',
                        'scheduled_date': '{scheduled_date}',
                        'equipment': '{equipment}'
                    }
                },
                {
                    'action_type': 'send_notification',
                    'recipients': 'maintenance_team',
                    'title': 'Nuevo Mantenimiento Programado',
                    'message': 'Se ha programado mantenimiento preventivo para {equipment} el {scheduled_date}',
                    'notification_type': 'maintenance'
                }
            ]
        )
        
        # Workflow para alertas de gastos
        self.workflow_engine.add_workflow(
            'expense_alert',
            steps=[
                {
                    'action_type': 'send_notification',
                    'recipients': 'admin_users',
                    'title': 'Alerta de Gasto Excesivo',
                    'message': 'El gasto en {category} ha superado el límite establecido: ${amount}',
                    'notification_type': 'alert'
                }
            ]
        )
    
    def schedule_preventive_maintenance(self, equipment: str, frequency_days: int):
        """Programar mantenimiento preventivo"""
        next_date = datetime.now() + timedelta(days=frequency_days)
        
        # Crear tarea programada
        self.scheduler.every(frequency_days).days.do(
            self._execute_preventive_maintenance,
            equipment=equipment,
            scheduled_date=next_date
        )
        
        self.logger.info(f"Mantenimiento preventivo programado para {equipment} cada {frequency_days} días")
    
    def _execute_preventive_maintenance(self, equipment: str, scheduled_date: datetime):
        """Ejecutar mantenimiento preventivo"""
        workflow_data = {
            'equipment': equipment,
            'scheduled_date': scheduled_date.strftime('%Y-%m-%d')
        }
        
        success = self.workflow_engine.execute_workflow('preventive_maintenance', workflow_data)
        
        if success:
            self.logger.info(f"Mantenimiento preventivo ejecutado para {equipment}")
        else:
            self.logger.error(f"Error ejecutando mantenimiento preventivo para {equipment}")
    
    def start_scheduler(self):
        """Iniciar el programador en un hilo separado"""
        def run_scheduler():
            while True:
                self.scheduler.run_pending()
                time.sleep(60)  # Verificar cada minuto
                
        scheduler_thread = Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        self.logger.info("Programador de mantenimiento iniciado")


class IntelligentNotificationSystem:
    """Sistema de notificaciones inteligente"""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.knowledge_base = BarrioKnowledgeBase()
        self.logger = logging.getLogger(__name__)
        self.user_preferences = {}
        self.notification_rules = []
        
    def set_user_preferences(self, user_id: int, preferences: Dict):
        """Configurar preferencias de notificación del usuario"""
        self.user_preferences[user_id] = preferences
        
    def add_notification_rule(self, rule: AutomationRule):
        """Agregar regla de notificación"""
        self.notification_rules.append(rule)
        
    def send_smart_notification(self, user_id: int, event_type: str, data: Dict):
        """Enviar notificación inteligente basada en preferencias y contexto"""
        
        # Obtener preferencias del usuario
        preferences = self.user_preferences.get(user_id, {})
        
        # Verificar si el usuario quiere este tipo de notificación
        if not preferences.get(f'notify_{event_type}', True):
            return
            
        # Determinar canal preferido
        channel = preferences.get('preferred_channel', 'email')
        
        # Generar mensaje contextual
        message = self._generate_contextual_message(event_type, data, user_id)
        
        # Enviar notificación
        if channel == 'email':
            self.notification_service.send_email_notification(
                user_id=user_id,
                subject=f"Notificación: {event_type.title()}",
                message=message
            )
        elif channel == 'whatsapp':
            self.notification_service.send_whatsapp_notification(
                user_id=user_id,
                message=message
            )
        else:
            # Notificación interna
            self.notification_service.send_notification(
                recipients=[user_id],
                title=f"Notificación: {event_type.title()}",
                message=message,
                notification_type='info'
            )
    
    def _generate_contextual_message(self, event_type: str, data: Dict, user_id: int) -> str:
        """Generar mensaje contextual basado en el tipo de evento y datos"""
        
        user = User.query.get(user_id)
        if not user:
            return "Notificación del sistema"
            
        if event_type == 'visit_request':
            return f"Hola {user.name}, tienes una solicitud de visita pendiente de {data.get('visitor_name', 'un visitante')} para el {data.get('visit_date', 'fecha no especificada')}."
            
        elif event_type == 'maintenance_completed':
            return f"El mantenimiento '{data.get('title', '')}' ha sido completado. Gracias por tu paciencia."
            
        elif event_type == 'payment_due':
            return f"Recordatorio: Tu cuota de {data.get('amount', '0')} vence el {data.get('due_date', 'pronto')}. Por favor, realiza el pago a tiempo."
            
        elif event_type == 'security_alert':
            return f"Alerta de seguridad: {data.get('description', 'Incidente reportado')}. Por favor, mantén la calma y sigue las instrucciones de seguridad."
            
        elif event_type == 'reservation_confirmed':
            return f"Tu reserva para {data.get('space_name', 'espacio común')} el {data.get('date', '')} ha sido confirmada."
            
        else:
            return f"Notificación del sistema: {data.get('message', 'Evento importante')}"
    
    def analyze_notification_patterns(self):
        """Analizar patrones de notificaciones para optimizar"""
        
        # Obtener estadísticas de notificaciones
        notifications = Notification.query.all()
        
        # Analizar patrones por tipo
        patterns = {}
        for notification in notifications:
            notification_type = notification.notification_type
            if notification_type not in patterns:
                patterns[notification_type] = {
                    'count': 0,
                    'read_count': 0,
                    'response_time': []
                }
            
            patterns[notification_type]['count'] += 1
            if notification.read_at:
                patterns[notification_type]['read_count'] += 1
                
        # Generar recomendaciones
        recommendations = []
        for notification_type, stats in patterns.items():
            read_rate = stats['read_count'] / stats['count'] if stats['count'] > 0 else 0
            
            if read_rate < 0.5:
                recommendations.append(f"Las notificaciones de tipo '{notification_type}' tienen baja tasa de lectura. Considerar cambiar el formato o timing.")
            elif read_rate > 0.9:
                recommendations.append(f"Las notificaciones de tipo '{notification_type}' son muy efectivas. Mantener el formato actual.")
                
        return recommendations


class AIWorkflowOptimizer:
    """Optimizador de workflows basado en IA"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.workflow_engine = IntelligentWorkflowEngine()
        
    def analyze_workflow_performance(self, workflow_id: str) -> Dict:
        """Analizar rendimiento de un workflow"""
        
        # Obtener historial de ejecución
        executions = [ex for ex in self.workflow_engine.execution_history if ex['workflow_id'] == workflow_id]
        
        if not executions:
            return {'error': 'No hay datos de ejecución para este workflow'}
            
        # Calcular métricas
        total_executions = len(executions)
        successful_executions = len([ex for ex in executions if ex['status'] == WorkflowStatus.COMPLETED])
        success_rate = successful_executions / total_executions
        
        # Tiempo promedio de ejecución (simulado)
        avg_execution_time = 2.5  # segundos
        
        return {
            'workflow_id': workflow_id,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'success_rate': success_rate,
            'avg_execution_time': avg_execution_time,
            'recommendations': self._generate_optimization_recommendations(success_rate, avg_execution_time)
        }
    
    def _generate_optimization_recommendations(self, success_rate: float, avg_time: float) -> List[str]:
        """Generar recomendaciones de optimización"""
        recommendations = []
        
        if success_rate < 0.8:
            recommendations.append("Tasa de éxito baja. Revisar condiciones y acciones del workflow.")
            
        if avg_time > 5:
            recommendations.append("Tiempo de ejecución alto. Considerar optimizar acciones o paralelizar pasos.")
            
        if success_rate > 0.95 and avg_time < 2:
            recommendations.append("Workflow funcionando excelente. Considerar replicar patrón en otros workflows.")
            
        return recommendations
    
    def suggest_workflow_improvements(self, workflow_id: str) -> Dict:
        """Sugerir mejoras para un workflow"""
        
        workflow = self.workflow_engine.workflows.get(workflow_id)
        if not workflow:
            return {'error': 'Workflow no encontrado'}
            
        suggestions = {
            'workflow_id': workflow_id,
            'current_steps': len(workflow['steps']),
            'suggestions': []
        }
        
        # Analizar pasos del workflow
        for i, step in enumerate(workflow['steps']):
            action_type = step.get('action_type')
            
            if action_type == 'wait' and step.get('wait_time', 0) > 300:
                suggestions['suggestions'].append(f"Paso {i+1}: Considerar reducir tiempo de espera o usar notificaciones asíncronas")
                
            elif action_type == 'send_notification':
                if not step.get('conditions'):
                    suggestions['suggestions'].append(f"Paso {i+1}: Agregar condiciones para evitar notificaciones innecesarias")
                    
            elif action_type == 'create_record':
                if not step.get('fields'):
                    suggestions['suggestions'].append(f"Paso {i+1}: Definir campos obligatorios para el registro")
        
        return suggestions


class AutomationManager:
    """Gestor principal de automatización"""
    
    def __init__(self):
        self.workflow_engine = IntelligentWorkflowEngine()
        self.maintenance_scheduler = SmartMaintenanceScheduler()
        self.notification_system = IntelligentNotificationSystem()
        self.ai_optimizer = AIWorkflowOptimizer()
        self.logger = logging.getLogger(__name__)
        
    def initialize_automation(self):
        """Inicializar sistema de automatización"""
        
        # Configurar workflows por defecto
        self._setup_default_automations()
        
        # Iniciar programador de mantenimiento
        self.maintenance_scheduler.start_scheduler()
        
        # Configurar reglas de notificación inteligente
        self._setup_notification_rules()
        
        self.logger.info("Sistema de automatización inteligente inicializado")
    
    def _setup_default_automations(self):
        """Configurar automatizaciones por defecto"""
        
        # Automatización de aprobación de visitas
        self.workflow_engine.add_workflow(
            'auto_visit_approval',
            steps=[
                {
                    'action_type': 'send_notification',
                    'recipients': 'resident',
                    'title': 'Solicitud de Visita Recibida',
                    'message': 'Nueva solicitud de visita de {visitor_name} para el {visit_date}',
                    'notification_type': 'visit'
                },
                {
                    'action_type': 'wait',
                    'wait_time': 3600  # Esperar 1 hora
                },
                {
                    'action_type': 'update_record',
                    'model': 'Visit',
                    'record_id': '{visit_id}',
                    'fields': {
                        'status': 'approved'
                    }
                },
                {
                    'action_type': 'send_notification',
                    'recipients': 'visitor',
                    'title': 'Visita Aprobada',
                    'message': 'Tu solicitud de visita ha sido aprobada automáticamente',
                    'notification_type': 'success'
                }
            ],
            conditions={
                'visitor_type': 'frequent',
                'visit_time': 'business_hours'
            }
        )
        
        # Automatización de alertas de seguridad
        self.workflow_engine.add_workflow(
            'security_alert_workflow',
            steps=[
                {
                    'action_type': 'create_record',
                    'model': 'SecurityReport',
                    'fields': {
                        'title': 'Alerta de Seguridad Automática',
                        'description': '{alert_description}',
                        'priority': 'high',
                        'status': 'active'
                    }
                },
                {
                    'action_type': 'send_notification',
                    'recipients': 'security_team',
                    'title': 'Alerta de Seguridad',
                    'message': 'Nueva alerta de seguridad: {alert_description}',
                    'notification_type': 'alert'
                },
                {
                    'action_type': 'send_notification',
                    'recipients': 'all_residents',
                    'title': 'Alerta de Seguridad',
                    'message': 'Se ha detectado una actividad sospechosa. Por favor, mantengan la calma y sigan las instrucciones de seguridad.',
                    'notification_type': 'alert'
                }
            ]
        )
    
    def _setup_notification_rules(self):
        """Configurar reglas de notificación inteligente"""
        
        # Regla para notificaciones de mantenimiento
        maintenance_rule = AutomationRule(
            id="maintenance_notifications",
            name="Notificaciones de Mantenimiento",
            description="Notificaciones inteligentes para eventos de mantenimiento",
            automation_type=AutomationType.MAINTENANCE_SCHEDULING,
            conditions={
                'maintenance_type': 'preventive',
                'priority': 'high'
            },
            actions=[
                {
                    'type': 'send_notification',
                    'recipients': 'affected_residents',
                    'channel': 'email',
                    'template': 'maintenance_alert'
                }
            ],
            priority=1
        )
        
        self.notification_system.add_notification_rule(maintenance_rule)
    
    def get_automation_status(self) -> Dict:
        """Obtener estado del sistema de automatización"""
        
        return {
            'workflows': {
                'total': len(self.workflow_engine.workflows),
                'active': len([w for w in self.workflow_engine.workflows.values() if w['status'] != WorkflowStatus.FAILED])
            },
            'scheduler': {
                'running': True,
                'scheduled_jobs': len(self.maintenance_scheduler.scheduler.jobs)
            },
            'notifications': {
                'rules_count': len(self.notification_system.notification_rules),
                'user_preferences_count': len(self.notification_system.user_preferences)
            },
            'ai_optimizer': {
                'available': True
            }
        }
    
    def execute_automation(self, automation_type: AutomationType, data: Dict) -> bool:
        """Ejecutar automatización específica"""
        
        try:
            if automation_type == AutomationType.MAINTENANCE_SCHEDULING:
                return self._execute_maintenance_automation(data)
            elif automation_type == AutomationType.VISIT_APPROVAL:
                return self._execute_visit_automation(data)
            elif automation_type == AutomationType.EXPENSE_ALERTS:
                return self._execute_expense_automation(data)
            elif automation_type == AutomationType.SECURITY_MONITORING:
                return self._execute_security_automation(data)
            else:
                self.logger.error(f"Tipo de automatización no soportado: {automation_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error ejecutando automatización {automation_type}: {e}")
            return False
    
    def _execute_maintenance_automation(self, data: Dict) -> bool:
        """Ejecutar automatización de mantenimiento"""
        equipment = data.get('equipment')
        frequency = data.get('frequency_days', 30)
        
        self.maintenance_scheduler.schedule_preventive_maintenance(equipment, frequency)
        return True
    
    def _execute_visit_automation(self, data: Dict) -> bool:
        """Ejecutar automatización de visitas"""
        workflow_data = {
            'visit_id': data.get('visit_id'),
            'visitor_name': data.get('visitor_name'),
            'visit_date': data.get('visit_date'),
            'visitor_type': data.get('visitor_type', 'regular'),
            'visit_time': data.get('visit_time', 'any')
        }
        
        return self.workflow_engine.execute_workflow('auto_visit_approval', workflow_data)
    
    def _execute_expense_automation(self, data: Dict) -> bool:
        """Ejecutar automatización de gastos"""
        category = data.get('category')
        amount = data.get('amount')
        
        workflow_data = {
            'category': category,
            'amount': amount
        }
        
        return self.workflow_engine.execute_workflow('expense_alert', workflow_data)
    
    def _execute_security_automation(self, data: Dict) -> bool:
        """Ejecutar automatización de seguridad"""
        alert_description = data.get('description', 'Actividad sospechosa detectada')
        
        workflow_data = {
            'alert_description': alert_description
        }
        
        return self.workflow_engine.execute_workflow('security_alert_workflow', workflow_data)


# Instancia global del gestor de automatización
automation_manager = AutomationManager()


def init_intelligent_automation(app):
    """Inicializar sistema de automatización inteligente"""
    
    try:
        # Inicializar gestor de automatización
        automation_manager.initialize_automation()
        
        # Registrar rutas de API para automatización
        @app.route('/api/v1/automation/status', methods=['GET'])
        def get_automation_status():
            """Obtener estado del sistema de automatización"""
            return {
                'status': 'success',
                'data': automation_manager.get_automation_status()
            }
        
        @app.route('/api/v1/automation/execute', methods=['POST'])
        def execute_automation():
            """Ejecutar automatización específica"""
            try:
                data = request.get_json()
                automation_type = AutomationType(data.get('type'))
                automation_data = data.get('data', {})
                
                success = automation_manager.execute_automation(automation_type, automation_data)
                
                return {
                    'status': 'success' if success else 'error',
                    'message': 'Automatización ejecutada' if success else 'Error ejecutando automatización'
                }
                
            except Exception as e:
                return {
                    'status': 'error',
                    'message': str(e)
                }, 400
        
        @app.route('/api/v1/automation/workflows/<workflow_id>/analyze', methods=['GET'])
        def analyze_workflow(workflow_id):
            """Analizar rendimiento de un workflow"""
            analysis = automation_manager.ai_optimizer.analyze_workflow_performance(workflow_id)
            return {
                'status': 'success',
                'data': analysis
            }
        
        @app.route('/api/v1/automation/workflows/<workflow_id>/suggestions', methods=['GET'])
        def get_workflow_suggestions(workflow_id):
            """Obtener sugerencias de mejora para un workflow"""
            suggestions = automation_manager.ai_optimizer.suggest_workflow_improvements(workflow_id)
            return {
                'status': 'success',
                'data': suggestions
            }
        
        @app.route('/api/v1/automation/notifications/patterns', methods=['GET'])
        def analyze_notification_patterns():
            """Analizar patrones de notificaciones"""
            recommendations = automation_manager.notification_system.analyze_notification_patterns()
            return {
                'status': 'success',
                'data': {
                    'recommendations': recommendations
                }
            }
        
        print("✅ Sistema de automatización inteligente inicializado")
        
    except Exception as e:
        print(f"⚠️ Error inicializando automatización inteligente: {e}")


# Decoradores para facilitar el uso
def automated_workflow(workflow_id: str):
    """Decorador para ejecutar workflow automáticamente"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Ejecutar workflow después de la función
            automation_manager.workflow_engine.execute_workflow(workflow_id, {
                'function_result': result,
                'executed_at': datetime.now().isoformat()
            })
            
            return result
        return wrapper
    return decorator


def smart_notification(event_type: str):
    """Decorador para enviar notificación inteligente"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Enviar notificación inteligente
            if 'user_id' in kwargs:
                automation_manager.notification_system.send_smart_notification(
                    user_id=kwargs['user_id'],
                    event_type=event_type,
                    data={'result': result}
                )
            
            return result
        return wrapper
    return decorator
