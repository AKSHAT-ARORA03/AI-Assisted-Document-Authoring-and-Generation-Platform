from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
from app.models.user import UserInDB
from app.models.project import Project, ContentGenerationRequest, Section, Slide
from app.utils.auth import get_current_user, get_current_user_optional
from app.utils.database import get_collection
from app.utils.memory_store import memory_project_store
from app.services.ai_service import AIService
import uuid
from datetime import datetime

router = APIRouter()

async def get_universal_user_id(current_user) -> str:
    """Get user ID with universal fallback for development"""
    if current_user and hasattr(current_user, 'id'):
        return str(current_user.id)
    return "test_user_123"  # Consistent fallback for development

@router.post("/outline/{project_id}")
async def generate_outline(
    project_id: str,
    num_sections: int = 5,
    current_user = Depends(get_current_user_optional)
):
    """Generate AI-powered outline for a project - MongoDB FIRST for ALL users"""
    user_id = await get_universal_user_id(current_user)
    
    # Try MongoDB FIRST for persistence (universal approach)
    project = None
    collection = await get_collection("projects")
    if collection is not None and ObjectId.is_valid(project_id):
        try:
            project_data = await collection.find_one({
                "_id": ObjectId(project_id),
                "user_id": user_id
            })
            if project_data:
                project = project_data
        except Exception as e:
            print(f"MongoDB error: {e}")
    
    # Fallback to memory store only if MongoDB fails
    if not project:
        project = await memory_project_store.find_project_by_id(project_id, user_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Generate outline using AI
        titles = await AIService.generate_document_outline(
            topic=project["topic"],
            document_type=project["document_type"],
            num_sections=num_sections
        )
        
        # Create sections or slides based on document type
        if project["document_type"] == "docx":
            sections = []
            for i, title in enumerate(titles):
                section = Section(
                    id=str(uuid.uuid4()),
                    title=title,
                    order=i + 1
                )
                sections.append(section)
            
            # Update project with generated sections - MongoDB FIRST
            update_data = {
                "sections": [section.dict() for section in sections],
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
            
            return {"sections": sections}
        
        else:  # pptx
            slides = []
            for i, title in enumerate(titles):
                slide = Slide(
                    id=str(uuid.uuid4()),
                    title=title,
                    order=i + 1
                )
                slides.append(slide)
            
            # Update project with generated slides - MongoDB FIRST
            update_data = {
                "slides": [slide.dict() for slide in slides],
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
            
            return {"slides": slides}
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating outline: {str(e)}"
        )

@router.post("/section/{project_id}/{section_id}")
async def generate_section_content(
    project_id: str,
    section_id: str,
    request: ContentGenerationRequest,
    current_user = Depends(get_current_user_optional)
):
    """Generate content for a specific section - MongoDB FIRST for ALL users"""
    user_id = await get_universal_user_id(current_user)
    
    # Try MongoDB FIRST for persistence (universal approach)
    project = None
    collection = await get_collection("projects")
    if collection is not None and ObjectId.is_valid(project_id):
        try:
            project_data = await collection.find_one({
                "_id": ObjectId(project_id),
                "user_id": user_id
            })
            if project_data:
                project = project_data
        except Exception as e:
            print(f"MongoDB error: {e}")
    
    # Fallback to memory store only if MongoDB fails
    if not project:
        project = await memory_project_store.find_project_by_id(project_id, user_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project["document_type"] != "docx":
        raise HTTPException(status_code=400, detail="This endpoint is for Word documents only")
    
    # Find the section
    sections = project.get("sections", [])
    section_index = None
    target_section = None
    
    for i, section in enumerate(sections):
        if section["id"] == section_id:
            section_index = i
            target_section = section
            break
    
    if target_section is None:
        raise HTTPException(status_code=404, detail="Section not found")
    
    try:
        # Get context from previous sections
        context = ""
        for section in sections[:section_index]:
            if section.get("content"):
                context += f"{section['title']}: {section['content'][:200]}...\n"
        
        # Generate content
        content = await AIService.generate_section_content(
            section_title=target_section["title"],
            topic=project["topic"],
            context=context if context else None,
            word_count=250
        )
        
        # Update section with generated content
        sections[section_index]["content"] = content
        sections[section_index]["generated_at"] = datetime.utcnow()
        
        # Update project with generated content - MongoDB FIRST
        update_data = {
            "sections": sections,
            "status": "generating",
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
        
        return {
            "section_id": section_id,
            "content": content,
            "generated_at": sections[section_index]["generated_at"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating content: {str(e)}"
        )

@router.post("/slide/{project_id}/{slide_id}")
async def generate_slide_content(
    project_id: str,
    slide_id: str,
    request: ContentGenerationRequest,
    current_user = Depends(get_current_user_optional)
):
    """Generate content for a specific slide - MongoDB FIRST for ALL users"""
    user_id = await get_universal_user_id(current_user)
    
    # Try MongoDB FIRST for persistence (universal approach)
    project = None
    collection = await get_collection("projects")
    if collection is not None and ObjectId.is_valid(project_id):
        try:
            project_data = await collection.find_one({
                "_id": ObjectId(project_id),
                "user_id": user_id
            })
            if project_data:
                project = project_data
        except Exception as e:
            print(f"MongoDB error: {e}")
    
    # Fallback to memory store only if MongoDB fails
    if not project:
        project = await memory_project_store.find_project_by_id(project_id, user_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project["document_type"] != "pptx":
        raise HTTPException(status_code=400, detail="This endpoint is for PowerPoint presentations only")
    
    # Find the slide
    slides = project.get("slides", [])
    slide_index = None
    target_slide = None
    
    for i, slide in enumerate(slides):
        if slide["id"] == slide_id:
            slide_index = i
            target_slide = slide
            break
    
    if target_slide is None:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    try:
        # Get context from previous slides
        context = ""
        for slide in slides[:slide_index]:
            if slide.get("content"):
                context += f"{slide['title']}: {', '.join(slide['content'][:2])}...\n"
        
        # Generate content (bullet points)
        bullet_points = await AIService.generate_slide_content(
            slide_title=target_slide["title"],
            topic=project["topic"],
            context=context if context else None,
            num_bullets=4
        )
        
        # Update slide with generated content
        slides[slide_index]["content"] = bullet_points
        slides[slide_index]["generated_at"] = datetime.utcnow()
        
        # Update project with generated content - MongoDB FIRST
        update_data = {
            "slides": slides,
            "status": "generating",
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
        
        return {
            "slide_id": slide_id,
            "content": bullet_points,
            "generated_at": slides[slide_index]["generated_at"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating content: {str(e)}"
        )

@router.post("/all-sections/{project_id}")
async def generate_all_sections(
    project_id: str,
    current_user = Depends(get_current_user_optional)
):
    """INTELLIGENT WORKFLOW: Generate content for all sections/slides. Auto-creates outline if missing!"""
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
        if project["document_type"] == "docx":
            # INTELLIGENT WORKFLOW: Auto-generate outline if missing
            sections = project.get("sections", []) or []
            if not sections:
                print(f"No sections found for project {project_id}, auto-generating outline...")
                # Auto-generate outline first
                await generate_outline(project_id, 5, current_user)
                # Refresh project data after outline generation
                if collection is not None and ObjectId.is_valid(project_id):
                    try:
                        project = await collection.find_one({"_id": ObjectId(project_id), "user_id": user_id})
                    except:
                        pass
                if not project:
                    project = await memory_project_store.find_project_by_id(project_id, user_id)
                sections = project.get("sections", []) or [] if project else []
            
            context = ""
            
            for i, section in enumerate(sections):
                if not section.get("content") and project:  # Only generate if content doesn't exist and project is valid
                    content = await AIService.generate_section_content(
                        section_title=section["title"],
                        topic=project["topic"],
                        context=context if context else None,
                        word_count=250
                    )
                    
                    sections[i]["content"] = content
                    sections[i]["generated_at"] = datetime.utcnow()
                    
                    # Add to context for next sections
                    context += f"{section['title']}: {content[:200]}...\n"
            
            # Update project - MongoDB FIRST for persistence
            update_data = {
                "sections": sections,
                "status": "completed",
                "updated_at": datetime.utcnow()
            }
            
            # Try MongoDB first
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
            
            return {"message": "All sections generated successfully (auto-created outline if needed)", "sections": sections}
        
        else:  # pptx
            # INTELLIGENT WORKFLOW: Auto-generate slides outline if missing
            slides = project.get("slides", []) or [] if project else []
            if not slides:
                print(f"No slides found for project {project_id}, auto-generating outline...")
                # Auto-generate slides outline first
                await generate_outline(project_id, 5, current_user)
                # Refresh project data after outline generation
                if collection is not None and ObjectId.is_valid(project_id):
                    try:
                        project = await collection.find_one({"_id": ObjectId(project_id), "user_id": user_id})
                    except:
                        pass
                if not project:
                    project = await memory_project_store.find_project_by_id(project_id, user_id)
                slides = project.get("slides", []) or [] if project else []
            
            context = ""
            
            for i, slide in enumerate(slides):
                if not slide.get("content") and project:  # Only generate if content doesn't exist and project is valid
                    bullet_points = await AIService.generate_slide_content(
                        slide_title=slide["title"],
                        topic=project["topic"],
                        context=context if context else None,
                        num_bullets=4
                    )
                    
                    slides[i]["content"] = bullet_points
                    slides[i]["generated_at"] = datetime.utcnow()
                    
                    # Add to context for next slides
                    context += f"{slide['title']}: {', '.join(bullet_points[:2])}...\n"
            
            # Update project - MongoDB FIRST for persistence
            update_data = {
                "slides": slides,
                "status": "completed",
                "updated_at": datetime.utcnow()
            }
            
            # Try MongoDB first
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
            
            return {"message": "All slides generated successfully (auto-created outline if needed)", "slides": slides}
    
    except HTTPException:
        # Re-raise HTTPException as-is (preserves status code and message)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating content: {str(e)}"
        )