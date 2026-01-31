# Modules package - Modular Monolithic Architecture

from flask import Flask


def register_modules(app: Flask):
    """Register all application modules."""
    from app.modules.auth import auth_bp
    from app.modules.categories import categories_bp
    from app.modules.suppliers import suppliers_bp
    from app.modules.brands import brands_bp
    from app.modules.products import products_bp
    from app.modules.warehouses import warehouses_bp
    from app.modules.stock import stock_bp
    from app.modules.customers import customers_bp
    from app.modules.purchase_orders import purchase_orders_bp
    from app.modules.sales_orders import sales_orders_bp
    from app.modules.inventory import inventory_bp

    # Register blueprints with API prefix
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
    app.register_blueprint(brands_bp, url_prefix='/api/brands')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(warehouses_bp, url_prefix='/api/warehouses')
    app.register_blueprint(stock_bp, url_prefix='/api/stock')
    app.register_blueprint(customers_bp, url_prefix='/api/customers')
    app.register_blueprint(purchase_orders_bp, url_prefix='/api/purchase-orders')
    app.register_blueprint(sales_orders_bp, url_prefix='/api/sales-orders')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
