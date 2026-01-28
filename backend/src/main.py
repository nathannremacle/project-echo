"""
Project Echo Backend - FastAPI Application Entry Point
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.middleware.error_handler import setup_error_handlers
from src.utils.health_check import perform_health_check
from src.utils.logging import setup_logging
from src.api.orchestration import router as orchestration_router
from src.api.music import router as music_router
from src.api.audio_replacement import router as audio_replacement_router
from src.api.phase2 import router as phase2_router
from src.api.creator_attribution import router as creator_attribution_router
from src.api.enhanced_analytics import router as enhanced_analytics_router

# Initialize logging
setup_logging()

# Create FastAPI app
# Note: root_path is not needed here because DigitalOcean strips /api before forwarding
app = FastAPI(
    title="Project Echo API",
    version="1.0.0",
    description="Multi-channel YouTube automation system",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup error handlers
setup_error_handlers(app)

# Include routers
app.include_router(orchestration_router)
app.include_router(music_router)
app.include_router(audio_replacement_router)
app.include_router(phase2_router)
app.include_router(creator_attribution_router)
app.include_router(enhanced_analytics_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Project Echo API", "version": "1.0.0"}


@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint
    
    Verifies:
    - Database connectivity
    - GitHub Actions environment
    - Python dependencies
    - Configuration loading
    
    Returns:
    - 200 if healthy
    - 503 if unhealthy or degraded
    """
    health = perform_health_check()
    
    # Return appropriate status code
    if health.status == "healthy":
        status_code = status.HTTP_200_OK
    else:
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        content=health.model_dump(),
        status_code=status_code,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
