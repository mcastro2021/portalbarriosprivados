from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, SecurityReport, User, Notification
from werkzeug.utils import secure_filename
from datetime import datetime, time
import os
import json

bp = Blueprint('security', __name__, url_prefix='/security')

@bp.route('/')
def index():
    """Mostrar reportes de seguridad"""
    # Permitir acceso público para crear reportes o ver botón antipánico
    
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    severity = request.args.get('severity', '')
    
    query = SecurityReport.query
    
    # Filtros según tipo de usuario
    if current_user.is_authenticated and current_user.can_view_security_reports():
        # Admin ve todos los reportes
        pass
    elif current_user.is_authenticated:
        # Usuario normal solo ve sus propios reportes
        query = query.filter_by(reporter_id=current_user.id)
    else:
        # Usuario anónimo solo ve reportes públicos críticos
        query = query.filter_by(severity='critical')
    
    if status:
        query = query.filter_by(status=status)
    
    if severity:
        query = query.filter_by(severity=severity)
    
    reports = query.order_by(SecurityReport.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    # Estadísticas
    total_reports = SecurityReport.query.count()
    pending_reports = SecurityReport.query.filter_by(status='reported').count()
    resolved_reports = SecurityReport.query.filter_by(status='resolved').count()
    
    return render_template('security/index.html',
                         reports=reports,
                         total_reports=total_reports,
                         pending_reports=pending_reports,
                         resolved_reports=resolved_reports,
                         current_status=status,
                         current_severity=severity)

@bp.route('/new', methods=['GET', 'POST'])
def new_report():
    """Crear nuevo reporte de seguridad"""
    if request.method == 'POST':
        try:
            # Obtener fecha y hora del incidente
            incident_date_str = request.form.get('incident_date')
            incident_time_str = request.form.get('incident_time')
            
            incident_date = datetime.strptime(incident_date_str, '%Y-%m-%d').date() if incident_date_str else None
            incident_time = datetime.strptime(incident_time_str, '%H:%M').time() if incident_time_str else None
            
            # Crear reporte
            report = SecurityReport(
                user_id=current_user.id if current_user.is_authenticated else None,
                reporter_name=request.form.get('reporter_name') if not current_user.is_authenticated else None,
                reporter_phone=request.form.get('reporter_phone') if not current_user.is_authenticated else None,
                reporter_email=request.form.get('reporter_email') if not current_user.is_authenticated else None,
                title=request.form.get('title'),
                incident_type=request.form.get('incident_type'),
                description=request.form.get('description'),
                location=request.form.get('location'),
                severity=request.form.get('severity', 'medium'),
                incident_date=incident_date,
                incident_time=incident_time,
                witnesses=request.form.get('witnesses'),
                suspects=request.form.get('suspects'),
                contact_phone=request.form.get('contact_phone', current_user.phone),
                emergency_contact=request.form.get('emergency_contact'),
                anonymous=bool(request.form.get('anonymous'))
            )
            
            db.session.add(report)
            db.session.flush()  # Para obtener el ID
            
            # Procesar fotos
            photo_paths = []
            for i in range(5):  # Máximo 5 fotos
                file_key = f'photo_{i}'
                if file_key in request.files:
                    file = request.files[file_key]
                    if file and file.filename:
                        filename = secure_filename(f"security_{report.id}_{i}_{file.filename}")
                        file_path = os.path.join('uploads', 'security', filename)
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        file.save(file_path)
                        photo_paths.append(filename)
            
            if photo_paths:
                report.photo_paths = json.dumps(photo_paths)
            
            db.session.commit()
            
            # Notificar a administradores y seguridad
            notify_security_team(report)
            
            flash('Reporte de seguridad enviado exitosamente', 'success')
            return redirect(url_for('security.view', id=report.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el reporte: {str(e)}', 'error')
    
    return render_template('security/new_report.html')

@bp.route('/<int:id>')
@login_required
def view(id):
    """Ver reporte específico"""
    report = SecurityReport.query.get_or_404(id)
    
    # Verificar permisos
    if not current_user.can_view_security_reports() and report.user_id != current_user.id:
        flash('No tienes permiso para ver este reporte', 'error')
        return redirect(url_for('security.index'))
    
    return render_template('security/view.html', report=report)

@bp.route('/assign/<int:id>', methods=['POST'])
@login_required
def assign(id):
    """Asignar reporte a usuario"""
    if not current_user.can_access_admin():
        return jsonify({'error': 'No autorizado'}), 403
    
    report = SecurityReport.query.get_or_404(id)
    assignee_id = request.json.get('assignee_id')
    
    try:
        if assignee_id:
            assignee = User.query.get(assignee_id)
            if not assignee or assignee.role not in ['admin', 'security']:
                return jsonify({'error': 'Usuario no válido para asignación'}), 400
            
            report.assigned_to = assignee_id
            report.assigned_at = datetime.utcnow()
            report.status = 'investigating'
        else:
            report.assigned_to = None
            report.assigned_at = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reporte asignado exitosamente' if assignee_id else 'Asignación removida'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/update_status/<int:id>', methods=['POST'])
@login_required
def update_status(id):
    """Actualizar estado del reporte"""
    if not current_user.can_view_security_reports():
        return jsonify({'error': 'No autorizado'}), 403
    
    report = SecurityReport.query.get_or_404(id)
    new_status = request.json.get('status')
    admin_notes = request.json.get('admin_notes', '')
    
    if new_status not in ['reported', 'investigating', 'resolved', 'closed']:
        return jsonify({'error': 'Estado no válido'}), 400
    
    try:
        report.status = new_status
        if admin_notes:
            report.admin_notes = admin_notes
        
        if new_status == 'resolved':
            report.resolved_at = datetime.utcnow()
        
        db.session.commit()
        
        # Notificar al usuario que creó el reporte
        if report.user_id != current_user.id:
            status_display = {
                'reported': 'Reportado',
                'investigating': 'Investigando', 
                'resolved': 'Resuelto',
                'closed': 'Cerrado'
            }.get(new_status, new_status.title())
            
            notification = Notification(
                user_id=report.user_id,
                title='Actualización de Reporte de Seguridad',
                message=f'Tu reporte "{report.title}" ha sido actualizado a: {status_display}',
                category='security',
                related_id=report.id,
                related_type='security_report'
            )
            db.session.add(notification)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Estado actualizado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/panic_button', methods=['POST'])
def panic_button():
    """Activar botón de pánico - EMERGENCIA INMEDIATA"""
    try:
        # Log de activación del botón de pánico
        logger.critical("🚨 BOTÓN DE PÁNICO ACTIVADO")
        
        # Crear reporte de emergencia
        data = request.get_json() or {}
        
        if current_user.is_authenticated:
            user_info = f'{current_user.name} ({current_user.username})'
            location = current_user.address or 'Ubicación no especificada'
            contact_phone = current_user.phone
            emergency_contact = current_user.emergency_contact
        else:
            user_info = data.get('anonymous_name', 'Usuario Anónimo')
            location = data.get('location', 'Ubicación no especificada')
            contact_phone = data.get('anonymous_phone', 'No especificado')
            emergency_contact = None
        
        # Crear reporte de emergencia con prioridad máxima
        report = SecurityReport(
            user_id=current_user.id if current_user.is_authenticated else None,
            reporter_name=data.get('anonymous_name') if not current_user.is_authenticated else None,
            reporter_phone=data.get('anonymous_phone') if not current_user.is_authenticated else None,
            title='🚨 ALERTA DE PÁNICO - EMERGENCIA INMEDIATA',
            incident_type='emergency',
            description=f'BOTÓN DE PÁNICO ACTIVADO\n\nUsuario: {user_info}\nUbicación: {location}\nHora: {datetime.utcnow().strftime("%H:%M:%S")}\n\nDescripción: {data.get("emergency_description", "Emergencia reportada")}\n\nACCIÓN INMEDIATA REQUERIDA',
            location=location,
            severity='critical',
            status='active',  # Estado activo para emergencias
            incident_date=datetime.utcnow().date(),
            incident_time=datetime.utcnow().time(),
            contact_phone=contact_phone,
            emergency_contact=emergency_contact
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Notificar inmediatamente a todo el equipo de seguridad
        notify_emergency_team(report)
        
        # Log de confirmación
        logger.critical(f"🚨 ALERTA DE PÁNICO CONFIRMADA: Reporte ID {report.id}")
        
        return jsonify({
            'success': True,
            'message': '🚨 ALERTA DE PÁNICO ENVIADA\nEl equipo de seguridad ha sido notificado inmediatamente.',
            'report_id': report.id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error en botón de pánico: {str(e)}")
        return jsonify({'error': 'Error procesando alerta de pánico. Contacta seguridad directamente.'}), 500

def notify_security_team(report):
    """Notificar al equipo de seguridad sobre nuevo reporte"""
    security_users = User.query.filter(User.role.in_(['admin', 'security'])).all()
    
    for user in security_users:
        notification = Notification(
            user_id=user.id,
            title='Nuevo Reporte de Seguridad',
            message=f'Nuevo reporte: {report.title} (Severidad: {report.get_severity_display()})',
            category='security',
            related_id=report.id,
            related_type='security_report'
        )
        db.session.add(notification)

def notify_emergency_team(report):
    """Notificar al equipo de emergencia sobre alerta de pánico"""
    emergency_users = User.query.filter(User.role.in_(['admin', 'security'])).all()
    
    for user in emergency_users:
        # Notificación de emergencia con prioridad máxima
        notification = Notification(
            user_id=user.id,
            title='🚨 ALERTA DE PÁNICO - EMERGENCIA 🚨',
            message=f'BOTÓN DE PÁNICO ACTIVADO\n\nUsuario: {report.author.name if report.author else report.reporter_name}\nUbicación: {report.location}\nHora: {datetime.utcnow().strftime("%H:%M:%S")}\n\nACCIÓN INMEDIATA REQUERIDA',
            category='emergency',
            related_id=report.id,
            related_type='security_report',
            priority='critical'
        )
        db.session.add(notification)
        
        # Log de emergencia para auditoría
        logger.critical(f"🚨 ALERTA DE PÁNICO: Usuario {report.author.name if report.author else report.reporter_name} en {report.location}")
    
    db.session.commit()