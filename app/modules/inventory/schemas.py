# Inventory schemas

from marshmallow import Schema, fields, validate


class InventoryTransactionSchema(Schema):
    """Inventory Transaction schema."""
    transaction_id = fields.Int(dump_only=True)
    transaction_type = fields.Str(required=True, validate=validate.OneOf([
        'purchase', 'sale', 'adjustment', 'transfer', 'return', 'damage'
    ]))
    product_id = fields.Int(required=True)
    warehouse_id = fields.Int(required=True)
    quantity = fields.Int(required=True)
    reference_type = fields.Str(validate=validate.Length(max=50))
    reference_id = fields.Int()
    transaction_date = fields.DateTime(dump_only=True)
    notes = fields.Str()
    performed_by = fields.Int(dump_only=True)


class InventoryTransactionCreateSchema(Schema):
    """Inventory Transaction creation schema."""
    transaction_type = fields.Str(required=True, validate=validate.OneOf([
        'purchase', 'sale', 'adjustment', 'transfer', 'return', 'damage'
    ]))
    product_id = fields.Int(required=True)
    warehouse_id = fields.Int(required=True)
    quantity = fields.Int(required=True)
    reference_type = fields.Str(validate=validate.Length(max=50))
    reference_id = fields.Int()
    notes = fields.Str()


class StockAdjustmentSchema(Schema):
    """Stock Adjustment schema."""
    adjustment_id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True)
    warehouse_id = fields.Int(required=True)
    old_quantity = fields.Int(dump_only=True, validate=validate.Range(min=0))
    new_quantity = fields.Int(required=True, validate=validate.Range(min=0))
    quantity_difference = fields.Int(dump_only=True)
    adjustment_quantity = fields.Int(dump_only=True)  # Alias for backward compatibility
    reason = fields.Str(required=True, validate=validate.OneOf([
        'physical_count', 'damage', 'theft', 'expired', 'correction', 'other'
    ]))
    notes = fields.Str()
    adjusted_by = fields.Int(dump_only=True)
    adjustment_date = fields.DateTime(dump_only=True)


class StockAdjustmentCreateSchema(Schema):
    """Stock Adjustment creation schema."""
    product_id = fields.Int(required=True)
    warehouse_id = fields.Int(required=True)
    new_quantity = fields.Int(required=True, validate=validate.Range(min=0))
    reason = fields.Str(required=True, validate=validate.OneOf([
        'physical_count', 'damage', 'theft', 'expired', 'correction', 'other'
    ]))
    notes = fields.Str()


transaction_schema = InventoryTransactionSchema()
transactions_schema = InventoryTransactionSchema(many=True)
transaction_create_schema = InventoryTransactionCreateSchema()

adjustment_schema = StockAdjustmentSchema()
adjustments_schema = StockAdjustmentSchema(many=True)
adjustment_create_schema = StockAdjustmentCreateSchema()
