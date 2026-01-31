# Sales Order schemas

from marshmallow import Schema, fields, validate


class SalesOrderItemSchema(Schema):
    """Sales Order Item schema."""
    order_item_id = fields.Int(dump_only=True)
    order_id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    unit_price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    discount = fields.Decimal(load_default=0, places=2, validate=validate.Range(min=0))
    line_total = fields.Float(dump_only=True)


class SalesOrderSchema(Schema):
    """Sales Order schema."""
    order_id = fields.Int(dump_only=True)
    order_number = fields.Str(required=True, validate=validate.Length(max=50))
    customer_id = fields.Int(required=True)
    warehouse_id = fields.Int(required=True)
    order_date = fields.Date(required=True)
    expected_delivery_date = fields.Date(allow_none=True)
    actual_delivery_date = fields.Date(allow_none=True, dump_only=True)
    status = fields.Str(validate=validate.OneOf(['pending', 'processing', 'shipped', 'delivered', 'cancelled']))
    total_amount = fields.Decimal(places=2, dump_only=True)
    tax_amount = fields.Decimal(places=2, load_default=0)
    shipping_cost = fields.Decimal(places=2, load_default=0)
    discount_amount = fields.Decimal(places=2, load_default=0, validate=validate.Range(min=0))
    payment_status = fields.Str(validate=validate.OneOf(['unpaid', 'partial', 'paid']))
    notes = fields.Str()
    created_by = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    items = fields.Nested(SalesOrderItemSchema, many=True)
    customer = fields.Dict(dump_only=True)


class SalesOrderCreateSchema(Schema):
    """Sales Order creation schema."""
    order_number = fields.Str(required=True, validate=validate.Length(max=50))
    customer_id = fields.Int(required=True)
    warehouse_id = fields.Int(required=True)
    order_date = fields.Date(required=True)
    expected_delivery_date = fields.Date(allow_none=True)
    tax_amount = fields.Decimal(places=2, load_default=0)
    shipping_cost = fields.Decimal(places=2, load_default=0)
    discount_amount = fields.Decimal(places=2, load_default=0, validate=validate.Range(min=0))
    notes = fields.Str()
    items = fields.Nested(SalesOrderItemSchema, many=True)


sales_order_schema = SalesOrderSchema()
sales_orders_schema = SalesOrderSchema(many=True)
sales_order_create_schema = SalesOrderCreateSchema()
so_item_schema = SalesOrderItemSchema()
