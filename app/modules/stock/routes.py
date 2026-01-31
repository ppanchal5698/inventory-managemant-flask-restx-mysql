# Stock routes

from flask import request
from flask_login import login_required

from app.modules.stock import stock_bp
from app.modules.stock.services import StockService
from app.modules.stock.schemas import stock_create_schema, stock_update_schema
from app.core.utils import api_response, require_role


@stock_bp.route('', methods=['GET'])
@login_required
def get_stocks():
    """Get all stock entries."""
    product_id = request.args.get('product_id', type=int)
    warehouse_id = request.args.get('warehouse_id', type=int)
    include_product = request.args.get('include_product', 'false').lower() == 'true'
    include_warehouse = request.args.get('include_warehouse', 'false').lower() == 'true'
    
    if product_id:
        stocks = StockService.get_by_product(product_id)
    elif warehouse_id:
        stocks = StockService.get_by_warehouse(warehouse_id)
    else:
        stocks = StockService.get_all()
    
    return api_response(data=[
        s.to_dict(include_product=include_product, include_warehouse=include_warehouse) 
        for s in stocks
    ])


@stock_bp.route('/<int:stock_id>', methods=['GET'])
@login_required
def get_stock(stock_id):
    """Get stock by ID."""
    stock = StockService.get_by_id(stock_id)
    if not stock:
        return api_response(message='Stock entry not found', status_code=404)
    return api_response(data=stock.to_dict(include_product=True, include_warehouse=True))


@stock_bp.route('/lookup', methods=['GET'])
@login_required
def lookup_stock():
    """Lookup stock by product and warehouse."""
    product_id = request.args.get('product_id', type=int)
    warehouse_id = request.args.get('warehouse_id', type=int)
    
    if not product_id or not warehouse_id:
        return api_response(message='product_id and warehouse_id required', status_code=400)
    
    stock = StockService.get_by_product_and_warehouse(product_id, warehouse_id)
    if not stock:
        return api_response(message='Stock entry not found', status_code=404)
    return api_response(data=stock.to_dict())


@stock_bp.route('', methods=['POST'])
@login_required
@require_role('admin', 'manager', 'staff')
def create_stock():
    """Create a new stock entry."""
    data = request.get_json()
    errors = stock_create_schema.validate(data)
    if errors:
        return api_response(message=errors, status_code=400)
    
    # Check if stock already exists
    existing = StockService.get_by_product_and_warehouse(
        data['product_id'], data['warehouse_id']
    )
    if existing:
        return api_response(
            message='Stock entry already exists for this product-warehouse combination',
            status_code=400
        )
    
    stock = StockService.create(**data)
    return api_response(data=stock.to_dict(), message='Stock created', status_code=201)


@stock_bp.route('/<int:stock_id>', methods=['PUT'])
@login_required
@require_role('admin', 'manager', 'staff')
def update_stock(stock_id):
    """Update stock entry."""
    stock = StockService.get_by_id(stock_id)
    if not stock:
        return api_response(message='Stock entry not found', status_code=404)
    
    data = request.get_json()
    errors = stock_update_schema.validate(data)
    if errors:
        return api_response(message=errors, status_code=400)
    
    stock = StockService.update(stock, **data)
    return api_response(data=stock.to_dict(), message='Stock updated')


@stock_bp.route('/<int:stock_id>/adjust', methods=['POST'])
@login_required
@require_role('admin', 'manager', 'staff')
def adjust_stock(stock_id):
    """Adjust stock quantity."""
    stock = StockService.get_by_id(stock_id)
    if not stock:
        return api_response(message='Stock entry not found', status_code=404)
    
    data = request.get_json()
    adjustment = data.get('adjustment', 0)
    
    stock = StockService.adjust_quantity(stock, adjustment)
    return api_response(data=stock.to_dict(), message='Stock adjusted')
