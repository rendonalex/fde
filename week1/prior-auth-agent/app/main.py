"""Main FastAPI application for Prior-Authorization Check Agent."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.database import Base, engine, get_settings
from app.routes import prior_auth_check_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Prior-Authorization Check Agent

    Automates prior-authorization verification for scheduled medical procedures.

    ## Features

    * **5-Step Decision Logic**: Automated prior-auth lookup, matching, and validation
    * **State Machine**: Enforces valid workflow transitions per specification
    * **Human-in-Loop**: AI recommends, humans decide
    * **Confidence Scoring**: HIGH/MEDIUM/LOW confidence with detailed rationale
    * **Audit Trail**: Complete tracking of all decisions and state changes

    ## Workflow

    1. Create prior-auth check for an appointment
    2. System executes 5-step analysis (automatic)
    3. Review AI recommendation and confidence score
    4. Record human decision (approve/reschedule/escalate)
    5. System documents result in EHR

    ## Implementation

    Built with Python/FastAPI and PostgreSQL per Claude.md specification.
    Uses mock adapters for external systems (athenahealth EHR, prior-auth database).
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to create database tables
@app.on_event("startup")
async def startup_event():
    """Create database tables on startup."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")

# Include routers
app.include_router(prior_auth_check_router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": "2026-04-22T00:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
