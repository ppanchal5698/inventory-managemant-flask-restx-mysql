# Brand routes

from flask import request
from flask_login import login_required

from app.modules.brands import brands_bp
from app.modules.brands.services import BrandService
from app.modules.brands.schemas import brand_create_schema
from app.core.utils import api_response, require_role


@brands_bp.route('', methods=['GET'])
@login_required
def get_brands():
    """Get all brands."""
    brands = BrandService.get_all()
    return api_response(data=[b.to_dict() for b in brands])


@brands_bp.route('/<int:brand_id>', methods=['GET'])
@login_required
def get_brand(brand_id):
    """Get brand by ID."""
    brand = BrandService.get_by_id(brand_id)
    if not brand:
        return api_response(message='Brand not found', status_code=404)
    return api_response(data=brand.to_dict())


@brands_bp.route('', methods=['POST'])
@login_required
@require_role('admin', 'manager')
def create_brand():
    """Create a new brand."""
    data = request.get_json()
    errors = brand_create_schema.validate(data)
    if errors:
        return api_response(message=errors, status_code=400)
    
    # Check if brand name already exists
    if BrandService.get_by_name(data['brand_name']):
        return api_response(message='Brand name already exists', status_code=400)
    
    brand = BrandService.create(**data)
    return api_response(data=brand.to_dict(), message='Brand created', status_code=201)


@brands_bp.route('/<int:brand_id>', methods=['PUT'])
@login_required
@require_role('admin', 'manager')
def update_brand(brand_id):
    """Update brand."""
    brand = BrandService.get_by_id(brand_id)
    if not brand:
        return api_response(message='Brand not found', status_code=404)
    
    data = request.get_json()
    brand = BrandService.update(brand, **data)
    return api_response(data=brand.to_dict(), message='Brand updated')


@brands_bp.route('/<int:brand_id>', methods=['DELETE'])
@login_required
@require_role('admin')
def delete_brand(brand_id):
    """Delete brand."""
    brand = BrandService.get_by_id(brand_id)
    if not brand:
        return api_response(message='Brand not found', status_code=404)
    
    BrandService.delete(brand)
    return api_response(message='Brand deleted')
