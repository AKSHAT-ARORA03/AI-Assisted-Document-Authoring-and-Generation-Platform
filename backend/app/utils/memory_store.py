# Simple in-memory storage for development when MongoDB is not available
from typing import Dict, Optional, List
from app.models.user import UserInDB
from datetime import datetime
import uuid
import asyncio

class MemoryUserStore:
    def __init__(self):
        self.users: Dict[str, dict] = {}
        
    async def find_user_by_email(self, email: str) -> Optional[dict]:
        """Find user by email in memory store"""
        return self.users.get(email)
    
    async def create_user(self, user_data: dict) -> dict:
        """Create user in memory store"""
        self.users[user_data["email"]] = user_data
        return user_data
    
    async def get_all_users(self) -> list:
        """Get all users from memory store"""
        return list(self.users.values())

class MemoryProjectStore:
    def __init__(self):
        self.projects: Dict[str, dict] = {}
        
    async def create_project(self, project_data: dict) -> dict:
        """Create project in memory store"""
        project_id = str(uuid.uuid4())
        project_data["id"] = project_id
        project_data["_id"] = project_id  # For compatibility
        project_data["created_at"] = datetime.utcnow()
        project_data["updated_at"] = datetime.utcnow()
        self.projects[project_id] = project_data
        return project_data
    
    async def find_projects_by_user(self, user_id: str, search: str = "", document_type: str = "") -> List[dict]:
        """Find projects by user ID with optional filtering"""
        user_projects = []
        for project in self.projects.values():
            if project.get("user_id") == user_id:
                # Apply search filter
                if search:
                    if search.lower() not in project.get("title", "").lower() and \
                       search.lower() not in project.get("topic", "").lower():
                        continue
                
                # Apply document type filter
                if document_type and project.get("document_type") != document_type:
                    continue
                    
                user_projects.append(project)
        
        # Sort by created_at desc
        user_projects.sort(key=lambda x: x.get("created_at", datetime.utcnow()), reverse=True)
        return user_projects
    
    async def find_project_by_id(self, project_id: str, user_id: str) -> Optional[dict]:
        """Find project by ID and user ID"""
        project = self.projects.get(project_id)
        if project and project.get("user_id") == user_id:
            return project
        return None
    
    async def update_project(self, project_id: str, user_id: str, update_data: dict) -> Optional[dict]:
        """Update project in memory store"""
        if project_id in self.projects and self.projects[project_id].get("user_id") == user_id:
            self.projects[project_id].update(update_data)
            self.projects[project_id]["updated_at"] = datetime.utcnow()
            return self.projects[project_id]
        return None
    
    async def delete_project(self, project_id: str, user_id: str) -> bool:
        """Delete project from memory store"""
        if project_id in self.projects and self.projects[project_id].get("user_id") == user_id:
            del self.projects[project_id]
            return True
        return False

# Global instances
memory_store = MemoryUserStore()
memory_project_store = MemoryProjectStore()