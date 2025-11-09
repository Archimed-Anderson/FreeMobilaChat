"""
Security utilities for authentication
Handles password hashing, JWT token generation and validation
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any
import jwt
import os
from .models import TokenData, UserRole

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours default


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hashed version
    
    Args:
        plain_password: The password entered by the user
        hashed_password: The stored hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password for secure storage
    
    Args:
        password: The plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing user data to encode in token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(UTC)
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """
    Verify and decode a JWT token
    
    Args:
        token: The JWT token to verify
        
    Returns:
        TokenData if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id: int = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if user_id is None or email is None:
            return None
            
        return TokenData(
            user_id=user_id,
            email=email,
            role=UserRole(role) if role else None
        )
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.JWTError:
        # Invalid token
        return None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    
    Args:
        password: The password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    return True, "Password is strong"


def get_role_permissions(role: UserRole) -> Dict[str, bool]:
    """
    Get permissions for a specific user role
    
    Args:
        role: The user role
        
    Returns:
        Dictionary of permission flags
    """
    permissions = {
        UserRole.CLIENT_SAV: {
            "can_view_own_tickets": True,
            "can_create_ticket": True,
            "can_view_dashboard": False,
            "can_analyze_data": False,
            "can_manage_users": False,
            "can_export_data": False
        },
        UserRole.AGENT_SAV: {
            "can_view_own_tickets": True,
            "can_create_ticket": True,
            "can_view_all_tickets": True,
            "can_view_dashboard": True,
            "can_analyze_data": False,
            "can_manage_users": False,
            "can_export_data": True
        },
        UserRole.DATA_ANALYST: {
            "can_view_own_tickets": True,
            "can_create_ticket": True,
            "can_view_all_tickets": True,
            "can_view_dashboard": True,
            "can_analyze_data": True,
            "can_manage_users": False,
            "can_export_data": True,
            "can_train_models": True
        },
        UserRole.MANAGER: {
            "can_view_own_tickets": True,
            "can_create_ticket": True,
            "can_view_all_tickets": True,
            "can_view_dashboard": True,
            "can_analyze_data": True,
            "can_manage_users": True,
            "can_export_data": True,
            "can_train_models": True,
            "can_view_reports": True
        }
    }
    
    return permissions.get(role, {})

