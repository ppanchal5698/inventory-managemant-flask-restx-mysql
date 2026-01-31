# User model tests

import pytest
from app.modules.auth.models import User


class TestUserModel:
    """Tests for User model."""

    def test_create_user(self, app, db_session):
        """Test user creation."""
        with app.app_context():
            user = User(
                username='newuser',
                first_name='New',
                last_name='User',
                email='new@example.com',
                role='staff'
            )
            user.set_password('password123')
            db_session.add(user)
            db_session.commit()
            
            assert user.user_id is not None
            assert user.username == 'newuser'
            assert user.is_active is True

    def test_password_hashing(self, app, db_session):
        """Test password hashing and verification."""
        with app.app_context():
            user = User(
                username='hashtest',
                first_name='Hash',
                last_name='Test',
                email='hash@example.com',
                role='staff'
            )
            user.set_password('mypassword')
            db_session.add(user)
            db_session.commit()
            
            # Password should be hashed
            assert user.password_hash != 'mypassword'
            # Check password should work
            assert user.check_password('mypassword') is True
            assert user.check_password('wrongpassword') is False

    def test_user_full_name(self, test_user, app):
        """Test full_name property."""
        with app.app_context():
            assert test_user.full_name == 'Test User'

    def test_user_to_dict(self, test_user, app):
        """Test user serialization."""
        with app.app_context():
            data = test_user.to_dict()
            
            assert 'user_id' in data
            assert data['username'] == 'testuser'
            assert data['email'] == 'test@example.com'
            assert 'password_hash' not in data  # Should not expose password

    def test_user_get_id(self, test_user, app):
        """Test get_id for Flask-Login."""
        with app.app_context():
            assert test_user.get_id() == str(test_user.user_id)

    def test_user_roles(self, app, db_session):
        """Test different user roles."""
        with app.app_context():
            for role in ['admin', 'manager', 'staff', 'viewer']:
                user = User(
                    username=f'{role}user',
                    first_name=role.capitalize(),
                    last_name='User',
                    email=f'{role}@example.com',
                    role=role
                )
                user.set_password('password')
                db_session.add(user)
            
            db_session.commit()
            
            admin = User.query.filter_by(username='adminuser').first()
            assert admin.role == 'admin'
