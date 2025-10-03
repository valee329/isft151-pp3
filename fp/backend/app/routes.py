from flask import render_template, request, redirect, session, flash
from models import rows_to_posts  # Using Post model for the feed list

def register_routes(app, get_db_connection, user_has_profile):
    """
    Attach all route handlers to the Flask app.
    """

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['POST'])
    def login():
        name = request.form.get('txtName')
        lastname = request.form.get('txtLastname')
        password = request.form.get('txtPassword')

        conn = get_db_connection()
        if not conn:
            flash('DB connection error.')
            return redirect('/')

        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT id, name, lastname
                FROM user
                WHERE name=%s AND lastname=%s AND password=%s
            """, (name, lastname, password))
            user = cur.fetchone()
            if user:
                session['logged_in'] = True
                session['user_id'] = user['id']
                session['user_name'] = f"{user['name']} {user['lastname']}"
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
        return redirect('/')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form.get('txtName')
            lastname = request.form.get('txtLastname')
            role = request.form.get('txtRole')
            password = request.form.get('txtPassword')

            if not all([name, lastname, role, password]):
                flash('All fields required.')
                return render_template('register.html')

            conn = get_db_connection()
            if not conn:
                flash('DB connection error.')
                return render_template('register.html')

            cur = conn.cursor()
            try:
                cur.execute("""
                    INSERT INTO user (name, lastname, id_role, password)
                    VALUES (%s, %s, %s, %s)
                """, (name, lastname, role, password))
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

    @app.route('/complete_profile', methods=['GET', 'POST'])
    def complete_profile():
        if not session.get('logged_in'):
            return redirect('/')
        user_id = session.get('user_id')
        if user_has_profile(user_id):
            return redirect('/feed')

        if request.method == 'POST':
            bio = request.form.get('bio')
            location = request.form.get('location')
            avatar_url = request.form.get('avatar_url')

            conn = get_db_connection()
            if not conn:
                flash('DB connection error.')
                return render_template('profile.html')

            cur = conn.cursor()
            try:
                cur.execute("""
                    INSERT INTO user_profile (user_id, bio, location, avatar_url)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, bio, location, avatar_url))
                conn.commit()
                return redirect('/feed')
            except Exception as e:
                print(f"Profile save error: {e}")
                flash('Could not save profile.')
            finally:
                cur.close()
                conn.close()
        return render_template('profile.html')

    @app.route('/profile')
    def profile():
        if not session.get('logged_in'):
            return redirect('/')
        user_id = session.get('user_id')

        conn = get_db_connection()
        data = None
        if conn:
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
                           p.created_at AS profile_created
                    FROM user u
                    JOIN role r ON r.id_role = u.id_role
                    LEFT JOIN user_profile p ON p.user_id = u.id
                    WHERE u.id = %s
                """, (user_id,))
                data = cur.fetchone()
            except Exception as e:
                print(f"Profile fetch error: {e}")
            finally:
                cur.close()
                conn.close()

        if not user_has_profile(user_id):
            return redirect('/complete_profile')
        return render_template('view_profile.html', user=data)

    @app.route('/feed')
    def feed():
        if not session.get('logged_in'):
            return redirect('/')

        conn = get_db_connection()
        posts = []
        if conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute("""
                    SELECT posts.id,
                           posts.content,
                           posts.created_at,
                           user.id AS user_id,
                           user.name,
                           user.lastname
                    FROM posts
                    JOIN user ON posts.user_id = user.id
                    ORDER BY posts.created_at DESC
                """)
                rows = cur.fetchall()
                posts = rows_to_posts(rows)  # list[Post]
            except Exception as e:
                print(f"Feed error: {e}")
            finally:
                cur.close()
                conn.close()
        return render_template('feed.html', posts=posts)

    @app.route('/create_post', methods=['POST'])
    def create_post():
        if not session.get('logged_in'):
            return redirect('/')

        content = request.form.get('content')
        user_id = session.get('user_id')
        if not content or not content.strip():
            return redirect('/feed')

        conn = get_db_connection()
        if not conn:
            flash('DB connection error.')
            return redirect('/feed')

        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO posts (user_id, content)
                VALUES (%s, %s)
            """, (user_id, content.strip()))
            conn.commit()
        except Exception as e:
            print(f"Create post error: {e}")
            flash('Could not create post.')
        finally:
            cur.close()
            conn.close()
        return redirect('/feed')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect('/')