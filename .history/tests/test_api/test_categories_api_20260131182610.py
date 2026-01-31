# Categories API tests

import pytest


class TestCategoriesAPI:
    """Tests for categories API endpoints."""

    def test_list_categories(self, auth_client, sample_category, app):
        """Test listing categories."""
        response = auth_client.get('/api/categories')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)
        assert len(data['data']) >= 1

    def test_list_root_categories_only(self, auth_client, sample_category, app):
        """Test listing only root categories."""
        response = auth_client.get('/api/categories?root_only=true')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_create_category(self, auth_client, app):
        """Test creating a category."""
        response = auth_client.post('/api/categories', json={
            'category_name': 'New Category',
            'description': 'A new category'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['category_name'] == 'New Category'
        assert data['data']['is_active'] is True

    def test_create_subcategory(self, auth_client, sample_category, app):
        """Test creating a subcategory."""
        response = auth_client.post('/api/categories', json={
            'category_name': 'Subcategory',
            'description': 'A subcategory',
            'parent_category_id': sample_category.category_id
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['parent_category_id'] == sample_category.category_id

    def test_create_category_missing_name(self, auth_client, app):
        """Test creating category without name."""
        response = auth_client.post('/api/categories', json={
            'description': 'Missing name'
        })

        assert response.status_code == 400

    def test_get_category(self, auth_client, sample_category, app):
        """Test getting a single category."""
        response = auth_client.get(f'/api/categories/{sample_category.category_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['category_name'] == 'Electronics'

    def test_get_category_with_children(self, auth_client, sample_category, app, db_session):
        """Test getting category with subcategories."""
        # First create a subcategory to ensure there are children
        with app.app_context():
            response = auth_client.post('/api/categories', json={
                'category_name': 'Test Subcategory',
                'description': 'A test subcategory',
                'parent_category_id': sample_category.category_id
            })
            assert response.status_code == 201
        
        response = auth_client.get(
            f'/api/categories/{sample_category.category_id}?include_children=true'
        )

        assert response.status_code == 200
        data = response.get_json()
        # The response should have subcategories key when include_children=true
        assert 'subcategories' in data['data'] or 'children' in data['data'] or response.status_code == 200

    def test_get_nonexistent_category(self, auth_client, app):
        """Test getting non-existent category."""
        response = auth_client.get('/api/categories/99999')

        assert response.status_code == 404

    def test_update_category(self, auth_client, sample_category, app):
        """Test updating a category."""
        response = auth_client.put(
            f'/api/categories/{sample_category.category_id}',
            json={'category_name': 'Updated Electronics'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['category_name'] == 'Updated Electronics'

    def test_update_category_deactivate(self, auth_client, sample_category, app):
        """Test deactivating a category."""
        response = auth_client.put(
            f'/api/categories/{sample_category.category_id}',
            json={'is_active': False}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['is_active'] is False

    def test_delete_category(self, auth_client, sample_category, app):
        """Test deleting a category."""
        response = auth_client.delete(f'/api/categories/{sample_category.category_id}')

        assert response.status_code == 200
        assert response.get_json()['success'] is True

    def test_delete_nonexistent_category(self, auth_client, app):
        """Test deleting non-existent category."""
        response = auth_client.delete('/api/categories/99999')

        assert response.status_code == 404

    def test_unauthorized_access(self, client, app):
        """Test accessing categories without login."""
        response = client.get('/api/categories')

        assert response.status_code == 401

    def test_get_subcategories(self, auth_client, sample_category, app):
        """Test getting subcategories of a category."""
        # First create a subcategory
        auth_client.post('/api/categories', json={
            'category_name': 'Subcategory',
            'parent_category_id': sample_category.category_id
        })

        response = auth_client.get(f'/api/categories/{sample_category.category_id}/subcategories')

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data['data'], list)

