# Database utilities and base model

from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )


class CRUDMixin:
    """Mixin for common CRUD operations (Async)."""

    async def save(self):
        """Save the current instance."""
        db.session.add(self)
        await db.session.commit()
        return self

    async def delete(self):
        """Delete the current instance."""
        await db.session.delete(self)
        await db.session.commit()

    @classmethod
    async def get_by_id(cls, id):
        """Get instance by primary key."""
        return await db.session.get(cls, id)

    @classmethod
    async def get_all(cls):
        """Get all instances."""
        result = await db.session.execute(select(cls))
        return result.scalars().all()

    @classmethod
    async def get_active(cls):
        """Get all active instances (requires is_active column)."""
        if hasattr(cls, 'is_active'):
            result = await db.session.execute(select(cls).filter_by(is_active=True))
            return result.scalars().all()
        return await cls.get_all()


class BaseModel(AsyncAttrs, db.Model, TimestampMixin, CRUDMixin):
    """Abstract base model with timestamps, AsyncAttrs, and CRUD operations."""
    __abstract__ = True
