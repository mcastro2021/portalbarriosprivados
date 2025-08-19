from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('map', __name__, url_prefix='/map')

@bp.route('/')
@login_required
def index():
    """Mapa principal del barrio"""
    return render_template('map.html')

@bp.route('/interactive')
def interactive():
    """Mapa interactivo avanzado con 3D"""
    return render_template('interactive_map.html')
