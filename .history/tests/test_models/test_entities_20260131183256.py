# Entity model tests - Category, Brand, Supplier, Product, Warehouse, Customer

import pytest

from app.modules.brands.models import Brand
from app.modules.categories.models import Category
from app.modules.customers.models import Customer
from app.modules.products.models import Product
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

    def test_category_to_dict(self, sample_category, app):
        """Test category serialization."""
        with app.app_context():
            data = sample_category.to_dict()
            assert 'category_id' in data
            assert 'category_name' in data
            assert 'is_active' in data


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

    def test_brand_unique_name(self, app, db_session, sample_brand):
        """Test brand name uniqueness."""
        with app.app_context():
            from sqlalchemy.exc import IntegrityError

            duplicate = Brand(brand_name=sample_brand.brand_name)
            db_session.add(duplicate)

            with pytest.raises(IntegrityError):
                db_session.commit()
            db_session.rollback()

    def test_brand_to_dict(self, sample_brand, app):
        """Test brand serialization."""
        with app.app_context():
            data = sample_brand.to_dict()
            assert data['brand_name'] == 'TechBrand'
            assert 'manufacturer_name' in data


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
                unit_price=50.00,
                category_id=sample_category.category_id,
                brand_id=sample_brand.brand_id
            )
            db_session.add(product)
            db_session.commit()

            assert product.product_id is not None
            assert product.category_id == sample_category.category_id
            assert product.brand_id == sample_brand.brand_id

    def test_product_unique_code(self, app, db_session, sample_product):
        """Test product code uniqueness."""
        with app.app_context():
            from sqlalchemy.exc import IntegrityError

            duplicate = Product(
                product_code=sample_product.product_code,
                product_name='Duplicate',
                unit_price=10.00
            )
            db_session.add(duplicate)

            with pytest.raises(IntegrityError):
                db_session.commit()
            db_session.rollback()

    def test_product_to_dict(self, sample_product, app):
        """Test product serialization."""
        with app.app_context():
            data = sample_product.to_dict()
            assert data['product_code'] == 'PROD001'
            assert data['unit_price'] == 99.99


class TestWarehouseModel:
    """Tests for Warehouse model."""

    def test_create_warehouse(self, app, db_session):
        """Test warehouse creation."""
        with app.app_context():
            warehouse = Warehouse(
                warehouse_name='New Warehouse',
                location='Suburb',
                capacity=5000
            )
            db_session.add(warehouse)
            db_session.commit()

            assert warehouse.warehouse_id is not None

    def test_warehouse_to_dict(self, sample_warehouse, app):
        """Test warehouse serialization."""
        with app.app_context():
            data = sample_warehouse.to_dict()
            assert data['warehouse_name'] == 'Main Warehouse'
            assert data['capacity'] == 10000


class TestCustomerModel:
    """Tests for Customer model."""

    def test_create_customer(self, app, db_session):
        """Test customer creation."""
        with app.app_context():
            customer = Customer(
                customer_name='New Customer',
                email='newcustomer@example.com'
            )
            db_session.add(customer)
            db_session.commit()

            assert customer.customer_id is not None

    def test_customer_to_dict(self, sample_customer, app):
        """Test customer serialization."""
        with app.app_context():
            data = sample_customer.to_dict()
            assert data['customer_name'] == 'Test Customer Inc.'
            assert data['contact_person'] == 'Jane Doe'
