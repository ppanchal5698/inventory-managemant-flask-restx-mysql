# Purchase Order routes

from flask import request
from flask_login import login_required, current_user

from app.modules.purchase_orders import purchase_orders_bp
from app.modules.purchase_orders.services import PurchaseOrderService
from app.modules.purchase_orders.schemas import purchase_order_create_schema, po_item_schema
from app.core.utils import api_response, require_role


@purchase_orders_bp.route('', methods=['GET'])
@login_required
def get_purchase_orders():
    """Get all purchase orders."""
    status = request.args.get('status')
    supplier_id = request.args.get('supplier_id', type=int)
    
    if supplier_id:
        orders = PurchaseOrderService.get_by_supplier(supplier_id)
    else:
        orders = PurchaseOrderService.get_all(status=status)
    
    return api_response(data=[o.to_dict() for o in orders])


@purchase_orders_bp.route('/<int:po_id>', methods=['GET'])
@login_required
def get_purchase_order(po_id):
    """Get purchase order by ID."""
    include_items = request.args.get('include_items', 'true').lower() == 'true'
    po = PurchaseOrderService.get_by_id(po_id)
    if not po:
        return api_response(message='Purchase order not found', status_code=404)
    return api_response(data=po.to_dict(include_items=include_items))


@purchase_orders_bp.route('/generate-number', methods=['GET'])
@login_required
@require_role('admin', 'manager', 'staff')
def generate_po_number():
    """Generate a new PO number."""
    po_number = PurchaseOrderService.generate_po_number()
    return api_response(data={'po_number': po_number})


@purchase_orders_bp.route('', methods=['POST'])
@login_required
@require_role('admin', 'manager', 'staff')
def create_purchase_order():
    """Create a new purchase order."""
    data = request.get_json()
    errors = purchase_order_create_schema.validate(data)
    if errors:
        return api_response(message=errors, status_code=400)
    
    # Check if PO number already exists
    if PurchaseOrderService.get_by_number(data['po_number']):
        return api_response(message='PO number already exists', status_code=400)
    
    po = PurchaseOrderService.create(created_by=current_user.user_id, **data)
    return api_response(data=po.to_dict(include_items=True), message='Purchase order created', status_code=201)


@purchase_orders_bp.route('/<int:po_id>', methods=['PUT'])
@login_required
@require_role('admin', 'manager')
def update_purchase_order(po_id):
    """Update purchase order."""
    po = PurchaseOrderService.get_by_id(po_id)
    if not po:
        return api_response(message='Purchase order not found', status_code=404)
    
    data = request.get_json()
    po = PurchaseOrderService.update(po, **data)
    return api_response(data=po.to_dict(), message='Purchase order updated')


@purchase_orders_bp.route('/<int:po_id>/status', methods=['PUT'])
@login_required
@require_role('admin', 'manager')
def update_po_status(po_id):
    """Update purchase order status."""
    po = PurchaseOrderService.get_by_id(po_id)
    if not po:
        return api_response(message='Purchase order not found', status_code=404)
    
    data = request.get_json()
    status = data.get('status')
    if status not in ['draft', 'pending', 'approved', 'received', 'cancelled']:
        return api_response(message='Invalid status', status_code=400)
    
    po = PurchaseOrderService.update_status(po, status)
    return api_response(data=po.to_dict(), message='Status updated')


@purchase_orders_bp.route('/<int:po_id>/items', methods=['POST'])
@login_required
@require_role('admin', 'manager', 'staff')
def add_po_item(po_id):
    """Add item to purchase order."""
    po = PurchaseOrderService.get_by_id(po_id)
    if not po:
        return api_response(message='Purchase order not found', status_code=404)
    
    if po.status != 'draft':
        return api_response(message='Can only add items to draft orders', status_code=400)
    
    data = request.get_json()
    errors = po_item_schema.validate(data)
    if errors:
        return api_response(message=errors, status_code=400)
    
    item = PurchaseOrderService.add_item(
        po, data['product_id'], data['quantity'], data['unit_price']
    )
    return api_response(data=item.to_dict(), message='Item added', status_code=201)


@purchase_orders_bp.route('/<int:po_id>', methods=['DELETE'])
@login_required
@require_role('admin')
def delete_purchase_order(po_id):
    """Delete purchase order."""
    po = PurchaseOrderService.get_by_id(po_id)
    if not po:
        return api_response(message='Purchase order not found', status_code=404)
    
    try:
        PurchaseOrderService.delete(po)
        return api_response(message='Purchase order deleted')
    except ValueError as e:
        return api_response(message=str(e), status_code=400)
