# Inventory API endpoints using Flask-RESTX

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_required, current_user
from datetime import datetime

from app.modules.inventory.services import InventoryTransactionService, StockAdjustmentService
from app.modules.inventory.schemas import (
    transaction_create_schema, transactions_schema,
    adjustment_create_schema, adjustments_schema
)
from app.core.utils import api_response, require_role

inventory_ns = Namespace('inventory', description='Inventory operations')

# API Models for Swagger documentation
transaction_model = inventory_ns.model('InventoryTransaction', {
    'transaction_id': fields.Integer(readonly=True),
    'product_id': fields.Integer(required=True),
    'warehouse_id': fields.Integer(required=True),
    'transaction_type': fields.String(required=True),
    'quantity': fields.Integer(required=True),
    'reference_type': fields.String(),
    'reference_id': fields.Integer(),
    'notes': fields.String(),
    'created_at': fields.DateTime(readonly=True)
})

adjustment_model = inventory_ns.model('StockAdjustment', {
    'adjustment_id': fields.Integer(readonly=True),
    'product_id': fields.Integer(required=True),
    'warehouse_id': fields.Integer(required=True),
    'quantity_change': fields.Integer(required=True),
    'reason': fields.String(required=True),
    'notes': fields.String(),
    'created_at': fields.DateTime(readonly=True)
})


@inventory_ns.route('/transactions')
class TransactionList(Resource):
    @inventory_ns.doc('list_transactions')
    @login_required
    def get(self):
        """Get all inventory transactions."""
        transaction_type = request.args.get('type')
        product_id = request.args.get('product_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        
        transactions = InventoryTransactionService.get_all(
            transaction_type=transaction_type,
            product_id=product_id,
            warehouse_id=warehouse_id
        )
        return api_response(data=[t.to_dict() for t in transactions])

    @inventory_ns.doc('create_transaction')
    @login_required
    @require_role('admin', 'manager', 'staff')
    def post(self):
        """Create a new inventory transaction."""
        data = request.get_json()
        errors = transaction_create_schema.validate(data)
        if errors:
            return api_response(message=errors, status_code=400)
        
        transaction = InventoryTransactionService.create(
            performed_by=current_user.user_id,
            **data
        )
        return api_response(data=transaction.to_dict(), message='Transaction created', status_code=201)


@inventory_ns.route('/transactions/<int:transaction_id>')
class TransactionDetail(Resource):
    @inventory_ns.doc('get_transaction')
    @login_required
    def get(self, transaction_id):
        """Get transaction by ID."""
        transaction = InventoryTransactionService.get_by_id(transaction_id)
        if not transaction:
            return api_response(message='Transaction not found', status_code=404)
        return api_response(data=transaction.to_dict())


@inventory_ns.route('/transactions/reference/<reference_type>/<int:reference_id>')
class TransactionsByReference(Resource):
    @inventory_ns.doc('get_transactions_by_reference')
    @login_required
    def get(self, reference_type, reference_id):
        """Get transactions by reference."""
        transactions = InventoryTransactionService.get_by_reference(reference_type, reference_id)
        return api_response(data=[t.to_dict() for t in transactions])


@inventory_ns.route('/adjustments')
class AdjustmentList(Resource):
    @inventory_ns.doc('list_adjustments')
    @login_required
    def get(self):
        """Get all stock adjustments."""
        product_id = request.args.get('product_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        reason = request.args.get('reason')
        
        adjustments = StockAdjustmentService.get_all(
            product_id=product_id,
            warehouse_id=warehouse_id,
            reason=reason
        )
        return api_response(data=[a.to_dict() for a in adjustments])

    @inventory_ns.doc('create_adjustment')
    @login_required
    @require_role('admin', 'manager')
    def post(self):
        """Create a stock adjustment."""
        data = request.get_json()
        errors = adjustment_create_schema.validate(data)
        if errors:
            return api_response(message=errors, status_code=400)
        
        adjustment = StockAdjustmentService.create(
            adjusted_by=current_user.user_id,
            **data
        )
        return api_response(data=adjustment.to_dict(), message='Adjustment created', status_code=201)


@inventory_ns.route('/adjustments/<int:adjustment_id>')
class AdjustmentDetail(Resource):
    @inventory_ns.doc('get_adjustment')
    @login_required
    def get(self, adjustment_id):
        """Get adjustment by ID."""
        adjustment = StockAdjustmentService.get_by_id(adjustment_id)
        if not adjustment:
            return api_response(message='Adjustment not found', status_code=404)
        return api_response(data=adjustment.to_dict())


@inventory_ns.route('/reports/movements')
class MovementReport(Resource):
    @inventory_ns.doc('get_movement_report')
    @login_required
    @require_role('admin', 'manager')
    def get(self):
        """Get inventory movement report."""
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return api_response(message='start_date and end_date required', status_code=400)
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return api_response(message='Invalid date format. Use YYYY-MM-DD', status_code=400)
        
        transactions = InventoryTransactionService.get_by_date_range(start_date, end_date)
        adjustments = StockAdjustmentService.get_by_date_range(start_date, end_date)
        
        return api_response(data={
            'transactions': [t.to_dict() for t in transactions],
            'adjustments': [a.to_dict() for a in adjustments],
            'period': {'start_date': start_date_str, 'end_date': end_date_str}
        })
