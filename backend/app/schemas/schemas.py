"""
Pydantic Schemas Module
-----------------------
Defines request and response schemas for API validation.
Pydantic ensures data validation and serialization.

Each schema has:
- Base: common fields
- Create: fields needed for creation
- Response: fields returned in API responses
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ============================================================
# USER SCHEMAS
# ============================================================

class UserCreate(BaseModel):
    """Schema for user registration"""
    name: str
    email: str
    password: str
    role: str = "student"  # Default role is student


class UserLogin(BaseModel):
    """Schema for user login"""
    email: str
    password: str


class UserResponse(BaseModel):
    """Schema for user data in API responses"""
    id: int
    name: str
    email: str
    role: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Allows ORM model → Pydantic conversion


# ============================================================
# RESOURCE SCHEMAS
# ============================================================

class ResourceCreate(BaseModel):
    """Schema for adding a new resource"""
    title: str
    description: Optional[str] = None
    category: str


class ResourceResponse(BaseModel):
    """Schema for resource data in API responses"""
    id: int
    title: str
    description: Optional[str] = None
    category: str
    status: str
    owner_id: int
    owner_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# BOOK SCHEMAS
# ============================================================

class BookCreate(BaseModel):
    """Schema for adding a new book"""
    title: str
    author: Optional[str] = None
    subject: Optional[str] = None


class BookResponse(BaseModel):
    """Schema for book data in API responses"""
    id: int
    title: str
    author: Optional[str] = None
    subject: Optional[str] = None
    status: str
    owner_id: int
    owner_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# REQUEST SCHEMAS
# ============================================================

class RequestCreate(BaseModel):
    """Schema for creating a borrow request"""
    item_id: int
    item_type: str  # 'resource' or 'book'


class RequestAction(BaseModel):
    """Schema for approving/rejecting a request"""
    action: str  # 'approve' or 'reject'


class RequestResponse(BaseModel):
    """Schema for request data in API responses"""
    id: int
    item_id: int
    item_type: str
    requester_id: int
    owner_id: int
    status: str
    borrow_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    requester_name: Optional[str] = None
    owner_name: Optional[str] = None
    item_title: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================
# TOKEN / AUTH SCHEMAS
# ============================================================

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str
    user: UserResponse


class NotificationResponse(BaseModel):
    """Schema for notification messages"""
    id: int
    message: str
    created_at: Optional[datetime] = None
    is_read: bool = False
