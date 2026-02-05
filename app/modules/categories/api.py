# Categories API endpoints using Flask-RESTX

from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields

from app.core.utils import api_response, require_role, async_route
from app.modules.categories.schemas import (
    CategoryCreate
)
from app.modules.categories.services import CategoryService

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
    @jwt_required()
    @async_route
    async def get(self):
        """Get all categories."""
        root_only = request.args.get('root_only', 'false').lower() == 'true'
        if root_only:
            categories = await CategoryService.get_root_categories()
        else:
            categories = await CategoryService.get_all()
        return api_response(data=[c.to_dict() for c in categories])

    @categories_ns.expect(category_create_model)
    @categories_ns.doc('create_category')
    @require_role('admin', 'manager')
    @async_route
    async def post(self):
        """Create a new category."""
        try:
            data = CategoryCreate.model_validate(request.get_json())
        except Exception as e:
            return api_response(message=str(e), status_code=400)

        category = await CategoryService.create(**data.model_dump())
        return api_response(data=category.to_dict(), message='Category created', status_code=201)


@categories_ns.route('/<int:category_id>')
class CategoryDetail(Resource):
    @categories_ns.doc('get_category')
    @jwt_required()
    @async_route
    async def get(self, category_id):
        """Get category by ID."""
        include_children = request.args.get('include_children', 'false').lower() == 'true'
        category = await CategoryService.get_by_id(category_id, load_children=include_children)
        if not category:
            return api_response(message='Category not found', status_code=404)

        return api_response(data=category.to_dict(include_children=include_children))

    @categories_ns.doc('update_category')
    @require_role('admin', 'manager')
    @async_route
    async def put(self, category_id):
        """Update category."""
        category = await CategoryService.get_by_id(category_id)
        if not category:
            return api_response(message='Category not found', status_code=404)

        data = request.get_json()
        category = await CategoryService.update(category, **data)
        return api_response(data=category.to_dict(), message='Category updated')

    @categories_ns.doc('delete_category')
    @require_role('admin')
    @async_route
    async def delete(self, category_id):
        """Delete category."""
        category = await CategoryService.get_by_id(category_id)
        if not category:
            return api_response(message='Category not found', status_code=404)

        await CategoryService.delete(category)
        return api_response(message='Category deleted')


@categories_ns.route('/<int:category_id>/subcategories')
class CategorySubcategories(Resource):
    @categories_ns.doc('get_subcategories')
    @jwt_required()
    @async_route
    async def get(self, category_id):
        """Get subcategories of a category."""
        subcategories = await CategoryService.get_subcategories(category_id)
        return api_response(data=[c.to_dict() for c in subcategories])
