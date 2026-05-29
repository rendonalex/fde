"""
FastAPI application for ADR-4 Shadow Log Store.
Per specs/06b-capability-spec-triage.md Section 8.2.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from .database import init_db, get_db, ShadowLogEntry
from .models import (
    NormalizedClaimRecord,
    RoutingDecisionOutput,
    RoutingDecisionRecord,
    ProcessorDecisionUpdate,
    ShadowLogMetrics,
    AgreementStatus,
    RoutingDecision
)
from .agent import create_agent

# Initialize FastAPI app
app = FastAPI(
    title="ADR-4 Clinical Content Triage Agent",
    description="Shadow Log Store API and Classification Endpoint",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "adr4-triage-agent"}


# ============================================================================
# CLASSIFICATION ENDPOINT
# ============================================================================

@app.post("/api/v1/classify", response_model=RoutingDecisionOutput, status_code=status.HTTP_200_OK)
def classify_claim(claim: NormalizedClaimRecord):
    """
    Classify a normalized claim record using LLM with codebook reasoning.
    Per specs/06b-capability-spec-triage.md Section 6.3.

    Args:
        claim: Normalized claim record from ADR-1

    Returns:
        Routing decision with confidence and reasoning trace

    Raises:
        400: If claim fails preconditions (extraction_status != AUTO_COMPLETE)
        500: If classification fails or OPENAI_API_KEY not set
    """
    try:
        # Create agent (LLM-based classification)
        agent = create_agent()

        # Classify
        result = agent.classify(claim)

        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================================================
# SHADOW LOG ENDPOINTS
# ============================================================================

@app.post("/api/v1/shadow-log", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_shadow_log_entry(
    record: RoutingDecisionRecord,
    db: Session = Depends(get_db)
):
    """
    Write agent classification to shadow log.

    Args:
        record: Routing decision record from agent
        db: Database session

    Returns:
        {"shadow_log_id": "uuid"}

    Raises:
        409: If shadow_log_id already exists
        500: If write fails
    """
    try:
        # Check if entry already exists
        existing = db.query(ShadowLogEntry).filter(
            ShadowLogEntry.shadow_log_id == record.shadow_log_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Shadow log entry {record.shadow_log_id} already exists"
            )

        # Create entry
        entry = ShadowLogEntry(
            shadow_log_id=record.shadow_log_id,
            claim_id=record.claim_id,
            agent_routing_decision=record.agent_routing_decision.value,
            agent_confidence=record.agent_confidence,
            agent_confidence_fallback=record.agent_confidence_fallback,
            clinical_indicators_detected=record.clinical_indicators_detected,
            criteria_provisions_matched=record.criteria_provisions_matched,
            reasoning_trace=record.reasoning_trace,
            agent_version=record.agent_version,
            logged_at=record.logged_at,
            processor_routing_decision=None,
            processor_user_id=None,
            processor_decided_at=None,
            agreement=None,
            ground_truth_routing=None,
            adjudication_id=None
        )

        db.add(entry)
        db.commit()
        db.refresh(entry)

        return {"shadow_log_id": entry.shadow_log_id}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.put("/api/v1/shadow-log/{shadow_log_id}/processor-decision", status_code=status.HTTP_200_OK)
def update_processor_decision(
    shadow_log_id: str,
    update: ProcessorDecisionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update shadow log entry with processor routing decision.

    Args:
        shadow_log_id: Shadow log entry ID
        update: Processor decision data
        db: Database session

    Returns:
        {"status": "updated", "agreement": "AGREE | DISAGREE"}

    Raises:
        404: If shadow_log_id not found
        500: If update fails
    """
    try:
        # Find entry
        entry = db.query(ShadowLogEntry).filter(
            ShadowLogEntry.shadow_log_id == shadow_log_id
        ).first()

        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shadow log entry {shadow_log_id} not found"
            )

        # Compute agreement
        agent_decision = entry.agent_routing_decision
        processor_decision = update.processor_routing_decision.value
        agreement = AgreementStatus.AGREE if agent_decision == processor_decision else AgreementStatus.DISAGREE

        # Update entry
        entry.processor_routing_decision = processor_decision
        entry.processor_user_id = update.processor_user_id
        entry.processor_decided_at = update.processor_decided_at
        entry.agreement = agreement.value

        db.commit()

        return {
            "status": "updated",
            "shadow_log_id": shadow_log_id,
            "agreement": agreement.value
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/api/v1/shadow-log", response_model=List[RoutingDecisionRecord])
def list_shadow_log_entries(
    claim_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Query shadow log entries.

    Args:
        claim_id: Filter by claim ID (optional)
        date_from: Filter by logged_at >= date_from (ISO 8601)
        date_to: Filter by logged_at <= date_to (ISO 8601)
        limit: Max results (default 100)
        db: Database session

    Returns:
        List of shadow log entries
    """
    try:
        query = db.query(ShadowLogEntry)

        # Apply filters
        if claim_id:
            query = query.filter(ShadowLogEntry.claim_id == claim_id)

        if date_from:
            date_from_dt = datetime.fromisoformat(date_from.replace("Z", "+00:00"))
            query = query.filter(ShadowLogEntry.logged_at >= date_from_dt)

        if date_to:
            date_to_dt = datetime.fromisoformat(date_to.replace("Z", "+00:00"))
            query = query.filter(ShadowLogEntry.logged_at <= date_to_dt)

        # Execute
        entries = query.order_by(ShadowLogEntry.logged_at.desc()).limit(limit).all()

        # Convert to Pydantic models
        results = []
        for entry in entries:
            results.append(RoutingDecisionRecord(
                shadow_log_id=entry.shadow_log_id,
                claim_id=entry.claim_id,
                agent_routing_decision=RoutingDecision(entry.agent_routing_decision),
                agent_confidence=entry.agent_confidence,
                agent_confidence_fallback=entry.agent_confidence_fallback,
                clinical_indicators_detected=entry.clinical_indicators_detected,
                criteria_provisions_matched=entry.criteria_provisions_matched,
                reasoning_trace=entry.reasoning_trace,
                agent_version=entry.agent_version,
                logged_at=entry.logged_at,
                processor_routing_decision=RoutingDecision(entry.processor_routing_decision) if entry.processor_routing_decision else None,
                processor_user_id=entry.processor_user_id,
                processor_decided_at=entry.processor_decided_at,
                agreement=AgreementStatus(entry.agreement) if entry.agreement else None,
                ground_truth_routing=RoutingDecision(entry.ground_truth_routing) if entry.ground_truth_routing else None,
                adjudication_id=entry.adjudication_id
            ))

        return results

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/api/v1/shadow-log/metrics", response_model=ShadowLogMetrics)
def get_shadow_log_metrics(db: Session = Depends(get_db)):
    """
    Query shadow log metrics for [A6] gate validation.

    Returns:
        Metrics including false-negative rate and gate status

    Per specs/06b-capability-spec-triage.md Section 8.2.
    """
    try:
        # Total entries
        total_entries = db.query(ShadowLogEntry).count()

        # Labeled entries (processor decision recorded)
        labeled_entries = db.query(ShadowLogEntry).filter(
            ShadowLogEntry.processor_routing_decision.isnot(None)
        ).count()

        # Disagreement entries
        disagreement_entries = db.query(ShadowLogEntry).filter(
            ShadowLogEntry.agreement == AgreementStatus.DISAGREE.value
        ).count()

        # False negatives (agent=FAST_PATH, processor=CLINICAL_PATH)
        false_negative_count = db.query(ShadowLogEntry).filter(
            ShadowLogEntry.agent_routing_decision == RoutingDecision.FAST_PATH.value,
            ShadowLogEntry.processor_routing_decision == RoutingDecision.CLINICAL_PATH.value
        ).count()

        # Compute false-negative rate
        false_negative_rate = 0.0
        if labeled_entries > 0:
            false_negative_rate = false_negative_count / labeled_entries

        # [A6] gate conditions
        gate_threshold = 0.02
        min_labeled_entries = 2000

        gate_status = "PASS" if (false_negative_rate < gate_threshold and labeled_entries >= min_labeled_entries) else "FAIL"
        wave_2_ready = (gate_status == "PASS")

        return ShadowLogMetrics(
            total_entries=total_entries,
            labeled_entries=labeled_entries,
            disagreement_entries=disagreement_entries,
            false_negative_count=false_negative_count,
            false_negative_rate=round(false_negative_rate, 4),
            gate_status=gate_status,
            gate_threshold=gate_threshold,
            min_labeled_entries=min_labeled_entries,
            wave_2_ready=wave_2_ready
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error": str(exc)}
    )
