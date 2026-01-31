# Order API tests - Purchase Orders, Sales Orders, Inventory

from datetime import date

import pytest


class TestPurchaseOrdersAPI:
    """Tests for purchase orders API endpoints."""

    def test_list_purchase_orders(self, auth_client, app):
        """Test listing purchase orders."""
        response = auth_client.get('/api/purchase-orders')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_create_purchase_order(self, auth_client, sample_supplier,
                                    sample_warehouse, app):
        """Test creating a purchase order."""
        response = auth_client.post('/api/purchase-orders', json={
            'po_number': 'PO-TEST-001',
            'supplier_id': sample_supplier.supplier_id,
            'warehouse_id': sample_warehouse.warehouse_id,
            'order_date': str(date.today())
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['po_number'] == 'PO-TEST-001'

    def test_get_purchase_order(self, auth_client, sample_supplier,
                                 sample_warehouse, app):
        """Test getting a purchase order."""
        # First create one
        create_response = auth_client.post('/api/purchase-orders', json={
            'po_number': 'PO-GET-001',
            'supplier_id': sample_supplier.supplier_id,
            'warehouse_id': sample_warehouse.warehouse_id,
            'order_date': str(date.today())
        })
        po_id = create_response.get_json()['data']['po_id']

        # Then get it
        response = auth_client.get(f'/api/purchase-orders/{po_id}')

        assert response.status_code == 200
        assert response.get_json()['data']['po_number'] == 'PO-GET-001'


class TestSalesOrdersAPI:
    """Tests for sales orders API endpoints."""

    def test_list_sales_orders(self, auth_client, app):
        """Test listing sales orders."""
        response = auth_client.get('/api/sales-orders')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_create_sales_order(self, auth_client, sample_customer,
                                 sample_warehouse, app):
        """Test creating a sales order."""
        response = auth_client.post('/api/sales-orders', json={
            'order_number': 'SO-TEST-001',
            'customer_id': sample_customer.customer_id,
            'warehouse_id': sample_warehouse.warehouse_id,
            'order_date': str(date.today())
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['order_number'] == 'SO-TEST-001'

    def test_get_sales_order(self, auth_client, sample_customer,
                              sample_warehouse, app):
        """Test getting a sales order."""
        # First create one
        create_response = auth_client.post('/api/sales-orders', json={
            'order_number': 'SO-GET-001',
            'customer_id': sample_customer.customer_id,
            'warehouse_id': sample_warehouse.warehouse_id,
            'order_date': str(date.today())
        })
        order_id = create_response.get_json()['data']['order_id']

        # Then get it
        response = auth_client.get(f'/api/sales-orders/{order_id}')

        assert response.status_code == 200


class TestInventoryAPI:
    """Tests for inventory API endpoints."""

    def test_list_transactions(self, auth_client, app):
        """Test listing inventory transactions."""
        response = auth_client.get('/api/inventory/transactions')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_list_stock_adjustments(self, auth_client, app):
        """Test listing stock adjustments."""
        response = auth_client.get('/api/inventory/adjustments')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_create_stock_adjustment(self, auth_client, sample_product,
                                      sample_warehouse, app):
        """Test creating a stock adjustment."""
        response = auth_client.post('/api/inventory/adjustments', json={
            'product_id': sample_product.product_id,
            'warehouse_id': sample_warehouse.warehouse_id,
            'new_quantity': 95,
            'reason': 'damage',
            'notes': 'Test adjustment'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True

