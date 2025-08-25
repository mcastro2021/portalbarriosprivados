#!/usr/bin/env python3
"""
WSGI entry point para Gunicorn
Archivo separado para evitar problemas de importación
"""

import os
import sys
import traceback

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

def create_application():
    """Crear aplicación Flask de forma segura"""
    try:
        print("🔄 Iniciando creación de aplicación WSGI...")
        
        # Intentar importar la aplicación existente primero
        try:
            from app import app as existing_app
            if existing_app:
                print("✅ Aplicación existente encontrada en app.py")
                return existing_app
        except (ImportError, AttributeError) as e:
            print(f"ℹ️ No se pudo importar app existente: {e}")
        
        # Si no existe, crear usando create_app
        try:
            from app import create_app
            config_name = os.environ.get('FLASK_ENV', 'production')
            application = create_app(config_name)
            print("✅ Aplicación Flask creada usando create_app()")
            return application
        except Exception as e:
            print(f"⚠️ Error con create_app: {e}")
        
        # Último intento: importar cualquier objeto Flask del módulo app
        try:
            import app as app_module
            for attr_name in dir(app_module):
                attr = getattr(app_module, attr_name)
                if hasattr(attr, 'wsgi_app'):  # Es una aplicación Flask
                    print(f"✅ Aplicación Flask encontrada como {attr_name}")
                    return attr
        except Exception as e:
            print(f"⚠️ Error buscando aplicación Flask: {e}")
        
        raise Exception("No se pudo encontrar ninguna aplicación Flask válida")
        
    except Exception as e:
        print(f"❌ Error crítico creando aplicación Flask:")
        print(f"Error: {str(e)}")
        print("Traceback completo:")
        traceback.print_exc()
        
        # Crear aplicación mínima de fallback
        try:
            from flask import Flask, jsonify
            
            fallback_app = Flask(__name__)
            fallback_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key')
            
            @fallback_app.route('/')
            def index():
                return jsonify({
                    'status': 'error',
                    'message': 'Aplicación en modo fallback',
                    'error': str(e),
                    'help': 'Revisa los logs para más detalles'
                })
            
            @fallback_app.route('/health')
            def health_check():
                return jsonify({
                    'status': 'unhealthy',
                    'message': 'Aplicación principal falló',
                    'error': str(e),
                    'fallback': True
                })
            
            @fallback_app.errorhandler(404)
            def not_found(error):
                return jsonify({
                    'status': 'error',
                    'message': 'Endpoint no encontrado',
                    'fallback_mode': True
                }), 404
            
            @fallback_app.errorhandler(500)
            def internal_error(error):
                return jsonify({
                    'status': 'error',
                    'message': 'Error interno del servidor',
                    'fallback_mode': True
                }), 500
            
            print("⚠️ Usando aplicación de fallback completa")
            return fallback_app
            
        except Exception as fallback_error:
            print(f"💥 Error crítico creando fallback: {fallback_error}")
            # Último recurso: aplicación mínima sin dependencias
            class MinimalWSGI:
                def __call__(self, environ, start_response):
                    status = '500 Internal Server Error'
                    headers = [('Content-Type', 'application/json')]
                    start_response(status, headers)
                    return [b'{"error": "Critical application failure", "status": "failed"}']
            
            return MinimalWSGI()

# Crear la aplicación
print("🚀 Iniciando WSGI...")
application = create_application()

# Alias para compatibilidad
app = application

# Verificar que la aplicación es válida
if hasattr(application, 'wsgi_app') or callable(application):
    print("✅ Aplicación WSGI válida creada")
else:
    print("⚠️ Aplicación creada pero podría no ser válida para WSGI")

if __name__ == "__main__":
    if hasattr(application, 'run'):
        application.run(debug=False, host='0.0.0.0', port=5000)
    else:
        print("❌ No se puede ejecutar directamente - usar con Gunicorn")
