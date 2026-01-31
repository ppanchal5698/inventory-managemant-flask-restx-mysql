# Stock schemas

from marshmallow import Schema, fields, validate


class StockSchema(Schema):
    """Stock serialization schema."""
    stock_id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True)
    warehouse_id = fields.Int(required=True)
    quantity_on_hand = fields.Int(required=True)
    quantity_reserved = fields.Int(load_default=0)
    quantity_available = fields.Int(dump_only=True)
    last_stock_check = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    product = fields.Nested('ProductSchema', dump_only=True)
    warehouse = fields.Nested('WarehouseSchema', dump_only=True)


class StockCreateSchema(Schema):
    """Stock creation schema."""
    product_id = fields.Int(required=True)
    warehouse_id = fields.Int(required=True)
    quantity_on_hand = fields.Int(required=True, validate=validate.Range(min=0))
    quantity_reserved = fields.Int(load_default=0, validate=validate.Range(min=0))


class StockUpdateSchema(Schema):
    """Stock update schema."""
    quantity_on_hand = fields.Int(validate=validate.Range(min=0))
    quantity_reserved = fields.Int(validate=validate.Range(min=0))


stock_schema = StockSchema()
stocks_schema = StockSchema(many=True)
stock_create_schema = StockCreateSchema()
stock_update_schema = StockUpdateSchema()
