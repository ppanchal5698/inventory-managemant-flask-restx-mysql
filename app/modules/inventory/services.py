# Inventory services (Async)

from typing import List, Optional
from sqlalchemy import select, desc
from app.extensions import db
from app.modules.inventory.models import InventoryTransaction, StockAdjustment
from app.modules.stock.models import Stock
from app.core.cache import CacheKeyPrefixes, invalidate_cache, cached_list

CACHE_PREFIX = CacheKeyPrefixes.STOCK
CACHE_TIMEOUT = 300


class InventoryService:
    """Inventory management service."""

    @staticmethod
    async def record_transaction(product_id: int, warehouse_id: int, transaction_type: str,
                           quantity: int, reference_type: str = None, reference_id: int = None,
                           notes: str = None, performed_by: int = None) -> InventoryTransaction:
        """Record an inventory transaction and update stock."""

        # Determine stock impact based on transaction type
        # In general, positive quantity means ADD to stock, negative means REMOVE?
        # Or do we pass positive quantity and type determines direction?
        # Usually transaction_type determines direction.

        # Let's assume quantity is always positive in input, and logic determines sign.
        # Wait, the caller might pass signed quantity.
        # Looking at legacy code or standard:
        # purchase -> increase
        # sale -> decrease
        # return -> increase
        # damage -> decrease
        # transfer -> decrease (from), increase (to - separate transaction)

        # Let's handle sign logic here.
        change = 0
        if transaction_type in ['purchase', 'return', 'adjustment_in']:
            change = abs(quantity)
        elif transaction_type in ['sale', 'damage', 'theft', 'transfer_out', 'adjustment_out']:
            change = -abs(quantity)
        elif transaction_type == 'adjustment':
            # For direct adjustment, we need context. Assuming user passes signed quantity if generic 'adjustment'
            # Or we look at quantity sign.
            change = quantity
        else:
            change = quantity

        # Create transaction record
        transaction = InventoryTransaction(
            transaction_type=transaction_type,
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity=change, # Store the actual change
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            performed_by=performed_by
        )
        db.session.add(transaction)
        
        # Update stock level
        stmt = select(Stock).filter_by(product_id=product_id, warehouse_id=warehouse_id)
        result = await db.session.execute(stmt)
        stock = result.scalar_one_or_none()

        if not stock:
            # Create new stock entry if positive change
            if change > 0:
                stock = Stock(
                    product_id=product_id,
                    warehouse_id=warehouse_id,
                    quantity_on_hand=0
                )
                db.session.add(stock)
            else:
                raise ValueError("Cannot decrease stock for non-existent stock entry")

        stock.quantity_on_hand += change
        if stock.quantity_on_hand < 0:
            # Allow negative stock? Usually no.
            # raise ValueError("Insufficient stock")
            pass
            
        await db.session.commit()
        await invalidate_cache(CACHE_PREFIX, stock.stock_id)
        
        return transaction

    @staticmethod
    async def adjust_stock(product_id: int, warehouse_id: int, new_quantity: int,
                     reason: str, notes: str = None, adjusted_by: int = None) -> StockAdjustment:
        """Adjust stock level to a specific quantity."""

        stmt = select(Stock).filter_by(product_id=product_id, warehouse_id=warehouse_id)
        result = await db.session.execute(stmt)
        stock = result.scalar_one_or_none()
        
        old_quantity = 0
        if stock:
            old_quantity = stock.quantity_on_hand
        else:
            # Create stock if it doesn't exist
            stock = Stock(product_id=product_id, warehouse_id=warehouse_id, quantity_on_hand=0)
            db.session.add(stock)

        adjustment = StockAdjustment(
            product_id=product_id,
            warehouse_id=warehouse_id,
            old_quantity=old_quantity,
            new_quantity=new_quantity,
            reason=reason,
            notes=notes,
            adjusted_by=adjusted_by
        )
        db.session.add(adjustment)
        
        # Update stock
        stock.quantity_on_hand = new_quantity
        stock.last_stock_check = func.now()

        # Record generic transaction for history
        transaction = InventoryTransaction(
            transaction_type='adjustment',
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity=new_quantity - old_quantity,
            reference_type='stock_adjustment',
            # We don't have adjustment.id yet until flush/commit.
            # We can commit later.
            notes=f"Stock adjustment: {reason}",
            performed_by=adjusted_by
        )
        db.session.add(transaction)

        await db.session.commit()
        # Update reference_id after commit
        transaction.reference_id = adjustment.adjustment_id
        await db.session.commit()
        
        await invalidate_cache(CACHE_PREFIX, stock.stock_id)
        
        return adjustment

    @staticmethod
    async def get_recent_transactions(limit: int = 50) -> List[InventoryTransaction]:
        """Get recent inventory transactions."""
        stmt = select(InventoryTransaction).order_by(desc(InventoryTransaction.transaction_date)).limit(limit)
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_transactions_by_product(product_id: int) -> List[InventoryTransaction]:
        """Get transactions for a product."""
        stmt = select(InventoryTransaction).filter_by(product_id=product_id).order_by(desc(InventoryTransaction.transaction_date))
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_transactions_by_warehouse(warehouse_id: int) -> List[InventoryTransaction]:
        """Get transactions for a warehouse."""
        stmt = select(InventoryTransaction).filter_by(warehouse_id=warehouse_id).order_by(desc(InventoryTransaction.transaction_date))
        result = await db.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_recent_adjustments(limit: int = 50) -> List[StockAdjustment]:
        """Get recent stock adjustments."""
        stmt = select(StockAdjustment).order_by(desc(StockAdjustment.adjustment_date)).limit(limit)
        result = await db.session.execute(stmt)
        return result.scalars().all()
