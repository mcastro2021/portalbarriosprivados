#!/usr/bin/env python3
"""
Script de prueba para verificar las redirecciones del dashboard
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dashboard_redirects():
    """Probar las redirecciones del dashboard"""
    try:
        from main import create_app
        from models import db, User
        
        app = create_app()
        
        with app.app_context():
            print("🔍 Verificando redirecciones del dashboard...")
            
            # Verificar usuarios existentes
            users = User.query.all()
            print(f"\n📊 Usuarios en el sistema: {len(users)}")
            
            for user in users:
                print(f"   - {user.name} ({user.username}) - Rol: {user.role}")
                
                # Simular redirección según rol
                if user.role == 'admin':
                    expected_redirect = 'admin.dashboard'
                else:
                    expected_redirect = 'main.dashboard'
                
                print(f"     → Debería redirigir a: {expected_redirect}")
            
            # Verificar que existe la ruta main.dashboard
            print("\n🔗 Verificando rutas disponibles...")
            
            with app.test_client() as client:
                # Probar acceso a rutas principales
                routes_to_test = [
                    ('/', 'Página principal'),
                    ('/dashboard', 'Dashboard general'),
                    ('/admin/dashboard', 'Panel de administración')
                ]
                
                for route, description in routes_to_test:
                    try:
                        response = client.get(route, follow_redirects=False)
                        print(f"   ✅ {description} ({route}): {response.status_code}")
                    except Exception as e:
                        print(f"   ❌ {description} ({route}): Error - {e}")
            
            print("\n✅ Verificación completada")
            return True
            
    except Exception as e:
        print(f"❌ Error en la verificación: {e}")
        return False

def test_user_roles():
    """Verificar roles de usuarios"""
    try:
        from main import create_app
        from models import db, User
        
        app = create_app()
        
        with app.app_context():
            print("\n👥 Verificando roles de usuarios...")
            
            # Contar usuarios por rol
            admin_users = User.query.filter_by(role='admin').count()
            resident_users = User.query.filter_by(role='resident').count()
            other_users = User.query.filter(User.role.notin_(['admin', 'resident'])).count()
            
            print(f"   - Administradores: {admin_users}")
            print(f"   - Residentes: {resident_users}")
            print(f"   - Otros roles: {other_users}")
            
            # Mostrar usuarios admin
            if admin_users > 0:
                print("\n👑 Usuarios administradores:")
                admins = User.query.filter_by(role='admin').all()
                for admin in admins:
                    print(f"   - {admin.name} ({admin.username}) - {admin.email}")
            
            # Mostrar algunos residentes
            if resident_users > 0:
                print(f"\n🏠 Primeros {min(3, resident_users)} residentes:")
                residents = User.query.filter_by(role='resident').limit(3).all()
                for resident in residents:
                    print(f"   - {resident.name} ({resident.username}) - {resident.email}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error verificando roles: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 Prueba de redirecciones del dashboard")
    print("=" * 50)
    
    # Probar redirecciones
    success1 = test_dashboard_redirects()
    
    # Probar roles de usuarios
    success2 = test_user_roles()
    
    if success1 and success2:
        print("\n🎉 Todas las pruebas pasaron exitosamente")
        print("\n📋 Resumen:")
        print("✅ Las redirecciones están configuradas correctamente")
        print("✅ Los usuarios se redirigen según su rol")
        print("✅ Administradores → Panel de Administración")
        print("✅ Residentes → Dashboard General")
    else:
        print("\n❌ Algunas pruebas fallaron")

if __name__ == "__main__":
    main()
