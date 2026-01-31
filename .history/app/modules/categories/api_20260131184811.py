# Categories API endpoints using Flask-RESTX

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_required

from app.modules.categories.services import CategoryService
from app.modules.categories.schemas import category_schema, categories_schema, category_create_schema
from app.core.utils import api_response, require_role

categories_ns = Namespace('categories', description='Category operations')

# API Models for Swagger documentation
category_model = categories_ns.model('Category', {
    'category_id': fields.Integer(readonly=True),
    'category_name': fields.String(required=True),
    'parent_category_id': fields.Integer(),
    'description': fields.String(),
    'is_active': fields.Boolean(readonly=True),
    'created_at': fields.DateTime(readonly=True)
})

category_create_model = categories_ns.model('CategoryCreate', {
    'category_name': fields.String(required=True),
    'parent_category_id': fields.Integer(),
    'description': fields.String()
})


@categories_ns.route('')
class CategoryList(Resource):
    @categories_ns.doc('list_categories')
    @login_required
    def get(self):
        """Get all categories."""
        root_only = request.args.get('root_only', 'false').lower() == 'true'
        if root_only:
            categories = CategoryService.get_root_categories()
        else:
            categories = CategoryService.get_all()
        return api_response(data=[c.to_dict() for c in categories])

    @categories_ns.expect(category_create_model)
    @categories_ns.doc('create_category')
    @login_required
    @require_role('admin', 'manager')
    def post(self):
        """Create a new category."""
        data = request.get_json()
        errors = category_create_schema.validate(data)
        if errors:
            return api_response(message=errors, status_code=400)
        
        category = CategoryService.create(**data)
        return api_response(data=category.to_dict(), message='Category created', status_code=201)


@categories_ns.route('/<int:category_id>')
class CategoryDetail(Resource):
    @categories_ns.doc('get_category')
    @login_required
    def get(self, category_id):
        """Get category by ID."""
        include_children = request.args.get('include_children', 'false').lower() == 'true'
        category = CategoryService.get_by_id(category_id)
        if not category:
            return api_response(message='Category not found', status_code=404)
        
        # If include_children is True, we need to ensure the object is attached to a session
        # to avoid DetachedInstanceError when accessing subcategories
        if include_children:
            from app.extensions import db
            # Merge the potentially detached cached object into the current session
            category = db.session.merge(category)
        
        return api_response(data=category.to_dict(include_children=include_children))

    @categories_ns.doc('update_category')
    @login_required
    @require_role('admin', 'manager')
    def put(self, category_id):
        """Update category."""
        category = CategoryService.get_by_id(category_id)
        if not category:
            return api_response(message='Category not found', status_code=404)
        
        data = request.get_json()
        category = CategoryService.update(category, **data)
        return api_response(data=category.to_dict(), message='Category updated')

    @categories_ns.doc('delete_category')
    @login_required
    @require_role('admin')
    def delete(self, category_id):
        """Delete category."""
        category = CategoryService.get_by_id(category_id)
        if not category:
            return api_response(message='Category not found', status_code=404)
        
        CategoryService.delete(category)
        return api_response(message='Category deleted')


@categories_ns.route('/<int:category_id>/subcategories')
class CategorySubcategories(Resource):
    @categories_ns.doc('get_subcategories')
    @login_required
    def get(self, category_id):
        """Get subcategories of a category."""
        subcategories = CategoryService.get_subcategories(category_id)
        return api_response(data=[c.to_dict() for c in subcategories])
