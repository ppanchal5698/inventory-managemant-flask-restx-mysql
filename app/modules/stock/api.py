# Stock API endpoints using Flask-RESTX

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_required

from app.modules.stock.services import StockService
from app.modules.stock.schemas import stock_create_schema, stock_update_schema
from app.core.utils import api_response, require_role

stock_ns = Namespace('stock', description='Stock operations')

# API Models for Swagger documentation
stock_model = stock_ns.model('Stock', {
    'stock_id': fields.Integer(readonly=True),
    'product_id': fields.Integer(required=True),
    'warehouse_id': fields.Integer(required=True),
    'quantity_on_hand': fields.Integer(),
    'quantity_reserved': fields.Integer(),
    'created_at': fields.DateTime(readonly=True)
})

stock_adjust_model = stock_ns.model('StockAdjust', {
    'adjustment': fields.Integer(required=True, description='Adjustment amount (positive or negative)')
})


@stock_ns.route('')
class StockList(Resource):
    @stock_ns.doc('list_stocks')
    @login_required
    def get(self):
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

    @stock_ns.doc('create_stock')
    @login_required
    @require_role('admin', 'manager', 'staff')
    def post(self):
        """Create a new stock entry."""
        data = request.get_json()
        errors = stock_create_schema.validate(data)
        if errors:
            return api_response(message=errors, status_code=400)
        
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


@stock_ns.route('/lookup')
class StockLookup(Resource):
    @stock_ns.doc('lookup_stock')
    @login_required
    def get(self):
        """Lookup stock by product and warehouse."""
        product_id = request.args.get('product_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        
        if not product_id or not warehouse_id:
            return api_response(message='product_id and warehouse_id required', status_code=400)
        
        stock = StockService.get_by_product_and_warehouse(product_id, warehouse_id)
        if not stock:
            return api_response(message='Stock entry not found', status_code=404)
        return api_response(data=stock.to_dict())


@stock_ns.route('/<int:stock_id>')
class StockDetail(Resource):
    @stock_ns.doc('get_stock')
    @login_required
    def get(self, stock_id):
        """Get stock by ID."""
        stock = StockService.get_by_id(stock_id)
        if not stock:
            return api_response(message='Stock entry not found', status_code=404)
        return api_response(data=stock.to_dict(include_product=True, include_warehouse=True))

    @stock_ns.doc('update_stock')
    @login_required
    @require_role('admin', 'manager', 'staff')
    def put(self, stock_id):
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


@stock_ns.route('/<int:stock_id>/adjust')
class StockAdjust(Resource):
    @stock_ns.expect(stock_adjust_model)
    @stock_ns.doc('adjust_stock')
    @login_required
    @require_role('admin', 'manager', 'staff')
    def post(self, stock_id):
        """Adjust stock quantity."""
        stock = StockService.get_by_id(stock_id)
        if not stock:
            return api_response(message='Stock entry not found', status_code=404)
        
        data = request.get_json()
        adjustment = data.get('adjustment', 0)
        
        stock = StockService.adjust_quantity(stock, adjustment)
        return api_response(data=stock.to_dict(), message='Stock adjusted')
