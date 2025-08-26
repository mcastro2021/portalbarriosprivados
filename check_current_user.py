#!/usr/bin/env python3
"""
Script para verificar el usuario actual y su rol
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, db
from models import User

def check_current_user():
    """Verificar el usuario actual y su rol"""
    print("🔍 Verificando usuarios en el sistema...")
    
    with app.app_context():
        # Mostrar todos los usuarios
        users = User.query.all()
        print(f"\n📊 Usuarios en el sistema: {len(users)}")
        for user in users:
            print(f"   - {user.name} ({user.username}) - {user.role}")
        
        # Verificar si hay usuarios admin
        admin_users = User.query.filter_by(role='admin').all()
        print(f"\n👑 Usuarios administradores: {len(admin_users)}")
        for user in admin_users:
            print(f"   - {user.name} ({user.username}) - {user.email}")
        
        # Verificar si hay usuarios residentes
        resident_users = User.query.filter_by(role='resident').all()
        print(f"\n🏠 Usuarios residentes: {len(resident_users)}")
        for user in resident_users:
            print(f"   - {user.name} ({user.username}) - {user.email}")
        
        # Verificar otros roles
        other_users = User.query.filter(User.role != 'admin', User.role != 'resident').all()
        print(f"\n🔧 Otros roles: {len(other_users)}")
        for user in other_users:
            print(f"   - {user.name} ({user.username}) - {user.role} - {user.email}")

if __name__ == '__main__':
    check_current_user()
