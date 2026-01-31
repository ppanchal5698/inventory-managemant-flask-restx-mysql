# Auth services

from typing import Optional, List
from app.extensions import db
from app.modules.auth.models import User


class AuthService:
    """Authentication and user management service."""

    @staticmethod
    def get_all_users(include_inactive: bool = False) -> List[User]:
        """Get all users."""
        if include_inactive:
            return User.query.all()
        return User.query.filter_by(is_active=True).all()

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID."""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username."""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email."""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def create_user(username: str, password: str, first_name: str, last_name: str,
                    email: str, phone: str = None, role: str = 'staff') -> User:
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
        db.session.commit()
        return user

    @staticmethod
    def update_user(user: User, **kwargs) -> User:
        """Update user attributes."""
        for key, value in kwargs.items():
            if hasattr(user, key) and key not in ['user_id', 'password_hash']:
                setattr(user, key, value)
        db.session.commit()
        return user

    @staticmethod
    def change_password(user: User, new_password: str) -> User:
        """Change user password."""
        user.set_password(new_password)
        db.session.commit()
        return user

    @staticmethod
    def deactivate_user(user: User) -> User:
        """Deactivate a user."""
        user.is_active = False
        db.session.commit()
        return user

    @staticmethod
    def activate_user(user: User) -> User:
        """Activate a user."""
        user.is_active = True
        db.session.commit()
        return user

    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        user = User.query.filter_by(username=username, is_active=True).first()
        if user and user.check_password(password):
            return user
        return None
