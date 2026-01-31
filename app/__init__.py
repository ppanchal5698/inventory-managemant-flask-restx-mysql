# create_app, register_extensions, register_blueprints
# Modular Monolithic Architecture for Inventory Management System - REST API

from flask import Flask

from app.config import Config
from app.extensions import db, migrate, cache, login_manager, api


def create_app(config_class=Config):
    """Application factory."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Initialize extensions
    register_extensions(app)

    # Register API namespaces (modular monolith)
    register_api_namespaces()

    # Register error handlers
    register_error_handlers(app)

    # Register CLI commands
    register_cli_commands(app)

    # Register middleware
    register_middleware(app)

    return app


def register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    login_manager.init_app(app)
    api.init_app(app)


def register_api_namespaces():
    """Register all API namespaces."""
    from app.modules.auth.api import auth_ns
    from app.modules.categories.api import categories_ns
    from app.modules.suppliers.api import suppliers_ns
    from app.modules.brands.api import brands_ns
    from app.modules.products.api import products_ns
    from app.modules.warehouses.api import warehouses_ns
    from app.modules.stock.api import stock_ns
    from app.modules.customers.api import customers_ns
    from app.modules.purchase_orders.api import purchase_orders_ns
    from app.modules.sales_orders.api import sales_orders_ns
    from app.modules.inventory.api import inventory_ns

    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(categories_ns, path='/categories')
    api.add_namespace(suppliers_ns, path='/suppliers')
    api.add_namespace(brands_ns, path='/brands')
    api.add_namespace(products_ns, path='/products')
    api.add_namespace(warehouses_ns, path='/warehouses')
    api.add_namespace(stock_ns, path='/stock')
    api.add_namespace(customers_ns, path='/customers')
    api.add_namespace(purchase_orders_ns, path='/purchase-orders')
    api.add_namespace(sales_orders_ns, path='/sales-orders')
    api.add_namespace(inventory_ns, path='/inventory')


def register_error_handlers(app):
    """Register error handlers for JSON responses."""
    from flask import jsonify

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'success': False, 'message': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({'success': False, 'message': 'Access forbidden'}), 403


def register_cli_commands(app):
    """Register CLI commands."""
    from app.cli import register_cli_commands as _register_cli
    _register_cli(app)


def register_middleware(app):
    """Register middleware hooks."""
    from app.middleware import register_middleware as _register_middleware
    _register_middleware(app)
