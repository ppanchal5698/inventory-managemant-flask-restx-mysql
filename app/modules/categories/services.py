# Category services (Async)

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.modules.categories.models import Category
from app.core.cache import CacheKeyPrefixes, invalidate_cache, cached_list, cached_item

CACHE_PREFIX = CacheKeyPrefixes.CATEGORIES
CACHE_TIMEOUT = 300  # 5 minutes


class CategoryService:
    """Category management service."""

    @staticmethod
    @cached_list(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_all(include_inactive: bool = False) -> List[Category]:
        """Get all categories."""
        stmt = select(Category)
        if not include_inactive:
            stmt = stmt.filter_by(is_active=True)
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    @cached_list(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_root_categories() -> List[Category]:
        """Get all root categories (no parent)."""
        stmt = select(Category).filter_by(parent_category_id=None, is_active=True)
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    @cached_item(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_by_id(category_id: int, load_children: bool = False) -> Optional[Category]:
        """Get category by ID."""
        if load_children:
            stmt = select(Category).options(selectinload(Category.subcategories)).filter_by(category_id=category_id)
            result = await db.session.execute(stmt)
            return result.scalar_one_or_none()
        return await db.session.get(Category, category_id)

    @staticmethod
    async def create(**kwargs) -> Category:
        """Create a new category."""
        # Ensure we don't pass unexpected args if model doesn't support them,
        # but Category model should support is_active.
        category = Category(**kwargs)
        db.session.add(category)
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX)
        return category

    @staticmethod
    async def update(category: Category, **kwargs) -> Category:
        """Update category."""
        for key, value in kwargs.items():
            if hasattr(category, key) and key != 'category_id':
                setattr(category, key, value)
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX, category.category_id)
        return category

    @staticmethod
    async def delete(category: Category) -> None:
        """Soft delete category."""
        category.is_active = False
        await db.session.commit()
        # Invalidate cache
        await invalidate_cache(CACHE_PREFIX, category.category_id)

    @staticmethod
    @cached_list(CACHE_PREFIX, timeout=CACHE_TIMEOUT)
    async def get_subcategories(category_id: int) -> List[Category]:
        """Get subcategories of a category."""
        stmt = select(Category).filter_by(parent_category_id=category_id, is_active=True)
        result = await db.session.execute(stmt)
        return result.scalars().all()
