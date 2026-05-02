"""
Authentication Router
---------------------
Handles user registration and login endpoints.

Endpoints:
- POST /api/auth/register - Register a new user
- POST /api/auth/login    - Login and get JWT token
- GET  /api/auth/me       - Get current user profile
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import User
from ..schemas.schemas import UserCreate, UserLogin, UserResponse, Token
from ..utils.auth import hash_password, verify_password, create_access_token, get_current_user

# Create router with prefix and tags
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ============================================================
# REGISTER ENDPOINT
# ============================================================

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Steps:
    1. Check if email already exists
    2. Hash the password
    3. Create user in database
    4. Generate JWT token
    5. Return token and user data
    """
    # Step 1: Check for existing email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Step 2: Hash password for secure storage
    hashed_pw = hash_password(user_data.password)
    
    # Step 3: Create new user object
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_pw,
        role=user_data.role
    )
    
    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh to get the auto-generated ID
    
    # Step 4: Generate JWT token
    access_token = create_access_token(data={"user_id": new_user.id})
    
    # Step 5: Return response
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
            role=new_user.role,
            created_at=new_user.created_at
        )
    )


# ============================================================
# LOGIN ENDPOINT
# ============================================================

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    
    Steps:
    1. Find user by email
    2. Verify password
    3. Generate and return JWT token
    """
    # Step 1: Find user
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Step 2: Verify password
    if not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Step 3: Generate token
    access_token = create_access_token(data={"user_id": user.id})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            created_at=user.created_at
        )
    )


# ============================================================
# GET CURRENT USER ENDPOINT
# ============================================================

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the currently authenticated user's profile.
    Requires valid JWT token in Authorization header.
    """
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at
    )
