# CRUD service tests

import pytest
from app.modules.categories.services import CategoryService
from app.modules.brands.services import BrandService
from app.modules.products.services import ProductService
from app.modules.warehouses.services import WarehouseService
from app.modules.suppliers.services import SupplierService
from app.modules.customers.services import CustomerService
from app.modules.stock.services import StockService


class TestCategoryService:
    """Tests for CategoryService."""

    def test_create_category(self, app, db_session):
        """Test category creation."""
        with app.app_context():
            category = CategoryService.create(
                category_name='Test Category',
                description='A test category'
            )
            assert category.category_id is not None

    def test_get_all_categories(self, app, db_session):
        """Test getting all categories."""
        with app.app_context():
            CategoryService.create(category_name='Cat1')
            CategoryService.create(category_name='Cat2')
            
            categories = CategoryService.get_all()
            assert len(categories) == 2

    def test_get_root_categories(self, app, db_session):
        """Test getting root categories."""
        with app.app_context():
            parent = CategoryService.create(category_name='Parent')
            CategoryService.create(
                category_name='Child',
                parent_category_id=parent.category_id
            )
            
            roots = CategoryService.get_root_categories()
            assert len(roots) == 1
            assert roots[0].category_name == 'Parent'

    def test_update_category(self, sample_category, app, db_session):
        """Test updating category."""
        with app.app_context():
            updated = CategoryService.update(
                sample_category,
                category_name='Updated Category'
            )
            assert updated.category_name == 'Updated Category'

    def test_delete_category(self, sample_category, app, db_session):
        """Test soft deleting category."""
        with app.app_context():
            CategoryService.delete(sample_category)
            assert sample_category.is_active is False


class TestBrandService:
    """Tests for BrandService."""

    def test_create_brand(self, app, db_session):
        """Test brand creation."""
        with app.app_context():
            brand = BrandService.create(
                brand_name='NewBrand',
                manufacturer_name='New Mfg'
            )
            assert brand.brand_id is not None

    def test_get_by_name(self, sample_brand, app):
        """Test getting brand by name."""
        with app.app_context():
            brand = BrandService.get_by_name('TechBrand')
            assert brand is not None
            assert brand.brand_id == sample_brand.brand_id


class TestProductService:
    """Tests for ProductService."""

    def test_create_product(self, app, db_session, sample_category, sample_brand):
        """Test product creation."""
        with app.app_context():
            product = ProductService.create(
                product_code='NEWPROD',
                product_name='New Product',
                unit_price=25.00,
                category_id=sample_category.category_id,
                brand_id=sample_brand.brand_id
            )
            assert product.product_id is not None

    def test_get_by_code(self, sample_product, app):
        """Test getting product by code."""
        with app.app_context():
            product = ProductService.get_by_code('PROD001')
            assert product is not None

    def test_search_products(self, sample_product, app, db_session):
        """Test searching products."""
        with app.app_context():
            results = ProductService.search('Test')
            assert len(results) >= 1

    def test_get_by_category(self, sample_product, app):
        """Test getting products by category."""
        with app.app_context():
            products = ProductService.get_by_category(sample_product.category_id)
            assert len(products) >= 1


class TestWarehouseService:
    """Tests for WarehouseService."""

    def test_create_warehouse(self, app, db_session):
        """Test warehouse creation."""
        with app.app_context():
            warehouse = WarehouseService.create(
                warehouse_name='New Warehouse',
                location='Suburb',
                capacity=3000
            )
            assert warehouse.warehouse_id is not None

    def test_update_warehouse(self, sample_warehouse, app, db_session):
        """Test updating warehouse."""
        with app.app_context():
            updated = WarehouseService.update(
                sample_warehouse,
                capacity=15000
            )
            assert updated.capacity == 15000


class TestSupplierService:
    """Tests for SupplierService."""

    def test_create_supplier(self, app, db_session):
        """Test supplier creation."""
        with app.app_context():
            supplier = SupplierService.create(
                supplier_name='New Supplier',
                email='new@supplier.com'
            )
            assert supplier.supplier_id is not None

    def test_search_suppliers(self, sample_supplier, app):
        """Test searching suppliers."""
        with app.app_context():
            results = SupplierService.search('Tech')
            assert len(results) >= 1


class TestCustomerService:
    """Tests for CustomerService."""

    def test_create_customer(self, app, db_session):
        """Test customer creation."""
        with app.app_context():
            customer = CustomerService.create(
                customer_name='New Customer',
                email='new@customer.com'
            )
            assert customer.customer_id is not None

    def test_search_customers(self, sample_customer, app):
        """Test searching customers."""
        with app.app_context():
            results = CustomerService.search('Test')
            assert len(results) >= 1


class TestStockService:
    """Tests for StockService."""

    def test_create_stock(self, app, db_session, sample_product, sample_warehouse):
        """Test stock creation."""
        with app.app_context():
            stock = StockService.create(
                product_id=sample_product.product_id,
                warehouse_id=sample_warehouse.warehouse_id,
                quantity_on_hand=50
            )
            assert stock.stock_id is not None

    def test_get_by_product_and_warehouse(self, sample_stock, app):
        """Test getting stock by product and warehouse."""
        with app.app_context():
            stock = StockService.get_by_product_and_warehouse(
                sample_stock.product_id,
                sample_stock.warehouse_id
            )
            assert stock is not None

    def test_adjust_quantity(self, sample_stock, app, db_session):
        """Test adjusting stock quantity."""
        with app.app_context():
            original = sample_stock.quantity_on_hand  # 100
            StockService.adjust_quantity(sample_stock, 25)
            assert sample_stock.quantity_on_hand == original + 25
            
            StockService.adjust_quantity(sample_stock, -50)
            assert sample_stock.quantity_on_hand == original - 25

    def test_reserve_stock(self, sample_stock, app, db_session):
        """Test reserving stock."""
        with app.app_context():
            original_reserved = sample_stock.quantity_reserved  # 10
            
            success = StockService.reserve_stock(sample_stock, 20)
            assert success is True
            assert sample_stock.quantity_reserved == original_reserved + 20
            
            # Try to reserve more than available (100 - 30 = 70)
            success = StockService.reserve_stock(sample_stock, 100)
            assert success is False

    def test_release_reservation(self, sample_stock, app, db_session):
        """Test releasing stock reservation."""
        with app.app_context():
            original_reserved = sample_stock.quantity_reserved  # 10
            
            StockService.release_reservation(sample_stock, 5)
            assert sample_stock.quantity_reserved == original_reserved - 5

    def test_get_or_create(self, app, db_session, sample_product, sample_warehouse):
        """Test get_or_create functionality."""
        with app.app_context():
            # Create new stock
            stock1 = StockService.get_or_create(
                sample_product.product_id,
                sample_warehouse.warehouse_id
            )
            assert stock1.stock_id is not None
            
            # Get existing stock
            stock2 = StockService.get_or_create(
                sample_product.product_id,
                sample_warehouse.warehouse_id
            )
            assert stock2.stock_id == stock1.stock_id
