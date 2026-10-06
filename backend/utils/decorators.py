from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required

def role_required(required_role):
    """
    Decorator to ensure the authenticated user has the specified role.
    Usage: @role_required('Admin')
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')

            if user_role != required_role:
                return jsonify({
                    'error': f'Access denied. {required_role} privileges required.'
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator