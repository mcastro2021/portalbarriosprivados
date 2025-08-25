from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """Obtener estadísticas del dashboard"""
    try:
        from models import Visit, Reservation, Maintenance, Expense
        
        # Estadísticas básicas
        stats = {
            'pending_visits': 0,
            'active_reservations': 0,
            'pending_maintenance': 0,
            'pending_expenses': 0
        }
        
        # Contar visitas pendientes
        try:
            stats['pending_visits'] = Visit.query.filter_by(
                resident_id=current_user.id, 
                status='pending'
            ).count()
        except:
            pass
        
        # Contar reservas activas
        try:
            stats['active_reservations'] = Reservation.query.filter_by(
                user_id=current_user.id, 
                status='approved'
            ).count()
        except:
            pass
        
        # Contar mantenimiento pendiente
        try:
            stats['pending_maintenance'] = Maintenance.query.filter_by(
                user_id=current_user.id, 
                status='pending'
            ).count()
        except:
            pass
        
        # Contar expensas pendientes
        try:
            stats['pending_expenses'] = Expense.query.filter_by(
                user_id=current_user.id, 
                status='pending'
            ).count()
        except:
            pass
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
