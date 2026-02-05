# Category model

from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Text, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import BaseModel

if TYPE_CHECKING:
    from app.modules.products.models import Product

class Category(BaseModel):
    """Product category model with hierarchical support."""
    __tablename__ = 'categories'

    category_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    parent_category_id: Mapped[Optional[int]] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('categories.category_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Self-referential relationship for hierarchy
    parent: Mapped[Optional["Category"]] = relationship('Category', remote_side=[category_id], back_populates='subcategories')
    subcategories: Mapped[List["Category"]] = relationship('Category', back_populates='parent')

    # Products in this category
    products: Mapped[List["Product"]] = relationship('Product', back_populates='category')

    def to_dict(self, include_children=False):
        """Serialize category to dictionary."""
        data = {
            'category_id': self.category_id,
            'category_name': self.category_name,
            'parent_category_id': self.parent_category_id,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_children:
            # Requires loading subcategories.
            # In async, we must ensure they are loaded.
            # If not loaded, this might fail or raise error.
            # But normally we control loading in service.
            data['subcategories'] = [c.to_dict() for c in self.subcategories]
        return data

    def __repr__(self):
        return f'<Category {self.category_name}>'
