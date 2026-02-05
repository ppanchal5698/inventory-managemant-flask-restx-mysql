# Customer schemas (Pydantic)

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class CustomerBase(BaseModel):
    """Base customer schema."""
    customer_name: str = Field(..., max_length=150)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field('USA', max_length=50)
    postal_code: Optional[str] = Field(None, max_length=20)
    tax_id: Optional[str] = Field(None, max_length=50)
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class CustomerCreate(CustomerBase):
    """Customer creation schema."""
    pass

class CustomerResponse(CustomerBase):
    """Customer response schema."""
    customer_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
