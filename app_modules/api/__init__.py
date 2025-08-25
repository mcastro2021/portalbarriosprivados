"""
API REST para Portal Barrios Privados
"""

from flask import Blueprint
from .v1 import api_v1

# Crear blueprint principal de API
api = Blueprint('api', __name__, url_prefix='/api')

# Registrar versiones de API
api.register_blueprint(api_v1, url_prefix='/v1')

__all__ = ['api']
