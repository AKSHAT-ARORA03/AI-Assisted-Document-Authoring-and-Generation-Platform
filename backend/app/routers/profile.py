"""
Profile and statistics endpoints for the API.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import random
from app.utils.auth import get_current_user, get_current_user_optional

router = APIRouter(tags=["Profile"])

# In-memory storage for profiles (fallback when MongoDB is not available)
profile_storage = {}

def get_universal_user_id(user=None):
    """Get user ID with universal fallback support"""
    if user:
        return getattr(user, 'id', getattr(user, 'user_id', 'test_user_123'))
    return 'test_user_123'

@router.get("/profile")
async def get_user_profile(current_user = Depends(get_current_user_optional)):
    """Get user profile information"""
    from app.utils.database import get_collection
    
    user_id = get_universal_user_id(current_user)
    user_email = getattr(current_user, 'email', 'akshatarora1299@gmail.com')
    
    try:
        # Try MongoDB first
        users_collection = await get_collection("users")
        if users_collection:
            user_doc = await users_collection.find_one({"$or": [
                {"user_id": user_id}, 
                {"email": user_email}
            ]})
            
            if user_doc:
                return {
                    "id": user_id,
                    "email": user_email,
                    "name": user_doc.get("name", "User"),
                    "bio": user_doc.get("bio", ""),
                    "company": user_doc.get("company", ""),
                    "title": user_doc.get("title", ""),
                    "location": user_doc.get("location", "")
                }
    except Exception as e:
        print(f"MongoDB error in get_profile: {e}")
    
    # Fallback to memory storage
    if user_id in profile_storage:
        stored_profile = profile_storage[user_id]
        return {
            "id": user_id,
            "email": user_email,
            "name": stored_profile.get("name", "User"),
            "bio": stored_profile.get("bio", ""),
            "company": stored_profile.get("company", ""),
            "title": stored_profile.get("title", ""),
            "location": stored_profile.get("location", "")
        }
    
    # Return basic profile
    return {
        "id": user_id,
        "email": user_email,
        "name": "User",
        "bio": "",
        "company": "",
        "title": "",
        "location": ""
    }

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None

class UserPreferences(BaseModel):
    notifications: bool = True
    emailUpdates: bool = False
    autoSave: bool = True
    defaultFormat: str = "word"

class UserActivity(BaseModel):
    type: str
    title: str
    timestamp: datetime

@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user = Depends(get_current_user_optional)
):
    """Update user profile information"""
    from app.utils.database import get_collection
    
    user_id = get_universal_user_id(current_user)
    user_email = getattr(current_user, 'email', 'akshatarora1299@gmail.com')
    
    # Create profile data
    update_data = {
        "user_id": user_id,
        "email": user_email,
        "updated_at": datetime.now().isoformat()
    }
    
    # Add non-null fields from the request
    if profile_data.name:
        update_data["name"] = profile_data.name
    if profile_data.bio is not None:
        update_data["bio"] = profile_data.bio
    if profile_data.company is not None:
        update_data["company"] = profile_data.company
    if profile_data.title is not None:
        update_data["title"] = profile_data.title
    if profile_data.location is not None:
        update_data["location"] = profile_data.location
    
    try:
        # Try MongoDB first
        users_collection = await get_collection("users")
        if users_collection:
            await users_collection.update_one(
                {"$or": [{"user_id": user_id}, {"email": user_email}]},
                {"$set": update_data},
                upsert=True
            )
            print(f"✅ MongoDB: Profile updated for user {user_id}: {update_data}")
        else:
            raise Exception("No MongoDB connection")
            
    except Exception as e:
        print(f"❌ MongoDB error: {e}")
        # Fallback to memory storage
        profile_storage[user_id] = update_data
        print(f"✅ Memory: Profile stored for user {user_id}: {update_data}")
    
    # Return the updated profile
    return {
        "id": user_id,
        "email": user_email,
        "name": update_data.get("name", "User"),
        "bio": update_data.get("bio", ""),
        "company": update_data.get("company", ""),
        "title": update_data.get("title", ""),
        "location": update_data.get("location", "")
    }

@router.get("/stats")
async def get_user_stats(current_user = Depends(get_current_user_optional)):
    """Get user statistics"""
    from app.utils.database import get_collection
    
    user_id = get_universal_user_id(current_user)
    
    try:
        # Get real project count from database
        projects_collection = await get_collection("projects")
        if projects_collection:
            project_count = await projects_collection.count_documents({"user_id": user_id})
        else:
            project_count = 0
            
        # Calculate documents created (each project can have multiple sections)
        documents_created = project_count * 2 if project_count > 0 else 0
        
        # Calculate time saved (estimate based on projects)
        time_saved = project_count * 3 if project_count > 0 else 0
        
        # Get user creation date or use reasonable default
        join_date = getattr(current_user, 'created_at', None)
        if not join_date:
            join_date = (datetime.now() - timedelta(days=30)).isoformat()
        elif hasattr(join_date, 'isoformat'):
            join_date = join_date.isoformat()
        
        return {
            "totalProjects": project_count,
            "documentsCreated": documents_created,
            "timesSaved": time_saved,
            "joinDate": join_date
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        # Fallback to basic stats
        return {
            "totalProjects": 0,
            "documentsCreated": 0,
            "timesSaved": 0,
            "joinDate": (datetime.now() - timedelta(days=30)).isoformat()
        }

@router.get("/activities")
async def get_user_activities(current_user = Depends(get_current_user_optional)):
    """Get user recent activities"""
    from app.utils.database import get_collection
    
    user_id = get_universal_user_id(current_user)
    
    try:
        # Get real projects from database
        projects_collection = await get_collection("projects")
        activities = []
        
        if projects_collection:
            # Get recent projects
            recent_projects = await projects_collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(5).to_list(length=5)
            
            for project in recent_projects:
                activities.append({
                    "type": "project_created",
                    "title": f"Created project: {project.get('title', 'Untitled Project')}",
                    "timestamp": project.get("created_at", datetime.now()).isoformat() if isinstance(project.get("created_at"), datetime) else project.get("created_at", datetime.now().isoformat())
                })
                
                # Add document export activity if project is completed
                if project.get("status") == "completed":
                    activities.append({
                        "type": "document_exported",
                        "title": f"Exported document: {project.get('title', 'Untitled')}.{project.get('document_type', 'docx')}",
                        "timestamp": project.get("updated_at", project.get("created_at", datetime.now())).isoformat() if isinstance(project.get("updated_at"), datetime) else project.get("updated_at", datetime.now().isoformat())
                    })
        
        # Sort activities by timestamp and limit to 5
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:5]
        
    except Exception as e:
        print(f"Error getting activities: {e}")
        # Fallback activities
        return [
            {
                "type": "project_created",
                "title": "Welcome to AI Document Platform!",
                "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat()
            }
        ]

@router.get("/preferences")
async def get_user_preferences(current_user = Depends(get_current_user_optional)):
    """Get user preferences"""
    from app.utils.database import get_collection
    
    user_id = get_universal_user_id(current_user)
    
    try:
        users_collection = await get_collection("users")
        if users_collection:
            user_doc = await users_collection.find_one({"user_id": user_id})
            if user_doc and "preferences" in user_doc:
                return user_doc["preferences"]
    except Exception as e:
        print(f"Error getting preferences: {e}")
    
    # Return default preferences
    return {
        "notifications": True,
        "emailUpdates": False,
        "autoSave": True,
        "defaultFormat": "word"
    }

@router.put("/preferences")
async def update_user_preferences(
    preferences: UserPreferences,
    current_user = Depends(get_current_user_optional)
):
    """Update user preferences"""
    from app.utils.database import get_collection
    
    user_id = get_universal_user_id(current_user)
    
    try:
        users_collection = await get_collection("users")
        if users_collection:
            await users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"preferences": preferences.dict()}},
                upsert=True
            )
    except Exception as e:
        print(f"Error updating preferences: {e}")
    
    return preferences.dict()