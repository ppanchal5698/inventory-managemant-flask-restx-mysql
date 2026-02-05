# Purchase Order services (Async)

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.modules.purchase_orders.models import PurchaseOrder, PurchaseOrderItem
from app.modules.inventory.services import InventoryService

class PurchaseOrderService:
    """Purchase Order management service."""

    @staticmethod
    async def get_all() -> List[PurchaseOrder]:
        """Get all purchase orders."""
        stmt = select(PurchaseOrder).order_by(PurchaseOrder.order_date.desc())
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(po_id: int) -> Optional[PurchaseOrder]:
        """Get purchase order by ID."""
        stmt = select(PurchaseOrder).options(selectinload(PurchaseOrder.items)).filter_by(po_id=po_id)
        result = await db.session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(data: dict) -> PurchaseOrder:
        """Create a new purchase order."""
        items_data = data.pop('items', [])

        po = PurchaseOrder(**data)
        db.session.add(po)
        
        for item_data in items_data:
            item = PurchaseOrderItem(**item_data)
            po.items.append(item)

        subtotal = sum(i.quantity * i.unit_price for i in po.items)
        po.total_amount = subtotal + po.tax_amount + po.shipping_cost

        await db.session.commit()

        # Reload with items to ensure relationships are loaded for to_dict
        stmt = select(PurchaseOrder).options(selectinload(PurchaseOrder.items)).filter_by(po_id=po.po_id)
        result = await db.session.execute(stmt)
        po = result.scalar_one()

        return po

    @staticmethod
    async def update(po: PurchaseOrder, data: dict) -> PurchaseOrder:
        """Update purchase order."""
        new_status = data.get('status')
        old_status = po.status

        for key, value in data.items():
            if hasattr(po, key) and key != 'po_id':
                setattr(po, key, value)

        if new_status == 'received' and old_status != 'received':
            # Add inventory
            for item in po.items:
                await InventoryService.record_transaction(
                    product_id=item.product_id,
                    warehouse_id=po.warehouse_id,
                    transaction_type='purchase',
                    quantity=item.quantity, # Or received_quantity if partial? assuming full
                    reference_type='purchase_order',
                    reference_id=po.po_id,
                    notes=f"PO {po.po_number} received"
                )

        await db.session.commit()

        # Reload with items
        stmt = select(PurchaseOrder).options(selectinload(PurchaseOrder.items)).filter_by(po_id=po.po_id)
        result = await db.session.execute(stmt)
        po = result.scalar_one()

        return po

    @staticmethod
    async def delete(po: PurchaseOrder) -> None:
        """Delete purchase order."""
        await db.session.delete(po)
        await db.session.commit()
