from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Visit, User
from datetime import datetime, timedelta
from dateutil import parser
import qrcode
import io
import base64
import uuid

bp = Blueprint('visits', __name__, url_prefix='/visits')

@bp.route('/')
@login_required
def index():
    """Lista de visitas"""
    page = request.args.get('page', 1, type=int)
    
    # Si es administrador, mostrar todas las visitas
    if current_user.role == 'admin':
        visits = Visit.query.order_by(Visit.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False)
    else:
        # Si es residente, mostrar solo sus visitas
        visits = Visit.query.filter_by(resident_id=current_user.id).order_by(Visit.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False)
    
    return render_template('visits/index.html', visits=visits)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Registrar nueva visita"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            visitor_name = request.form.get('visitor_name', '').strip()
            visitor_phone = request.form.get('visitor_phone', '').strip()
            visitor_document = request.form.get('visitor_document', '').strip()
            vehicle_plate = request.form.get('vehicle_plate', '').strip()
            visit_date = request.form.get('visit_date', '')
            visit_time = request.form.get('visit_time', '')
            estimated_duration = request.form.get('estimated_duration', '1')
            visit_purpose = request.form.get('visit_purpose', '')
            notes = request.form.get('notes', '').strip()
            notify_security = request.form.get('notify_security') == 'on'
            
            # Validaciones
            if not visitor_name:
                flash('El nombre del visitante es obligatorio', 'error')
                return render_template('visits/new.html')
            
            if not visitor_phone:
                flash('El teléfono del visitante es obligatorio', 'error')
                return render_template('visits/new.html')
            
            if not visitor_document:
                flash('El DNI/Pasaporte del visitante es obligatorio', 'error')
                return render_template('visits/new.html')
            
            if not visit_date or not visit_time:
                flash('La fecha y hora de visita son obligatorias', 'error')
                return render_template('visits/new.html')
            
            if not visit_purpose:
                flash('El propósito de la visita es obligatorio', 'error')
                return render_template('visits/new.html')
            
            # Combinar fecha y hora
            entry_time = parser.parse(f"{visit_date} {visit_time}")
            
            # Verificar que la fecha no sea en el pasado
            if entry_time < datetime.now():
                flash('La fecha y hora de visita no pueden ser en el pasado', 'error')
                return render_template('visits/new.html')
            
            # Crear visita
            visit = Visit(
                visitor_name=visitor_name,
                visitor_phone=visitor_phone,
                visitor_document=visitor_document,
                vehicle_plate=vehicle_plate,
                resident_id=current_user.id,
                entry_time=entry_time,
                estimated_duration=int(estimated_duration),
                visit_purpose=visit_purpose,
                notes=notes,
                notify_security=notify_security,
                qr_code_id=f"visit_{uuid.uuid4().hex[:8]}"
            )
            
            # Generar QR code
            visit.generate_qr_code()
            
            db.session.add(visit)
            db.session.commit()
            
            flash('Visita registrada exitosamente', 'success')
            return redirect(url_for('visits.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la visita: {str(e)}', 'error')
            return render_template('visits/new.html')
    
    return render_template('visits/new.html')

@bp.route('/<int:visit_id>')
@login_required
def show(visit_id):
    """Mostrar detalles de una visita"""
    visit = Visit.query.get_or_404(visit_id)
    
    # Verificar permisos
    if visit.resident_id != current_user.id and current_user.role != 'admin':
        flash('No tienes permisos para ver esta visita', 'error')
        return redirect(url_for('visits.index'))
    
    return render_template('visits/show.html', visit=visit)

@bp.route('/<int:visit_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(visit_id):
    """Editar visita"""
    visit = Visit.query.get_or_404(visit_id)
    
    # Verificar permisos
    if visit.resident_id != current_user.id and current_user.role != 'admin':
        flash('No tienes permisos para editar esta visita', 'error')
        return redirect(url_for('visits.index'))
    
    # No permitir editar visitas completadas
    if visit.status == 'completed':
        flash('No se puede editar una visita completada', 'error')
        return redirect(url_for('visits.show', visit_id=visit.id))
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            visitor_name = request.form.get('visitor_name', '').strip()
            visitor_phone = request.form.get('visitor_phone', '').strip()
            visitor_document = request.form.get('visitor_document', '').strip()
            vehicle_plate = request.form.get('vehicle_plate', '').strip()
            visit_date = request.form.get('visit_date', '')
            visit_time = request.form.get('visit_time', '')
            estimated_duration = request.form.get('estimated_duration', '1')
            visit_purpose = request.form.get('visit_purpose', '')
            notes = request.form.get('notes', '').strip()
            notify_security = request.form.get('notify_security') == 'on'
            
            # Validaciones
            if not visitor_name:
                flash('El nombre del visitante es obligatorio', 'error')
                return render_template('visits/edit.html', visit=visit)
            
            if not visitor_phone:
                flash('El teléfono del visitante es obligatorio', 'error')
                return render_template('visits/edit.html', visit=visit)
            
            if not visitor_document:
                flash('El DNI/Pasaporte del visitante es obligatorio', 'error')
                return render_template('visits/edit.html', visit=visit)
            
            if not visit_date or not visit_time:
                flash('La fecha y hora de visita son obligatorias', 'error')
                return render_template('visits/edit.html', visit=visit)
            
            if not visit_purpose:
                flash('El propósito de la visita es obligatorio', 'error')
                return render_template('visits/edit.html', visit=visit)
            
            # Actualizar visita
            visit.visitor_name = visitor_name
            visit.visitor_phone = visitor_phone
            visit.visitor_document = visitor_document
            visit.vehicle_plate = vehicle_plate
            visit.entry_time = parser.parse(f"{visit_date} {visit_time}")
            visit.estimated_duration = int(estimated_duration)
            visit.visit_purpose = visit_purpose
            visit.notes = notes
            visit.notify_security = notify_security
            
            db.session.commit()
            
            flash('Visita actualizada exitosamente', 'success')
            return redirect(url_for('visits.show', visit_id=visit.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la visita: {str(e)}', 'error')
    
    return render_template('visits/edit.html', visit=visit)

@bp.route('/<int:visit_id>/delete', methods=['POST'])
@login_required
def delete(visit_id):
    """Eliminar visita"""
    visit = Visit.query.get_or_404(visit_id)
    
    # Verificar permisos
    if visit.resident_id != current_user.id and current_user.role != 'admin':
        flash('No tienes permisos para eliminar esta visita', 'error')
        return redirect(url_for('visits.index'))
    
    # No permitir eliminar visitas activas o completadas
    if visit.status in ['active', 'completed']:
        flash('No se puede eliminar una visita activa o completada', 'error')
        return redirect(url_for('visits.show', visit_id=visit.id))
    
    try:
        db.session.delete(visit)
        db.session.commit()
        flash('Visita eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la visita: {str(e)}', 'error')
    
    return redirect(url_for('visits.index'))

@bp.route('/<int:visit_id>/check-in', methods=['POST'])
@login_required
def check_in(visit_id):
    """Registrar entrada de visita"""
    visit = Visit.query.get_or_404(visit_id)
    
    # Verificar permisos
    if visit.resident_id != current_user.id and current_user.role not in ['admin', 'security']:
        return jsonify({'error': 'No autorizado'}), 403
    
    if visit.status != 'pending':
        return jsonify({'error': 'La visita no está pendiente'}), 400
    
    try:
        visit.check_in()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Entrada registrada para {visit.visitor_name}',
            'visit_id': visit.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:visit_id>/check-out', methods=['POST'])
@login_required
def check_out(visit_id):
    """Registrar salida de visita"""
    visit = Visit.query.get_or_404(visit_id)
    
    # Verificar permisos
    if visit.resident_id != current_user.id and current_user.role not in ['admin', 'security']:
        return jsonify({'error': 'No autorizado'}), 403
    
    if visit.status != 'active':
        return jsonify({'error': 'La visita no está activa'}), 400
    
    try:
        visit.check_out()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Salida registrada para {visit.visitor_name}',
            'visit_id': visit.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/qr/<int:visit_id>')
def qr_code(visit_id):
    """Mostrar código QR de visita"""
    visit = Visit.query.get_or_404(visit_id)
    
    # Verificar permisos
    if visit.resident_id != current_user.id and current_user.role != 'admin':
        flash('No tienes permisos para ver este código QR', 'error')
        return redirect(url_for('visits.index'))
    
    if not visit.qr_code:
        visit.generate_qr_code()
        db.session.commit()
    
    return render_template('visits/qr_code.html', visit=visit)

@bp.route('/api/validate-qr/<qr_code_id>')
def validate_qr(qr_code_id):
    """Validar código QR de visita"""
    visit = Visit.query.filter_by(qr_code_id=qr_code_id).first()
    
    if not visit:
        return jsonify({'valid': False, 'error': 'Código QR inválido'})
    
    if visit.status == 'completed':
        return jsonify({'valid': False, 'error': 'Visita ya completada'})
    
    if visit.is_expired():
        return jsonify({'valid': False, 'error': 'Visita expirada'})
    
    return jsonify({
        'valid': True,
        'visit': {
            'id': visit.id,
            'visitor_name': visit.visitor_name,
            'visitor_document': visit.visitor_document,
            'vehicle_plate': visit.vehicle_plate,
            'status': visit.status,
            'entry_time': visit.entry_time.isoformat() if visit.entry_time else None,
            'resident_name': visit.resident.name
        }
    }) 