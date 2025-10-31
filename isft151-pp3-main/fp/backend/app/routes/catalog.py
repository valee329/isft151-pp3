from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from ..repositories import catalog_repo
from ..decorators import vendor_required

catalog_bp = Blueprint('catalog', __name__)

@catalog_bp.route('/catalog/create', methods=['GET', 'POST'])
@login_required
@vendor_required
def create_catalog():
    # Verificar si ya tiene un catálogo
    existing_catalog = catalog_repo.get_vendor_catalog(current_user.id)
    if existing_catalog:
        flash('Ya tienes un catálogo creado', 'warning')
        return redirect(url_for('catalog.view_catalog', vendor_id=current_user.id))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('El nombre del catálogo es requerido', 'error')
            return render_template('catalog/create.html')
        
        if catalog_repo.create_catalog(current_user.id, name, description):
            flash('Catálogo creado exitosamente!', 'success')
            return redirect(url_for('catalog.view_catalog', vendor_id=current_user.id))
        
        flash('Error al crear el catálogo', 'error')
    
    return render_template('catalog/create.html')

@catalog_bp.route('/catalog/<int:vendor_id>', methods=['GET'])
def view_catalog(vendor_id):
    catalog = catalog_repo.get_vendor_catalog(vendor_id)
    if not catalog:
        flash('Catálogo no encontrado', 'error')
        return redirect(url_for('feed.index'))
    
    products = catalog_repo.get_catalog_products(catalog['id'])
    return render_template('catalog/view.html', 
                         catalog=catalog, 
                         products=products,
                         vendor_id=vendor_id)

@catalog_bp.route('/catalog/<int:catalog_id>/add_product', methods=['GET', 'POST'])
@login_required
@vendor_required
def add_product(catalog_id):
    # Verificar que el catálogo pertenece al vendor actual
    catalog = catalog_repo.get_vendor_catalog(current_user.id)
    if not catalog or catalog['id'] != catalog_id:
        flash('No tienes permiso para agregar productos a este catálogo', 'error')
        return redirect(url_for('feed.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price')
        image_url = request.form.get('image_url', '').strip()
        
        # Validaciones
        if not name:
            flash('El nombre del producto es requerido', 'error')
            return render_template('catalog/add_product.html', catalog_id=catalog_id)
        
        try:
            price = float(price)
            if price <= 0:
                raise ValueError
        except (TypeError, ValueError):
            flash('El precio debe ser un número mayor que 0', 'error')
            return render_template('catalog/add_product.html', catalog_id=catalog_id)
        
        if catalog_repo.add_product(catalog_id, name, description, price, image_url):
            flash('Producto agregado exitosamente!', 'success')
            return redirect(url_for('catalog.view_catalog', vendor_id=current_user.id))
        
        flash('Error al agregar el producto', 'error')
    
    return render_template('catalog/add_product.html', catalog_id=catalog_id)