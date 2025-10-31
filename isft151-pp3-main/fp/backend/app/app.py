import os
from flask import Flask
from flask_login import LoginManager
from .config import SECRET_KEY  # changed to relative
from .routes.auth import auth_bp
from .routes.catalog import catalog_bp
from flask_login import current_user

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'templates')
        ),
        static_folder=os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'static')
        )
    )

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # User loader callback
    @login_manager.user_loader
    def load_user(user_id):
        # Aquí debes retornar tu objeto usuario desde la BD
        from .repositories.user_repo import fetch_user
        return fetch_user(user_id)

    @app.context_processor
    def utility_processor():
        return dict(current_user=current_user)
    
    app.secret_key = SECRET_KEY
    app.config['SESSION_TYPE'] = 'filesystem'

    from .routes.auth import auth_bp
    from .routes.vendor import vendor_bp
    from .routes.feed import feed_bp
    from .routes.health import health_bp
    from .routes.catalog import catalog_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(vendor_bp)
    app.register_blueprint(feed_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(catalog_bp)

    return app