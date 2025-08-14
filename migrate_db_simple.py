"""
Migración simplificada para Render.com
"""

import sqlite3
import os
import sys

def migrate_database():
    """Migrar base de datos agregando columnas de IA"""
    
    # Buscar archivos de base de datos comunes
    possible_paths = [
        'instance/barrio_cerrado.db',
        '/opt/render/project/src/instance/barrio_cerrado.db',
        'barrio_cerrado.db',
        '/tmp/barrio_cerrado.db'
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ No se encontró la base de datos")
        print("🔍 Buscando en:")
        for path in possible_paths:
            print(f"   - {path}")
        return False
    
    print(f"📊 Base de datos encontrada: {db_path}")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la tabla maintenance existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='maintenance'")
        if not cursor.fetchone():
            print("❌ Tabla 'maintenance' no encontrada")
            return False
        
        # Obtener columnas existentes
        cursor.execute("PRAGMA table_info(maintenance)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Columnas existentes: {len(existing_columns)}")
        
        # Columnas a agregar
        new_columns = [
            'ai_classification TEXT',
            'ai_suggestions TEXT',
            'assigned_area VARCHAR(100)',
            'expected_response_time VARCHAR(50)',
            'ai_confidence REAL',
            'manual_override BOOLEAN DEFAULT 0'
        ]
        
        added_count = 0
        
        # Agregar cada columna
        for column_def in new_columns:
            column_name = column_def.split()[0]
            
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE maintenance ADD COLUMN {column_def}"
                    cursor.execute(sql)
                    added_count += 1
                    print(f"✅ Agregada: {column_name}")
                except Exception as e:
                    print(f"❌ Error con {column_name}: {e}")
            else:
                print(f"⏭️ Ya existe: {column_name}")
        
        # Confirmar cambios
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Migración completada: {added_count} columnas agregadas")
        return True
        
    except Exception as e:
        print(f"❌ Error durante migración: {e}")
        return False

if __name__ == '__main__':
    success = migrate_database()
    sys.exit(0 if success else 1)
