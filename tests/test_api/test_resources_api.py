# Brands, Suppliers, Warehouses, Customers API tests


class TestBrandsAPI:
    """Tests for brands API endpoints."""

    def test_list_brands(self, auth_client, sample_brand, app):
        """Test listing brands."""
        response = auth_client.get('/api/brands')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_create_brand(self, auth_client, app):
        """Test creating a brand."""
        response = auth_client.post('/api/brands', json={
            'brand_name': 'NewBrand',
            'manufacturer_name': 'New Mfg Inc.',
            'description': 'Quality products'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['brand_name'] == 'NewBrand'

    def test_create_brand_duplicate_name(self, auth_client, sample_brand, app):
        """Test creating brand with duplicate name."""
        response = auth_client.post('/api/brands', json={
            'brand_name': sample_brand.brand_name,
            'manufacturer_name': 'Duplicate'
        })

        assert response.status_code == 400

    def test_get_brand(self, auth_client, sample_brand, app):
        """Test getting a single brand."""
        response = auth_client.get(f'/api/brands/{sample_brand.brand_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['brand_name'] == 'TechBrand'

    def test_update_brand(self, auth_client, sample_brand, app):
        """Test updating a brand."""
        response = auth_client.put(
            f'/api/brands/{sample_brand.brand_id}',
            json={'description': 'Updated description'}
        )

        assert response.status_code == 200

    def test_delete_brand(self, auth_client, sample_brand, app):
        """Test deleting a brand."""
        response = auth_client.delete(f'/api/brands/{sample_brand.brand_id}')

        assert response.status_code == 200


class TestSuppliersAPI:
    """Tests for suppliers API endpoints."""

    def test_list_suppliers(self, auth_client, sample_supplier, app):
        """Test listing suppliers."""
        response = auth_client.get('/api/suppliers')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_search_suppliers(self, auth_client, sample_supplier, app):
        """Test searching suppliers."""
        response = auth_client.get('/api/suppliers?search=Tech')

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data['data'], list)

    def test_create_supplier(self, auth_client, app):
        """Test creating a supplier."""
        response = auth_client.post('/api/suppliers', json={
            'supplier_name': 'New Supplier Co.',
            'contact_person': 'Jane Doe',
            'email': 'jane@newsupplier.com',
            'phone': '+1234567890',
            'city': 'Boston',
            'country': 'USA'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['contact_person'] == 'Jane Doe'
        assert data['data']['country'] == 'USA'

    def test_create_supplier_missing_name(self, auth_client, app):
        """Test creating supplier without name."""
        response = auth_client.post('/api/suppliers', json={
            'contact_person': 'John',
            'email': 'john@example.com'
        })

        assert response.status_code == 400

    def test_create_supplier_invalid_email(self, auth_client, app):
        """Test creating supplier with invalid email."""
        response = auth_client.post('/api/suppliers', json={
            'supplier_name': 'Test Supplier',
            'email': 'invalid-email'
        })

        assert response.status_code == 400

    def test_get_supplier(self, auth_client, sample_supplier, app):
        """Test getting a single supplier."""
        response = auth_client.get(f'/api/suppliers/{sample_supplier.supplier_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['supplier_name'] == 'Tech Supplies Co.'

    def test_update_supplier(self, auth_client, sample_supplier, app):
        """Test updating a supplier."""
        response = auth_client.put(
            f'/api/suppliers/{sample_supplier.supplier_id}',
            json={
                'contact_person': 'Updated Contact',
                'phone': '+9999999999'
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['contact_person'] == 'Updated Contact'

    def test_delete_supplier(self, auth_client, sample_supplier, app):
        """Test deleting a supplier."""
        response = auth_client.delete(f'/api/suppliers/{sample_supplier.supplier_id}')

        assert response.status_code == 200


class TestWarehousesAPI:
    """Tests for warehouses API endpoints."""

    def test_list_warehouses(self, auth_client, sample_warehouse, app):
        """Test listing warehouses."""
        response = auth_client.get('/api/warehouses')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_create_warehouse(self, auth_client, app):
        """Test creating a warehouse."""
        response = auth_client.post('/api/warehouses', json={
            'warehouse_name': 'New Warehouse',
            'location': 'Industrial Area',
            'city': 'Chicago',
            'country': 'USA',
            'capacity': 5000
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['warehouse_name'] == 'New Warehouse'
        assert data['data']['capacity'] == 5000

    def test_create_warehouse_missing_name(self, auth_client, app):
        """Test creating warehouse without name."""
        response = auth_client.post('/api/warehouses', json={
            'location': 'Somewhere',
            'capacity': 1000
        })

        assert response.status_code == 400

    def test_get_warehouse(self, auth_client, sample_warehouse, app):
        """Test getting a single warehouse."""
        response = auth_client.get(f'/api/warehouses/{sample_warehouse.warehouse_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['warehouse_name'] == 'Main Warehouse'

    def test_get_warehouse_with_stock(self, auth_client, sample_warehouse, sample_stock, app):
        """Test getting warehouse with stock information."""
        response = auth_client.get(
            f'/api/warehouses/{sample_warehouse.warehouse_id}?include_stock=true'
        )

        assert response.status_code == 200

    def test_update_warehouse(self, auth_client, sample_warehouse, app):
        """Test updating a warehouse."""
        response = auth_client.put(
            f'/api/warehouses/{sample_warehouse.warehouse_id}',
            json={
                'warehouse_name': 'Updated Warehouse',
                'capacity': 15000
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['capacity'] == 15000

    def test_delete_warehouse(self, auth_client, sample_warehouse, app):
        """Test deleting a warehouse."""
        response = auth_client.delete(f'/api/warehouses/{sample_warehouse.warehouse_id}')

        assert response.status_code == 200


class TestCustomersAPI:
    """Tests for customers API endpoints."""

    def test_list_customers(self, auth_client, sample_customer, app):
        """Test listing customers."""
        response = auth_client.get('/api/customers')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_search_customers(self, auth_client, sample_customer, app):
        """Test searching customers."""
        response = auth_client.get('/api/customers?search=Test')

        assert response.status_code == 200

    def test_create_customer(self, auth_client, app):
        """Test creating a customer."""
        response = auth_client.post('/api/customers', json={
            'customer_name': 'New Customer Corp',
            'contact_person': 'John Smith',
            'email': 'john@newcustomer.com',
            'phone': '+1234567890',
            'city': 'Seattle',
            'country': 'USA',
            'credit_limit': 50000.00
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['contact_person'] == 'John Smith'
        assert data['data']['country'] == 'USA'

    def test_create_customer_with_defaults(self, auth_client, app):
        """Test creating customer with default country."""
        response = auth_client.post('/api/customers', json={
            'customer_name': 'Local Customer',
            'contact_person': 'Jane Doe',
            'email': 'jane@localcustomer.com'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['country'] == 'USA'  # Default value

    def test_get_customer(self, auth_client, sample_customer, app):
        """Test getting a single customer."""
        response = auth_client.get(f'/api/customers/{sample_customer.customer_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['customer_name'] == 'Test Customer Inc.'

    def test_update_customer(self, auth_client, sample_customer, app):
        """Test updating a customer."""
        response = auth_client.put(
            f'/api/customers/{sample_customer.customer_id}',
            json={
                'contact_person': 'Updated Contact',
                'credit_limit': 75000.00
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['contact_person'] == 'Updated Contact'

    def test_delete_customer(self, auth_client, sample_customer, app):
        """Test deleting a customer."""
        response = auth_client.delete(f'/api/customers/{sample_customer.customer_id}')

        assert response.status_code == 200

