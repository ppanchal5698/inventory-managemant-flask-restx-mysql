# Warehouse services

from typing import Optional, List
from app.extensions import db, cache
from app.modules.warehouses.models import Warehouse
from app.core.cache import CacheKeyPrefixes

CACHE_PREFIX = CacheKeyPrefixes.WAREHOUSES
CACHE_TIMEOUT = 300  # 5 minutes


class WarehouseService:
    """Warehouse management service."""

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_all(include_inactive: bool = False) -> List[Warehouse]:
        """Get all warehouses."""
        query = Warehouse.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(Warehouse.warehouse_name).all()

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_by_id(warehouse_id: int) -> Optional[Warehouse]:
        """Get warehouse by ID."""
        return Warehouse.query.get(warehouse_id)

    @staticmethod
    def create(**kwargs) -> Warehouse:
        """Create a new warehouse."""
        warehouse = Warehouse(**kwargs)
        db.session.add(warehouse)
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(WarehouseService.get_all)
        return warehouse

    @staticmethod
    def update(warehouse: Warehouse, **kwargs) -> Warehouse:
        """Update warehouse."""
        for key, value in kwargs.items():
            if hasattr(warehouse, key) and key != 'warehouse_id':
                setattr(warehouse, key, value)
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(WarehouseService.get_all)
        cache.delete_memoized(WarehouseService.get_by_id, warehouse.warehouse_id)
        return warehouse

    @staticmethod
    def delete(warehouse: Warehouse) -> None:
        """Soft delete warehouse."""
        warehouse.is_active = False
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(WarehouseService.get_all)
        cache.delete_memoized(WarehouseService.get_by_id, warehouse.warehouse_id)
