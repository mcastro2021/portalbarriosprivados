from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Página principal"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/home')
@login_required
def home():
    """Página de inicio para usuarios autenticados"""
    return redirect(url_for('admin.dashboard'))
