# Warehouse model

from app.core.database import BaseModel
from app.extensions import db


class Warehouse(BaseModel):
    """Warehouse model."""
    __tablename__ = 'warehouses'

    warehouse_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    warehouse_name = db.Column(db.String(100), nullable=False, index=True)
    location = db.Column(db.String(200))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50), default='USA')
    postal_code = db.Column(db.String(20))
    manager_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    capacity = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    stock_entries = db.relationship('Stock', backref='warehouse', lazy='dynamic')
    purchase_orders = db.relationship('PurchaseOrder', backref='warehouse', lazy='dynamic')
    sales_orders = db.relationship('SalesOrder', backref='warehouse', lazy='dynamic')

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
