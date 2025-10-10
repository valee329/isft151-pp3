from ..db import get_db_connection

VENDOR_DESC = "vendor"

def fetch_vendor(vendor_id):
    conn = get_db_connection()
    if not conn:
        return None
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT u.id,
                   u.name,
                   u.lastname,
                   p.bio,
                   p.location,
                   p.avatar_url,
                   p.created_at
            FROM user u
            JOIN role r ON r.id_role = u.id_role
            LEFT JOIN user_profile p ON p.user_id = u.id
            WHERE u.id = %s
              AND (r.description = %s OR r.id_role = 1)
        """, (vendor_id, VENDOR_DESC))
        return cur.fetchone()
    except Exception as e:
        print(f"[VENDOR] fetch error: {e}")
        return None
    finally:
        try:
            cur.close()
        except:
            pass
        if conn:
            conn.close()

def list_vendors():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT u.id,
               u.name AS first_name,
               u.lastname AS last_name,
               up.avatar_url,
               up.bio,
               up.location
        FROM user u
        JOIN role r ON r.id_role = u.id_role
        LEFT JOIN user_profile up ON up.user_id = u.id
        WHERE r.description = %s
        ORDER BY u.id DESC
    """, ("vendor",))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows