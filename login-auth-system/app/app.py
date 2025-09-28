from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG, SECRET_KEY
import os

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'

# Database connection function
def get_db_connection():
    from config import DB_CONFIG
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Function to execute the SQL script (handles procedures safely)
def execute_sql_script(script_path: str):
    if not os.path.isfile(script_path):
        print(f"SQL script not found: {script_path}")
        return
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            with open(script_path, 'r', encoding='utf-8') as sql_file:
                sql_script = sql_file.read()
            for _ in cursor.execute(sql_script, multi=True):
                pass
            connection.commit()
            print("SQL script executed successfully.")
        except Error as e:
            print(f"Error executing SQL script: {e}")
        finally:
            cursor.close()
            connection.close()
    else:
        print("Unable to connect to the database.")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    name = request.form.get('txtName')
    lastname = request.form.get('txtLastname')
    password = request.form.get('txtPassword')

    if not all([name, lastname, password]):
        flash('All fields are required.')
        return redirect('/')

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            # Direct query instead of stored procedure
            cursor.execute("""
                SELECT id, name, lastname
                FROM user
                WHERE name = %s AND lastname = %s AND password = %s
            """, (name, lastname, password))
            user = cursor.fetchone()
            if user:
                session['logged_in'] = True
                session['user_id'] = user['id']
                session['user_name'] = f"{user['name']} {user['lastname']}"
                return redirect('/feed')
            else:
                flash('Invalid credentials. Please try again.')
                return redirect('/')
        except Error as e:
            print(f"Database error: {e}")
            flash('An error occurred. Please try again later.')
        finally:
            cursor.close()
            connection.close()
    else:
        flash('Unable to connect to the database.')
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('txtName')
        lastname = request.form.get('txtLastname')
        role = request.form.get('txtRole')
        password = request.form.get('txtPassword')

        if not all([name, lastname, role, password]):
            flash('All fields are required.')
            return render_template('register.html')

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    INSERT INTO user (name, lastname, id_role, password)
                    VALUES (%s, %s, %s, %s)
                """, (name, lastname, role, password))
                connection.commit()
                flash('Registration successful! You can now log in.')
                return redirect('/')
            except Error as e:
                print(f"Database error: {e}")
                flash('An error occurred. Please try again later.')
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Unable to connect to the database.')
    return render_template('register.html')

@app.route('/feed')
def feed():
    if not session.get('logged_in'):
        return redirect('/')

    connection = get_db_connection()
    posts = []
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT posts.id, posts.content, posts.created_at, user.name, user.lastname
                FROM posts
                JOIN user ON posts.user_id = user.id
                ORDER BY posts.created_at DESC
            """)
            posts = cursor.fetchall()
        except Error as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
            connection.close()
    return render_template('feed.html', posts=posts)

@app.route('/create_post', methods=['POST'])
def create_post():
    if not session.get('logged_in'):
        return redirect('/')

    content = request.form.get('content')
    user_id = session.get('user_id')

    if content and user_id:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    INSERT INTO posts (user_id, content)
                    VALUES (%s, %s)
                """, (user_id, content))
                connection.commit()
            except Error as e:
                print(f"Database error: {e}")
            finally:
                cursor.close()
                connection.close()
    return redirect('/feed')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Test database connection
def test_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Database connection successful!")
        else:
            print("Failed to connect to the database.")
    except mysql.connector.Error as e:
        print(f"Error connecting to the database: {e}")
    finally:
        try:
            if connection.is_connected():
                connection.close()
        except NameError:
            pass

if __name__ == '__main__':
    # Optional: uncomment to (re)run schema (ensure idempotent SQL)
    # execute_sql_script(os.path.join(os.path.dirname(__file__), 'setup_db.sql'))
    test_db_connection()
    app.run(debug=True)