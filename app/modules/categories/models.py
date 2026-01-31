# Category model

from app.core.database import BaseModel
from app.extensions import db


class Category(BaseModel):
    """Product category model with hierarchical support."""
    __tablename__ = 'categories'

    category_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(100), nullable=False, index=True)
    parent_category_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('categories.category_id', ondelete='SET NULL', onupdate='CASCADE'))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Self-referential relationship for hierarchy
    parent = db.relationship('Category', remote_side=[category_id], backref='subcategories')

    # Products in this category
    products = db.relationship('Product', backref='category', lazy='dynamic')

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
            data['subcategories'] = [c.to_dict() for c in self.subcategories]
        return data

    def __repr__(self):
        return f'<Category {self.category_name}>'
