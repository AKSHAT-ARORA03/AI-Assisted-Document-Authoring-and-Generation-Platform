from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import auth, projects, generation, refinement, export, profile
from app.utils.database import connect_to_mongo, close_mongo_connection
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AI-Assisted Document Authoring Platform",
    description="Create, refine, and export professional documents with AI assistance",
    version="1.0.0"
)

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Database events
@app.on_event("startup")
async def startup_db_client():
    try:
        await connect_to_mongo()
        print("✅ MongoDB connected - Universal user support enabled")
    except Exception as e:
        print(f"MongoDB connection warning (fallback to memory store): {e}")
        # Don't shut down the app if MongoDB connection fails - graceful degradation

@app.on_event("shutdown")
async def shutdown_db_client():
    try:
        await close_mongo_connection()
    except Exception as e:
        print(f"Shutdown error: {e}")

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(profile.router, prefix="/api/v1/auth", tags=["profile"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(generation.router, prefix="/api/v1/generation", tags=["generation"])
app.include_router(refinement.router, prefix="/api/v1/refinement", tags=["refinement"])
app.include_router(export.router, prefix="/api/v1/export", tags=["export"])

@app.get("/")
async def root():
    return {"message": "AI-Assisted Document Authoring Platform API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "document-authoring-platform"}

@app.get("/debug/test")
async def debug_test():
    return {"message": "Debug endpoint working", "timestamp": "2024-11-19"}

@app.options("/{full_path:path}")
async def options_handler():
    return {"message": "OK"}