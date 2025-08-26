#!/usr/bin/env python3
"""
Script para resetear la base de datos (SOLO USAR EN DESARROLLO)
Este script elimina todos los datos y los recrea desde cero.
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, Visit, Reservation, News, Maintenance, Expense, Classified, SecurityReport, Notification, NeighborhoodMap, ChatbotSession

def reset_database():
    """Resetear completamente la base de datos"""
    app = create_app()
    
    with app.app_context():
        print("⚠️  ADVERTENCIA: Esto eliminará TODOS los datos de la base de datos")
        print("⚠️  Solo use este script en desarrollo")
        
        confirm = input("¿Está seguro que desea continuar? (escriba 'SI' para confirmar): ")
        if confirm != 'SI':
            print("❌ Operación cancelada")
            return
        
        print("🗄️ Reseteando base de datos...")
        
        # Eliminar todas las tablas
        db.drop_all()
        print("✅ Tablas eliminadas")
        
        # Crear tablas nuevamente
        db.create_all()
        print("✅ Tablas recreadas")
        
        # Crear usuario administrador
        admin = User(
            username='admin',
            email='admin@barrioprivado.com',
            name='Administrador del Sistema',
            role='admin',
            is_active=True,
            email_verified=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuario administrador creado (admin/admin123)")
        
        # No crear datos de ejemplo automáticamente
        # Los datos deben ser creados manualmente por el administrador cuando sea necesario
        
        db.session.commit()
        print("✅ Base de datos reseteada sin datos de ejemplo")
        print("✅ Base de datos reseteada completamente")

if __name__ == '__main__':
    reset_database()
