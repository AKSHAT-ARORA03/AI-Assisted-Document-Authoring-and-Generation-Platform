from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from bson import ObjectId
from app.models.user import UserInDB
from app.models.project import (
    Project, ProjectCreate, ProjectUpdate, ProjectInDB,
    Section, Slide
)
from app.utils.auth import get_current_user, get_current_user_optional
from app.utils.database import get_collection
from app.utils.memory_store import memory_project_store
import uuid
from datetime import datetime

# Router with universal user support - MongoDB-first approach
router = APIRouter()

async def get_universal_user_id(current_user) -> str:
    """Get user ID with universal fallback for development"""
    if current_user and hasattr(current_user, 'id'):
        return str(current_user.id)
    return "test_user_123"  # Consistent fallback for development

async def create_project_impl(project_data: ProjectCreate, current_user):
    """Create a new project - MongoDB FIRST for ALL users"""
    user_id = await get_universal_user_id(current_user)
    
    project_dict = {
        "title": project_data.title,
        "document_type": project_data.document_type,
        "topic": project_data.topic,
        "description": project_data.description,
        "user_id": user_id,
        "sections": [] if project_data.document_type == "docx" else None,
        "slides": [] if project_data.document_type == "pptx" else None,
        "status": "draft",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Try MongoDB FIRST for persistence
    collection = await get_collection("projects")
    if collection is not None:
        try:
            from app.models.project import ProjectInDB
            project_in_db = ProjectInDB(**project_dict)
            result = await collection.insert_one(project_in_db.dict(by_alias=True, exclude={"id"}))
            
            # Return created project
            created_project = await collection.find_one({"_id": result.inserted_id})
            if created_project:
                created_project["id"] = str(created_project["_id"])
                return Project(**created_project)
        except Exception as e:
            print(f"MongoDB error, using memory store: {e}")
    
    # Fallback to memory store
    created_project = await memory_project_store.create_project(project_dict)
    return Project(**created_project)

async def get_user_projects_impl(skip: int, limit: int, document_type: Optional[str], search: Optional[str], current_user):
    """Get user projects - MongoDB FIRST for ALL users"""
    user_id = await get_universal_user_id(current_user)
    
    # Try MongoDB FIRST for persistence
    collection = await get_collection("projects")
    if collection is not None:
        try:
            filter_query = {"user_id": user_id}
            
            if document_type:
                filter_query["document_type"] = document_type
            
            if search:
                filter_query["$or"] = [
                    {"title": {"$regex": search, "$options": "i"}},
                    {"topic": {"$regex": search, "$options": "i"}}
                ]
            
            cursor = collection.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)
            projects = await cursor.to_list(length=limit)
            
            # Return MongoDB results directly (don't fall back to memory store)
            return [Project(**project, id=str(project["_id"])) for project in projects]
        except Exception as e:
            print(f"MongoDB error, using memory store: {e}")
    
    # Only use memory store if MongoDB completely fails
    try:
        projects = await memory_project_store.find_projects_by_user(user_id, search or "", document_type or "")
        paginated_projects = projects[skip:skip + limit]
        return [Project(**project) for project in paginated_projects]
    except Exception as e:
        print(f"Memory store also failed: {e}")
        return []  # Return empty list instead of error

@router.get("/health")
async def projects_health():
    """Health check for projects router"""
    return {"message": "Projects router operational", "universal_support": True}

@router.post("", response_model=Project)
async def create_project_no_slash(
    project_data: ProjectCreate,
    current_user = Depends(get_current_user_optional)
):
    """Create a new project - Universal support for ALL users"""
    return await create_project_impl(project_data, current_user)

@router.post("/", response_model=Project)
async def create_project_with_slash(
    project_data: ProjectCreate,
    current_user = Depends(get_current_user_optional)
):
    """Create a new project - endpoint with trailing slash"""
    return await create_project_impl(project_data, current_user)

async def create_project_impl(project_data: ProjectCreate, current_user):
    """Create a new project implementation"""
    collection = await get_collection("projects")
    
    # Generate IDs for sections or slides
    if project_data.document_type == "docx" and project_data.sections:
        sections = []
        for i, section_data in enumerate(project_data.sections):
            section = Section(
                id=str(uuid.uuid4()),
                title=section_data.title,
                order=section_data.order
            )
            sections.append(section)
    else:
        sections = None
    
    if project_data.document_type == "pptx" and project_data.slides:
        slides = []
        for i, slide_data in enumerate(project_data.slides):
            slide = Slide(
                id=str(uuid.uuid4()),
                title=slide_data.title,
                order=slide_data.order
            )
            slides.append(slide)
    else:
        slides = None
    
    project_dict = {
        "title": project_data.title,
        "document_type": project_data.document_type,
        "topic": project_data.topic,
        "description": project_data.description,
        "user_id": str(current_user.id) if current_user else "test_user_123",
        "sections": [section.dict() for section in sections] if sections else ([] if project_data.document_type == "docx" else None),
        "slides": [slide.dict() for slide in slides] if slides else ([] if project_data.document_type == "pptx" else None),
        "status": "draft"
    }
    
    # Try MongoDB first, fallback to memory store
    if collection is not None:
        try:
            project_in_db = ProjectInDB(**project_dict)
            result = await collection.insert_one(project_in_db.dict(by_alias=True, exclude={"id"}))
            
            # Return created project
            created_project = await collection.find_one({"_id": result.inserted_id})
            return Project(**created_project, id=str(created_project["_id"]))
        except Exception as e:
            print(f"MongoDB error, using memory store: {e}")
    
    # Fallback to memory store
    created_project = await memory_project_store.create_project(project_dict)
    return Project(**created_project)

@router.get("", response_model=List[Project])
async def get_user_projects_no_slash(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    document_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user = Depends(get_current_user_optional)
):
    """Get user's projects without trailing slash - Universal support for ALL users"""
    return await get_user_projects_impl(skip, limit, document_type, search, current_user)

@router.get("/", response_model=List[Project])
async def get_user_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    document_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user = Depends(get_current_user_optional)
):
    """Get user's projects with optional filtering - Universal support for ALL users"""
    return await get_user_projects_impl(skip, limit, document_type, search, current_user)
    
    collection = await get_collection("projects")
    
    # Try MongoDB first, fallback to memory store
    if collection is not None:
        try:
            # Build filter query
            filter_query = {"user_id": str(current_user.id) if current_user else "test_user_123"}
            
            if document_type:
                filter_query["document_type"] = document_type
            
            if search:
                filter_query["$or"] = [
                    {"title": {"$regex": search, "$options": "i"}},
                    {"topic": {"$regex": search, "$options": "i"}}
                ]
            
            # Get projects with pagination
            cursor = collection.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)
            projects = await cursor.to_list(length=limit)
            
            return [Project(**project, id=str(project["_id"])) for project in projects]
        except Exception as e:
            print(f"MongoDB error, using memory store: {e}")
    
    # Fallback to memory store
    projects = await memory_project_store.find_projects_by_user(
        str(current_user.id) if current_user else "test_user_123", 
        search or "", 
        document_type or ""
    )
    
    # Apply pagination
    paginated_projects = projects[skip:skip + limit]
    return [Project(**project) for project in paginated_projects]

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    current_user = Depends(get_current_user_optional)
):
    """Get a specific project - Universal support for ALL users"""
    user_id = await get_universal_user_id(current_user)
    
    # Try MongoDB FIRST for persistence
    collection = await get_collection("projects")
    if collection is not None and ObjectId.is_valid(project_id):
        try:
            project_data = await collection.find_one({
                "_id": ObjectId(project_id),
                "user_id": user_id
            })
            if project_data:
                project_data["id"] = str(project_data["_id"])
                return Project(**project_data)
        except Exception as e:
            print(f"MongoDB error: {e}")
    
    # Fallback to memory store
    project = await memory_project_store.find_project_by_id(project_id, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return Project(**project)

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user = Depends(get_current_user_optional)
):
    """Update a project - Universal support for ALL users"""
    user_id = await get_universal_user_id(current_user)
    
    update_data = project_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    # Try MongoDB FIRST for persistence
    collection = await get_collection("projects")
    if collection is not None and ObjectId.is_valid(project_id):
        try:
            existing_project = await collection.find_one({
                "_id": ObjectId(project_id),
                "user_id": user_id
            })
            
            if existing_project:
                await collection.update_one(
                    {"_id": ObjectId(project_id)},
                    {"$set": update_data}
                )
                updated_project_data = await collection.find_one({"_id": ObjectId(project_id)})
                updated_project_data["id"] = str(updated_project_data["_id"])
                return Project(**updated_project_data)
        except Exception as e:
            print(f"MongoDB error: {e}")
    
    # Fallback to memory store
    updated_project = await memory_project_store.update_project(project_id, user_id, update_data)
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return Project(**updated_project)

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user = Depends(get_current_user_optional)
):
    """Delete a project - Universal support for ALL users"""
    user_id = await get_universal_user_id(current_user)
    
    # Try MongoDB FIRST for persistence
    collection = await get_collection("projects")
    if collection is not None and ObjectId.is_valid(project_id):
        try:
            result = await collection.delete_one({
                "_id": ObjectId(project_id),
                "user_id": user_id
            })
            
            if result.deleted_count > 0:
                return {"message": "Project deleted successfully"}
        except Exception as e:
            print(f"MongoDB error: {e}")
    
    # Fallback to memory store
    deleted = await memory_project_store.delete_project(project_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"message": "Project deleted successfully"}