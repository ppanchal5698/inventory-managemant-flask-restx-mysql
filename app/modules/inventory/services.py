# Inventory services

from typing import Optional, List
from datetime import datetime, date
from app.extensions import db
from app.modules.inventory.models import InventoryTransaction, StockAdjustment
from app.modules.stock.services import StockService


class InventoryTransactionService:
    """Inventory Transaction management service."""

    @staticmethod
    def get_all(transaction_type: str = None, product_id: int = None, 
                warehouse_id: int = None) -> List[InventoryTransaction]:
        """Get all transactions with optional filters."""
        query = InventoryTransaction.query
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)
        if product_id:
            query = query.filter_by(product_id=product_id)
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        return query.order_by(InventoryTransaction.transaction_date.desc()).all()

    @staticmethod
    def get_by_id(transaction_id: int) -> Optional[InventoryTransaction]:
        """Get transaction by ID."""
        return InventoryTransaction.query.get(transaction_id)

    @staticmethod
    def get_by_reference(reference_type: str, reference_id: int) -> List[InventoryTransaction]:
        """Get transactions by reference."""
        return InventoryTransaction.query.filter_by(
            reference_type=reference_type,
            reference_id=reference_id
        ).all()

    @staticmethod
    def get_by_date_range(start_date: date, end_date: date) -> List[InventoryTransaction]:
        """Get transactions within date range."""
        return InventoryTransaction.query.filter(
            InventoryTransaction.transaction_date >= datetime.combine(start_date, datetime.min.time()),
            InventoryTransaction.transaction_date <= datetime.combine(end_date, datetime.max.time())
        ).order_by(InventoryTransaction.transaction_date.desc()).all()

    @staticmethod
    def create(transaction_type: str, product_id: int, warehouse_id: int, 
               quantity: int, performed_by: int, reference_type: str = None,
               reference_id: int = None, notes: str = None,
               update_stock: bool = True) -> InventoryTransaction:
        """Create a new transaction and optionally update stock."""
        transaction = InventoryTransaction(
            transaction_type=transaction_type,
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            performed_by=performed_by
        )
        db.session.add(transaction)
        
        # Update stock if requested
        if update_stock:
            stock = StockService.get_or_create(product_id, warehouse_id)
            
            # Determine if quantity should be added or subtracted
            if transaction_type in ['purchase', 'return']:
                StockService.adjust_quantity(stock, quantity)
            elif transaction_type in ['sale', 'damage']:
                StockService.adjust_quantity(stock, -quantity)
            elif transaction_type == 'adjustment':
                StockService.adjust_quantity(stock, quantity)  # quantity can be +/-
        
        db.session.commit()
        return transaction


class StockAdjustmentService:
    """Stock Adjustment management service."""

    @staticmethod
    def get_all(product_id: int = None, warehouse_id: int = None,
                reason: str = None) -> List[StockAdjustment]:
        """Get all adjustments with optional filters."""
        query = StockAdjustment.query
        if product_id:
            query = query.filter_by(product_id=product_id)
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        if reason:
            query = query.filter_by(reason=reason)
        return query.order_by(StockAdjustment.adjustment_date.desc()).all()

    @staticmethod
    def get_by_id(adjustment_id: int) -> Optional[StockAdjustment]:
        """Get adjustment by ID."""
        return StockAdjustment.query.get(adjustment_id)

    @staticmethod
    def create(product_id: int, warehouse_id: int, new_quantity: int,
               reason: str, adjusted_by: int, notes: str = None) -> StockAdjustment:
        """Create a stock adjustment and update stock."""
        # Get current stock
        stock = StockService.get_or_create(product_id, warehouse_id)
        old_quantity = stock.quantity_on_hand
        
        # Create adjustment record
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
        
        # Update stock to new quantity
        stock.quantity_on_hand = new_quantity
        stock.last_stock_check = datetime.utcnow()
        
        # Create corresponding transaction
        adjustment_qty = new_quantity - old_quantity
        if adjustment_qty != 0:
            InventoryTransactionService.create(
                transaction_type='adjustment',
                product_id=product_id,
                warehouse_id=warehouse_id,
                quantity=adjustment_qty,
                performed_by=adjusted_by,
                reference_type='stock_adjustment',
                reference_id=adjustment.adjustment_id,
                notes=f"Adjustment: {reason} - {notes or ''}",
                update_stock=False  # Stock already updated above
            )
        
        db.session.commit()
        return adjustment

    @staticmethod
    def get_by_date_range(start_date: date, end_date: date) -> List[StockAdjustment]:
        """Get adjustments within date range."""
        return StockAdjustment.query.filter(
            StockAdjustment.adjustment_date >= datetime.combine(start_date, datetime.min.time()),
            StockAdjustment.adjustment_date <= datetime.combine(end_date, datetime.max.time())
        ).order_by(StockAdjustment.adjustment_date.desc()).all()
