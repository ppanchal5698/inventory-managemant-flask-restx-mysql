# WSGI / before_request hooks

from flask import request, g
import time


def register_middleware(app):
    """Register middleware hooks."""

    @app.before_request
    def before_request():
        """Execute before each request."""
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        """Execute after each request."""
        # Add request timing header
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            response.headers['X-Request-Time'] = f'{elapsed:.4f}s'
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response

    @app.teardown_request
    def teardown_request(exception=None):
        """Execute at the end of each request."""
        pass
