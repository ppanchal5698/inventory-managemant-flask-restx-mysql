# Inventory routes

from flask import request
from flask_login import login_required, current_user
from datetime import datetime

from app.modules.inventory import inventory_bp
from app.modules.inventory.services import InventoryTransactionService, StockAdjustmentService
from app.modules.inventory.schemas import (
    transaction_create_schema, transactions_schema,
    adjustment_create_schema, adjustments_schema
)
from app.core.utils import api_response, require_role


# Transaction routes

@inventory_bp.route('/transactions', methods=['GET'])
@login_required
def get_transactions():
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


@inventory_bp.route('/transactions/<int:transaction_id>', methods=['GET'])
@login_required
def get_transaction(transaction_id):
    """Get transaction by ID."""
    transaction = InventoryTransactionService.get_by_id(transaction_id)
    if not transaction:
        return api_response(message='Transaction not found', status_code=404)
    return api_response(data=transaction.to_dict())


@inventory_bp.route('/transactions/reference/<reference_type>/<int:reference_id>', methods=['GET'])
@login_required
def get_transactions_by_reference(reference_type, reference_id):
    """Get transactions by reference."""
    transactions = InventoryTransactionService.get_by_reference(reference_type, reference_id)
    return api_response(data=[t.to_dict() for t in transactions])


@inventory_bp.route('/transactions', methods=['POST'])
@login_required
@require_role('admin', 'manager', 'staff')
def create_transaction():
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


# Adjustment routes

@inventory_bp.route('/adjustments', methods=['GET'])
@login_required
def get_adjustments():
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


@inventory_bp.route('/adjustments/<int:adjustment_id>', methods=['GET'])
@login_required
def get_adjustment(adjustment_id):
    """Get adjustment by ID."""
    adjustment = StockAdjustmentService.get_by_id(adjustment_id)
    if not adjustment:
        return api_response(message='Adjustment not found', status_code=404)
    return api_response(data=adjustment.to_dict())


@inventory_bp.route('/adjustments', methods=['POST'])
@login_required
@require_role('admin', 'manager')
def create_adjustment():
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


# Reports

@inventory_bp.route('/reports/movements', methods=['GET'])
@login_required
@require_role('admin', 'manager')
def get_movement_report():
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
