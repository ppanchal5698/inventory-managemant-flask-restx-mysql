# Supplier services

from typing import Optional, List
from app.extensions import db, cache
from app.modules.suppliers.models import Supplier
from app.core.cache import CacheKeyPrefixes

CACHE_PREFIX = CacheKeyPrefixes.SUPPLIERS
CACHE_TIMEOUT = 300  # 5 minutes


class SupplierService:
    """Supplier management service."""

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_all(include_inactive: bool = False) -> List[Supplier]:
        """Get all suppliers."""
        query = Supplier.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(Supplier.supplier_name).all()

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_by_id(supplier_id: int) -> Optional[Supplier]:
        """Get supplier by ID."""
        return Supplier.query.get(supplier_id)

    @staticmethod
    def search(query: str) -> List[Supplier]:
        """Search suppliers by name (not cached due to dynamic query)."""
        return Supplier.query.filter(
            Supplier.supplier_name.ilike(f'%{query}%'),
            Supplier.is_active == True
        ).all()

    @staticmethod
    def create(**kwargs) -> Supplier:
        """Create a new supplier."""
        supplier = Supplier(**kwargs)
        db.session.add(supplier)
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(SupplierService.get_all)
        return supplier

    @staticmethod
    def update(supplier: Supplier, **kwargs) -> Supplier:
        """Update supplier."""
        for key, value in kwargs.items():
            if hasattr(supplier, key) and key != 'supplier_id':
                setattr(supplier, key, value)
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(SupplierService.get_all)
        cache.delete_memoized(SupplierService.get_by_id, supplier.supplier_id)
        return supplier

    @staticmethod
    def delete(supplier: Supplier) -> None:
        """Soft delete supplier."""
        supplier.is_active = False
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(SupplierService.get_all)
        cache.delete_memoized(SupplierService.get_by_id, supplier.supplier_id)
