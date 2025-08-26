#!/usr/bin/env python3
"""
Script para instalar dependencias faltantes de las fases 1-6
"""

import subprocess
import sys
import os
from typing import List, Dict

def run_command(command: List[str]) -> bool:
    """Ejecutar comando y retornar éxito/fallo"""
    try:
        print(f"🔄 Ejecutando: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ Comando exitoso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando comando: {e}")
        print(f"   Salida: {e.stdout}")
        print(f"   Error: {e.stderr}")
        return False

def install_dependencies():
    """Instalar todas las dependencias de las fases 1-6"""
    
    print("🚀 Instalando dependencias para Fases 1-6")
    print("=" * 50)
    
    # Dependencias principales
    main_deps = [
        "numpy==1.24.3",
        "pandas==2.0.3",
        "matplotlib==3.7.2",
        "seaborn==0.12.2",
        "scikit-learn==1.3.0"
    ]
    
    # Dependencias de integración externa
    external_deps = [
        "googlemaps==4.10.0",
        "geopy==2.3.0",
        "stripe==6.6.0",
        "paypalrestsdk==1.13.1",
        "sendgrid==6.10.0",
        "boto3==1.28.44"
    ]
    
    # Dependencias de escalabilidad
    scalability_deps = [
        "docker==6.1.3"
    ]
    
    # Dependencias opcionales
    optional_deps = [
        "openweathermap==0.1.0"
    ]
    
    all_deps = main_deps + external_deps + scalability_deps + optional_deps
    
    print("📦 Instalando dependencias principales...")
    for dep in main_deps:
        if not run_command([sys.executable, "-m", "pip", "install", dep]):
            print(f"⚠️ No se pudo instalar {dep}")
    
    print("\n🌐 Instalando dependencias de integración externa...")
    for dep in external_deps:
        if not run_command([sys.executable, "-m", "pip", "install", dep]):
            print(f"⚠️ No se pudo instalar {dep}")
    
    print("\n🐳 Instalando dependencias de escalabilidad...")
    for dep in scalability_deps:
        if not run_command([sys.executable, "-m", "pip", "install", dep]):
            print(f"⚠️ No se pudo instalar {dep}")
    
    print("\n🔧 Instalando dependencias opcionales...")
    for dep in optional_deps:
        if not run_command([sys.executable, "-m", "pip", "install", dep]):
            print(f"⚠️ No se pudo instalar {dep}")
    
    print("\n✅ Instalación completada")
    print("\n📋 Para verificar las dependencias instaladas, ejecuta:")
    print("   python -c \"from optional_dependencies import show_dependencies_status; show_dependencies_status()\"")

def verify_installation():
    """Verificar que las dependencias se instalaron correctamente"""
    print("\n🔍 Verificando instalación...")
    
    try:
        from optional_dependencies import show_dependencies_status
        status = show_dependencies_status()
        
        print("\n📊 Estado de dependencias:")
        for dep, available in status.items():
            icon = "✅" if available else "❌"
            print(f"  {icon} {dep}")
        
        missing = [dep for dep, available in status.items() if not available]
        if missing:
            print(f"\n⚠️ Dependencias faltantes: {', '.join(missing)}")
            print("   Ejecuta este script nuevamente para instalarlas")
        else:
            print("\n🎉 ¡Todas las dependencias están instaladas!")
            
    except ImportError as e:
        print(f"❌ Error verificando dependencias: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_installation()
    else:
        install_dependencies()
        verify_installation()
