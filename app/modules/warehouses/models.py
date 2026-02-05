# Warehouse model

from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Text, Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import BaseModel

if TYPE_CHECKING:
    from app.modules.stock.models import Stock
    from app.modules.purchase_orders.models import PurchaseOrder
    from app.modules.sales_orders.models import SalesOrder
    from app.modules.inventory.models import InventoryTransaction, StockAdjustment

class Warehouse(BaseModel):
    """Warehouse model."""
    __tablename__ = 'warehouses'

    warehouse_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    warehouse_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(50))
    state: Mapped[Optional[str]] = mapped_column(String(50))
    country: Mapped[Optional[str]] = mapped_column(String(50), default='USA')
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    manager_name: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    capacity: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    stock_entries: Mapped[List["Stock"]] = relationship('Stock', back_populates='warehouse')
    purchase_orders: Mapped[List["PurchaseOrder"]] = relationship('PurchaseOrder', back_populates='warehouse')
    sales_orders: Mapped[List["SalesOrder"]] = relationship('SalesOrder', back_populates='warehouse')

    # Inventory Module Relationships
    transactions: Mapped[List["InventoryTransaction"]] = relationship('InventoryTransaction', back_populates='warehouse')
    adjustments: Mapped[List["StockAdjustment"]] = relationship('StockAdjustment', back_populates='warehouse')

    def to_dict(self):
        """Serialize warehouse to dictionary."""
        return {
            'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse_name,
            'location': self.location,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'manager_name': self.manager_name,
            'phone': self.phone,
            'capacity': self.capacity,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Warehouse {self.warehouse_name}>'
