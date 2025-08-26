"""
FASE 6: ESCALABILIDAD Y DEPLOYMENT PROFESIONAL
===============================================

Sistema de escalabilidad, containerización y deployment profesional.
"""

import os
import json
# Importar docker de forma segura
from optional_dependencies import get_docker, DOCKER_AVAILABLE
docker = get_docker()
import logging
import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import requests
import psutil
import redis
from datetime import datetime
import schedule
from flask import current_app, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentType(Enum):
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    CLOUD = "cloud"

@dataclass
class DeploymentConfig:
    name: str
    type: DeploymentType
    replicas: int = 1
    cpu_limit: str = "500m"
    memory_limit: str = "512Mi"
    ports: List[int] = None
    environment: Dict = None
    
    def __post_init__(self):
        if self.ports is None:
            self.ports = [5000]
        if self.environment is None:
            self.environment = {}

class DockerManager:
    """Gestor de contenedores Docker"""
    
    def __init__(self):
        self.client = None
        self._init_client()
    
    def _init_client(self):
        try:
            self.client = docker.from_env()
            self.client.ping()
            logger.info("✅ Docker inicializado")
        except Exception as e:
            logger.error(f"❌ Error Docker: {e}")
    
    def build_image(self, dockerfile_path: str, tag: str) -> Dict:
        try:
            if not self.client:
                return {"success": False, "error": "Docker no disponible"}
            
            image, logs = self.client.images.build(
                path=".",
                dockerfile=dockerfile_path,
                tag=tag,
                rm=True
            )
            
            return {"success": True, "image_id": image.id}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_container(self, image: str, name: str, ports: Dict = None) -> Dict:
        try:
            if not self.client:
                return {"success": False, "error": "Docker no disponible"}
            
            container = self.client.containers.run(
                image=image,
                name=name,
                ports=ports or {},
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )
            
            return {
                "success": True,
                "container_id": container.id,
                "status": container.status
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

class LoadBalancer:
    """Balanceador de carga simple"""
    
    def __init__(self):
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            logger.info("✅ Redis para balanceo inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Redis no disponible: {e}")
    
    def register_server(self, server_id: str, host: str, port: int) -> Dict:
        try:
            if not self.redis_client:
                return {"success": False, "error": "Redis no disponible"}
            
            server_info = {
                "host": host,
                "port": port,
                "active": True,
                "last_check": datetime.now().isoformat()
            }
            
            self.redis_client.hset("load_balancer:servers", server_id, json.dumps(server_info))
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_next_server(self) -> Optional[Dict]:
        try:
            if not self.redis_client:
                return None
            
            servers = self.redis_client.hgetall("load_balancer:servers")
            available = []
            
            for server_id, server_data in servers.items():
                server_info = json.loads(server_data)
                if server_info.get("active", False):
                    available.append({
                        "id": server_id.decode(),
                        "host": server_info["host"],
                        "port": server_info["port"]
                    })
            
            return available[0] if available else None
        except Exception as e:
            logger.error(f"❌ Error obteniendo servidor: {e}")
            return None

class MonitoringSystem:
    """Sistema de monitoreo básico"""
    
    def __init__(self):
        self.metrics = {}
    
    def collect_metrics(self) -> Dict:
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": (disk.used / disk.total) * 100
            }
            
            self.metrics = metrics
            return metrics
        except Exception as e:
            logger.error(f"❌ Error recolectando métricas: {e}")
            return {}
    
    def check_alerts(self) -> List[Dict]:
        alerts = []
        
        if not self.metrics:
            return alerts
        
        if self.metrics["cpu_percent"] > 90:
            alerts.append({
                "level": "critical",
                "metric": "cpu",
                "value": self.metrics["cpu_percent"],
                "message": f"CPU usage critical: {self.metrics['cpu_percent']}%"
            })
        
        if self.metrics["memory_percent"] > 95:
            alerts.append({
                "level": "critical",
                "metric": "memory",
                "value": self.metrics["memory_percent"],
                "message": f"Memory usage critical: {self.metrics['memory_percent']}%"
            })
        
        return alerts

class ScalabilityManager:
    """Gestor principal de escalabilidad"""
    
    def __init__(self):
        self.docker_manager = DockerManager()
        self.load_balancer = LoadBalancer()
        self.monitoring = MonitoringSystem()
        self._init_scheduled_tasks()
    
    def _init_scheduled_tasks(self):
        try:
            schedule.every(30).seconds.do(self._monitoring_task)
            
            def run_scheduler():
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            
            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()
            
            logger.info("✅ Tareas programadas inicializadas")
        except Exception as e:
            logger.error(f"❌ Error inicializando tareas: {e}")
    
    def _monitoring_task(self):
        try:
            metrics = self.monitoring.collect_metrics()
            alerts = self.monitoring.check_alerts()
            
            for alert in alerts:
                logger.warning(f"🚨 ALERTA: {alert['message']}")
        except Exception as e:
            logger.error(f"❌ Error en monitoreo: {e}")
    
    def deploy_application(self, config: DeploymentConfig) -> Dict:
        try:
            if config.type == DeploymentType.DOCKER:
                return self._deploy_docker(config)
            else:
                return {"success": False, "error": "Tipo no soportado"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _deploy_docker(self, config: DeploymentConfig) -> Dict:
        try:
            build_result = self.docker_manager.build_image(
                dockerfile_path="Dockerfile",
                tag=f"{config.name}:latest"
            )
            
            if not build_result["success"]:
                return build_result
            
            run_result = self.docker_manager.run_container(
                image=f"{config.name}:latest",
                name=config.name,
                ports={f"{port}/tcp": port for port in config.ports}
            )
            
            if run_result["success"]:
                self.load_balancer.register_server(
                    server_id=run_result["container_id"],
                    host="localhost",
                    port=config.ports[0]
                )
            
            return run_result
        except Exception as e:
            return {"success": False, "error": str(e)}

# Instancia global
scalability_manager = ScalabilityManager()

def init_scalability_deployment(app):
    """Inicializar sistema de escalabilidad"""
    try:
        # Verificar dependencias requeridas
        if not DOCKER_AVAILABLE:
            logger.warning("⚠️ docker no disponible - sistema de escalabilidad limitado")
        
        app.scalability_manager = scalability_manager
        app.scalability_manager = scalability_manager
        
        @app.route('/api/deploy', methods=['POST'])
        def deploy_application():
            try:
                data = request.get_json()
                config = DeploymentConfig(**data)
                result = scalability_manager.deploy_application(config)
                return jsonify(result)
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 400
        
        @app.route('/api/metrics')
        def get_metrics():
            try:
                metrics = scalability_manager.monitoring.collect_metrics()
                return jsonify(metrics)
            except Exception as e:
                return jsonify({"error": str(e)}), 400
        
        logger.info("✅ Sistema de escalabilidad inicializado")
    except Exception as e:
        logger.error(f"❌ Error inicializando escalabilidad: {e}")

if __name__ == "__main__":
    print("🚀 Sistema de Escalabilidad y Deployment - Fase 6")
    print("=" * 55)
    
    manager = ScalabilityManager()
    
    config = DeploymentConfig(
        name="portalbarriosprivados",
        type=DeploymentType.DOCKER,
        replicas=1
    )
    
    result = manager.deploy_application(config)
    print(f"Deployment: {result['success']}")
    
    print("\n✅ Fase 6: Escalabilidad y Deployment completada")
