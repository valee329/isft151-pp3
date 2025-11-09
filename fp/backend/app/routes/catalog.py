import os
import uuid
from flask import render_template, request, redirect, flash, session, current_app, url_for
from werkzeug.utils import secure_filename
from app.repositories import catalog_repo
from app.db import get_db_connection

# Carpeta de destino para las imágenes
static_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'static', 'product_images')
)
os.makedirs(static_folder, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def register_catalog_routes(app, get_db_connection):
    @app.route("/catalog")
    def catalog_list():
        """Muestra todos los productos del catálogo"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, price, description, image_url FROM product")
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("catalog.html", items=items)
    
    @app.route('/catalog/<int:item_id>')
    def catalog_view(item_id):
        conn = get_db_connection()
        item = None
        if conn:
            try:
                item = catalog_repo.get_item(conn, item_id)
            except Exception as e:
                print(f"Catalog item fetch error: {e}")
            finally:
                conn.close()
        if not item:
            flash('Item not found.')
            return redirect('/catalog')
        return render_template('view_catalog.html', item=item)

    @app.route('/catalog/create', methods=['GET', 'POST'])
    def catalog_create():
        if not session.get('logged_in'):
            return redirect('/')

        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            price = request.form.get('price')

            file = request.files.get('product_image')
            if not file or file.filename == '':
                flash('Please select an image.')
                return redirect(request.url)
            if not allowed_file(file.filename):
                flash('Invalid image format.')
                return redirect(request.url)

            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join('product_images', unique_name)
            file.save(os.path.join(static_folder, unique_name))

            conn = get_db_connection()
            if conn:
                try:
                    catalog_repo.create_item(conn, name, description, price, file_path, session['user_id'])
                    flash('Item created successfully!')
                    return redirect('/catalog')
                except Exception as e:
                    print(f"Catalog create error: {e}")
                    flash('Could not create catalog item.')
                finally:
                    conn.close()
        return render_template('create_catalog.html')
