# Sales Order services

from typing import Optional, List
from datetime import datetime, date
from app.extensions import db
from app.modules.sales_orders.models import SalesOrder, SalesOrderItem


class SalesOrderService:
    """Sales Order management service."""

    @staticmethod
    def get_all(status: str = None, payment_status: str = None) -> List[SalesOrder]:
        """Get all sales orders."""
        query = SalesOrder.query
        if status:
            query = query.filter_by(status=status)
        if payment_status:
            query = query.filter_by(payment_status=payment_status)
        return query.order_by(SalesOrder.created_at.desc()).all()

    @staticmethod
    def get_by_id(order_id: int) -> Optional[SalesOrder]:
        """Get sales order by ID."""
        return SalesOrder.query.get(order_id)

    @staticmethod
    def get_by_number(order_number: str) -> Optional[SalesOrder]:
        """Get sales order by number."""
        return SalesOrder.query.filter_by(order_number=order_number).first()

    @staticmethod
    def get_by_customer(customer_id: int) -> List[SalesOrder]:
        """Get sales orders by customer."""
        return SalesOrder.query.filter_by(customer_id=customer_id).order_by(
            SalesOrder.order_date.desc()
        ).all()

    @staticmethod
    def get_by_date_range(start_date: date, end_date: date) -> List[SalesOrder]:
        """Get sales orders within date range."""
        return SalesOrder.query.filter(
            SalesOrder.order_date >= start_date,
            SalesOrder.order_date <= end_date
        ).order_by(SalesOrder.order_date.desc()).all()

    @staticmethod
    def create(order_number: str, customer_id: int, warehouse_id: int, order_date,
               created_by: int, items: list = None, **kwargs) -> SalesOrder:
        """Create a new sales order."""
        order = SalesOrder(
            order_number=order_number,
            customer_id=customer_id,
            warehouse_id=warehouse_id,
            order_date=order_date,
            created_by=created_by,
            **kwargs
        )
        db.session.add(order)
        db.session.flush()  # Get order_id
        
        # Add items if provided
        if items:
            for item_data in items:
                item = SalesOrderItem(
                    order_id=order.order_id,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    discount=item_data.get('discount', 0)
                )
                db.session.add(item)
        
        db.session.commit()
        order.calculate_total()
        db.session.commit()
        return order

    @staticmethod
    def update(order: SalesOrder, **kwargs) -> SalesOrder:
        """Update sales order."""
        for key, value in kwargs.items():
            if hasattr(order, key) and key not in ['order_id', 'created_by']:
                setattr(order, key, value)
        db.session.commit()
        return order

    @staticmethod
    def update_status(order: SalesOrder, status: str) -> SalesOrder:
        """Update sales order status."""
        order.status = status
        db.session.commit()
        return order

    @staticmethod
    def update_payment_status(order: SalesOrder, payment_status: str) -> SalesOrder:
        """Update payment status."""
        order.payment_status = payment_status
        db.session.commit()
        return order

    @staticmethod
    def add_item(order: SalesOrder, product_id: int, quantity: int, 
                  unit_price: float, discount: float = 0) -> SalesOrderItem:
        """Add item to sales order."""
        item = SalesOrderItem(
            order_id=order.order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            discount=discount
        )
        db.session.add(item)
        db.session.commit()
        order.calculate_total()
        db.session.commit()
        return item

    @staticmethod
    def cancel_order(order: SalesOrder) -> SalesOrder:
        """Cancel a sales order."""
        order.status = 'cancelled'
        db.session.commit()
        return order

    @staticmethod
    def generate_order_number() -> str:
        """Generate a unique order number."""
        today = date.today()
        prefix = f"SO-{today.strftime('%Y%m%d')}"
        
        # Find the last order number for today
        last_order = SalesOrder.query.filter(
            SalesOrder.order_number.like(f'{prefix}%')
        ).order_by(SalesOrder.order_number.desc()).first()
        
        if last_order:
            last_seq = int(last_order.order_number.split('-')[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        
        return f"{prefix}-{new_seq:04d}"
