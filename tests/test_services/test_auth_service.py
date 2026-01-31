# Auth service tests

import pytest
from app.modules.auth.services import AuthService
from app.modules.auth.models import User


class TestAuthService:
    """Tests for AuthService."""

    def test_create_user(self, app, db_session):
        """Test user creation via service."""
        with app.app_context():
            user = AuthService.create_user(
                username='serviceuser',
                password='password123',
                first_name='Service',
                last_name='User',
                email='service@example.com',
                role='staff'
            )
            
            assert user.user_id is not None
            assert user.username == 'serviceuser'
            assert user.check_password('password123')

    def test_authenticate_success(self, app, db_session):
        """Test successful authentication."""
        with app.app_context():
            AuthService.create_user(
                username='authuser',
                password='mypassword',
                first_name='Auth',
                last_name='User',
                email='auth@example.com'
            )
            
            user = AuthService.authenticate('authuser', 'mypassword')
            assert user is not None
            assert user.username == 'authuser'

    def test_authenticate_wrong_password(self, app, db_session):
        """Test authentication with wrong password."""
        with app.app_context():
            AuthService.create_user(
                username='wrongpass',
                password='correct',
                first_name='Wrong',
                last_name='Pass',
                email='wrongpass@example.com'
            )
            
            user = AuthService.authenticate('wrongpass', 'incorrect')
            assert user is None

    def test_authenticate_nonexistent_user(self, app, db_session):
        """Test authentication with non-existent user."""
        with app.app_context():
            user = AuthService.authenticate('nonexistent', 'password')
            assert user is None

    def test_authenticate_inactive_user(self, app, db_session):
        """Test authentication with inactive user."""
        with app.app_context():
            user = AuthService.create_user(
                username='inactiveuser',
                password='password',
                first_name='Inactive',
                last_name='User',
                email='inactive@example.com'
            )
            AuthService.deactivate_user(user)
            
            result = AuthService.authenticate('inactiveuser', 'password')
            assert result is None

    def test_get_user_by_id(self, test_user, app):
        """Test getting user by ID."""
        with app.app_context():
            user = AuthService.get_user_by_id(test_user.user_id)
            assert user is not None
            assert user.username == 'testuser'

    def test_get_user_by_username(self, test_user, app):
        """Test getting user by username."""
        with app.app_context():
            user = AuthService.get_user_by_username('testuser')
            assert user is not None
            assert user.email == 'test@example.com'

    def test_get_user_by_email(self, test_user, app):
        """Test getting user by email."""
        with app.app_context():
            user = AuthService.get_user_by_email('test@example.com')
            assert user is not None
            assert user.username == 'testuser'

    def test_update_user(self, test_user, app, db_session):
        """Test updating user."""
        with app.app_context():
            updated = AuthService.update_user(
                test_user,
                first_name='Updated',
                phone='555-1234'
            )
            
            assert updated.first_name == 'Updated'
            assert updated.phone == '555-1234'

    def test_change_password(self, test_user, app, db_session):
        """Test changing password."""
        with app.app_context():
            AuthService.change_password(test_user, 'newpassword123')
            
            assert test_user.check_password('newpassword123')
            assert not test_user.check_password('testpass123')

    def test_deactivate_activate_user(self, app, db_session):
        """Test deactivating and activating user."""
        with app.app_context():
            user = AuthService.create_user(
                username='toggleuser',
                password='password',
                first_name='Toggle',
                last_name='User',
                email='toggle@example.com'
            )
            
            AuthService.deactivate_user(user)
            assert user.is_active is False
            
            AuthService.activate_user(user)
            assert user.is_active is True

    def test_get_all_users(self, app, db_session):
        """Test getting all users."""
        with app.app_context():
            AuthService.create_user('user1', 'pass', 'One', 'User', 'one@example.com')
            AuthService.create_user('user2', 'pass', 'Two', 'User', 'two@example.com')
            user3 = AuthService.create_user('user3', 'pass', 'Three', 'User', 'three@example.com')
            AuthService.deactivate_user(user3)
            
            active_users = AuthService.get_all_users()
            all_users = AuthService.get_all_users(include_inactive=True)
            
            assert len(active_users) == 2
            assert len(all_users) == 3
