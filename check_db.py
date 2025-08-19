#!/usr/bin/env python3
"""
Script para verificar el estado de la base de datos
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, Visit, Reservation, News, Maintenance, Expense, Classified, SecurityReport, Notification, NeighborhoodMap, ChatbotSession

def check_database_status():
    """Verificar el estado de la base de datos"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Verificando estado de la base de datos...")
        print("=" * 50)
        
        # Verificar si las tablas existen
        try:
            # Contar registros en cada tabla
            user_count = User.query.count()
            visit_count = Visit.query.count()
            reservation_count = Reservation.query.count()
            news_count = News.query.count()
            maintenance_count = Maintenance.query.count()
            expense_count = Expense.query.count()
            classified_count = Classified.query.count()
            security_count = SecurityReport.query.count()
            notification_count = Notification.query.count()
            map_count = NeighborhoodMap.query.count()
            chatbot_count = ChatbotSession.query.count()
            
            print(f"👥 Usuarios: {user_count}")
            print(f"👤 Visitas: {visit_count}")
            print(f"📅 Reservas: {reservation_count}")
            print(f"📰 Noticias: {news_count}")
            print(f"🔧 Mantenimiento: {maintenance_count}")
            print(f"💳 Expensas: {expense_count}")
            print(f"📋 Clasificados: {classified_count}")
            print(f"🛡️ Reportes de seguridad: {security_count}")
            print(f"🔔 Notificaciones: {notification_count}")
            print(f"🗺️ Datos del mapa: {map_count}")
            print(f"🤖 Sesiones de chatbot: {chatbot_count}")
            
            # Verificar usuario administrador
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print(f"\n✅ Usuario administrador existe (ID: {admin.id})")
                print(f"   Email: {admin.email}")
                print(f"   Rol: {admin.role}")
                print(f"   Activo: {admin.is_active}")
                print(f"   Creado: {admin.created_at}")
            else:
                print("\n❌ Usuario administrador NO existe")
            
            # Verificar datos de ejemplo
            if news_count > 0:
                print(f"\n✅ Datos de ejemplo existen ({news_count} noticias)")
            else:
                print("\nℹ️ No hay datos de ejemplo")
            
            if map_count > 0:
                print(f"✅ Datos del mapa existen ({map_count} registros)")
            else:
                print("ℹ️ No hay datos del mapa")
                
            print("\n" + "=" * 50)
            print("✅ Verificación completada")
            
        except Exception as e:
            print(f"❌ Error al verificar la base de datos: {e}")
            print("💡 Ejecuta 'python init_db.py' para inicializar la base de datos")

if __name__ == '__main__':
    check_database_status()
