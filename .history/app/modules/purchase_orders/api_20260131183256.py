# Purchase Orders API endpoints using Flask-RESTX

from flask import request
from flask_login import current_user, login_required
from flask_restx import Namespace, Resource, fields

from app.core.utils import api_response, require_role
from app.modules.purchase_orders.schemas import (
    po_item_schema,
    purchase_order_create_schema,
)
from app.modules.purchase_orders.services import PurchaseOrderService

purchase_orders_ns = Namespace('purchase-orders', description='Purchase order operations')

# API Models for Swagger documentation
po_item_model = purchase_orders_ns.model('POItem', {
    'product_id': fields.Integer(required=True),
    'quantity': fields.Integer(required=True),
    'unit_price': fields.Float(required=True)
})

po_status_model = purchase_orders_ns.model('POStatus', {
    'status': fields.String(required=True, enum=['draft', 'pending', 'approved', 'received', 'cancelled'])
})

purchase_order_model = purchase_orders_ns.model('PurchaseOrder', {
    'po_id': fields.Integer(readonly=True),
    'po_number': fields.String(required=True),
    'supplier_id': fields.Integer(required=True),
    'status': fields.String(),
    'order_date': fields.DateTime(),
    'expected_date': fields.DateTime(),
    'total_amount': fields.Float(),
    'notes': fields.String(),
    'created_at': fields.DateTime(readonly=True)
})


@purchase_orders_ns.route('')
class PurchaseOrderList(Resource):
    @purchase_orders_ns.doc('list_purchase_orders')
    @login_required
    def get(self):
        """Get all purchase orders."""
        status = request.args.get('status')
        supplier_id = request.args.get('supplier_id', type=int)

        if supplier_id:
            orders = PurchaseOrderService.get_by_supplier(supplier_id)
        else:
            orders = PurchaseOrderService.get_all(status=status)

        return api_response(data=[o.to_dict() for o in orders])

    @purchase_orders_ns.doc('create_purchase_order')
    @login_required
    @require_role('admin', 'manager', 'staff')
    def post(self):
        """Create a new purchase order."""
        data = request.get_json()
        errors = purchase_order_create_schema.validate(data)
        if errors:
            return api_response(message=errors, status_code=400)

        if PurchaseOrderService.get_by_number(data['po_number']):
            return api_response(message='PO number already exists', status_code=400)

        # Load data to transform date strings to date objects
        loaded_data = purchase_order_create_schema.load(data)
        po = PurchaseOrderService.create(created_by=current_user.user_id, **loaded_data)
        return api_response(data=po.to_dict(include_items=True), message='Purchase order created', status_code=201)


@purchase_orders_ns.route('/generate-number')
class GeneratePONumber(Resource):
    @purchase_orders_ns.doc('generate_po_number')
    @login_required
    @require_role('admin', 'manager', 'staff')
    def get(self):
        """Generate a new PO number."""
        po_number = PurchaseOrderService.generate_po_number()
        return api_response(data={'po_number': po_number})


@purchase_orders_ns.route('/<int:po_id>')
class PurchaseOrderDetail(Resource):
    @purchase_orders_ns.doc('get_purchase_order')
    @login_required
    def get(self, po_id):
        """Get purchase order by ID."""
        include_items = request.args.get('include_items', 'true').lower() == 'true'
        po = PurchaseOrderService.get_by_id(po_id)
        if not po:
            return api_response(message='Purchase order not found', status_code=404)
        return api_response(data=po.to_dict(include_items=include_items))

    @purchase_orders_ns.doc('update_purchase_order')
    @login_required
    @require_role('admin', 'manager')
    def put(self, po_id):
        """Update purchase order."""
        po = PurchaseOrderService.get_by_id(po_id)
        if not po:
            return api_response(message='Purchase order not found', status_code=404)

        data = request.get_json()
        po = PurchaseOrderService.update(po, **data)
        return api_response(data=po.to_dict(), message='Purchase order updated')

    @purchase_orders_ns.doc('delete_purchase_order')
    @login_required
    @require_role('admin')
    def delete(self, po_id):
        """Delete purchase order."""
        po = PurchaseOrderService.get_by_id(po_id)
        if not po:
            return api_response(message='Purchase order not found', status_code=404)

        try:
            PurchaseOrderService.delete(po)
            return api_response(message='Purchase order deleted')
        except ValueError as e:
            return api_response(message=str(e), status_code=400)


@purchase_orders_ns.route('/<int:po_id>/status')
class PurchaseOrderStatus(Resource):
    @purchase_orders_ns.expect(po_status_model)
    @purchase_orders_ns.doc('update_po_status')
    @login_required
    @require_role('admin', 'manager')
    def put(self, po_id):
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


@purchase_orders_ns.route('/<int:po_id>/items')
class PurchaseOrderItems(Resource):
    @purchase_orders_ns.expect(po_item_model)
    @purchase_orders_ns.doc('add_po_item')
    @login_required
    @require_role('admin', 'manager', 'staff')
    def post(self, po_id):
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
