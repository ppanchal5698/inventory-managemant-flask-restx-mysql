# Customers API endpoints using Flask-RESTX

from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields

from app.modules.customers.services import CustomerService
from app.modules.customers.schemas import CustomerCreate
from app.core.utils import api_response, require_role, async_route

customers_ns = Namespace('customers', description='Customer operations')

# API Models for Swagger documentation
customer_model = customers_ns.model('Customer', {
    'customer_id': fields.Integer(readonly=True),
    'customer_name': fields.String(required=True),
    'contact_person': fields.String(),
    'email': fields.String(),
    'phone': fields.String(),
    'address': fields.String(),
    'city': fields.String(),
    'state': fields.String(),
    'country': fields.String(),
    'postal_code': fields.String(),
    'tax_id': fields.String(),
    'credit_limit': fields.Float(),
    'is_active': fields.Boolean(readonly=True),
    'created_at': fields.DateTime(readonly=True)
})

customer_create_model = customers_ns.model('CustomerCreate', {
    'customer_name': fields.String(required=True),
    'contact_person': fields.String(),
    'email': fields.String(),
    'phone': fields.String(),
    'address': fields.String(),
    'city': fields.String(),
    'state': fields.String(),
    'country': fields.String(),
    'postal_code': fields.String(),
    'tax_id': fields.String(),
    'credit_limit': fields.Float()
})


@customers_ns.route('')
class CustomerList(Resource):
    @customers_ns.doc('list_customers')
    @jwt_required()
    @async_route
    async def get(self):
        """Get all customers."""
        search_query = request.args.get('search')
        if search_query:
            customers = await CustomerService.search(search_query)
        else:
            customers = await CustomerService.get_all()
        return api_response(data=[c.to_dict() for c in customers])

    @customers_ns.expect(customer_create_model)
    @customers_ns.doc('create_customer')
    @require_role('admin', 'manager')
    @async_route
    async def post(self):
        """Create a new customer."""
        try:
            data = CustomerCreate.model_validate(request.get_json())
        except Exception as e:
            return api_response(message=str(e), status_code=400)
        
        customer = await CustomerService.create(**data.model_dump())
        return api_response(data=customer.to_dict(), message='Customer created', status_code=201)


@customers_ns.route('/<int:customer_id>')
class CustomerDetail(Resource):
    @customers_ns.doc('get_customer')
    @jwt_required()
    @async_route
    async def get(self, customer_id):
        """Get customer by ID."""
        customer = await CustomerService.get_by_id(customer_id)
        if not customer:
            return api_response(message='Customer not found', status_code=404)
        return api_response(data=customer.to_dict())

    @customers_ns.doc('update_customer')
    @require_role('admin', 'manager')
    @async_route
    async def put(self, customer_id):
        """Update customer."""
        customer = await CustomerService.get_by_id(customer_id)
        if not customer:
            return api_response(message='Customer not found', status_code=404)
        
        data = request.get_json()
        customer = await CustomerService.update(customer, **data)
        return api_response(data=customer.to_dict(), message='Customer updated')

    @customers_ns.doc('delete_customer')
    @require_role('admin')
    @async_route
    async def delete(self, customer_id):
        """Delete customer."""
        customer = await CustomerService.get_by_id(customer_id)
        if not customer:
            return api_response(message='Customer not found', status_code=404)
        
        await CustomerService.delete(customer)
        return api_response(message='Customer deleted')
