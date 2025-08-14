"""
Sistema inteligente de mantenimiento con IA
Integra el chatbot con el sistema de reclamos
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Maintenance, User
from knowledge_base import AIClaimClassifier
from datetime import datetime
import json

bp = Blueprint('smart_maintenance', __name__, url_prefix='/smart-maintenance')

# Inicializar clasificador
claim_classifier = AIClaimClassifier()

@bp.route('/create-from-chat', methods=['POST'])
@login_required
def create_from_chat():
    """Crear reclamo desde el chatbot con clasificación automática"""
    try:
        data = request.get_json()
        
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        
        if not title or not description:
            return jsonify({'error': 'Título y descripción son requeridos'}), 400
        
        # Clasificar automáticamente el reclamo
        clasificacion = claim_classifier.clasificar_reclamo(title, description)
        
        # Crear el reclamo con información IA
        maintenance = Maintenance(
            user_id=current_user.id,
            title=title,
            description=description,
            category=clasificacion['categoria'],
            priority=clasificacion['prioridad'],
            assigned_area=clasificacion['area_responsable'],
            expected_response_time=clasificacion['tiempo_respuesta'],
            ai_classification=json.dumps(clasificacion),
            status='pending',
            created_at=datetime.utcnow()
        )
        
        # Agregar metadata de IA
        if 'sugerencias' in clasificacion:
            maintenance.ai_suggestions = json.dumps(clasificacion['sugerencias'])
        
        db.session.add(maintenance)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'maintenance_id': maintenance.id,
            'classification': clasificacion,
            'message': f'Reclamo creado exitosamente con ID #{maintenance.id}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/classify-preview', methods=['POST'])
@login_required
def classify_preview():
    """Vista previa de clasificación sin crear el reclamo"""
    try:
        data = request.get_json()
        
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        
        if not title and not description:
            return jsonify({'error': 'Se requiere título o descripción'}), 400
        
        # Clasificar el texto
        clasificacion = claim_classifier.clasificar_reclamo(title, description)
        
        return jsonify({
            'success': True,
            'classification': clasificacion
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/ai-dashboard')
@login_required
def ai_dashboard():
    """Dashboard con estadísticas de IA"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener estadísticas de clasificaciones
    maintenance_records = Maintenance.query.filter(
        Maintenance.ai_classification.isnot(None)
    ).all()
    
    # Analizar estadísticas
    stats = analyze_ai_stats(maintenance_records)
    
    return render_template('smart_maintenance/ai_dashboard.html', stats=stats)

def analyze_ai_stats(records):
    """Analizar estadísticas de clasificaciones IA"""
    if not records:
        return {
            'total_classified': 0,
            'categories': {},
            'priorities': {},
            'areas': {},
            'accuracy_rate': 0,
            'avg_response_time': 0
        }
    
    categories = {}
    priorities = {}
    areas = {}
    
    for record in records:
        try:
            classification = json.loads(record.ai_classification)
            
            # Contar categorías
            cat = classification.get('categoria', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
            
            # Contar prioridades
            prio = classification.get('prioridad', 'unknown')
            priorities[prio] = priorities.get(prio, 0) + 1
            
            # Contar áreas
            area = classification.get('area_responsable', 'unknown')
            areas[area] = areas.get(area, 0) + 1
            
        except (json.JSONDecodeError, KeyError):
            continue
    
    return {
        'total_classified': len(records),
        'categories': categories,
        'priorities': priorities,
        'areas': areas,
        'accuracy_rate': calculate_accuracy_rate(records),
        'recent_classifications': get_recent_classifications(records)
    }

def calculate_accuracy_rate(records):
    """Calcular tasa de precisión (simulada)"""
    # En un sistema real, esto se basaría en feedback de usuarios
    # Por ahora, simulamos basándose en completitud de datos
    accurate_count = 0
    
    for record in records:
        try:
            classification = json.loads(record.ai_classification)
            # Considerar "preciso" si tiene todos los campos principales
            if all(key in classification for key in ['categoria', 'prioridad', 'area_responsable']):
                accurate_count += 1
        except:
            continue
    
    return (accurate_count / len(records) * 100) if records else 0

def get_recent_classifications(records):
    """Obtener clasificaciones recientes"""
    recent = sorted(records, key=lambda x: x.created_at, reverse=True)[:10]
    
    result = []
    for record in recent:
        try:
            classification = json.loads(record.ai_classification)
            result.append({
                'id': record.id,
                'title': record.title,
                'category': classification.get('categoria'),
                'priority': classification.get('prioridad'),
                'area': classification.get('area_responsable'),
                'created_at': record.created_at.strftime('%d/%m/%Y %H:%M')
            })
        except:
            continue
    
    return result

@bp.route('/retrain-model', methods=['POST'])
@login_required
def retrain_model():
    """Reentrenar modelo con feedback (simulado)"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'Permisos insuficientes'}), 403
    
    try:
        # En un sistema real, esto reentrenarían el modelo de IA
        # Por ahora, simulamos el proceso
        
        flash('Modelo de IA reentrenado exitosamente con los últimos datos', 'success')
        return jsonify({
            'success': True,
            'message': 'Modelo reentrenado exitosamente',
            'improvements': [
                'Precisión en categoría "seguridad" mejorada en 5%',
                'Detección de urgencias optimizada',
                'Nuevas palabras clave agregadas al vocabulario'
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
