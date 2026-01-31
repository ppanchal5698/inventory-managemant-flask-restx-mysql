# Category services

from typing import Optional, List
from app.extensions import db, cache
from app.modules.categories.models import Category
from app.core.cache import CacheKeyPrefixes, invalidate_cache

CACHE_PREFIX = CacheKeyPrefixes.CATEGORIES
CACHE_TIMEOUT = 300  # 5 minutes


class CategoryService:
    """Category management service."""

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_all(include_inactive: bool = False) -> List[Category]:
        """Get all categories."""
        query = Category.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.all()

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_root_categories() -> List[Category]:
        """Get all root categories (no parent)."""
        return Category.query.filter_by(parent_category_id=None, is_active=True).all()

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_by_id(category_id: int) -> Optional[Category]:
        """Get category by ID."""
        return Category.query.get(category_id)

    @staticmethod
    def create(category_name: str, parent_category_id: int = None, 
               description: str = None) -> Category:
        """Create a new category."""
        category = Category(
            category_name=category_name,
            parent_category_id=parent_category_id,
            description=description
        )
        db.session.add(category)
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(CategoryService.get_all)
        cache.delete_memoized(CategoryService.get_root_categories)
        return category

    @staticmethod
    def update(category: Category, **kwargs) -> Category:
        """Update category."""
        for key, value in kwargs.items():
            if hasattr(category, key) and key != 'category_id':
                setattr(category, key, value)
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(CategoryService.get_all)
        cache.delete_memoized(CategoryService.get_root_categories)
        cache.delete_memoized(CategoryService.get_by_id, category.category_id)
        cache.delete_memoized(CategoryService.get_subcategories, category.parent_category_id)
        return category

    @staticmethod
    def delete(category: Category) -> None:
        """Soft delete category."""
        category.is_active = False
        db.session.commit()
        # Invalidate cache
        cache.delete_memoized(CategoryService.get_all)
        cache.delete_memoized(CategoryService.get_root_categories)
        cache.delete_memoized(CategoryService.get_by_id, category.category_id)

    @staticmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_subcategories(category_id: int) -> List[Category]:
        """Get subcategories of a category."""
        return Category.query.filter_by(parent_category_id=category_id, is_active=True).all()
