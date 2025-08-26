#!/usr/bin/env python3
"""
Script para eliminar usuarios de ejemplo específicos
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, db
from models import User

def delete_demo_users():
    """Eliminar usuarios de ejemplo específicos"""
    print("🗑️ Eliminando usuarios de ejemplo...")
    
    with app.app_context():
        # Lista de usuarios a eliminar
        demo_users = [
            'Juan Pérez',
            'María González', 
            'Carlos Rodríguez',
            'Roberto García'
        ]
        
        deleted_count = 0
        
        for user_name in demo_users:
            user = User.query.filter_by(name=user_name).first()
            if user:
                print(f"   - Eliminando: {user.name} ({user.username})")
                db.session.delete(user)
                deleted_count += 1
            else:
                print(f"   - No encontrado: {user_name}")
        
        if deleted_count > 0:
            db.session.commit()
            print(f"✅ {deleted_count} usuarios eliminados exitosamente")
        else:
            print("ℹ️ No se encontraron usuarios para eliminar")
        
        # Mostrar usuarios restantes
        remaining_users = User.query.all()
        print(f"\n📊 Usuarios restantes en el sistema: {len(remaining_users)}")
        for user in remaining_users:
            print(f"   - {user.name} ({user.username}) - {user.role}")

if __name__ == '__main__':
    delete_demo_users()
