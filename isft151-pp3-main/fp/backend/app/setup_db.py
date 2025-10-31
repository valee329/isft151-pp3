import time
import os
import mysql.connector
from mysql.connector import Error
from .config import DB_CONFIG

SQL_FILE = os.path.join(os.path.dirname(__file__), "setup_db.sql")

def get_db_connection():
    start = time.time()
    try:
        conn = mysql.connector.connect(
            **DB_CONFIG,
            connection_timeout=5
        )
        conn.ping(reconnect=True, attempts=1, delay=0)
        return conn
    except Error as e:
        elapsed = (time.time() - start) * 1000
        print(f"[DB] Connection failed after {elapsed:.1f} ms: {e}")
        return None

def setup_database():
    print("[DB] Starting database setup...")
    if not os.path.exists(SQL_FILE):
        print(f"[DB] SQL file not found: {SQL_FILE}")
        return False

    cfg = DB_CONFIG.copy()
    cfg.pop('database', None)  # allow CREATE DATABASE

    try:
        conn = mysql.connector.connect(**cfg, connection_timeout=5)
    except Error as e:
        print(f"[DB] Connection error: {e}")
        return False

    try:
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            script = f.read()
        cur = conn.cursor()
        for stmt in [s.strip() for s in script.split(';') if s.strip()]:
            cur.execute(stmt)
        conn.commit()
        print("[DB] Database setup completed successfully.")
        return True
    except Error as e:
        print(f"[DB] Execution error: {e}")
        return False
    finally:
        try:
            cur.close()
        except:
            pass
        conn.close()