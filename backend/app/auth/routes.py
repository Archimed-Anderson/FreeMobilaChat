"""
Authentication API routes
Handles user registration, login, and authentication endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
from datetime import timedelta

from .models import User, UserCreate, UserLogin, Token, PasswordChange, UserUpdate
from .database import AuthDatabase
from .security import (
    verify_password,
    create_access_token,
    verify_token,
    get_password_hash,
    validate_password_strength,
    get_role_permissions
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Security scheme
security = HTTPBearer()

# Initialize database
auth_db = AuthDatabase()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    
    Args:
        credentials: Bearer token from request header
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    token_data = verify_token(token)
    
    if token_data is None or token_data.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_db.get_user_by_id(token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    return user


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_create: UserCreate):
    """
    Register a new user
    
    Args:
        user_create: User registration data
        
    Returns:
        JWT token and user information
        
    Raises:
        HTTPException: If user already exists or validation fails
    """
    logger.info(f"Signup attempt for email: {user_create.email}")
    
    # Check if user already exists
    if auth_db.user_exists(user_create.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    is_valid, message = validate_password_strength(user_create.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Create user
    user = auth_db.create_user(user_create)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Update last login
    auth_db.update_last_login(user.id)
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user.id,
            "email": user.email,
            "role": user.role.value
        }
    )
    
    logger.info(f"User registered successfully: {user.email}")
    
    return Token(
        access_token=access_token,
        user=user
    )


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin):
    """
    Authenticate user and return JWT token
    
    Args:
        user_login: User login credentials
        
    Returns:
        JWT token and user information
        
    Raises:
        HTTPException: If credentials are invalid
    """
    logger.info(f"Login attempt for email: {user_login.email}")
    
    # Get user from database
    user_in_db = auth_db.get_user_by_email(user_login.email)
    if user_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(user_login.password, user_in_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user_in_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    
    # Update last login
    auth_db.update_last_login(user_in_db.id)
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user_in_db.id,
            "email": user_in_db.email,
            "role": user_in_db.role.value
        }
    )
    
    # Get user without password
    user = auth_db.get_user_by_id(user_in_db.id)
    
    logger.info(f"User logged in successfully: {user_login.email}")
    
    return Token(
        access_token=access_token,
        user=user
    )


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Args:
        current_user: Current user from JWT token
        
    Returns:
        Current user information
    """
    return current_user


@router.get("/me/permissions")
async def get_my_permissions(current_user: User = Depends(get_current_user)):
    """
    Get current user's permissions based on role
    
    Args:
        current_user: Current user from JWT token
        
    Returns:
        Dictionary of permissions
    """
    permissions = get_role_permissions(current_user.role)
    return {
        "user_id": current_user.id,
        "role": current_user.role,
        "permissions": permissions
    }


@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's information
    
    Args:
        user_update: User update data
        current_user: Current user from JWT token
        
    Returns:
        Updated user information
    """
    update_data = user_update.dict(exclude_unset=True)
    
    if not update_data:
        return current_user
    
    updated_user = auth_db.update_user(current_user.id, **update_data)
    
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )
    
    logger.info(f"User updated: {current_user.email}")
    return updated_user


@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user)
):
    """
    Change user password
    
    Args:
        password_change: Current and new password
        current_user: Current user from JWT token
        
    Returns:
        Success message
    """
    # Get user with hashed password
    user_in_db = auth_db.get_user_by_email(current_user.email)
    
    if user_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_change.current_password, user_in_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    is_valid, message = validate_password_strength(password_change.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Update password
    try:
        conn = auth_db.get_connection()
        cursor = conn.cursor()
        
        new_hashed_password = get_password_hash(password_change.new_password)
        cursor.execute(
            "UPDATE users SET hashed_password = ? WHERE id = ?",
            (new_hashed_password, current_user.id)
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Password changed for user: {current_user.email}")
        
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.post("/verify-token")
async def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify if JWT token is valid
    
    Args:
        credentials: Bearer token from request header
        
    Returns:
        Token validity status and user information
    """
    token = credentials.credentials
    token_data = verify_token(token)
    
    if token_data is None:
        return {
            "valid": False,
            "message": "Invalid or expired token"
        }
    
    user = auth_db.get_user_by_id(token_data.user_id)
    if user is None:
        return {
            "valid": False,
            "message": "User not found"
        }
    
    return {
        "valid": True,
        "user": user,
        "message": "Token is valid"
    }


@router.get("/health")
async def auth_health_check():
    """
    Health check endpoint for authentication service
    
    Returns:
        Service status
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "database": "connected"
    }

