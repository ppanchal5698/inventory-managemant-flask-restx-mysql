# Products API tests (Async)

import pytest
import asyncio

@pytest.mark.asyncio
class TestProductsAPI:
    """Tests for products API endpoints."""

    async def test_list_products(self, auth_client, sample_product):
        """Test listing products."""
        response = await auth_client.get('/api/products')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1

    async def test_list_products_with_stock(self, auth_client, sample_product, sample_stock):
        """Test listing products with stock information."""
        response = await auth_client.get('/api/products?include_stock=true')

        assert response.status_code == 200

    async def test_search_products(self, auth_client, sample_product):
        """Test searching products."""
        response = await auth_client.get('/api/products?search=Test')

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data['data'], list)

    async def test_filter_by_category(self, auth_client, sample_product, sample_category):
        """Test filtering products by category."""
        response = await auth_client.get(f'/api/products?category_id={sample_category.category_id}')

        assert response.status_code == 200

    async def test_filter_by_brand(self, auth_client, sample_product, sample_brand):
        """Test filtering products by brand."""
        response = await auth_client.get(f'/api/products?brand_id={sample_brand.brand_id}')

        assert response.status_code == 200

    async def test_create_product(self, auth_client, sample_category, sample_brand):
        """Test creating a product."""
        response = await auth_client.post('/api/products', json={
            'product_code': 'NEWPROD001',
            'product_name': 'New Product',
            'unit_price': 29.99,
            'cost_price': 15.00,
            'category_id': sample_category.category_id,
            'brand_id': sample_brand.brand_id,
            'reorder_level': 10,
            'min_stock_level': 5,
            'max_stock_level': 100,
            'unit_of_measure': 'pcs',
            'barcode': '1234567890123',
            'sku': 'SKU-NEW-001'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['product_code'] == 'NEWPROD001'
        assert float(data['data']['unit_price']) == 29.99

    async def test_create_product_duplicate_code(self, auth_client, sample_product, sample_category, sample_brand):
        """Test creating product with duplicate code."""
        response = await auth_client.post('/api/products', json={
            'product_code': sample_product.product_code,  # Duplicate
            'product_name': 'Duplicate Product',
            'unit_price': 20.00,
            'category_id': sample_category.category_id,
            'brand_id': sample_brand.brand_id
        })

        assert response.status_code == 400

    async def test_create_product_missing_required(self, auth_client):
        """Test creating product with missing required fields."""
        response = await auth_client.post('/api/products', json={
            'product_name': 'Incomplete Product'
            # Missing product_code and unit_price
        })

        assert response.status_code == 400

    async def test_get_product(self, auth_client, sample_product):
        """Test getting a single product."""
        response = await auth_client.get(f'/api/products/{sample_product.product_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['product_code'] == 'PROD001'

    async def test_get_product_by_barcode(self, auth_client, sample_product, db_session):
        """Test getting product by barcode."""
        # Update product with barcode
        # Need to update in DB session. sample_product is detached?
        # conftest yields objects.
        # But for update we should use service or merge.
        # Or just update attrs and commit.

        # sample_product attached to db_session?
        # db_session fixture yields session.
        # sample_product is created in db_session.
        # But if db_session is closed/rollback after fixture setup?
        # The test function gets 'db_session' fixture which is fresh.
        # sample_product was created in ITS OWN scope?
        # In conftest:
        # @pytest.fixture
        # async def sample_product(app, db_session, ...): ...
        # The db_session passed to sample_product is the one yielded by db_session fixture?
        # Yes, scope='function'.
        # So it's the same session.

        sample_product.barcode = '1234567890'
        db_session.add(sample_product)
        await db_session.commit()

        response = await auth_client.get(f'/api/products/barcode/{sample_product.barcode}')

        assert response.status_code == 200

    async def test_get_low_stock_products(self, auth_client, sample_product, sample_stock):
        """Test getting low stock products."""
        response = await auth_client.get('/api/products/low-stock')

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data['data'], list)

    async def test_update_product(self, auth_client, sample_product):
        """Test updating a product."""
        response = await auth_client.put(
            f'/api/products/{sample_product.product_id}',
            json={
                'unit_price': 109.99,
                'reorder_level': 15
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert float(data['data']['unit_price']) == 109.99

    async def test_update_product_deactivate(self, auth_client, sample_product):
        """Test deactivating a product."""
        response = await auth_client.put(
            f'/api/products/{sample_product.product_id}',
            json={'is_active': False}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['is_active'] is False

    async def test_delete_product(self, auth_client, sample_product):
        """Test deleting a product."""
        response = await auth_client.delete(f'/api/products/{sample_product.product_id}')

        assert response.status_code == 200
