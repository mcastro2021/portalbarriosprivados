#!/usr/bin/env python3
"""
Test script para verificar que el WSGI entry point funciona correctamente
"""

import os
import sys

def test_wsgi_import():
    """Test para verificar que wsgi.py puede importar la aplicación correctamente"""
    try:
        print("🔄 Probando importación de wsgi...")
        
        # Configurar variables de entorno
        os.environ['FLASK_ENV'] = 'production'
        if not os.environ.get('SECRET_KEY'):
            os.environ['SECRET_KEY'] = 'test-secret-key'
        
        # Intentar importar wsgi
        from wsgi import app
        
        print("✅ wsgi.py importado correctamente")
        
        # Verificar que app es una aplicación Flask válida
        if hasattr(app, 'wsgi_app'):
            print("✅ app tiene wsgi_app - es una aplicación Flask válida")
        else:
            print("⚠️ app no tiene wsgi_app")
            
        # Verificar que app es callable
        if callable(app):
            print("✅ app es callable")
        else:
            print("⚠️ app no es callable")
            
        print("🎉 Test de importación WSGI completado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de importación WSGI: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_direct_import():
    """Test para verificar que app.py puede importarse directamente"""
    try:
        print("🔄 Probando importación directa de app.py...")
        
        # Configurar variables de entorno
        os.environ['FLASK_ENV'] = 'production'
        if not os.environ.get('SECRET_KEY'):
            os.environ['SECRET_KEY'] = 'test-secret-key'
        
        # Intentar importar app directamente
        from main import app
        
        print("✅ main.py importado correctamente")
        
        # Verificar que app es una aplicación Flask válida
        if hasattr(app, 'wsgi_app'):
            print("✅ app tiene wsgi_app - es una aplicación Flask válida")
        else:
            print("⚠️ app no tiene wsgi_app")
            
        print("🎉 Test de importación directa completado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de importación directa: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando tests de importación...")
    
    # Test 1: Importación WSGI
    wsgi_success = test_wsgi_import()
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Importación directa
    direct_success = test_app_direct_import()
    
    print("\n" + "="*50 + "\n")
    
    if wsgi_success and direct_success:
        print("🎉 Todos los tests pasaron exitosamente!")
        sys.exit(0)
    else:
        print("❌ Algunos tests fallaron")
        sys.exit(1)
