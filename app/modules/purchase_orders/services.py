# Purchase Order services

from typing import Optional, List
from datetime import datetime
from app.extensions import db
from app.modules.purchase_orders.models import PurchaseOrder, PurchaseOrderItem


class PurchaseOrderService:
    """Purchase Order management service."""

    @staticmethod
    def get_all(status: str = None) -> List[PurchaseOrder]:
        """Get all purchase orders."""
        query = PurchaseOrder.query
        if status:
            query = query.filter_by(status=status)
        return query.order_by(PurchaseOrder.created_at.desc()).all()

    @staticmethod
    def get_by_id(po_id: int) -> Optional[PurchaseOrder]:
        """Get purchase order by ID."""
        return PurchaseOrder.query.get(po_id)

    @staticmethod
    def get_by_number(po_number: str) -> Optional[PurchaseOrder]:
        """Get purchase order by number."""
        return PurchaseOrder.query.filter_by(po_number=po_number).first()

    @staticmethod
    def get_by_supplier(supplier_id: int) -> List[PurchaseOrder]:
        """Get purchase orders by supplier."""
        return PurchaseOrder.query.filter_by(supplier_id=supplier_id).all()

    @staticmethod
    def create(po_number: str, supplier_id: int, warehouse_id: int, order_date,
               created_by: int, items: list = None, **kwargs) -> PurchaseOrder:
        """Create a new purchase order."""
        po = PurchaseOrder(
            po_number=po_number,
            supplier_id=supplier_id,
            warehouse_id=warehouse_id,
            order_date=order_date,
            created_by=created_by,
            **kwargs
        )
        db.session.add(po)
        db.session.flush()  # Get po_id
        
        # Add items if provided
        if items:
            for item_data in items:
                item = PurchaseOrderItem(
                    po_id=po.po_id,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price']
                )
                db.session.add(item)
        
        db.session.commit()
        po.calculate_total()
        db.session.commit()
        return po

    @staticmethod
    def update(po: PurchaseOrder, **kwargs) -> PurchaseOrder:
        """Update purchase order."""
        for key, value in kwargs.items():
            if hasattr(po, key) and key not in ['po_id', 'created_by']:
                setattr(po, key, value)
        db.session.commit()
        return po

    @staticmethod
    def update_status(po: PurchaseOrder, status: str) -> PurchaseOrder:
        """Update purchase order status."""
        po.status = status
        db.session.commit()
        return po

    @staticmethod
    def add_item(po: PurchaseOrder, product_id: int, quantity: int, 
                  unit_price: float) -> PurchaseOrderItem:
        """Add item to purchase order."""
        item = PurchaseOrderItem(
            po_id=po.po_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price
        )
        db.session.add(item)
        db.session.commit()
        po.calculate_total()
        db.session.commit()
        return item

    @staticmethod
    def receive_item(item: PurchaseOrderItem, quantity: int) -> PurchaseOrderItem:
        """Record received quantity for an item."""
        item.received_quantity += quantity
        db.session.commit()
        return item

    @staticmethod
    def delete(po: PurchaseOrder) -> None:
        """Delete purchase order (only if draft)."""
        if po.status == 'draft':
            db.session.delete(po)
            db.session.commit()
        else:
            raise ValueError("Can only delete draft orders")

    @staticmethod
    def generate_po_number() -> str:
        """Generate a unique PO number."""
        from datetime import date
        today = date.today()
        prefix = f"PO-{today.strftime('%Y%m%d')}"
        
        # Find the last PO number for today
        last_po = PurchaseOrder.query.filter(
            PurchaseOrder.po_number.like(f'{prefix}%')
        ).order_by(PurchaseOrder.po_number.desc()).first()
        
        if last_po:
            last_seq = int(last_po.po_number.split('-')[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        
        return f"{prefix}-{new_seq:04d}"
