import time
import mysql.connector
from mysql.connector import Error
from .config import DB_CONFIG  # relative

def get_db_connection():
    start = time.time()
    try:
        conn = mysql.connector.connect(**DB_CONFIG, connection_timeout=5)
        conn.ping(reconnect=True, attempts=1, delay=0)
        return conn
    except Error as e:
        elapsed = (time.time() - start) * 1000
        print(f"[DB] Connection failed after {elapsed:.1f} ms: {e}")
        return None