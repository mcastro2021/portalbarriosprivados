#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos permanentes
"""

import os
import sys
from datetime import datetime, timedelta

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, Visit, Reservation, News, Maintenance, Expense, Classified, SecurityReport, Notification, NeighborhoodMap, ChatbotSession

def init_permanent_db():
    """Inicializar base de datos con datos permanentes"""
    app = create_app()
    
    with app.app_context():
        print("🗄️ Inicializando base de datos permanente...")
        
        # Crear tablas
        db.create_all()
        print("✅ Tablas creadas")
        
        # Crear usuario administrador si no existe
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@barrioprivado.com',
                name='Administrador del Sistema',
                role='admin',
                is_active=True,
                email_verified=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario administrador creado (admin/admin123)")
        else:
            print("ℹ️ Usuario administrador ya existe")
        
        # Crear datos del mapa de Tejas 4 (solo si no existen)
        create_tejas4_map_data()
        
        # Crear noticias de ejemplo (solo si no existen)
        create_sample_news(admin)
        
        # Commit todos los cambios
        db.session.commit()
        print("✅ Base de datos inicializada correctamente")

def create_tejas4_map_data():
    """Crear datos específicos del mapa de Tejas 4"""
    print("🗺️ Verificando datos del mapa de Tejas 4...")
    
    # Verificar si ya existen datos del mapa
    if NeighborhoodMap.query.count() > 0:
        print("ℹ️ Los datos del mapa ya existen, saltando creación...")
        return
    
    print("🗺️ Creando datos del mapa de Tejas 4...")
    
    # Datos de las etapas basados en la imagen
    map_data = [
        # Etapa 1 - Vendida (Manzanas 40-57)
        {
            'block_name': 'Etapa 1 - Manzana 40',
            'street_name': 'Calle Principal',
            'block_number': 40,
            'total_houses': 12,
            'occupied_houses': 12,
            'description': 'Primera etapa del desarrollo - Completamente vendida',
            'stage': '1',
            'status': 'vendida',
            'block_type': 'residential',
            'coordinates_lat': -34.6037,
            'coordinates_lng': -58.3816
        },
        {
            'block_name': 'Etapa 1 - Manzana 41',
            'street_name': 'Calle Secundaria',
            'block_number': 41,
            'total_houses': 15,
            'occupied_houses': 15,
            'description': 'Primera etapa del desarrollo - Completamente vendida',
            'stage': '1',
            'status': 'vendida',
            'block_type': 'residential',
            'coordinates_lat': -34.6038,
            'coordinates_lng': -58.3817
        },
        
        # Etapa 2A - En Venta (Manzanas 20-39)
        {
            'block_name': 'Etapa 2A - Manzana 20',
            'street_name': 'Avenida Central',
            'block_number': 20,
            'total_houses': 18,
            'occupied_houses': 8,
            'description': 'Segunda etapa - Lotes disponibles para compra',
            'stage': '2A',
            'status': 'en_venta',
            'block_type': 'residential',
            'coordinates_lat': -34.6039,
            'coordinates_lng': -58.3818
        },
        {
            'block_name': 'Etapa 2A - Manzana 21',
            'street_name': 'Calle Norte',
            'block_number': 21,
            'total_houses': 16,
            'occupied_houses': 6,
            'description': 'Segunda etapa - Lotes disponibles para compra',
            'stage': '2A',
            'status': 'en_venta',
            'block_type': 'residential',
            'coordinates_lat': -34.6040,
            'coordinates_lng': -58.3819
        },
        
        # Etapa 2B - Desarrollo (Manzanas 1-19)
        {
            'block_name': 'Etapa 2B - Manzana 1',
            'street_name': 'Calle Sur',
            'block_number': 1,
            'total_houses': 14,
            'occupied_houses': 0,
            'description': 'Tercera etapa - En desarrollo, próximamente disponible',
            'stage': '2B',
            'status': 'desarrollo',
            'block_type': 'residential',
            'coordinates_lat': -34.6041,
            'coordinates_lng': -58.3820
        },
        {
            'block_name': 'Etapa 2B - Manzana 2',
            'street_name': 'Calle Este',
            'block_number': 2,
            'total_houses': 12,
            'occupied_houses': 0,
            'description': 'Tercera etapa - En desarrollo, próximamente disponible',
            'stage': '2B',
            'status': 'desarrollo',
            'block_type': 'residential',
            'coordinates_lat': -34.6042,
            'coordinates_lng': -58.3821
        },
        
        # Etapa 3 - Futuro (Manzanas 58-70)
        {
            'block_name': 'Etapa 3 - Manzana 58',
            'street_name': 'Calle Oeste',
            'block_number': 58,
            'total_houses': 10,
            'occupied_houses': 0,
            'description': 'Cuarta etapa - Planificada para futuras expansiones',
            'stage': '3',
            'status': 'futuro',
            'block_type': 'residential',
            'coordinates_lat': -34.6043,
            'coordinates_lng': -58.3822
        },
        
        # Espacios Verdes
        {
            'block_name': 'Espacio Verde 1',
            'street_name': 'Área Recreativa',
            'block_number': 100,
            'total_houses': 0,
            'occupied_houses': 0,
            'description': 'Espacio verde común - 8121.0m² - Plaza central',
            'stage': 'EV',
            'status': 'publico',
            'block_type': 'amenity',
            'coordinates_lat': -34.6044,
            'coordinates_lng': -58.3823
        },
        {
            'block_name': 'Espacio Verde 2',
            'street_name': 'Parque Norte',
            'block_number': 101,
            'total_houses': 0,
            'occupied_houses': 0,
            'description': 'Espacio verde común - 2333.7m² - Parque recreativo',
            'stage': 'EV',
            'status': 'publico',
            'block_type': 'amenity',
            'coordinates_lat': -34.6045,
            'coordinates_lng': -58.3824
        },
        {
            'block_name': 'Espacio Verde 3',
            'street_name': 'Reserva Natural',
            'block_number': 102,
            'total_houses': 0,
            'occupied_houses': 0,
            'description': 'Espacio verde común - 2093.91m² - Reserva natural',
            'stage': 'EV',
            'status': 'publico',
            'block_type': 'amenity',
            'coordinates_lat': -34.6046,
            'coordinates_lng': -58.3825
        },
        {
            'block_name': 'Espacio Verde 4',
            'street_name': 'Plaza Sur',
            'block_number': 103,
            'total_houses': 0,
            'occupied_houses': 0,
            'description': 'Espacio verde común - 314.16m² - Plaza de barrio',
            'stage': 'EV',
            'status': 'publico',
            'block_type': 'amenity',
            'coordinates_lat': -34.6047,
            'coordinates_lng': -58.3826
        },
        {
            'block_name': 'Espacio Verde 5',
            'street_name': 'Jardín Central',
            'block_number': 104,
            'total_houses': 0,
            'occupied_houses': 0,
            'description': 'Espacio verde común - 295.73m² - Jardín central',
            'stage': 'EV',
            'status': 'publico',
            'block_type': 'amenity',
            'coordinates_lat': -34.6048,
            'coordinates_lng': -58.3827
        },
        {
            'block_name': 'Espacio Verde 6',
            'street_name': 'Parque Grande',
            'block_number': 105,
            'total_houses': 0,
            'occupied_houses': 0,
            'description': 'Espacio verde común - 5342.93m² - Parque principal',
            'stage': 'EV',
            'status': 'publico',
            'block_type': 'amenity',
            'coordinates_lat': -34.6049,
            'coordinates_lng': -58.3828
        },
        {
            'block_name': 'Espacio Verde 7',
            'street_name': 'Jardín Este',
            'block_number': 106,
            'total_houses': 0,
            'occupied_houses': 0,
            'description': 'Espacio verde común - 350.40m² - Jardín oriental',
            'stage': 'EV',
            'status': 'publico',
            'block_type': 'amenity',
            'coordinates_lat': -34.6050,
            'coordinates_lng': -58.3829
        },
        
        # Amenities
        {
            'block_name': 'Club House',
            'street_name': 'Centro Comunitario',
            'block_number': 200,
            'total_houses': 0,
            'occupied_houses': 0,
            'description': 'Club house con piscina, quincho y SUM',
            'stage': 'AM',
            'status': 'activo',
            'block_type': 'amenity',
            'coordinates_lat': -34.6051,
            'coordinates_lng': -58.3830
        },
        {
            'block_name': 'Seguridad',
            'street_name': 'Puesto de Control',
            'block_number': 201,
            'total_houses': 0,
            'occupied_houses': 0,
            'description': 'Puesto de seguridad 24hs con CCTV',
            'stage': 'AM',
            'status': 'activo',
            'block_type': 'amenity',
            'coordinates_lat': -34.6052,
            'coordinates_lng': -58.3831
        }
    ]
    
    # Crear registros del mapa
    for data in map_data:
        map_item = NeighborhoodMap(**data)
        db.session.add(map_item)
    
    print(f"✅ {len(map_data)} registros del mapa creados")

def create_sample_news(admin):
    """Crear noticias de ejemplo"""
    print("📰 Verificando noticias de ejemplo...")
    
    # Verificar si ya existen noticias
    if News.query.count() > 0:
        print("ℹ️ Las noticias ya existen, saltando creación...")
        return
    
    print("📰 Creando noticias de ejemplo...")
    
    news_data = [
        {
            'title': 'Bienvenidos al Portal de Tejas Cuatro',
            'content': 'Este es el portal oficial de nuestro barrio cerrado Tejas Cuatro. Aquí podrán gestionar visitas, reservar espacios, consultar expensas y explorar nuestro mapa interactivo.',
            'category': 'general',
            'is_important': True,
            'is_published': True
        },
        {
            'title': 'Mapa Interactivo Disponible',
            'content': 'Ya está disponible nuestro mapa interactivo donde podrán explorar todas las etapas del desarrollo, lotes disponibles y espacios verdes. ¡Exploren las diferentes secciones!',
            'category': 'general',
            'is_important': True,
            'is_published': True
        },
        {
            'title': 'Etapa 2A - Lotes Disponibles',
            'content': 'Tenemos lotes disponibles en la Etapa 2A del desarrollo. Infraestructura completa, seguridad 24hs y todos los servicios incluidos. ¡Consulten por precios y financiación!',
            'category': 'ventas',
            'is_important': True,
            'is_published': True
        },
        {
            'title': 'Mantenimiento Programado - Espacios Verdes',
            'content': 'El próximo lunes se realizará mantenimiento en los espacios verdes del barrio. Los parques estarán cerrados de 8:00 a 16:00 hs.',
            'category': 'mantenimiento',
            'is_important': False,
            'is_published': True
        }
    ]
    
    for news_item_data in news_data:
        news_item = News(**news_item_data, author_id=admin.id)
        db.session.add(news_item)
    
    print(f"✅ {len(news_data)} noticias creadas")

if __name__ == '__main__':
    init_permanent_db() 