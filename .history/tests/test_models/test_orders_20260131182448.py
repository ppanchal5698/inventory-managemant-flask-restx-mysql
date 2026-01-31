# Stock and Order model tests

from datetime import date

import pytest

from app.modules.inventory.models import InventoryTransaction, StockAdjustment
from app.modules.purchase_orders.models import PurchaseOrder, PurchaseOrderItem
from app.modules.sales_orders.models import SalesOrder, SalesOrderItem
from app.modules.stock.models import Stock


class TestStockModel:
    """Tests for Stock model."""

    def test_create_stock(self, app, db_session, sample_product, sample_warehouse):
        """Test stock creation."""
        with app.app_context():
            stock = Stock(
                product_id=sample_product.product_id,
                warehouse_id=sample_warehouse.warehouse_id,
                quantity_on_hand=50,
                quantity_reserved=5
            )
            db_session.add(stock)
            db_session.commit()

            assert stock.stock_id is not None

    def test_stock_quantity_available(self, sample_stock, app):
        """Test quantity_available property."""
        with app.app_context():
            # quantity_on_hand=100, quantity_reserved=10
            assert sample_stock.quantity_available == 90

    def test_stock_to_dict(self, sample_stock, app):
        """Test stock serialization."""
        with app.app_context():
            data = sample_stock.to_dict()
            assert data['quantity_on_hand'] == 100
            assert data['quantity_reserved'] == 10
            assert data['quantity_available'] == 90


class TestPurchaseOrderModel:
    """Tests for PurchaseOrder model."""

    def test_create_purchase_order(self, app, db_session, sample_supplier,
                                    sample_warehouse, test_user):
        """Test purchase order creation."""
        with app.app_context():
            po = PurchaseOrder(
                po_number='PO-001',
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

    def test_purchase_order_items(self, app, db_session, sample_supplier,
                                   sample_warehouse, sample_product, test_user):
        """Test purchase order with items."""
        with app.app_context():
            po = PurchaseOrder(
                po_number='PO-002',
                supplier_id=sample_supplier.supplier_id,
                warehouse_id=sample_warehouse.warehouse_id,
                order_date=date.today(),
                created_by=test_user.user_id
            )
            db_session.add(po)
            db_session.commit()

            item = PurchaseOrderItem(
                po_id=po.po_id,
                product_id=sample_product.product_id,
                quantity=10,
                unit_price=49.99
            )
            db_session.add(item)
            db_session.commit()

            assert float(item.line_total) == 499.9
            assert len(list(po.items)) == 1


class TestSalesOrderModel:
    """Tests for SalesOrder model."""

    def test_create_sales_order(self, app, db_session, sample_customer,
                                 sample_warehouse, test_user):
        """Test sales order creation."""
        with app.app_context():
            order = SalesOrder(
                order_number='SO-001',
                customer_id=sample_customer.customer_id,
                warehouse_id=sample_warehouse.warehouse_id,
                order_date=date.today(),
                status='pending',
                created_by=test_user.user_id
            )
            db_session.add(order)
            db_session.commit()

            assert order.order_id is not None
            assert order.status == 'pending'
            assert order.payment_status == 'unpaid'

    def test_sales_order_items(self, app, db_session, sample_customer,
                                sample_warehouse, sample_product, test_user):
        """Test sales order with items."""
        with app.app_context():
            order = SalesOrder(
                order_number='SO-002',
                customer_id=sample_customer.customer_id,
                warehouse_id=sample_warehouse.warehouse_id,
                order_date=date.today(),
                created_by=test_user.user_id
            )
            db_session.add(order)
            db_session.commit()

            item = SalesOrderItem(
                order_id=order.order_id,
                product_id=sample_product.product_id,
                quantity=5,
                unit_price=99.99,
                discount=10.00
            )
            db_session.add(item)
            db_session.commit()

            # (5 * 99.99) - 10 = 489.95
            assert float(item.line_total) == 489.95


class TestInventoryTransactionModel:
    """Tests for InventoryTransaction model."""

    def test_create_transaction(self, app, db_session, sample_product,
                                 sample_warehouse, test_user):
        """Test inventory transaction creation."""
        with app.app_context():
            transaction = InventoryTransaction(
                transaction_type='purchase',
                product_id=sample_product.product_id,
                warehouse_id=sample_warehouse.warehouse_id,
                quantity=50,
                reference_type='purchase_order',
                reference_id=1,
                performed_by=test_user.user_id
            )
            db_session.add(transaction)
            db_session.commit()

            assert transaction.transaction_id is not None
            assert transaction.transaction_type == 'purchase'


class TestStockAdjustmentModel:
    """Tests for StockAdjustment model."""

    def test_create_adjustment(self, app, db_session, sample_product,
                                sample_warehouse, test_user):
        """Test stock adjustment creation."""
        with app.app_context():
            adjustment = StockAdjustment(
                product_id=sample_product.product_id,
                warehouse_id=sample_warehouse.warehouse_id,
                old_quantity=100,
                new_quantity=95,
                reason='damage',
                notes='5 units damaged in transit',
                adjusted_by=test_user.user_id
            )
            db_session.add(adjustment)
            db_session.commit()

            assert adjustment.adjustment_id is not None
            assert adjustment.quantity_difference == -5
