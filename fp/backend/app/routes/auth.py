from flask import Blueprint, render_template, request, redirect, session, flash, jsonify
from ..db import get_db_connection
from ..repositories.user_repo import user_has_profile
import random, string

auth_bp = Blueprint('auth', __name__)

# helper to create/store a new captcha
def _new_captcha(n: int = 5) -> str:
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))
    session['captcha_code'] = code
    return code

@auth_bp.route('/')
def index():
    code = _new_captcha()
    return render_template('index.html', captcha_code=code)

@auth_bp.route('/captcha-refresh')
def captcha_refresh():
    code = _new_captcha()
    return jsonify({'code': code})

@auth_bp.route('/login', methods=['POST'])
def login():
    name = request.form.get('txtName')
    lastname = request.form.get('txtLastname')
    password = request.form.get('txtPassword')
    captcha_in = (request.form.get('captcha_input') or '').strip().upper()

    # validate captcha before hitting DB
    expected = (session.get('captcha_code') or '').strip().upper()
    if not captcha_in or captcha_in != expected:
        flash('Invalid captcha.')
        _new_captcha()
        return redirect('/')

    conn = get_db_connection()
    if not conn:
        flash('DB connection error.')
        _new_captcha()
        return redirect('/')

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT id, name, lastname
            FROM `user`
            WHERE name=%s AND lastname=%s AND password=%s
        """, (name, lastname, password))
        user = cur.fetchone()
        if user:
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['user_name'] = f"{user['name']} {user['lastname']}"
            print(" LOGIN EXITOSO - SESIÓN:", dict(session))
            if not user_has_profile(user['id']):
                return redirect('/complete_profile')
            return redirect('/feed')
        flash('Invalid credentials.')
    except Exception as e:
        print(f"Login error: {e}")
        flash('Error during login.')
    finally:
        cur.close()
        conn.close()
        _new_captcha()  # rotate captcha after each attempt
    return redirect('/')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('txtName')
        lastname = request.form.get('txtLastname')
        role = request.form.get('txtRole')  # expects '1' or '2'
        password = request.form.get('txtPassword')
        confirm_password = request.form.get('txtConfirmPassword')

        if not all([name, lastname, role, password, confirm_password]):
            flash('All fields required.')
            return render_template('register.html', name=name, lastname=lastname, role=role)

        if password != confirm_password:
            flash('Passwords do not match.')
            return render_template('register.html', name=name, lastname=lastname, role=role)

        conn = get_db_connection()
        if not conn:
            flash('DB connection error.')
            return render_template('register.html', name=name, lastname=lastname, role=role)

        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO `user` (name, lastname, id_role, password)
                VALUES (%s, %s, %s, %s)
            """, (name, lastname, int(role), password))
            conn.commit()
            flash('Registered successfully. Log in now.')
            return redirect('/')
        except Exception as e:
            print(f"Register error: {e}")
            flash('Registration failed.')
        finally:
            cur.close()
            conn.close()
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')