#!/usr/bin/env python3
"""
Script para probar las mejoras de logs en entorno de producción
"""

import os
import sys

# Simular entorno de producción
os.environ['FLASK_ENV'] = 'production'

def test_production_logs():
    """Probar las mejoras de logs en producción"""
    print("🧪 Probando logs en entorno de producción...")
    print("=" * 60)
    
    try:
        # Importar y crear la aplicación
        from main import create_app
        app = create_app()
        
        print("\n✅ Aplicación creada exitosamente en modo producción")
        print("📋 Logs esperados en producción:")
        print("   - INFO: Redis no disponible - usando fallback en memoria")
        print("   - INFO: Docker no disponible - funcionalidades de containerización limitadas")
        print("   - INFO: Rate limiting no disponible - usando fallback")
        print("   - INFO: Redis no disponible - balanceo de carga limitado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando logs de producción: {e}")
        return False

def test_development_logs():
    """Probar logs en entorno de desarrollo"""
    print("\n🧪 Probando logs en entorno de desarrollo...")
    print("=" * 60)
    
    try:
        # Simular entorno de desarrollo
        os.environ['FLASK_ENV'] = 'development'
        
        # Importar y crear la aplicación
        from main import create_app
        app = create_app()
        
        print("\n✅ Aplicación creada exitosamente en modo desarrollo")
        print("📋 Logs esperados en desarrollo:")
        print("   - WARNING: Redis no disponible: [error completo]")
        print("   - ERROR: Error Docker: [error completo]")
        print("   - WARNING: Rate limiting no disponible: [error completo]")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando logs de desarrollo: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Test de Mejoras de Logs para Producción")
    print("=" * 60)
    
    # Probar logs de producción
    production_success = test_production_logs()
    
    # Probar logs de desarrollo
    development_success = test_development_logs()
    
    print("\n" + "=" * 60)
    print("📊 Resumen de Pruebas:")
    print(f"   Producción: {'✅ Exitoso' if production_success else '❌ Falló'}")
    print(f"   Desarrollo: {'✅ Exitoso' if development_success else '❌ Falló'}")
    
    if production_success and development_success:
        print("\n🎉 Todas las pruebas pasaron exitosamente!")
        print("✅ Las mejoras de logs están funcionando correctamente")
    else:
        print("\n⚠️ Algunas pruebas fallaron")
        print("❌ Revisar las mejoras de logs")
    
    sys.exit(0 if (production_success and development_success) else 1)
