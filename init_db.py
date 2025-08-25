#!/usr/bin/env python3
"""
Script de inicialización de la base de datos
Incluye migración de columnas de 2FA
"""

import os
import sys
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

def migrate_2fa_columns(db):
    """Agregar columnas de 2FA a la tabla users si no existen"""
    try:
        print("🔍 Verificando columnas de 2FA...")
        
        # Verificar qué columnas ya existen
        result = db.session.execute(text("PRAGMA table_info(users)"))
        existing_columns = [row[1] for row in result.fetchall()]
        
        print(f"Columnas existentes: {existing_columns}")
        
        # Columnas a agregar
        columns_to_add = [
            {
                'name': 'two_factor_enabled',
                'definition': 'BOOLEAN DEFAULT FALSE'
            },
            {
                'name': 'two_factor_secret',
                'definition': 'VARCHAR(32)'
            },
            {
                'name': 'two_factor_enabled_at',
                'definition': 'TIMESTAMP'
            },
            {
                'name': 'two_factor_backup_codes',
                'definition': 'TEXT'
            }
        ]
        
        # Agregar columnas faltantes
        for column in columns_to_add:
            if column['name'] not in existing_columns:
                print(f"➕ Agregando columna: {column['name']}")
                sql = f"ALTER TABLE users ADD COLUMN {column['name']} {column['definition']}"
                db.session.execute(text(sql))
                print(f"✅ Columna {column['name']} agregada exitosamente")
            else:
                print(f"ℹ️ Columna {column['name']} ya existe")
        
        db.session.commit()
        print("✅ Migración de columnas 2FA completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en migración 2FA: {e}")
        db.session.rollback()
        return False

def init_database():
    """Inicializar la base de datos"""
    try:
        # Importar después de configurar el entorno
        from main import create_app
        from models import db, User
        
        app = create_app()
        
        with app.app_context():
            print("🚀 Iniciando inicialización de base de datos...")
            
            # Crear todas las tablas
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            
            # Migrar columnas de 2FA
            migrate_2fa_columns(db)
            
            # Verificar si ya existe un usuario admin
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                print("👤 Creando usuario administrador...")
                
                admin_user = User(
                    username='admin',
                    email='admin@barrioprivado.com',
                    name='Administrador',
                    role='admin',
                    is_active=True,
                    email_verified=True
                )
                admin_user.set_password('admin123')
                
                db.session.add(admin_user)
                db.session.commit()
                
                print("✅ Usuario administrador creado exitosamente")
                print("   Usuario: admin")
                print("   Contraseña: admin123")
            else:
                print("ℹ️ Usuario administrador ya existe")
            
            print("🎉 Inicialización de base de datos completada")
            return True
            
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    if success:
        print("✅ Base de datos inicializada correctamente")
        sys.exit(0)
    else:
        print("❌ Error al inicializar la base de datos")
        sys.exit(1) 