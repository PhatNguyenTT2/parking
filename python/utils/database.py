"""
Database connection module
Handles MongoDB connection using Motor (async driver)
"""
from motor.motor_asyncio import AsyncIOMotorClient
from utils.config import MONGODB_URI
from utils.logger import info, error

# Global database client
client = None
db = None

async def connect_db():
    """Connect to MongoDB"""
    global client, db
    
    try:
        info('connecting to', MONGODB_URI)
        client = AsyncIOMotorClient(MONGODB_URI)
        
        # Get database from URI or use default
        db = client.get_default_database()
        
        # Test connection
        await client.admin.command('ping')
        info('connected to MongoDB')
        
    except Exception as e:
        error('error connecting to MongoDB:', str(e))
        raise

async def close_db():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        info('MongoDB connection closed')

def get_database():
    """Get database instance"""
    return db

def get_collection(name: str):
    """Get collection by name"""
    return db[name]
