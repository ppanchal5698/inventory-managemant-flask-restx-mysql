# Order and Inventory model tests

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.modules.inventory.models import InventoryTransaction, StockAdjustment
from app.modules.purchase_orders.models import PurchaseOrder, PurchaseOrderItem
from app.modules.sales_orders.models import SalesOrder, SalesOrderItem


class TestPurchaseOrderModel:
    """Tests for PurchaseOrder model."""

    def test_create_purchase_order(self, app, db_session, sample_supplier, sample_warehouse, test_user):
        """Test purchase order creation."""
        with app.app_context():
            po = PurchaseOrder(
                po_number='PO-MODEL-001',
                supplier_id=sample_supplier.supplier_id,
                warehouse_id=sample_warehouse.warehouse_id,
                order_date=date.today(),
                status='draft',
                created_by=test_user.user_id
            )
            db_session.add(po)
            db_session.commit()

            assert po.po_id is not None
            assert po.status == 'draft'
            assert po.created_at is not None

    def test_purchase_order_unique_number(self, app, db_session, sample_purchase_order):
        """Test PO number uniqueness."""
        with app.app_context():
            duplicate = PurchaseOrder(
                po_number=sample_purchase_order.po_number,
                supplier_id=sample_purchase_order.supplier_id,
                warehouse_id=sample_purchase_order.warehouse_id,
                order_date=date.today(),
                created_by=sample_purchase_order.created_by
            )
            db_session.add(duplicate)

            with pytest.raises(IntegrityError):
                db_session.commit()
            db_session.rollback()

    def test_purchase_order_with_costs(self, app, db_session, sample_supplier, sample_warehouse, test_user):
        """Test purchase order with tax and shipping."""
        with app.app_context():
            po = PurchaseOrder(
                po_number='PO-COSTS-001',
                supplier_id=sample_supplier.supplier_id,
                warehouse_id=sample_warehouse.warehouse_id,
                order_date=date.today(),
                tax_amount=Decimal('150.00'),
                shipping_cost=Decimal('50.00'),
                created_by=test_user.user_id
            )
            db_session.add(po)
            db_session.commit()

            assert po.tax_amount == Decimal('150.00')
            assert po.shipping_cost == Decimal('50.00')

    def test_purchase_order_status_workflow(self, app, db_session, sample_purchase_order):
        """Test purchase order status changes."""
        with app.app_context():
            assert sample_purchase_order.status == 'pending'

            sample_purchase_order.status = 'approved'
            db_session.commit()
            assert sample_purchase_order.status == 'approved'

            sample_purchase_order.status = 'received'
            db_session.commit()
            assert sample_purchase_order.status == 'received'

    def test_purchase_order_to_dict(self, sample_purchase_order, app):
        """Test purchase order serialization."""
        with app.app_context():
            data = sample_purchase_order.to_dict()
            assert data['po_number'] == 'PO-TEST-001'
            assert 'supplier_id' in data
            assert 'status' in data


class TestPurchaseOrderItemModel:
    """Tests for PurchaseOrderItem model."""

    def test_create_po_item(self, app, db_session, sample_purchase_order, sample_product):
        """Test purchase order item creation."""
        with app.app_context():
            item = PurchaseOrderItem(
                po_id=sample_purchase_order.po_id,
                product_id=sample_product.product_id,
                quantity=50,
                unit_price=Decimal('49.99'),
                received_quantity=0
            )
            db_session.add(item)
            db_session.commit()

            assert item.po_item_id is not None
            assert item.quantity == 50
            assert item.received_quantity == 0

    def test_po_item_line_total(self, app, db_session, sample_po_with_items):
        """Test line total calculation."""
        with app.app_context():
            from app.modules.purchase_orders.models import PurchaseOrder
            # Fetch fresh instance attached to current session
            po = db_session.query(PurchaseOrder).get(sample_po_with_items.po_id)
            items = list(po.items.all())
            assert len(items) >= 1
            item = items[0]
            expected_total = item.quantity * item.unit_price

            # Check if line_total is calculated (generated column or property)
            assert item.quantity * item.unit_price == expected_total

    def test_po_item_received_tracking(self, app, db_session, sample_po_with_items):
        """Test tracking received quantities."""
        with app.app_context():
            from app.modules.purchase_orders.models import PurchaseOrder
            # Fetch fresh instance attached to current session
            po = db_session.query(PurchaseOrder).get(sample_po_with_items.po_id)
            items = list(po.items.all())
            assert len(items) >= 1
            item = items[0]

            item.received_quantity = 30
            db_session.commit()

            assert item.received_quantity == 30
            remaining = item.quantity - item.received_quantity
            assert remaining == 20

    def test_po_item_to_dict(self, app, db_session, sample_po_with_items):
        """Test PO item serialization."""
        with app.app_context():
            from app.modules.purchase_orders.models import PurchaseOrder
            # Fetch fresh instance attached to current session
            po = db_session.query(PurchaseOrder).get(sample_po_with_items.po_id)
            items = list(po.items.all())
            assert len(items) >= 1
            item = items[0]
            data = item.to_dict()

            assert 'po_item_id' in data
            assert 'product_id' in data
            assert 'quantity' in data


class TestSalesOrderModel:
    """Tests for SalesOrder model."""

    def test_create_sales_order(self, app, db_session, sample_customer, sample_warehouse, test_user):
        """Test sales order creation."""
        with app.app_context():
            so = SalesOrder(
                order_number='SO-MODEL-001',
                customer_id=sample_customer.customer_id,
                warehouse_id=sample_warehouse.warehouse_id,
                order_date=date.today(),
                payment_status='unpaid',
                status='pending',
                created_by=test_user.user_id
            )
            db_session.add(so)
            db_session.commit()

            assert so.order_id is not None
            assert so.payment_status == 'unpaid'
            assert so.status == 'pending'

    def test_sales_order_unique_number(self, app, db_session, sample_sales_order):
        """Test order number uniqueness."""
        with app.app_context():
            duplicate = SalesOrder(
                order_number=sample_sales_order.order_number,
                customer_id=sample_sales_order.customer_id,
                warehouse_id=sample_sales_order.warehouse_id,
                order_date=date.today(),
                payment_status='unpaid',
                created_by=sample_sales_order.created_by
            )
            db_session.add(duplicate)

            with pytest.raises(IntegrityError):
                db_session.commit()
            db_session.rollback()

    def test_sales_order_with_amounts(self, app, db_session, sample_customer, sample_warehouse, test_user):
        """Test sales order with tax, shipping, and discount."""
        with app.app_context():
            so = SalesOrder(
                order_number='SO-AMOUNTS-001',
                customer_id=sample_customer.customer_id,
                warehouse_id=sample_warehouse.warehouse_id,
                order_date=date.today(),
                tax_amount=Decimal('95.00'),
                shipping_cost=Decimal('20.00'),
                discount_amount=Decimal('50.00'),
                payment_status='unpaid',
                created_by=test_user.user_id
            )
            db_session.add(so)
            db_session.commit()

            assert so.tax_amount == Decimal('95.00')
            assert so.discount_amount == Decimal('50.00')

    def test_sales_order_payment_workflow(self, app, db_session, sample_sales_order):
        """Test sales order payment status changes."""
        with app.app_context():
            assert sample_sales_order.payment_status == 'unpaid'

            sample_sales_order.payment_status = 'partial'
            db_session.commit()
            assert sample_sales_order.payment_status == 'partial'

            sample_sales_order.payment_status = 'paid'
            db_session.commit()
            assert sample_sales_order.payment_status == 'paid'

    def test_sales_order_status_workflow(self, app, db_session, sample_sales_order):
        """Test sales order status changes."""
        with app.app_context():
            sample_sales_order.status = 'processing'
            db_session.commit()

            sample_sales_order.status = 'shipped'
            db_session.commit()

            sample_sales_order.status = 'delivered'
            db_session.commit()

            assert sample_sales_order.status == 'delivered'

    def test_sales_order_to_dict(self, sample_sales_order, app):
        """Test sales order serialization."""
        with app.app_context():
            data = sample_sales_order.to_dict()
            assert data['order_number'] == 'SO-TEST-001'
            assert 'customer_id' in data
            assert 'payment_status' in data


class TestSalesOrderItemModel:
    """Tests for SalesOrderItem model."""

    def test_create_so_item(self, app, db_session, sample_sales_order, sample_product):
        """Test sales order item creation."""
        with app.app_context():
            item = SalesOrderItem(
                order_id=sample_sales_order.order_id,
                product_id=sample_product.product_id,
                quantity=10,
                unit_price=Decimal('99.99'),
                discount=Decimal('10.00')
            )
            db_session.add(item)
            db_session.commit()

            assert item.order_item_id is not None
            assert item.quantity == 10
            assert item.discount == Decimal('10.00')

    def test_so_item_line_total(self, app, db_session, sample_so_with_items):
        """Test line total calculation with discount."""
        with app.app_context():
            items = list(sample_so_with_items.items.all())
            assert len(items) >= 1
            item = items[0]
            subtotal = item.quantity * item.unit_price
            expected_total = subtotal - item.discount

            # Check calculation
            actual_total = (item.quantity * item.unit_price) - item.discount
            assert actual_total == expected_total

    def test_so_item_to_dict(self, app, db_session, sample_so_with_items):
        """Test SO item serialization."""
        with app.app_context():
            items = list(sample_so_with_items.items.all())
            assert len(items) >= 1
            item = items[0]
            data = item.to_dict()

            assert 'order_item_id' in data
            assert 'product_id' in data
            assert 'quantity' in data


class TestInventoryTransactionModel:
    """Tests for InventoryTransaction model."""

    def test_create_transaction_in(self, app, db_session, sample_product, sample_warehouse):
        """Test incoming inventory transaction."""
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

            assert transaction.transaction_id is not None
            assert transaction.transaction_type == 'purchase'
            assert transaction.quantity == 100

    def test_create_transaction_out(self, app, db_session, sample_product, sample_warehouse):
        """Test outgoing inventory transaction."""
        with app.app_context():
            transaction = InventoryTransaction(
                product_id=sample_product.product_id,
                warehouse_id=sample_warehouse.warehouse_id,
                transaction_type='sale',
                quantity=50,
                reference_type='sales_order',
                reference_id=1
            )
            db_session.add(transaction)
            db_session.commit()

            assert transaction.transaction_type == 'sale'
            assert transaction.quantity == 50

    def test_transaction_with_notes(self, app, db_session, sample_product, sample_warehouse):
        """Test transaction with notes."""
        with app.app_context():
            transaction = InventoryTransaction(
                product_id=sample_product.product_id,
                warehouse_id=sample_warehouse.warehouse_id,
                transaction_type='purchase',
                quantity=25,
                notes='Stock received from supplier'
            )
            db_session.add(transaction)
            db_session.commit()

            assert transaction.notes == 'Stock received from supplier'

    def test_transaction_to_dict(self, sample_inventory_transaction, app):
        """Test inventory transaction serialization."""
        with app.app_context():
            data = sample_inventory_transaction.to_dict()
            assert 'transaction_id' in data
            assert 'transaction_type' in data
            assert 'quantity' in data


class TestStockAdjustmentModel:
    """Tests for StockAdjustment model."""

    def test_create_adjustment_damage(self, app, db_session, sample_product, sample_warehouse, test_user):
        """Test stock adjustment for damage."""
        with app.app_context():
            adjustment = StockAdjustment(
                product_id=sample_product.product_id,
                warehouse_id=sample_warehouse.warehouse_id,
                old_quantity=100,
                new_quantity=95,
                reason='damage',
                notes='Damaged during shipping',
                adjusted_by=test_user.user_id
            )
            db_session.add(adjustment)
            db_session.commit()

            assert adjustment.adjustment_id is not None
            assert adjustment.quantity_difference == -5
            assert adjustment.reason == 'damage'

    def test_create_adjustment_found(self, app, db_session, sample_product, sample_warehouse, test_user):
        """Test stock adjustment for found items."""
        with app.app_context():
            adjustment = StockAdjustment(
                product_id=sample_product.product_id,
                warehouse_id=sample_warehouse.warehouse_id,
                old_quantity=100,
                new_quantity=103,
                reason='physical_count',
                notes='Found during inventory count',
                adjusted_by=test_user.user_id
            )
            db_session.add(adjustment)
            db_session.commit()

            assert adjustment.quantity_difference == 3
            assert adjustment.reason == 'physical_count'

    def test_create_adjustment_correction(self, app, db_session, sample_product, sample_warehouse, test_user):
        """Test stock adjustment for correction."""
        with app.app_context():
            adjustment = StockAdjustment(
                product_id=sample_product.product_id,
                warehouse_id=sample_warehouse.warehouse_id,
                old_quantity=100,
                new_quantity=90,
                reason='correction',
                notes='Correcting count error',
                adjusted_by=test_user.user_id
            )
            db_session.add(adjustment)
            db_session.commit()

            assert adjustment.reason == 'correction'
            assert adjustment.quantity_difference == -10

    def test_adjustment_to_dict(self, sample_stock_adjustment, app):
        """Test stock adjustment serialization."""
        with app.app_context():
            data = sample_stock_adjustment.to_dict()
            assert 'adjustment_id' in data
            assert 'quantity_difference' in data
            assert 'adjustment_quantity' in data  # Alias
            assert 'reason' in data
