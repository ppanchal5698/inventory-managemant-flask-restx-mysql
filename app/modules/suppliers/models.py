# Supplier model

from app.core.database import BaseModel
from app.extensions import db


class Supplier(BaseModel):
    """Supplier model."""
    __tablename__ = 'suppliers'

    supplier_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    supplier_name = db.Column(db.String(150), nullable=False, index=True)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50), default='USA')
    postal_code = db.Column(db.String(20))
    tax_id = db.Column(db.String(50))
    payment_terms = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy='dynamic')

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
