from ..db import get_db_connection

def find_user_by_credentials(name, lastname, password):
    conn = get_db_connection()
    if not conn:
        return None
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT id, name, lastname, id_role
            FROM user
            WHERE name=%s AND lastname=%s AND password=%s
            LIMIT 1
        """, (name, lastname, password))
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()

def create_user(name, lastname, role_id, password):
    conn = get_db_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO user (name, lastname, id_role, password)
            VALUES (%s, %s, %s, %s)
        """, (name, lastname, role_id, password))
        conn.commit()
        return True
    except Exception as e:
        print(f"[USER] Insert error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def user_has_profile(user_id: int) -> bool:
    conn = get_db_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM user_profile WHERE user_id=%s LIMIT 1", (user_id,))
        return cur.fetchone() is not None
    except Exception as e:
        print(f"[USER] user_has_profile error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def get_user_with_profile(user_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT u.id,
               u.name AS first_name,
               u.lastname AS last_name,
               u.name AS username,          -- adjust if you have a username column
               u.email,
               r.description AS role,
               up.avatar_url,
               up.bio,
               up.location,
               up.created_at
        FROM user u
        LEFT JOIN user_profile up ON up.user_id = u.id
        LEFT JOIN role r ON r.id_role = u.id_role
        WHERE u.id = %s
    """, (user_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row