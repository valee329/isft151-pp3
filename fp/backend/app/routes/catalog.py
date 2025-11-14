import os
import uuid
from flask import render_template, request, redirect, flash, session, current_app, url_for
from werkzeug.utils import secure_filename
from app.repositories import catalog_repo
from app.db import get_db_connection

# Carpeta de destino para las imágenes
static_folder = os.path.join(
    os.path.dirname(__file__), '..', 'static', 'product_images'
)
os.makedirs(static_folder, exist_ok=True)

# Extensiones de imagen permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    """Verifica si la extensión del archivo es válida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def register_catalog_routes(app, get_db_connection):

    @app.route("/catalog")
    def catalog_list():
        """Muestra todos los productos del catálogo"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.id, c.name, c.price, c.description, c.image_url,
                   u.name AS vendor_name
            FROM catalog_item c
            JOIN user u ON c.vendor_id = u.id
            ORDER BY c.created_at DESC
        """)
        items = cursor.fetchall()
        print("ITEMS ENCONTRADOS:", items)
        cursor.close()
        conn.close()
        return render_template("catalog.html", items=items)

    @app.route('/catalog/<int:item_id>')
    def catalog_view(item_id):
        """Muestra el detalle de un producto específico."""
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
            flash('Item no encontrado.')
            return redirect('/catalog')

        return render_template('view_catalog.html', item=item)

    @app.route('/catalog/create', methods=['GET', 'POST'])
    def catalog_create():
        """Permite crear un nuevo producto en el catálogo."""
        
        if not session.get('logged_in'):
            flash('Debes iniciar sesión para crear un producto.')
            return redirect('/')

        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            price = request.form.get('price')

           
            file = request.files.get('product_image')
            if not file or file.filename == '':
                flash('Por favor selecciona una imagen.')
                return redirect(request.url)

            if not allowed_file(file.filename):
                flash('Formato de imagen no permitido (usa png, jpg, jpeg o gif).')
                return redirect(request.url)

            
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"

            
            image_folder = os.path.join(current_app.static_folder, 'product_images')
            os.makedirs(image_folder, exist_ok=True)

            file_path = os.path.join(image_folder, unique_name)
            file.save(file_path)

            
            db_image_path = f"product_images/{unique_name}"

            
            vendor_id = session.get('user_id')
            if not vendor_id:
                flash('Error: No se encontró el usuario logueado.')
                return redirect('/')

            
            conn = get_db_connection()
            if conn:
                try:
                    catalog_repo.create_item(conn, name, description, price, db_image_path, vendor_id)
                    
                    return redirect('/catalog')
                except Exception as e:
                    print(f"Catalog create error: {e}")
                    print("Usuario logueado:", session.get('user_id'))
                    flash('No se pudo crear el producto. Verifica la consola para más detalles.')
                finally:
                    conn.close()

      
        return render_template('create_catalog.html')
