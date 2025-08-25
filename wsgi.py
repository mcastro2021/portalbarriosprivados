#!/usr/bin/env python3
"""
WSGI entry point para Gunicorn
Archivo separado para evitar problemas de importación
"""

import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

def create_application():
    """Crear aplicación Flask de forma segura"""
    try:
        # Importar y crear la aplicación
        from app import create_app
        
        # Usar configuración de producción
        config_name = os.environ.get('FLASK_ENV', 'production')
        application = create_app(config_name)
        
        print("✅ Aplicación Flask creada correctamente para WSGI")
        return application
        
    except Exception as e:
        print(f"❌ Error creando aplicación Flask: {e}")
        
        # Crear aplicación mínima de fallback
        from flask import Flask, jsonify
        
        fallback_app = Flask(__name__)
        
        @fallback_app.route('/')
        def health():
            return jsonify({
                'status': 'error',
                'message': 'Error en la aplicación principal',
                'error': str(e)
            })
        
        @fallback_app.route('/health')
        def health_check():
            return jsonify({
                'status': 'error',
                'message': 'Aplicación en modo fallback',
                'error': str(e)
            })
        
        print("⚠️ Usando aplicación de fallback")
        return fallback_app

# Crear la aplicación
application = create_application()

# Alias para compatibilidad
app = application

if __name__ == "__main__":
    application.run(debug=False, host='0.0.0.0', port=5000)
