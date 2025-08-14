"""
Script de migración para agregar columnas de IA al modelo Maintenance
"""

from flask import Flask
from models import db, Maintenance
from config import config
import sqlite3
import os

def create_app():
    """Crear aplicación Flask para migración"""
    app = Flask(__name__)
    app.config.from_object(config['production'])
    db.init_app(app)
    return app

def check_column_exists(cursor, table_name, column_name):
    """Verificar si una columna existe en la tabla"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def migrate_database():
    """Ejecutar migración de base de datos"""
    app = create_app()
    
    with app.app_context():
        try:
            # Obtener ruta de la base de datos
            db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
            
            if not os.path.exists(db_path):
                print(f"❌ Base de datos no encontrada en: {db_path}")
                print("🔄 Creando nueva base de datos...")
                db.create_all()
                print("✅ Base de datos creada correctamente")
                return
            
            print(f"📊 Migrando base de datos: {db_path}")
            
            # Conectar directamente con SQLite
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Lista de columnas a agregar
            new_columns = [
                ('ai_classification', 'TEXT'),
                ('ai_suggestions', 'TEXT'),
                ('assigned_area', 'VARCHAR(100)'),
                ('expected_response_time', 'VARCHAR(50)'),
                ('ai_confidence', 'REAL'),
                ('manual_override', 'BOOLEAN DEFAULT 0')
            ]
            
            columns_added = []
            columns_skipped = []
            
            # Agregar cada columna si no existe
            for column_name, column_type in new_columns:
                if not check_column_exists(cursor, 'maintenance', column_name):
                    try:
                        sql = f"ALTER TABLE maintenance ADD COLUMN {column_name} {column_type}"
                        cursor.execute(sql)
                        columns_added.append(column_name)
                        print(f"✅ Columna agregada: {column_name}")
                    except Exception as e:
                        print(f"❌ Error agregando columna {column_name}: {e}")
                else:
                    columns_skipped.append(column_name)
                    print(f"⏭️ Columna ya existe: {column_name}")
            
            # Confirmar cambios
            conn.commit()
            conn.close()
            
            # Resumen
            print("\n" + "="*50)
            print("📋 RESUMEN DE MIGRACIÓN")
            print("="*50)
            print(f"✅ Columnas agregadas: {len(columns_added)}")
            for col in columns_added:
                print(f"   - {col}")
            
            print(f"⏭️ Columnas existentes: {len(columns_skipped)}")
            for col in columns_skipped:
                print(f"   - {col}")
            
            if columns_added:
                print("\n🎉 ¡Migración completada exitosamente!")
                print("🚀 La aplicación ahora debería funcionar correctamente")
            else:
                print("\n🔄 No se requirieron cambios en la base de datos")
            
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            raise

if __name__ == '__main__':
    migrate_database()
