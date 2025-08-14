"""
Rutas para el sistema de detección de incidentes en cámaras
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, SecurityReport, User
from camera_incident_detection import camera_detector, initialize_camera_system, get_live_camera_status, get_recent_incidents, start_demo_detection
from datetime import datetime, timedelta
import json

bp = Blueprint('camera_security', __name__, url_prefix='/admin/camera-security')

@bp.route('/')
@login_required
def index():
    """Panel principal del sistema de cámaras"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener estado de cámaras
    camera_status = get_live_camera_status()
    
    # Obtener incidentes recientes
    recent_incidents = get_recent_incidents(24)
    
    # Estadísticas de seguridad
    total_reports = SecurityReport.query.filter(
        SecurityReport.created_at >= datetime.now() - timedelta(days=7)
    ).count()
    
    ai_reports = SecurityReport.query.filter(
        SecurityReport.title.like('%ALERTA AUTOMÁTICA%'),
        SecurityReport.created_at >= datetime.now() - timedelta(days=7)
    ).count()
    
    critical_incidents = SecurityReport.query.filter(
        SecurityReport.severity == 'critical',
        SecurityReport.created_at >= datetime.now() - timedelta(hours=24)
    ).count()
    
    stats = {
        'total_cameras': camera_status.get('total_cameras', 0),
        'total_incidents': recent_incidents.get('total_incidents', 0),
        'total_reports': total_reports,
        'ai_reports': ai_reports,
        'critical_incidents': critical_incidents,
        'detection_rate': (ai_reports / total_reports * 100) if total_reports > 0 else 0
    }
    
    return render_template('camera_security/index.html', 
                         camera_status=camera_status,
                         recent_incidents=recent_incidents,
                         stats=stats)

@bp.route('/cameras/status')
@login_required
def cameras_status():
    """API para obtener estado de cámaras en tiempo real"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        status = get_live_camera_status()
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/incidents/recent')
@login_required
def recent_incidents():
    """API para obtener incidentes recientes"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        hours = request.args.get('hours', 24, type=int)
        incidents = get_recent_incidents(hours)
        
        return jsonify({
            'success': True,
            'data': incidents,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/cameras/initialize', methods=['POST'])
@login_required
def initialize_cameras():
    """Inicializar sistema de cámaras"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        initialize_camera_system()
        
        return jsonify({
            'success': True,
            'message': 'Sistema de cámaras inicializado correctamente'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/detection/start-demo', methods=['POST'])
@login_required
def start_detection_demo():
    """Iniciar demostración de detección"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        data = request.get_json()
        camera_id = data.get('camera_id', 'CAM_001')
        
        start_demo_detection(camera_id)
        
        return jsonify({
            'success': True,
            'message': f'Demostración iniciada para cámara {camera_id}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/camera/<camera_id>/analyze', methods=['POST'])
@login_required
def analyze_camera_frame():
    """Analizar frame específico de cámara"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        camera_id = request.view_args['camera_id']
        
        # Simular análisis de frame
        frame_data = f"manual_frame_{datetime.now().timestamp()}"
        result = camera_detector.analyze_frame(camera_id, frame_data)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Configuración del sistema de detección"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Actualizar configuración del detector
            if 'confidence_threshold' in data:
                camera_detector.alert_thresholds['confidence_threshold'] = float(data['confidence_threshold'])
            
            if 'person_limit' in data:
                camera_detector.alert_thresholds['person_limit'] = int(data['person_limit'])
            
            if 'vehicle_speed_limit' in data:
                camera_detector.alert_thresholds['vehicle_speed_limit'] = float(data['vehicle_speed_limit'])
            
            return jsonify({
                'success': True,
                'message': 'Configuración actualizada correctamente'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # GET - mostrar configuración actual
    current_settings = {
        'alert_thresholds': camera_detector.alert_thresholds,
        'detection_models': camera_detector.detection_models
    }
    
    return render_template('camera_security/settings.html', settings=current_settings)
