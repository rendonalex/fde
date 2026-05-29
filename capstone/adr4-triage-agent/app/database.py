"""
SQLite database setup for shadow log store.
Per specs/06b-capability-spec-triage.md Section 8.2.
"""

from sqlalchemy import create_engine, Column, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database file location
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "shadow_log.db")

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ShadowLogEntry(Base):
    """
    Shadow evaluation log database table.
    Maps to RoutingDecisionRecord Pydantic model.
    """
    __tablename__ = "shadow_log"

    shadow_log_id = Column(String, primary_key=True, index=True)
    claim_id = Column(String, index=True, nullable=False)

    # Agent decision fields
    agent_routing_decision = Column(String, nullable=False)
    agent_confidence = Column(Float, nullable=False)
    agent_confidence_fallback = Column(Boolean, nullable=False)
    clinical_indicators_detected = Column(JSON, nullable=False)  # List[str]
    criteria_provisions_matched = Column(JSON, nullable=False)  # List[str]
    reasoning_trace = Column(Text, nullable=False)
    agent_version = Column(String, nullable=False, default="1.0.0")
    logged_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Processor decision fields (updated after processor routes)
    processor_routing_decision = Column(String, nullable=True)
    processor_user_id = Column(String, nullable=True)
    processor_decided_at = Column(DateTime, nullable=True)
    agreement = Column(String, nullable=True)  # AGREE or DISAGREE

    # Ground truth adjudication (Dr. Webb)
    ground_truth_routing = Column(String, nullable=True)
    adjudication_id = Column(String, nullable=True)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
