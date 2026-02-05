# Brand model

from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Text, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import BaseModel

if TYPE_CHECKING:
    from app.modules.products.models import Product

class Brand(BaseModel):
    """Brand model."""
    __tablename__ = 'brands'

    brand_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    brand_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    manufacturer_name: Mapped[Optional[str]] = mapped_column(String(150))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    products: Mapped[List["Product"]] = relationship('Product', back_populates='brand')

    def to_dict(self):
        """Serialize brand to dictionary."""
        return {
            'brand_id': self.brand_id,
            'brand_name': self.brand_name,
            'manufacturer_name': self.manufacturer_name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Brand {self.brand_name}>'
