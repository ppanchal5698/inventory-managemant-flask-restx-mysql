# Brands API endpoints using Flask-RESTX

from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields

from app.modules.brands.services import BrandService
from app.modules.brands.schemas import BrandCreate
from app.core.utils import api_response, require_role, async_route

brands_ns = Namespace('brands', description='Brand operations')

# API Models for Swagger documentation
brand_model = brands_ns.model('Brand', {
    'brand_id': fields.Integer(readonly=True),
    'brand_name': fields.String(required=True),
    'manufacturer_name': fields.String(),
    'description': fields.String(),
    'is_active': fields.Boolean(readonly=True),
    'created_at': fields.DateTime(readonly=True)
})

brand_create_model = brands_ns.model('BrandCreate', {
    'brand_name': fields.String(required=True),
    'manufacturer_name': fields.String(),
    'description': fields.String()
})


@brands_ns.route('')
class BrandList(Resource):
    @brands_ns.doc('list_brands')
    @jwt_required()
    @async_route
    async def get(self):
        """Get all brands."""
        brands = await BrandService.get_all()
        return api_response(data=[b.to_dict() for b in brands])

    @brands_ns.expect(brand_create_model)
    @brands_ns.doc('create_brand')
    @require_role('admin', 'manager')
    @async_route
    async def post(self):
        """Create a new brand."""
        try:
            data = BrandCreate.model_validate(request.get_json())
        except Exception as e:
            return api_response(message=str(e), status_code=400)
        
        if await BrandService.get_by_name(data.brand_name):
            return api_response(message='Brand name already exists', status_code=400)
        
        brand = await BrandService.create(**data.model_dump())
        return api_response(data=brand.to_dict(), message='Brand created', status_code=201)


@brands_ns.route('/<int:brand_id>')
class BrandDetail(Resource):
    @brands_ns.doc('get_brand')
    @jwt_required()
    @async_route
    async def get(self, brand_id):
        """Get brand by ID."""
        brand = await BrandService.get_by_id(brand_id)
        if not brand:
            return api_response(message='Brand not found', status_code=404)
        return api_response(data=brand.to_dict())

    @brands_ns.doc('update_brand')
    @require_role('admin', 'manager')
    @async_route
    async def put(self, brand_id):
        """Update brand."""
        brand = await BrandService.get_by_id(brand_id)
        if not brand:
            return api_response(message='Brand not found', status_code=404)
        
        data = request.get_json()
        brand = await BrandService.update(brand, **data)
        return api_response(data=brand.to_dict(), message='Brand updated')

    @brands_ns.doc('delete_brand')
    @require_role('admin')
    @async_route
    async def delete(self, brand_id):
        """Delete brand."""
        brand = await BrandService.get_by_id(brand_id)
        if not brand:
            return api_response(message='Brand not found', status_code=404)
        
        await BrandService.delete(brand)
        return api_response(message='Brand deleted')
