# Purchase Orders API endpoints using Flask-RESTX

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields

from app.modules.purchase_orders.services import PurchaseOrderService
from app.modules.purchase_orders.schemas import PurchaseOrderCreate
from app.core.utils import api_response, require_role, async_route

purchase_orders_ns = Namespace('purchase-orders', description='Purchase Order operations')

# API Models
po_item_model = purchase_orders_ns.model('PurchaseOrderItem', {
    'product_id': fields.Integer(required=True),
    'quantity': fields.Integer(required=True),
    'unit_price': fields.Float(required=True)
})

po_create_model = purchase_orders_ns.model('PurchaseOrderCreate', {
    'po_number': fields.String(required=True),
    'supplier_id': fields.Integer(required=True),
    'warehouse_id': fields.Integer(required=True),
    'order_date': fields.String(required=True),
    'expected_delivery_date': fields.String(),
    'tax_amount': fields.Float(),
    'shipping_cost': fields.Float(),
    'notes': fields.String(),
    'items': fields.List(fields.Nested(po_item_model))
})


@purchase_orders_ns.route('')
class PurchaseOrderList(Resource):
    @purchase_orders_ns.doc('list_purchase_orders')
    @jwt_required()
    @async_route
    async def get(self):
        """Get all purchase orders."""
        orders = await PurchaseOrderService.get_all()
        return api_response(data=[o.to_dict(include_items=False) for o in orders])

    @purchase_orders_ns.expect(po_create_model)
    @purchase_orders_ns.doc('create_purchase_order')
    @require_role('admin', 'manager')
    @async_route
    async def post(self):
        """Create a new purchase order."""
        try:
            data = PurchaseOrderCreate.model_validate(request.get_json())
        except Exception as e:
            return api_response(message=str(e), status_code=400)

        user_id = get_jwt_identity()
        po_data = data.model_dump()
        po_data['created_by'] = user_id

        po = await PurchaseOrderService.create(po_data)
        return api_response(data=po.to_dict(include_items=True), message='Purchase Order created', status_code=201)


@purchase_orders_ns.route('/<int:po_id>')
class PurchaseOrderDetail(Resource):
    @purchase_orders_ns.doc('get_purchase_order')
    @jwt_required()
    @async_route
    async def get(self, po_id):
        """Get purchase order by ID."""
        po = await PurchaseOrderService.get_by_id(po_id)
        if not po:
            return api_response(message='Purchase Order not found', status_code=404)
        return api_response(data=po.to_dict(include_items=True))

    @purchase_orders_ns.doc('update_purchase_order')
    @require_role('admin', 'manager')
    @async_route
    async def put(self, po_id):
        """Update purchase order."""
        po = await PurchaseOrderService.get_by_id(po_id)
        if not po:
            return api_response(message='Purchase Order not found', status_code=404)

        data = request.get_json()
        po = await PurchaseOrderService.update(po, data)
        return api_response(data=po.to_dict(include_items=True), message='Purchase Order updated')

    @purchase_orders_ns.doc('delete_purchase_order')
    @require_role('admin')
    @async_route
    async def delete(self, po_id):
        """Delete purchase order."""
        po = await PurchaseOrderService.get_by_id(po_id)
        if not po:
            return api_response(message='Purchase Order not found', status_code=404)

        await PurchaseOrderService.delete(po)
        return api_response(message='Purchase Order deleted')
