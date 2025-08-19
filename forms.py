from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, IntegerField, FloatField, DateField, TimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Nombre completo', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repetir contraseña', validators=[DataRequired(), EqualTo('password')])
    address = StringField('Dirección', validators=[Optional(), Length(max=200)])
    phone = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    emergency_contact = StringField('Contacto de emergencia', validators=[Optional(), Length(max=200)])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Contraseña actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Repetir nueva contraseña', validators=[DataRequired(), EqualTo('new_password')])

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

class VisitForm(FlaskForm):
    visitor_name = StringField('Nombre del visitante', validators=[DataRequired(), Length(max=100)])
    visitor_phone = StringField('Teléfono del visitante', validators=[Optional(), Length(max=20)])
    visitor_document = StringField('Documento del visitante', validators=[Optional(), Length(max=20)])
    vehicle_plate = StringField('Patente del vehículo', validators=[Optional(), Length(max=20)])
    visit_purpose = StringField('Motivo de la visita', validators=[Optional(), Length(max=200)])
    estimated_duration = IntegerField('Duración estimada (horas)', validators=[Optional(), NumberRange(min=1, max=24)], default=1)
    notes = TextAreaField('Notas adicionales', validators=[Optional()])
    notify_security = BooleanField('Notificar a seguridad', default=True)

class ReservationForm(FlaskForm):
    space_type = SelectField('Tipo de espacio', validators=[DataRequired()], choices=[
        ('quincho_1', 'Quincho Principal'),
        ('quincho_2', 'Quincho Pequeño'),
        ('sum', 'SUM (Salón de Usos Múltiples)'),
        ('cancha_futbol', 'Cancha de Fútbol'),
        ('cancha_tenis', 'Cancha de Tenis'),
        ('piscina', 'Piscina'),
        ('coworking', 'Espacio Coworking')
    ])
    start_date = DateField('Fecha de inicio', validators=[DataRequired()])
    start_time = TimeField('Hora de inicio', validators=[DataRequired()])
    end_time = TimeField('Hora de fin', validators=[DataRequired()])
    guests_count = IntegerField('Número de invitados', validators=[Optional(), NumberRange(min=1, max=200)], default=1)
    event_type = StringField('Tipo de evento', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Descripción del evento', validators=[Optional()])

class MaintenanceForm(FlaskForm):
    title = StringField('Título del reclamo', validators=[DataRequired(), Length(max=200)])
    category = SelectField('Categoría', validators=[Optional()], choices=[
        ('plomeria', 'Plomería'),
        ('electricidad', 'Electricidad'),
        ('jardineria', 'Jardinería'),
        ('limpieza', 'Limpieza'),
        ('seguridad', 'Seguridad'),
        ('espacios_comunes', 'Espacios Comunes'),
        ('otros', 'Otros')
    ])
    description = TextAreaField('Descripción detallada', validators=[DataRequired()], widget=TextArea())
    location = StringField('Ubicación', validators=[Optional(), Length(max=200)])
    priority = SelectField('Prioridad', validators=[Optional()], choices=[
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente')
    ], default='medium')
    contact_phone = StringField('Teléfono de contacto', validators=[Optional(), Length(max=20)])
    preferred_time = StringField('Horario preferido', validators=[Optional(), Length(max=100)])
    urgent_access = BooleanField('Requiere acceso urgente')

class ClassifiedForm(FlaskForm):
    title = StringField('Título del anuncio', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Descripción', validators=[DataRequired()], widget=TextArea())
    category = SelectField('Categoría', validators=[Optional()], choices=[
        ('compra_venta', 'Compra/Venta'),
        ('servicios', 'Servicios'),
        ('eventos', 'Eventos'),
        ('alquiler', 'Alquiler'),
        ('empleo', 'Empleo'),
        ('mascotas', 'Mascotas'),
        ('otros', 'Otros')
    ])
    price = FloatField('Precio', validators=[Optional(), NumberRange(min=0)])
    condition = SelectField('Estado', validators=[Optional()], choices=[
        ('nuevo', 'Nuevo'),
        ('usado_excelente', 'Usado - Excelente'),
        ('usado_bueno', 'Usado - Bueno'),
        ('usado_regular', 'Usado - Regular'),
        ('para_reparar', 'Para reparar')
    ])
    contact_name = StringField('Nombre de contacto', validators=[Optional(), Length(max=100)])
    contact_phone = StringField('Teléfono de contacto', validators=[Optional(), Length(max=20)])
    contact_email = StringField('Email de contacto', validators=[Optional(), Email()])
    location = StringField('Ubicación', validators=[Optional(), Length(max=200)])
    tags = StringField('Etiquetas (separadas por comas)', validators=[Optional(), Length(max=200)])

class SecurityReportForm(FlaskForm):
    title = StringField('Título del reporte', validators=[DataRequired(), Length(max=200)])
    incident_type = SelectField('Tipo de incidente', validators=[DataRequired()], choices=[
        ('robo', 'Robo'),
        ('vandalismo', 'Vandalismo'),
        ('persona_sospechosa', 'Persona sospechosa'),
        ('vehiculo_sospechoso', 'Vehículo sospechoso'),
        ('ruidos_molestos', 'Ruidos molestos'),
        ('emergencia_medica', 'Emergencia médica'),
        ('incendio', 'Incendio'),
        ('otros', 'Otros')
    ])
    description = TextAreaField('Descripción del incidente', validators=[DataRequired()], widget=TextArea())
    location = StringField('Ubicación del incidente', validators=[Optional(), Length(max=200)])
    severity = SelectField('Severidad', validators=[Optional()], choices=[
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica')
    ], default='medium')
    incident_date = DateField('Fecha del incidente', validators=[Optional()])
    incident_time = TimeField('Hora del incidente', validators=[Optional()])
    witnesses = TextAreaField('Testigos', validators=[Optional()])
    suspects = TextAreaField('Sospechosos', validators=[Optional()])
    contact_phone = StringField('Teléfono de contacto', validators=[Optional(), Length(max=20)])
    emergency_contact = StringField('Contacto de emergencia', validators=[Optional(), Length(max=200)])
    anonymous = BooleanField('Reporte anónimo')

class NewsForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Contenido', validators=[DataRequired()], widget=TextArea())
    category = SelectField('Categoría', validators=[Optional()], choices=[
        ('general', 'General'),
        ('mantenimiento', 'Mantenimiento'),
        ('seguridad', 'Seguridad'),
        ('eventos', 'Eventos'),
        ('obras', 'Obras'),
        ('cortes', 'Cortes de servicios'),
        ('emergencias', 'Emergencias'),
        ('anuncios', 'Anuncios')
    ])
    is_important = BooleanField('Noticia importante')
    is_published = BooleanField('Publicar inmediatamente', default=True)