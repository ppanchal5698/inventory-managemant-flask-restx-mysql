# Sales Order models

from app.core.database import BaseModel
from app.extensions import db


class SalesOrder(BaseModel):
    """Sales Order model."""
    __tablename__ = 'sales_orders'

    order_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('customers.customer_id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    warehouse_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('warehouses.warehouse_id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    order_date = db.Column(db.Date, nullable=False, index=True)
    expected_delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.Date)
    status = db.Column(db.Enum('pending', 'processing', 'shipped', 'delivered', 'cancelled',
                                name='so_status'), nullable=False, default='pending', index=True)
    total_amount = db.Column(db.Numeric(12, 2))
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    shipping_cost = db.Column(db.Numeric(10, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    payment_status = db.Column(db.Enum('unpaid', 'partial', 'paid', name='payment_status'),
                                nullable=False, default='unpaid')
    notes = db.Column(db.Text)
    created_by = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('users.user_id', ondelete='SET NULL', onupdate='CASCADE'))

    # Relationships
    items = db.relationship('SalesOrderItem', backref='sales_order',
                            lazy='dynamic', cascade='all, delete-orphan')

    def calculate_total(self):
        """Calculate total amount from items."""
        subtotal = float(sum(item.line_total or 0 for item in self.items))
        tax = float(self.tax_amount or 0)
        shipping = float(self.shipping_cost or 0)
        discount = float(self.discount_amount or 0)
        self.total_amount = subtotal + tax + shipping - discount
        return self.total_amount

    def to_dict(self, include_items=False, include_customer=False):
        """Serialize sales order to dictionary."""
        data = {
            'order_id': self.order_id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'warehouse_id': self.warehouse_id,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'status': self.status,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'tax_amount': float(self.tax_amount) if self.tax_amount else None,
            'shipping_cost': float(self.shipping_cost) if self.shipping_cost else None,
            'discount_amount': float(self.discount_amount) if self.discount_amount else None,
            'payment_status': self.payment_status,
            'notes': self.notes,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        if include_customer and self.customer:
            data['customer'] = self.customer.to_dict()
        return data

    def __repr__(self):
        return f'<SalesOrder {self.order_number}>'


class SalesOrderItem(db.Model):
    """Sales Order Item model."""
    __tablename__ = 'sales_order_items'

    order_item_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    order_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('sales_orders.order_id', ondelete='CASCADE', onupdate='CASCADE'),
                         nullable=False, index=True)
    product_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('products.product_id', ondelete='RESTRICT', onupdate='CASCADE'),
                           nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    discount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    line_total = db.Column(db.Numeric(12, 2), db.Computed('((quantity * unit_price) - discount)'))

    def to_dict(self):
        """Serialize item to dictionary."""
        return {
            'order_item_id': self.order_item_id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'discount': float(self.discount) if self.discount else None,
            'line_total': float(self.line_total) if self.line_total else None,
        }

    def __repr__(self):
        return f'<SalesOrderItem order_id={self.order_id} product_id={self.product_id}>'
