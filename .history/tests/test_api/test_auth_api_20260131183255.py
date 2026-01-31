# Auth API tests

import pytest


class TestAuthAPI:
    """Tests for auth API endpoints."""

    def test_login_success(self, client, test_user, app):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['username'] == 'testuser'

    def test_login_wrong_password(self, client, test_user, app):
        """Test login with wrong password."""
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False

    def test_login_nonexistent_user(self, client, app):
        """Test login with non-existent user."""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'password'
        })

        assert response.status_code == 401

    def test_login_missing_credentials(self, client, app):
        """Test login with missing credentials."""
        response = client.post('/api/auth/login', json={})
        assert response.status_code == 400

    def test_logout(self, auth_client, app):
        """Test logout."""
        response = auth_client.post('/api/auth/logout')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_get_current_user(self, auth_client, app):
        """Test getting current user info."""
        response = auth_client.get('/api/auth/me')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['username'] == 'testuser'
        assert data['data']['role'] == 'admin'

    def test_get_current_user_unauthorized(self, client, app):
        """Test getting current user without login."""
        response = client.get('/api/auth/me')

        assert response.status_code == 401


class TestUserManagementAPI:
    """Tests for user management endpoints."""

    def test_list_users(self, auth_client, app):
        """Test listing users (admin only)."""
        response = auth_client.get('/api/auth/users')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)
        assert len(data['data']) >= 1

    def test_create_user(self, auth_client, app):
        """Test creating a new user."""
        response = auth_client.post('/api/auth/users', json={
            'username': 'newuser',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'role': 'staff'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['username'] == 'newuser'
        assert data['data']['role'] == 'staff'

    def test_create_user_duplicate_username(self, auth_client, test_user, app):
        """Test creating user with duplicate username."""
        response = auth_client.post('/api/auth/users', json={
            'username': 'testuser',  # Already exists
            'password': 'password',
            'first_name': 'Duplicate',
            'last_name': 'User',
            'email': 'duplicate@example.com',
            'role': 'staff'
        })

        assert response.status_code == 400

    def test_create_user_duplicate_email(self, auth_client, test_user, app):
        """Test creating user with duplicate email."""
        response = auth_client.post('/api/auth/users', json={
            'username': 'anotheruser',
            'password': 'password',
            'first_name': 'Another',
            'last_name': 'User',
            'email': 'test@example.com',  # Already exists
            'role': 'staff'
        })

        assert response.status_code == 400

    def test_create_user_missing_required(self, auth_client, app):
        """Test creating user with missing required fields."""
        response = auth_client.post('/api/auth/users', json={
            'username': 'incomplete'
            # Missing password and email
        })

        assert response.status_code == 400

    def test_get_user_by_id(self, auth_client, test_user, app):
        """Test getting user by ID."""
        response = auth_client.get(f'/api/auth/users/{test_user.user_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['username'] == 'testuser'

    def test_get_user_nonexistent(self, auth_client, app):
        """Test getting non-existent user."""
        response = auth_client.get('/api/auth/users/99999')

        assert response.status_code == 404

    def test_update_user(self, auth_client, test_user, app):
        """Test updating user information."""
        response = auth_client.put(f'/api/auth/users/{test_user.user_id}', json={
            'first_name': 'Updated',
            'phone': '+1234567890'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['first_name'] == 'Updated'

    def test_change_password(self, auth_client, app):
        """Test changing user password."""
        response = auth_client.post('/api/auth/change-password', json={
            'current_password': 'testpass123',
            'new_password': 'newpassword456'
        })

        assert response.status_code == 200
        assert response.get_json()['success'] is True

    def test_change_password_wrong_current(self, auth_client, app):
        """Test changing password with wrong current password."""
        response = auth_client.post('/api/auth/change-password', json={
            'current_password': 'wrongpassword',
            'new_password': 'newpassword456'
        })

        assert response.status_code == 400

    def test_delete_user_unauthorized(self, auth_client, test_user, app):
        """Test that users cannot delete themselves."""
        response = auth_client.delete(f'/api/auth/users/{test_user.user_id}')

        # Should either be forbidden, prevent self-deletion, or method not allowed
        assert response.status_code in [403, 400, 405]


