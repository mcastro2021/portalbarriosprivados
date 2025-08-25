"""
Sistema de monitoreo y métricas
Proporciona recolección de métricas, monitoreo de salud y alertas
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
from flask import request, g, current_app
from flask_login import current_user
import json
import os
from functools import wraps

class MetricsCollector:
    """Recolector de métricas del sistema"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.Lock()
        self.start_time = datetime.utcnow()
    
    def increment_counter(self, name, value=1, tags=None):
        """Incrementar contador"""
        with self.lock:
            key = self._build_key(name, tags)
            self.counters[key] += value
    
    def set_gauge(self, name, value, tags=None):
        """Establecer valor de gauge"""
        with self.lock:
            key = self._build_key(name, tags)
            self.gauges[key] = value
    
    def record_histogram(self, name, value, tags=None):
        """Registrar valor en histograma"""
        with self.lock:
            key = self._build_key(name, tags)
            self.histograms[key].append({
                'value': value,
                'timestamp': datetime.utcnow()
            })
    
    def record_timing(self, name, duration_ms, tags=None):
        """Registrar tiempo de ejecución"""
        self.record_histogram(f"{name}.duration", duration_ms, tags)
    
    def _build_key(self, name, tags):
        """Construir clave única para métrica"""
        if tags:
            tag_str = ','.join([f"{k}={v}" for k, v in sorted(tags.items())])
            return f"{name}[{tag_str}]"
        return name
    
    def get_metrics_summary(self):
        """Obtener resumen de métricas"""
        with self.lock:
            summary = {
                'timestamp': datetime.utcnow().isoformat(),
                'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds(),
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {}
            }
            
            # Procesar histogramas
            for key, values in self.histograms.items():
                if values:
                    recent_values = [v['value'] for v in values if 
                                   (datetime.utcnow() - v['timestamp']).total_seconds() < 300]  # Últimos 5 minutos
                    
                    if recent_values:
                        summary['histograms'][key] = {
                            'count': len(recent_values),
                            'min': min(recent_values),
                            'max': max(recent_values),
                            'avg': sum(recent_values) / len(recent_values),
                            'p50': self._percentile(recent_values, 50),
                            'p95': self._percentile(recent_values, 95),
                            'p99': self._percentile(recent_values, 99)
                        }
            
            return summary
    
    def _percentile(self, values, percentile):
        """Calcular percentil"""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]

class HealthChecker:
    """Verificador de salud del sistema"""
    
    def __init__(self):
        self.checks = {}
        self.last_check_time = None
        self.check_interval = 60  # segundos
    
    def register_check(self, name, check_function, critical=False):
        """Registrar verificación de salud"""
        self.checks[name] = {
            'function': check_function,
            'critical': critical,
            'last_result': None,
            'last_check': None
        }
    
    def run_checks(self):
        """Ejecutar todas las verificaciones"""
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        for name, check_config in self.checks.items():
            try:
                start_time = time.time()
                result = check_config['function']()
                duration = (time.time() - start_time) * 1000  # ms
                
                check_result = {
                    'status': 'healthy' if result.get('healthy', True) else 'unhealthy',
                    'message': result.get('message', 'OK'),
                    'duration_ms': duration,
                    'details': result.get('details', {}),
                    'critical': check_config['critical']
                }
                
                # Actualizar estado general
                if not result.get('healthy', True):
                    if check_config['critical']:
                        results['overall_status'] = 'critical'
                    elif results['overall_status'] == 'healthy':
                        results['overall_status'] = 'degraded'
                
                check_config['last_result'] = check_result
                check_config['last_check'] = datetime.utcnow()
                
            except Exception as e:
                check_result = {
                    'status': 'error',
                    'message': f'Check failed: {str(e)}',
                    'duration_ms': 0,
                    'details': {'error': str(e)},
                    'critical': check_config['critical']
                }
                
                if check_config['critical']:
                    results['overall_status'] = 'critical'
                elif results['overall_status'] == 'healthy':
                    results['overall_status'] = 'degraded'
            
            results['checks'][name] = check_result
        
        self.last_check_time = datetime.utcnow()
        return results

class MonitoringService:
    """Servicio principal de monitoreo"""
    
    def __init__(self, app=None):
        self.app = app
        self.metrics = MetricsCollector()
        self.health_checker = HealthChecker()
        self.alerts = []
        self.alert_thresholds = {}
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar servicio de monitoreo"""
        self.app = app
        
        # Configurar verificaciones de salud por defecto
        self._setup_default_health_checks()
        
        # Configurar middleware de métricas
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        # Configurar umbrales de alerta por defecto
        self._setup_default_alert_thresholds()
        
        # Iniciar hilo de monitoreo en background
        self._start_background_monitoring()
        
        print("✅ Sistema de monitoreo inicializado")
    
    def _setup_default_health_checks(self):
        """Configurar verificaciones de salud por defecto"""
        
        def check_database():
            """Verificar conexión a base de datos"""
            try:
                from models import db
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
                return {'healthy': True, 'message': 'Database connection OK'}
            except Exception as e:
                return {'healthy': False, 'message': f'Database error: {str(e)}'}
        
        def check_disk_space():
            """Verificar espacio en disco"""
            try:
                disk_usage = psutil.disk_usage('/')
                free_percent = (disk_usage.free / disk_usage.total) * 100
                
                if free_percent < 10:
                    return {'healthy': False, 'message': f'Low disk space: {free_percent:.1f}% free'}
                elif free_percent < 20:
                    return {'healthy': True, 'message': f'Disk space warning: {free_percent:.1f}% free'}
                else:
                    return {'healthy': True, 'message': f'Disk space OK: {free_percent:.1f}% free'}
            except Exception as e:
                return {'healthy': False, 'message': f'Disk check error: {str(e)}'}
        
        def check_memory():
            """Verificar uso de memoria"""
            try:
                memory = psutil.virtual_memory()
                if memory.percent > 90:
                    return {'healthy': False, 'message': f'High memory usage: {memory.percent:.1f}%'}
                elif memory.percent > 80:
                    return {'healthy': True, 'message': f'Memory usage warning: {memory.percent:.1f}%'}
                else:
                    return {'healthy': True, 'message': f'Memory usage OK: {memory.percent:.1f}%'}
            except Exception as e:
                return {'healthy': False, 'message': f'Memory check error: {str(e)}'}
        
        def check_cpu():
            """Verificar uso de CPU"""
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                if cpu_percent > 90:
                    return {'healthy': False, 'message': f'High CPU usage: {cpu_percent:.1f}%'}
                elif cpu_percent > 80:
                    return {'healthy': True, 'message': f'CPU usage warning: {cpu_percent:.1f}%'}
                else:
                    return {'healthy': True, 'message': f'CPU usage OK: {cpu_percent:.1f}%'}
            except Exception as e:
                return {'healthy': False, 'message': f'CPU check error: {str(e)}'}
        
        # Registrar verificaciones
        self.health_checker.register_check('database', check_database, critical=True)
        self.health_checker.register_check('disk_space', check_disk_space, critical=True)
        self.health_checker.register_check('memory', check_memory, critical=False)
        self.health_checker.register_check('cpu', check_cpu, critical=False)
    
    def _setup_default_alert_thresholds(self):
        """Configurar umbrales de alerta por defecto"""
        self.alert_thresholds = {
            'response_time_p95': 2000,  # ms
            'error_rate': 5,  # %
            'memory_usage': 85,  # %
            'cpu_usage': 85,  # %
            'disk_usage': 85,  # %
        }
    
    def _start_background_monitoring(self):
        """Iniciar monitoreo en background"""
        def monitor():
            while True:
                try:
                    # Recolectar métricas del sistema
                    self._collect_system_metrics()
                    
                    # Verificar umbrales de alerta
                    self._check_alert_thresholds()
                    
                    time.sleep(60)  # Ejecutar cada minuto
                except Exception as e:
                    current_app.logger.error(f"Error in background monitoring: {str(e)}")
                    time.sleep(60)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def _collect_system_metrics(self):
        """Recolectar métricas del sistema"""
        try:
            # Métricas de CPU
            cpu_percent = psutil.cpu_percent()
            self.metrics.set_gauge('system.cpu.usage_percent', cpu_percent)
            
            # Métricas de memoria
            memory = psutil.virtual_memory()
            self.metrics.set_gauge('system.memory.usage_percent', memory.percent)
            self.metrics.set_gauge('system.memory.available_bytes', memory.available)
            
            # Métricas de disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.metrics.set_gauge('system.disk.usage_percent', disk_percent)
            self.metrics.set_gauge('system.disk.free_bytes', disk.free)
            
            # Métricas de red (si están disponibles)
            try:
                net_io = psutil.net_io_counters()
                self.metrics.set_gauge('system.network.bytes_sent', net_io.bytes_sent)
                self.metrics.set_gauge('system.network.bytes_recv', net_io.bytes_recv)
            except:
                pass
            
        except Exception as e:
            current_app.logger.error(f"Error collecting system metrics: {str(e)}")
    
    def _check_alert_thresholds(self):
        """Verificar umbrales de alerta"""
        try:
            metrics_summary = self.metrics.get_metrics_summary()
            
            # Verificar tiempo de respuesta
            if 'http.request.duration' in metrics_summary['histograms']:
                p95 = metrics_summary['histograms']['http.request.duration']['p95']
                if p95 > self.alert_thresholds['response_time_p95']:
                    self._create_alert('high_response_time', f'P95 response time: {p95:.0f}ms', 'warning')
            
            # Verificar uso de memoria
            memory_usage = metrics_summary['gauges'].get('system.memory.usage_percent', 0)
            if memory_usage > self.alert_thresholds['memory_usage']:
                self._create_alert('high_memory_usage', f'Memory usage: {memory_usage:.1f}%', 'warning')
            
            # Verificar uso de CPU
            cpu_usage = metrics_summary['gauges'].get('system.cpu.usage_percent', 0)
            if cpu_usage > self.alert_thresholds['cpu_usage']:
                self._create_alert('high_cpu_usage', f'CPU usage: {cpu_usage:.1f}%', 'warning')
            
        except Exception as e:
            current_app.logger.error(f"Error checking alert thresholds: {str(e)}")
    
    def _create_alert(self, alert_type, message, severity='info'):
        """Crear alerta"""
        alert = {
            'id': len(self.alerts) + 1,
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            'resolved': False
        }
        
        self.alerts.append(alert)
        
        # Mantener solo las últimas 100 alertas
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # Log de la alerta
        current_app.logger.warning(f"Alert created: {alert_type} - {message}")
    
    def _before_request(self):
        """Middleware antes de request"""
        g.start_time = time.time()
        
        # Incrementar contador de requests
        self.metrics.increment_counter('http.requests.total', tags={
            'method': request.method,
            'endpoint': request.endpoint or 'unknown'
        })
    
    def _after_request(self, response):
        """Middleware después de request"""
        if hasattr(g, 'start_time'):
            duration_ms = (time.time() - g.start_time) * 1000
            
            # Registrar tiempo de respuesta
            self.metrics.record_timing('http.request', duration_ms, tags={
                'method': request.method,
                'status_code': response.status_code,
                'endpoint': request.endpoint or 'unknown'
            })
            
            # Incrementar contador de respuestas
            self.metrics.increment_counter('http.responses.total', tags={
                'method': request.method,
                'status_code': response.status_code,
                'endpoint': request.endpoint or 'unknown'
            })
            
            # Incrementar contador de errores si es necesario
            if response.status_code >= 400:
                self.metrics.increment_counter('http.errors.total', tags={
                    'method': request.method,
                    'status_code': response.status_code,
                    'endpoint': request.endpoint or 'unknown'
                })
        
        return response
    
    def get_health_status(self):
        """Obtener estado de salud"""
        return self.health_checker.run_checks()
    
    def get_metrics(self):
        """Obtener métricas"""
        return self.metrics.get_metrics_summary()
    
    def get_alerts(self, limit=50):
        """Obtener alertas recientes"""
        return self.alerts[-limit:] if self.alerts else []
    
    def resolve_alert(self, alert_id):
        """Resolver alerta"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['resolved'] = True
                alert['resolved_at'] = datetime.utcnow().isoformat()
                return True
        return False
    
    def add_custom_metric(self, name, value, metric_type='gauge', tags=None):
        """Agregar métrica personalizada"""
        if metric_type == 'counter':
            self.metrics.increment_counter(name, value, tags)
        elif metric_type == 'gauge':
            self.metrics.set_gauge(name, value, tags)
        elif metric_type == 'histogram':
            self.metrics.record_histogram(name, value, tags)
    
    def register_health_check(self, name, check_function, critical=False):
        """Registrar verificación de salud personalizada"""
        self.health_checker.register_check(name, check_function, critical)

# Decoradores para métricas
def monitor_performance(metric_name=None):
    """Decorador para monitorear rendimiento de funciones"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            name = metric_name or f"{f.__module__}.{f.__name__}"
            
            try:
                result = f(*args, **kwargs)
                
                # Registrar éxito
                duration_ms = (time.time() - start_time) * 1000
                monitoring_service.metrics.record_timing(name, duration_ms, tags={'status': 'success'})
                monitoring_service.metrics.increment_counter(f"{name}.calls", tags={'status': 'success'})
                
                return result
                
            except Exception as e:
                # Registrar error
                duration_ms = (time.time() - start_time) * 1000
                monitoring_service.metrics.record_timing(name, duration_ms, tags={'status': 'error'})
                monitoring_service.metrics.increment_counter(f"{name}.calls", tags={'status': 'error'})
                monitoring_service.metrics.increment_counter(f"{name}.errors")
                
                raise
        
        return decorated_function
    return decorator

def count_calls(metric_name=None):
    """Decorador para contar llamadas a funciones"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            name = metric_name or f"{f.__module__}.{f.__name__}.calls"
            monitoring_service.metrics.increment_counter(name)
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Instancia global del servicio de monitoreo
monitoring_service = MonitoringService()
