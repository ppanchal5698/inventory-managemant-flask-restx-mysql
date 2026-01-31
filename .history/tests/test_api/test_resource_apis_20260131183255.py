# Resource API tests - Categories, Brands, Suppliers, Products, etc.

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

    def test_get_category(self, auth_client, sample_category, app):
        """Test getting a single category."""
        response = auth_client.get(f'/api/categories/{sample_category.category_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['category_name'] == 'Electronics'

    def test_update_category(self, auth_client, sample_category, app):
        """Test updating a category."""
        response = auth_client.put(
            f'/api/categories/{sample_category.category_id}',
            json={'category_name': 'Updated Electronics'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['category_name'] == 'Updated Electronics'

    def test_delete_category(self, auth_client, sample_category, app):
        """Test deleting a category."""
        response = auth_client.delete(f'/api/categories/{sample_category.category_id}')

        assert response.status_code == 200
        assert response.get_json()['success'] is True

    def test_unauthorized_access(self, client, app):
        """Test accessing categories without login."""
        response = client.get('/api/categories')

        assert response.status_code == 401


class TestBrandsAPI:
    """Tests for brands API endpoints."""

    def test_list_brands(self, auth_client, sample_brand, app):
        """Test listing brands."""
        response = auth_client.get('/api/brands')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_create_brand(self, auth_client, app):
        """Test creating a brand."""
        response = auth_client.post('/api/brands', json={
            'brand_name': 'NewBrand',
            'manufacturer_name': 'New Mfg Inc.'
        })

        assert response.status_code == 201

    def test_get_brand(self, auth_client, sample_brand, app):
        """Test getting a single brand."""
        response = auth_client.get(f'/api/brands/{sample_brand.brand_id}')

        assert response.status_code == 200


class TestSuppliersAPI:
    """Tests for suppliers API endpoints."""

    def test_list_suppliers(self, auth_client, sample_supplier, app):
        """Test listing suppliers."""
        response = auth_client.get('/api/suppliers')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_create_supplier(self, auth_client, app):
        """Test creating a supplier."""
        response = auth_client.post('/api/suppliers', json={
            'supplier_name': 'New Supplier Co.',
            'contact_person': 'Jane Doe',
            'email': 'jane@newsupplier.com'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['contact_person'] == 'Jane Doe'


class TestProductsAPI:
    """Tests for products API endpoints."""

    def test_list_products(self, auth_client, sample_product, app):
        """Test listing products."""
        response = auth_client.get('/api/products')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_create_product(self, auth_client, sample_category, sample_brand, app):
        """Test creating a product."""
        response = auth_client.post('/api/products', json={
            'product_code': 'NEWPROD001',
            'product_name': 'New Product',
            'unit_price': 29.99,
            'category_id': sample_category.category_id,
            'brand_id': sample_brand.brand_id
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['product_code'] == 'NEWPROD001'

    def test_search_products(self, auth_client, sample_product, app):
        """Test searching products."""
        response = auth_client.get('/api/products?search=Test')

        assert response.status_code == 200

    def test_get_low_stock(self, auth_client, app):
        """Test getting low stock products."""
        response = auth_client.get('/api/products/low-stock')

        assert response.status_code == 200


class TestWarehousesAPI:
    """Tests for warehouses API endpoints."""

    def test_list_warehouses(self, auth_client, sample_warehouse, app):
        """Test listing warehouses."""
        response = auth_client.get('/api/warehouses')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_create_warehouse(self, auth_client, app):
        """Test creating a warehouse."""
        response = auth_client.post('/api/warehouses', json={
            'warehouse_name': 'New Warehouse',
            'location': 'Industrial Area',
            'capacity': 5000
        })

        assert response.status_code == 201


class TestCustomersAPI:
    """Tests for customers API endpoints."""

    def test_list_customers(self, auth_client, sample_customer, app):
        """Test listing customers."""
        response = auth_client.get('/api/customers')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_create_customer(self, auth_client, app):
        """Test creating a customer."""
        response = auth_client.post('/api/customers', json={
            'customer_name': 'New Customer Corp',
            'contact_person': 'John Smith',
            'email': 'john@newcustomer.com'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['contact_person'] == 'John Smith'


class TestStockAPI:
    """Tests for stock API endpoints."""

    def test_list_stock(self, auth_client, sample_stock, app):
        """Test listing stock."""
        response = auth_client.get('/api/stock')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_create_stock(self, auth_client, sample_product, sample_warehouse, app):
        """Test creating a stock entry."""
        response = auth_client.post('/api/stock', json={
            'product_id': sample_product.product_id,
            'warehouse_id': sample_warehouse.warehouse_id,
            'quantity_on_hand': 200
        })

        assert response.status_code == 201

    def test_adjust_stock(self, auth_client, sample_stock, app):
        """Test adjusting stock."""
        response = auth_client.post(
            f'/api/stock/{sample_stock.stock_id}/adjust',
            json={'adjustment': 50, 'reason': 'Stock received'}
        )

        assert response.status_code == 200

