#!/usr/bin/env python3
"""
Script para verificar y eliminar noticias de demostración
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, db
from models import News, User

def check_demo_news():
    """Verificar y eliminar noticias de demostración"""
    print("🔍 Verificando noticias de demostración...")
    
    with app.app_context():
        # Buscar noticias que parezcan de demostración
        demo_keywords = [
            'demo', 'test', 'ejemplo', 'muestra', 'prueba', 'sample',
            'noticia de prueba', 'noticia demo', 'noticia ejemplo',
            'Bienvenidos', 'Bienvenido', 'Primera noticia',
            'Noticia de prueba', 'Noticia demo'
        ]
        
        demo_news = []
        
        # Buscar por palabras clave en el título
        for keyword in demo_keywords:
            news_items = News.query.filter(News.title.ilike(f'%{keyword}%')).all()
            demo_news.extend(news_items)
        
        # Buscar por palabras clave en el contenido
        for keyword in demo_keywords:
            news_items = News.query.filter(News.content.ilike(f'%{keyword}%')).all()
            demo_news.extend(news_items)
        
        # Eliminar duplicados
        demo_news = list(set(demo_news))
        
        if demo_news:
            print(f"\n⚠️ Encontradas {len(demo_news)} noticias de demostración:")
            for news in demo_news:
                print(f"   - ID {news.id}: '{news.title}' (Autor: {news.author.name if news.author else 'N/A'})")
            
            # Preguntar si eliminar
            response = input("\n¿Desea eliminar estas noticias de demostración? (SI/NO): ").strip().upper()
            
            if response == 'SI':
                deleted_count = 0
                for news in demo_news:
                    try:
                        print(f"   - Eliminando: '{news.title}'")
                        db.session.delete(news)
                        deleted_count += 1
                    except Exception as e:
                        print(f"   ❌ Error eliminando noticia {news.id}: {str(e)}")
                
                if deleted_count > 0:
                    db.session.commit()
                    print(f"\n✅ {deleted_count} noticias de demostración eliminadas exitosamente")
                else:
                    print("\n❌ No se pudieron eliminar las noticias")
            else:
                print("\nℹ️ Operación cancelada")
        else:
            print("\n✅ No se encontraron noticias de demostración")
        
        # Mostrar estadísticas generales
        total_news = News.query.count()
        published_news = News.query.filter_by(is_published=True).count()
        important_news = News.query.filter_by(is_important=True).count()
        
        print(f"\n📊 Estadísticas de noticias:")
        print(f"   - Total: {total_news}")
        print(f"   - Publicadas: {published_news}")
        print(f"   - Importantes: {important_news}")
        
        # Mostrar noticias recientes
        recent_news = News.query.order_by(News.created_at.desc()).limit(5).all()
        if recent_news:
            print(f"\n📰 Últimas 5 noticias:")
            for news in recent_news:
                print(f"   - ID {news.id}: '{news.title}' ({news.created_at.strftime('%d/%m/%Y')})")

if __name__ == '__main__':
    check_demo_news()
