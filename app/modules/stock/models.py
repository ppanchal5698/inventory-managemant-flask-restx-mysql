# Stock model

from app.core.database import BaseModel
from app.extensions import db


class Stock(BaseModel):
    """Stock/Inventory model - tracks product quantities per warehouse."""
    __tablename__ = 'stock'

    stock_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    product_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('products.product_id', ondelete='CASCADE', onupdate='CASCADE'),
                           nullable=False, index=True)
    warehouse_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('warehouses.warehouse_id', ondelete='CASCADE', onupdate='CASCADE'),
                              nullable=False, index=True)
    quantity_on_hand = db.Column(db.Integer, nullable=False, default=0)
    quantity_reserved = db.Column(db.Integer, nullable=False, default=0)
    quantity_available = db.Column(db.Integer, db.Computed('(quantity_on_hand - quantity_reserved)'))
    last_stock_check = db.Column(db.DateTime)

    # Unique constraint for product-warehouse combination
    __table_args__ = (
        db.UniqueConstraint('product_id', 'warehouse_id', name='uk_product_warehouse'),
        db.Index('idx_warehouse_quantity', 'warehouse_id', 'quantity_on_hand'),
    )

    product = db.relationship('Product', back_populates='stock_entries')
    warehouse = db.relationship('Warehouse', back_populates='stock_entries')

    def to_dict(self, include_product=False, include_warehouse=False):
        """Serialize stock to dictionary."""
        data = {
            'stock_id': self.stock_id,
            'product_id': self.product_id,
            'warehouse_id': self.warehouse_id,
            'quantity_on_hand': self.quantity_on_hand,
            'quantity_reserved': self.quantity_reserved,
            'quantity_available': self.quantity_available,
            'last_stock_check': self.last_stock_check.isoformat() if self.last_stock_check else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_product and self.product:
            data['product'] = self.product.to_dict()
        if include_warehouse and self.warehouse:
            data['warehouse'] = self.warehouse.to_dict()
        return data

    def __repr__(self):
        return f'<Stock product_id={self.product_id} warehouse_id={self.warehouse_id}>'
