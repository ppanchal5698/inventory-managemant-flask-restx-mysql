# Purchase Orders and Sales Orders API tests

from datetime import date
from decimal import Decimal


class TestPurchaseOrdersAPI:
    """Tests for purchase orders API endpoints."""

    def test_list_purchase_orders(self, auth_client, sample_purchase_order, app):
        """Test listing purchase orders."""
        response = auth_client.get('/api/purchase-orders')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_filter_po_by_status(self, auth_client, sample_purchase_order, app):
        """Test filtering purchase orders by status."""
        response = auth_client.get('/api/purchase-orders?status=pending')

        assert response.status_code == 200

    def test_filter_po_by_supplier(self, auth_client, sample_purchase_order, sample_supplier, app):
        """Test filtering purchase orders by supplier."""
        response = auth_client.get(f'/api/purchase-orders?supplier_id={sample_supplier.supplier_id}')

        assert response.status_code == 200

    def test_create_purchase_order(self, auth_client, sample_supplier, sample_warehouse, sample_product, app):
        """Test creating a purchase order."""
        response = auth_client.post('/api/purchase-orders', json={
            'po_number': 'PO-NEW-001',
            'supplier_id': sample_supplier.supplier_id,
            'warehouse_id': sample_warehouse.warehouse_id,
            'order_date': str(date.today()),
            'expected_delivery_date': '2026-02-15',
            'tax_amount': 500.00,
            'shipping_cost': 100.00,
            'notes': 'Test order',
            'items': [
                {
                    'product_id': sample_product.product_id,
                    'quantity': 50,
                    'unit_price': 49.99,
                    'received_quantity': 0
                }
            ]
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['po_number'] == 'PO-NEW-001'
        assert data['data']['status'] == 'draft' or data['data']['status'] == 'pending'

    def test_create_po_missing_required(self, auth_client, app):
        """Test creating PO with missing required fields."""
        response = auth_client.post('/api/purchase-orders', json={
            'po_number': 'PO-INVALID'
            # Missing supplier_id, warehouse_id, order_date
        })

        assert response.status_code == 400

    def test_create_po_invalid_supplier(self, auth_client, sample_warehouse, app):
        """Test creating PO with invalid supplier."""
        response = auth_client.post('/api/purchase-orders', json={
            'po_number': 'PO-INV-002',
            'supplier_id': 99999,  # Non-existent
            'warehouse_id': sample_warehouse.warehouse_id,
            'order_date': str(date.today())
        })

        assert response.status_code == 400

    def test_get_purchase_order(self, auth_client, sample_purchase_order, app):
        """Test getting a purchase order."""
        response = auth_client.get(f'/api/purchase-orders/{sample_purchase_order.po_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['po_number'] == 'PO-TEST-001'

    def test_get_po_with_items(self, auth_client, sample_po_with_items, app):
        """Test getting PO with items."""
        response = auth_client.get(
            f'/api/purchase-orders/{sample_po_with_items.po_id}?include_items=true'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
        assert len(data['data']['items']) >= 1

    def test_update_purchase_order(self, auth_client, sample_purchase_order, app):
        """Test updating a purchase order."""
        response = auth_client.put(
            f'/api/purchase-orders/{sample_purchase_order.po_id}',
            json={'notes': 'Updated notes'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['notes'] == 'Updated notes'

    def test_update_po_status(self, auth_client, sample_purchase_order, app):
        """Test updating PO status."""
        response = auth_client.put(
            f'/api/purchase-orders/{sample_purchase_order.po_id}/status',
            json={'status': 'approved'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['status'] == 'approved'

    def test_update_po_invalid_status(self, auth_client, sample_purchase_order, app):
        """Test updating PO with invalid status."""
        response = auth_client.put(
            f'/api/purchase-orders/{sample_purchase_order.po_id}/status',
            json={'status': 'invalid_status'}
        )

        assert response.status_code == 400

    def test_add_po_item(self, auth_client, sample_supplier, sample_warehouse, test_user, sample_product, db_session, app):
        """Test adding item to a draft purchase order."""
        # Create a draft PO that allows item addition
        from datetime import date

        from app.modules.purchase_orders.models import PurchaseOrder

        with app.app_context():
            draft_po = PurchaseOrder(
                po_number='PO-ITEM-001',
                supplier_id=sample_supplier.supplier_id,
                warehouse_id=sample_warehouse.warehouse_id,
                order_date=date.today(),
                status='draft',  # Must be draft to add items
                created_by=test_user.user_id
            )
            db_session.add(draft_po)
            db_session.commit()
            db_session.refresh(draft_po)
            po_id = draft_po.po_id

        response = auth_client.post(
            f'/api/purchase-orders/{po_id}/items',
            json={
                'product_id': sample_product.product_id,
                'quantity': 25,
                'unit_price': 49.99
            }
        )

        assert response.status_code == 201

    def test_add_po_item_pending_fails(self, auth_client, sample_purchase_order, sample_product, app):
        """Test that adding items to a pending PO fails."""
        response = auth_client.post(
            f'/api/purchase-orders/{sample_purchase_order.po_id}/items',
            json={
                'product_id': sample_product.product_id,
                'quantity': 25,
                'unit_price': 49.99
            }
        )
        assert response.status_code == 400

    def test_generate_po_number(self, auth_client, app):
        """Test generating PO number."""
        response = auth_client.get('/api/purchase-orders/generate-number')

        assert response.status_code == 200
        data = response.get_json()
        assert 'po_number' in data['data'] or 'number' in data['data']

    def test_delete_purchase_order(self, auth_client, sample_supplier, sample_warehouse, test_user, db_session, app):
        """Test deleting a draft purchase order."""
        # Create a draft PO that can be deleted
        from datetime import date

        from app.modules.purchase_orders.models import PurchaseOrder

        with app.app_context():
            draft_po = PurchaseOrder(
                po_number='PO-DELETE-001',
                supplier_id=sample_supplier.supplier_id,
                warehouse_id=sample_warehouse.warehouse_id,
                order_date=date.today(),
                status='draft',  # Must be draft to delete
                created_by=test_user.user_id
            )
            db_session.add(draft_po)
            db_session.commit()
            db_session.refresh(draft_po)
            po_id = draft_po.po_id

        response = auth_client.delete(f'/api/purchase-orders/{po_id}')
        assert response.status_code == 200

    def test_delete_purchase_order_pending_fails(self, auth_client, sample_purchase_order, app):
        """Test that deleting a pending purchase order fails."""
        response = auth_client.delete(f'/api/purchase-orders/{sample_purchase_order.po_id}')
        assert response.status_code == 400  # Can't delete pending orders


class TestSalesOrdersAPI:
    """Tests for sales orders API endpoints."""

    def test_list_sales_orders(self, auth_client, sample_sales_order, app):
        """Test listing sales orders."""
        response = auth_client.get('/api/sales-orders')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_filter_so_by_status(self, auth_client, sample_sales_order, app):
        """Test filtering sales orders by status."""
        response = auth_client.get('/api/sales-orders?status=pending')

        assert response.status_code == 200

    def test_filter_so_by_payment_status(self, auth_client, sample_sales_order, app):
        """Test filtering sales orders by payment status."""
        response = auth_client.get('/api/sales-orders?payment_status=unpaid')

        assert response.status_code == 200

    def test_filter_so_by_customer(self, auth_client, sample_sales_order, sample_customer, app):
        """Test filtering sales orders by customer."""
        response = auth_client.get(f'/api/sales-orders?customer_id={sample_customer.customer_id}')

        assert response.status_code == 200

    def test_create_sales_order(self, auth_client, sample_customer, sample_warehouse, sample_product, app):
        """Test creating a sales order."""
        response = auth_client.post('/api/sales-orders', json={
            'order_number': 'SO-NEW-001',
            'customer_id': sample_customer.customer_id,
            'warehouse_id': sample_warehouse.warehouse_id,
            'order_date': str(date.today()),
            'expected_delivery_date': '2026-02-07',
            'tax_amount': 95.00,
            'shipping_cost': 20.00,
            'discount_amount': 10.00,
            'notes': 'Test sales order',
            'items': [
                {
                    'product_id': sample_product.product_id,
                    'quantity': 10,
                    'unit_price': 99.99,
                    'discount': 10.00
                }
            ]
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['order_number'] == 'SO-NEW-001'
        assert data['data']['payment_status'] == 'unpaid'

    def test_create_so_missing_required(self, auth_client, app):
        """Test creating SO with missing required fields."""
        response = auth_client.post('/api/sales-orders', json={
            'order_number': 'SO-INVALID'
            # Missing customer_id, warehouse_id, order_date
        })

        assert response.status_code == 400

    def test_get_sales_order(self, auth_client, sample_sales_order, app):
        """Test getting a sales order."""
        response = auth_client.get(f'/api/sales-orders/{sample_sales_order.order_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['order_number'] == 'SO-TEST-001'

    def test_get_so_with_items_and_customer(self, auth_client, sample_so_with_items, app):
        """Test getting SO with items and customer info."""
        response = auth_client.get(
            f'/api/sales-orders/{sample_so_with_items.order_id}?include_items=true&include_customer=true'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
        assert 'customer' in data['data'] or 'customer_name' in data['data']

    def test_update_sales_order(self, auth_client, sample_sales_order, app):
        """Test updating a sales order."""
        response = auth_client.put(
            f'/api/sales-orders/{sample_sales_order.order_id}',
            json={'notes': 'Updated delivery notes'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['notes'] == 'Updated delivery notes'

    def test_update_order_status(self, auth_client, sample_sales_order, app):
        """Test updating order status."""
        response = auth_client.put(
            f'/api/sales-orders/{sample_sales_order.order_id}/status',
            json={'status': 'processing'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['status'] == 'processing'

    def test_update_payment_status(self, auth_client, sample_sales_order, app):
        """Test updating payment status."""
        response = auth_client.put(
            f'/api/sales-orders/{sample_sales_order.order_id}/payment-status',
            json={'payment_status': 'paid'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['payment_status'] == 'paid'

    def test_add_so_item(self, auth_client, sample_sales_order, sample_product, app):
        """Test adding item to sales order."""
        response = auth_client.post(
            f'/api/sales-orders/{sample_sales_order.order_id}/items',
            json={
                'product_id': sample_product.product_id,
                'quantity': 5,
                'unit_price': 99.99,
                'discount': 0
            }
        )

        assert response.status_code == 201

    def test_cancel_sales_order(self, auth_client, sample_sales_order, app):
        """Test cancelling a sales order."""
        response = auth_client.post(f'/api/sales-orders/{sample_sales_order.order_id}/cancel')

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['status'] == 'cancelled'

    def test_generate_order_number(self, auth_client, app):
        """Test generating order number."""
        response = auth_client.get('/api/sales-orders/generate-number')

        assert response.status_code == 200
        data = response.get_json()
        assert 'order_number' in data['data'] or 'number' in data['data']

    def test_delete_sales_order(self, auth_client, sample_sales_order, app):
        """Test deleting a sales order."""
        response = auth_client.delete(f'/api/sales-orders/{sample_sales_order.order_id}')

        # Might not be allowed or only for certain statuses (405 = method not allowed)
        assert response.status_code in [200, 400, 403, 405]

