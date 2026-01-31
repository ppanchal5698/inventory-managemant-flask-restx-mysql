# Sales Order routes

from flask import request
from flask_login import login_required, current_user

from app.modules.sales_orders import sales_orders_bp
from app.modules.sales_orders.services import SalesOrderService
from app.modules.sales_orders.schemas import sales_order_create_schema, so_item_schema
from app.core.utils import api_response, require_role


@sales_orders_bp.route('', methods=['GET'])
@login_required
def get_sales_orders():
    """Get all sales orders."""
    status = request.args.get('status')
    payment_status = request.args.get('payment_status')
    customer_id = request.args.get('customer_id', type=int)
    
    if customer_id:
        orders = SalesOrderService.get_by_customer(customer_id)
    else:
        orders = SalesOrderService.get_all(status=status, payment_status=payment_status)
    
    return api_response(data=[o.to_dict() for o in orders])


@sales_orders_bp.route('/<int:order_id>', methods=['GET'])
@login_required
def get_sales_order(order_id):
    """Get sales order by ID."""
    include_items = request.args.get('include_items', 'true').lower() == 'true'
    include_customer = request.args.get('include_customer', 'false').lower() == 'true'
    
    order = SalesOrderService.get_by_id(order_id)
    if not order:
        return api_response(message='Sales order not found', status_code=404)
    return api_response(data=order.to_dict(include_items=include_items, include_customer=include_customer))


@sales_orders_bp.route('/generate-number', methods=['GET'])
@login_required
@require_role('admin', 'manager', 'staff')
def generate_order_number():
    """Generate a new order number."""
    order_number = SalesOrderService.generate_order_number()
    return api_response(data={'order_number': order_number})


@sales_orders_bp.route('', methods=['POST'])
@login_required
@require_role('admin', 'manager', 'staff')
def create_sales_order():
    """Create a new sales order."""
    data = request.get_json()
    errors = sales_order_create_schema.validate(data)
    if errors:
        return api_response(message=errors, status_code=400)
    
    # Check if order number already exists
    if SalesOrderService.get_by_number(data['order_number']):
        return api_response(message='Order number already exists', status_code=400)
    
    order = SalesOrderService.create(created_by=current_user.user_id, **data)
    return api_response(data=order.to_dict(include_items=True), message='Sales order created', status_code=201)


@sales_orders_bp.route('/<int:order_id>', methods=['PUT'])
@login_required
@require_role('admin', 'manager')
def update_sales_order(order_id):
    """Update sales order."""
    order = SalesOrderService.get_by_id(order_id)
    if not order:
        return api_response(message='Sales order not found', status_code=404)
    
    data = request.get_json()
    order = SalesOrderService.update(order, **data)
    return api_response(data=order.to_dict(), message='Sales order updated')


@sales_orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@login_required
@require_role('admin', 'manager', 'staff')
def update_order_status(order_id):
    """Update sales order status."""
    order = SalesOrderService.get_by_id(order_id)
    if not order:
        return api_response(message='Sales order not found', status_code=404)
    
    data = request.get_json()
    status = data.get('status')
    if status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        return api_response(message='Invalid status', status_code=400)
    
    order = SalesOrderService.update_status(order, status)
    return api_response(data=order.to_dict(), message='Status updated')


@sales_orders_bp.route('/<int:order_id>/payment-status', methods=['PUT'])
@login_required
@require_role('admin', 'manager')
def update_payment_status(order_id):
    """Update payment status."""
    order = SalesOrderService.get_by_id(order_id)
    if not order:
        return api_response(message='Sales order not found', status_code=404)
    
    data = request.get_json()
    payment_status = data.get('payment_status')
    if payment_status not in ['unpaid', 'partial', 'paid']:
        return api_response(message='Invalid payment status', status_code=400)
    
    order = SalesOrderService.update_payment_status(order, payment_status)
    return api_response(data=order.to_dict(), message='Payment status updated')


@sales_orders_bp.route('/<int:order_id>/items', methods=['POST'])
@login_required
@require_role('admin', 'manager', 'staff')
def add_order_item(order_id):
    """Add item to sales order."""
    order = SalesOrderService.get_by_id(order_id)
    if not order:
        return api_response(message='Sales order not found', status_code=404)
    
    if order.status not in ['pending', 'processing']:
        return api_response(message='Cannot add items to this order', status_code=400)
    
    data = request.get_json()
    errors = so_item_schema.validate(data)
    if errors:
        return api_response(message=errors, status_code=400)
    
    item = SalesOrderService.add_item(
        order, data['product_id'], data['quantity'], 
        data['unit_price'], data.get('discount', 0)
    )
    return api_response(data=item.to_dict(), message='Item added', status_code=201)


@sales_orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
@require_role('admin', 'manager')
def cancel_order(order_id):
    """Cancel a sales order."""
    order = SalesOrderService.get_by_id(order_id)
    if not order:
        return api_response(message='Sales order not found', status_code=404)
    
    if order.status in ['delivered', 'cancelled']:
        return api_response(message='Cannot cancel this order', status_code=400)
    
    order = SalesOrderService.cancel_order(order)
    return api_response(data=order.to_dict(), message='Order cancelled')
