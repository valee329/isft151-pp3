def list_items(conn):
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT c.id, c.name, c.description, c.price, c.image_url, c.created_at,
                   u.name AS vendor_name
            FROM catalog_item c
            JOIN user u ON c.vendor_id = u.id
            ORDER BY c.created_at DESC
        """)
        return cur.fetchall()
    finally:
        cur.close()

def get_item(conn, item_id):
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT c.id, c.name, c.description, c.price, c.image_url, c.created_at,
                   u.name AS vendor_name
            FROM catalog_item c
            JOIN user u ON c.vendor_id = u.id
            WHERE c.id = %s
        """, (item_id,))
        return cur.fetchone()
    finally:
        cur.close()

def create_item(conn, name, description, price, image_url, vendor_id):
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO catalog_item (name, description, price, image_url, vendor_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, description, price, image_url, vendor_id))
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
