from fastapi import FastAPI
from routers.organization import org_router
from routers.admin import admin_router

# Initialize the FastAPI application
app = FastAPI(
    title="Organization Management Service",
    description="Multi-tenant backend service for managing organizations.",
    version="1.0.0"
)

# Include the routers
app.include_router(org_router)
app.include_router(admin_router)

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Organization Management Service API"}