from flask import Blueprint
from ..db import get_db_connection

health_bp = Blueprint('health', __name__)

@health_bp.route('/health/app')
def health_app():
    return {"app": "ok"}

@health_bp.route('/health/db')
def health_db():
    conn = get_db_connection()
    if conn:
        conn.close()
        return {"db": "ok"}
    return ({"db": "down"}, 500)