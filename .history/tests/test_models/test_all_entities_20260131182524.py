# Entity model tests - Category, Brand, Supplier, Product, Warehouse, Customer, Stock

from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.modules.brands.models import Brand
from app.modules.categories.models import Category
from app.modules.customers.models import Customer
from app.modules.products.models import Product
from app.modules.stock.models import Stock
from app.modules.suppliers.models import Supplier
from app.modules.warehouses.models import Warehouse


class TestCategoryModel:
    """Tests for Category model."""

    def test_create_category(self, app, db_session):
        """Test category creation."""
        with app.app_context():
            category = Category(
                category_name='Test Category',
                description='A test category'
            )
            db_session.add(category)
            db_session.commit()

            assert category.category_id is not None
            assert category.is_active is True
            assert category.created_at is not None

    def test_category_hierarchy(self, app, db_session):
        """Test parent-child category relationship."""
        with app.app_context():
            parent = Category(category_name='Parent Category')
            db_session.add(parent)
            db_session.commit()

            child = Category(
                category_name='Child Category',
                parent_category_id=parent.category_id
            )
            db_session.add(child)
            db_session.commit()

            assert child.parent == parent
            assert child in parent.subcategories

    def test_category_deactivation(self, app, db_session):
        """Test category deactivation."""
        with app.app_context():
            category = Category(category_name='To Deactivate')
            db_session.add(category)
            db_session.commit()

            category.is_active = False
            db_session.commit()

            assert category.is_active is False

    def test_category_to_dict(self, sample_category, app):
        """Test category serialization."""
        with app.app_context():
            data = sample_category.to_dict()
            assert 'category_id' in data
            assert 'category_name' in data
            assert 'is_active' in data
            assert data['category_name'] == 'Electronics'


class TestBrandModel:
    """Tests for Brand model."""

    def test_create_brand(self, app, db_session):
        """Test brand creation."""
        with app.app_context():
            brand = Brand(
                brand_name='New Brand',
                manufacturer_name='New Manufacturer'
            )
            db_session.add(brand)
            db_session.commit()

            assert brand.brand_id is not None
            assert brand.is_active is True
            assert brand.created_at is not None

    def test_brand_unique_name(self, app, db_session, sample_brand):
        """Test brand name uniqueness."""
        with app.app_context():
            duplicate = Brand(brand_name=sample_brand.brand_name)
            db_session.add(duplicate)

            with pytest.raises(IntegrityError):
                db_session.commit()
            db_session.rollback()

    def test_brand_with_description(self, app, db_session):
        """Test brand with description."""
        with app.app_context():
            brand = Brand(
                brand_name='Descriptive Brand',
                manufacturer_name='Manufacturer',
                description='A detailed description'
            )
            db_session.add(brand)
            db_session.commit()

            assert brand.description == 'A detailed description'

    def test_brand_to_dict(self, sample_brand, app):
        """Test brand serialization."""
        with app.app_context():
            data = sample_brand.to_dict()
            assert data['brand_name'] == 'TechBrand'
            assert 'manufacturer_name' in data
            assert 'is_active' in data


class TestSupplierModel:
    """Tests for Supplier model."""

    def test_create_supplier(self, app, db_session):
        """Test supplier creation."""
        with app.app_context():
            supplier = Supplier(
                supplier_name='New Supplier',
                contact_person='Contact Person',
                email='supplier@example.com'
            )
            db_session.add(supplier)
            db_session.commit()

            assert supplier.supplier_id is not None
            assert supplier.is_active is True

    def test_supplier_default_country(self, app, db_session):
        """Test supplier default country."""
        with app.app_context():
            supplier = Supplier(
                supplier_name='US Supplier',
                contact_person='John'
            )
            db_session.add(supplier)
            db_session.commit()

            assert supplier.country == 'USA'

    def test_supplier_full_details(self, app, db_session):
        """Test supplier with all details."""
        with app.app_context():
            supplier = Supplier(
                supplier_name='Complete Supplier',
                contact_person='Jane Doe',
                email='jane@supplier.com',
                phone='+1234567890',
                address='123 Main St',
                city='Boston',
                state='MA',
                country='USA',
                postal_code='02101',
                tax_id='TAX-123',
                payment_terms='Net 30'
            )
            db_session.add(supplier)
            db_session.commit()

            assert supplier.payment_terms == 'Net 30'
            assert supplier.tax_id == 'TAX-123'

    def test_supplier_to_dict(self, sample_supplier, app):
        """Test supplier serialization."""
        with app.app_context():
            data = sample_supplier.to_dict()
            assert data['supplier_name'] == 'Tech Supplies Co.'
            assert data['contact_person'] == 'John Smith'


class TestProductModel:
    """Tests for Product model."""

    def test_create_product(self, app, db_session, sample_category, sample_brand):
        """Test product creation."""
        with app.app_context():
            product = Product(
                product_code='NEW001',
                product_name='New Product',
                unit_price=Decimal('50.00'),
                category_id=sample_category.category_id,
                brand_id=sample_brand.brand_id
            )
            db_session.add(product)
            db_session.commit()

            assert product.product_id is not None
            assert product.category_id == sample_category.category_id
            assert product.brand_id == sample_brand.brand_id
            assert product.is_active is True

    def test_product_unique_code(self, app, db_session, sample_product):
        """Test product code uniqueness."""
        with app.app_context():
            duplicate = Product(
                product_code=sample_product.product_code,
                product_name='Duplicate',
                unit_price=Decimal('10.00')
            )
            db_session.add(duplicate)

            with pytest.raises(IntegrityError):
                db_session.commit()
            db_session.rollback()

    def test_product_with_barcode_sku(self, app, db_session):
        """Test product with barcode and SKU."""
        with app.app_context():
            product = Product(
                product_code='BARSKU001',
                product_name='Product with Codes',
                unit_price=Decimal('25.00'),
                barcode='1234567890123',
                sku='SKU-TEST-001'
            )
            db_session.add(product)
            db_session.commit()

            assert product.barcode == '1234567890123'
            assert product.sku == 'SKU-TEST-001'

    def test_product_pricing(self, app, db_session):
        """Test product with cost and unit price."""
        with app.app_context():
            product = Product(
                product_code='PRICE001',
                product_name='Priced Product',
                unit_price=Decimal('99.99'),
                cost_price=Decimal('49.99')
            )
            db_session.add(product)
            db_session.commit()

            profit_margin = product.unit_price - product.cost_price
            assert profit_margin == Decimal('50.00')

    def test_product_stock_levels(self, app, db_session):
        """Test product stock level settings."""
        with app.app_context():
            product = Product(
                product_code='STOCK001',
                product_name='Stock Product',
                unit_price=Decimal('30.00'),
                reorder_level=10,
                min_stock_level=5,
                max_stock_level=100
            )
            db_session.add(product)
            db_session.commit()

            assert product.reorder_level == 10
            assert product.min_stock_level == 5
            assert product.max_stock_level == 100

    def test_product_to_dict(self, sample_product, app):
        """Test product serialization."""
        with app.app_context():
            data = sample_product.to_dict()
            assert data['product_code'] == 'PROD001'
            assert data['product_name'] == 'Test Product'


class TestWarehouseModel:
    """Tests for Warehouse model."""

    def test_create_warehouse(self, app, db_session):
        """Test warehouse creation."""
        with app.app_context():
            warehouse = Warehouse(
                warehouse_name='Test Warehouse',
                location='Downtown',
                city='Chicago',
                capacity=5000
            )
            db_session.add(warehouse)
            db_session.commit()

            assert warehouse.warehouse_id is not None
            assert warehouse.is_active is True

    def test_warehouse_default_country(self, app, db_session):
        """Test warehouse default country."""
        with app.app_context():
            warehouse = Warehouse(
                warehouse_name='US Warehouse',
                location='Location',
                city='Miami'
            )
            db_session.add(warehouse)
            db_session.commit()

            assert warehouse.country == 'USA'

    def test_warehouse_full_address(self, app, db_session):
        """Test warehouse with complete address."""
        with app.app_context():
            warehouse = Warehouse(
                warehouse_name='Complete Warehouse',
                location='Industrial Park',
                address='789 Warehouse Blvd',
                city='Dallas',
                state='TX',
                country='USA',
                postal_code='75201',
                capacity=20000
            )
            db_session.add(warehouse)
            db_session.commit()

            assert warehouse.state == 'TX'
            assert warehouse.postal_code == '75201'

    def test_warehouse_to_dict(self, sample_warehouse, app):
        """Test warehouse serialization."""
        with app.app_context():
            data = sample_warehouse.to_dict()
            assert data['warehouse_name'] == 'Main Warehouse'


class TestCustomerModel:
    """Tests for Customer model."""

    def test_create_customer(self, app, db_session):
        """Test customer creation."""
        with app.app_context():
            customer = Customer(
                customer_name='New Customer',
                contact_person='Contact',
                email='customer@example.com'
            )
            db_session.add(customer)
            db_session.commit()

            assert customer.customer_id is not None
            assert customer.is_active is True

    def test_customer_with_credit_limit(self, app, db_session):
        """Test customer with credit limit."""
        with app.app_context():
            customer = Customer(
                customer_name='Credit Customer',
                contact_person='Manager',
                email='credit@example.com',
                credit_limit=Decimal('100000.00')
            )
            db_session.add(customer)
            db_session.commit()

            assert customer.credit_limit == Decimal('100000.00')

    def test_customer_full_details(self, app, db_session):
        """Test customer with all details."""
        with app.app_context():
            customer = Customer(
                customer_name='Complete Customer Inc.',
                contact_person='Jane Manager',
                email='jane@completecustomer.com',
                phone='+1234567890',
                address='456 Business Ave',
                city='San Francisco',
                state='CA',
                country='USA',
                postal_code='94102',
                tax_id='TAX-456',
                credit_limit=Decimal('50000.00')
            )
            db_session.add(customer)
            db_session.commit()

            assert customer.tax_id == 'TAX-456'
            assert customer.state == 'CA'

    def test_customer_to_dict(self, sample_customer, app):
        """Test customer serialization."""
        with app.app_context():
            data = sample_customer.to_dict()
            assert data['customer_name'] == 'Test Customer Inc.'


class TestStockModel:
    """Tests for Stock model."""

    def test_create_stock(self, app, db_session, sample_product, sample_warehouse):
        """Test stock creation."""
        with app.app_context():
            stock = Stock(
                product_id=sample_product.product_id,
                warehouse_id=sample_warehouse.warehouse_id,
                quantity_on_hand=100,
                quantity_reserved=0
            )
            db_session.add(stock)
            db_session.commit()

            assert stock.stock_id is not None
            assert stock.quantity_on_hand == 100

    def test_stock_available_quantity(self, app, db_session, sample_product, sample_warehouse):
        """Test stock available quantity calculation."""
        with app.app_context():
            stock = Stock(
                product_id=sample_product.product_id,
                warehouse_id=sample_warehouse.warehouse_id,
                quantity_on_hand=100,
                quantity_reserved=25
            )
            db_session.add(stock)
            db_session.commit()

            # Check if quantity_available is calculated correctly
            available = stock.quantity_on_hand - stock.quantity_reserved
            assert available == 75

    def test_stock_unique_constraint(self, app, db_session, sample_stock):
        """Test stock unique constraint (product + warehouse)."""
        with app.app_context():
            duplicate = Stock(
                product_id=sample_stock.product_id,
                warehouse_id=sample_stock.warehouse_id,
                quantity_on_hand=50
            )
            db_session.add(duplicate)

            with pytest.raises(IntegrityError):
                db_session.commit()
            db_session.rollback()

    def test_stock_to_dict(self, sample_stock, app):
        """Test stock serialization."""
        with app.app_context():
            data = sample_stock.to_dict()
            assert 'stock_id' in data
            assert 'product_id' in data
            assert 'warehouse_id' in data
            assert 'quantity_on_hand' in data
