#!/usr/bin/env python3
"""
Script para eliminar el usuario residente de prueba
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, db
from models import User

def delete_resident_user():
    """Eliminar el usuario residente de prueba"""
    print("🗑️ Eliminando usuario residente de prueba...")
    
    with app.app_context():
        # Buscar el usuario residente
        resident = User.query.filter_by(email='residente@barrioprivado.com').first()
        
        if resident:
            print(f"   - Eliminando: {resident.name} ({resident.username}) - {resident.role}")
            db.session.delete(resident)
            db.session.commit()
            print(f"✅ Usuario residente eliminado exitosamente")
        else:
            print("ℹ️ No se encontró el usuario residente para eliminar")
        
        # Mostrar usuarios restantes
        remaining_users = User.query.all()
        print(f"\n📊 Usuarios restantes en el sistema: {len(remaining_users)}")
        for user in remaining_users:
            print(f"   - {user.name} ({user.username}) - {user.role}")

if __name__ == '__main__':
    delete_resident_user()
