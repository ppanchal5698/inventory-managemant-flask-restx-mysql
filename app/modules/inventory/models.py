# Inventory Transaction and Stock Adjustment models

from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, Text, Enum, ForeignKey, DateTime, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import Computed

from app.core.database import BaseModel

if TYPE_CHECKING:
    from app.modules.products.models import Product
    from app.modules.warehouses.models import Warehouse
    from app.modules.auth.models import User

class InventoryTransaction(BaseModel):
    """Inventory Transaction model - tracks all inventory movements."""
    __tablename__ = 'inventory_transactions'

    transaction_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    transaction_type: Mapped[str] = mapped_column(Enum('purchase', 'sale', 'adjustment', 'transfer',
                                          'return', 'damage', name='transaction_type'),
                                  nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('products.product_id', ondelete='RESTRICT', onupdate='CASCADE'),
                           nullable=False, index=True)
    warehouse_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('warehouses.warehouse_id', ondelete='RESTRICT', onupdate='CASCADE'),
                              nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_type: Mapped[Optional[str]] = mapped_column(String(50))  # 'purchase_order', 'sales_order', etc.
    reference_id: Mapped[Optional[int]] = mapped_column(BigInteger().with_variant(Integer, "sqlite"))  # ID of the related document
    transaction_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    performed_by: Mapped[Optional[int]] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('users.user_id', ondelete='SET NULL', onupdate='CASCADE'))

    # Relationships
    product: Mapped["Product"] = relationship('Product', backref='transactions')
    warehouse: Mapped["Warehouse"] = relationship('Warehouse', back_populates='transactions')
    user: Mapped[Optional["User"]] = relationship('User', backref='inventory_transactions')

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


class StockAdjustment(BaseModel):
    """Stock Adjustment model - tracks stock corrections."""
    __tablename__ = 'stock_adjustments'

    adjustment_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('products.product_id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('warehouses.warehouse_id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    old_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    new_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    # Computed columns can be tricky in some DBs, but standard SA syntax usually works.
    # Note: SQLite supports generated columns in newer versions.
    quantity_difference: Mapped[int] = mapped_column(Integer, Computed('(new_quantity - old_quantity)'))
    reason: Mapped[str] = mapped_column(Enum('physical_count', 'damage', 'theft', 'expired',
                                'correction', 'other', name='adjustment_reason'), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    adjusted_by: Mapped[Optional[int]] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('users.user_id', ondelete='SET NULL', onupdate='CASCADE'))
    adjustment_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), index=True)

    # Relationships
    product: Mapped["Product"] = relationship('Product', backref='adjustments')
    warehouse: Mapped["Warehouse"] = relationship('Warehouse', back_populates='adjustments')
    user: Mapped[Optional["User"]] = relationship('User', backref='stock_adjustments')

    def to_dict(self):
        """Serialize adjustment to dictionary."""
        return {
            'adjustment_id': self.adjustment_id,
            'product_id': self.product_id,
            'warehouse_id': self.warehouse_id,
            'old_quantity': self.old_quantity,
            'new_quantity': self.new_quantity,
            'quantity_difference': self.quantity_difference,
            'adjustment_quantity': self.quantity_difference,
            'reason': self.reason,
            'notes': self.notes,
            'adjusted_by': self.adjusted_by,
            'adjustment_date': self.adjustment_date.isoformat() if self.adjustment_date else None,
        }

    def __repr__(self):
        return f'<StockAdjustment {self.adjustment_id}>'
