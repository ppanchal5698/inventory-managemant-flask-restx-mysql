# Inventory Transaction and Stock Adjustment models

from datetime import datetime

from app.extensions import db


class InventoryTransaction(db.Model):
    """Inventory Transaction model - tracks all inventory movements."""
    __tablename__ = 'inventory_transactions'

    transaction_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    transaction_type = db.Column(db.Enum('purchase', 'sale', 'adjustment', 'transfer',
                                          'return', 'damage', name='transaction_type'),
                                  nullable=False, index=True)
    product_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('products.product_id', ondelete='RESTRICT', onupdate='CASCADE'),
                           nullable=False, index=True)
    warehouse_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('warehouses.warehouse_id', ondelete='RESTRICT', onupdate='CASCADE'),
                              nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    reference_type = db.Column(db.String(50))  # 'purchase_order', 'sales_order', etc.
    reference_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"))  # ID of the related document
    transaction_date = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp(), index=True)
    notes = db.Column(db.Text)
    performed_by = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('users.user_id', ondelete='SET NULL', onupdate='CASCADE'))

    # Relationships
    product = db.relationship('Product', backref='transactions')
    warehouse = db.relationship('Warehouse', backref='transactions')
    user = db.relationship('User', backref='inventory_transactions')

    def to_dict(self):
        """Serialize transaction to dictionary."""
        return {
            'transaction_id': self.transaction_id,
            'transaction_type': self.transaction_type,
            'product_id': self.product_id,
            'warehouse_id': self.warehouse_id,
            'quantity': self.quantity,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'notes': self.notes,
            'performed_by': self.performed_by,
        }

    def __repr__(self):
        return f'<InventoryTransaction {self.transaction_id} {self.transaction_type}>'


class StockAdjustment(db.Model):
    """Stock Adjustment model - tracks stock corrections."""
    __tablename__ = 'stock_adjustments'

    adjustment_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    product_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('products.product_id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    warehouse_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('warehouses.warehouse_id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    old_quantity = db.Column(db.Integer, nullable=False)
    new_quantity = db.Column(db.Integer, nullable=False)
    quantity_difference = db.Column(db.Integer, db.Computed('(new_quantity - old_quantity)'))
    reason = db.Column(db.Enum('physical_count', 'damage', 'theft', 'expired',
                                'correction', 'other', name='adjustment_reason'), nullable=False)
    notes = db.Column(db.Text)
    adjusted_by = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('users.user_id', ondelete='SET NULL', onupdate='CASCADE'))
    adjustment_date = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp(), index=True)

    # Relationships
    product = db.relationship('Product', backref='adjustments')
    warehouse = db.relationship('Warehouse', backref='adjustments')
    user = db.relationship('User', backref='stock_adjustments')

    def to_dict(self):
        """Serialize adjustment to dictionary."""
        return {
            'adjustment_id': self.adjustment_id,
            'product_id': self.product_id,
            'warehouse_id': self.warehouse_id,
            'old_quantity': self.old_quantity,
            'new_quantity': self.new_quantity,
            'quantity_difference': self.quantity_difference,
            'adjustment_quantity': self.quantity_difference,  # Alias for backward compatibility
            'reason': self.reason,
            'notes': self.notes,
            'adjusted_by': self.adjusted_by,
            'adjustment_date': self.adjustment_date.isoformat() if self.adjustment_date else None,
        }

    def __repr__(self):
        return f'<StockAdjustment {self.adjustment_id}>'
