# Warehouse schemas (Pydantic)

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class WarehouseBase(BaseModel):
    """Base warehouse schema."""
    warehouse_name: str = Field(..., max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field('USA', max_length=50)
    postal_code: Optional[str] = Field(None, max_length=20)
    manager_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    capacity: Optional[int] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class WarehouseCreate(WarehouseBase):
    """Warehouse creation schema."""
    pass

class WarehouseResponse(WarehouseBase):
    """Warehouse response schema."""
    warehouse_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
