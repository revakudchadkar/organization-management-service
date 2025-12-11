from pydantic import BaseModel, EmailStr
from typing import Optional

# --- Master Database Models (Collections: organizations, admins) ---

class OrganizationBase(BaseModel):
    organization_name: str

class OrganizationCreate(OrganizationBase):
    email: EmailStr
    password: str

class OrganizationDB(OrganizationBase):
    id: Optional[str] = None
    org_collection_name: str
    admin_user_id: str
    
    class Config:
        # Allows conversion from MongoDB's '_id' to 'id'
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            str: lambda v: str(v),
        }

class AdminDB(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    hashed_password: str
    organization_id: str # Reference to the OrganizationDB entry
    organization_name: str
    
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            str: lambda v: str(v),
        }

# --- Login & Token Models ---

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    organization_name: Optional[str] = None