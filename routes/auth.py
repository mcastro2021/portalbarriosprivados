from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from forms import LoginForm, RegistrationForm, ChangePasswordForm, ForgotPasswordForm
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember_me.data
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'error')
                return render_template('auth/login.html', form=form)
            
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Redirigir a la página solicitada o al dashboard
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard')
            
            flash(f'¡Bienvenido, {user.name}!', 'success')
            return redirect(next_page)
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=form.username.data).first():
            flash('El nombre de usuario ya está en uso', 'error')
            return render_template('auth/register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('El email ya está registrado', 'error')
            return render_template('auth/register.html', form=form)
        
        try:
            # Crear nuevo usuario
            user = User(
                username=form.username.data,
                email=form.email.data,
                name=form.name.data,
                address=form.address.data,
                phone=form.phone.data,
                emergency_contact=form.emergency_contact.data,
                role='resident',  # Por defecto todos son residentes
                is_active=True,
                email_verified=False
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            # Log del error para debugging
            print(f"Error en registro: {str(e)}")
            flash(f'Error al crear la cuenta: {str(e)}', 'error')
    
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('index'))

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Página de recuperación de contraseña"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generar token de recuperación (temporal - para desarrollo)
            import secrets
            reset_token = secrets.token_urlsafe(32)
            
            # En desarrollo, mostramos el token directamente
            # En producción, esto se enviaría por email
            flash(f'Token de recuperación para {user.username}: {reset_token}', 'info')
            flash('Guarda este token y úsalo para cambiar tu contraseña.', 'warning')
            
            # Aquí normalmente se guardaría el token en la BD y se enviaría por email
            # Para este demo, redirigimos con el token
            return redirect(url_for('auth.reset_password', token=reset_token, user_id=user.id))
        else:
            flash('Si el email existe, recibirás instrucciones para recuperar tu contraseña.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Cambiar contraseña"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('La contraseña actual es incorrecta', 'error')
            return render_template('auth/change_password.html', form=form)
        
        try:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Contraseña actualizada correctamente', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            print(f"Error al cambiar contraseña: {str(e)}")
            flash('Error al actualizar la contraseña', 'error')
    
    return render_template('auth/change_password.html', form=form)

@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Resetear contraseña con token"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    token = request.args.get('token')
    user_id = request.args.get('user_id', type=int)
    
    if not token or not user_id:
        flash('Token de recuperación inválido', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or len(new_password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
        elif new_password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
        else:
            try:
                user.set_password(new_password)
                db.session.commit()
                flash('Contraseña actualizada correctamente. Ya puedes iniciar sesión.', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                flash('Error al actualizar la contraseña', 'error')
    
    return render_template('auth/reset_password.html', user=user, token=token)

@bp.route('/admin-reset-user/<username>')
@login_required
def admin_reset_user(username):
    """Función de administrador para resetear contraseña de usuario (solo para desarrollo)"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para esta acción', 'error')
        return redirect(url_for('dashboard'))
    
    user = User.query.filter_by(username=username).first()
    if not user:
        flash(f'Usuario {username} no encontrado', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Contraseña temporal para desarrollo
    temp_password = 'temp123456'
    user.set_password(temp_password)
    db.session.commit()
    
    flash(f'Contraseña de {username} resetada a: {temp_password}', 'success')
    flash('El usuario debe cambiar esta contraseña al iniciar sesión', 'warning')
    
    return redirect(url_for('admin.dashboard'))

@bp.route('/debug-user/<username>')
@login_required
def debug_user(username):
    """Función de debug para verificar estado del usuario"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para esta acción', 'error')
        return redirect(url_for('dashboard'))
    
    user = User.query.filter_by(username=username).first()
    if not user:
        flash(f'Usuario {username} no encontrado', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Información de debug
    debug_info = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'name': user.name,
        'role': user.role,
        'is_active': user.is_active,
        'email_verified': user.email_verified,
        'created_at': user.created_at,
        'last_login': user.last_login,
        'address': user.address,
        'phone': user.phone,
        'has_password_hash': bool(user.password_hash),
        'password_hash_length': len(user.password_hash) if user.password_hash else 0
    }
    
    # Test de contraseña común
    common_passwords = ['password', 'admin123', 'temp123456', '123456', username, 'mcastro2025']
    working_passwords = []
    
    for pwd in common_passwords:
        if user.check_password(pwd):
            working_passwords.append(pwd)
    
    flash(f'Información de usuario {username}:', 'info')
    for key, value in debug_info.items():
        flash(f'{key}: {value}', 'info')
    
    if working_passwords:
        flash(f'Contraseñas que funcionan: {", ".join(working_passwords)}', 'success')
    else:
        flash('Ninguna contraseña común funciona', 'warning')
    
    return redirect(url_for('admin.dashboard'))