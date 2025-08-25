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

# Asegurar que el directorio app/ no interfiera con las importaciones
# Agregar el directorio actual al principio del path para priorizar archivos locales
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))

def create_application():
    """Crear aplicación Flask de forma segura"""
    try:
        print("🔄 Iniciando creación de aplicación WSGI...")
        
        # Configurar variables de entorno críticas
        if not os.environ.get('FLASK_ENV'):
            os.environ['FLASK_ENV'] = 'production'
        if not os.environ.get('SECRET_KEY'):
            os.environ['SECRET_KEY'] = 'fallback-secret-key-for-production'
        
        # Intentar importar la aplicación existente primero
        try:
            from main import app as existing_app
            if existing_app and hasattr(existing_app, 'wsgi_app'):
                print("✅ Aplicación existente encontrada en main.py")
                return existing_app
        except (ImportError, AttributeError) as e:
            print(f"ℹ️ No se pudo importar app existente: {e}")
        
        # Si no existe, crear usando create_app
        try:
            from main import create_app
            config_name = os.environ.get('FLASK_ENV', 'production')
            application = create_app(config_name)
            print("✅ Aplicación Flask creada usando create_app()")
            return application
        except Exception as e:
            print(f"⚠️ Error con create_app: {e}")
            import traceback
            traceback.print_exc()
        
        # Último intento: importar cualquier objeto Flask del módulo main
        try:
            import main as main_module
            for attr_name in dir(main_module):
                attr = getattr(main_module, attr_name)
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
                        'error': 'Application failed to load',
                        'help': 'Revisa los logs para más detalles'
                    })
            
                            @fallback_app.route('/health')
                def health_check():
                    return jsonify({
                        'status': 'unhealthy',
                        'message': 'Aplicación principal falló',
                        'error': 'Application failed to load',
                        'fallback': True
                    })
            
                            @fallback_app.route('/diagnostic')
                def diagnostic():
                    return jsonify({
                        'status': 'wsgi_fallback_diagnostic',
                        'message': 'WSGI fallback mode active',
                        'error': 'Application failed to load',
                        'python_path': sys.path,
                        'current_dir': os.getcwd(),
                        'files_in_dir': os.listdir('.'),
                        'wsgi_mode': True
                    })
            
                            @fallback_app.route('/auth/login', methods=['GET', 'POST'])
                def fallback_login():
                    return jsonify({
                        'status': 'error',
                        'message': 'Login endpoint not available in WSGI fallback mode',
                        'error': 'Application failed to load',
                        'wsgi_fallback': True
                    }), 500
            
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
try:
    application = create_application()
    
    # Alias para compatibilidad
    app = application
    
    # Verificar que la aplicación es válida
    if hasattr(application, 'wsgi_app') or callable(application):
        print("✅ Aplicación WSGI válida creada")
        print(f"✅ Tipo de aplicación: {type(application)}")
    else:
        print("⚠️ Aplicación creada pero podría no ser válida para WSGI")
        
except Exception as e:
    print(f"❌ Error crítico creando aplicación WSGI: {e}")
    import traceback
    traceback.print_exc()
    
    # Crear aplicación de fallback mínima
    class FallbackApp:
        def __init__(self):
            self.wsgi_app = self
            
        def __call__(self, environ, start_response):
            status = '500 Internal Server Error'
            headers = [('Content-Type', 'application/json')]
            start_response(status, headers)
            return [b'{"error": "Application failed to start", "status": "error"}']
    
    application = FallbackApp()
    app = application
    print("⚠️ Usando aplicación de fallback")

if __name__ == "__main__":
    if hasattr(application, 'run'):
        application.run(debug=False, host='0.0.0.0', port=5000)
    else:
        print("❌ No se puede ejecutar directamente - usar con Gunicorn")
