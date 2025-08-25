"""
Esquemas de validación usando Marshmallow
Proporciona validación robusta y serialización de datos
"""

from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from marshmallow.decorators import post_load
import re
from datetime import datetime, timedelta

class BaseSchema(Schema):
    """Esquema base con configuraciones comunes"""
    
    class Meta:
        # Incluir campos desconocidos como errores
        unknown = 'EXCLUDE'
        # Ordenar campos por nombre
        ordered = True
    
    @validates_schema
    def validate_schema(self, data, **kwargs):
        """Validaciones personalizadas a nivel de esquema"""
        pass

class UserRegistrationSchema(BaseSchema):
    """Esquema para registro de usuarios"""
    
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=80, error="El nombre de usuario debe tener entre 3 y 80 caracteres"),
            validate.Regexp(r'^[a-zA-Z0-9_]+$', error="Solo se permiten letras, números y guiones bajos")
        ]
    )
    
    email = fields.Email(
        required=True,
        validate=validate.Length(max=120, error="El email no puede exceder 120 caracteres")
    )
    
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=128, error="La contraseña debe tener entre 6 y 128 caracteres")
    )
    
    confirm_password = fields.Str(required=True)
    
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100, error="El nombre debe tener entre 2 y 100 caracteres")
    )
    
    phone = fields.Str(
        allow_none=True,
        validate=validate.Regexp(r'^\+?[\d\s\-\(\)]+$', error="Formato de teléfono inválido")
    )
    
    address = fields.Str(
        allow_none=True,
        validate=validate.Length(max=200, error="La dirección no puede exceder 200 caracteres")
    )
    
    @validates('password')
    def validate_password(self, value):
        """Validar fortaleza de contraseña"""
        if not re.search(r'[A-Za-z]', value):
            raise ValidationError("La contraseña debe contener al menos una letra")
        if not re.search(r'\d', value):
            raise ValidationError("La contraseña debe contener al menos un número")
        if len(set(value)) < 4:
            raise ValidationError("La contraseña debe tener al menos 4 caracteres únicos")
    
    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        """Validar que las contraseñas coincidan"""
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError("Las contraseñas no coinciden", field_name='confirm_password')

class UserUpdateSchema(BaseSchema):
    """Esquema para actualización de usuarios"""
    
    name = fields.Str(
        validate=validate.Length(min=2, max=100, error="El nombre debe tener entre 2 y 100 caracteres")
    )
    
    email = fields.Email(
        validate=validate.Length(max=120, error="El email no puede exceder 120 caracteres")
    )
    
    phone = fields.Str(
        allow_none=True,
        validate=validate.Regexp(r'^\+?[\d\s\-\(\)]+$', error="Formato de teléfono inválido")
    )
    
    address = fields.Str(
        allow_none=True,
        validate=validate.Length(max=200, error="La dirección no puede exceder 200 caracteres")
    )
    
    emergency_contact = fields.Str(
        allow_none=True,
        validate=validate.Length(max=200, error="El contacto de emergencia no puede exceder 200 caracteres")
    )

class LoginSchema(BaseSchema):
    """Esquema para login"""
    
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    two_factor_token = fields.Str(allow_none=True)
    backup_code = fields.Str(allow_none=True)
    remember_me = fields.Bool(missing=False)

class PasswordChangeSchema(BaseSchema):
    """Esquema para cambio de contraseña"""
    
    current_password = fields.Str(required=True)
    new_password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=128, error="La contraseña debe tener entre 6 y 128 caracteres")
    )
    confirm_password = fields.Str(required=True)
    
    @validates('new_password')
    def validate_password(self, value):
        """Validar fortaleza de contraseña"""
        if not re.search(r'[A-Za-z]', value):
            raise ValidationError("La contraseña debe contener al menos una letra")
        if not re.search(r'\d', value):
            raise ValidationError("La contraseña debe contener al menos un número")
    
    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        """Validar que las contraseñas coincidan"""
        if data.get('new_password') != data.get('confirm_password'):
            raise ValidationError("Las contraseñas no coinciden", field_name='confirm_password')

class VisitSchema(BaseSchema):
    """Esquema para visitas"""
    
    visitor_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100, error="El nombre del visitante debe tener entre 2 y 100 caracteres")
    )
    
    visitor_phone = fields.Str(
        allow_none=True,
        validate=validate.Regexp(r'^\+?[\d\s\-\(\)]+$', error="Formato de teléfono inválido")
    )
    
    visitor_document = fields.Str(
        allow_none=True,
        validate=validate.Length(max=20, error="El documento no puede exceder 20 caracteres")
    )
    
    vehicle_plate = fields.Str(
        allow_none=True,
        validate=validate.Length(max=20, error="La patente no puede exceder 20 caracteres")
    )
    
    entry_time = fields.DateTime(allow_none=True)
    estimated_duration = fields.Int(
        validate=validate.Range(min=1, max=24, error="La duración debe estar entre 1 y 24 horas"),
        missing=1
    )
    
    visit_purpose = fields.Str(
        allow_none=True,
        validate=validate.Length(max=200, error="El propósito no puede exceder 200 caracteres")
    )
    
    notes = fields.Str(allow_none=True)
    notify_security = fields.Bool(missing=True)

class ReservationSchema(BaseSchema):
    """Esquema para reservas"""
    
    space_type = fields.Str(
        required=True,
        validate=validate.OneOf([
            'quincho_1', 'quincho_2', 'sum', 'cancha_futbol', 
            'cancha_tenis', 'piscina', 'coworking'
        ], error="Tipo de espacio inválido")
    )
    
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    
    guests_count = fields.Int(
        validate=validate.Range(min=1, max=200, error="El número de invitados debe estar entre 1 y 200"),
        missing=1
    )
    
    event_type = fields.Str(
        allow_none=True,
        validate=validate.Length(max=100, error="El tipo de evento no puede exceder 100 caracteres")
    )
    
    description = fields.Str(allow_none=True)
    
    @validates_schema
    def validate_times(self, data, **kwargs):
        """Validar que las fechas sean coherentes"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError("La hora de fin debe ser posterior a la hora de inicio")
            
            if start_time < datetime.utcnow():
                raise ValidationError("No se pueden hacer reservas en el pasado")
            
            duration = end_time - start_time
            if duration > timedelta(hours=12):
                raise ValidationError("La reserva no puede exceder 12 horas")

class MaintenanceSchema(BaseSchema):
    """Esquema para reclamos de mantenimiento"""
    
    title = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=200, error="El título debe tener entre 5 y 200 caracteres")
    )
    
    category = fields.Str(
        validate=validate.OneOf([
            'plomeria', 'electricidad', 'jardineria', 'limpieza', 
            'seguridad', 'infraestructura', 'otros'
        ], error="Categoría inválida")
    )
    
    description = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=1000, error="La descripción debe tener entre 10 y 1000 caracteres")
    )
    
    location = fields.Str(
        allow_none=True,
        validate=validate.Length(max=200, error="La ubicación no puede exceder 200 caracteres")
    )
    
    priority = fields.Str(
        validate=validate.OneOf(['low', 'medium', 'high', 'urgent'], error="Prioridad inválida"),
        missing='medium'
    )
    
    contact_phone = fields.Str(
        allow_none=True,
        validate=validate.Regexp(r'^\+?[\d\s\-\(\)]+$', error="Formato de teléfono inválido")
    )
    
    preferred_time = fields.Str(
        allow_none=True,
        validate=validate.Length(max=100, error="El horario preferido no puede exceder 100 caracteres")
    )
    
    urgent_access = fields.Bool(missing=False)

class NewsSchema(BaseSchema):
    """Esquema para noticias"""
    
    title = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=200, error="El título debe tener entre 5 y 200 caracteres")
    )
    
    content = fields.Str(
        required=True,
        validate=validate.Length(min=20, error="El contenido debe tener al menos 20 caracteres")
    )
    
    category = fields.Str(
        validate=validate.OneOf([
            'general', 'mantenimiento', 'seguridad', 'eventos', 
            'obras', 'cortes', 'emergencias', 'anuncios'
        ], error="Categoría inválida")
    )
    
    is_important = fields.Bool(missing=False)
    is_published = fields.Bool(missing=True)
    expires_at = fields.DateTime(allow_none=True)
    
    @validates('expires_at')
    def validate_expiry(self, value):
        """Validar fecha de expiración"""
        if value and value <= datetime.utcnow():
            raise ValidationError("La fecha de expiración debe ser futura")

class SecurityReportSchema(BaseSchema):
    """Esquema para reportes de seguridad"""
    
    title = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=200, error="El título debe tener entre 5 y 200 caracteres")
    )
    
    incident_type = fields.Str(
        required=True,
        validate=validate.OneOf([
            'robo', 'vandalismo', 'ruido', 'vehiculo_sospechoso', 
            'persona_sospechosa', 'emergencia', 'otros'
        ], error="Tipo de incidente inválido")
    )
    
    description = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=1000, error="La descripción debe tener entre 10 y 1000 caracteres")
    )
    
    location = fields.Str(
        allow_none=True,
        validate=validate.Length(max=200, error="La ubicación no puede exceder 200 caracteres")
    )
    
    severity = fields.Str(
        validate=validate.OneOf(['low', 'medium', 'high', 'critical'], error="Severidad inválida"),
        missing='medium'
    )
    
    incident_date = fields.Date(allow_none=True)
    incident_time = fields.Time(allow_none=True)
    
    witnesses = fields.Str(allow_none=True)
    suspects = fields.Str(allow_none=True)
    
    contact_phone = fields.Str(
        allow_none=True,
        validate=validate.Regexp(r'^\+?[\d\s\-\(\)]+$', error="Formato de teléfono inválido")
    )
    
    emergency_contact = fields.Str(
        allow_none=True,
        validate=validate.Length(max=200, error="El contacto de emergencia no puede exceder 200 caracteres")
    )
    
    anonymous = fields.Bool(missing=False)
    
    # Campos para reportes anónimos
    reporter_name = fields.Str(
        allow_none=True,
        validate=validate.Length(max=100, error="El nombre no puede exceder 100 caracteres")
    )
    
    reporter_phone = fields.Str(
        allow_none=True,
        validate=validate.Regexp(r'^\+?[\d\s\-\(\)]+$', error="Formato de teléfono inválido")
    )
    
    reporter_email = fields.Email(
        allow_none=True,
        validate=validate.Length(max=120, error="El email no puede exceder 120 caracteres")
    )

class ClassifiedSchema(BaseSchema):
    """Esquema para clasificados"""
    
    title = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=200, error="El título debe tener entre 5 y 200 caracteres")
    )
    
    description = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=1000, error="La descripción debe tener entre 10 y 1000 caracteres")
    )
    
    category = fields.Str(
        validate=validate.OneOf([
            'compra_venta', 'servicios', 'eventos', 'alquiler', 
            'empleo', 'mascotas', 'otros'
        ], error="Categoría inválida")
    )
    
    price = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0, error="El precio debe ser positivo")
    )
    
    condition = fields.Str(
        allow_none=True,
        validate=validate.OneOf(['nuevo', 'usado', 'excelente', 'bueno', 'regular'], error="Condición inválida")
    )
    
    contact_name = fields.Str(
        allow_none=True,
        validate=validate.Length(max=100, error="El nombre de contacto no puede exceder 100 caracteres")
    )
    
    contact_phone = fields.Str(
        allow_none=True,
        validate=validate.Regexp(r'^\+?[\d\s\-\(\)]+$', error="Formato de teléfono inválido")
    )
    
    contact_email = fields.Email(
        allow_none=True,
        validate=validate.Length(max=120, error="El email no puede exceder 120 caracteres")
    )
    
    location = fields.Str(
        allow_none=True,
        validate=validate.Length(max=200, error="La ubicación no puede exceder 200 caracteres")
    )
    
    tags = fields.Str(
        allow_none=True,
        validate=validate.Length(max=200, error="Las etiquetas no pueden exceder 200 caracteres")
    )
    
    expiry_date = fields.DateTime(allow_none=True)
    
    @validates('expiry_date')
    def validate_expiry(self, value):
        """Validar fecha de expiración"""
        if value and value <= datetime.utcnow():
            raise ValidationError("La fecha de expiración debe ser futura")

class TwoFactorSetupSchema(BaseSchema):
    """Esquema para configuración de 2FA"""
    
    secret = fields.Str(required=True)
    verification_token = fields.Str(
        required=True,
        validate=validate.Regexp(r'^\d{6}$', error="El token debe ser de 6 dígitos")
    )

class TwoFactorVerificationSchema(BaseSchema):
    """Esquema para verificación de 2FA"""
    
    token = fields.Str(
        allow_none=True,
        validate=validate.Regexp(r'^\d{6}$', error="El token debe ser de 6 dígitos")
    )
    
    backup_code = fields.Str(
        allow_none=True,
        validate=validate.Regexp(r'^[A-Z0-9]{8}$', error="El código de respaldo debe ser de 8 caracteres")
    )
    
    @validates_schema
    def validate_auth_method(self, data, **kwargs):
        """Validar que se proporcione token o código de respaldo"""
        if not data.get('token') and not data.get('backup_code'):
            raise ValidationError("Se requiere token o código de respaldo")

# Función helper para validar datos
def validate_data(schema_class, data):
    """Validar datos usando un esquema específico"""
    try:
        schema = schema_class()
        result = schema.load(data)
        return {'success': True, 'data': result}
    except ValidationError as e:
        return {'success': False, 'errors': e.messages}

# Decorador para validación automática
def validate_with_schema(schema_class):
    """Decorador para validar datos de request automáticamente"""
    def decorator(f):
        from functools import wraps
        from flask import request, jsonify
        from app.core.error_handler import ValidationError as CustomValidationError
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obtener datos del request
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            # Validar datos
            result = validate_data(schema_class, data)
            
            if not result['success']:
                # Crear error de validación personalizado
                error_messages = []
                for field, messages in result['errors'].items():
                    if isinstance(messages, list):
                        error_messages.extend([f"{field}: {msg}" for msg in messages])
                    else:
                        error_messages.append(f"{field}: {messages}")
                
                raise CustomValidationError("; ".join(error_messages))
            
            # Agregar datos validados al request
            request.validated_data = result['data']
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
