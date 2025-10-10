from ..db import get_db_connection

def get_or_create_role(description: str):
    description = description.lower().strip()
    conn = get_db_connection()
    if not conn:
        return None
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_role FROM role WHERE description=%s", (description,))
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO role (description) VALUES (%s)", (description,))
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        print(f"[ROLE] Error: {e}")
        return None
    finally:
        cur.close()
        conn.close()