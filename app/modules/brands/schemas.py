# Brand schemas (Pydantic)

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class BrandBase(BaseModel):
    """Base brand schema."""
    brand_name: str = Field(..., max_length=100)
    manufacturer_name: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class BrandCreate(BrandBase):
    """Brand creation schema."""
    pass

class BrandResponse(BrandBase):
    """Brand response schema."""
    brand_id: int
    created_at: datetime
