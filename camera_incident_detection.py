"""
Sistema de Detección de Incidentes en Cámaras de Seguridad
Detección en tiempo real con IA y alertas automáticas
"""

import json
import uuid
from datetime import datetime, timedelta
from flask import current_app
from models import db, SecurityReport, User, Notification

class CameraIncidentDetector:
    """Detector de incidentes usando IA en tiempo real"""
    
    def __init__(self):
        self.active_cameras = {}
        self.detection_models = {
            'person_detection': True,
            'vehicle_detection': True,
            'intrusion_detection': True,
            'violence_detection': True,
            'fire_detection': True,
            'crowd_detection': True
        }
        self.alert_thresholds = {
            'confidence_threshold': 0.75,
            'person_limit': 10,
            'vehicle_speed_limit': 30,
            'restricted_hours': {'start': 22, 'end': 6}
        }
    
    def register_camera(self, camera_id, location, camera_type='security'):
        """Registrar nueva cámara en el sistema"""
        self.active_cameras[camera_id] = {
            'id': camera_id,
            'location': location,
            'type': camera_type,
            'status': 'active',
            'last_detection': None,
            'incident_count': 0,
            'registered_at': datetime.now()
        }
        print(f"📹 Cámara {camera_id} registrada en {location}")
    
    def analyze_frame(self, camera_id, frame_data, timestamp=None):
        """Analizar frame de cámara en busca de incidentes"""
        if timestamp is None:
            timestamp = datetime.now()
        
        camera = self.active_cameras.get(camera_id)
        if not camera:
            return {'error': 'Cámara no registrada'}
        
        # Simular análisis de IA (en producción aquí iría el modelo real)
        detection_results = self._simulate_ai_detection(frame_data, camera_id, timestamp)
        
        # Procesar resultados y generar alertas si es necesario
        if detection_results['incidents_detected']:
            self._handle_incidents(camera_id, detection_results, timestamp)
        
        # Actualizar estadísticas de cámara
        camera['last_detection'] = timestamp
        
        return detection_results
    
    def _simulate_ai_detection(self, frame_data, camera_id, timestamp):
        """Simular detección de IA (reemplazar con modelo real)"""
        import random
        
        # Simular diferentes tipos de detecciones
        detections = []
        incidents_detected = []
        
        # Detección de personas
        person_count = random.randint(0, 15)
        if person_count > 0:
            detections.append({
                'type': 'person',
                'count': person_count,
                'confidence': random.uniform(0.6, 0.98),
                'bounding_boxes': self._generate_bounding_boxes(person_count)
            })
            
            # Verificar si hay incidentes
            if person_count > self.alert_thresholds['person_limit']:
                incidents_detected.append({
                    'type': 'crowd_detected',
                    'severity': 'medium',
                    'description': f'Multitud detectada: {person_count} personas',
                    'confidence': detections[-1]['confidence']
                })
        
        # Detección de vehículos
        if random.random() < 0.3:  # 30% probabilidad de vehículo
            vehicle_count = random.randint(1, 5)
            speed = random.uniform(10, 50)
            detections.append({
                'type': 'vehicle',
                'count': vehicle_count,
                'speed': speed,
                'confidence': random.uniform(0.7, 0.95)
            })
            
            if speed > self.alert_thresholds['vehicle_speed_limit']:
                incidents_detected.append({
                    'type': 'speeding_vehicle',
                    'severity': 'high',
                    'description': f'Vehículo a alta velocidad: {speed:.1f} km/h',
                    'confidence': detections[-1]['confidence']
                })
        
        # Detección de intrusión (horarios restringidos)
        current_hour = timestamp.hour
        restricted_hours = self.alert_thresholds['restricted_hours']
        
        if (current_hour >= restricted_hours['start'] or 
            current_hour <= restricted_hours['end']) and person_count > 0:
            incidents_detected.append({
                'type': 'after_hours_intrusion',
                'severity': 'critical',
                'description': f'Intrusión fuera de horario: {person_count} personas a las {timestamp.strftime("%H:%M")}',
                'confidence': 0.85
            })
        
        # Detección de actividad sospechosa (simulada)
        if random.random() < 0.05:  # 5% probabilidad
            incidents_detected.append({
                'type': 'suspicious_activity',
                'severity': 'high',
                'description': 'Comportamiento sospechoso detectado por IA',
                'confidence': random.uniform(0.75, 0.90)
            })
        
        # Detección de incendio (muy baja probabilidad)
        if random.random() < 0.01:  # 1% probabilidad
            incidents_detected.append({
                'type': 'fire_detected',
                'severity': 'critical',
                'description': 'Posible incendio detectado - Verificar inmediatamente',
                'confidence': random.uniform(0.80, 0.95)
            })
        
        return {
            'camera_id': camera_id,
            'timestamp': timestamp.isoformat(),
            'detections': detections,
            'incidents_detected': incidents_detected,
            'total_incidents': len(incidents_detected),
            'frame_analyzed': True
        }
    
    def _generate_bounding_boxes(self, count):
        """Generar bounding boxes simuladas"""
        import random
        boxes = []
        for _ in range(count):
            boxes.append({
                'x': random.randint(0, 1920),
                'y': random.randint(0, 1080),
                'width': random.randint(50, 200),
                'height': random.randint(100, 300),
                'confidence': random.uniform(0.6, 0.98)
            })
        return boxes
    
    def _handle_incidents(self, camera_id, detection_results, timestamp):
        """Manejar incidentes detectados"""
        camera = self.active_cameras[camera_id]
        
        for incident in detection_results['incidents_detected']:
            # Crear reporte de seguridad automático
            self._create_security_report(camera_id, incident, timestamp)
            
            # Incrementar contador de incidentes
            camera['incident_count'] += 1
            
            print(f"🚨 INCIDENTE DETECTADO - Cámara {camera_id}: {incident['description']}")
    
    def _create_security_report(self, camera_id, incident, timestamp):
        """Crear reporte de seguridad automático"""
        try:
            camera = self.active_cameras[camera_id]
            
            report = SecurityReport(
                user_id=None,  # Reporte automático del sistema
                reporter_name='Sistema de IA - Cámaras',
                reporter_email='security@sistema.com',
                title=f"🤖 ALERTA AUTOMÁTICA: {incident['type'].replace('_', ' ').title()}",
                incident_type='automatic_detection',
                description=f"""DETECCIÓN AUTOMÁTICA POR IA
                
📹 Cámara: {camera_id}
📍 Ubicación: {camera['location']}
🤖 Tipo: {incident['type']}
⚠️ Severidad: {incident['severity'].upper()}
🎯 Confianza: {incident['confidence']:.2%}
📅 Detectado: {timestamp.strftime('%d/%m/%Y %H:%M:%S')}

📋 Descripción:
{incident['description']}

🔍 ACCIÓN REQUERIDA:
- Verificar cámaras inmediatamente
- Evaluar necesidad de respuesta de seguridad
- Confirmar o descartar alerta

⚡ Este reporte fue generado automáticamente por el sistema de IA.""",
                location=camera['location'],
                severity='critical' if incident['severity'] == 'critical' else 'high',
                status='investigating',
                incident_date=timestamp.date(),
                incident_time=timestamp.time()
            )
            
            db.session.add(report)
            db.session.commit()
            
            return report.id
        except Exception as e:
            print(f"❌ Error creando reporte: {e}")
            return None
    
    def get_camera_status(self, camera_id=None):
        """Obtener estado de cámaras"""
        if camera_id:
            return self.active_cameras.get(camera_id, {'error': 'Cámara no encontrada'})
        
        return {
            'total_cameras': len(self.active_cameras),
            'cameras': list(self.active_cameras.values()),
            'total_incidents': sum(cam['incident_count'] for cam in self.active_cameras.values())
        }
    
    def get_incidents_summary(self, hours=24):
        """Obtener resumen de incidentes recientes"""
        since = datetime.now() - timedelta(hours=hours)
        
        try:
            # En producción, consultar base de datos real
            recent_reports = SecurityReport.query.filter(
                SecurityReport.created_at >= since,
                SecurityReport.title.like('%ALERTA AUTOMÁTICA%')
            ).all()
        except:
            recent_reports = []
        
        summary = {
            'total_incidents': len(recent_reports),
            'by_severity': {},
            'by_type': {},
            'recent_incidents': []
        }
        
        for report in recent_reports:
            # Contar por severidad
            severity = report.severity
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
            # Contar por tipo
            incident_type = report.incident_type
            summary['by_type'][incident_type] = summary['by_type'].get(incident_type, 0) + 1
            
            # Agregar a recientes
            summary['recent_incidents'].append({
                'id': report.id,
                'title': report.title,
                'severity': report.severity,
                'location': report.location,
                'created_at': report.created_at.isoformat(),
                'confidence': 0.85  # Simulated confidence
            })
        
        return summary

# Instancia global del detector
camera_detector = CameraIncidentDetector()

# Configuración inicial de cámaras
def initialize_camera_system():
    """Inicializar sistema de cámaras"""
    cameras_config = [
        {'id': 'CAM_001', 'location': 'Entrada Principal'},
        {'id': 'CAM_002', 'location': 'Portón Vehículos'},
        {'id': 'CAM_003', 'location': 'Plaza Central'},
        {'id': 'CAM_004', 'location': 'Club House'},
        {'id': 'CAM_005', 'location': 'Sector Infantil'},
        {'id': 'CAM_006', 'location': 'Estacionamiento'},
        {'id': 'CAM_007', 'location': 'Perímetro Norte'},
        {'id': 'CAM_008', 'location': 'Perímetro Sur'},
    ]
    
    for cam in cameras_config:
        camera_detector.register_camera(cam['id'], cam['location'])
    
    print(f"🔧 Sistema de cámaras inicializado: {len(cameras_config)} cámaras activas")

# Funciones de utilidad
def get_live_camera_status():
    """Obtener estado actual de todas las cámaras"""
    return camera_detector.get_camera_status()

def get_recent_incidents(hours=24):
    """Obtener incidentes recientes"""
    return camera_detector.get_incidents_summary(hours)

def start_demo_detection(camera_id='CAM_001'):
    """Iniciar demostración de detección"""
    print(f"🎬 Demo de detección iniciada para cámara {camera_id}")
    
    # Simular algunas detecciones
    import time
    import threading
    
    def demo_loop():
        for i in range(3):
            frame_data = f"demo_frame_{i}"
            result = camera_detector.analyze_frame(camera_id, frame_data)
            print(f"Demo {i+1}: {result.get('total_incidents', 0)} incidentes detectados")
            time.sleep(2)
    
    thread = threading.Thread(target=demo_loop)
    thread.daemon = True
    thread.start()
