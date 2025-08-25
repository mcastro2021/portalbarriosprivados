"""
Utilidades generales para la aplicación
"""

from flask import current_app

def get_csrf_token():
    """Obtener token CSRF o None si está deshabilitado"""
    try:
        if current_app.config.get('WTF_CSRF_ENABLED', False):
            from flask_wtf.csrf import generate_csrf
            return generate_csrf()
        else:
            return None
    except:
        return None

def is_csrf_enabled():
    """Verificar si CSRF está habilitado"""
    return current_app.config.get('WTF_CSRF_ENABLED', False)
