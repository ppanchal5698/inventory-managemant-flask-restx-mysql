# Inventory API endpoints using Flask-RESTX

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields

from app.modules.inventory.services import InventoryService
from app.modules.inventory.schemas import (
    InventoryTransactionCreate, StockAdjustmentCreate
)
from app.core.utils import api_response, require_role, async_route

inventory_ns = Namespace('inventory', description='Inventory operations')

# API Models for Swagger
transaction_model = inventory_ns.model('InventoryTransaction', {
    'transaction_id': fields.Integer(readonly=True),
    'transaction_type': fields.String(required=True),
    'product_id': fields.Integer(required=True),
    'warehouse_id': fields.Integer(required=True),
    'quantity': fields.Integer(required=True),
    'reference_type': fields.String(),
    'reference_id': fields.Integer(),
    'transaction_date': fields.DateTime(readonly=True),
    'notes': fields.String()
})

adjustment_model = inventory_ns.model('StockAdjustment', {
    'adjustment_id': fields.Integer(readonly=True),
    'product_id': fields.Integer(required=True),
    'warehouse_id': fields.Integer(required=True),
    'old_quantity': fields.Integer(readonly=True),
    'new_quantity': fields.Integer(required=True),
    'quantity_difference': fields.Integer(readonly=True),
    'reason': fields.String(required=True),
    'notes': fields.String(),
    'adjustment_date': fields.DateTime(readonly=True)
})

transaction_create_model = inventory_ns.model('InventoryTransactionCreate', {
    'transaction_type': fields.String(required=True),
    'product_id': fields.Integer(required=True),
    'warehouse_id': fields.Integer(required=True),
    'quantity': fields.Integer(required=True),
    'reference_type': fields.String(),
    'reference_id': fields.Integer(),
    'notes': fields.String()
})

adjustment_create_model = inventory_ns.model('StockAdjustmentCreate', {
    'product_id': fields.Integer(required=True),
    'warehouse_id': fields.Integer(required=True),
    'new_quantity': fields.Integer(required=True),
    'reason': fields.String(required=True),
    'notes': fields.String()
})


@inventory_ns.route('/transactions')
class TransactionList(Resource):
    @inventory_ns.doc('list_transactions')
    @jwt_required()
    @async_route
    async def get(self):
        """Get inventory transactions."""
        product_id = request.args.get('product_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        
        if product_id:
            transactions = await InventoryService.get_transactions_by_product(product_id)
        elif warehouse_id:
            transactions = await InventoryService.get_transactions_by_warehouse(warehouse_id)
        else:
            transactions = await InventoryService.get_recent_transactions()

        return api_response(data=[t.to_dict() for t in transactions])

    @inventory_ns.expect(transaction_create_model)
    @inventory_ns.doc('create_transaction')
    @require_role('admin', 'manager')
    @async_route
    async def post(self):
        """Create a new inventory transaction (manual)."""
        try:
            data = InventoryTransactionCreate.model_validate(request.get_json())
        except Exception as e:
            return api_response(message=str(e), status_code=400)
        
        user_id = get_jwt_identity()

        # Convert pydantic model to dict, exclude None
        tx_data = data.model_dump(exclude_unset=True)
        tx_data['performed_by'] = user_id

        transaction = await InventoryService.record_transaction(**tx_data)
        return api_response(data=transaction.to_dict(), message='Transaction recorded', status_code=201)


@inventory_ns.route('/adjustments')
class AdjustmentList(Resource):
    @inventory_ns.doc('list_adjustments')
    @require_role('admin', 'manager')
    @async_route
    async def get(self):
        """Get stock adjustments."""
        adjustments = await InventoryService.get_recent_adjustments()
        return api_response(data=[a.to_dict() for a in adjustments])

    @inventory_ns.expect(adjustment_create_model)
    @inventory_ns.doc('create_adjustment')
    @require_role('admin', 'manager')
    @async_route
    async def post(self):
        """Create a stock adjustment."""
        try:
            data = StockAdjustmentCreate.model_validate(request.get_json())
        except Exception as e:
            return api_response(message=str(e), status_code=400)

        user_id = get_jwt_identity()
        
        adj_data = data.model_dump(exclude_unset=True)
        adj_data['adjusted_by'] = user_id
        
        adjustment = await InventoryService.adjust_stock(**adj_data)
        return api_response(data=adjustment.to_dict(), message='Stock adjusted', status_code=201)
