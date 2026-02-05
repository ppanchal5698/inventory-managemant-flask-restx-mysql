# Category schemas (Pydantic)

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class CategoryBase(BaseModel):
    """Base category schema."""
    category_name: str = Field(..., max_length=100)
    parent_category_id: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(CategoryBase):
    """Category creation schema."""
    pass

class CategoryResponse(CategoryBase):
    """Category response schema."""
    category_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    subcategories: Optional[List['CategoryResponse']] = None

# Resolve forward reference
CategoryResponse.model_rebuild()
