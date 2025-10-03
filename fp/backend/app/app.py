import os
import mysql.connector
from mysql.connector import Error
from flask import Flask
from config import DB_CONFIG, SECRET_KEY

TEMPLATE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'templates')
)

app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.secret_key = SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def user_has_profile(user_id: int) -> bool:
    conn = get_db_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM user_profile WHERE user_id=%s", (user_id,))
        return cur.fetchone() is not None
    finally:
        cur.close()
        conn.close()

from routes import register_routes
register_routes(app, get_db_connection, user_has_profile)

if __name__ == '__main__':
    app.run(debug=True)