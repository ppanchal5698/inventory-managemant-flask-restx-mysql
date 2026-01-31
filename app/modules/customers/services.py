# Customer services

from typing import Optional, List
from app.extensions import db, cache
from app.modules.customers.models import Customer
from app.core.cache import CacheKeyPrefixes

CACHE_PREFIX = CacheKeyPrefixes.CUSTOMERS
CACHE_TIMEOUT = 300  # 5 minutes


class CustomerService:
    """Customer management service."""

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_all(include_inactive: bool = False) -> List[Customer]:
        """Get all customers."""
        query = Customer.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(Customer.customer_name).all()

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_by_id(customer_id: int) -> Optional[Customer]:
        """Get customer by ID."""
        return Customer.query.get(customer_id)

    @staticmethod
    def search(query: str) -> List[Customer]:
        """Search customers by name or email (not cached due to dynamic query)."""
        return Customer.query.filter(
            db.or_(
                Customer.customer_name.ilike(f'%{query}%'),
                Customer.email.ilike(f'%{query}%')
            ),
            Customer.is_active == True
        ).all()

    @staticmethod
    def create(**kwargs) -> Customer:
        """Create a new customer."""
        customer = Customer(**kwargs)
        db.session.add(customer)
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(CustomerService.get_all)
        return customer

    @staticmethod
    def update(customer: Customer, **kwargs) -> Customer:
        """Update customer."""
        for key, value in kwargs.items():
            if hasattr(customer, key) and key != 'customer_id':
                setattr(customer, key, value)
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(CustomerService.get_all)
        cache.delete_memoized(CustomerService.get_by_id, customer.customer_id)
        return customer

    @staticmethod
    def delete(customer: Customer) -> None:
        """Soft delete customer."""
        customer.is_active = False
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(CustomerService.get_all)
        cache.delete_memoized(CustomerService.get_by_id, customer.customer_id)
