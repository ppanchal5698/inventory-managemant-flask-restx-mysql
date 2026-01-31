# Brand services

from typing import Optional, List
from app.extensions import db, cache
from app.modules.brands.models import Brand
from app.core.cache import CacheKeyPrefixes

CACHE_PREFIX = CacheKeyPrefixes.BRANDS
CACHE_TIMEOUT = 300  # 5 minutes


class BrandService:
    """Brand management service."""

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_all(include_inactive: bool = False) -> List[Brand]:
        """Get all brands."""
        query = Brand.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(Brand.brand_name).all()

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_by_id(brand_id: int) -> Optional[Brand]:
        """Get brand by ID."""
        return Brand.query.get(brand_id)

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_by_name(brand_name: str) -> Optional[Brand]:
        """Get brand by name."""
        return Brand.query.filter_by(brand_name=brand_name).first()

    @staticmethod
    def create(**kwargs) -> Brand:
        """Create a new brand."""
        brand = Brand(**kwargs)
        db.session.add(brand)
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(BrandService.get_all)
        return brand

    @staticmethod
    def update(brand: Brand, **kwargs) -> Brand:
        """Update brand."""
        old_name = brand.brand_name
        for key, value in kwargs.items():
            if hasattr(brand, key) and key != 'brand_id':
                setattr(brand, key, value)
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(BrandService.get_all)
        cache.delete_memoized(BrandService.get_by_id, brand.brand_id)
        cache.delete_memoized(BrandService.get_by_name, old_name)
        cache.delete_memoized(BrandService.get_by_name, brand.brand_name)
        return brand

    @staticmethod
    def delete(brand: Brand) -> None:
        """Soft delete brand."""
        brand.is_active = False
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(BrandService.get_all)
        cache.delete_memoized(BrandService.get_by_id, brand.brand_id)
        cache.delete_memoized(BrandService.get_by_name, brand.brand_name)
