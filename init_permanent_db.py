#!/usr/bin/env python3
"""
Script para inicializar la base de datos permanente con datos de ejemplo
"""

import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, Visit, Reservation, News, Maintenance, Expense, ChatbotSession

def init_database():
    """Inicializar la base de datos con datos de ejemplo"""
    app = create_app()
    
    with app.app_context():
        print("🗄️ Inicializando base de datos permanente...")
        
        # Crear todas las tablas
        db.create_all()
        print("✅ Tablas creadas")
        
        # Crear usuarios de ejemplo
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@tejas4.com',
                'name': 'Administrador',
                'role': 'admin',
                'house_number': 'A1',
                'phone': '+54 11 4444-5555',
                'is_active': True,
                'is_approved': True
            },
            {
                'username': 'residente1',
                'email': 'residente1@tejas4.com',
                'name': 'Juan Pérez',
                'role': 'resident',
                'house_number': 'B15',
                'phone': '+54 9 11 1234-5678',
                'is_active': True,
                'is_approved': True
            },
            {
                'username': 'residente2',
                'email': 'residente2@tejas4.com',
                'name': 'María González',
                'role': 'resident',
                'house_number': 'C8',
                'phone': '+54 9 11 8765-4321',
                'is_active': True,
                'is_approved': True
            }
        ]
        
        for user_data in users_data:
            if not User.query.filter_by(username=user_data['username']).first():
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    name=user_data['name'],
                    role=user_data['role'],
                    house_number=user_data['house_number'],
                    phone=user_data['phone'],
                    is_active=user_data['is_active'],
                    is_approved=user_data['is_approved']
                )
                user.set_password('password123')
                db.session.add(user)
                print(f"👤 Usuario creado: {user_data['username']}")
        
        # Crear noticias de ejemplo
        news_data = [
            {
                'title': 'Bienvenidos al Portal del Barrio Tejas 4',
                'content': 'Ya está disponible el nuevo portal web del barrio. Aquí podrán gestionar visitas, reservas, expensas y más.',
                'category': 'general',
                'is_published': True,
                'is_important': True
            },
            {
                'title': 'Mantenimiento de Piscina',
                'content': 'La piscina estará cerrada del 15 al 20 de enero para mantenimiento anual.',
                'category': 'mantenimiento',
                'is_published': True,
                'is_important': False
            },
            {
                'title': 'Nuevo Reglamento de Mascotas',
                'content': 'Recordamos que el máximo de mascotas por vivienda es 2, siempre con correa.',
                'category': 'anuncios',
                'is_published': True,
                'is_important': False
            }
        ]
        
        for news_data_item in news_data:
            if not News.query.filter_by(title=news_data_item['title']).first():
                news = News(
                    title=news_data_item['title'],
                    content=news_data_item['content'],
                    category=news_data_item['category'],
                    is_published=news_data_item['is_published'],
                    is_important=news_data_item['is_important'],
                    author_id=1  # Admin
                )
                db.session.add(news)
                print(f"📢 Noticia creada: {news_data_item['title']}")
        
        # Crear expensas de ejemplo
        expenses_data = [
            {
                'user_id': 2,
                'month': 'Enero',
                'period': '2024',
                'amount': 15000.00,
                'description': 'Expensas Enero 2024',
                'due_date': datetime.now() + timedelta(days=15),
                'status': 'pending'
            },
            {
                'user_id': 3,
                'month': 'Enero',
                'period': '2024',
                'amount': 15000.00,
                'description': 'Expensas Enero 2024',
                'due_date': datetime.now() + timedelta(days=15),
                'status': 'pending'
            }
        ]
        
        for expense_data in expenses_data:
            if not Expense.query.filter_by(user_id=expense_data['user_id'], description=expense_data['description']).first():
                expense = Expense(
                    user_id=expense_data['user_id'],
                    month=expense_data['month'],
                    period=expense_data['period'],
                    amount=expense_data['amount'],
                    description=expense_data['description'],
                    due_date=expense_data['due_date'],
                    status=expense_data['status']
                )
                db.session.add(expense)
                print(f"💳 Expensa creada: {expense_data['description']}")
        
        # Crear visitas de ejemplo
        visits_data = [
            {
                'resident_id': 2,
                'visitor_name': 'Carlos López',
                'visitor_phone': '+54 9 11 1111-1111',
                'visit_purpose': 'Visita familiar',
                'entry_time': datetime.now() + timedelta(days=1),
                'status': 'pending'
            },
            {
                'resident_id': 3,
                'visitor_name': 'Ana Martínez',
                'visitor_phone': '+54 9 11 2222-2222',
                'visit_purpose': 'Mantenimiento',
                'entry_time': datetime.now() + timedelta(days=2),
                'status': 'pending'
            }
        ]
        
        for visit_data in visits_data:
            if not Visit.query.filter_by(resident_id=visit_data['resident_id'], visitor_name=visit_data['visitor_name']).first():
                visit = Visit(
                    resident_id=visit_data['resident_id'],
                    visitor_name=visit_data['visitor_name'],
                    visitor_phone=visit_data['visitor_phone'],
                    visit_purpose=visit_data['visit_purpose'],
                    entry_time=visit_data['entry_time'],
                    status=visit_data['status']
                )
                db.session.add(visit)
                print(f"👥 Visita creada: {visit_data['visitor_name']}")
        
        # Crear reservas de ejemplo
        reservations_data = [
            {
                'user_id': 2,
                'space_type': 'quincho',
                'space_name': 'Quincho Principal',
                'start_time': datetime.now() + timedelta(days=7, hours=18),
                'end_time': datetime.now() + timedelta(days=7, hours=22),
                'event_type': 'Cumpleaños',
                'status': 'pending'
            },
            {
                'user_id': 3,
                'space_type': 'deportes',
                'space_name': 'Cancha de Tenis',
                'start_time': datetime.now() + timedelta(days=3, hours=16),
                'end_time': datetime.now() + timedelta(days=3, hours=18),
                'event_type': 'Partido de tenis',
                'status': 'approved'
            }
        ]
        
        for reservation_data in reservations_data:
            if not Reservation.query.filter_by(user_id=reservation_data['user_id'], space_name=reservation_data['space_name'], start_time=reservation_data['start_time']).first():
                reservation = Reservation(
                    user_id=reservation_data['user_id'],
                    space_type=reservation_data['space_type'],
                    space_name=reservation_data['space_name'],
                    start_time=reservation_data['start_time'],
                    end_time=reservation_data['end_time'],
                    event_type=reservation_data['event_type'],
                    status=reservation_data['status']
                )
                db.session.add(reservation)
                print(f"📅 Reserva creada: {reservation_data['space_name']}")
        
        # Crear reclamos de mantenimiento de ejemplo
        maintenance_data = [
            {
                'user_id': 2,
                'title': 'Foco quemado en pasillo',
                'description': 'El foco del pasillo de la manzana B está quemado',
                'category': 'iluminacion',
                'priority': 'medium',
                'status': 'pending'
            },
            {
                'user_id': 3,
                'title': 'Fuga de agua en quincho',
                'description': 'Hay una fuga de agua en el quincho principal',
                'category': 'plomeria',
                'priority': 'high',
                'status': 'in_progress'
            }
        ]
        
        for maintenance_item in maintenance_data:
            if not Maintenance.query.filter_by(user_id=maintenance_item['user_id'], title=maintenance_item['title']).first():
                maintenance = Maintenance(
                    user_id=maintenance_item['user_id'],
                    title=maintenance_item['title'],
                    description=maintenance_item['description'],
                    category=maintenance_item['category'],
                    priority=maintenance_item['priority'],
                    status=maintenance_item['status']
                )
                db.session.add(maintenance)
                print(f"🔧 Reclamo creado: {maintenance_item['title']}")
        
        # Commit todos los cambios
        db.session.commit()
        print("✅ Base de datos inicializada correctamente")
        print("\n📋 Datos creados:")
        print(f"   👤 Usuarios: {User.query.count()}")
        print(f"   📢 Noticias: {News.query.count()}")
        print(f"   💳 Expensas: {Expense.query.count()}")
        print(f"   👥 Visitas: {Visit.query.count()}")
        print(f"   📅 Reservas: {Reservation.query.count()}")
        print(f"   🔧 Reclamos: {Maintenance.query.count()}")
        
        print("\n🔑 Credenciales de acceso:")
        print("   Admin: admin / password123")
        print("   Residente 1: residente1 / password123")
        print("   Residente 2: residente2 / password123")

if __name__ == "__main__":
    init_database()
