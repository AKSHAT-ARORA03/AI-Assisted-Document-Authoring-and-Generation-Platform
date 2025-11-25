import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import auth, projects, generation, refinement, export, profile
from app.utils.database import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


# Initialize FastAPI app
app = FastAPI(
    title="AI Document Authoring Platform",
    description="Professional AI-powered document creation and editing platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("DEBUG", "False").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("DEBUG", "False").lower() == "true" else None
)

# CORS Configuration for Production
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_str:
    # Handle wildcard patterns for Vercel deployments
    allowed_origins = []
    for origin in allowed_origins_str.split(","):
        origin = origin.strip()
        if "*.vercel.app" in origin:
            # Allow all Vercel subdomains
            allowed_origins.extend([
                "https://ai-document-authoring.vercel.app",
                "https://ai-assisted-document-authoring.vercel.app", 
                "https://document-authoring-platform.vercel.app"
            ])
        else:
            allowed_origins.append(origin)
else:
    allowed_origins = ["*"]  # Fallback for development

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(generation.router, prefix="/api/v1/generation", tags=["AI Generation"])
app.include_router(refinement.router, prefix="/api/v1/refinement", tags=["Content Refinement"])
app.include_router(export.router, prefix="/api/v1/export", tags=["Document Export"])
app.include_router(profile.router, prefix="/api/v1", tags=["User Profile"])

# Health check endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "AI Document Authoring Platform API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_service": "available",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "document-authoring-platform"}

@app.get("/debug/test")
async def debug_test():
    return {"message": "Debug endpoint working", "timestamp": "2024-11-19"}

@app.options("/{full_path:path}")
async def options_handler():
    return {"message": "OK"}