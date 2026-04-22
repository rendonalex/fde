"""Database configuration and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql://postgres:postgres@localhost:5432/prior_auth_db"
    app_name: str = "Prior-Authorization Check Agent"
    app_version: str = "1.0.0"
    debug: bool = True

    # Business rules
    expiration_warning_days: int = 7
    trigger_window_hours: int = 48
    fuzzy_match_threshold: float = 0.8

    # External system endpoints
    athenahealth_api_url: str = "http://localhost:8001/mock/athenahealth"
    prior_auth_db_api_url: str = "http://localhost:8002/mock/prior-auth-db"
    insurance_requirements_api_url: str = "http://localhost:8003/mock/insurance-requirements"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Database setup
settings = get_settings()
engine = create_engine(settings.database_url, echo=settings.debug)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
