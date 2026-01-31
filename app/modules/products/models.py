# Product model

from app.core.database import BaseModel
from app.extensions import db


class Product(BaseModel):
    """Product model."""
    __tablename__ = 'products'

    product_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    product_code = db.Column(db.String(50), unique=True, nullable=False)
    product_name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    category_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('categories.category_id', ondelete='SET NULL', onupdate='CASCADE'))
    brand_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('brands.brand_id', ondelete='SET NULL', onupdate='CASCADE'))
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    cost_price = db.Column(db.Numeric(12, 2))
    reorder_level = db.Column(db.Integer, nullable=False, default=10)
    min_stock_level = db.Column(db.Integer, nullable=False, default=5)
    max_stock_level = db.Column(db.Integer)
    unit_of_measure = db.Column(db.String(20), nullable=False, default='pcs')
    barcode = db.Column(db.String(100), unique=True)
    sku = db.Column(db.String(100), unique=True)
    weight = db.Column(db.Numeric(10, 3))
    dimensions = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    stock_entries = db.relationship('Stock', backref='product', lazy='dynamic')
    purchase_order_items = db.relationship('PurchaseOrderItem', backref='product', lazy='dynamic')
    sales_order_items = db.relationship('SalesOrderItem', backref='product', lazy='dynamic')

    @property
    def total_stock(self):
        """Calculate total stock across all warehouses."""
        from app.modules.stock.models import Stock
        result = db.session.query(db.func.sum(Stock.quantity_on_hand)).filter(
            Stock.product_id == self.product_id
        ).scalar()
        return result or 0

    def to_dict(self, include_stock=False):
        """Serialize product to dictionary."""
        data = {
            'product_id': self.product_id,
            'product_code': self.product_code,
            'product_name': self.product_name,
            'description': self.description,
            'category_id': self.category_id,
            'brand_id': self.brand_id,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'cost_price': float(self.cost_price) if self.cost_price else None,
            'reorder_level': self.reorder_level,
            'min_stock_level': self.min_stock_level,
            'max_stock_level': self.max_stock_level,
            'unit_of_measure': self.unit_of_measure,
            'barcode': self.barcode,
            'sku': self.sku,
            'weight': float(self.weight) if self.weight else None,
            'dimensions': self.dimensions,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_stock:
            data['total_stock'] = self.total_stock
        return data

    def __repr__(self):
        return f'<Product {self.product_code}>'
