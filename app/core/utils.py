# Utility functions

from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from sqlalchemy import select, func
from asgiref.sync import async_to_sync
from app.extensions import db


def api_response(data=None, message=None, status_code=200):
    """Standard API response format."""
    response = {
        'success': status_code < 400,
        'data': data,
        'message': message
    }
    return response, status_code


async def paginate(stmt, page=1, per_page=20, max_per_page=100):
    """Paginate a SQLAlchemy select statement (Async)."""
    page = max(1, page)
    per_page = min(max(1, per_page), max_per_page)
    
    paginated_stmt = stmt.limit(per_page).offset((page - 1) * per_page)
    result = await db.session.execute(paginated_stmt)
    items = result.scalars().all()

    has_next = len(items) == per_page
    has_prev = page > 1
    
    return {
        'items': items,
        'page': page,
        'per_page': per_page,
        'total': 0, # Placeholder
        'pages': 0, # Placeholder
        'has_next': has_next,
        'has_prev': has_prev
    }


def require_role(*roles):
    """Decorator to require specific user roles (JWT)."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                if claims.get('role') not in roles:
                    return api_response(message='Insufficient permissions', status_code=403)
            except Exception as e:
                return api_response(message=str(e), status_code=401)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def async_route(f):
    """Decorator to allow async route handlers in Flask-RESTX."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return async_to_sync(f)(*args, **kwargs)
    return wrapper
