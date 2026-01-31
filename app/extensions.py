# db, migrate, cache, login_manager, api

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_login import LoginManager
from flask_restx import Api

db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
login_manager = LoginManager()

# Flask-RESTX API
api = Api(
    title='Inventory Management System API',
    version='1.0',
    description='REST API for Inventory Management System',
    doc='/docs',  # Swagger UI at /docs
    prefix='/api'
)

login_manager.login_message_category = 'info'


@login_manager.unauthorized_handler
def unauthorized():
    """Handle unauthorized access for API."""
    return {'success': False, 'message': 'Authentication required', 'data': None}, 401
