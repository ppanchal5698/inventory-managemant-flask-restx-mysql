# Purchase Order schemas

from marshmallow import Schema, fields, validate


class PurchaseOrderItemSchema(Schema):
    """Purchase Order Item schema."""
    po_item_id = fields.Int(dump_only=True)
    po_id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    unit_price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    received_quantity = fields.Int(load_default=0, validate=validate.Range(min=0))
    line_total = fields.Float(dump_only=True)


class PurchaseOrderSchema(Schema):
    """Purchase Order schema."""
    po_id = fields.Int(dump_only=True)
    po_number = fields.Str(required=True, validate=validate.Length(max=50))
    supplier_id = fields.Int(required=True)
    warehouse_id = fields.Int(required=True)
    order_date = fields.Date(required=True)
    expected_delivery_date = fields.Date(allow_none=True)
    actual_delivery_date = fields.Date(allow_none=True, dump_only=True)
    status = fields.Str(validate=validate.OneOf(['draft', 'pending', 'approved', 'received', 'cancelled']))
    total_amount = fields.Decimal(places=2, dump_only=True, validate=validate.Range(min=0))
    tax_amount = fields.Decimal(places=2, load_default=0, validate=validate.Range(min=0))
    shipping_cost = fields.Decimal(places=2, load_default=0, validate=validate.Range(min=0))
    notes = fields.Str()
    created_by = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    items = fields.Nested(PurchaseOrderItemSchema, many=True)


class PurchaseOrderCreateSchema(Schema):
    """Purchase Order creation schema."""
    po_number = fields.Str(required=True, validate=validate.Length(max=50))
    supplier_id = fields.Int(required=True)
    warehouse_id = fields.Int(required=True)
    order_date = fields.Date(required=True)
    expected_delivery_date = fields.Date(allow_none=True)
    tax_amount = fields.Decimal(places=2, load_default=0, validate=validate.Range(min=0))
    shipping_cost = fields.Decimal(places=2, load_default=0, validate=validate.Range(min=0))
    notes = fields.Str()
    items = fields.Nested(PurchaseOrderItemSchema, many=True)


purchase_order_schema = PurchaseOrderSchema()
purchase_orders_schema = PurchaseOrderSchema(many=True)
purchase_order_create_schema = PurchaseOrderCreateSchema()
po_item_schema = PurchaseOrderItemSchema()
