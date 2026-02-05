# Supplier model

from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Text, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import BaseModel

if TYPE_CHECKING:
    from app.modules.purchase_orders.models import PurchaseOrder

class Supplier(BaseModel):
    """Supplier model."""
    __tablename__ = 'suppliers'

    supplier_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    supplier_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    contact_person: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(50))
    state: Mapped[Optional[str]] = mapped_column(String(50))
    country: Mapped[Optional[str]] = mapped_column(String(50), default='USA')
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    tax_id: Mapped[Optional[str]] = mapped_column(String(50))
    payment_terms: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    # Note: PurchaseOrder model needs 'supplier' relationship defined with back_populates='purchase_orders' if we change backref here.
    # For now, I will use backref='supplier' in relationship() syntax to keep compatibility with existing PurchaseOrder model if it doesn't define 'supplier'.
    # Actually, legacy backref works in 2.0.
    # But better to be explicit.
    # I will patch PurchaseOrder model to add 'supplier' relationship.
    purchase_orders: Mapped[List["PurchaseOrder"]] = relationship('PurchaseOrder', back_populates='supplier')

    def to_dict(self):
        """Serialize supplier to dictionary."""
        return {
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier_name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'tax_id': self.tax_id,
            'payment_terms': self.payment_terms,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Supplier {self.supplier_name}>'
