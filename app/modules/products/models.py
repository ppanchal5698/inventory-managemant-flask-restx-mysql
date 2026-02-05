# Product model

from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import String, Boolean, Text, Integer, Numeric, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import BaseModel

if TYPE_CHECKING:
    from app.modules.categories.models import Category
    from app.modules.brands.models import Brand
    from app.modules.stock.models import Stock
    from app.modules.purchase_orders.models import PurchaseOrderItem
    from app.modules.sales_orders.models import SalesOrderItem

class Product(BaseModel):
    """Product model."""
    __tablename__ = 'products'

    product_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    product_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category_id: Mapped[Optional[int]] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('categories.category_id', ondelete='SET NULL', onupdate='CASCADE'))
    brand_id: Mapped[Optional[int]] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('brands.brand_id', ondelete='SET NULL', onupdate='CASCADE'))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cost_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    reorder_level: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    min_stock_level: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    max_stock_level: Mapped[Optional[int]] = mapped_column(Integer)
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=False, default='pcs')
    barcode: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    sku: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    dimensions: Mapped[Optional[str]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    category: Mapped[Optional["Category"]] = relationship('Category', back_populates='products')
    brand: Mapped[Optional["Brand"]] = relationship('Brand', back_populates='products')

    # We remove backref='product' from these and define explicit relationships
    stock_entries: Mapped[List["Stock"]] = relationship('Stock', back_populates='product')
    purchase_order_items: Mapped[List["PurchaseOrderItem"]] = relationship('PurchaseOrderItem', back_populates='product')
    sales_order_items: Mapped[List["SalesOrderItem"]] = relationship('SalesOrderItem', back_populates='product')

    def to_dict(self, include_stock=False, total_stock=0):
        """Serialize product to dictionary."""
        data = {
            'product_id': self.product_id,
            'product_code': self.product_code,
            'product_name': self.product_name,
            'description': self.description,
            'category_id': self.category_id,
            'brand_id': self.brand_id,
            'unit_price': float(self.unit_price) if self.unit_price is not None else None,
            'cost_price': float(self.cost_price) if self.cost_price is not None else None,
            'reorder_level': self.reorder_level,
            'min_stock_level': self.min_stock_level,
            'max_stock_level': self.max_stock_level,
            'unit_of_measure': self.unit_of_measure,
            'barcode': self.barcode,
            'sku': self.sku,
            'weight': float(self.weight) if self.weight is not None else None,
            'dimensions': self.dimensions,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_stock:
            data['total_stock'] = total_stock
        return data

    def __repr__(self):
        return f'<Product {self.product_code}>'
