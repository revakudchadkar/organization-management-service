from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

# Initialize the MongoDB client
client = AsyncIOMotorClient(settings.MONGO_URI)

# Connect to the Master Database
master_db = client[settings.MASTER_DB_NAME]

# --- Dynamic Database/Collection Utility ---

# Note: In the requirement, you requested dynamic *collections* (org_<name>)
# within the *same* Master Database. This is much simpler than creating entirely 
# new databases, but both are possible. We will use dynamic collections within 
# the Master Database as the immediate requirement states.

def get_org_collection_name(org_name: str) -> str:
    """Generates the required dynamic collection name."""
    return f"org_{org_name.lower().replace(' ', '_')}"

async def create_dynamic_org_collection(org_collection_name: str):
    """
    Creates the dynamic collection for the new organization.
    Since MongoDB is schemaless, simply inserting the first document 
    will create the collection. For initialization, we can create an index.
    """
    if org_collection_name not in await master_db.list_collection_names():
        # Optional: Initialize with an index (e.g., for tenant-specific users)
        collection = master_db[org_collection_name]
        await collection.create_index("user_email", unique=True)
        print(f"Collection '{org_collection_name}' created and indexed.")