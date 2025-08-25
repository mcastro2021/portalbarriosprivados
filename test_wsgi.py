#!/usr/bin/env python3
"""
Script para probar la configuración WSGI localmente
"""

import sys
import os

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

def test_wsgi_import():
    """Probar importación de WSGI"""
    print("🧪 Probando configuración WSGI...")
    
    try:
        # Probar importación del módulo wsgi
        print("1. Importando módulo wsgi...")
        import wsgi
        print("   ✅ Módulo wsgi importado correctamente")
        
        # Probar acceso a la aplicación
        print("2. Verificando aplicación...")
        if hasattr(wsgi, 'application'):
            app = wsgi.application
            print("   ✅ wsgi.application encontrada")
            
            # Verificar que es una aplicación Flask válida
            if hasattr(app, 'wsgi_app'):
                print("   ✅ Es una aplicación Flask válida")
                
                # Probar configuración básica
                print("3. Verificando configuración...")
                print(f"   - Nombre de la app: {app.name}")
                print(f"   - Debug mode: {app.debug}")
                print(f"   - Testing mode: {app.testing}")
                
                # Probar context de aplicación
                print("4. Probando contexto de aplicación...")
                with app.app_context():
                    print("   ✅ Contexto de aplicación funciona")
                
                # Probar request básico
                print("5. Probando request de prueba...")
                with app.test_client() as client:
                    response = client.get('/health')
                    print(f"   - Status code: {response.status_code}")
                    print(f"   - Content type: {response.content_type}")
                    if response.status_code == 200:
                        print("   ✅ Endpoint /health responde correctamente")
                    else:
                        print("   ⚠️ Endpoint /health no responde como esperado")
                
                print("\n🎉 Configuración WSGI parece estar correcta!")
                return True
                
            else:
                print("   ❌ No es una aplicación Flask válida")
                return False
        else:
            print("   ❌ wsgi.application no encontrada")
            return False
            
    except ImportError as e:
        print(f"   ❌ Error importando wsgi: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_import():
    """Probar importación directa de app.py"""
    print("\n🧪 Probando importación directa de app.py...")
    
    try:
        # Probar importación de create_app
        print("1. Importando create_app...")
        from app import create_app
        print("   ✅ create_app importada correctamente")
        
        # Probar creación de aplicación
        print("2. Creando aplicación...")
        app = create_app('production')
        print("   ✅ Aplicación creada correctamente")
        
        # Probar importación de app existente
        print("3. Probando importación de app existente...")
        try:
            from app import app as existing_app
            print("   ✅ App existente encontrada")
        except (ImportError, AttributeError) as e:
            print(f"   ⚠️ App existente no encontrada: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Probar dependencias críticas"""
    print("\n🧪 Probando dependencias críticas...")
    
    critical_deps = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'gunicorn'
    ]
    
    missing_deps = []
    
    for dep in critical_deps:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - FALTANTE")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n⚠️ Dependencias faltantes: {', '.join(missing_deps)}")
        return False
    else:
        print("\n✅ Todas las dependencias críticas están disponibles")
        return True

def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 PRUEBA DE CONFIGURACIÓN WSGI")
    print("=" * 60)
    
    # Probar dependencias
    deps_ok = test_dependencies()
    
    # Probar importación de app
    app_ok = test_app_import()
    
    # Probar configuración WSGI
    wsgi_ok = test_wsgi_import()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"Dependencias: {'✅ OK' if deps_ok else '❌ ERROR'}")
    print(f"App import: {'✅ OK' if app_ok else '❌ ERROR'}")
    print(f"WSGI config: {'✅ OK' if wsgi_ok else '❌ ERROR'}")
    
    if deps_ok and app_ok and wsgi_ok:
        print("\n🎉 ¡Configuración WSGI lista para deployment!")
        print("\nComando para Gunicorn:")
        print("gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120")
        return 0
    else:
        print("\n❌ Hay problemas que necesitan ser resueltos antes del deployment")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
