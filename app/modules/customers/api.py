# Customers API endpoints using Flask-RESTX

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_required

from app.modules.customers.services import CustomerService
from app.modules.customers.schemas import customer_create_schema
from app.core.utils import api_response, require_role

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
    'country': fields.String(),
    'is_active': fields.Boolean(readonly=True),
    'created_at': fields.DateTime(readonly=True)
})


@customers_ns.route('')
class CustomerList(Resource):
    @customers_ns.doc('list_customers')
    @login_required
    def get(self):
        """Get all customers."""
        search_query = request.args.get('search')
        if search_query:
            customers = CustomerService.search(search_query)
        else:
            customers = CustomerService.get_all()
        return api_response(data=[c.to_dict() for c in customers])

    @customers_ns.doc('create_customer')
    @login_required
    @require_role('admin', 'manager', 'staff')
    def post(self):
        """Create a new customer."""
        data = request.get_json()
        errors = customer_create_schema.validate(data)
        if errors:
            return api_response(message=errors, status_code=400)
        
        customer = CustomerService.create(**data)
        return api_response(data=customer.to_dict(), message='Customer created', status_code=201)


@customers_ns.route('/<int:customer_id>')
class CustomerDetail(Resource):
    @customers_ns.doc('get_customer')
    @login_required
    def get(self, customer_id):
        """Get customer by ID."""
        customer = CustomerService.get_by_id(customer_id)
        if not customer:
            return api_response(message='Customer not found', status_code=404)
        return api_response(data=customer.to_dict())

    @customers_ns.doc('update_customer')
    @login_required
    @require_role('admin', 'manager', 'staff')
    def put(self, customer_id):
        """Update customer."""
        customer = CustomerService.get_by_id(customer_id)
        if not customer:
            return api_response(message='Customer not found', status_code=404)
        
        data = request.get_json()
        customer = CustomerService.update(customer, **data)
        return api_response(data=customer.to_dict(), message='Customer updated')

    @customers_ns.doc('delete_customer')
    @login_required
    @require_role('admin', 'manager')
    def delete(self, customer_id):
        """Delete customer."""
        customer = CustomerService.get_by_id(customer_id)
        if not customer:
            return api_response(message='Customer not found', status_code=404)
        
        CustomerService.delete(customer)
        return api_response(message='Customer deleted')
