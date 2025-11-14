from flask import Blueprint, render_template, redirect, session, flash, current_app
from ..repositories.user_repo import user_has_profile
from ..repositories.vendor_repo import list_vendors
from ..db import get_db_connection

feed_bp = Blueprint('feed', __name__)

@feed_bp.route('/feed')
def feed():
    if not session.get('logged_in'):
        return redirect('/')
    user_id = session.get('user_id')
    if not user_has_profile(user_id):
        return redirect('/complete_profile')

    conn = get_db_connection()
    if not conn:
        flash('DB connection error'); return render_template('feed.html', vendors=[])

    VENDOR_ROLE_ID = 1  # per your DB

    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT u.id, u.name, u.lastname, p.bio, p.location, p.avatar_url
        FROM `user` u
        LEFT JOIN user_profile p ON p.user_id = u.id
        WHERE u.id_role = %s
        ORDER BY u.id DESC
    """, (VENDOR_ROLE_ID,))
    vendors = cur.fetchall()
    cur.close(); conn.close()

    if not vendors:
        flash('No se encontraron proveedores con el rol ID 1.')
    return render_template('feed.html', vendors=vendors)