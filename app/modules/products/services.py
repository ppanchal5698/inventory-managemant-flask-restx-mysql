# Product services (Async)

from typing import Optional, List, Tuple
from sqlalchemy import select, or_, func, desc
from app.extensions import db
from app.modules.products.models import Product
# Import Stock model locally to avoid circular imports?
# Or assume Stock is available.
# We need Stock for stock calculation.
from app.modules.stock.models import Stock
from app.core.cache import CacheKeyPrefixes, invalidate_cache, cached_list, cached_item

CACHE_PREFIX = CacheKeyPrefixes.PRODUCTS
CACHE_TIMEOUT = 300  # 5 minutes


class ProductService:
    """Product management service."""

    @staticmethod
    @cached_list(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_all(include_inactive: bool = False) -> List[Product]:
        """Get all products."""
        stmt = select(Product).order_by(Product.product_name)
        if not include_inactive:
            stmt = stmt.filter_by(is_active=True)
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    @cached_item(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_by_id(product_id: int) -> Optional[Product]:
        """Get product by ID."""
        return await db.session.get(Product, product_id)

    @staticmethod
    @cached_item(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_by_code(product_code: str) -> Optional[Product]:
        """Get product by code."""
        stmt = select(Product).filter_by(product_code=product_code)
        result = await db.session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    @cached_item(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_by_barcode(barcode: str) -> Optional[Product]:
        """Get product by barcode."""
        stmt = select(Product).filter_by(barcode=barcode)
        result = await db.session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def search(query: str) -> List[Product]:
        """Search products by name or code."""
        stmt = select(Product).filter(
            or_(
                Product.product_name.ilike(f'%{query}%'),
                Product.product_code.ilike(f'%{query}%')
            ),
            Product.is_active == True
        )
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    @cached_list(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_by_category(category_id: int) -> List[Product]:
        """Get products by category."""
        stmt = select(Product).filter_by(category_id=category_id, is_active=True)
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_total_stock(product_id: int) -> int:
        """Calculate total stock for a product."""
        stmt = select(func.sum(Stock.quantity_on_hand)).filter_by(product_id=product_id)
        result = await db.session.execute(stmt)
        total = result.scalar()
        return total or 0

    @staticmethod
    async def get_all_with_stock(include_inactive: bool = False) -> List[Tuple[Product, int]]:
        """Get all products with their total stock."""
        stmt = select(Product, func.coalesce(func.sum(Stock.quantity_on_hand), 0).label('total')) \
            .outerjoin(Stock) \
            .group_by(Product.product_id) \
            .order_by(Product.product_name)

        if not include_inactive:
            stmt = stmt.filter(Product.is_active == True)

        result = await db.session.execute(stmt)
        return result.all()

    @staticmethod
    async def get_low_stock_products() -> List[Tuple[Product, int]]:
        """Get products with low stock. Returns list of (Product, current_stock)."""
        # Optimized query
        stmt = select(Product, func.coalesce(func.sum(Stock.quantity_on_hand), 0).label('total')) \
            .outerjoin(Stock) \
            .filter(Product.is_active == True) \
            .group_by(Product.product_id) \
            .having(func.coalesce(func.sum(Stock.quantity_on_hand), 0) <= Product.reorder_level)

        result = await db.session.execute(stmt)
        return result.all() # returns rows of (Product, total)

    @staticmethod
    async def create(**kwargs) -> Product:
        """Create a new product."""
        product = Product(**kwargs)
        db.session.add(product)
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX)
        if product.category_id:
            # We can't easily invalidate "get_by_category" without known args?
            # invalidate_cache deletes "list" keys. get_by_category is "list".
            pass
        return product

    @staticmethod
    async def update(product: Product, **kwargs) -> Product:
        """Update product."""
        # Invalidate specific cache keys
        await invalidate_cache(CACHE_PREFIX, product.product_id)

        for key, value in kwargs.items():
            if hasattr(product, key) and key != 'product_id':
                setattr(product, key, value)
        await db.session.commit()

        # Invalidate list caches
        await invalidate_cache(CACHE_PREFIX)
        return product

    @staticmethod
    async def delete(product: Product) -> None:
        """Soft delete product."""
        product.is_active = False
        await db.session.commit()
        await invalidate_cache(CACHE_PREFIX, product.product_id)
        await invalidate_cache(CACHE_PREFIX)
