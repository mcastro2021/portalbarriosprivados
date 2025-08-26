#!/usr/bin/env python3
"""
Script para eliminar automáticamente noticias de demostración
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, db
from models import News

def delete_demo_news():
    """Eliminar noticias de demostración automáticamente"""
    print("🗑️ Eliminando noticias de demostración...")
    
    with app.app_context():
        # IDs de las noticias de demostración encontradas
        demo_news_ids = [6, 1]  # IDs encontrados en el check anterior
        
        deleted_count = 0
        
        for news_id in demo_news_ids:
            try:
                news_item = News.query.get(news_id)
                if news_item:
                    print(f"   - Eliminando: ID {news_id} - '{news_item.title}'")
                    db.session.delete(news_item)
                    deleted_count += 1
                else:
                    print(f"   - No encontrada: ID {news_id}")
            except Exception as e:
                print(f"   ❌ Error eliminando noticia {news_id}: {str(e)}")
        
        if deleted_count > 0:
            db.session.commit()
            print(f"\n✅ {deleted_count} noticias de demostración eliminadas exitosamente")
        else:
            print("\nℹ️ No se eliminaron noticias")
        
        # Mostrar estadísticas actualizadas
        total_news = News.query.count()
        published_news = News.query.filter_by(is_published=True).count()
        important_news = News.query.filter_by(is_important=True).count()
        
        print(f"\n📊 Estadísticas actualizadas:")
        print(f"   - Total: {total_news}")
        print(f"   - Publicadas: {published_news}")
        print(f"   - Importantes: {important_news}")
        
        # Mostrar noticias restantes
        remaining_news = News.query.order_by(News.created_at.desc()).limit(5).all()
        if remaining_news:
            print(f"\n📰 Noticias restantes:")
            for news in remaining_news:
                print(f"   - ID {news.id}: '{news.title}' ({news.created_at.strftime('%d/%m/%Y')})")

if __name__ == '__main__':
    delete_demo_news()
