"""
FanPulse API - Main Application
================================

FastAPI application for the FanPulse platform.
Provides REST API for VAR-Lens and Tactical Pulse agents.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FanPulse API",
    description="AI-powered platform for understanding FIFA World Cup matches",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "FanPulse API",
        "version": "1.0.0",
        "description": "AI-powered platform for understanding FIFA World Cup matches",
        "agents": {
            "var_lens": {
                "name": "VAR-Lens",
                "description": "Explains VAR decisions using FIFA/IFAB rules",
                "endpoint": "/var-lens",
                "status": "operational"
            },
            "tactical_pulse": {
                "name": "Tactical Pulse",
                "description": "Analyzes tactical changes and match momentum",
                "endpoint": "/tactical-pulse",
                "status": "coming_soon"
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


# Health check
@app.get("/health")
async def health_check():
    """Overall health check."""
    return {
        "status": "healthy",
        "service": "FanPulse API",
        "version": "1.0.0"
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested endpoint {request.url.path} was not found",
            "available_endpoints": [
                "/",
                "/health",
                "/var-lens/explain",
                "/var-lens/health",
                "/docs"
            ]
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting FanPulse API...")
    
    try:
        # Initialize VAR-Lens agent
        from src.api.routes.var_lens import initialize_rag
        
        logger.info("Initializing VAR-Lens agent...")
        if initialize_rag():
            logger.info("✅ VAR-Lens agent initialized successfully")
        else:
            logger.warning("⚠️ VAR-Lens agent initialization failed")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
    
    logger.info("FanPulse API started successfully")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down FanPulse API...")


# Include routers
try:
    from src.api.routes.var_lens import router as var_lens_router
    app.include_router(var_lens_router)
    logger.info("✅ VAR-Lens routes loaded")
except Exception as e:
    logger.error(f"❌ Failed to load VAR-Lens routes: {e}")


# Run with: uvicorn src.api.main:app --reload
if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting FanPulse API server...")
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

# Made with Bob
