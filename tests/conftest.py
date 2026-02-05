# pytest configuration and fixtures (Async)

import pytest
import asyncio
from datetime import date
from decimal import Decimal

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.modules.auth.models import User
from app.modules.categories.models import Category
from app.modules.brands.models import Brand
from app.modules.suppliers.models import Supplier
from app.modules.products.models import Product
from app.modules.warehouses.models import Warehouse
from app.modules.stock.models import Stock

@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='session')
async def app():
    """Create application for testing."""
    app = create_app(TestConfig)

    # Create tables
    with app.app_context():
        async with db.engine.begin() as conn:
            await conn.run_sync(db.metadata.create_all)

        yield app

        async with db.engine.begin() as conn:
            await conn.run_sync(db.metadata.drop_all)

@pytest.fixture(scope='function')
async def db_session(app):
    """Create a fresh database session for each test."""
    with app.app_context():
        # Clean up tables
        async with db.engine.begin() as conn:
             for table in reversed(db.metadata.sorted_tables):
                 await conn.execute(table.delete())

        async with db.session() as session:
            yield session
            await session.rollback()
            await session.close()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
async def test_user(app, db_session):
    """Create a test user."""
    user = User(
        username='testuser',
        first_name='Test',
        last_name='User',
        email='test@example.com',
        role='admin'
    )
    user.set_password('testpass123')
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def auth_client(client, test_user):
    """Create authenticated test client."""
    # Run login in a thread to avoid blocking the loop
    response = await asyncio.to_thread(
        client.post,
        '/api/auth/login',
        json={'username': 'testuser', 'password': 'testpass123'}
    )

    assert response.status_code == 200
    token = response.get_json()['data']['access_token']

    class AuthClientWrapper:
        def __init__(self, client, token):
            self.client = client
            self.headers = {'Authorization': f'Bearer {token}'}

        async def get(self, *args, **kwargs):
            kwargs.setdefault('headers', {}).update(self.headers)
            return await asyncio.to_thread(self.client.get, *args, **kwargs)

        async def post(self, *args, **kwargs):
            kwargs.setdefault('headers', {}).update(self.headers)
            return await asyncio.to_thread(self.client.post, *args, **kwargs)

        async def put(self, *args, **kwargs):
            kwargs.setdefault('headers', {}).update(self.headers)
            return await asyncio.to_thread(self.client.put, *args, **kwargs)

        async def delete(self, *args, **kwargs):
            kwargs.setdefault('headers', {}).update(self.headers)
            return await asyncio.to_thread(self.client.delete, *args, **kwargs)

    return AuthClientWrapper(client, token)

# --- Catalog Fixtures ---

@pytest.fixture
async def sample_category(app, db_session):
    """Create a sample category."""
    category = Category(
        category_name='Electronics',
        description='Electronic devices'
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category

@pytest.fixture
async def sample_brand(app, db_session):
    """Create a sample brand."""
    brand = Brand(
        brand_name='TechBrand',
        manufacturer_name='Tech Inc.'
    )
    db_session.add(brand)
    await db_session.commit()
    await db_session.refresh(brand)
    return brand

@pytest.fixture
async def sample_supplier(app, db_session):
    """Create a sample supplier."""
    supplier = Supplier(
        supplier_name='Tech Supplies Co.',
        email='supplier@tech.com'
    )
    db_session.add(supplier)
    await db_session.commit()
    await db_session.refresh(supplier)
    return supplier

@pytest.fixture
async def sample_product(app, db_session, sample_category, sample_brand):
    """Create a sample product."""
    product = Product(
        product_code='PROD001',
        product_name='Test Product',
        description='A test product',
        category_id=sample_category.category_id,
        brand_id=sample_brand.brand_id,
        unit_price=Decimal('99.99'),
        cost_price=Decimal('49.99'),
        reorder_level=10,
        min_stock_level=5,
        unit_of_measure='pcs',
        barcode='1234567890123',
        sku='SKU-PROD001',
        weight=Decimal('1.5'),
        dimensions='10x5x3 cm'
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product

# --- Inventory Fixtures (needed for product tests involving stock) ---

@pytest.fixture
async def sample_warehouse(app, db_session):
    """Create a sample warehouse."""
    warehouse = Warehouse(
        warehouse_name='Main Warehouse',
        location='Downtown',
        address='456 Warehouse Ave',
        capacity=10000
    )
    db_session.add(warehouse)
    await db_session.commit()
    await db_session.refresh(warehouse)
    return warehouse

@pytest.fixture
async def sample_stock(app, db_session, sample_product, sample_warehouse):
    """Create a sample stock entry."""
    stock = Stock(
        product_id=sample_product.product_id,
        warehouse_id=sample_warehouse.warehouse_id,
        quantity_on_hand=100,
        quantity_reserved=10
    )
    db_session.add(stock)
    await db_session.commit()
    await db_session.refresh(stock)
    return stock
