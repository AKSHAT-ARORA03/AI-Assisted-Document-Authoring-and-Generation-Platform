from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
from app.models.user import UserInDB
from app.models.project import RefinementRequest, FeedbackRequest, RefinementHistory, Feedback
from app.utils.auth import get_current_user, get_current_user_optional
from app.utils.database import get_collection
from app.utils.memory_store import memory_project_store
from app.services.ai_service import AIService
from datetime import datetime

router = APIRouter()

@router.post("/refine/{project_id}/{section_id}")
async def refine_section_content(
    project_id: str,
    section_id: str,
    request: RefinementRequest,
    current_user = Depends(get_current_user_optional)
):
    """Refine content for a specific section or slide"""
    user_id = str(current_user.id) if current_user else "test_user_123"
    
    # Try memory store first
    project = await memory_project_store.find_project_by_id(project_id, user_id)
    
    # If not in memory store and we have MongoDB, try there
    if not project and ObjectId.is_valid(project_id):
        collection = await get_collection("projects")
        if collection is not None:
            project = await collection.find_one({
                "_id": ObjectId(project_id),
                "user_id": user_id
            })
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Determine if we're working with sections or slides
    is_docx = project["document_type"] == "docx"
    items = project.get("sections" if is_docx else "slides", [])
    
    # Find the target item
    item_index = None
    target_item = None
    
    for i, item in enumerate(items):
        if item["id"] == section_id:
            item_index = i
            target_item = item
            break
    
    if target_item is None:
        raise HTTPException(status_code=404, detail=f"{'Section' if is_docx else 'Slide'} not found")
    
    if not target_item.get("content"):
        raise HTTPException(status_code=400, detail="No content to refine")
    
    try:
        # Get current content
        current_content = target_item["content"]
        if isinstance(current_content, list):  # For slides
            current_content = '\n'.join(current_content)
        
        # Refine content using AI
        refined_content = await AIService.refine_content(
            current_content=current_content,
            refinement_prompt=request.prompt,
            content_type="slide" if not is_docx else "section"
        )
        
        # Create refinement history entry
        refinement_entry = RefinementHistory(
            timestamp=datetime.utcnow(),
            prompt=request.prompt,
            old_content=current_content,
            new_content=refined_content,
            accepted=False
        )
        
        # Update refinement history in project
        refinement_history = project.get("refinement_history", {})
        if section_id not in refinement_history:
            refinement_history[section_id] = []
        
        refinement_history[section_id].append(refinement_entry.dict())
        
        # Update project in memory store first
        update_data = {
            "refinement_history": refinement_history,
            "updated_at": datetime.utcnow()
        }
        
        updated_project = await memory_project_store.update_project(project_id, user_id, update_data)
        
        # If not in memory store, try MongoDB
        if not updated_project and ObjectId.is_valid(project_id):
            collection = await get_collection("projects")
            if collection is not None:
                await collection.update_one(
                    {"_id": ObjectId(project_id)},
                    {"$set": update_data}
                )
        
        # Convert back to list for slides
        if not is_docx and isinstance(target_item["content"], list):
            refined_content_list = [point.strip() for point in refined_content.split('\n') if point.strip()]
        else:
            refined_content_list = refined_content
        
        return {
            "section_id": section_id,
            "original_content": current_content,
            "refined_content": refined_content_list if not is_docx else refined_content,
            "refinement_prompt": request.prompt,
            "timestamp": refinement_entry.timestamp
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error refining content: {str(e)}"
        )

@router.post("/accept/{project_id}/{section_id}")
async def accept_refinement(
    project_id: str,
    section_id: str,
    current_user = Depends(get_current_user_optional)
):
    """Accept the latest refinement for a section/slide"""
    user_id = str(current_user.id) if current_user else "test_user_123"
    
    # Try memory store first
    project = await memory_project_store.find_project_by_id(project_id, user_id)
    
    # If not in memory store and we have MongoDB, try there
    if not project and ObjectId.is_valid(project_id):
        collection = await get_collection("projects")
        if collection is not None:
            project = await collection.find_one({
                "_id": ObjectId(project_id),
                "user_id": user_id
            })
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get latest refinement
    refinement_history = project.get("refinement_history", {})
    if section_id not in refinement_history or not refinement_history[section_id]:
        raise HTTPException(status_code=404, detail="No refinements found for this section")
    
    latest_refinement = refinement_history[section_id][-1]
    
    # Update the actual content
    is_docx = project["document_type"] == "docx"
    items = project.get("sections" if is_docx else "slides", [])
    
    item_index = None
    for i, item in enumerate(items):
        if item["id"] == section_id:
            item_index = i
            break
    
    if item_index is None:
        raise HTTPException(status_code=404, detail=f"{'Section' if is_docx else 'Slide'} not found")
    
    # Update content and mark refinement as accepted
    new_content = latest_refinement["new_content"]
    if not is_docx:  # For slides, convert back to list
        new_content = [point.strip() for point in new_content.split('\n') if point.strip()]
    
    items[item_index]["content"] = new_content
    latest_refinement["accepted"] = True
    
    # Update project in memory store first
    update_data = {
        "sections" if is_docx else "slides": items,
        "refinement_history": refinement_history,
        "updated_at": datetime.utcnow()
    }
    
    updated_project = await memory_project_store.update_project(project_id, user_id, update_data)
    
    # If not in memory store, try MongoDB
    if not updated_project and ObjectId.is_valid(project_id):
        collection = await get_collection("projects")
        if collection is not None:
            await collection.update_one(
                {"_id": ObjectId(project_id)},
                {"$set": update_data}
            )
    
    return {"message": "Refinement accepted successfully", "new_content": new_content}

@router.post("/feedback/{project_id}/{section_id}")
async def submit_feedback(
    project_id: str,
    section_id: str,
    request: FeedbackRequest,
    current_user = Depends(get_current_user_optional)
):
    """Submit feedback for a section/slide"""
    user_id = str(current_user.id) if current_user else "test_user_123"
    
    # Try memory store first
    project = await memory_project_store.find_project_by_id(project_id, user_id)
    
    # If not in memory store and we have MongoDB, try there
    if not project and ObjectId.is_valid(project_id):
        collection = await get_collection("projects")
        if collection is not None:
            project = await collection.find_one({
                "_id": ObjectId(project_id),
                "user_id": user_id
            })
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create feedback entry
    feedback_entry = Feedback(
        liked=request.liked,
        comment=request.comment,
        timestamp=datetime.utcnow()
    )
    
    # Update feedback in project
    feedback = project.get("feedback", {})
    feedback[section_id] = feedback_entry.dict()
    
    # Update project in memory store first
    update_data = {
        "feedback": feedback,
        "updated_at": datetime.utcnow()
    }
    
    updated_project = await memory_project_store.update_project(project_id, user_id, update_data)
    
    # If not in memory store, try MongoDB
    if not updated_project and ObjectId.is_valid(project_id):
        collection = await get_collection("projects")
        if collection is not None:
            await collection.update_one(
                {"_id": ObjectId(project_id)},
                {"$set": update_data}
            )
    
    return {"message": "Feedback submitted successfully", "feedback": feedback_entry}

@router.get("/history/{project_id}/{section_id}")
async def get_refinement_history(
    project_id: str,
    section_id: str,
    current_user = Depends(get_current_user_optional)
):
    """Get refinement history for a section/slide"""
    user_id = str(current_user.id) if current_user else "test_user_123"
    
    # Try memory store first
    project = await memory_project_store.find_project_by_id(project_id, user_id)
    
    # If not in memory store and we have MongoDB, try there
    if not project and ObjectId.is_valid(project_id):
        collection = await get_collection("projects")
        if collection is not None:
            project = await collection.find_one({
                "_id": ObjectId(project_id),
                "user_id": user_id
            })
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    refinement_history = project.get("refinement_history", {})
    section_history = refinement_history.get(section_id, [])
    
    return {"section_id": section_id, "history": section_history}