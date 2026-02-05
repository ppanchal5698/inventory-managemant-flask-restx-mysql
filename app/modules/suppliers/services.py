# Supplier services (Async)

from typing import Optional, List
from sqlalchemy import select
from app.extensions import db
from app.modules.suppliers.models import Supplier
from app.core.cache import CacheKeyPrefixes, invalidate_cache, cached_list, cached_item

CACHE_PREFIX = CacheKeyPrefixes.SUPPLIERS
CACHE_TIMEOUT = 300  # 5 minutes


class SupplierService:
    """Supplier management service."""

    @staticmethod
    @cached_list(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_all(include_inactive: bool = False) -> List[Supplier]:
        """Get all suppliers."""
        stmt = select(Supplier).order_by(Supplier.supplier_name)
        if not include_inactive:
            stmt = stmt.filter_by(is_active=True)
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    @cached_item(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_by_id(supplier_id: int) -> Optional[Supplier]:
        """Get supplier by ID."""
        return await db.session.get(Supplier, supplier_id)

    @staticmethod
    async def search(query: str) -> List[Supplier]:
        """Search suppliers by name."""
        stmt = select(Supplier).filter(
            Supplier.supplier_name.ilike(f'%{query}%'),
            Supplier.is_active == True
        )
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create(**kwargs) -> Supplier:
        """Create a new supplier."""
        supplier = Supplier(**kwargs)
        db.session.add(supplier)
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX)
        return supplier

    @staticmethod
    async def update(supplier: Supplier, **kwargs) -> Supplier:
        """Update supplier."""
        for key, value in kwargs.items():
            if hasattr(supplier, key) and key != 'supplier_id':
                setattr(supplier, key, value)
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX, supplier.supplier_id)
        await invalidate_cache(CACHE_PREFIX)
        return supplier

    @staticmethod
    async def delete(supplier: Supplier) -> None:
        """Soft delete supplier."""
        supplier.is_active = False
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX, supplier.supplier_id)
        await invalidate_cache(CACHE_PREFIX)
