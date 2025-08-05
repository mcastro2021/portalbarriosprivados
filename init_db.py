#!/usr/bin/env python3
"""
Script para inicializar la base de datos del Portal de Barrio Cerrado
"""

import os
import sys
from app import create_app, init_db, create_sample_data
from models import db, User, News, NeighborhoodMap

def main():
    """Función principal para inicializar la base de datos"""
    print("🚀 Inicializando Portal de Barrio Cerrado...")
    
    # Crear aplicación
    app = create_app()
    
    with app.app_context():
        try:
            # Crear todas las tablas
            print("📊 Creando tablas de la base de datos...")
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            
            # Verificar si ya existe un administrador
            admin = User.query.filter_by(username='admin').first()
            
            if not admin:
                print("👤 Creando usuario administrador...")
                
                # Crear usuario administrador
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
                
                print("✅ Usuario administrador creado:")
                print("   Usuario: admin")
                print("   Contraseña: admin123")
                print("   Email: admin@barrioprivado.com")
                
                # Crear datos de ejemplo
                print("📝 Creando datos de ejemplo...")
                create_sample_data()
                print("✅ Datos de ejemplo creados")
                
            else:
                print("ℹ️  El usuario administrador ya existe")
            
            # Mostrar estadísticas
            total_users = User.query.count()
            total_news = News.query.count()
            total_blocks = NeighborhoodMap.query.count()
            
            print("\n📈 Estadísticas de la base de datos:")
            print(f"   Usuarios: {total_users}")
            print(f"   Noticias: {total_news}")
            print(f"   Manzanas: {total_blocks}")
            
            print("\n🎉 ¡Inicialización completada exitosamente!")
            print("\n📋 Próximos pasos:")
            print("   1. Ejecuta: python app.py")
            print("   2. Abre tu navegador en: http://localhost:5000")
            print("   3. Inicia sesión con admin/admin123")
            print("   4. Configura las variables de entorno para producción")
            
        except Exception as e:
            print(f"❌ Error durante la inicialización: {str(e)}")
            db.session.rollback()
            sys.exit(1)

def create_sample_data():
    """Crear datos de ejemplo para el sistema"""
    
    # Crear usuarios de ejemplo
    users_data = [
        {
            'username': 'residente1',
            'email': 'residente1@barrioprivado.com',
            'name': 'Juan Pérez',
            'role': 'resident',
            'address': 'Manzana A, Casa 1',
            'phone': '+54 9 11 1234-5678'
        },
        {
            'username': 'residente2',
            'email': 'residente2@barrioprivado.com',
            'name': 'María González',
            'role': 'resident',
            'address': 'Manzana A, Casa 2',
            'phone': '+54 9 11 2345-6789'
        },
        {
            'username': 'seguridad1',
            'email': 'seguridad@barrioprivado.com',
            'name': 'Carlos Rodríguez',
            'role': 'security',
            'phone': '+54 9 11 8765-4321'
        },
        {
            'username': 'mantenimiento1',
            'email': 'mantenimiento@barrioprivado.com',
            'name': 'Roberto García',
            'role': 'maintenance',
            'phone': '+54 9 11 5555-1234'
        }
    ]
    
    admin = User.query.filter_by(username='admin').first()
    
    for user_data in users_data:
        if not User.query.filter_by(username=user_data['username']).first():
            user = User(**user_data)
            user.set_password('password123')
            user.email_verified = True
            user.is_active = True
            db.session.add(user)
    
    # Crear noticias de ejemplo
    news_data = [
        {
            'title': 'Bienvenidos al Portal del Barrio',
            'content': '''¡Bienvenidos al portal oficial de nuestro barrio cerrado!

Este sistema les permitirá:
• Registrar visitas de manera anticipada
• Reservar espacios comunes (quinchos, SUM, canchas)
• Consultar y pagar expensas
• Reportar problemas de mantenimiento
• Publicar y ver anuncios clasificados
• Recibir notificaciones importantes
• Y mucho más...

Para comenzar, les recomendamos:
1. Completar su perfil con información actualizada
2. Revisar las noticias y comunicaciones
3. Explorar las diferentes funcionalidades disponibles

¡Esperamos que este portal mejore la comunicación y organización de nuestro barrio!''',
            'category': 'general',
            'is_important': True
        },
        {
            'title': 'Mantenimiento Programado - Piscina',
            'content': '''Se informa a todos los residentes que el próximo lunes 15 de enero se realizará mantenimiento en la piscina.

Detalles del mantenimiento:
• Fecha: Lunes 15 de enero
• Horario: 8:00 a 16:00 hs
• Motivo: Limpieza profunda y revisión de filtros
• Duración estimada: 8 horas

La piscina permanecerá cerrada durante este período por seguridad. Agradecemos su comprensión.

Para consultas, contactar a mantenimiento@barrioprivado.com''',
            'category': 'mantenimiento',
            'is_important': True
        },
        {
            'title': 'Nuevo Sistema de Seguridad',
            'content': '''Se ha implementado un nuevo sistema de seguridad en el barrio que incluye:

• Cámaras de vigilancia adicionales
• Control de acceso mejorado
• Sistema de alarmas comunitarias
• Botón de pánico en el portal

Todos los residentes pueden acceder a las cámaras desde el portal web (según permisos). Para activar su acceso, contacten a seguridad@barrioprivado.com''',
            'category': 'seguridad',
            'is_important': False
        },
        {
            'title': 'Evento Comunitario - Fiesta de Verano',
            'content': '''¡Los invitamos a la Fiesta de Verano del barrio!

• Fecha: Sábado 20 de enero
• Horario: 19:00 a 02:00 hs
• Lugar: Quincho Principal
• Incluye: Cena, música en vivo, actividades para niños

Para reservar su lugar, utilicen el sistema de reservas del portal. Cupos limitados.

¡Los esperamos para celebrar juntos!''',
            'category': 'eventos',
            'is_important': False
        },
        {
            'title': 'Corte Programado de Agua',
            'content': '''Se informa que habrá un corte programado de agua el próximo miércoles 17 de enero.

Detalles:
• Fecha: Miércoles 17 de enero
• Horario: 9:00 a 17:00 hs
• Motivo: Reparación de cañería principal
• Zona afectada: Manzanas A y B

Se recomienda almacenar agua para uso esencial durante este período.

Disculpen las molestias ocasionadas.''',
            'category': 'cortes',
            'is_important': True
        }
    ]
    
    for news_item_data in news_data:
        if not News.query.filter_by(title=news_item_data['title']).first():
            news_item = News(**news_item_data, author_id=admin.id)
            db.session.add(news_item)
    
    # Crear datos del mapa del barrio
    map_data = [
        {
            'block_name': 'Manzana A',
            'street_name': 'Calle Principal',
            'block_number': 1,
            'total_houses': 12,
            'occupied_houses': 10,
            'description': 'Primera manzana del barrio, ubicada en la entrada principal'
        },
        {
            'block_name': 'Manzana B',
            'street_name': 'Calle Secundaria',
            'block_number': 2,
            'total_houses': 15,
            'occupied_houses': 12,
            'description': 'Segunda manzana, con vista al parque central'
        },
        {
            'block_name': 'Manzana C',
            'street_name': 'Calle de los Pinos',
            'block_number': 3,
            'total_houses': 18,
            'occupied_houses': 16,
            'description': 'Manzana más grande, con acceso directo a las canchas'
        },
        {
            'block_name': 'Manzana D',
            'street_name': 'Calle del Lago',
            'block_number': 4,
            'total_houses': 10,
            'occupied_houses': 8,
            'description': 'Manzana premium con vista al lago artificial'
        }
    ]
    
    for map_item_data in map_data:
        if not NeighborhoodMap.query.filter_by(block_name=map_item_data['block_name']).first():
            map_item = NeighborhoodMap(**map_item_data)
            # Coordenadas de ejemplo (Buenos Aires)
            map_item.set_coordinates(-34.6037, -58.3816)
            db.session.add(map_item)
    
    db.session.commit()

if __name__ == '__main__':
    main() 