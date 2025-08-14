#!/usr/bin/env python3
"""
Script de emergencia para Render.com
Corrige el error de columnas faltantes en maintenance
"""

import os
import sqlite3
import sys

def find_database():
    """Buscar archivo de base de datos"""
    possible_paths = [
        'instance/barrio_cerrado.db',
        '/opt/render/project/src/instance/barrio_cerrado.db',
        'barrio_cerrado.db',
        '/tmp/barrio_cerrado.db',
        '/app/instance/barrio_cerrado.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def check_and_fix_database():
    """Revisar y arreglar base de datos"""
    
    db_path = find_database()
    if not db_path:
        print("❌ Base de datos no encontrada")
        return False
    
    print(f"📊 Procesando: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tabla maintenance
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='maintenance'")
        if not cursor.fetchone():
            print("❌ Tabla maintenance no existe")
            return False
        
        # Obtener estructura actual
        cursor.execute("PRAGMA table_info(maintenance)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        print(f"📋 Columnas actuales: {len(columns)}")
        
        # Columnas requeridas para IA
        required_columns = {
            'ai_classification': 'TEXT',
            'ai_suggestions': 'TEXT', 
            'assigned_area': 'VARCHAR(100)',
            'expected_response_time': 'VARCHAR(50)',
            'ai_confidence': 'REAL',
            'manual_override': 'BOOLEAN'
        }
        
        # Agregar columnas faltantes
        added = 0
        for col_name, col_type in required_columns.items():
            if col_name not in columns:
                try:
                    sql = f"ALTER TABLE maintenance ADD COLUMN {col_name} {col_type}"
                    cursor.execute(sql)
                    added += 1
                    print(f"✅ + {col_name}")
                except Exception as e:
                    print(f"❌ Error {col_name}: {e}")
        
        if added > 0:
            conn.commit()
            print(f"🎉 {added} columnas agregadas exitosamente")
        else:
            print("✅ Base de datos ya está actualizada")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Arreglando base de datos...")
    success = check_and_fix_database()
    
    if success:
        print("✅ ¡Listo! La aplicación debería funcionar ahora")
    else:
        print("❌ No se pudo arreglar automáticamente")
    
    sys.exit(0 if success else 1)
