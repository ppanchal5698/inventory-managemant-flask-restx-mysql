# Product schemas (Pydantic)

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class ProductBase(BaseModel):
    """Base product schema."""
    product_code: str = Field(..., max_length=50)
    product_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    unit_price: Decimal = Field(..., ge=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    reorder_level: int = Field(10, ge=0)
    min_stock_level: int = Field(5, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    unit_of_measure: str = Field('pcs', max_length=20)
    barcode: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=100)
    weight: Optional[Decimal] = Field(None, ge=0)
    dimensions: Optional[str] = Field(None, max_length=50)
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class ProductCreate(ProductBase):
    """Product creation schema."""
    pass

class ProductResponse(ProductBase):
    """Product response schema."""
    product_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    total_stock: Optional[int] = 0
