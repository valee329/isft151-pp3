from ..db import get_db_connection

def insert_profile(user_id, bio, location, avatar_url):
    conn = get_db_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO user_profile (user_id, bio, location, avatar_url)
            VALUES (%s, %s, %s, %s)
        """, (user_id, bio, location, avatar_url))
        conn.commit()
        return True
    except Exception as e:
        print(f"[PROFILE] Insert error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def fetch_profile_with_role(user_id):
    conn = get_db_connection()
    if not conn:
        return None
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT u.id,
                   u.name,
                   u.lastname,
                   r.description AS role,
                   p.bio,
                   p.location,
                   p.avatar_url,
                   p.created_at
            FROM user u
            JOIN role r ON r.id_role = u.id_role
            LEFT JOIN user_profile p ON p.user_id = u.id
            WHERE u.id = %s
        """, (user_id,))
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()