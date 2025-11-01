# Nuevo módulo de rutas para el catálogo
import os
import uuid
from flask import render_template, request, redirect, flash, session, current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def register_catalog_routes(app, get_db_connection):
    upload_folder = os.path.join(app.static_folder, 'product_images')
    os.makedirs(upload_folder, exist_ok=True)

    @app.route('/catalog')
    def catalog_list():
        if not session.get('logged_in'):
            return redirect('/')
        
        conn = get_db_connection()
        items = []
        if conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute("""
                    SELECT c.*, u.name as vendor_name 
                    FROM catalog_item c 
                    JOIN user u ON c.vendor_id = u.id 
                    ORDER BY c.created_at DESC
                """)
                items = cur.fetchall()
            except Exception as e:
                print(f"Catalog fetch error: {e}")
            finally:
                cur.close()
                conn.close()
        return render_template('catalog.html', items=items)

    @app.route('/catalog/<int:item_id>')
    def catalog_view(item_id):
        conn = get_db_connection()
        item = None
        if conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute("""
                    SELECT c.*, u.name as vendor_name 
                    FROM catalog_item c
                    JOIN user u ON c.vendor_id = u.id 
                    WHERE c.id = %s
                """, (item_id,))
                item = cur.fetchone()
            except Exception as e:
                print(f"Catalog item fetch error: {e}")
            finally:
                cur.close()
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
            
            if 'product_image' not in request.files:
                flash('No file uploaded')
                return redirect(request.url)
                
            file = request.files['product_image']
            if file.filename == '':
                flash('No file selected')
                return redirect(request.url)
                
            if file and allowed_file(file.filename):
                original = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4().hex}_{original}"
                file_path = os.path.join('product_images', unique_name)
                file.save(os.path.join(current_app.static_folder, file_path))
                
                conn = get_db_connection()
                if conn:
                    cur = conn.cursor()
                    try:
                        cur.execute("""
                            INSERT INTO catalog_item (name, description, price, image_url, vendor_id) 
                            VALUES (%s, %s, %s, %s, %s)
                        """, (name, description, price, file_path, session['user_id']))
                        conn.commit()
                        flash('Item created successfully!')
                        return redirect('/catalog')
                    except Exception as e:
                        print(f"Catalog create error: {e}")
                        flash('Could not create catalog item.')
                    finally:
                        cur.close()
                        conn.close()
        return render_template('create_catalog.html')