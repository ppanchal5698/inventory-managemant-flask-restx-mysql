# Application Middleware

from werkzeug.wrappers import Request, Response, ResponseStream

def register_middleware(app):
    """Register middleware for the Flask application."""

    @app.after_request
    def add_security_headers(response):
        """Add security headers to response."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # HSTS (Strict-Transport-Security) only if HTTPS
        # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    @app.route('/api/ping')
    def health_check():
        """Health check endpoint."""
        return {'status': 'ok'}, 200
