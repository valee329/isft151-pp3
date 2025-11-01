# Repositorio simple para operaciones del catálogo
def list_items(conn):
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id, name, description, price, created_at FROM catalog_item ORDER BY created_at DESC")
        return cur.fetchall()
    finally:
        cur.close()

def get_item(conn, item_id):
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id, name, description, price, created_at FROM catalog_item WHERE id=%s", (item_id,))
        return cur.fetchone()
    finally:
        cur.close()

def create_item(conn, name, description, price):
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO catalog_item (name, description, price) VALUES (%s, %s, %s)",
                    (name, description, price))
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()