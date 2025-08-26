from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import db, User, Visit, Reservation, Maintenance, News, Expense, SecurityReport

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Página principal"""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/home')
@login_required
def home():
    """Página de inicio para usuarios autenticados"""
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('main.dashboard'))

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard general para usuarios residentes"""
    # Fechas para cálculos
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_month = today.replace(day=1)
    
    # Estadísticas específicas del usuario
    user_stats = {
        'total_residents': User.query.filter_by(is_active=True, role='resident').count(),
        'active_reservations': Reservation.query.filter_by(user_id=current_user.id, status='active').count(),
        'pending_maintenance': Maintenance.query.filter_by(user_id=current_user.id, status='pending').count(),
        'today_visits': Visit.query.filter_by(resident_id=current_user.id).filter(Visit.created_at >= today).count(),
        'monthly_visits': Visit.query.filter_by(resident_id=current_user.id).filter(Visit.created_at >= start_of_month).count(),
        'monthly_reservations': Reservation.query.filter_by(user_id=current_user.id).filter(Reservation.created_at >= start_of_month).count(),
        'pending_expenses': Expense.query.filter_by(status='pending').count() if hasattr(Expense, 'status') else 0
    }
    
    # Actividad reciente del usuario
    recent_visits = Visit.query.filter_by(resident_id=current_user.id).order_by(Visit.created_at.desc()).limit(5).all()
    recent_reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.created_at.desc()).limit(5).all()
    recent_maintenance = Maintenance.query.filter_by(user_id=current_user.id).order_by(Maintenance.created_at.desc()).limit(5).all()
    
    # Noticias recientes
    recent_news = News.query.filter_by(is_published=True).order_by(News.created_at.desc()).limit(3).all()
    
    return render_template('dashboard.html', 
                         stats=user_stats,
                         recent_visits=recent_visits,
                         recent_reservations=recent_reservations,
                         recent_maintenance=recent_maintenance,
                         recent_news=recent_news,
                         current_datetime=datetime.utcnow())
