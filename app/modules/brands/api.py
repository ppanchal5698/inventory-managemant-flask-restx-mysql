# Brands API endpoints using Flask-RESTX

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_required

from app.modules.brands.services import BrandService
from app.modules.brands.schemas import brand_create_schema
from app.core.utils import api_response, require_role

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


@brands_ns.route('')
class BrandList(Resource):
    @brands_ns.doc('list_brands')
    @login_required
    def get(self):
        """Get all brands."""
        brands = BrandService.get_all()
        return api_response(data=[b.to_dict() for b in brands])

    @brands_ns.doc('create_brand')
    @login_required
    @require_role('admin', 'manager')
    def post(self):
        """Create a new brand."""
        data = request.get_json()
        errors = brand_create_schema.validate(data)
        if errors:
            return api_response(message=errors, status_code=400)
        
        if BrandService.get_by_name(data['brand_name']):
            return api_response(message='Brand name already exists', status_code=400)
        
        brand = BrandService.create(**data)
        return api_response(data=brand.to_dict(), message='Brand created', status_code=201)


@brands_ns.route('/<int:brand_id>')
class BrandDetail(Resource):
    @brands_ns.doc('get_brand')
    @login_required
    def get(self, brand_id):
        """Get brand by ID."""
        brand = BrandService.get_by_id(brand_id)
        if not brand:
            return api_response(message='Brand not found', status_code=404)
        return api_response(data=brand.to_dict())

    @brands_ns.doc('update_brand')
    @login_required
    @require_role('admin', 'manager')
    def put(self, brand_id):
        """Update brand."""
        brand = BrandService.get_by_id(brand_id)
        if not brand:
            return api_response(message='Brand not found', status_code=404)
        
        data = request.get_json()
        brand = BrandService.update(brand, **data)
        return api_response(data=brand.to_dict(), message='Brand updated')

    @brands_ns.doc('delete_brand')
    @login_required
    @require_role('admin')
    def delete(self, brand_id):
        """Delete brand."""
        brand = BrandService.get_by_id(brand_id)
        if not brand:
            return api_response(message='Brand not found', status_code=404)
        
        BrandService.delete(brand)
        return api_response(message='Brand deleted')
