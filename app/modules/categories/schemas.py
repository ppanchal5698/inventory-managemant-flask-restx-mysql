# Category schemas

from marshmallow import Schema, fields, validate


class CategorySchema(Schema):
    """Category serialization schema."""
    category_id = fields.Int(dump_only=True)
    category_name = fields.Str(required=True, validate=validate.Length(max=100))
    parent_category_id = fields.Int(allow_none=True)
    description = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    subcategories = fields.Nested('self', many=True, dump_only=True)


class CategoryCreateSchema(Schema):
    """Category creation schema."""
    category_name = fields.Str(required=True, validate=validate.Length(max=100))
    parent_category_id = fields.Int(allow_none=True)
    description = fields.Str()


category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
category_create_schema = CategoryCreateSchema()
