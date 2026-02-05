# Auth services (Async)

from typing import Optional, List
from sqlalchemy import select, or_
from app.extensions import db
from app.modules.auth.models import User


class AuthService:
    """Authentication and user management service."""

    @staticmethod
    async def get_all_users(include_inactive: bool = False) -> List[User]:
        """Get all users."""
        stmt = select(User)
        if not include_inactive:
            stmt = stmt.filter_by(is_active=True)
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await db.session.get(User, user_id)

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username."""
        result = await db.session.execute(select(User).filter_by(username=username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.session.execute(select(User).filter_by(email=email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(username: str, password: str, first_name: str, last_name: str,
                    email: str, phone: Optional[str] = None, role: str = 'staff') -> User:
        """Create a new user."""
        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            role=role
        )
        user.set_password(password)
        db.session.add(user)
        await db.session.commit()
        return user

    @staticmethod
    async def update_user(user: User, **kwargs) -> User:
        """Update user attributes."""
        for key, value in kwargs.items():
            if hasattr(user, key) and key not in ['user_id', 'password_hash', 'created_at']:
                setattr(user, key, value)
        await db.session.commit()
        return user

    @staticmethod
    async def change_password(user: User, new_password: str) -> User:
        """Change user password."""
        user.set_password(new_password)
        await db.session.commit()
        return user

    @staticmethod
    async def deactivate_user(user: User) -> User:
        """Deactivate a user."""
        user.is_active = False
        await db.session.commit()
        return user

    @staticmethod
    async def activate_user(user: User) -> User:
        """Activate a user."""
        user.is_active = True
        await db.session.commit()
        return user

    @staticmethod
    async def authenticate(username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        result = await db.session.execute(select(User).filter_by(username=username, is_active=True))
        user = result.scalar_one_or_none()
        if user and user.check_password(password):
            return user
        return None
