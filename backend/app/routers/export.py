from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from bson import ObjectId
from app.models.user import UserInDB
from app.utils.auth import get_current_user, get_current_user_optional
from app.utils.database import get_collection
from app.utils.memory_store import memory_project_store
from app.services.document_service import DocumentService
from datetime import datetime
import urllib.parse
import io

# Updated for universal user support - 2025-11-20
router = APIRouter()

async def get_universal_user_id(current_user) -> str:
    """Get user ID with universal fallback for development"""
    if current_user and hasattr(current_user, 'id'):
        return str(current_user.id)
    return "test_user_123"  # Consistent fallback for development

@router.get("/{project_id}")
async def export_document(
    project_id: str,
    current_user: UserInDB = Depends(get_current_user_optional)
):
    """INTELLIGENT WORKFLOW: Export project as Word/PowerPoint. Auto-generates ALL missing content!"""
    user_id = await get_universal_user_id(current_user)
    
    # Try MongoDB FIRST for persistence (universal approach)
    project = None
    collection = await get_collection("projects")
    if collection is not None and ObjectId.is_valid(project_id):
        try:
            project = await collection.find_one({
                "_id": ObjectId(project_id),
                "user_id": user_id
            })
        except Exception as e:
            print(f"MongoDB error: {e}")
    
    # Fallback to memory store only if MongoDB fails
    if not project:
        project = await memory_project_store.find_project_by_id(project_id, user_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        document_type = project["document_type"] if project else "docx"
        
        # INTELLIGENT WORKFLOW: Auto-generate ALL missing content for seamless export
        from .generation import generate_all_sections
        
        if document_type == "docx":
            sections = project.get("sections", []) or [] if project else []
            
            # Auto-generate everything if missing
            if not sections or not any(section.get("content") for section in sections):
                print(f"Missing sections/content for project {project_id}, auto-generating complete workflow...")
                # This will auto-create outline AND generate all content
                await generate_all_sections(project_id, current_user)
                # Refresh project after generation
                if collection is not None and ObjectId.is_valid(project_id):
                    try:
                        project = await collection.find_one({"_id": ObjectId(project_id), "user_id": user_id})
                    except:
                        pass
                if not project:
                    project = await memory_project_store.find_project_by_id(project_id, user_id)
                sections = project.get("sections", []) or [] if project else []
            
            # Generate Word document
            if project:
                buffer = DocumentService.generate_word_document(project)
            else:
                raise HTTPException(status_code=500, detail="Failed to generate project data")
            
        elif document_type == "pptx":
            slides = project.get("slides", []) or [] if project else []
            
            # Auto-generate everything if missing
            if not slides or not any(slide.get("content") for slide in slides):
                print(f"Missing slides/content for project {project_id}, auto-generating complete workflow...")
                # This will auto-create slides outline AND generate all content
                await generate_all_sections(project_id, current_user)
                # Refresh project after generation
                if collection is not None and ObjectId.is_valid(project_id):
                    try:
                        project = await collection.find_one({"_id": ObjectId(project_id), "user_id": user_id})
                    except:
                        pass
                if not project:
                    project = await memory_project_store.find_project_by_id(project_id, user_id)
                slides = project.get("slides", []) or [] if project else []
            
            # Generate PowerPoint presentation
            if project:
                buffer = DocumentService.generate_powerpoint_presentation(project)
            else:
                raise HTTPException(status_code=500, detail="Failed to generate project data")
        
        else:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        # Update project status to completed - MongoDB FIRST
        update_data = {
            "status": "completed",
            "updated_at": datetime.utcnow()
        }
        
        # Try MongoDB FIRST for persistence
        if collection is not None and ObjectId.is_valid(project_id):
            try:
                await collection.update_one(
                    {"_id": ObjectId(project_id)},
                    {"$set": update_data}
                )
            except Exception as e:
                print(f"MongoDB update error: {e}")
                # Fallback to memory store
                await memory_project_store.update_project(project_id, user_id, update_data)
        else:
            # Use memory store if MongoDB not available
            await memory_project_store.update_project(project_id, user_id, update_data)
        
        # Prepare file for download
        file_extension = DocumentService.get_file_extension(document_type)
        mime_type = DocumentService.get_mime_type(document_type)
        
        # Create safe filename
        project_title = project.get("title", "Document") if project else "Document"
        safe_title = "".join(c for c in project_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title}.{file_extension}"
        encoded_filename = urllib.parse.quote(filename)
        
        # Return file as streaming response
        return StreamingResponse(
            content=iter([buffer.getvalue()]),
            media_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
    
    except HTTPException:
        # Re-raise HTTPException as-is (preserves status code and message)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting document: {str(e)}"
        )

@router.get("/{project_id}/preview")
async def preview_document_structure(
    project_id: str,
    current_user: UserInDB = Depends(get_current_user_optional)
):
    """Preview document structure without generating the actual file - Universal user support"""
    user_id = await get_universal_user_id(current_user)
    
    # Try memory store first
    project = await memory_project_store.find_project_by_id(project_id, user_id)
    
    if not project:
        # Fallback to MongoDB if available
        collection = await get_collection("projects")
        if collection is not None and ObjectId.is_valid(project_id):
            project_data = await collection.find_one({
                "_id": ObjectId(project_id),
                "user_id": user_id
            })
            if project_data:
                project = project_data

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    document_type = project["document_type"]
    
    if document_type == "docx":
        sections = project.get("sections", [])
        sections.sort(key=lambda x: x.get('order', 0))
        
        preview = {
            "title": project["title"],
            "document_type": document_type,
            "sections": [
                {
                    "title": section["title"],
                    "order": section.get("order", 0),
                    "has_content": bool(section.get("content")),
                    "content_length": len(section.get("content", "")) if section.get("content") else 0
                }
                for section in sections
            ],
            "total_sections": len(sections),
            "completed_sections": len([s for s in sections if s.get("content")])
        }
    
    else:  # pptx
        slides = project.get("slides", [])
        slides.sort(key=lambda x: x.get('order', 0))
        
        preview = {
            "title": project["title"],
            "document_type": document_type,
            "slides": [
                {
                    "title": slide["title"],
                    "order": slide.get("order", 0),
                    "has_content": bool(slide.get("content")),
                    "bullet_count": len(slide.get("content", [])) if slide.get("content") else 0
                }
                for slide in slides
            ],
            "total_slides": len(slides) + 1,  # +1 for title slide
            "completed_slides": len([s for s in slides if s.get("content")])
        }
    
    return preview