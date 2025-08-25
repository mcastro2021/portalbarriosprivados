#!/usr/bin/env python3
"""
Script de migración para agregar columnas de 2FA a la tabla users
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def migrate_2fa_columns():
    """Agregar columnas de 2FA a la tabla users"""
    
    # Configurar la base de datos
    database_url = os.environ.get('DATABASE_URL')
    
    # Si no hay DATABASE_URL, usar la configuración por defecto
    if not database_url:
        # Usar SQLite por defecto
        database_url = 'sqlite:///instance/contabilidad.db'
        print(f"ℹ️ Usando base de datos por defecto: {database_url}")
    
    # Crear engine
    engine = create_engine(database_url)
    
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
    
    try:
        with engine.connect() as conn:
            print("🔍 Verificando columnas existentes...")
            
            # Verificar qué columnas ya existen
            result = conn.execute(text("PRAGMA table_info(users)"))
            existing_columns = [row[1] for row in result.fetchall()]
            
            print(f"Columnas existentes: {existing_columns}")
            
            # Agregar columnas faltantes
            for column in columns_to_add:
                if column['name'] not in existing_columns:
                    print(f"➕ Agregando columna: {column['name']}")
                    sql = f"ALTER TABLE users ADD COLUMN {column['name']} {column['definition']}"
                    conn.execute(text(sql))
                    print(f"✅ Columna {column['name']} agregada exitosamente")
                else:
                    print(f"ℹ️ Columna {column['name']} ya existe")
            
            conn.commit()
            print("✅ Migración completada exitosamente")
            return True
            
    except OperationalError as e:
        print(f"❌ Error en la migración: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando migración de columnas 2FA...")
    success = migrate_2fa_columns()
    if success:
        print("🎉 Migración completada exitosamente")
        sys.exit(0)
    else:
        print("💥 Migración falló")
        sys.exit(1)
