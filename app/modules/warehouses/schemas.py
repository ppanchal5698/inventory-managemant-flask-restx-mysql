# Warehouse schemas

from marshmallow import Schema, fields, validate


class WarehouseSchema(Schema):
    """Warehouse serialization schema."""
    warehouse_id = fields.Int(dump_only=True)
    warehouse_name = fields.Str(required=True, validate=validate.Length(max=100))
    location = fields.Str(validate=validate.Length(max=200))
    address = fields.Str()
    city = fields.Str(validate=validate.Length(max=50))
    state = fields.Str(validate=validate.Length(max=50))
    country = fields.Str(validate=validate.Length(max=50))
    postal_code = fields.Str(validate=validate.Length(max=20))
    manager_name = fields.Str(validate=validate.Length(max=100))
    phone = fields.Str(validate=validate.Length(max=20))
    capacity = fields.Int()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)


class WarehouseCreateSchema(Schema):
    """Warehouse creation schema."""
    warehouse_name = fields.Str(required=True, validate=validate.Length(max=100))
    location = fields.Str(validate=validate.Length(max=200))
    address = fields.Str()
    city = fields.Str(validate=validate.Length(max=50))
    state = fields.Str(validate=validate.Length(max=50))
    country = fields.Str(validate=validate.Length(max=50))
    postal_code = fields.Str(validate=validate.Length(max=20))
    manager_name = fields.Str(validate=validate.Length(max=100))
    phone = fields.Str(validate=validate.Length(max=20))
    capacity = fields.Int()


warehouse_schema = WarehouseSchema()
warehouses_schema = WarehouseSchema(many=True)
warehouse_create_schema = WarehouseCreateSchema()
