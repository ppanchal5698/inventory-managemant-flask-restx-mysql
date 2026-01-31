# Products API endpoints using Flask-RESTX

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_required

from app.modules.products.services import ProductService
from app.modules.products.schemas import product_create_schema
from app.core.utils import api_response, require_role

products_ns = Namespace('products', description='Product operations')

# API Models for Swagger documentation
product_model = products_ns.model('Product', {
    'product_id': fields.Integer(readonly=True),
    'product_code': fields.String(required=True),
    'product_name': fields.String(required=True),
    'category_id': fields.Integer(),
    'brand_id': fields.Integer(),
    'description': fields.String(),
    'barcode': fields.String(),
    'unit_price': fields.Float(),
    'cost_price': fields.Float(),
    'reorder_level': fields.Integer(),
    'is_active': fields.Boolean(readonly=True),
    'created_at': fields.DateTime(readonly=True)
})


@products_ns.route('')
class ProductList(Resource):
    @products_ns.doc('list_products')
    @login_required
    def get(self):
        """Get all products."""
        search_query = request.args.get('search')
        category_id = request.args.get('category_id', type=int)
        include_stock = request.args.get('include_stock', 'false').lower() == 'true'
        
        if search_query:
            products = ProductService.search(search_query)
        elif category_id:
            products = ProductService.get_by_category(category_id)
        else:
            products = ProductService.get_all()
        
        return api_response(data=[p.to_dict(include_stock=include_stock) for p in products])

    @products_ns.doc('create_product')
    @login_required
    @require_role('admin', 'manager')
    def post(self):
        """Create a new product."""
        data = request.get_json()
        errors = product_create_schema.validate(data)
        if errors:
            return api_response(message=errors, status_code=400)
        
        if ProductService.get_by_code(data['product_code']):
            return api_response(message='Product code already exists', status_code=400)
        
        product = ProductService.create(**data)
        return api_response(data=product.to_dict(), message='Product created', status_code=201)


@products_ns.route('/low-stock')
class LowStockProducts(Resource):
    @products_ns.doc('get_low_stock_products')
    @login_required
    def get(self):
        """Get products with low stock."""
        products = ProductService.get_low_stock_products()
        return api_response(data=[p.to_dict(include_stock=True) for p in products])


@products_ns.route('/<int:product_id>')
class ProductDetail(Resource):
    @products_ns.doc('get_product')
    @login_required
    def get(self, product_id):
        """Get product by ID."""
        include_stock = request.args.get('include_stock', 'true').lower() == 'true'
        product = ProductService.get_by_id(product_id)
        if not product:
            return api_response(message='Product not found', status_code=404)
        return api_response(data=product.to_dict(include_stock=include_stock))

    @products_ns.doc('update_product')
    @login_required
    @require_role('admin', 'manager')
    def put(self, product_id):
        """Update product."""
        product = ProductService.get_by_id(product_id)
        if not product:
            return api_response(message='Product not found', status_code=404)
        
        data = request.get_json()
        product = ProductService.update(product, **data)
        return api_response(data=product.to_dict(), message='Product updated')

    @products_ns.doc('delete_product')
    @login_required
    @require_role('admin')
    def delete(self, product_id):
        """Delete product."""
        product = ProductService.get_by_id(product_id)
        if not product:
            return api_response(message='Product not found', status_code=404)
        
        ProductService.delete(product)
        return api_response(message='Product deleted')


@products_ns.route('/barcode/<barcode>')
class ProductByBarcode(Resource):
    @products_ns.doc('get_product_by_barcode')
    @login_required
    def get(self, barcode):
        """Get product by barcode."""
        product = ProductService.get_by_barcode(barcode)
        if not product:
            return api_response(message='Product not found', status_code=404)
        return api_response(data=product.to_dict(include_stock=True))
