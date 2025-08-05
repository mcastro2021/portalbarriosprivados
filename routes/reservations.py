from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Reservation, User
from datetime import datetime, timedelta
from dateutil import parser
from config import config

bp = Blueprint('reservations', __name__, url_prefix='/reservations')

@bp.route('/')
@login_required
def index():
    """Lista de reservas"""
    page = request.args.get('page', 1, type=int)
    
    # Si es administrador, mostrar todas las reservas
    if current_user.role == 'admin':
        reservations = Reservation.query.order_by(Reservation.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False)
    else:
        # Si es residente, mostrar solo sus reservas
        reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False)
    
    return render_template('reservations/index.html', reservations=reservations)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Crear nueva reserva"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            space_type = request.form.get('space_type', '').strip()
            space_name = request.form.get('space_name', '').strip()
            date = request.form.get('date', '').strip()
            start_time = request.form.get('start_time', '').strip()
            end_time = request.form.get('end_time', '').strip()
            guests_count = request.form.get('guests_count', '1')
            event_type = request.form.get('event_type', '').strip()
            description = request.form.get('description', '').strip()
            
            # Validaciones
            if not space_type:
                flash('El tipo de espacio es obligatorio', 'error')
                return render_template('reservations/new.html')
            
            if not space_name:
                flash('El nombre del espacio es obligatorio', 'error')
                return render_template('reservations/new.html')
            
            if not date:
                flash('La fecha es obligatoria', 'error')
                return render_template('reservations/new.html')
            
            if not start_time:
                flash('La hora de inicio es obligatoria', 'error')
                return render_template('reservations/new.html')
            
            if not end_time:
                flash('La hora de fin es obligatoria', 'error')
                return render_template('reservations/new.html')
            
            # Combinar fecha y hora
            start_datetime = parser.parse(f"{date} {start_time}")
            end_datetime = parser.parse(f"{date} {end_time}")
            
            # Validar que la hora de fin sea posterior a la de inicio
            if end_datetime <= start_datetime:
                flash('La hora de fin debe ser posterior a la hora de inicio', 'error')
                return render_template('reservations/new.html')
            
            # Verificar que la fecha no sea en el pasado
            if start_datetime < datetime.now():
                flash('La fecha y hora no pueden ser en el pasado', 'error')
                return render_template('reservations/new.html')
            
            # Verificar disponibilidad
            conflicting = Reservation.query.filter(
                Reservation.space_type == space_type,
                Reservation.status == 'approved',
                Reservation.start_time < end_datetime,
                Reservation.end_time > start_datetime
            ).first()
            
            if conflicting:
                flash('El espacio no está disponible en ese horario', 'error')
                return render_template('reservations/new.html')
            
            # Crear reserva
            reservation = Reservation(
                user_id=current_user.id,
                space_type=space_type,
                space_name=space_name,
                start_time=start_datetime,
                end_time=end_datetime,
                guests_count=int(guests_count),
                event_type=event_type,
                description=description
            )
            
            db.session.add(reservation)
            db.session.commit()
            
            flash('Reserva solicitada exitosamente', 'success')
            return redirect(url_for('reservations.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la reserva: {str(e)}', 'error')
            return render_template('reservations/new.html')
    
    # Obtener espacios disponibles
    spaces = config['COMMON_SPACES']
    return render_template('reservations/new.html', spaces=spaces)

@bp.route('/<int:reservation_id>')
@login_required
def show(reservation_id):
    """Mostrar detalles de una reserva"""
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Verificar permisos
    if reservation.user_id != current_user.id and current_user.role != 'admin':
        flash('No tienes permisos para ver esta reserva', 'error')
        return redirect(url_for('reservations.index'))
    
    return render_template('reservations/show.html', reservation=reservation)

@bp.route('/<int:reservation_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(reservation_id):
    """Editar reserva"""
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Verificar permisos
    if reservation.user_id != current_user.id and current_user.role != 'admin':
        flash('No tienes permisos para editar esta reserva', 'error')
        return redirect(url_for('reservations.index'))
    
    # No permitir editar reservas completadas o canceladas
    if reservation.status in ['completed', 'cancelled']:
        flash('No se puede editar una reserva completada o cancelada', 'error')
        return redirect(url_for('reservations.show', reservation_id=reservation.id))
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            space_type = request.form.get('space_type', '').strip()
            space_name = request.form.get('space_name', '').strip()
            date = request.form.get('date', '').strip()
            start_time = request.form.get('start_time', '').strip()
            end_time = request.form.get('end_time', '').strip()
            guests_count = request.form.get('guests_count', '1')
            event_type = request.form.get('event_type', '').strip()
            description = request.form.get('description', '').strip()
            
            # Validaciones
            if not space_type:
                flash('El tipo de espacio es obligatorio', 'error')
                return render_template('reservations/edit.html', reservation=reservation)
            
            if not space_name:
                flash('El nombre del espacio es obligatorio', 'error')
                return render_template('reservations/edit.html', reservation=reservation)
            
            if not date:
                flash('La fecha es obligatoria', 'error')
                return render_template('reservations/edit.html', reservation=reservation)
            
            if not start_time:
                flash('La hora de inicio es obligatoria', 'error')
                return render_template('reservations/edit.html', reservation=reservation)
            
            if not end_time:
                flash('La hora de fin es obligatoria', 'error')
                return render_template('reservations/edit.html', reservation=reservation)
            
            # Combinar fecha y hora
            start_datetime = parser.parse(f"{date} {start_time}")
            end_datetime = parser.parse(f"{date} {end_time}")
            
            # Validar que la hora de fin sea posterior a la de inicio
            if end_datetime <= start_datetime:
                flash('La hora de fin debe ser posterior a la hora de inicio', 'error')
                return render_template('reservations/edit.html', reservation=reservation)
            
            # Verificar disponibilidad (excluyendo la reserva actual)
            conflicting = Reservation.query.filter(
                Reservation.space_type == space_type,
                Reservation.status == 'approved',
                Reservation.start_time < end_datetime,
                Reservation.end_time > start_datetime,
                Reservation.id != reservation.id
            ).first()
            
            if conflicting:
                flash('El espacio no está disponible en ese horario', 'error')
                return render_template('reservations/edit.html', reservation=reservation)
            
            # Actualizar reserva
            reservation.space_type = space_type
            reservation.space_name = space_name
            reservation.start_time = start_datetime
            reservation.end_time = end_datetime
            reservation.guests_count = int(guests_count)
            reservation.event_type = event_type
            reservation.description = description
            
            db.session.commit()
            
            flash('Reserva actualizada exitosamente', 'success')
            return redirect(url_for('reservations.show', reservation_id=reservation.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la reserva: {str(e)}', 'error')
    
    # Obtener espacios disponibles
    spaces = config['COMMON_SPACES']
    return render_template('reservations/edit.html', reservation=reservation, spaces=spaces)

@bp.route('/<int:reservation_id>/delete', methods=['POST'])
@login_required
def delete(reservation_id):
    """Eliminar reserva"""
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Verificar permisos
    if reservation.user_id != current_user.id and current_user.role != 'admin':
        flash('No tienes permisos para eliminar esta reserva', 'error')
        return redirect(url_for('reservations.index'))
    
    # No permitir eliminar reservas completadas
    if reservation.status == 'completed':
        flash('No se puede eliminar una reserva completada', 'error')
        return redirect(url_for('reservations.show', reservation_id=reservation.id))
    
    try:
        db.session.delete(reservation)
        db.session.commit()
        flash('Reserva eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la reserva: {str(e)}', 'error')
    
    return redirect(url_for('reservations.index'))

@bp.route('/<int:reservation_id>/cancel', methods=['POST'])
@login_required
def cancel(reservation_id):
    """Cancelar reserva"""
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Verificar permisos
    if reservation.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    if reservation.status not in ['pending', 'approved']:
        return jsonify({'error': 'La reserva no puede ser cancelada'}), 400
    
    if not reservation.can_be_cancelled():
        return jsonify({'error': 'La reserva no puede ser cancelada (menos de 24 horas)'}), 400
    
    try:
        reservation.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reserva cancelada exitosamente'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/calendar')
@login_required
def calendar():
    """Calendario de reservas"""
    # Obtener reservas del mes actual
    now = datetime.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    
    reservations = Reservation.query.filter(
        Reservation.start_time >= start_of_month,
        Reservation.start_time <= end_of_month,
        Reservation.status == 'approved'
    ).all()
    
    # Formatear reservas para el calendario
    calendar_events = []
    for reservation in reservations:
        calendar_events.append({
            'id': reservation.id,
            'title': f"{reservation.space_name} - {reservation.user.name}",
            'start': reservation.start_time.isoformat(),
            'end': reservation.end_time.isoformat(),
            'url': url_for('reservations.show', reservation_id=reservation.id)
        })
    
    return render_template('reservations/calendar.html', events=calendar_events)

@bp.route('/api/availability/<space_type>')
@login_required
def availability(space_type):
    """API para verificar disponibilidad de un espacio"""
    date = request.args.get('date')
    if not date:
        return jsonify({'error': 'Fecha requerida'}), 400
    
    try:
        # Obtener reservas para la fecha especificada
        start_date = parser.parse(date).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        reservations = Reservation.query.filter(
            Reservation.space_type == space_type,
            Reservation.status == 'approved',
            Reservation.start_time >= start_date,
            Reservation.start_time < end_date
        ).all()
        
        # Formatear horarios ocupados
        busy_times = []
        for reservation in reservations:
            busy_times.append({
                'start': reservation.start_time.strftime('%H:%M'),
                'end': reservation.end_time.strftime('%H:%M')
            })
        
        return jsonify({
            'space_type': space_type,
            'date': date,
            'busy_times': busy_times
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 