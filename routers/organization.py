from fastapi import APIRouter, HTTPException, status, Depends
from models import OrganizationCreate, OrganizationDB, AdminDB, OrganizationBase
from database import master_db, get_org_collection_name, create_dynamic_org_collection
from auth import get_password_hash, get_current_admin
from bson import ObjectId

org_router = APIRouter(prefix="/org", tags=["Organization Management"])

@org_router.post("/create", response_model=OrganizationDB)
async def create_organization(org_data: OrganizationCreate):
    """
    Creates a new Organization, Admin user, and dynamic collection.
    (Functional Requirement 1)
    """
    # 1. Validate that the organization name does not already exist.
    existing_org = await master_db["organizations"].find_one(
        {"organization_name": org_data.organization_name}
    )
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization name already exists."
        )

    # 2. Prepare data
    org_collection_name = get_org_collection_name(org_data.organization_name)
    hashed_password = get_password_hash(org_data.password)

    # 3. Store Admin user (Master Database: admins collection)
    # Note: We must insert the admin first to get the Admin ID reference.
    admin_user = AdminDB(
        email=org_data.email, 
        hashed_password=hashed_password, 
        organization_id="", # Placeholder, will be updated after org insert
        organization_name=org_data.organization_name
    )
    admin_result = await master_db["admins"].insert_one(admin_user.model_dump(exclude={"id"}))
    admin_id = str(admin_result.inserted_id)

    # 4. Store Organization metadata (Master Database: organizations collection)
    org_db_entry = OrganizationDB(
        organization_name=org_data.organization_name,
        org_collection_name=org_collection_name,
        admin_user_id=admin_id,
        # Connection details are implicitly the Master DB URI
    )
    org_result = await master_db["organizations"].insert_one(org_db_entry.model_dump(exclude={"id"}))
    org_id = str(org_result.inserted_id)

    # 5. Update the admin record with the final organization_id
    await master_db["admins"].update_one(
        {"_id": ObjectId(admin_id)}, 
        {"$set": {"organization_id": org_id}}
    )
    
    # 6. Dynamically create a new Mongo collection
    await create_dynamic_org_collection(org_collection_name)

    # 7. Return success response
    org_db_entry.id = org_id
    return org_db_entry


@org_router.get("/get", response_model=OrganizationDB)
async def get_organization(organization_name: str):
    """
    Fetches organization details from the Master Database.
    (Functional Requirement 2)
    """
    organization_data = await master_db["organizations"].find_one(
        {"organization_name": organization_name}
    )

    if not organization_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{organization_name}' not found."
        )
        
    return OrganizationDB(**organization_data)


@org_router.put("/update", response_model=OrganizationDB)
async def update_organization(
    old_name: str, 
    new_org_data: OrganizationCreate, 
    current_admin: AdminDB = Depends(get_current_admin)
):
    """
    Updates Organization, Admin user, and dynamically handles collection rename/move.
    (Functional Requirement 3)
    """
    # 1. Verify the organization exists and the current admin belongs to it.
    organization_data = await master_db["organizations"].find_one(
        {"organization_name": old_name}
    )
    if not organization_data or current_admin.organization_name != old_name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{old_name}' not found or unauthorized."
        )

    # 2. Validate that the new organization name does not already exist (if name is changing)
    if old_name != new_org_data.organization_name:
        existing_org = await master_db["organizations"].find_one(
            {"organization_name": new_org_data.organization_name}
        )
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New organization name already exists."
            )

    # --- Dynamic Collection Handling (Rename/Sync) ---
    old_collection_name = get_org_collection_name(old_name)
    new_collection_name = get_org_collection_name(new_org_data.organization_name)
    
    # This block performs the "sync existing data to the new Table/Collection" step 
    # by renaming the existing collection if the name has changed.
    if old_collection_name != new_collection_name:
        await master_db.get_collection(old_collection_name).rename(new_collection_name)
    
    # --- Update Master Database Records ---
    
    # Update Admin Record
    new_hashed_password = get_password_hash(new_org_data.password)
    await master_db["admins"].update_one(
        {"_id": ObjectId(current_admin.id)},
        {"$set": {
            "email": new_org_data.email, 
            "hashed_password": new_hashed_password,
            "organization_name": new_org_data.organization_name
        }}
    )

    # Update Organization Metadata
    update_data = {
        "organization_name": new_org_data.organization_name,
        "org_collection_name": new_collection_name,
    }
    
    result = await master_db["organizations"].update_one(
        {"_id": organization_data["_id"]},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        # If no modification, fetch the current data
        updated_data = organization_data
    else:
        # Fetch the newly updated data
        updated_data = await master_db["organizations"].find_one({"_id": organization_data["_id"]})
        
    return OrganizationDB(**updated_data)


@org_router.delete("/delete")
async def delete_organization(organization_name: str, current_admin: AdminDB = Depends(get_current_admin)):
    """
    Deletes an Organization, its Admin, and its dynamic collection.
    (Functional Requirement 4)
    """
    # 1. Allow deletion for respective authenticated user only
    if current_admin.organization_name != organization_name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You can only delete the organization you administer."
        )

    # 2. Get organization metadata
    org_data = await master_db["organizations"].find_one(
        {"organization_name": organization_name}
    )
    if not org_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{organization_name}' not found."
        )
    
    org_collection_name = org_data["org_collection_name"]
    admin_id = org_data["admin_user_id"]
    
    # 3. Handle deletion of the relevant collections/records

    # Delete Dynamic Collection
    await master_db.get_collection(org_collection_name).drop()
    
    # Delete Admin user from Master DB
    await master_db["admins"].delete_one({"_id": ObjectId(admin_id)})
    
    # Delete Organization Metadata from Master DB
    await master_db["organizations"].delete_one({"_id": org_data["_id"]})

    return {"message": f"Organization '{organization_name}' and all associated data deleted successfully."}