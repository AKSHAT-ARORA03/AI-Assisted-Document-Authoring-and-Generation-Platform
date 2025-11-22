from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None

database = Database()

async def get_database() -> AsyncIOMotorClient:
    return database.client

async def connect_to_mongo():
    """Create database connection with fallback handling"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/document_platform")
    
    try:
        database.client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=5000)
        # Test the connection
        await database.client.admin.command('ping')
        print("Connected to MongoDB successfully")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Note: For development, install MongoDB locally or use MongoDB Atlas")
        # For development purposes, we'll still create a client but won't crash
        try:
            database.client = AsyncIOMotorClient("mongodb://localhost:27017/document_platform", serverSelectionTimeoutMS=1000)
        except:
            print("Could not establish any MongoDB connection. Some features may not work.")
            database.client = None

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()
        print("Disconnected from MongoDB")

async def get_collection(collection_name: str):
    """Get a collection from the database"""
    try:
        client = await get_database()
        if client is None:
            print(f"No database connection available for collection: {collection_name}")
            return None
        db = client.get_database("document_platform")
        return db.get_collection(collection_name)
    except Exception as e:
        print(f"Error getting collection {collection_name}: {e}")
        return None