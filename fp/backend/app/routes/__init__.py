from .auth import auth_bp
from .main import register_routes
from .catalog import register_catalog_routes

__all__ = ['register_routes', 'register_catalog_routes']