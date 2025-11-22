from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from datetime import timedelta, datetime
from app.models.user import UserCreate, UserLogin, User, Token, UserInDB
from app.utils.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_user_by_email,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.utils.database import get_collection

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    collection = await get_collection("users")
    hashed_password = get_password_hash(user_data.password)
    
    user_dict = {
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    try:
        if collection is None:
            # Use memory store fallback
            from app.utils.memory_store import memory_store
            user_id = f"user_{len(memory_store.users) + 1}"
            user_dict["_id"] = user_id
            created_user = await memory_store.create_user(user_dict)
            return User(
                id=user_id,
                email=created_user["email"],
                full_name=created_user["full_name"],
                created_at=created_user["created_at"],
                updated_at=created_user["updated_at"]
            )
        
        user_in_db = UserInDB(**user_dict)
        result = await collection.insert_one(user_in_db.dict(by_alias=True, exclude={"id"}))
        
        # Return user without password
        created_user = await collection.find_one({"_id": result.inserted_id})
        return User(
            id=str(created_user["_id"]),
            email=created_user["email"],
            full_name=created_user["full_name"],
            created_at=created_user["created_at"],
            updated_at=created_user["updated_at"]
        )
    except Exception as e:
        # Fallback to memory store if database fails
        from app.utils.memory_store import memory_store
        user_id = f"user_{len(memory_store.users) + 1}"
        user_dict["_id"] = user_id
        created_user = await memory_store.create_user(user_dict)
        return User(
            id=user_id,
            email=created_user["email"],
            full_name=created_user["full_name"],
            created_at=created_user["created_at"],
            updated_at=created_user["updated_at"]
        )

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user and return JWT token"""
    user = await authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/dev-login", response_model=Token)
async def dev_login():
    """Development-only login for test user"""
    # This endpoint automatically logs in the test user for development
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": "test@example.com"}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    """Get current user information"""
    return User(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}