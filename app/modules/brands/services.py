# Brand services (Async)

from typing import Optional, List
from sqlalchemy import select
from app.extensions import db
from app.modules.brands.models import Brand
from app.core.cache import CacheKeyPrefixes, invalidate_cache, cached_list, cached_item

CACHE_PREFIX = CacheKeyPrefixes.BRANDS
CACHE_TIMEOUT = 300  # 5 minutes


class BrandService:
    """Brand management service."""

    @staticmethod
    @cached_list(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_all(include_inactive: bool = False) -> List[Brand]:
        """Get all brands."""
        stmt = select(Brand).order_by(Brand.brand_name)
        if not include_inactive:
            stmt = stmt.filter_by(is_active=True)
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    @cached_item(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_by_id(brand_id: int) -> Optional[Brand]:
        """Get brand by ID."""
        return await db.session.get(Brand, brand_id)

    @staticmethod
    async def get_by_name(brand_name: str) -> Optional[Brand]:
        """Get brand by name."""
        stmt = select(Brand).filter_by(brand_name=brand_name)
        result = await db.session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(**kwargs) -> Brand:
        """Create a new brand."""
        brand = Brand(**kwargs)
        db.session.add(brand)
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX)
        return brand

    @staticmethod
    async def update(brand: Brand, **kwargs) -> Brand:
        """Update brand."""
        # old_name = brand.brand_name
        for key, value in kwargs.items():
            if hasattr(brand, key) and key != 'brand_id':
                setattr(brand, key, value)
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX, brand.brand_id)
        return brand

    @staticmethod
    async def delete(brand: Brand) -> None:
        """Soft delete brand."""
        brand.is_active = False
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX, brand.brand_id)
