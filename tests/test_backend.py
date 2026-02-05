import pytest
import asyncio
from decimal import Decimal

@pytest.mark.asyncio
async def test_end_to_end_flow(client, test_user):
    """
    Comprehensive End-to-End Test for Inventory Management System.
    """

    # --- 1. Authentication ---
    print("\n--- Step 1: Authentication ---")

    # User is already created by test_user fixture
    # Login
    response = await asyncio.to_thread(
        client.post,
        '/api/auth/login',
        json={'username': 'testuser', 'password': 'testpass123'}
    )
    assert response.status_code == 200, f"Login failed: {response.json}"
    token = response.get_json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("Login successful.")

    # Helper for requests
    async def api_post(url, data):
        return await asyncio.to_thread(client.post, url, json=data, headers=headers)

    async def api_get(url):
        return await asyncio.to_thread(client.get, url, headers=headers)

    async def api_put(url, data):
        return await asyncio.to_thread(client.put, url, json=data, headers=headers)

    # --- 2. Catalog Setup ---
    print("\n--- Step 2: Catalog Setup ---")

    # Create Category
    resp = await api_post('/api/categories', {
        'category_name': 'E2E Electronics',
        'description': 'Electronics for E2E test'
    })
    assert resp.status_code == 201
    category_id = resp.get_json()['data']['category_id']
    print(f"Category created: {category_id}")

    # Create Brand
    resp = await api_post('/api/brands', {
        'brand_name': 'E2E Tech',
        'manufacturer_name': 'E2E Mfg'
    })
    assert resp.status_code == 201
    brand_id = resp.get_json()['data']['brand_id']
    print(f"Brand created: {brand_id}")

    # Create Supplier
    resp = await api_post('/api/suppliers', {
        'supplier_name': 'E2E Supplier Inc.',
        'email': 'supplier@e2e.com',
        'contact_person': 'Supplier John'
    })
    assert resp.status_code == 201
    supplier_id = resp.get_json()['data']['supplier_id']
    print(f"Supplier created: {supplier_id}")

    # --- 3. Product Setup ---
    print("\n--- Step 3: Product Setup ---")

    resp = await api_post('/api/products', {
        'product_code': 'E2E-PROD-001',
        'product_name': 'E2E Widget',
        'category_id': category_id,
        'brand_id': brand_id,
        'unit_price': 100.00,
        'cost_price': 50.00,
        'reorder_level': 10,
        'sku': 'SKU-E2E-001'
    })
    assert resp.status_code == 201
    product_id = resp.get_json()['data']['product_id']
    print(f"Product created: {product_id}")

    # --- 4. Inventory Setup ---
    print("\n--- Step 4: Inventory Setup ---")

    # Create Warehouse
    resp = await api_post('/api/warehouses', {
        'warehouse_name': 'E2E Main Warehouse',
        'location': 'Test City'
    })
    assert resp.status_code == 201
    warehouse_id = resp.get_json()['data']['warehouse_id']
    print(f"Warehouse created: {warehouse_id}")

    # Verify initial stock
    resp = await api_get(f'/api/stock/lookup?product_id={product_id}&warehouse_id={warehouse_id}')
    assert resp.status_code == 404, "Stock should not exist yet"

    # --- 5. Procurement (Purchase Order) ---
    print("\n--- Step 5: Procurement (Purchase Order) ---")

    # Create PO
    po_data = {
        'po_number': 'PO-E2E-001',
        'supplier_id': supplier_id,
        'warehouse_id': warehouse_id,
        'order_date': '2023-10-27',
        'status': 'draft',
        'items': [
            {
                'product_id': product_id,
                'quantity': 100,
                'unit_price': 50.00
            }
        ]
    }
    resp = await api_post('/api/purchase-orders', po_data)
    assert resp.status_code == 201
    po_id = resp.get_json()['data']['po_id']
    print(f"Purchase Order created: {po_id}")

    # Receive PO
    resp = await api_put(f'/api/purchase-orders/{po_id}', {'status': 'received'})
    assert resp.status_code == 200
    print("Purchase Order received.")

    # Verify Stock Increase
    resp = await api_get(f'/api/stock/lookup?product_id={product_id}&warehouse_id={warehouse_id}')
    assert resp.status_code == 200
    stock_data = resp.get_json()['data']
    assert stock_data['quantity_on_hand'] == 100
    print(f"Stock verified: {stock_data['quantity_on_hand']} (Expected 100)")

    # --- 6. Sales Flow ---
    print("\n--- Step 6: Sales Flow ---")

    # Create Customer
    resp = await api_post('/api/customers', {
        'customer_name': 'E2E Customer Ltd',
        'email': 'customer@e2e.com'
    })
    assert resp.status_code == 201
    customer_id = resp.get_json()['data']['customer_id']
    print(f"Customer created: {customer_id}")

    # Create Sales Order
    so_data = {
        'order_number': 'SO-E2E-001',
        'customer_id': customer_id,
        'warehouse_id': warehouse_id,
        'order_date': '2023-10-28',
        'status': 'pending',
        'items': [
            {
                'product_id': product_id,
                'quantity': 20,
                'unit_price': 150.00
            }
        ]
    }
    resp = await api_post('/api/sales-orders', so_data)
    assert resp.status_code == 201
    so_id = resp.get_json()['data']['order_id']
    print(f"Sales Order created: {so_id}")

    # Ship Sales Order
    resp = await api_put(f'/api/sales-orders/{so_id}', {'status': 'shipped'})
    assert resp.status_code == 200
    print("Sales Order shipped.")

    # Verify Stock Decrease
    resp = await api_get(f'/api/stock/lookup?product_id={product_id}&warehouse_id={warehouse_id}')
    stock_data = resp.get_json()['data']
    assert stock_data['quantity_on_hand'] == 80
    print(f"Stock verified: {stock_data['quantity_on_hand']} (Expected 80)")

    # --- 7. Manual Adjustment ---
    print("\n--- Step 7: Stock Adjustment ---")

    # Adjust stock
    adj_data = {
        'product_id': product_id,
        'warehouse_id': warehouse_id,
        'new_quantity': 85,
        'reason': 'physical_count',
        'notes': 'Found 5 extra units'
    }
    resp = await api_post('/api/inventory/adjustments', adj_data)
    assert resp.status_code == 201
    print("Stock manually adjusted.")

    # Verify Final Stock
    resp = await api_get(f'/api/stock/lookup?product_id={product_id}&warehouse_id={warehouse_id}')
    stock_data = resp.get_json()['data']
    assert stock_data['quantity_on_hand'] == 85
    print(f"Final Stock verified: {stock_data['quantity_on_hand']} (Expected 85)")

    print("\n--- End-to-End Test Completed Successfully ---")
