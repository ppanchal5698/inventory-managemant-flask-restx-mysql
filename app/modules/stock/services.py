# Stock services

from typing import Optional, List
from datetime import datetime
from app.extensions import db
from app.modules.stock.models import Stock


class StockService:
    """Stock management service."""

    @staticmethod
    def get_all() -> List[Stock]:
        """Get all stock entries."""
        return Stock.query.all()

    @staticmethod
    def get_by_id(stock_id: int) -> Optional[Stock]:
        """Get stock by ID."""
        return Stock.query.get(stock_id)

    @staticmethod
    def get_by_product_and_warehouse(product_id: int, warehouse_id: int) -> Optional[Stock]:
        """Get stock entry for a product in a specific warehouse."""
        return Stock.query.filter_by(
            product_id=product_id, 
            warehouse_id=warehouse_id
        ).first()

    @staticmethod
    def get_by_product(product_id: int) -> List[Stock]:
        """Get all stock entries for a product."""
        return Stock.query.filter_by(product_id=product_id).all()

    @staticmethod
    def get_by_warehouse(warehouse_id: int) -> List[Stock]:
        """Get all stock entries for a warehouse."""
        return Stock.query.filter_by(warehouse_id=warehouse_id).all()

    @staticmethod
    def create(product_id: int, warehouse_id: int, quantity_on_hand: int = 0, 
               quantity_reserved: int = 0) -> Stock:
        """Create a new stock entry."""
        stock = Stock(
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity_on_hand=quantity_on_hand,
            quantity_reserved=quantity_reserved
        )
        db.session.add(stock)
        db.session.commit()
        return stock

    @staticmethod
    def update(stock: Stock, **kwargs) -> Stock:
        """Update stock entry."""
        for key, value in kwargs.items():
            if hasattr(stock, key) and key != 'stock_id':
                setattr(stock, key, value)
        db.session.commit()
        return stock

    @staticmethod
    def adjust_quantity(stock: Stock, adjustment: int) -> Stock:
        """Adjust quantity on hand by a value (positive or negative)."""
        stock.quantity_on_hand += adjustment
        if stock.quantity_on_hand < 0:
            stock.quantity_on_hand = 0
        db.session.commit()
        return stock

    @staticmethod
    def reserve_stock(stock: Stock, quantity: int) -> bool:
        """Reserve stock for an order."""
        if stock.quantity_available >= quantity:
            stock.quantity_reserved += quantity
            db.session.commit()
            return True
        return False

    @staticmethod
    def release_reservation(stock: Stock, quantity: int) -> Stock:
        """Release reserved stock."""
        stock.quantity_reserved = max(0, stock.quantity_reserved - quantity)
        db.session.commit()
        return stock

    @staticmethod
    def record_stock_check(stock: Stock) -> Stock:
        """Record a stock check timestamp."""
        stock.last_stock_check = datetime.utcnow()
        db.session.commit()
        return stock

    @staticmethod
    def get_or_create(product_id: int, warehouse_id: int) -> Stock:
        """Get existing stock entry or create a new one."""
        stock = StockService.get_by_product_and_warehouse(product_id, warehouse_id)
        if not stock:
            stock = StockService.create(product_id, warehouse_id)
        return stock
