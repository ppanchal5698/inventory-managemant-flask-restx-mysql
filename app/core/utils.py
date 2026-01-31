# Utility functions

from functools import wraps
from flask import jsonify, request
from flask_login import current_user


def api_response(data=None, message=None, status_code=200):
    """Standard API response format.
    
    Returns dict and status_code for Flask-RESTX compatibility.
    Flask-RESTX handles JSON serialization automatically.
    """
    response = {
        'success': status_code < 400,
        'data': data,
        'message': message
    }
    return response, status_code


def paginate(query, page=1, per_page=20, max_per_page=100):
    """Paginate a SQLAlchemy query."""
    page = max(1, page)
    per_page = min(max(1, per_page), max_per_page)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'items': pagination.items,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }


def require_role(*roles):
    """Decorator to require specific user roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return api_response(message='Authentication required', status_code=401)
            if current_user.role not in roles:
                return api_response(message='Insufficient permissions', status_code=403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
