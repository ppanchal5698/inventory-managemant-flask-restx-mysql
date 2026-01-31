# Product schemas

from marshmallow import Schema, fields, validate


class ProductSchema(Schema):
    """Product serialization schema."""
    product_id = fields.Int(dump_only=True)
    product_code = fields.Str(required=True, validate=validate.Length(max=50))
    product_name = fields.Str(required=True, validate=validate.Length(max=200))
    description = fields.Str()
    category_id = fields.Int(allow_none=True)
    brand_id = fields.Int(allow_none=True)
    unit_price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    cost_price = fields.Decimal(places=2, allow_none=True, validate=validate.Range(min=0))
    reorder_level = fields.Int(load_default=10, validate=validate.Range(min=0))
    min_stock_level = fields.Int(load_default=5, validate=validate.Range(min=0))
    max_stock_level = fields.Int(allow_none=True, validate=validate.Range(min=0))
    unit_of_measure = fields.Str(load_default='pcs', validate=validate.Length(max=20))
    barcode = fields.Str(validate=validate.Length(max=100), allow_none=True)
    sku = fields.Str(validate=validate.Length(max=100), allow_none=True)
    weight = fields.Decimal(places=3, allow_none=True, validate=validate.Range(min=0))
    dimensions = fields.Str(validate=validate.Length(max=50), allow_none=True)
    is_active = fields.Bool()
    total_stock = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ProductCreateSchema(Schema):
    """Product creation schema."""
    product_code = fields.Str(required=True, validate=validate.Length(max=50))
    product_name = fields.Str(required=True, validate=validate.Length(max=200))
    description = fields.Str()
    category_id = fields.Int(allow_none=True)
    brand_id = fields.Int(allow_none=True)
    unit_price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    cost_price = fields.Decimal(places=2, allow_none=True, validate=validate.Range(min=0))
    reorder_level = fields.Int(load_default=10, validate=validate.Range(min=0))
    min_stock_level = fields.Int(load_default=5, validate=validate.Range(min=0))
    max_stock_level = fields.Int(allow_none=True, validate=validate.Range(min=0))
    unit_of_measure = fields.Str(load_default='pcs')
    barcode = fields.Str(validate=validate.Length(max=100), allow_none=True)
    sku = fields.Str(validate=validate.Length(max=100), allow_none=True)
    weight = fields.Decimal(places=3, allow_none=True, validate=validate.Range(min=0))
    dimensions = fields.Str(validate=validate.Length(max=50), allow_none=True)


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
product_create_schema = ProductCreateSchema()
