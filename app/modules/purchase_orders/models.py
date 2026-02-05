# Purchase Order models

from app.core.database import BaseModel
from app.extensions import db


class PurchaseOrder(BaseModel):
    """Purchase Order model."""
    __tablename__ = 'purchase_orders'

    po_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    po_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    supplier_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('suppliers.supplier_id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    warehouse_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('warehouses.warehouse_id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    expected_delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.Date)
    status = db.Column(db.Enum('draft', 'pending', 'approved', 'received', 'cancelled',
                                name='po_status'), nullable=False, default='draft', index=True)
    total_amount = db.Column(db.Numeric(12, 2))
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    shipping_cost = db.Column(db.Numeric(10, 2), default=0)
    notes = db.Column(db.Text)
    created_by = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('users.user_id', ondelete='SET NULL', onupdate='CASCADE'))

    # Relationships
    items = db.relationship('PurchaseOrderItem', backref='purchase_order',
                            cascade='all, delete-orphan')
    creator = db.relationship('User', back_populates='purchase_orders')
    supplier = db.relationship('Supplier', back_populates='purchase_orders')
    warehouse = db.relationship('Warehouse', back_populates='purchase_orders')

    def calculate_total(self):
        """Calculate total amount from items."""
        total = sum(item.line_total for item in self.items)
        self.total_amount = total
        return total

    def to_dict(self, include_items=False):
        """Serialize purchase order to dictionary."""
        data = {
            'po_id': self.po_id,
            'po_number': self.po_number,
            'supplier_id': self.supplier_id,
            'warehouse_id': self.warehouse_id,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'status': self.status,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'tax_amount': float(self.tax_amount) if self.tax_amount else None,
            'shipping_cost': float(self.shipping_cost) if self.shipping_cost else None,
            'notes': self.notes,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        return data

    def __repr__(self):
        return f'<PurchaseOrder {self.po_number}>'


class PurchaseOrderItem(db.Model):
    """Purchase Order Item model."""
    __tablename__ = 'purchase_order_items'

    po_item_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    po_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('purchase_orders.po_id', ondelete='CASCADE', onupdate='CASCADE'),
                      nullable=False, index=True)
    product_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('products.product_id', ondelete='RESTRICT', onupdate='CASCADE'),
                           nullable=False, index=True)
    product = db.relationship('Product', back_populates='purchase_order_items')
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    received_quantity = db.Column(db.Integer, nullable=False, default=0)
    line_total = db.Column(db.Numeric(12, 2), db.Computed('(quantity * unit_price)'))

    def to_dict(self):
        """Serialize item to dictionary."""
        return {
            'po_item_id': self.po_item_id,
            'po_id': self.po_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'received_quantity': self.received_quantity,
            'line_total': float(self.line_total) if self.line_total else None,
        }

    def __repr__(self):
        return f'<PurchaseOrderItem po_id={self.po_id} product_id={self.product_id}>'
