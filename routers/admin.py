from fastapi import APIRouter, HTTPException, status, Depends
from models import AdminLogin, Token, AdminDB
from database import master_db
from auth import verify_password, create_access_token
from config import settings
from datetime import timedelta

admin_router = APIRouter(prefix="/admin", tags=["Admin Authentication"])

@admin_router.post("/login", response_model=Token)
async def admin_login(form_data: AdminLogin):
    """
    Handles Admin Login and returns a JWT token.
    (Functional Requirement 5)
    """
    admin_data = await master_db["admins"].find_one({"email": form_data.email})
    
    if not admin_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
        
    admin = AdminDB(**admin_data)
    
    if not verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
        
    # On success, return a JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # JWT Payload: Admin identification (sub=email), Organization identifier/ID (org=organization_name)
    access_token = create_access_token(
        data={"sub": admin.email, "org": admin.organization_name},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}