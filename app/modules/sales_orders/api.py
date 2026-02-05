# Sales Orders API endpoints using Flask-RESTX

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields

from app.modules.sales_orders.services import SalesOrderService
from app.modules.sales_orders.schemas import SalesOrderCreate
from app.core.utils import api_response, require_role, async_route

sales_orders_ns = Namespace('sales-orders', description='Sales Order operations')

# API Models
so_item_model = sales_orders_ns.model('SalesOrderItem', {
    'product_id': fields.Integer(required=True),
    'quantity': fields.Integer(required=True),
    'unit_price': fields.Float(required=True),
    'discount': fields.Float()
})

so_create_model = sales_orders_ns.model('SalesOrderCreate', {
    'order_number': fields.String(required=True),
    'customer_id': fields.Integer(required=True),
    'warehouse_id': fields.Integer(required=True),
    'order_date': fields.String(required=True),
    'expected_delivery_date': fields.String(),
    'tax_amount': fields.Float(),
    'shipping_cost': fields.Float(),
    'discount_amount': fields.Float(),
    'notes': fields.String(),
    'items': fields.List(fields.Nested(so_item_model))
})


@sales_orders_ns.route('')
class SalesOrderList(Resource):
    @sales_orders_ns.doc('list_sales_orders')
    @jwt_required()
    @async_route
    async def get(self):
        """Get all sales orders."""
        orders = await SalesOrderService.get_all()
        return api_response(data=[o.to_dict(include_items=False) for o in orders])

    @sales_orders_ns.expect(so_create_model)
    @sales_orders_ns.doc('create_sales_order')
    @require_role('admin', 'manager', 'staff')
    @async_route
    async def post(self):
        """Create a new sales order."""
        try:
            data = SalesOrderCreate.model_validate(request.get_json())
        except Exception as e:
            return api_response(message=str(e), status_code=400)

        user_id = get_jwt_identity()
        order_data = data.model_dump()
        order_data['created_by'] = user_id

        order = await SalesOrderService.create(order_data)
        return api_response(data=order.to_dict(include_items=True), message='Sales Order created', status_code=201)


@sales_orders_ns.route('/<int:order_id>')
class SalesOrderDetail(Resource):
    @sales_orders_ns.doc('get_sales_order')
    @jwt_required()
    @async_route
    async def get(self, order_id):
        """Get sales order by ID."""
        order = await SalesOrderService.get_by_id(order_id)
        if not order:
            return api_response(message='Sales Order not found', status_code=404)
        return api_response(data=order.to_dict(include_items=True, include_customer=True))

    @sales_orders_ns.doc('update_sales_order')
    @require_role('admin', 'manager')
    @async_route
    async def put(self, order_id):
        """Update sales order."""
        order = await SalesOrderService.get_by_id(order_id)
        if not order:
            return api_response(message='Sales Order not found', status_code=404)

        data = request.get_json()
        order = await SalesOrderService.update(order, data)
        return api_response(data=order.to_dict(include_items=True), message='Sales Order updated')

    @sales_orders_ns.doc('delete_sales_order')
    @require_role('admin')
    @async_route
    async def delete(self, order_id):
        """Delete sales order."""
        order = await SalesOrderService.get_by_id(order_id)
        if not order:
            return api_response(message='Sales Order not found', status_code=404)

        await SalesOrderService.delete(order)
        return api_response(message='Sales Order deleted')
