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
            flash('Error al crear la cuenta. Inténtalo nuevamente.', 'error')
    
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
            # Aquí iría la lógica para enviar email de recuperación
            flash('Si el email existe, recibirás instrucciones para recuperar tu contraseña.', 'info')
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
            flash('Error al actualizar la contraseña', 'error')
    
    return render_template('auth/change_password.html', form=form)