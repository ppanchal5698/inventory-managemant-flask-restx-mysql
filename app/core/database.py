# Database utilities and base model

from datetime import datetime

from app.extensions import db


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


class CRUDMixin:
    """Mixin for common CRUD operations."""

    def save(self):
        """Save the current instance."""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Delete the current instance."""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        """Get instance by primary key."""
        return cls.query.get(id)

    @classmethod
    def get_all(cls):
        """Get all instances."""
        return cls.query.all()

    @classmethod
    def get_active(cls):
        """Get all active instances (requires is_active column)."""
        if hasattr(cls, 'is_active'):
            return cls.query.filter_by(is_active=True).all()
        return cls.get_all()


class BaseModel(db.Model, TimestampMixin, CRUDMixin):
    """Abstract base model with timestamps and CRUD operations."""
    __abstract__ = True
