#!/usr/bin/env python3
"""
Script para crear un usuario residente de prueba
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, db
from models import User

def create_resident_user():
    """Crear un usuario residente de prueba"""
    print("👤 Creando usuario residente de prueba...")
    
    with app.app_context():
        # Verificar si ya existe
        existing_user = User.query.filter_by(email='residente@barrioprivado.com').first()
        if existing_user:
            print(f"⚠️ El usuario ya existe: {existing_user.name} ({existing_user.username}) - {existing_user.role}")
            return
        
        # Crear usuario residente
        resident = User(
            username='residente_test',
            email='residente@barrioprivado.com',
            name='Residente de Prueba',
            role='resident',
            address='Calle Test 123, Barrio Privado',
            phone='+5491112345678',
            emergency_contact='+5491187654321',
            is_active=True,
            email_verified=True,
            phone_verified=True
        )
        resident.set_password('Residente123!')
        
        db.session.add(resident)
        db.session.commit()
        
        print(f"✅ Usuario residente creado exitosamente:")
        print(f"   - Nombre: {resident.name}")
        print(f"   - Usuario: {resident.username}")
        print(f"   - Email: {resident.email}")
        print(f"   - Rol: {resident.role}")
        print(f"   - Contraseña: Residente123!")
        
        # Mostrar todos los usuarios
        users = User.query.all()
        print(f"\n📊 Usuarios en el sistema: {len(users)}")
        for user in users:
            print(f"   - {user.name} ({user.username}) - {user.role}")

if __name__ == '__main__':
    create_resident_user()
