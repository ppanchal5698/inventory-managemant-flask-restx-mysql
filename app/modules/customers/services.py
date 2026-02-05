# Customer services (Async)

from typing import Optional, List
from sqlalchemy import select
from app.extensions import db
from app.modules.customers.models import Customer
from app.core.cache import CacheKeyPrefixes, invalidate_cache, cached_list, cached_item

CACHE_PREFIX = CacheKeyPrefixes.CUSTOMERS
CACHE_TIMEOUT = 300  # 5 minutes


class CustomerService:
    """Customer management service."""

    @staticmethod
    @cached_list(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_all(include_inactive: bool = False) -> List[Customer]:
        """Get all customers."""
        stmt = select(Customer).order_by(Customer.customer_name)
        if not include_inactive:
            stmt = stmt.filter_by(is_active=True)
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    @cached_item(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_by_id(customer_id: int) -> Optional[Customer]:
        """Get customer by ID."""
        return await db.session.get(Customer, customer_id)

    @staticmethod
    async def search(query: str) -> List[Customer]:
        """Search customers by name."""
        stmt = select(Customer).filter(
            Customer.customer_name.ilike(f'%{query}%'),
            Customer.is_active == True
        )
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create(**kwargs) -> Customer:
        """Create a new customer."""
        customer = Customer(**kwargs)
        db.session.add(customer)
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX)
        return customer

    @staticmethod
    async def update(customer: Customer, **kwargs) -> Customer:
        """Update customer."""
        for key, value in kwargs.items():
            if hasattr(customer, key) and key != 'customer_id':
                setattr(customer, key, value)
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX, customer.customer_id)
        await invalidate_cache(CACHE_PREFIX)
        return customer

    @staticmethod
    async def delete(customer: Customer) -> None:
        """Soft delete customer."""
        customer.is_active = False
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX, customer.customer_id)
        await invalidate_cache(CACHE_PREFIX)
