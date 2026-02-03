# pytest configuration and fixtures

from datetime import date, datetime
from decimal import Decimal

import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.modules.auth.models import User
from app.modules.brands.models import Brand
from app.modules.categories.models import Category
from app.modules.customers.models import Customer
from app.modules.inventory.models import InventoryTransaction, StockAdjustment
from app.modules.products.models import Product
from app.modules.purchase_orders.models import PurchaseOrder, PurchaseOrderItem
from app.modules.sales_orders.models import SalesOrder, SalesOrderItem
from app.modules.stock.models import Stock
from app.modules.suppliers.models import Supplier
from app.modules.warehouses.models import Warehouse


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def db_session(app):
    """Create a fresh database session for each test."""
    with app.app_context():
        # Clear all tables
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

        yield db.session

        db.session.rollback()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def test_user(app, db_session):
    """Create a test user."""
    with app.app_context():
        user = User(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            role='admin'
        )
        user.set_password('testpass123')
        db_session.add(user)
        db_session.commit()

        # Refresh to get the ID
        db_session.refresh(user)
        return user


@pytest.fixture
def staff_user(app, db_session):
    """Create a staff user with limited permissions."""
    with app.app_context():
        user = User(
            username='staffuser',
            first_name='Staff',
            last_name='User',
            email='staff@example.com',
            role='staff'
        )
        user.set_password('staffpass123')
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user


@pytest.fixture
def auth_client(client, test_user, app):
    """Create authenticated test client."""
    with app.app_context():
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        assert response.status_code == 200
    return client


@pytest.fixture
def sample_category(app, db_session):
    """Create a sample category."""
    with app.app_context():
        category = Category(
            category_name='Electronics',
            description='Electronic devices and accessories'
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category


@pytest.fixture
def sample_brand(app, db_session):
    """Create a sample brand."""
    with app.app_context():
        brand = Brand(
            brand_name='TechBrand',
            manufacturer_name='Tech Manufacturing Inc.',
            description='Quality tech products'
        )
        db_session.add(brand)
        db_session.commit()
        db_session.refresh(brand)
        return brand


@pytest.fixture
def sample_supplier(app, db_session):
    """Create a sample supplier."""
    with app.app_context():
        supplier = Supplier(
            supplier_name='Tech Supplies Co.',
            contact_person='John Smith',
            email='john@techsupplies.com',
            phone='123-456-7890',
            address='123 Tech Street',
            city='New York',
            state='NY',
            country='USA',
            postal_code='10001',
            tax_id='TAX-123456',
            payment_terms='Net 30'
        )
        db_session.add(supplier)
        db_session.commit()
        db_session.refresh(supplier)
        return supplier


@pytest.fixture
def sample_warehouse(app, db_session):
    """Create a sample warehouse."""
    with app.app_context():
        warehouse = Warehouse(
            warehouse_name='Main Warehouse',
            location='Downtown',
            address='456 Warehouse Ave',
            city='New York',
            state='NY',
            country='USA',
            postal_code='10002',
            manager_name='Bob Manager',
            phone='555-123-4567',
            capacity=10000
        )
        db_session.add(warehouse)
        db_session.commit()
        db_session.refresh(warehouse)
        return warehouse


@pytest.fixture
def sample_product(app, db_session, sample_category, sample_brand):
    """Create a sample product."""
    with app.app_context():
        product = Product(
            product_code='PROD001',
            product_name='Test Product',
            description='A test product',
            category_id=sample_category.category_id,
            brand_id=sample_brand.brand_id,
            unit_price=99.99,
            cost_price=49.99,
            reorder_level=10,
            min_stock_level=5,
            max_stock_level=200,
            unit_of_measure='pcs',
            barcode='1234567890123',
            sku='SKU-PROD001',
            weight=1.5,
            dimensions='10x5x3 cm'
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        return product


@pytest.fixture
def sample_stock(app, db_session, sample_product, sample_warehouse):
    """Create a sample stock entry."""
    with app.app_context():
        stock = Stock(
            product_id=sample_product.product_id,
            warehouse_id=sample_warehouse.warehouse_id,
            quantity_on_hand=100,
            quantity_reserved=10
        )
        db_session.add(stock)
        db_session.commit()
        db_session.refresh(stock)
        return stock


@pytest.fixture
def sample_customer(app, db_session):
    """Create a sample customer."""
    with app.app_context():
        customer = Customer(
            customer_name='Test Customer Inc.',
            contact_person='Jane Doe',
            email='jane@testcustomer.com',
            phone='987-654-3210',
            address='789 Customer Blvd',
            city='Los Angeles',
            state='CA',
            country='USA',
            postal_code='90001',
            tax_id='CUST-TAX-789',
            credit_limit=50000.00
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        return customer


@pytest.fixture
def sample_purchase_order(app, db_session, sample_supplier, sample_warehouse, test_user):
    """Create a sample purchase order."""
    with app.app_context():
        po = PurchaseOrder(
            po_number='PO-TEST-001',
            supplier_id=sample_supplier.supplier_id,
            warehouse_id=sample_warehouse.warehouse_id,
            order_date=date.today(),
            status='pending',
            created_by=test_user.user_id
        )
        db_session.add(po)
        db_session.commit()
        db_session.refresh(po)
        return po


@pytest.fixture
def sample_sales_order(app, db_session, sample_customer, sample_warehouse, test_user):
    """Create a sample sales order."""
    with app.app_context():
        so = SalesOrder(
            order_number='SO-TEST-001',
            customer_id=sample_customer.customer_id,
            warehouse_id=sample_warehouse.warehouse_id,
            order_date=date.today(),
            status='pending',
            payment_status='unpaid',
            created_by=test_user.user_id
        )
        db_session.add(so)
        db_session.commit()
        db_session.refresh(so)
        return so


@pytest.fixture
def sample_po_with_items(app, db_session, sample_purchase_order, sample_product):
    """Create a purchase order with items."""
    with app.app_context():
        # Re-attach the purchase order to current session
        po = db_session.merge(sample_purchase_order)
        item = PurchaseOrderItem(
            po_id=po.po_id,
            product_id=sample_product.product_id,
            quantity=50,
            unit_price=Decimal('49.99'),
            received_quantity=0
        )
        db_session.add(item)
        db_session.commit()
        db_session.refresh(po)
        return po


@pytest.fixture
def sample_so_with_items(app, db_session, sample_sales_order, sample_product):
    """Create a sales order with items."""
    with app.app_context():
        # Re-attach the sales order to current session
        so = db_session.merge(sample_sales_order)
        item = SalesOrderItem(
            order_id=so.order_id,
            product_id=sample_product.product_id,
            quantity=10,
            unit_price=Decimal('99.99'),
            discount=Decimal('0.00')
        )
        db_session.add(item)
        db_session.commit()
        db_session.refresh(so)
        return so


@pytest.fixture
def sample_inventory_transaction(app, db_session, sample_product, sample_warehouse):
    """Create a sample inventory transaction."""
    with app.app_context():
        transaction = InventoryTransaction(
            product_id=sample_product.product_id,
            warehouse_id=sample_warehouse.warehouse_id,
            transaction_type='purchase',
            quantity=100,
            reference_type='purchase_order',
            reference_id=1
        )
        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)
        return transaction


@pytest.fixture
def sample_stock_adjustment(app, db_session, sample_product, sample_warehouse, test_user):
    """Create a sample stock adjustment."""
    with app.app_context():
        adjustment = StockAdjustment(
            product_id=sample_product.product_id,
            warehouse_id=sample_warehouse.warehouse_id,
            old_quantity=100,
            new_quantity=95,
            reason='damage',
            notes='Damaged during handling',
            adjusted_by=test_user.user_id
        )
        db_session.add(adjustment)
        db_session.commit()
        db_session.refresh(adjustment)
        return adjustment

