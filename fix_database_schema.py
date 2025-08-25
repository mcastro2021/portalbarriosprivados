#!/usr/bin/env python3
"""
Script para arreglar el esquema de la base de datos agregando columnas faltantes
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError

def fix_database_schema():
    """Arreglar el esquema de la base de datos"""
    
    # Intentar diferentes configuraciones de base de datos
    possible_urls = [
        os.environ.get('DATABASE_URL'),
        'sqlite:///instance/contabilidad.db',
        'sqlite:///instance/portalbarriosprivados.db',
        'sqlite:///portalbarriosprivados.db'
    ]
    
    engine = None
    database_url = None
    
    # Probar cada URL hasta encontrar una que funcione
    for url in possible_urls:
        if url:
            try:
                print(f"🔍 Probando conexión a: {url}")
                test_engine = create_engine(url)
                with test_engine.connect() as conn:
                    # Verificar si la tabla users existe
                    inspector = inspect(test_engine)
                    if 'users' in inspector.get_table_names():
                        engine = test_engine
                        database_url = url
                        print(f"✅ Conexión exitosa a: {url}")
                        break
                    else:
                        print(f"ℹ️ Tabla 'users' no encontrada en: {url}")
            except Exception as e:
                print(f"❌ Error conectando a {url}: {e}")
    
    if not engine:
        print("❌ No se pudo conectar a ninguna base de datos")
        return False
    
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
            print("🔍 Verificando columnas existentes en tabla 'users'...")
            
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
            print("✅ Esquema de base de datos arreglado exitosamente")
            return True
            
    except OperationalError as e:
        print(f"❌ Error en la migración: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando arreglo del esquema de base de datos...")
    success = fix_database_schema()
    if success:
        print("🎉 Esquema arreglado exitosamente")
        sys.exit(0)
    else:
        print("💥 Arreglo del esquema falló")
        sys.exit(1)
