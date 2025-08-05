from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Maintenance, User
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from config import config

bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')

@bp.route('/')
@login_required
def index():
    """Lista de reportes de mantenimiento"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    # Construir query base
    if current_user.role == 'admin':
        query = Maintenance.query
    elif current_user.role == 'maintenance':
        query = Maintenance.query.filter(
            (Maintenance.assigned_to == current_user.id) | 
            (Maintenance.assigned_to.is_(None))
        )
    else:
        query = Maintenance.query.filter_by(user_id=current_user.id)
    
    # Filtrar por estado si se especifica
    if status:
        query = query.filter_by(status=status)
    
    maintenance = query.order_by(Maintenance.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    # Obtener estados para el filtro
    statuses = config['MAINTENANCE_STATUSES']
    
    return render_template('maintenance/index.html', maintenance=maintenance, statuses=statuses, current_status=status)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Crear nuevo reporte de mantenimiento"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            title = request.form.get('title', '').strip()
            category = request.form.get('category', '').strip()
            priority = request.form.get('priority', '').strip()
            location = request.form.get('location', '').strip()
            description = request.form.get('description', '').strip()
            contact_phone = request.form.get('contact_phone', '').strip()
            preferred_time = request.form.get('preferred_time', '').strip()
            urgent_access = request.form.get('urgent_access') == 'on'
            
            # Validaciones
            if not title:
                flash('El título es obligatorio', 'error')
                return render_template('maintenance/new.html')
            
            if not priority:
                flash('La prioridad es obligatoria', 'error')
                return render_template('maintenance/new.html')
            
            if not location:
                flash('La ubicación es obligatoria', 'error')
                return render_template('maintenance/new.html')
            
            if not description:
                flash('La descripción es obligatoria', 'error')
                return render_template('maintenance/new.html')
            
            # Procesar fotos
            photo_paths = []
            if 'photos' in request.files:
                files = request.files.getlist('photos')
                for file in files:
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        file_path = os.path.join('maintenance', filename)
                        full_path = os.path.join('uploads', file_path)
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        file.save(full_path)
                        photo_paths.append(file_path)
            
            # Crear descripción completa
            full_description = description
            if category:
                full_description += f"\nCategoría: {category}"
            if contact_phone:
                full_description += f"\nTeléfono: {contact_phone}"
            if preferred_time:
                full_description += f"\nHorario preferido: {preferred_time}"
            if urgent_access:
                full_description += "\n⚠️ REQUIERE ACCESO URGENTE"
            
            # Guardar la primera foto como principal
            photo_path = photo_paths[0] if photo_paths else None
            
            # Crear reporte
            maintenance = Maintenance(
                user_id=current_user.id,
                title=title,
                description=full_description,
                location=location,
                priority=priority,
                photo_path=photo_path
            )
            
            db.session.add(maintenance)
            db.session.commit()
            
            flash('Reporte de mantenimiento enviado exitosamente', 'success')
            return redirect(url_for('maintenance.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al enviar el reporte: {str(e)}', 'error')
            return render_template('maintenance/new.html')
    
    # Obtener prioridades
    priorities = config['MAINTENANCE_PRIORITIES']
    return render_template('maintenance/new.html', priorities=priorities)

@bp.route('/<int:maintenance_id>')
@login_required
def show(maintenance_id):
    """Mostrar detalles de un reporte de mantenimiento"""
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    
    # Verificar permisos
    if (maintenance.user_id != current_user.id and 
        current_user.role not in ['admin', 'maintenance']):
        flash('No tienes permisos para ver este reporte', 'error')
        return redirect(url_for('maintenance.index'))
    
    return render_template('maintenance/show.html', maintenance=maintenance)

@bp.route('/<int:maintenance_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(maintenance_id):
    """Editar reporte de mantenimiento"""
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    
    # Verificar permisos
    if maintenance.user_id != current_user.id and current_user.role != 'admin':
        flash('No tienes permisos para editar este reporte', 'error')
        return redirect(url_for('maintenance.show', maintenance_id=maintenance.id))
    
    # No permitir editar reportes completados
    if maintenance.status == 'completed':
        flash('No se puede editar un reporte completado', 'error')
        return redirect(url_for('maintenance.show', maintenance_id=maintenance.id))
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            title = request.form.get('title', '').strip()
            category = request.form.get('category', '').strip()
            priority = request.form.get('priority', '').strip()
            location = request.form.get('location', '').strip()
            description = request.form.get('description', '').strip()
            contact_phone = request.form.get('contact_phone', '').strip()
            preferred_time = request.form.get('preferred_time', '').strip()
            urgent_access = request.form.get('urgent_access') == 'on'
            
            # Validaciones
            if not title:
                flash('El título es obligatorio', 'error')
                return render_template('maintenance/edit.html', maintenance=maintenance)
            
            if not priority:
                flash('La prioridad es obligatoria', 'error')
                return render_template('maintenance/edit.html', maintenance=maintenance)
            
            if not location:
                flash('La ubicación es obligatoria', 'error')
                return render_template('maintenance/edit.html', maintenance=maintenance)
            
            if not description:
                flash('La descripción es obligatoria', 'error')
                return render_template('maintenance/edit.html', maintenance=maintenance)
            
            # Procesar nuevas fotos
            if 'photos' in request.files:
                files = request.files.getlist('photos')
                for file in files:
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        file_path = os.path.join('maintenance', filename)
                        full_path = os.path.join('uploads', file_path)
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        file.save(full_path)
                        maintenance.add_photo_path(file_path)
            
            # Crear descripción completa
            full_description = description
            if category:
                full_description += f"\nCategoría: {category}"
            if contact_phone:
                full_description += f"\nTeléfono: {contact_phone}"
            if preferred_time:
                full_description += f"\nHorario preferido: {preferred_time}"
            if urgent_access:
                full_description += "\n⚠️ REQUIERE ACCESO URGENTE"
            
            # Actualizar reporte
            maintenance.title = title
            maintenance.description = full_description
            maintenance.location = location
            maintenance.priority = priority
            
            db.session.commit()
            
            flash('Reporte actualizado exitosamente', 'success')
            return redirect(url_for('maintenance.show', maintenance_id=maintenance.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el reporte: {str(e)}', 'error')
    
    # Obtener prioridades
    priorities = config['MAINTENANCE_PRIORITIES']
    return render_template('maintenance/edit.html', maintenance=maintenance, priorities=priorities)

@bp.route('/<int:maintenance_id>/delete', methods=['POST'])
@login_required
def delete(maintenance_id):
    """Eliminar reporte de mantenimiento"""
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    
    # Verificar permisos
    if maintenance.user_id != current_user.id and current_user.role != 'admin':
        flash('No tienes permisos para eliminar este reporte', 'error')
        return redirect(url_for('maintenance.index'))
    
    # No permitir eliminar reportes completados
    if maintenance.status == 'completed':
        flash('No se puede eliminar un reporte completado', 'error')
        return redirect(url_for('maintenance.show', maintenance_id=maintenance.id))
    
    try:
        # Eliminar fotos asociadas
        photo_paths = maintenance.get_photo_paths_list()
        for photo_path in photo_paths:
            try:
                full_path = os.path.join('uploads', photo_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
            except:
                pass  # Si no se puede eliminar la foto, continuar
        
        db.session.delete(maintenance)
        db.session.commit()
        flash('Reporte eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el reporte: {str(e)}', 'error')
    
    return redirect(url_for('maintenance.index'))

@bp.route('/<int:maintenance_id>/assign', methods=['POST'])
@login_required
def assign(maintenance_id):
    """Asignar reporte a personal de mantenimiento"""
    if current_user.role not in ['admin', 'maintenance']:
        return jsonify({'error': 'No autorizado'}), 403
    
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    assignee_id = request.form.get('assignee_id', type=int)
    
    try:
        if assignee_id:
            assignee = User.query.get(assignee_id)
            if assignee and assignee.role == 'maintenance':
                maintenance.assigned_to = assignee_id
                maintenance.assigned_at = datetime.utcnow()
                maintenance.status = 'in_progress'
            else:
                return jsonify({'error': 'Usuario de mantenimiento no válido'}), 400
        else:
            maintenance.assigned_to = None
            maintenance.assigned_at = None
            maintenance.status = 'pending'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reporte asignado exitosamente',
            'assignee_name': assignee.name if assignee else None
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:maintenance_id>/update-status', methods=['POST'])
@login_required
def update_status(maintenance_id):
    """Actualizar estado del reporte"""
    if current_user.role not in ['admin', 'maintenance']:
        return jsonify({'error': 'No autorizado'}), 403
    
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    new_status = request.form.get('status', '').strip()
    admin_notes = request.form.get('admin_notes', '').strip()
    
    if new_status not in ['pending', 'in_progress', 'completed', 'cancelled']:
        return jsonify({'error': 'Estado no válido'}), 400
    
    try:
        maintenance.status = new_status
        if admin_notes:
            maintenance.admin_notes = admin_notes
        
        if new_status == 'completed':
            maintenance.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Estado actualizado a {new_status}',
            'status': new_status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/stats')
@login_required
def api_stats():
    """API para estadísticas de mantenimiento"""
    if current_user.role not in ['admin', 'maintenance']:
        return jsonify({'error': 'No autorizado'}), 403
    
    # Construir query base
    if current_user.role == 'admin':
        query = Maintenance.query
    else:
        query = Maintenance.query.filter(
            (Maintenance.assigned_to == current_user.id) | 
            (Maintenance.assigned_to.is_(None))
        )
    
    # Estadísticas por estado
    stats = {}
    for status_code, status_name in config['MAINTENANCE_STATUSES']:
        count = query.filter_by(status=status_code).count()
        stats[status_code] = {
            'name': status_name,
            'count': count
        }
    
    # Estadísticas por prioridad
    priority_stats = {}
    for priority_code, priority_name in config['MAINTENANCE_PRIORITIES']:
        count = query.filter_by(priority=priority_code).count()
        priority_stats[priority_code] = {
            'name': priority_name,
            'count': count
        }
    
    return jsonify({
        'status_stats': stats,
        'priority_stats': priority_stats,
        'total': query.count()
    }) 