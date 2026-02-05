# Stock schemas (Pydantic)

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class StockBase(BaseModel):
    """Base stock schema."""
    product_id: int
    warehouse_id: int
    quantity_on_hand: int = Field(..., ge=0)
    quantity_reserved: int = Field(0, ge=0)

    model_config = ConfigDict(from_attributes=True)

class StockCreate(StockBase):
    """Stock creation schema."""
    pass

class StockUpdate(BaseModel):
    """Stock update schema."""
    quantity_on_hand: Optional[int] = Field(None, ge=0)
    quantity_reserved: Optional[int] = Field(None, ge=0)

class StockResponse(StockBase):
    """Stock response schema."""
    stock_id: int
    quantity_available: int
    last_stock_check: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class StockAdjust(BaseModel):
    """Stock adjustment schema."""
    adjustment: int
