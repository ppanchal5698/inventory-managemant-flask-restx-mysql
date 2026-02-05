# Auth API tests (Async)

import pytest
import asyncio

@pytest.mark.asyncio
class TestAuthAPI:
    """Tests for auth API endpoints."""

    async def test_login_success(self, client, test_user):
        """Test successful login."""
        response = await asyncio.to_thread(
            client.post,
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'testpass123'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['user']['username'] == 'testuser'
        assert 'access_token' in data['data']

    async def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        response = await asyncio.to_thread(
            client.post,
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'wrongpassword'}
        )

        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False

    async def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = await asyncio.to_thread(
            client.post,
            '/api/auth/login',
            json={'username': 'nonexistent', 'password': 'password'}
        )

        assert response.status_code == 401

    async def test_login_missing_credentials(self, client):
        """Test login with missing credentials."""
        response = await asyncio.to_thread(
            client.post,
            '/api/auth/login',
            json={}
        )
        assert response.status_code == 400

    async def test_logout(self, auth_client):
        """Test logout."""
        response = await auth_client.post('/api/auth/logout')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    async def test_get_current_user(self, auth_client):
        """Test getting current user info."""
        response = await auth_client.get('/api/auth/me')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['username'] == 'testuser'
        assert data['data']['role'] == 'admin'

    async def test_get_current_user_unauthorized(self, client):
        """Test getting current user without login."""
        response = await asyncio.to_thread(
            client.get,
            '/api/auth/me'
        )

        assert response.status_code == 401 # or 422 if header missing format


@pytest.mark.asyncio
class TestUserManagementAPI:
    """Tests for user management endpoints."""

    async def test_list_users(self, auth_client):
        """Test listing users (admin only)."""
        response = await auth_client.get('/api/auth/users')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)
        assert len(data['data']) >= 1

    async def test_create_user(self, auth_client):
        """Test creating a new user."""
        response = await auth_client.post('/api/auth/users', json={
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

    async def test_create_user_duplicate_username(self, auth_client, test_user):
        """Test creating user with duplicate username."""
        response = await auth_client.post('/api/auth/users', json={
            'username': 'testuser',  # Already exists
            'password': 'password',
            'first_name': 'Duplicate',
            'last_name': 'User',
            'email': 'duplicate@example.com',
            'role': 'staff'
        })

        assert response.status_code == 400

    async def test_create_user_duplicate_email(self, auth_client, test_user):
        """Test creating user with duplicate email."""
        response = await auth_client.post('/api/auth/users', json={
            'username': 'anotheruser',
            'password': 'password',
            'first_name': 'Another',
            'last_name': 'User',
            'email': 'test@example.com',  # Already exists
            'role': 'staff'
        })

        assert response.status_code == 400

    async def test_create_user_missing_required(self, auth_client):
        """Test creating user with missing required fields."""
        response = await auth_client.post('/api/auth/users', json={
            'username': 'incomplete'
            # Missing password and email
        })

        assert response.status_code == 400

    async def test_get_user_by_id(self, auth_client, test_user):
        """Test getting user by ID."""
        response = await auth_client.get(f'/api/auth/users/{test_user.user_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['username'] == 'testuser'

    async def test_get_user_nonexistent(self, auth_client):
        """Test getting non-existent user."""
        response = await auth_client.get('/api/auth/users/99999')

        assert response.status_code == 404

    async def test_update_user(self, auth_client, test_user):
        """Test updating user information."""
        response = await auth_client.put(f'/api/auth/users/{test_user.user_id}', json={
            'first_name': 'Updated',
            'phone': '+1234567890'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['first_name'] == 'Updated'

    async def test_change_password(self, auth_client):
        """Test changing user password."""
        response = await auth_client.post('/api/auth/change-password', json={
            'current_password': 'testpass123',
            'new_password': 'newpassword456'
        })

        assert response.status_code == 200
        assert response.get_json()['success'] is True

    async def test_change_password_wrong_current(self, auth_client):
        """Test changing password with wrong current password."""
        response = await auth_client.post('/api/auth/change-password', json={
            'current_password': 'wrongpassword',
            'new_password': 'newpassword456'
        })

        assert response.status_code == 400
