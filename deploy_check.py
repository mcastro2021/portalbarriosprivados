#!/usr/bin/env python3
"""
Script de verificación para despliegue en Render.com
Verifica que todos los archivos necesarios estén presentes y configurados correctamente
"""

import os
import sys

def check_files():
    """Verificar que todos los archivos necesarios estén presentes"""
    required_files = [
        'main.py',
        'wsgi.py',
        'requirements.txt',
        'render.yaml',
        'Procfile',
        'config.py',
        'models.py',
        'routes/__init__.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {missing_files}")
        return False
    else:
        print("✅ Todos los archivos requeridos están presentes")
        return True

def check_wsgi_config():
    """Verificar configuración de WSGI"""
    try:
        with open('wsgi.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'app = application' in content:
            print("✅ wsgi.py tiene el alias 'app' configurado")
        else:
            print("⚠️ wsgi.py podría no tener el alias 'app' configurado")
            
        if 'from main import' in content:
            print("✅ wsgi.py importa desde main.py")
        else:
            print("❌ wsgi.py no importa desde main.py")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Error verificando wsgi.py: {e}")
        return False

def check_render_config():
    """Verificar configuración de Render"""
    try:
        with open('render.yaml', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'wsgi:app' in content:
            print("✅ render.yaml usa wsgi:app correctamente")
        else:
            print("❌ render.yaml no usa wsgi:app correctamente")
            return False
            
        if 'FLASK_ENV' in content:
            print("✅ render.yaml tiene FLASK_ENV configurado")
        else:
            print("⚠️ render.yaml podría no tener FLASK_ENV configurado")
            
        return True
    except Exception as e:
        print(f"❌ Error verificando render.yaml: {e}")
        return False

def check_procfile():
    """Verificar Procfile"""
    try:
        with open('Procfile', 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"📄 Contenido del Procfile: '{content.strip()}'")
        
        if 'wsgi:app' in content:
            print("✅ Procfile usa wsgi:app correctamente")
        else:
            print("❌ Procfile no usa wsgi:app correctamente")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Error verificando Procfile: {e}")
        return False

def check_requirements():
    """Verificar requirements.txt"""
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            
        required_packages = ['Flask', 'gunicorn', 'Flask-SQLAlchemy']
        missing_packages = []
        
        for package in required_packages:
            if package not in content:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"⚠️ Paquetes faltantes en requirements.txt: {missing_packages}")
        else:
            print("✅ requirements.txt tiene los paquetes básicos")
            
        return True
    except Exception as e:
        print(f"❌ Error verificando requirements.txt: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🔍 Verificando configuración de despliegue...")
    print("=" * 50)
    
    checks = [
        ("Archivos requeridos", check_files),
        ("Configuración WSGI", check_wsgi_config),
        ("Configuración Render", check_render_config),
        ("Procfile", check_procfile),
        ("Requirements", check_requirements)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n📋 Verificando {check_name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Todas las verificaciones pasaron exitosamente!")
        print("✅ La aplicación está lista para despliegue en Render.com")
        return 0
    else:
        print("❌ Algunas verificaciones fallaron")
        print("⚠️ Revisa los problemas antes de desplegar")
        return 1

if __name__ == "__main__":
    sys.exit(main())
