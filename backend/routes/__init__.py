from .admin_routes import admin_bp
from .user_routes import user_bp
from .staff_routes import staff_bp

__all__ = ['admin_bp', 'user_bp', 'staff_bp']