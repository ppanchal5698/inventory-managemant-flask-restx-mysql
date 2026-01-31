# Category routes

from flask import request
from flask_login import login_required

from app.modules.categories import categories_bp
from app.modules.categories.services import CategoryService
from app.modules.categories.schemas import category_schema, categories_schema, category_create_schema
from app.core.utils import api_response, require_role


@categories_bp.route('', methods=['GET'])
@login_required
def get_categories():
    """Get all categories."""
    root_only = request.args.get('root_only', 'false').lower() == 'true'
    if root_only:
        categories = CategoryService.get_root_categories()
    else:
        categories = CategoryService.get_all()
    return api_response(data=[c.to_dict() for c in categories])


@categories_bp.route('/<int:category_id>', methods=['GET'])
@login_required
def get_category(category_id):
    """Get category by ID."""
    include_children = request.args.get('include_children', 'false').lower() == 'true'
    category = CategoryService.get_by_id(category_id)
    if not category:
        return api_response(message='Category not found', status_code=404)
    return api_response(data=category.to_dict(include_children=include_children))


@categories_bp.route('/<int:category_id>/subcategories', methods=['GET'])
@login_required
def get_subcategories(category_id):
    """Get subcategories of a category."""
    subcategories = CategoryService.get_subcategories(category_id)
    return api_response(data=[c.to_dict() for c in subcategories])


@categories_bp.route('', methods=['POST'])
@login_required
@require_role('admin', 'manager')
def create_category():
    """Create a new category."""
    data = request.get_json()
    errors = category_create_schema.validate(data)
    if errors:
        return api_response(message=errors, status_code=400)
    
    category = CategoryService.create(**data)
    return api_response(data=category.to_dict(), message='Category created', status_code=201)


@categories_bp.route('/<int:category_id>', methods=['PUT'])
@login_required
@require_role('admin', 'manager')
def update_category(category_id):
    """Update category."""
    category = CategoryService.get_by_id(category_id)
    if not category:
        return api_response(message='Category not found', status_code=404)
    
    data = request.get_json()
    category = CategoryService.update(category, **data)
    return api_response(data=category.to_dict(), message='Category updated')


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@login_required
@require_role('admin')
def delete_category(category_id):
    """Delete category."""
    category = CategoryService.get_by_id(category_id)
    if not category:
        return api_response(message='Category not found', status_code=404)
    
    CategoryService.delete(category)
    return api_response(message='Category deleted')
