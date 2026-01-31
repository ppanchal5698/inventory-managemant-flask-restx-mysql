# Customer model

from app.core.database import BaseModel
from app.extensions import db


class Customer(BaseModel):
    """Customer model."""
    __tablename__ = 'customers'

    customer_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    customer_name = db.Column(db.String(150), nullable=False, index=True)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100), index=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50), default='USA')
    postal_code = db.Column(db.String(20))
    tax_id = db.Column(db.String(50))
    credit_limit = db.Column(db.Numeric(12, 2))
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    sales_orders = db.relationship('SalesOrder', backref='customer', lazy='dynamic')

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
            'credit_limit': float(self.credit_limit) if self.credit_limit else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Customer {self.customer_name}>'
