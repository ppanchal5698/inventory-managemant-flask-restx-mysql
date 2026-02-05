# Products API endpoints using Flask-RESTX

from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields

from app.modules.products.services import ProductService
from app.modules.products.schemas import ProductCreate
from app.core.utils import api_response, require_role, async_route

products_ns = Namespace('products', description='Product operations')

# API Models for Swagger documentation
product_model = products_ns.model('Product', {
    'product_id': fields.Integer(readonly=True),
    'product_code': fields.String(required=True),
    'product_name': fields.String(required=True),
    'category_id': fields.Integer(),
    'brand_id': fields.Integer(),
    'description': fields.String(),
    'barcode': fields.String(),
    'unit_price': fields.Float(),
    'cost_price': fields.Float(),
    'reorder_level': fields.Integer(),
    'is_active': fields.Boolean(readonly=True),
    'created_at': fields.DateTime(readonly=True),
    'total_stock': fields.Integer(readonly=True)
})

product_create_model = products_ns.model('ProductCreate', {
    'product_code': fields.String(required=True),
    'product_name': fields.String(required=True),
    'category_id': fields.Integer(),
    'brand_id': fields.Integer(),
    'description': fields.String(),
    'barcode': fields.String(),
    'unit_price': fields.Float(required=True),
    'cost_price': fields.Float(),
    'reorder_level': fields.Integer(),
    'min_stock_level': fields.Integer(),
    'max_stock_level': fields.Integer(),
    'unit_of_measure': fields.String(),
    'sku': fields.String(),
    'weight': fields.Float(),
    'dimensions': fields.String()
})


@products_ns.route('')
class ProductList(Resource):
    @products_ns.doc('list_products')
    @jwt_required()
    @async_route
    async def get(self):
        """Get all products."""
        search_query = request.args.get('search')
        category_id = request.args.get('category_id', type=int)
        include_stock = request.args.get('include_stock', 'false').lower() == 'true'
        
        if search_query:
            products = await ProductService.search(search_query)
            data = []
            for p in products:
                stock = await ProductService.get_total_stock(p.product_id) if include_stock else 0
                data.append(p.to_dict(include_stock=include_stock, total_stock=stock))
            return api_response(data=data)

        elif category_id:
            products = await ProductService.get_by_category(category_id)
            data = []
            for p in products:
                stock = await ProductService.get_total_stock(p.product_id) if include_stock else 0
                data.append(p.to_dict(include_stock=include_stock, total_stock=stock))
            return api_response(data=data)

        else:
            if include_stock:
                results = await ProductService.get_all_with_stock()
                # results is list of (Product, total)
                return api_response(data=[p.to_dict(include_stock=True, total_stock=total) for p, total in results])
            else:
                products = await ProductService.get_all()
                return api_response(data=[p.to_dict() for p in products])

    @products_ns.expect(product_create_model)
    @products_ns.doc('create_product')
    @require_role('admin', 'manager')
    @async_route
    async def post(self):
        """Create a new product."""
        try:
            data = ProductCreate.model_validate(request.get_json())
        except Exception as e:
            return api_response(message=str(e), status_code=400)
        
        if await ProductService.get_by_code(data.product_code):
            return api_response(message='Product code already exists', status_code=400)
        
        product = await ProductService.create(**data.model_dump())
        return api_response(data=product.to_dict(), message='Product created', status_code=201)


@products_ns.route('/low-stock')
class LowStockProducts(Resource):
    @products_ns.doc('get_low_stock_products')
    @require_role('admin', 'manager')
    @async_route
    async def get(self):
        """Get products with low stock."""
        results = await ProductService.get_low_stock_products()
        # results is list of (Product, total)
        return api_response(data=[p.to_dict(include_stock=True, total_stock=total) for p, total in results])


@products_ns.route('/<int:product_id>')
class ProductDetail(Resource):
    @products_ns.doc('get_product')
    @jwt_required()
    @async_route
    async def get(self, product_id):
        """Get product by ID."""
        include_stock = request.args.get('include_stock', 'true').lower() == 'true'
        product = await ProductService.get_by_id(product_id)
        if not product:
            return api_response(message='Product not found', status_code=404)

        stock = 0
        if include_stock:
            stock = await ProductService.get_total_stock(product.product_id)

        return api_response(data=product.to_dict(include_stock=include_stock, total_stock=stock))

    @products_ns.doc('update_product')
    @require_role('admin', 'manager')
    @async_route
    async def put(self, product_id):
        """Update product."""
        product = await ProductService.get_by_id(product_id)
        if not product:
            return api_response(message='Product not found', status_code=404)
        
        data = request.get_json()
        product = await ProductService.update(product, **data)
        return api_response(data=product.to_dict(), message='Product updated')

    @products_ns.doc('delete_product')
    @require_role('admin')
    @async_route
    async def delete(self, product_id):
        """Delete product."""
        product = await ProductService.get_by_id(product_id)
        if not product:
            return api_response(message='Product not found', status_code=404)
        
        await ProductService.delete(product)
        return api_response(message='Product deleted')


@products_ns.route('/barcode/<barcode>')
class ProductByBarcode(Resource):
    @products_ns.doc('get_product_by_barcode')
    @jwt_required()
    @async_route
    async def get(self, barcode):
        """Get product by barcode."""
        product = await ProductService.get_by_barcode(barcode)
        if not product:
            return api_response(message='Product not found', status_code=404)

        stock = await ProductService.get_total_stock(product.product_id)
        return api_response(data=product.to_dict(include_stock=True, total_stock=stock))
