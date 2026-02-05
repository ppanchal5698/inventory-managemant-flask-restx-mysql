# Suppliers API endpoints using Flask-RESTX

from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields

from app.modules.suppliers.services import SupplierService
from app.modules.suppliers.schemas import SupplierCreate
from app.core.utils import api_response, require_role, async_route

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

supplier_create_model = suppliers_ns.model('SupplierCreate', {
    'supplier_name': fields.String(required=True),
    'contact_person': fields.String(),
    'email': fields.String(),
    'phone': fields.String(),
    'address': fields.String(),
    'city': fields.String(),
    'state': fields.String(),
    'country': fields.String(),
    'postal_code': fields.String(),
    'tax_id': fields.String(),
    'payment_terms': fields.String()
})


@suppliers_ns.route('')
class SupplierList(Resource):
    @suppliers_ns.doc('list_suppliers')
    @jwt_required()
    @async_route
    async def get(self):
        """Get all suppliers."""
        search_query = request.args.get('search')
        if search_query:
            suppliers = await SupplierService.search(search_query)
        else:
            suppliers = await SupplierService.get_all()
        return api_response(data=[s.to_dict() for s in suppliers])

    @suppliers_ns.expect(supplier_create_model)
    @suppliers_ns.doc('create_supplier')
    @require_role('admin', 'manager')
    @async_route
    async def post(self):
        """Create a new supplier."""
        try:
            data = SupplierCreate.model_validate(request.get_json())
        except Exception as e:
            return api_response(message=str(e), status_code=400)
        
        supplier = await SupplierService.create(**data.model_dump())
        return api_response(data=supplier.to_dict(), message='Supplier created', status_code=201)


@suppliers_ns.route('/<int:supplier_id>')
class SupplierDetail(Resource):
    @suppliers_ns.doc('get_supplier')
    @jwt_required()
    @async_route
    async def get(self, supplier_id):
        """Get supplier by ID."""
        supplier = await SupplierService.get_by_id(supplier_id)
        if not supplier:
            return api_response(message='Supplier not found', status_code=404)
        return api_response(data=supplier.to_dict())

    @suppliers_ns.doc('update_supplier')
    @require_role('admin', 'manager')
    @async_route
    async def put(self, supplier_id):
        """Update supplier."""
        supplier = await SupplierService.get_by_id(supplier_id)
        if not supplier:
            return api_response(message='Supplier not found', status_code=404)
        
        data = request.get_json()
        supplier = await SupplierService.update(supplier, **data)
        return api_response(data=supplier.to_dict(), message='Supplier updated')

    @suppliers_ns.doc('delete_supplier')
    @require_role('admin')
    @async_route
    async def delete(self, supplier_id):
        """Delete supplier."""
        supplier = await SupplierService.get_by_id(supplier_id)
        if not supplier:
            return api_response(message='Supplier not found', status_code=404)
        
        await SupplierService.delete(supplier)
        return api_response(message='Supplier deleted')
