"""
FastAPI Main Application
Virtual Merchandise Try-On System
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from .database import init_db
from .config import settings
from .routes import auth, tryon, admin, master
from .scheduler import start_scheduler

from fastapi.staticfiles import StaticFiles
import os

# ...

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Virtual Try-On API...")
    init_db()
    print("✅ Database initialized")
    
    # Ensure storage directories exist
    os.makedirs("storage/merch", exist_ok=True)
    os.makedirs("storage/uploads", exist_ok=True)
    
    start_scheduler()
    print("✅ Scheduler started")
    yield
    # Shutdown
    print("👋 Shutting down...")

app = FastAPI(
    title="Virtual Merchandise Try-On API",
    description="Computer-vision based virtual try-on system for college fest",
    version="1.0.0",
    lifespan=lifespan
)

# Mount Static Files
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Health Check
@app.get("/")
async def root():
    return {
        "message": "Virtual Try-On API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tryon.router, prefix="/api/tryon", tags=["Try-On"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(master.router, prefix="/api/master", tags=["Master"])

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
