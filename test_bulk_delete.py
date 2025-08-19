#!/usr/bin/env python3
"""
Script de prueba para la funcionalidad de eliminación masiva de usuarios
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User

def test_bulk_delete():
    """Probar la funcionalidad de eliminación masiva"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Probando funcionalidad de eliminación masiva...")
        print("=" * 60)
        
        # Crear usuarios de prueba
        test_users = []
        for i in range(5):
            user = User(
                username=f'test_user_{i}',
                email=f'test{i}@example.com',
                name=f'Usuario de Prueba {i}',
                role='resident',
                is_active=True,
                email_verified=True
            )
            user.set_password('test123')
            test_users.append(user)
            db.session.add(user)
        
        db.session.commit()
        print(f"✅ {len(test_users)} usuarios de prueba creados")
        
        # Verificar usuarios creados
        created_users = User.query.filter(User.username.like('test_user_%')).all()
        print(f"📊 Usuarios de prueba en BD: {len(created_users)}")
        
        # Simular eliminación masiva
        user_ids = [user.id for user in created_users]
        protected_users = ['admin', 'mcastro2025']
        
        print(f"\n🗑️ Simulando eliminación de {len(user_ids)} usuarios...")
        
        # Obtener usuarios a eliminar
        users_to_delete = User.query.filter(User.id.in_(user_ids)).all()
        results = []
        deleted_count = 0
        
        for user in users_to_delete:
            try:
                # Verificar que no sea un usuario protegido
                if user.username in protected_users:
                    results.append(f'{user.username}: error - Usuario protegido del sistema')
                    continue
                
                username = user.username
                db.session.delete(user)
                deleted_count += 1
                results.append(f'{user.username}: eliminado')
                
            except Exception as e:
                results.append(f'{user.username}: error - {str(e)}')
        
        db.session.commit()
        
        print(f"✅ {deleted_count} usuarios eliminados exitosamente")
        print("\n📋 Resultados detallados:")
        for result in results:
            print(f"  {result}")
        
        # Verificar usuarios restantes
        remaining_users = User.query.filter(User.username.like('test_user_%')).all()
        print(f"\n📊 Usuarios de prueba restantes: {len(remaining_users)}")
        
        print("\n" + "=" * 60)
        print("✅ Prueba completada")

if __name__ == '__main__':
    test_bulk_delete()
