# Warehouses API endpoints using Flask-RESTX

from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields

from app.modules.warehouses.services import WarehouseService
from app.modules.warehouses.schemas import WarehouseCreate
from app.core.utils import api_response, require_role, async_route

warehouses_ns = Namespace('warehouses', description='Warehouse operations')

# API Models for Swagger documentation
warehouse_model = warehouses_ns.model('Warehouse', {
    'warehouse_id': fields.Integer(readonly=True),
    'warehouse_name': fields.String(required=True),
    'location': fields.String(),
    'address': fields.String(),
    'city': fields.String(),
    'state': fields.String(),
    'country': fields.String(),
    'postal_code': fields.String(),
    'manager_name': fields.String(),
    'phone': fields.String(),
    'capacity': fields.Integer(),
    'is_active': fields.Boolean(readonly=True),
    'created_at': fields.DateTime(readonly=True)
})

warehouse_create_model = warehouses_ns.model('WarehouseCreate', {
    'warehouse_name': fields.String(required=True),
    'location': fields.String(),
    'address': fields.String(),
    'city': fields.String(),
    'state': fields.String(),
    'country': fields.String(),
    'postal_code': fields.String(),
    'manager_name': fields.String(),
    'phone': fields.String(),
    'capacity': fields.Integer()
})


@warehouses_ns.route('')
class WarehouseList(Resource):
    @warehouses_ns.doc('list_warehouses')
    @jwt_required()
    @async_route
    async def get(self):
        """Get all warehouses."""
        warehouses = await WarehouseService.get_all()
        return api_response(data=[w.to_dict() for w in warehouses])

    @warehouses_ns.expect(warehouse_create_model)
    @warehouses_ns.doc('create_warehouse')
    @require_role('admin', 'manager')
    @async_route
    async def post(self):
        """Create a new warehouse."""
        try:
            data = WarehouseCreate.model_validate(request.get_json())
        except Exception as e:
            return api_response(message=str(e), status_code=400)
        
        warehouse = await WarehouseService.create(**data.model_dump())
        return api_response(data=warehouse.to_dict(), message='Warehouse created', status_code=201)


@warehouses_ns.route('/<int:warehouse_id>')
class WarehouseDetail(Resource):
    @warehouses_ns.doc('get_warehouse')
    @jwt_required()
    @async_route
    async def get(self, warehouse_id):
        """Get warehouse by ID."""
        warehouse = await WarehouseService.get_by_id(warehouse_id)
        if not warehouse:
            return api_response(message='Warehouse not found', status_code=404)
        return api_response(data=warehouse.to_dict())

    @warehouses_ns.doc('update_warehouse')
    @require_role('admin', 'manager')
    @async_route
    async def put(self, warehouse_id):
        """Update warehouse."""
        warehouse = await WarehouseService.get_by_id(warehouse_id)
        if not warehouse:
            return api_response(message='Warehouse not found', status_code=404)
        
        data = request.get_json()
        warehouse = await WarehouseService.update(warehouse, **data)
        return api_response(data=warehouse.to_dict(), message='Warehouse updated')

    @warehouses_ns.doc('delete_warehouse')
    @require_role('admin')
    @async_route
    async def delete(self, warehouse_id):
        """Delete warehouse."""
        warehouse = await WarehouseService.get_by_id(warehouse_id)
        if not warehouse:
            return api_response(message='Warehouse not found', status_code=404)
        
        await WarehouseService.delete(warehouse)
        return api_response(message='Warehouse deleted')
