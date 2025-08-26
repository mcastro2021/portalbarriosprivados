#!/usr/bin/env python3
"""
Script para prevenir la creación de noticias de demostración
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, db
from models import News, User

def prevent_demo_news():
    """Prevenir la creación de noticias de demostración"""
    print("🛡️ Configurando prevención de noticias de demostración...")
    
    with app.app_context():
        # Lista de palabras clave prohibidas para títulos
        forbidden_keywords = [
            'demo', 'test', 'ejemplo', 'muestra', 'prueba', 'sample',
            'noticia de prueba', 'noticia demo', 'noticia ejemplo',
            'Bienvenidos', 'Bienvenido', 'Primera noticia',
            'Noticia de prueba', 'Noticia demo', 'Portal del Barrio'
        ]
        
        # Verificar noticias existentes que puedan ser de demo
        existing_demo_news = []
        
        for keyword in forbidden_keywords:
            news_items = News.query.filter(News.title.ilike(f'%{keyword}%')).all()
            existing_demo_news.extend(news_items)
        
        # Eliminar duplicados
        existing_demo_news = list(set(existing_demo_news))
        
        if existing_demo_news:
            print(f"\n⚠️ Encontradas {len(existing_demo_news)} noticias que podrían ser de demostración:")
            for news in existing_demo_news:
                print(f"   - ID {news.id}: '{news.title}' (Autor: {news.author.name if news.author else 'N/A'})")
            
            response = input("\n¿Desea eliminar estas noticias potencialmente de demo? (SI/NO): ").strip().upper()
            
            if response == 'SI':
                deleted_count = 0
                for news in existing_demo_news:
                    try:
                        print(f"   - Eliminando: '{news.title}'")
                        db.session.delete(news)
                        deleted_count += 1
                    except Exception as e:
                        print(f"   ❌ Error eliminando noticia {news.id}: {str(e)}")
                
                if deleted_count > 0:
                    db.session.commit()
                    print(f"\n✅ {deleted_count} noticias eliminadas exitosamente")
                else:
                    print("\n❌ No se pudieron eliminar las noticias")
            else:
                print("\nℹ️ Operación cancelada")
        else:
            print("\n✅ No se encontraron noticias de demostración")
        
        # Mostrar estadísticas finales
        total_news = News.query.count()
        published_news = News.query.filter_by(is_published=True).count()
        important_news = News.query.filter_by(is_important=True).count()
        
        print(f"\n📊 Estadísticas finales:")
        print(f"   - Total: {total_news}")
        print(f"   - Publicadas: {published_news}")
        print(f"   - Importantes: {important_news}")
        
        # Mostrar noticias restantes
        remaining_news = News.query.order_by(News.created_at.desc()).limit(5).all()
        if remaining_news:
            print(f"\n📰 Noticias restantes:")
            for news in remaining_news:
                print(f"   - ID {news.id}: '{news.title}' ({news.created_at.strftime('%d/%m/%Y')})")
        
        print(f"\n🛡️ Prevención configurada:")
        print(f"   - Palabras clave prohibidas: {len(forbidden_keywords)}")
        print(f"   - Sistema limpio de noticias de demo")
        print(f"   - Solo contenido real permitido")

if __name__ == '__main__':
    prevent_demo_news()
