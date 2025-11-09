"""
User authentication models
Defines data structures for user management and authentication
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles in the system"""
    CLIENT_SAV = "client_sav"
    AGENT_SAV = "agent_sav"
    DATA_ANALYST = "data_analyst"
    MANAGER = "manager"


class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)
    role: UserRole


class UserCreate(UserBase):
    """Model for user registration"""
    password: str = Field(min_length=8, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "role": "client_sav",
                "password": "securepassword123"
            }
        }


class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class User(UserBase):
    """Complete user model with all fields"""
    id: int
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserInDB(User):
    """User model with hashed password for database storage"""
    hashed_password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: User


class TokenData(BaseModel):
    """Data extracted from JWT token"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None


class UserUpdate(BaseModel):
    """Model for updating user information"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Jane Doe",
                "email": "jane@example.com"
            }
        }


class PasswordChange(BaseModel):
    """Model for password change"""
    current_password: str
    new_password: str = Field(min_length=8, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newpassword456"
            }
        }

