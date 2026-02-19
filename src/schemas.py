"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from models import UserRole


class UserRegister(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    full_name: str
    password: str
    role: Optional[UserRole] = UserRole.STUDENT


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True


class ActivityResponse(BaseModel):
    """Schema for activity response."""
    name: str
    description: str
    schedule: str
    max_participants: int
    participants: list

    class Config:
        from_attributes = True
