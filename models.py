from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
import qrcode
import io
import base64

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Modelo de usuario del sistema"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='resident')  # resident, admin, security, maintenance
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    emergency_contact = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    phone_verified = db.Column(db.Boolean, default=False)
    profile_image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relaciones
    visits = db.relationship('Visit', backref='resident', lazy='dynamic', cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', foreign_keys='Reservation.user_id', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    news = db.relationship('News', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    maintenance_requests = db.relationship('Maintenance', foreign_keys='Maintenance.user_id', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    classifieds = db.relationship('Classified', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    security_reports = db.relationship('SecurityReport', foreign_keys='SecurityReport.user_id', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Establecer contraseña hasheada"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_address(self):
        """Obtener dirección completa"""
        return f"{self.address}" if self.address else "Dirección no especificada"
    
    def get_role_display(self):
        """Obtener nombre legible del rol"""
        roles = {
            'resident': 'Residente',
            'admin': 'Administrador',
            'security': 'Seguridad',
            'maintenance': 'Mantenimiento'
        }
        return roles.get(self.role, self.role.title())
    
    def can_access_admin(self):
        """Verificar si puede acceder al panel de administración"""
        return self.role in ['admin']
    
    def can_manage_users(self):
        """Verificar si puede gestionar usuarios"""
        return self.role in ['admin']
    
    def can_manage_spaces(self):
        """Verificar si puede gestionar espacios"""
        return self.role in ['admin', 'maintenance']
    
    def can_view_security_reports(self):
        """Verificar si puede ver reportes de seguridad"""
        return self.role in ['admin', 'security']

class Visit(db.Model):
    """Modelo de visitas"""
    __tablename__ = 'visits'
    
    id = db.Column(db.Integer, primary_key=True)
    visitor_name = db.Column(db.String(100), nullable=False)
    visitor_phone = db.Column(db.String(20))
    visitor_document = db.Column(db.String(20))
    vehicle_plate = db.Column(db.String(20))
    resident_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    entry_time = db.Column(db.DateTime)
    exit_time = db.Column(db.DateTime)
    estimated_duration = db.Column(db.Integer, default=1)  # horas
    visit_purpose = db.Column(db.String(200))
    notes = db.Column(db.Text)
    qr_code = db.Column(db.Text)
    qr_code_id = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20), default='pending')  # pending, active, completed, cancelled
    notify_security = db.Column(db.Boolean, default=True)
    security_notified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def generate_qr_code(self):
        """Generar código QR único para la visita"""
        if not self.qr_code_id:
            self.qr_code_id = f"visit_{self.id}_{uuid.uuid4().hex[:8]}"
        
        qr_data = f"BARRIO_VISIT:{self.qr_code_id}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        self.qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    def check_in(self):
        """Registrar entrada"""
        self.status = 'active'
        self.entry_time = datetime.utcnow()
    
    def check_out(self):
        """Registrar salida"""
        self.status = 'completed'
        self.exit_time = datetime.utcnow()
    
    def get_duration(self):
        """Obtener duración de la visita"""
        if self.entry_time and self.exit_time:
            return self.exit_time - self.entry_time
        elif self.entry_time:
            return datetime.utcnow() - self.entry_time
        return None
    
    def is_expired(self):
        """Verificar si la visita ha expirado"""
        if self.entry_time:
            return datetime.utcnow() > self.entry_time + timedelta(hours=self.estimated_duration)
        return False

class Reservation(db.Model):
    """Modelo de reservas de espacios comunes"""
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    space_type = db.Column(db.String(50), nullable=False)
    space_name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    guests_count = db.Column(db.Integer, default=1)
    event_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, cancelled, completed
    admin_notes = db.Column(db.Text)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con el aprobador
    approver = db.relationship('User', foreign_keys=[approved_by])
    
    def get_duration(self):
        """Obtener duración de la reserva"""
        return self.end_time - self.start_time
    
    def is_conflicting(self, other_reservation):
        """Verificar si hay conflicto con otra reserva"""
        return (self.space_type == other_reservation.space_type and
                self.status == 'approved' and other_reservation.status == 'approved' and
                self.start_time < other_reservation.end_time and
                self.end_time > other_reservation.start_time)
    
    def can_be_cancelled(self):
        """Verificar si la reserva puede ser cancelada"""
        return (self.status in ['pending', 'approved'] and 
                self.start_time > datetime.utcnow() + timedelta(hours=24))

class News(db.Model):
    """Modelo de noticias y comunicaciones"""
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50))
    is_important = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_expired(self):
        """Verificar si la noticia ha expirado"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def get_excerpt(self, length=150):
        """Obtener extracto del contenido"""
        return self.content[:length] + '...' if len(self.content) > length else self.content

class Maintenance(db.Model):
    """Modelo de reclamos y mantenimiento"""
    __tablename__ = 'maintenance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200))
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    photo_paths = db.Column(db.Text)  # JSON array de rutas de fotos
    contact_phone = db.Column(db.String(20))
    preferred_time = db.Column(db.String(100))
    urgent_access = db.Column(db.Boolean, default=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con el asignado
    assignee = db.relationship('User', foreign_keys=[assigned_to])
    
    def get_photo_paths_list(self):
        """Obtener lista de rutas de fotos"""
        import json
        if self.photo_paths:
            return json.loads(self.photo_paths)
        return []
    
    def add_photo_path(self, photo_path):
        """Agregar ruta de foto"""
        import json
        paths = self.get_photo_paths_list()
        paths.append(photo_path)
        self.photo_paths = json.dumps(paths)
    
    def get_priority_display(self):
        """Obtener nombre legible de la prioridad"""
        priorities = {
            'low': 'Baja',
            'medium': 'Media',
            'high': 'Alta',
            'urgent': 'Urgente'
        }
        return priorities.get(self.priority, self.priority.title())
    
    def get_status_display(self):
        """Obtener nombre legible del estado"""
        statuses = {
            'pending': 'Pendiente',
            'in_progress': 'En Progreso',
            'completed': 'Completado',
            'cancelled': 'Cancelado'
        }
        return statuses.get(self.status, self.status.title())

class Expense(db.Model):
    """Modelo de expensas y pagos"""
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month = db.Column(db.String(7), nullable=False)  # YYYY-MM
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue, cancelled
    payment_method = db.Column(db.String(50))
    payment_date = db.Column(db.DateTime)
    payment_reference = db.Column(db.String(100))
    mercadopago_preference_id = db.Column(db.String(100))
    mercadopago_payment_id = db.Column(db.String(100))
    due_date = db.Column(db.DateTime)
    late_fee = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_overdue(self):
        """Verificar si la expensa está vencida"""
        if self.due_date and self.status == 'pending':
            return datetime.utcnow() > self.due_date
        return False
    
    def get_total_amount(self):
        """Obtener monto total con recargos"""
        return self.amount + self.late_fee
    
    def get_month_display(self):
        """Obtener mes en formato legible"""
        try:
            year, month = self.month.split('-')
            from datetime import date
            return date(int(year), int(month), 1).strftime('%B %Y')
        except:
            return self.month

class Classified(db.Model):
    """Modelo de anuncios clasificados"""
    __tablename__ = 'classifieds'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    price = db.Column(db.Float)
    condition = db.Column(db.String(50))
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    location = db.Column(db.String(200))
    image_paths = db.Column(db.Text)  # JSON array de rutas de imágenes
    tags = db.Column(db.String(200))
    expiry_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_image_paths_list(self):
        """Obtener lista de rutas de imágenes"""
        import json
        if self.image_paths:
            return json.loads(self.image_paths)
        return []
    
    def add_image_path(self, image_path):
        """Agregar ruta de imagen"""
        import json
        paths = self.get_image_paths_list()
        paths.append(image_path)
        self.image_paths = json.dumps(paths)
    
    def is_expired(self):
        """Verificar si el clasificado ha expirado"""
        if self.expiry_date:
            return datetime.utcnow() > self.expiry_date
        return False
    
    def increment_views(self):
        """Incrementar contador de vistas"""
        self.views_count += 1

class SecurityReport(db.Model):
    """Modelo de reportes de seguridad"""
    __tablename__ = 'security_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    incident_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200))
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(20), default='reported')  # reported, investigating, resolved, closed
    incident_date = db.Column(db.DateTime)
    incident_time = db.Column(db.Time)
    witnesses = db.Column(db.Text)
    suspects = db.Column(db.Text)
    photo_paths = db.Column(db.Text)  # JSON array de rutas de fotos
    contact_phone = db.Column(db.String(20))
    emergency_contact = db.Column(db.String(200))
    anonymous = db.Column(db.Boolean, default=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con el asignado
    assignee = db.relationship('User', foreign_keys=[assigned_to])
    
    def get_photo_paths_list(self):
        """Obtener lista de rutas de fotos"""
        import json
        if self.photo_paths:
            return json.loads(self.photo_paths)
        return []
    
    def add_photo_path(self, photo_path):
        """Agregar ruta de foto"""
        import json
        paths = self.get_photo_paths_list()
        paths.append(photo_path)
        self.photo_paths = json.dumps(paths)
    
    def get_severity_display(self):
        """Obtener nombre legible de la severidad"""
        severities = {
            'low': 'Baja',
            'medium': 'Media',
            'high': 'Alta',
            'critical': 'Crítica'
        }
        return severities.get(self.severity, self.severity.title())

class Notification(db.Model):
    """Modelo de notificaciones"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))  # email, push, sms, whatsapp
    category = db.Column(db.String(50))  # visit, reservation, news, maintenance, security, expense
    related_id = db.Column(db.Integer)  # ID del elemento relacionado
    related_type = db.Column(db.String(50))  # Tipo del elemento relacionado
    is_read = db.Column(db.Boolean, default=False)
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def mark_as_read(self):
        """Marcar como leída"""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def mark_as_sent(self):
        """Marcar como enviada"""
        self.is_sent = True
        self.sent_at = datetime.utcnow()

class NeighborhoodMap(db.Model):
    """Modelo del mapa del barrio"""
    __tablename__ = 'neighborhood_map'
    
    id = db.Column(db.Integer, primary_key=True)
    block_name = db.Column(db.String(100), nullable=False)
    street_name = db.Column(db.String(100))
    block_number = db.Column(db.Integer)
    total_houses = db.Column(db.Integer, default=0)
    occupied_houses = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    coordinates = db.Column(db.String(200))  # JSON con lat/lng
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_coordinates_dict(self):
        """Obtener coordenadas como diccionario"""
        import json
        if self.coordinates:
            return json.loads(self.coordinates)
        return {}
    
    def set_coordinates(self, lat, lng):
        """Establecer coordenadas"""
        import json
        self.coordinates = json.dumps({'lat': lat, 'lng': lng})
    
    def get_occupancy_rate(self):
        """Obtener tasa de ocupación"""
        if self.total_houses > 0:
            return (self.occupied_houses / self.total_houses) * 100
        return 0

class ChatbotSession(db.Model):
    """Modelo de sesiones del chatbot"""
    __tablename__ = 'chatbot_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    context = db.Column(db.Text)  # JSON con contexto de la conversación
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con usuario
    user = db.relationship('User')
    
    def get_context_dict(self):
        """Obtener contexto como diccionario"""
        import json
        if self.context:
            return json.loads(self.context)
        return {}
    
    def set_context(self, context_dict):
        """Establecer contexto"""
        import json
        self.context = json.dumps(context_dict)
    
    def update_context(self, key, value):
        """Actualizar contexto"""
        context = self.get_context_dict()
        context[key] = value
        self.set_context(context) 