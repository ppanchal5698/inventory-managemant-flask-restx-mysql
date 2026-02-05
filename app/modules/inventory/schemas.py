# Inventory schemas (Pydantic)

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

class InventoryTransactionBase(BaseModel):
    """Base inventory transaction schema."""
    transaction_type: Literal['purchase', 'sale', 'adjustment', 'transfer', 'return', 'damage']
    product_id: int
    warehouse_id: int
    quantity: int
    reference_type: Optional[str] = Field(None, max_length=50)
    reference_id: Optional[int] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class InventoryTransactionCreate(InventoryTransactionBase):
    pass

class InventoryTransactionResponse(InventoryTransactionBase):
    transaction_id: int
    transaction_date: datetime
    performed_by: Optional[int] = None

class StockAdjustmentBase(BaseModel):
    """Base stock adjustment schema."""
    product_id: int
    warehouse_id: int
    new_quantity: int = Field(..., ge=0)
    reason: Literal['physical_count', 'damage', 'theft', 'expired', 'correction', 'other']
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class StockAdjustmentCreate(StockAdjustmentBase):
    pass

class StockAdjustmentResponse(StockAdjustmentBase):
    adjustment_id: int
    old_quantity: int
    quantity_difference: int
    adjustment_date: datetime
    adjusted_by: Optional[int] = None
