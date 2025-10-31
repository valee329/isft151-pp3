from ..db import get_db_connection

def has_vendor_catalog(vendor_id):
    conn = get_db_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT EXISTS(
                SELECT 1 FROM catalog 
                WHERE vendor_id = %s
            )
        """, (vendor_id,))
        return cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()

def create_catalog(vendor_id, name, description):
    conn = get_db_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO catalog (vendor_id, name, description)
            VALUES (%s, %s, %s)
        """, (vendor_id, name, description))
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        print(f"[CATALOG] Create error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def get_vendor_catalog(vendor_id):
    conn = get_db_connection()
    if not conn:
        return None
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT c.*, COUNT(p.id) as product_count 
            FROM catalog c
            LEFT JOIN product p ON p.catalog_id = c.id
            WHERE c.vendor_id = %s
            GROUP BY c.id
        """, (vendor_id,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()



def add_product(catalog_id, name, description, price, image_url=None):
    conn = get_db_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO product (catalog_id, name, description, price, image_url)
            VALUES (%s, %s, %s, %s, %s)
        """, (catalog_id, name, description, price, image_url))
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        print(f"[CATALOG] Add product error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def get_catalog_products(catalog_id):
    conn = get_db_connection()
    if not conn:
        return None
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT * FROM product 
            WHERE catalog_id = %s
            ORDER BY created_at DESC
        """, (catalog_id,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()