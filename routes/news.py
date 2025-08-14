from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import db, News, User
from datetime import datetime

bp = Blueprint('news', __name__, url_prefix='/news')

@bp.route('/')
def index():
    """Lista de noticias"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    
    # Filtrar por categoría si se especifica
    query = News.query.filter_by(is_published=True)
    if category:
        query = query.filter_by(category=category)
    
    news = query.order_by(News.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    # Obtener categorías para el filtro
    from flask import current_app
    categories = current_app.config['NEWS_CATEGORIES']
    
    return render_template('news/index.html', news=news, categories=categories, current_category=category)

@bp.route('/<int:news_id>')
def show(news_id):
    """Mostrar noticia individual"""
    news_item = News.query.get_or_404(news_id)
    
    # Solo mostrar noticias publicadas (excepto para administradores)
    if not news_item.is_published and not current_user.is_authenticated:
        flash('Noticia no encontrada', 'error')
        return redirect(url_for('news.index'))
    
    return render_template('news/show.html', news=news_item)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Crear nueva noticia"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para crear noticias', 'error')
        return redirect(url_for('news.index'))
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            category = request.form.get('category', '').strip()
            is_important = request.form.get('is_important') == 'on'
            is_published = request.form.get('is_published') == 'on'
            
            # Validaciones
            if not title:
                flash('El título es obligatorio', 'error')
                return render_template('news/new.html')
            
            if not content:
                flash('El contenido es obligatorio', 'error')
                return render_template('news/new.html')
            
            if not category:
                flash('La categoría es obligatoria', 'error')
                return render_template('news/new.html')
            
            # Crear noticia
            news_item = News(
                title=title,
                content=content,
                author_id=current_user.id,
                category=category,
                is_important=is_important,
                is_published=is_published
            )
            
            db.session.add(news_item)
            db.session.commit()
            
            flash('Noticia creada exitosamente', 'success')
            return redirect(url_for('news.show', news_id=news_item.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la noticia: {str(e)}', 'error')
            return render_template('news/new.html')
    
    # Obtener categorías
    categories = current_app.config['NEWS_CATEGORIES']
    return render_template('news/new.html', categories=categories)

@bp.route('/<int:news_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(news_id):
    """Editar noticia"""
    news_item = News.query.get_or_404(news_id)
    
    # Verificar permisos
    if news_item.author_id != current_user.id and not current_user.can_access_admin():
        flash('No tienes permisos para editar esta noticia', 'error')
        return redirect(url_for('news.show', news_id=news_item.id))
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            category = request.form.get('category', '').strip()
            is_important = request.form.get('is_important') == 'on'
            is_published = request.form.get('is_published') == 'on'
            
            # Validaciones
            if not title:
                flash('El título es obligatorio', 'error')
                return render_template('news/edit.html', news=news_item)
            
            if not content:
                flash('El contenido es obligatorio', 'error')
                return render_template('news/edit.html', news=news_item)
            
            if not category:
                flash('La categoría es obligatoria', 'error')
                return render_template('news/edit.html', news=news_item)
            
            # Actualizar noticia
            news_item.title = title
            news_item.content = content
            news_item.category = category
            news_item.is_important = is_important
            news_item.is_published = is_published
            
            db.session.commit()
            
            flash('Noticia actualizada exitosamente', 'success')
            return redirect(url_for('news.show', news_id=news_item.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la noticia: {str(e)}', 'error')
    
    # Obtener categorías
    categories = current_app.config['NEWS_CATEGORIES']
    return render_template('news/edit.html', news=news_item, categories=categories)

@bp.route('/<int:news_id>/delete', methods=['POST'])
@login_required
def delete(news_id):
    """Eliminar noticia"""
    news_item = News.query.get_or_404(news_id)
    
    # Verificar permisos
    if news_item.author_id != current_user.id and not current_user.can_access_admin():
        flash('No tienes permisos para eliminar esta noticia', 'error')
        return redirect(url_for('news.show', news_id=news_item.id))
    
    try:
        db.session.delete(news_item)
        db.session.commit()
        flash('Noticia eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la noticia: {str(e)}', 'error')
    
    return redirect(url_for('news.index'))

@bp.route('/admin')
@login_required
def admin():
    """Panel de administración de noticias"""
    if not current_user.can_access_admin():
        flash('No tienes permisos para acceder al panel de administración', 'error')
        return redirect(url_for('news.index'))
    
    page = request.args.get('page', 1, type=int)
    news = News.query.order_by(News.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('news/admin.html', news=news)

@bp.route('/api/recent')
def api_recent():
    """API para obtener noticias recientes"""
    limit = request.args.get('limit', 5, type=int)
    category = request.args.get('category', '')
    
    query = News.query.filter_by(is_published=True)
    if category:
        query = query.filter_by(category=category)
    
    recent_news = query.order_by(News.created_at.desc()).limit(limit).all()
    
    news_list = []
    for news_item in recent_news:
        news_list.append({
            'id': news_item.id,
            'title': news_item.title,
            'content': news_item.get_excerpt(100),
            'category': news_item.category,
            'is_important': news_item.is_important,
            'created_at': news_item.created_at.isoformat(),
            'author_name': news_item.author.name
        })
    
    return jsonify(news_list)

@bp.route('/<int:news_id>/publish', methods=['POST'])
@login_required
def publish(news_id):
    """Publicar una noticia"""
    if not current_user.can_access_admin():
        return jsonify({'success': False, 'message': 'No tienes permisos'}), 403
    
    news_item = News.query.get_or_404(news_id)
    news_item.is_published = True
    news_item.published_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Noticia publicada correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<int:news_id>/unpublish', methods=['POST'])
@login_required
def unpublish(news_id):
    """Despublicar una noticia"""
    if not current_user.can_access_admin():
        return jsonify({'success': False, 'message': 'No tienes permisos'}), 403
    
    news_item = News.query.get_or_404(news_id)
    news_item.is_published = False
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Noticia despublicada correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500 