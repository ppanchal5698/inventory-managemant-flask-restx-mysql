# Sales Order schemas (Pydantic)

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class SalesOrderItemBase(BaseModel):
    """Base sales order item schema."""
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount: Decimal = Field(0, ge=0)

    model_config = ConfigDict(from_attributes=True)

class SalesOrderItemCreate(SalesOrderItemBase):
    pass

class SalesOrderItemResponse(SalesOrderItemBase):
    order_item_id: int
    order_id: int
    line_total: Optional[Decimal] = None

class SalesOrderBase(BaseModel):
    """Base sales order schema."""
    order_number: str = Field(..., max_length=50)
    customer_id: int
    warehouse_id: int
    order_date: date
    expected_delivery_date: Optional[date] = None
    status: Literal['pending', 'processing', 'shipped', 'delivered', 'cancelled'] = 'pending'
    tax_amount: Decimal = Field(0, ge=0)
    shipping_cost: Decimal = Field(0, ge=0)
    discount_amount: Decimal = Field(0, ge=0)
    payment_status: Literal['unpaid', 'partial', 'paid'] = 'unpaid'
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SalesOrderCreate(SalesOrderBase):
    """Sales Order creation schema."""
    items: List[SalesOrderItemCreate]

class SalesOrderResponse(SalesOrderBase):
    """Sales Order response schema."""
    order_id: int
    total_amount: Optional[Decimal] = None
    actual_delivery_date: Optional[date] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: Optional[List[SalesOrderItemResponse]] = None
    customer: Optional[Dict[str, Any]] = None # Or use CustomerResponse if available
