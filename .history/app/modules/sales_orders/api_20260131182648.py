# Sales Orders API endpoints using Flask-RESTX

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_required, current_user

from app.modules.sales_orders.services import SalesOrderService
from app.modules.sales_orders.schemas import sales_order_create_schema, so_item_schema
from app.core.utils import api_response, require_role

sales_orders_ns = Namespace('sales-orders', description='Sales order operations')

# API Models for Swagger documentation
so_item_model = sales_orders_ns.model('SOItem', {
    'product_id': fields.Integer(required=True),
    'quantity': fields.Integer(required=True),
    'unit_price': fields.Float(required=True),
    'discount': fields.Float(default=0)
})

order_status_model = sales_orders_ns.model('OrderStatus', {
    'status': fields.String(required=True, enum=['pending', 'processing', 'shipped', 'delivered', 'cancelled'])
})

payment_status_model = sales_orders_ns.model('PaymentStatus', {
    'payment_status': fields.String(required=True, enum=['unpaid', 'partial', 'paid'])
})

sales_order_model = sales_orders_ns.model('SalesOrder', {
    'order_id': fields.Integer(readonly=True),
    'order_number': fields.String(required=True),
    'customer_id': fields.Integer(required=True),
    'status': fields.String(),
    'payment_status': fields.String(),
    'order_date': fields.DateTime(),
    'total_amount': fields.Float(),
    'notes': fields.String(),
    'created_at': fields.DateTime(readonly=True)
})


@sales_orders_ns.route('')
class SalesOrderList(Resource):
    @sales_orders_ns.doc('list_sales_orders')
    @login_required
    def get(self):
        """Get all sales orders."""
        status = request.args.get('status')
        payment_status = request.args.get('payment_status')
        customer_id = request.args.get('customer_id', type=int)
        
        if customer_id:
            orders = SalesOrderService.get_by_customer(customer_id)
        else:
            orders = SalesOrderService.get_all(status=status, payment_status=payment_status)
        
        return api_response(data=[o.to_dict() for o in orders])

    @sales_orders_ns.doc('create_sales_order')
    @login_required
    @require_role('admin', 'manager', 'staff')
    def post(self):
        """Create a new sales order."""
        data = request.get_json()
        errors = sales_order_create_schema.validate(data)
        if errors:
            return api_response(message=errors, status_code=400)
        
        if SalesOrderService.get_by_number(data['order_number']):
            return api_response(message='Order number already exists', status_code=400)
        
        # Load data to transform date strings to date objects
        loaded_data = sales_order_create_schema.load(data)
        order = SalesOrderService.create(created_by=current_user.user_id, **loaded_data)
        return api_response(data=order.to_dict(include_items=True), message='Sales order created', status_code=201)


@sales_orders_ns.route('/generate-number')
class GenerateOrderNumber(Resource):
    @sales_orders_ns.doc('generate_order_number')
    @login_required
    @require_role('admin', 'manager', 'staff')
    def get(self):
        """Generate a new order number."""
        order_number = SalesOrderService.generate_order_number()
        return api_response(data={'order_number': order_number})


@sales_orders_ns.route('/<int:order_id>')
class SalesOrderDetail(Resource):
    @sales_orders_ns.doc('get_sales_order')
    @login_required
    def get(self, order_id):
        """Get sales order by ID."""
        include_items = request.args.get('include_items', 'true').lower() == 'true'
        include_customer = request.args.get('include_customer', 'false').lower() == 'true'
        
        order = SalesOrderService.get_by_id(order_id)
        if not order:
            return api_response(message='Sales order not found', status_code=404)
        return api_response(data=order.to_dict(include_items=include_items, include_customer=include_customer))

    @sales_orders_ns.doc('update_sales_order')
    @login_required
    @require_role('admin', 'manager')
    def put(self, order_id):
        """Update sales order."""
        order = SalesOrderService.get_by_id(order_id)
        if not order:
            return api_response(message='Sales order not found', status_code=404)
        
        data = request.get_json()
        order = SalesOrderService.update(order, **data)
        return api_response(data=order.to_dict(), message='Sales order updated')


@sales_orders_ns.route('/<int:order_id>/status')
class SalesOrderStatus(Resource):
    @sales_orders_ns.expect(order_status_model)
    @sales_orders_ns.doc('update_order_status')
    @login_required
    @require_role('admin', 'manager', 'staff')
    def put(self, order_id):
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


@sales_orders_ns.route('/<int:order_id>/payment-status')
class SalesOrderPaymentStatus(Resource):
    @sales_orders_ns.expect(payment_status_model)
    @sales_orders_ns.doc('update_payment_status')
    @login_required
    @require_role('admin', 'manager')
    def put(self, order_id):
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


@sales_orders_ns.route('/<int:order_id>/items')
class SalesOrderItems(Resource):
    @sales_orders_ns.expect(so_item_model)
    @sales_orders_ns.doc('add_order_item')
    @login_required
    @require_role('admin', 'manager', 'staff')
    def post(self, order_id):
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


@sales_orders_ns.route('/<int:order_id>/cancel')
class CancelSalesOrder(Resource):
    @sales_orders_ns.doc('cancel_order')
    @login_required
    @require_role('admin', 'manager')
    def post(self, order_id):
        """Cancel a sales order."""
        order = SalesOrderService.get_by_id(order_id)
        if not order:
            return api_response(message='Sales order not found', status_code=404)
        
        if order.status in ['delivered', 'cancelled']:
            return api_response(message='Cannot cancel this order', status_code=400)
        
        order = SalesOrderService.cancel_order(order)
        return api_response(data=order.to_dict(), message='Order cancelled')
