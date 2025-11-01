import os
from flask import Flask
from .config import SECRET_KEY  # changed to relative
from .routes.auth import auth_bp
from .db import get_db_connection
from .repositories.user_repo import user_has_profile
from .routes import register_routes, register_catalog_routes

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
    app.secret_key = SECRET_KEY
    app.config['SESSION_TYPE'] = 'filesystem'

    from .routes.vendor import vendor_bp
    from .routes.feed import feed_bp
    from .routes.health import health_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(vendor_bp)
    app.register_blueprint(feed_bp)
    app.register_blueprint(health_bp)

    register_routes(app, get_db_connection, user_has_profile)
    register_catalog_routes(app, get_db_connection)

    return app