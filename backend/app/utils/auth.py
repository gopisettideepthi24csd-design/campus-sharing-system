"""
Authentication Utility Module
------------------------------
Handles:
- Password hashing using bcrypt (via passlib)
- JWT token creation and verification
- Current user extraction from token

Security Flow:
1. User registers → password is hashed and stored
2. User logs in → credentials verified → JWT token issued
3. Protected routes → token extracted from header → user identified
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import User

# ============================================================
# CONFIGURATION
# ============================================================

# Secret key for JWT encoding (in production, use environment variable)
SECRET_KEY = os.getenv("SECRET_KEY", "campus-sharing-secret-key-2024")
ALGORITHM = "HS256"  # Hashing algorithm for JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Token valid for 24 hours

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token security scheme
security = HTTPBearer()


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    Returns the hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hash.
    Returns True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================
# JWT TOKEN FUNCTIONS
# ============================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing claims (e.g., user_id)
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Encode the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.
    
    Returns:
        Decoded payload dictionary, or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ============================================================
# DEPENDENCY: GET CURRENT USER
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to extract the current authenticated user.
    
    Flow:
    1. Extract token from Authorization header
    2. Decode and verify the token
    3. Fetch user from database
    4. Return user object
    
    Raises HTTPException 401 if authentication fails.
    """
    token = credentials.credentials
    
    # Verify the token
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user ID from token payload
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user
