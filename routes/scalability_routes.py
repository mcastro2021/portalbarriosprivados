"""
Rutas para escalabilidad y deployment - Fase 6
==============================================

APIs para gestión de contenedores, balanceo de carga y monitoreo.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from scalability_deployment import (
    scalability_manager, DeploymentConfig, DeploymentType
)
from optional_dependencies import DOCKER_AVAILABLE
import json
from datetime import datetime

scalability_bp = Blueprint('scalability', __name__, url_prefix='/scalability')

@scalability_bp.route('/deploy', methods=['POST'])
@login_required
def deploy_application():
    """Desplegar aplicación"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['name', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Campo requerido: {field}"}), 400
        
        # Crear configuración de deployment
        config = DeploymentConfig(
            name=data['name'],
            type=DeploymentType(data['type']),
            replicas=data.get('replicas', 1),
            cpu_limit=data.get('cpu_limit', '500m'),
            memory_limit=data.get('memory_limit', '512Mi'),
            ports=data.get('ports', [5000]),
            environment=data.get('environment', {})
        )
        
        # Desplegar aplicación
        result = scalability_manager.deploy_application(config)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@scalability_bp.route('/containers/list')
@login_required
def list_containers():
    """Listar contenedores"""
    try:
        if not DOCKER_AVAILABLE or not scalability_manager.docker_manager.client:
            return jsonify({"success": False, "error": "Docker no disponible"}), 503
        
        containers = scalability_manager.docker_manager.client.containers.list()
        
        container_list = []
        for container in containers:
            container_list.append({
                "id": container.id,
                "name": container.name,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else container.image.id,
                "ports": container.ports,
                "created": container.attrs['Created']
            })
        
        return jsonify({
            "success": True,
            "containers": container_list
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@scalability_bp.route('/containers/<container_id>/stop', methods=['POST'])
@login_required
def stop_container(container_id):
    """Detener contenedor"""
    try:
        if not DOCKER_AVAILABLE or not scalability_manager.docker_manager.client:
            return jsonify({"success": False, "error": "Docker no disponible"}), 503
        
        container = scalability_manager.docker_manager.client.containers.get(container_id)
        container.stop()
        
        return jsonify({"success": True, "message": "Contenedor detenido"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@scalability_bp.route('/containers/<container_id>/start', methods=['POST'])
@login_required
def start_container(container_id):
    """Iniciar contenedor"""
    try:
        if not scalability_manager.docker_manager.client:
            return jsonify({"success": False, "error": "Docker no disponible"}), 503
        
        container = scalability_manager.docker_manager.client.containers.get(container_id)
        container.start()
        
        return jsonify({"success": True, "message": "Contenedor iniciado"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@scalability_bp.route('/containers/<container_id>/stats')
@login_required
def get_container_stats(container_id):
    """Obtener estadísticas del contenedor"""
    try:
        if not scalability_manager.docker_manager.client:
            return jsonify({"success": False, "error": "Docker no disponible"}), 503
        
        container = scalability_manager.docker_manager.client.containers.get(container_id)
        stats = container.stats(stream=False)
        
        # Calcular uso de CPU
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                   stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                      stats['precpu_stats']['system_cpu_usage']
        cpu_usage = (cpu_delta / system_delta) * 100 if system_delta > 0 else 0
        
        # Calcular uso de memoria
        memory_usage = stats['memory_stats']['usage'] / stats['memory_stats']['limit'] * 100
        
        return jsonify({
            "success": True,
            "stats": {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "network_rx": stats['networks']['eth0']['rx_bytes'],
                "network_tx": stats['networks']['eth0']['tx_bytes']
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@scalability_bp.route('/load-balancer/servers')
@login_required
def get_load_balancer_servers():
    """Obtener servidores del balanceador de carga"""
    try:
        if not scalability_manager.load_balancer.redis_client:
            return jsonify({"success": False, "error": "Redis no disponible"}), 503
        
        servers = scalability_manager.load_balancer.redis_client.hgetall("load_balancer:servers")
        
        server_list = []
        for server_id, server_data in servers.items():
            server_info = json.loads(server_data)
            server_list.append({
                "id": server_id.decode(),
                "host": server_info["host"],
                "port": server_info["port"],
                "active": server_info["active"],
                "last_check": server_info["last_check"]
            })
        
        return jsonify({
            "success": True,
            "servers": server_list
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@scalability_bp.route('/load-balancer/register', methods=['POST'])
@login_required
def register_server():
    """Registrar servidor en el balanceador"""
    try:
        data = request.get_json()
        
        server_id = data.get('server_id')
        host = data.get('host')
        port = data.get('port')
        
        if not all([server_id, host, port]):
            return jsonify({"success": False, "error": "server_id, host y port requeridos"}), 400
        
        result = scalability_manager.load_balancer.register_server(
            server_id=server_id,
            host=host,
            port=port
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@scalability_bp.route('/load-balancer/next-server')
@login_required
def get_next_server():
    """Obtener siguiente servidor disponible"""
    try:
        server = scalability_manager.load_balancer.get_next_server()
        
        if server:
            return jsonify({
                "success": True,
                "server": server
            })
        else:
            return jsonify({"success": False, "error": "No hay servidores disponibles"}), 404
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@scalability_bp.route('/monitoring/metrics')
@login_required
def get_system_metrics():
    """Obtener métricas del sistema"""
    try:
        metrics = scalability_manager.monitoring.collect_metrics()
        
        return jsonify({
            "success": True,
            "metrics": metrics
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@scalability_bp.route('/monitoring/alerts')
@login_required
def get_system_alerts():
    """Obtener alertas del sistema"""
    try:
        alerts = scalability_manager.monitoring.check_alerts()
        
        return jsonify({
            "success": True,
            "alerts": alerts
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@scalability_bp.route('/health')
def health_check():
    """Health check del sistema de escalabilidad"""
    try:
        health_status = {
            "docker": scalability_manager.docker_manager.client is not None,
            "redis": scalability_manager.load_balancer.redis_client is not None,
            "monitoring": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Verificar conectividad
        if health_status["docker"]:
            try:
                scalability_manager.docker_manager.client.ping()
                health_status["docker_connected"] = True
            except:
                health_status["docker_connected"] = False
        
        if health_status["redis"]:
            try:
                scalability_manager.load_balancer.redis_client.ping()
                health_status["redis_connected"] = True
            except:
                health_status["redis_connected"] = False
        
        return jsonify({
            "success": True,
            "health": health_status
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@scalability_bp.route('/dashboard')
@login_required
def get_dashboard():
    """Obtener dashboard de escalabilidad"""
    try:
        # Métricas del sistema
        metrics = scalability_manager.monitoring.collect_metrics()
        
        # Contenedores
        containers = []
        if scalability_manager.docker_manager.client:
            try:
                containers = scalability_manager.docker_manager.client.containers.list()
                containers = [{
                    "id": c.id,
                    "name": c.name,
                    "status": c.status,
                    "image": c.image.tags[0] if c.image.tags else c.image.id
                } for c in containers]
            except:
                pass
        
        # Servidores del balanceador
        servers = []
        if scalability_manager.load_balancer.redis_client:
            try:
                redis_servers = scalability_manager.load_balancer.redis_client.hgetall("load_balancer:servers")
                for server_id, server_data in redis_servers.items():
                    server_info = json.loads(server_data)
                    servers.append({
                        "id": server_id.decode(),
                        "host": server_info["host"],
                        "port": server_info["port"],
                        "active": server_info["active"]
                    })
            except:
                pass
        
        # Alertas
        alerts = scalability_manager.monitoring.check_alerts()
        
        return jsonify({
            "success": True,
            "dashboard": {
                "metrics": metrics,
                "containers": containers,
                "servers": servers,
                "alerts": alerts
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def init_scalability_routes(app):
    """Inicializar rutas de escalabilidad"""
    app.register_blueprint(scalability_bp)
    print("✅ Rutas de escalabilidad registradas correctamente")
