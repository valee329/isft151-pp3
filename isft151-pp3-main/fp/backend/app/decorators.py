from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def vendor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar si el usuario está autenticado y es vendor
        if not current_user.is_authenticated:
            flash('Please log in first.', 'error')
            return redirect(url_for('auth.login'))
            
        if current_user.role != 'vendor':
            flash('Access denied. Vendor role required.', 'error')
            return redirect(url_for('main.index'))
            
        return f(*args, **kwargs)
    return decorated_function