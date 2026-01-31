# Brand schemas

from marshmallow import Schema, fields, validate


class BrandSchema(Schema):
    """Brand serialization schema."""
    brand_id = fields.Int(dump_only=True)
    brand_name = fields.Str(required=True, validate=validate.Length(max=100))
    manufacturer_name = fields.Str(validate=validate.Length(max=150))
    description = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)


class BrandCreateSchema(Schema):
    """Brand creation schema."""
    brand_name = fields.Str(required=True, validate=validate.Length(max=100))
    manufacturer_name = fields.Str(validate=validate.Length(max=150))
    description = fields.Str()


brand_schema = BrandSchema()
brands_schema = BrandSchema(many=True)
brand_create_schema = BrandCreateSchema()
