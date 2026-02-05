# Purchase Order schemas (Pydantic)

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict

class PurchaseOrderItemBase(BaseModel):
    """Base purchase order item schema."""
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    received_quantity: int = Field(0, ge=0)

    model_config = ConfigDict(from_attributes=True)

class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass

class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    po_item_id: int
    po_id: int
    line_total: Optional[Decimal] = None

class PurchaseOrderBase(BaseModel):
    """Base purchase order schema."""
    po_number: str = Field(..., max_length=50)
    supplier_id: int
    warehouse_id: int
    order_date: date
    expected_delivery_date: Optional[date] = None
    status: Literal['draft', 'pending', 'approved', 'received', 'cancelled'] = 'draft'
    tax_amount: Decimal = Field(0, ge=0)
    shipping_cost: Decimal = Field(0, ge=0)
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PurchaseOrderCreate(PurchaseOrderBase):
    """Purchase Order creation schema."""
    items: List[PurchaseOrderItemCreate]

class PurchaseOrderResponse(PurchaseOrderBase):
    """Purchase Order response schema."""
    po_id: int
    total_amount: Optional[Decimal] = None
    actual_delivery_date: Optional[date] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: Optional[List[PurchaseOrderItemResponse]] = None
