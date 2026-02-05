# Customer model

from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import String, Boolean, Text, BigInteger, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import BaseModel

if TYPE_CHECKING:
    from app.modules.sales_orders.models import SalesOrder

class Customer(BaseModel):
    """Customer model."""
    __tablename__ = 'customers'

    customer_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    customer_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    contact_person: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(50))
    state: Mapped[Optional[str]] = mapped_column(String(50))
    country: Mapped[Optional[str]] = mapped_column(String(50), default='USA')
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    tax_id: Mapped[Optional[str]] = mapped_column(String(50))
    credit_limit: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    sales_orders: Mapped[List["SalesOrder"]] = relationship('SalesOrder', back_populates='customer')

    def to_dict(self):
        """Serialize customer to dictionary."""
        return {
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'tax_id': self.tax_id,
            'credit_limit': float(self.credit_limit) if self.credit_limit is not None else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Customer {self.customer_name}>'
