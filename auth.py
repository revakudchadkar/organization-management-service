from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Any, Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from config import settings
from models import TokenData # AdminDB is removed here and imported locally below
from database import master_db
from bson import ObjectId

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

# --- Password Utilities ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- JWT Utilities ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# --- Dependency to get the current authenticated Admin ---

# NOTE: The return type 'AdminDB' is wrapped in quotes as a forward reference 
# to break the circular dependency.
async def get_current_admin(token: str = Depends(oauth2_scheme)) -> 'AdminDB':
    """
    Authenticates the user based on the JWT token and fetches Admin details.
    """
    # Import AdminDB locally to resolve circular import dependency
    from models import AdminDB 
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # Expected claims: email (Admin identification, sub), organization_name (Organization identifier, org)
        email: str = payload.get("sub")
        org_name: str = payload.get("org")
        
        if email is None or org_name is None:
            raise credentials_exception
        
        token_data = TokenData(email=email, organization_name=org_name)
    except JWTError:
        raise credentials_exception

    # Fetch admin details from the Master DB to ensure the user still exists
    admin_data = await master_db["admins"].find_one({"email": token_data.email})
    
    if admin_data is None:
        raise credentials_exception
    
    # Use AdminDB model for consistent structure
    admin = AdminDB(**admin_data)
    
    if admin.organization_name != org_name:
        # Token Organization ID does not match current record (e.g., org name was changed)
        raise credentials_exception
        
    return admin