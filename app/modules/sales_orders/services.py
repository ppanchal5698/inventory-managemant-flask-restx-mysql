# Sales Order services (Async)

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.modules.sales_orders.models import SalesOrder, SalesOrderItem
from app.modules.inventory.services import InventoryService
from app.core.cache import CacheKeyPrefixes, invalidate_cache, cached_list, cached_item

CACHE_PREFIX = CacheKeyPrefixes.SALES_ORDERS # Not defined yet in Prefix class
# We can just use string "sales_orders"

class SalesOrderService:
    """Sales Order management service."""

    @staticmethod
    async def get_all(include_inactive: bool = False) -> List[SalesOrder]:
        """Get all sales orders."""
        stmt = select(SalesOrder).order_by(SalesOrder.order_date.desc())
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(order_id: int) -> Optional[SalesOrder]:
        """Get sales order by ID."""
        # Eager load items for total calculation usually
        stmt = select(SalesOrder).options(selectinload(SalesOrder.items)).filter_by(order_id=order_id)
        result = await db.session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(data: dict) -> SalesOrder:
        """Create a new sales order."""
        items_data = data.pop('items', [])

        order = SalesOrder(**data)
        db.session.add(order)
        # Flush to get ID? Not needed if we add items to relationship
        
        for item_data in items_data:
            item = SalesOrderItem(**item_data)
            order.items.append(item)

        # Calculate totals
        # We need to manually calculate if using Python logic,
        # or rely on DB defaults/triggers (but computed columns are read-only usually).
        # We should calculate totals before commit if we want to store total_amount.

        # Simple total calc
        subtotal = sum((i.quantity * i.unit_price) - i.discount for i in order.items)
        order.total_amount = subtotal + order.tax_amount + order.shipping_cost - order.discount_amount

        await db.session.commit()

        # Reload with items
        stmt = select(SalesOrder).options(selectinload(SalesOrder.items)).filter_by(order_id=order.order_id)
        result = await db.session.execute(stmt)
        order = result.scalar_one()

        # Reserve stock?
        # Usually reserving stock happens on creation or explicit status change.
        # Let's assume we just record order for now.
        
        return order

    @staticmethod
    async def update(order: SalesOrder, data: dict) -> SalesOrder:
        """Update sales order."""
        # If updating status to 'shipped', we might need to deduct inventory.
        new_status = data.get('status')
        old_status = order.status

        for key, value in data.items():
            if hasattr(order, key) and key != 'order_id':
                setattr(order, key, value)

        if new_status == 'shipped' and old_status != 'shipped':
            # Deduct inventory
            for item in order.items:
                await InventoryService.record_transaction(
                    product_id=item.product_id,
                    warehouse_id=order.warehouse_id,
                    transaction_type='sale',
                    quantity=item.quantity,
                    reference_type='sales_order',
                    reference_id=order.order_id,
                    notes=f"Order {order.order_number} shipped"
                )

        await db.session.commit()

        # Reload with items
        stmt = select(SalesOrder).options(selectinload(SalesOrder.items)).filter_by(order_id=order.order_id)
        result = await db.session.execute(stmt)
        order = result.scalar_one()

        return order

    @staticmethod
    async def delete(order: SalesOrder) -> None:
        """Delete sales order."""
        await db.session.delete(order)
        await db.session.commit()
