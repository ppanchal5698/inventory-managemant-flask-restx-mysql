# Brand model

from app.core.database import BaseModel
from app.extensions import db


class Brand(BaseModel):
    """Brand model."""
    __tablename__ = 'brands'

    brand_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    brand_name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    manufacturer_name = db.Column(db.String(150))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    products = db.relationship('Product', backref='brand', lazy='dynamic')

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
