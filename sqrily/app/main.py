from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import structlog
import uvicorn
from datetime import datetime
import uuid

from .config import settings
from .database import engine, Base, get_db
from .dependencies import get_current_user
from .api.auth import router as auth_router
from .api.users import router as users_router
from .api.goals import router as goals_router
from .api.tasks import router as tasks_router
from .api.subtasks import router as subtasks_router
from .api.ai import router as ai_router
from .api.calendar import router as calendar_router
from .api.analytics import router as analytics_router
from .api.integrations import router as integrations_router
from .api.websockets import router as websockets_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="ADHD-friendly AI planner with Sqrily methodology integration",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    debug=settings.debug
)

# Security
security = HTTPBearer()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Session middleware for OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.jwt_secret_key,
    max_age=3600,
    same_site="lax",
    https_only=not settings.debug
)

# Trusted host middleware
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure this for production
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(
        "Unhandled exception occurred",
        exception=str(exc),
        path=request.url.path,
        method=request.method,
        request_id=str(uuid.uuid4())
    )
    
    if settings.debug:
        raise exc
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.utcnow().isoformat(),
            "adhd_friendly_message": "Something went wrong, but it's not your fault. Take a deep breath and try again in a moment."
        }
    )

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment
    }

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to Sqrily ADHD Planner API",
        "version": settings.app_version,
        "docs": "/api/docs",
        "health": "/health"
    }

# API routes
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(goals_router, prefix="/goals", tags=["goals"])
app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
app.include_router(subtasks_router, prefix="/subtasks", tags=["subtasks"])
app.include_router(ai_router, prefix="/ai", tags=["ai"])
app.include_router(calendar_router, prefix="/calendar", tags=["calendar"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(integrations_router, prefix="/integrations", tags=["integrations"])
app.include_router(websockets_router, prefix="/ws", tags=["websockets"])

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Sqrily ADHD Planner API", version=settings.app_version)
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    logger.info("Database tables created successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Sqrily ADHD Planner API")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )