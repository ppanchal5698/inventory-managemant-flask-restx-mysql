# Warehouse services (Async)

from typing import Optional, List
from sqlalchemy import select
from app.extensions import db
from app.modules.warehouses.models import Warehouse
from app.core.cache import CacheKeyPrefixes, invalidate_cache, cached_list, cached_item

CACHE_PREFIX = CacheKeyPrefixes.WAREHOUSES
CACHE_TIMEOUT = 300  # 5 minutes


class WarehouseService:
    """Warehouse management service."""

    @staticmethod
    @cached_list(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_all(include_inactive: bool = False) -> List[Warehouse]:
        """Get all warehouses."""
        stmt = select(Warehouse).order_by(Warehouse.warehouse_name)
        if not include_inactive:
            stmt = stmt.filter_by(is_active=True)
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    @cached_item(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_by_id(warehouse_id: int) -> Optional[Warehouse]:
        """Get warehouse by ID."""
        return await db.session.get(Warehouse, warehouse_id)

    @staticmethod
    async def create(**kwargs) -> Warehouse:
        """Create a new warehouse."""
        warehouse = Warehouse(**kwargs)
        db.session.add(warehouse)
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX)
        return warehouse

    @staticmethod
    async def update(warehouse: Warehouse, **kwargs) -> Warehouse:
        """Update warehouse."""
        for key, value in kwargs.items():
            if hasattr(warehouse, key) and key != 'warehouse_id':
                setattr(warehouse, key, value)
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX, warehouse.warehouse_id)
        await invalidate_cache(CACHE_PREFIX)
        return warehouse

    @staticmethod
    async def delete(warehouse: Warehouse) -> None:
        """Soft delete warehouse."""
        warehouse.is_active = False
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX, warehouse.warehouse_id)
        await invalidate_cache(CACHE_PREFIX)
