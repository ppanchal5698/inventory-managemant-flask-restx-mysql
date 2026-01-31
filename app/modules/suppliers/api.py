# Suppliers API endpoints using Flask-RESTX

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_required

from app.modules.suppliers.services import SupplierService
from app.modules.suppliers.schemas import supplier_create_schema
from app.core.utils import api_response, require_role

suppliers_ns = Namespace('suppliers', description='Supplier operations')

# API Models for Swagger documentation
supplier_model = suppliers_ns.model('Supplier', {
    'supplier_id': fields.Integer(readonly=True),
    'supplier_name': fields.String(required=True),
    'contact_person': fields.String(),
    'email': fields.String(),
    'phone': fields.String(),
    'address': fields.String(),
    'city': fields.String(),
    'country': fields.String(),
    'is_active': fields.Boolean(readonly=True),
    'created_at': fields.DateTime(readonly=True)
})


@suppliers_ns.route('')
class SupplierList(Resource):
    @suppliers_ns.doc('list_suppliers')
    @login_required
    def get(self):
        """Get all suppliers."""
        search_query = request.args.get('search')
        if search_query:
            suppliers = SupplierService.search(search_query)
        else:
            suppliers = SupplierService.get_all()
        return api_response(data=[s.to_dict() for s in suppliers])

    @suppliers_ns.doc('create_supplier')
    @login_required
    @require_role('admin', 'manager')
    def post(self):
        """Create a new supplier."""
        data = request.get_json()
        errors = supplier_create_schema.validate(data)
        if errors:
            return api_response(message=errors, status_code=400)
        
        supplier = SupplierService.create(**data)
        return api_response(data=supplier.to_dict(), message='Supplier created', status_code=201)


@suppliers_ns.route('/<int:supplier_id>')
class SupplierDetail(Resource):
    @suppliers_ns.doc('get_supplier')
    @login_required
    def get(self, supplier_id):
        """Get supplier by ID."""
        supplier = SupplierService.get_by_id(supplier_id)
        if not supplier:
            return api_response(message='Supplier not found', status_code=404)
        return api_response(data=supplier.to_dict())

    @suppliers_ns.doc('update_supplier')
    @login_required
    @require_role('admin', 'manager')
    def put(self, supplier_id):
        """Update supplier."""
        supplier = SupplierService.get_by_id(supplier_id)
        if not supplier:
            return api_response(message='Supplier not found', status_code=404)
        
        data = request.get_json()
        supplier = SupplierService.update(supplier, **data)
        return api_response(data=supplier.to_dict(), message='Supplier updated')

    @suppliers_ns.doc('delete_supplier')
    @login_required
    @require_role('admin')
    def delete(self, supplier_id):
        """Delete supplier."""
        supplier = SupplierService.get_by_id(supplier_id)
        if not supplier:
            return api_response(message='Supplier not found', status_code=404)
        
        SupplierService.delete(supplier)
        return api_response(message='Supplier deleted')
