"""
WSGI entry point for the application.
This file is used by gunicorn and other WSGI servers.
"""

import os
from app import create_app

# Crear la aplicación con configuración de producción
app = create_app('production')

if __name__ == "__main__":
    app.run()
