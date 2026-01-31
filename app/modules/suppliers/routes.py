# Supplier routes

from flask import request
from flask_login import login_required

from app.modules.suppliers import suppliers_bp
from app.modules.suppliers.services import SupplierService
from app.modules.suppliers.schemas import supplier_create_schema
from app.core.utils import api_response, require_role


@suppliers_bp.route('', methods=['GET'])
@login_required
def get_suppliers():
    """Get all suppliers."""
    search_query = request.args.get('search')
    if search_query:
        suppliers = SupplierService.search(search_query)
    else:
        suppliers = SupplierService.get_all()
    return api_response(data=[s.to_dict() for s in suppliers])


@suppliers_bp.route('/<int:supplier_id>', methods=['GET'])
@login_required
def get_supplier(supplier_id):
    """Get supplier by ID."""
    supplier = SupplierService.get_by_id(supplier_id)
    if not supplier:
        return api_response(message='Supplier not found', status_code=404)
    return api_response(data=supplier.to_dict())


@suppliers_bp.route('', methods=['POST'])
@login_required
@require_role('admin', 'manager')
def create_supplier():
    """Create a new supplier."""
    data = request.get_json()
    errors = supplier_create_schema.validate(data)
    if errors:
        return api_response(message=errors, status_code=400)
    
    supplier = SupplierService.create(**data)
    return api_response(data=supplier.to_dict(), message='Supplier created', status_code=201)


@suppliers_bp.route('/<int:supplier_id>', methods=['PUT'])
@login_required
@require_role('admin', 'manager')
def update_supplier(supplier_id):
    """Update supplier."""
    supplier = SupplierService.get_by_id(supplier_id)
    if not supplier:
        return api_response(message='Supplier not found', status_code=404)
    
    data = request.get_json()
    supplier = SupplierService.update(supplier, **data)
    return api_response(data=supplier.to_dict(), message='Supplier updated')


@suppliers_bp.route('/<int:supplier_id>', methods=['DELETE'])
@login_required
@require_role('admin')
def delete_supplier(supplier_id):
    """Delete supplier."""
    supplier = SupplierService.get_by_id(supplier_id)
    if not supplier:
        return api_response(message='Supplier not found', status_code=404)
    
    SupplierService.delete(supplier)
    return api_response(message='Supplier deleted')
