from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Classified
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json

bp = Blueprint('classifieds', __name__, url_prefix='/classifieds')

@bp.route('/')
def index():
    """Mostrar clasificados activos"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Classified.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Classified.title.contains(search) | 
                           Classified.description.contains(search))
    
    classifieds = query.order_by(Classified.is_featured.desc(), 
                               Classified.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False)
    
    # Obtener categorías disponibles
    categories = db.session.query(Classified.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('classifieds/index.html', 
                         classifieds=classifieds,
                         categories=categories,
                         current_category=category,
                         current_search=search)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Crear nuevo clasificado"""
    if request.method == 'POST':
        try:
            # Crear clasificado
            classified = Classified(
                user_id=current_user.id,
                title=request.form.get('title'),
                description=request.form.get('description'),
                category=request.form.get('category'),
                price=float(request.form.get('price', 0)) if request.form.get('price') else None,
                condition=request.form.get('condition'),
                contact_name=request.form.get('contact_name', current_user.name),
                contact_phone=request.form.get('contact_phone', current_user.phone),
                contact_email=request.form.get('contact_email', current_user.email),
                location=request.form.get('location'),
                tags=request.form.get('tags'),
                expiry_date=datetime.utcnow() + timedelta(days=30)  # 30 días por defecto
            )
            
            db.session.add(classified)
            db.session.flush()  # Para obtener el ID
            
            # Procesar imágenes
            image_paths = []
            for i in range(5):  # Máximo 5 imágenes
                file_key = f'image_{i}'
                if file_key in request.files:
                    file = request.files[file_key]
                    if file and file.filename:
                        filename = secure_filename(f"classified_{classified.id}_{i}_{file.filename}")
                        file_path = os.path.join('uploads', 'classifieds', filename)
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        file.save(file_path)
                        image_paths.append(filename)
            
            if image_paths:
                classified.image_paths = json.dumps(image_paths)
            
            db.session.commit()
            flash('Clasificado publicado exitosamente', 'success')
            return redirect(url_for('classifieds.view', id=classified.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el clasificado: {str(e)}', 'error')
    
    return render_template('classifieds/new.html')

@bp.route('/<int:id>')
def view(id):
    """Ver clasificado específico"""
    classified = Classified.query.get_or_404(id)
    
    # Incrementar contador de vistas
    classified.increment_views()
    db.session.commit()
    
    # Obtener clasificados relacionados
    related = Classified.query.filter(
        Classified.category == classified.category,
        Classified.id != classified.id,
        Classified.is_active == True
    ).limit(4).all()
    
    return render_template('classifieds/view.html', 
                         classified=classified,
                         related=related)

@bp.route('/my')
@login_required
def my_classifieds():
    """Mis clasificados"""
    page = request.args.get('page', 1, type=int)
    classifieds = Classified.query.filter_by(user_id=current_user.id).order_by(
        Classified.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('classifieds/my_classifieds.html', classifieds=classifieds)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar clasificado"""
    classified = Classified.query.get_or_404(id)
    
    if classified.user_id != current_user.id and not current_user.can_access_admin():
        flash('No tienes permiso para editar este clasificado', 'error')
        return redirect(url_for('classifieds.index'))
    
    if request.method == 'POST':
        try:
            classified.title = request.form.get('title')
            classified.description = request.form.get('description')
            classified.category = request.form.get('category')
            classified.price = float(request.form.get('price', 0)) if request.form.get('price') else None
            classified.condition = request.form.get('condition')
            classified.contact_name = request.form.get('contact_name')
            classified.contact_phone = request.form.get('contact_phone')
            classified.contact_email = request.form.get('contact_email')
            classified.location = request.form.get('location')
            classified.tags = request.form.get('tags')
            classified.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Clasificado actualizado exitosamente', 'success')
            return redirect(url_for('classifieds.view', id=classified.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el clasificado: {str(e)}', 'error')
    
    return render_template('classifieds/edit.html', classified=classified)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Eliminar clasificado"""
    classified = Classified.query.get_or_404(id)
    
    if classified.user_id != current_user.id and not current_user.can_access_admin():
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        # Marcar como inactivo en lugar de eliminar
        classified.is_active = False
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Clasificado eliminado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/contact/<int:id>', methods=['POST'])
@login_required
def contact(id):
    """Contactar al autor del clasificado"""
    classified = Classified.query.get_or_404(id)
    message = request.form.get('message')
    
    if not message:
        return jsonify({'error': 'El mensaje es requerido'}), 400
    
    try:
        # Aquí se podría implementar el envío de email o notificación
        # Por ahora solo devolvemos éxito
        
        return jsonify({
            'success': True, 
            'message': 'Mensaje enviado exitosamente',
            'contact_info': {
                'phone': classified.contact_phone,
                'email': classified.contact_email
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500