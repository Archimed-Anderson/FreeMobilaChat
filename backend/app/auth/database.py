"""
Authentication database manager
Handles user data storage and retrieval using SQLite
"""

import sqlite3
import logging
from typing import Optional, List
from datetime import datetime, UTC
from pathlib import Path
from .models import User, UserInDB, UserRole, UserCreate
from .security import get_password_hash

logger = logging.getLogger(__name__)


class AuthDatabase:
    """Database manager for authentication"""
    
    def __init__(self, db_path: str = "backend/data/users.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        # Ensure directory exists
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a new database connection"""
        conn = sqlite3.Connection(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            )
        """)
        
        # Create index on email for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email 
            ON users(email)
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("Authentication database initialized")
    
    def create_user(self, user_create: UserCreate) -> Optional[User]:
        """
        Create a new user
        
        Args:
            user_create: User creation data
            
        Returns:
            Created User object or None if failed
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Hash password
            hashed_password = get_password_hash(user_create.password)
            
            # Insert user
            cursor.execute("""
                INSERT INTO users (email, full_name, hashed_password, role)
                VALUES (?, ?, ?, ?)
            """, (
                user_create.email,
                user_create.full_name,
                hashed_password,
                user_create.role.value
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # Get created user
            user = self.get_user_by_id(user_id)
            conn.close()
            
            logger.info(f"User created successfully: {user_create.email}")
            return user
            
        except sqlite3.IntegrityError:
            logger.warning(f"User already exists: {user_create.email}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """
        Get user by email address
        
        Args:
            email: User email address
            
        Returns:
            UserInDB object or None if not found
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return UserInDB(
                    id=row["id"],
                    email=row["email"],
                    full_name=row["full_name"],
                    hashed_password=row["hashed_password"],
                    role=UserRole(row["role"]),
                    is_active=bool(row["is_active"]),
                    is_verified=bool(row["is_verified"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    last_login=datetime.fromisoformat(row["last_login"]) if row["last_login"] else None
                )
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(
                    id=row["id"],
                    email=row["email"],
                    full_name=row["full_name"],
                    role=UserRole(row["role"]),
                    is_active=bool(row["is_active"]),
                    is_verified=bool(row["is_verified"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    last_login=datetime.fromisoformat(row["last_login"]) if row["last_login"] else None
                )
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    def update_last_login(self, user_id: int) -> bool:
        """
        Update user's last login timestamp
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET last_login = ? 
                WHERE id = ?
            """, (datetime.now(UTC).isoformat(), user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users with pagination
        
        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            List of User objects
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM users 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (limit, skip))
            
            rows = cursor.fetchall()
            conn.close()
            
            users = []
            for row in rows:
                users.append(User(
                    id=row["id"],
                    email=row["email"],
                    full_name=row["full_name"],
                    role=UserRole(row["role"]),
                    is_active=bool(row["is_active"]),
                    is_verified=bool(row["is_verified"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    last_login=datetime.fromisoformat(row["last_login"]) if row["last_login"] else None
                ))
            
            return users
            
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """
        Update user information
        
        Args:
            user_id: User ID
            **kwargs: Fields to update
            
        Returns:
            Updated User object or None if failed
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build update query dynamically
            allowed_fields = ["full_name", "email", "is_active", "is_verified"]
            update_fields = []
            update_values = []
            
            for key, value in kwargs.items():
                if key in allowed_fields:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            if not update_fields:
                return self.get_user_by_id(user_id)
            
            update_values.append(user_id)
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            
            cursor.execute(query, tuple(update_values))
            conn.commit()
            conn.close()
            
            return self.get_user_by_id(user_id)
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user (soft delete by setting is_active=False)
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    def user_exists(self, email: str) -> bool:
        """
        Check if user exists by email
        
        Args:
            email: User email address
            
        Returns:
            True if user exists, False otherwise
        """
        user = self.get_user_by_email(email)
        return user is not None

