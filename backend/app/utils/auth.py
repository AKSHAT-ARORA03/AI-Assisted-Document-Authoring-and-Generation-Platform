from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user import TokenData, UserInDB
from app.utils.database import get_collection
import os
from dotenv import load_dotenv

load_dotenv()

# Security configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get user by email from database"""
    try:
        collection = await get_collection("users")
        if collection is None:
            # Fallback to memory store
            from app.utils.memory_store import memory_store
            user_data = await memory_store.find_user_by_email(email)
            if user_data:
                return UserInDB(**user_data)
            return None
        
        user_data = await collection.find_one({"email": email})
        if user_data:
            return UserInDB(**user_data)
        return None
    except Exception as e:
        print(f"Database error in get_user_by_email: {e}")
        # Fallback to memory store
        try:
            from app.utils.memory_store import memory_store
            user_data = await memory_store.find_user_by_email(email)
            if user_data:
                # For memory store, create a compatible object without ObjectId validation
                user_dict = user_data.copy()
                # Ensure we have a valid id field
                if '_id' not in user_dict:
                    user_dict['_id'] = user_dict.get('id', 'test_user_123')
                # Return a UserInDB-like object
                return type('MemoryUser', (), {
                    'id': str(user_dict.get('_id', user_dict.get('id', 'test_user_123'))),
                    'email': user_dict['email'],
                    'full_name': user_dict['full_name'],
                    'hashed_password': user_dict['hashed_password'],
                    'created_at': user_dict.get('created_at', datetime.utcnow()),
                    'updated_at': user_dict.get('updated_at', datetime.utcnow())
                })()
            return None
        except Exception as fallback_error:
            print(f"Memory store error: {fallback_error}")
            return None

async def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    """Authenticate user with email and password"""
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInDB:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        if not SECRET_KEY:
            raise credentials_exception
            
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_email(email=token_data.email or "")
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)):
    """Get current authenticated user from JWT token, return None if not authenticated"""
    if not credentials or not SECRET_KEY:
        return None
        
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            return None
            
        # For development, if it's the test user email, return a simple user object
        if email == "test@example.com":
            return type('TestUser', (), {
                'id': 'test_user_123',
                'email': 'test@example.com',
                'full_name': 'Test User',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })()
            
        user = await get_user_by_email(email)
        return user
    except JWTError:
        return None