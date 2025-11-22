from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Literal, Annotated
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId

class SectionBase(BaseModel):
    title: str
    order: int

class Section(SectionBase):
    id: str
    content: Optional[str] = None
    generated_at: Optional[datetime] = None

class SlideBase(BaseModel):
    title: str
    order: int

class Slide(SlideBase):
    id: str
    content: Optional[List[str]] = None  # List of bullet points
    generated_at: Optional[datetime] = None

class RefinementHistory(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    prompt: str
    old_content: str
    new_content: str
    accepted: bool = False

class Feedback(BaseModel):
    liked: Optional[bool] = None
    comment: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ProjectBase(BaseModel):
    title: str
    document_type: Literal["docx", "pptx"]
    topic: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    sections: Optional[List[SectionBase]] = None
    slides: Optional[List[SlideBase]] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    topic: Optional[str] = None
    description: Optional[str] = None
    sections: Optional[List[Section]] = None
    slides: Optional[List[Slide]] = None
    status: Optional[Literal["draft", "generating", "completed"]] = None

class ProjectInDB(ProjectBase):
    id: Annotated[PyObjectId, Field(alias="_id")] = Field(default_factory=PyObjectId)
    user_id: str
    sections: Optional[List[Section]] = None
    slides: Optional[List[Slide]] = None
    refinement_history: Dict[str, List[RefinementHistory]] = Field(default_factory=dict)
    feedback: Dict[str, Feedback] = Field(default_factory=dict)
    status: Literal["draft", "generating", "completed"] = "draft"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class Project(ProjectBase):
    id: str
    user_id: str
    sections: Optional[List[Section]] = None
    slides: Optional[List[Slide]] = None
    refinement_history: Dict[str, List[RefinementHistory]] = Field(default_factory=dict)
    feedback: Dict[str, Feedback] = Field(default_factory=dict)
    status: Literal["draft", "generating", "completed"] = "draft"
    created_at: datetime
    updated_at: datetime

class ContentGenerationRequest(BaseModel):
    section_id: Optional[str] = None
    slide_id: Optional[str] = None
    custom_prompt: Optional[str] = None

class RefinementRequest(BaseModel):
    prompt: str
    section_id: Optional[str] = None
    slide_id: Optional[str] = None

class FeedbackRequest(BaseModel):
    section_id: Optional[str] = None
    slide_id: Optional[str] = None
    liked: Optional[bool] = None
    comment: Optional[str] = None