# Customer routes

from flask import request
from flask_login import login_required

from app.modules.customers import customers_bp
from app.modules.customers.services import CustomerService
from app.modules.customers.schemas import customer_create_schema
from app.core.utils import api_response, require_role


@customers_bp.route('', methods=['GET'])
@login_required
def get_customers():
    """Get all customers."""
    search_query = request.args.get('search')
    if search_query:
        customers = CustomerService.search(search_query)
    else:
        customers = CustomerService.get_all()
    return api_response(data=[c.to_dict() for c in customers])


@customers_bp.route('/<int:customer_id>', methods=['GET'])
@login_required
def get_customer(customer_id):
    """Get customer by ID."""
    customer = CustomerService.get_by_id(customer_id)
    if not customer:
        return api_response(message='Customer not found', status_code=404)
    return api_response(data=customer.to_dict())


@customers_bp.route('', methods=['POST'])
@login_required
@require_role('admin', 'manager', 'staff')
def create_customer():
    """Create a new customer."""
    data = request.get_json()
    errors = customer_create_schema.validate(data)
    if errors:
        return api_response(message=errors, status_code=400)
    
    customer = CustomerService.create(**data)
    return api_response(data=customer.to_dict(), message='Customer created', status_code=201)


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@login_required
@require_role('admin', 'manager', 'staff')
def update_customer(customer_id):
    """Update customer."""
    customer = CustomerService.get_by_id(customer_id)
    if not customer:
        return api_response(message='Customer not found', status_code=404)
    
    data = request.get_json()
    customer = CustomerService.update(customer, **data)
    return api_response(data=customer.to_dict(), message='Customer updated')


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@login_required
@require_role('admin', 'manager')
def delete_customer(customer_id):
    """Delete customer."""
    customer = CustomerService.get_by_id(customer_id)
    if not customer:
        return api_response(message='Customer not found', status_code=404)
    
    CustomerService.delete(customer)
    return api_response(message='Customer deleted')
