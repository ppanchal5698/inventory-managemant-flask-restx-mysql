# Supplier schemas (Pydantic)

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class SupplierBase(BaseModel):
    """Base supplier schema."""
    supplier_name: str = Field(..., max_length=150)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field('USA', max_length=50)
    postal_code: Optional[str] = Field(None, max_length=20)
    tax_id: Optional[str] = Field(None, max_length=50)
    payment_terms: Optional[str] = Field(None, max_length=100)
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class SupplierCreate(SupplierBase):
    """Supplier creation schema."""
    pass

class SupplierResponse(SupplierBase):
    """Supplier response schema."""
    supplier_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
