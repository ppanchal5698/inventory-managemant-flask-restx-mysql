# Product routes

from flask import request
from flask_login import login_required

from app.modules.products import products_bp
from app.modules.products.services import ProductService
from app.modules.products.schemas import product_create_schema
from app.core.utils import api_response, require_role


@products_bp.route('', methods=['GET'])
@login_required
def get_products():
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


@products_bp.route('/low-stock', methods=['GET'])
@login_required
def get_low_stock_products():
    """Get products with low stock."""
    products = ProductService.get_low_stock_products()
    return api_response(data=[p.to_dict(include_stock=True) for p in products])


@products_bp.route('/<int:product_id>', methods=['GET'])
@login_required
def get_product(product_id):
    """Get product by ID."""
    include_stock = request.args.get('include_stock', 'true').lower() == 'true'
    product = ProductService.get_by_id(product_id)
    if not product:
        return api_response(message='Product not found', status_code=404)
    return api_response(data=product.to_dict(include_stock=include_stock))


@products_bp.route('/barcode/<barcode>', methods=['GET'])
@login_required
def get_product_by_barcode(barcode):
    """Get product by barcode."""
    product = ProductService.get_by_barcode(barcode)
    if not product:
        return api_response(message='Product not found', status_code=404)
    return api_response(data=product.to_dict(include_stock=True))


@products_bp.route('', methods=['POST'])
@login_required
@require_role('admin', 'manager')
def create_product():
    """Create a new product."""
    data = request.get_json()
    errors = product_create_schema.validate(data)
    if errors:
        return api_response(message=errors, status_code=400)
    
    # Check if product code already exists
    if ProductService.get_by_code(data['product_code']):
        return api_response(message='Product code already exists', status_code=400)
    
    product = ProductService.create(**data)
    return api_response(data=product.to_dict(), message='Product created', status_code=201)


@products_bp.route('/<int:product_id>', methods=['PUT'])
@login_required
@require_role('admin', 'manager')
def update_product(product_id):
    """Update product."""
    product = ProductService.get_by_id(product_id)
    if not product:
        return api_response(message='Product not found', status_code=404)
    
    data = request.get_json()
    product = ProductService.update(product, **data)
    return api_response(data=product.to_dict(), message='Product updated')


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@login_required
@require_role('admin')
def delete_product(product_id):
    """Delete product."""
    product = ProductService.get_by_id(product_id)
    if not product:
        return api_response(message='Product not found', status_code=404)
    
    ProductService.delete(product)
    return api_response(message='Product deleted')
