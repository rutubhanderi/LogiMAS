from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal
from enum import Enum


class UserRole(str, Enum):
    """User roles in the system"""
    CUSTOMER = "customer"
    DELIVERY_GUY = "delivery_guy"
    ADMIN = "admin"


class UserCreate(BaseModel):
    """Schema for customer self-registration"""
    email: EmailStr
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=72,
        description="Password must be between 8 and 72 characters"
    )
    name: Optional[str] = None
    phone: Optional[str] = None


class AdminUserCreate(BaseModel):
    """Schema for admin to create users with specific roles"""
    email: EmailStr
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=72,
        description="Password must be between 8 and 72 characters"
    )
    name: str
    phone: Optional[str] = None
    role: UserRole = Field(..., description="User role: customer, delivery_guy, or admin")
    
    @validator('role')
    def validate_role(cls, v):
        if v not in [UserRole.CUSTOMER, UserRole.DELIVERY_GUY, UserRole.ADMIN]:
            raise ValueError('Invalid role')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    """Public user information (no sensitive data)"""
    customer_id: UUID
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    role: str
    created_at: datetime
    is_active: bool
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserListResponse(BaseModel):
    """Response schema for listing users"""
    users: list[UserPublic]
    total: int


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str


class TokenWithRefresh(BaseModel):
    """JWT token response with refresh token"""
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    """Data extracted from JWT token"""
    customer_id: Optional[str] = None
    role: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token"""
    refresh_token: str