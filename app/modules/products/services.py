# Product services

from typing import Optional, List
from app.extensions import db, cache
from app.modules.products.models import Product
from app.core.cache import CacheKeyPrefixes

CACHE_PREFIX = CacheKeyPrefixes.PRODUCTS
CACHE_TIMEOUT = 300  # 5 minutes


class ProductService:
    """Product management service."""

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_all(include_inactive: bool = False) -> List[Product]:
        """Get all products."""
        query = Product.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(Product.product_name).all()

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_by_id(product_id: int) -> Optional[Product]:
        """Get product by ID."""
        return Product.query.get(product_id)

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_by_code(product_code: str) -> Optional[Product]:
        """Get product by code."""
        return Product.query.filter_by(product_code=product_code).first()

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_by_barcode(barcode: str) -> Optional[Product]:
        """Get product by barcode."""
        return Product.query.filter_by(barcode=barcode).first()

    @staticmethod
    def search(query: str) -> List[Product]:
        """Search products by name or code (not cached due to dynamic query)."""
        return Product.query.filter(
            db.or_(
                Product.product_name.ilike(f'%{query}%'),
                Product.product_code.ilike(f'%{query}%')
            ),
            Product.is_active == True
        ).all()

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_by_category(category_id: int) -> List[Product]:
        """Get products by category."""
        return Product.query.filter_by(category_id=category_id, is_active=True).all()

    @staticmethod
    def get_low_stock_products() -> List[Product]:
        """Get products with stock below reorder level (not cached - needs real-time data)."""
        products = Product.query.filter_by(is_active=True).all()
        return [p for p in products if p.total_stock <= p.reorder_level]

    @staticmethod
    def create(**kwargs) -> Product:
        """Create a new product."""
        product = Product(**kwargs)
        db.session.add(product)
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(ProductService.get_all)
        if product.category_id:
            cache.delete_memoized(ProductService.get_by_category, product.category_id)
        return product

    @staticmethod
    def update(product: Product, **kwargs) -> Product:
        """Update product."""
        old_category_id = product.category_id
        for key, value in kwargs.items():
            if hasattr(product, key) and key != 'product_id':
                setattr(product, key, value)
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(ProductService.get_all)
        cache.delete_memoized(ProductService.get_by_id, product.product_id)
        cache.delete_memoized(ProductService.get_by_code, product.product_code)
        if product.barcode:
            cache.delete_memoized(ProductService.get_by_barcode, product.barcode)
        if old_category_id:
            cache.delete_memoized(ProductService.get_by_category, old_category_id)
        if product.category_id:
            cache.delete_memoized(ProductService.get_by_category, product.category_id)
        return product

    @staticmethod
    def delete(product: Product) -> None:
        """Soft delete product."""
        product.is_active = False
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(ProductService.get_all)
        cache.delete_memoized(ProductService.get_by_id, product.product_id)
        cache.delete_memoized(ProductService.get_by_code, product.product_code)
        if product.category_id:
            cache.delete_memoized(ProductService.get_by_category, product.category_id)
