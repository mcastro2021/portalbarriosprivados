#!/usr/bin/env python3
"""
Script para limpiar usuarios de ejemplo y verificar que no se creen automáticamente
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def cleanup_demo_users():
    """Limpiar usuarios de ejemplo del sistema"""
    try:
        from main import create_app
        from models import db, User
        
        app = create_app()
        
        with app.app_context():
            print("🔍 Verificando usuarios en el sistema...")
            
            # Lista de usuarios de ejemplo que no deben existir
            demo_users = [
                'Juan Pérez',
                'María González', 
                'Carlos Rodríguez',
                'Roberto García',
                'testuser',
                'demo_user',
                'sample_user'
            ]
            
            # Buscar usuarios que coincidan con los nombres de ejemplo
            users_to_remove = []
            
            for demo_name in demo_users:
                # Buscar por nombre completo
                users = User.query.filter(User.name.contains(demo_name)).all()
                users_to_remove.extend(users)
                
                # Buscar por username que contenga parte del nombre
                username_parts = demo_name.lower().split()
                for part in username_parts:
                    users = User.query.filter(User.username.contains(part)).all()
                    users_to_remove.extend(users)
            
            # Eliminar duplicados
            users_to_remove = list(set(users_to_remove))
            
            # Filtrar para no eliminar el admin
            users_to_remove = [u for u in users_to_remove if u.username != 'admin']
            
            if users_to_remove:
                print(f"⚠️ Encontrados {len(users_to_remove)} usuarios de ejemplo:")
                for user in users_to_remove:
                    print(f"   - {user.name} ({user.username}) - {user.email}")
                
                confirm = input("¿Desea eliminar estos usuarios? (escriba 'SI' para confirmar): ")
                if confirm == 'SI':
                    for user in users_to_remove:
                        db.session.delete(user)
                        print(f"🗑️ Eliminado: {user.name}")
                    
                    db.session.commit()
                    print(f"✅ {len(users_to_remove)} usuarios de ejemplo eliminados")
                else:
                    print("❌ Operación cancelada")
            else:
                print("✅ No se encontraron usuarios de ejemplo")
            
            # Mostrar usuarios restantes
            all_users = User.query.all()
            print(f"\n📊 Usuarios en el sistema: {len(all_users)}")
            for user in all_users:
                print(f"   - {user.name} ({user.username}) - {user.role}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error limpiando usuarios: {e}")
        return False

def verify_no_auto_creation():
    """Verificar que no se creen usuarios automáticamente"""
    print("\n🔍 Verificando scripts de inicialización...")
    
    # Archivos a verificar
    files_to_check = [
        'main.py',
        'init_db.py', 
        'reset_db.py',
        'improved_setup.py'
    ]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            print(f"\n📄 Verificando {filename}:")
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Buscar patrones que podrían crear usuarios automáticamente
                patterns = [
                    'User(',
                    'User.create',
                    'User.add',
                    'create_sample_data',
                    'create_demo_users',
                    'create_sample_users'
                ]
                
                for pattern in patterns:
                    if pattern in content:
                        print(f"   ⚠️ Encontrado patrón: {pattern}")
                    else:
                        print(f"   ✅ No se encontró: {pattern}")
                        
            except Exception as e:
                print(f"   ❌ Error leyendo archivo: {e}")
        else:
            print(f"   ℹ️ Archivo no encontrado: {filename}")
    
    print("\n✅ Verificación completada")

def main():
    """Función principal"""
    print("🧹 Script de limpieza de usuarios de ejemplo")
    print("=" * 50)
    
    # Limpiar usuarios de ejemplo
    success = cleanup_demo_users()
    
    if success:
        # Verificar que no se creen automáticamente
        verify_no_auto_creation()
        
        print("\n🎉 Proceso completado")
        print("\n📋 Recomendaciones:")
        print("1. Solo el usuario 'admin' debe crearse automáticamente")
        print("2. Los demás usuarios deben crearse manualmente por el administrador")
        print("3. No usar datos de ejemplo en producción")
    else:
        print("❌ Error en el proceso")

if __name__ == "__main__":
    main()
