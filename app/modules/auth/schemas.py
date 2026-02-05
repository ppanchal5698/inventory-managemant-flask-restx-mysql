# Auth schemas (Pydantic)

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[str] = Field('staff', pattern='^(admin|manager|staff|viewer)$')

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    """User response schema."""
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

class LoginRequest(BaseModel):
    """Login request schema."""
    username: str
    password: str

class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str
    refresh_token: str
    user: UserResponse

class PasswordChange(BaseModel):
    """Password change schema."""
    current_password: str
    new_password: str = Field(..., min_length=8)
