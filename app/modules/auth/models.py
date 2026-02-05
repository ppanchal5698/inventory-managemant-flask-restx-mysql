# User model

from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Enum, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.core.database import BaseModel
# Note: we don't import db from extensions to avoid circular imports if possible,
# but BaseModel uses it.

if TYPE_CHECKING:
    from app.modules.purchase_orders.models import PurchaseOrder
    from app.modules.sales_orders.models import SalesOrder

class User(BaseModel):
    """User model for authentication and authorization."""
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    role: Mapped[str] = mapped_column(Enum('admin', 'manager', 'staff', 'viewer', name='user_role'),
                     nullable=False, default='staff')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    # Replaced lazy='dynamic' with standard relationship.
    # Use service methods for filtering.
    purchase_orders: Mapped[List["PurchaseOrder"]] = relationship(
        'PurchaseOrder',
        back_populates='creator',
        foreign_keys='PurchaseOrder.created_by'
    )
    sales_orders: Mapped[List["SalesOrder"]] = relationship(
        'SalesOrder',
        back_populates='creator',
        foreign_keys='SalesOrder.created_by'
    )

    @property
    def full_name(self) -> str:
        """Return full name."""
        return f"{self.first_name} {self.last_name}"

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        """Serialize user to dictionary."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<User {self.username}>'
