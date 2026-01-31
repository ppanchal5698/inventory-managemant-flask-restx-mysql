# Warehouses API endpoints using Flask-RESTX

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_required

from app.modules.warehouses.services import WarehouseService
from app.modules.warehouses.schemas import warehouse_create_schema
from app.core.utils import api_response, require_role

warehouses_ns = Namespace('warehouses', description='Warehouse operations')

# API Models for Swagger documentation
warehouse_model = warehouses_ns.model('Warehouse', {
    'warehouse_id': fields.Integer(readonly=True),
    'warehouse_name': fields.String(required=True),
    'location': fields.String(),
    'city': fields.String(),
    'country': fields.String(),
    'capacity': fields.Integer(),
    'is_active': fields.Boolean(readonly=True),
    'created_at': fields.DateTime(readonly=True)
})


@warehouses_ns.route('')
class WarehouseList(Resource):
    @warehouses_ns.doc('list_warehouses')
    @login_required
    def get(self):
        """Get all warehouses."""
        warehouses = WarehouseService.get_all()
        return api_response(data=[w.to_dict() for w in warehouses])

    @warehouses_ns.doc('create_warehouse')
    @login_required
    @require_role('admin', 'manager')
    def post(self):
        """Create a new warehouse."""
        data = request.get_json()
        errors = warehouse_create_schema.validate(data)
        if errors:
            return api_response(message=errors, status_code=400)
        
        warehouse = WarehouseService.create(**data)
        return api_response(data=warehouse.to_dict(), message='Warehouse created', status_code=201)


@warehouses_ns.route('/<int:warehouse_id>')
class WarehouseDetail(Resource):
    @warehouses_ns.doc('get_warehouse')
    @login_required
    def get(self, warehouse_id):
        """Get warehouse by ID."""
        warehouse = WarehouseService.get_by_id(warehouse_id)
        if not warehouse:
            return api_response(message='Warehouse not found', status_code=404)
        return api_response(data=warehouse.to_dict())

    @warehouses_ns.doc('update_warehouse')
    @login_required
    @require_role('admin', 'manager')
    def put(self, warehouse_id):
        """Update warehouse."""
        warehouse = WarehouseService.get_by_id(warehouse_id)
        if not warehouse:
            return api_response(message='Warehouse not found', status_code=404)
        
        data = request.get_json()
        warehouse = WarehouseService.update(warehouse, **data)
        return api_response(data=warehouse.to_dict(), message='Warehouse updated')

    @warehouses_ns.doc('delete_warehouse')
    @login_required
    @require_role('admin')
    def delete(self, warehouse_id):
        """Delete warehouse."""
        warehouse = WarehouseService.get_by_id(warehouse_id)
        if not warehouse:
            return api_response(message='Warehouse not found', status_code=404)
        
        WarehouseService.delete(warehouse)
        return api_response(message='Warehouse deleted')
