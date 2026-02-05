# Sales Order models

from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, Enum, Date, ForeignKey, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import Computed

from app.core.database import BaseModel

if TYPE_CHECKING:
    from app.modules.customers.models import Customer
    from app.modules.warehouses.models import Warehouse
    from app.modules.products.models import Product
    from app.modules.auth.models import User

class SalesOrder(BaseModel):
    """Sales Order model."""
    __tablename__ = 'sales_orders'

    order_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('customers.customer_id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('warehouses.warehouse_id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    expected_delivery_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_delivery_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Enum('pending', 'processing', 'shipped', 'delivered', 'cancelled',
                                name='so_status'), nullable=False, default='pending', index=True)
    total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    tax_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), default=0)
    shipping_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    payment_status: Mapped[str] = mapped_column(Enum('unpaid', 'partial', 'paid', name='payment_status'),
                                nullable=False, default='unpaid')
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('users.user_id', ondelete='SET NULL', onupdate='CASCADE'))

    # Relationships
    items: Mapped[List["SalesOrderItem"]] = relationship('SalesOrderItem', back_populates='sales_order',
                            cascade='all, delete-orphan')
    customer: Mapped["Customer"] = relationship('Customer', back_populates='sales_orders')
    warehouse: Mapped["Warehouse"] = relationship('Warehouse', back_populates='sales_orders')
    creator: Mapped[Optional["User"]] = relationship('User', back_populates='sales_orders')

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
            'total_amount': float(self.total_amount) if self.total_amount is not None else None,
            'tax_amount': float(self.tax_amount) if self.tax_amount is not None else None,
            'shipping_cost': float(self.shipping_cost) if self.shipping_cost is not None else None,
            'discount_amount': float(self.discount_amount) if self.discount_amount is not None else None,
            'payment_status': self.payment_status,
            'notes': self.notes,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        if include_customer and hasattr(self, 'customer') and self.customer:
            data['customer'] = self.customer.to_dict()
        return data

    def __repr__(self):
        return f'<SalesOrder {self.order_number}>'


class SalesOrderItem(BaseModel):
    """Sales Order Item model."""
    __tablename__ = 'sales_order_items'

    order_item_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('sales_orders.order_id', ondelete='CASCADE', onupdate='CASCADE'),
                         nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('products.product_id', ondelete='RESTRICT', onupdate='CASCADE'),
                           nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), Computed('((quantity * unit_price) - discount)'))

    # Relationships
    sales_order: Mapped["SalesOrder"] = relationship('SalesOrder', back_populates='items')
    product: Mapped["Product"] = relationship('Product', back_populates='sales_order_items')

    def to_dict(self):
        """Serialize item to dictionary."""
        return {
            'order_item_id': self.order_item_id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price is not None else None,
            'discount': float(self.discount) if self.discount is not None else None,
            'line_total': float(self.line_total) if self.line_total is not None else None,
        }

    def __repr__(self):
        return f'<SalesOrderItem order_id={self.order_id} product_id={self.product_id}>'
