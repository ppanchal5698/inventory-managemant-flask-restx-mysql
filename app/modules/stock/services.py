# Stock services (Async)

from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.modules.stock.models import Stock
from app.core.cache import CacheKeyPrefixes, invalidate_cache, cached_list, cached_item

CACHE_PREFIX = CacheKeyPrefixes.STOCK
CACHE_TIMEOUT = 300


class StockService:
    """Stock management service."""

    @staticmethod
    @cached_list(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_all() -> List[Stock]:
        """Get all stock entries."""
        stmt = select(Stock)
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    @cached_item(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_by_id(stock_id: int) -> Optional[Stock]:
        """Get stock by ID."""
        return await db.session.get(Stock, stock_id)

    @staticmethod
    async def get_by_product_and_warehouse(product_id: int, warehouse_id: int) -> Optional[Stock]:
        """Get stock entry for a product in a specific warehouse."""
        stmt = select(Stock).filter_by(product_id=product_id, warehouse_id=warehouse_id)
        result = await db.session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    @cached_list(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_by_product(product_id: int) -> List[Stock]:
        """Get all stock entries for a product."""
        stmt = select(Stock).filter_by(product_id=product_id)
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    @cached_list(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_by_warehouse(warehouse_id: int) -> List[Stock]:
        """Get all stock entries for a warehouse."""
        stmt = select(Stock).filter_by(warehouse_id=warehouse_id)
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create(product_id: int, warehouse_id: int, quantity_on_hand: int = 0,
               quantity_reserved: int = 0) -> Stock:
        """Create a new stock entry."""
        stock = Stock(
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity_on_hand=quantity_on_hand,
            quantity_reserved=quantity_reserved
        )
        db.session.add(stock)
        await db.session.commit()
        await invalidate_cache(CACHE_PREFIX)
        return stock

    @staticmethod
    async def update(stock: Stock, **kwargs) -> Stock:
        """Update stock entry."""
        for key, value in kwargs.items():
            if hasattr(stock, key) and key != 'stock_id':
                setattr(stock, key, value)
        await db.session.commit()
        await invalidate_cache(CACHE_PREFIX, stock.stock_id)
        return stock

    @staticmethod
    async def adjust_quantity(stock: Stock, adjustment: int) -> Stock:
        """Adjust quantity on hand by a value (positive or negative)."""
        stock.quantity_on_hand += adjustment
        if stock.quantity_on_hand < 0:
            stock.quantity_on_hand = 0
        await db.session.commit()
        await invalidate_cache(CACHE_PREFIX, stock.stock_id)
        return stock

    @staticmethod
    async def record_stock_check(stock: Stock) -> Stock:
        """Record a stock check timestamp."""
        stock.last_stock_check = func.now()
        await db.session.commit()
        await invalidate_cache(CACHE_PREFIX, stock.stock_id)
        return stock
