"""API routes for Prior-Authorization Check operations."""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db, get_settings
from app.models import PriorAuthCheck, CheckStatus, HumanDecision
from app.schemas import (
    PriorAuthCheckCreate,
    PriorAuthCheckResponse,
    HumanDecisionRequest,
)
from app.services import PriorAuthDecisionEngine
from app.adapters import AthenaHealthAdapter, PriorAuthDBAdapter, InsuranceRequirementsAdapter
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/prior-auth-checks", tags=["prior-auth-checks"])
settings = get_settings()


def get_decision_engine() -> PriorAuthDecisionEngine:
    """Dependency for getting decision engine with adapters."""
    athena_adapter = AthenaHealthAdapter(
        settings.athenahealth_api_url,
        "mock_client_id",
        "mock_client_secret"
    )
    prior_auth_adapter = PriorAuthDBAdapter(
        settings.prior_auth_db_api_url,
        "mock_api_key"
    )
    insurance_adapter = InsuranceRequirementsAdapter(
        settings.insurance_requirements_api_url
    )

    return PriorAuthDecisionEngine(athena_adapter, prior_auth_adapter, insurance_adapter)


@router.post("/", response_model=PriorAuthCheckResponse, status_code=status.HTTP_201_CREATED)
async def create_prior_auth_check(
    request: PriorAuthCheckCreate,
    db: Session = Depends(get_db),
    engine: PriorAuthDecisionEngine = Depends(get_decision_engine)
):
    """
    Create and execute a new prior-authorization check.

    Triggers the 5-step decision process per Claude.md Section 3:
    1. Determine if prior-auth required
    2. Locate prior-auth documentation
    3. Validate match
    4. Check expiration
    5. Generate recommendation

    Returns the check result with AI recommendation for human review.
    """
    logger.info(f"Creating prior-auth check for appointment {request.appointment_id}")

    # Fetch appointment data from EHR (mock)
    appointment_data = await engine.athena_adapter.get_appointment(request.appointment_id)

    if not appointment_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {request.appointment_id} not found in EHR"
        )

    # Check if prior-auth check already exists for this appointment
    existing_check = db.query(PriorAuthCheck).filter(
        PriorAuthCheck.appointment_id == request.appointment_id
    ).first()

    if existing_check:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Prior-auth check already exists for appointment {request.appointment_id}"
        )

    # Create new PriorAuthCheck entity
    scheduled_date = datetime.fromisoformat(appointment_data["scheduled_date"].replace("Z", "+00:00"))
    check_id = f"PAC-{int(datetime.utcnow().timestamp())}-{appointment_data['patient_id']}-{request.appointment_id}"

    # Get first procedure code (or empty string if none)
    procedure_codes = appointment_data.get("procedure_codes", [])
    procedure_code = procedure_codes[0] if procedure_codes else ""
    procedure_descriptions = appointment_data.get("procedure_descriptions", [])
    procedure_description = procedure_descriptions[0] if procedure_descriptions else None

    check = PriorAuthCheck(
        check_id=check_id,
        patient_id=appointment_data["patient_id"],
        appointment_id=request.appointment_id,
        scheduled_date=scheduled_date,
        procedure_code=procedure_code,
        procedure_description=procedure_description,
        insurance_policy_id=appointment_data["insurance_policy_id"],
        status=CheckStatus.PENDING_CHECK
    )

    db.add(check)
    db.commit()

    # Execute the 5-step check
    check = await engine.execute_check(check, appointment_data)

    db.commit()
    db.refresh(check)

    logger.info(f"Prior-auth check {check.check_id} created with status {check.status}")

    return PriorAuthCheckResponse.from_orm_with_lists(check)


@router.get("/{check_id}", response_model=PriorAuthCheckResponse)
def get_prior_auth_check(check_id: str, db: Session = Depends(get_db)):
    """
    Get prior-authorization check by ID.

    Returns current status and AI recommendation.
    """
    check = db.query(PriorAuthCheck).filter(PriorAuthCheck.check_id == check_id).first()

    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prior-auth check {check_id} not found"
        )

    return PriorAuthCheckResponse.from_orm_with_lists(check)


@router.get("/", response_model=List[PriorAuthCheckResponse])
def list_prior_auth_checks(
    status_filter: CheckStatus = None,
    patient_id: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List prior-authorization checks with optional filters.

    Filters:
    - status: Filter by check status
    - patient_id: Filter by patient ID
    - limit: Maximum number of results (default 50)
    """
    query = db.query(PriorAuthCheck)

    if status_filter:
        query = query.filter(PriorAuthCheck.status == status_filter)

    if patient_id:
        query = query.filter(PriorAuthCheck.patient_id == patient_id)

    checks = query.order_by(PriorAuthCheck.created_at.desc()).limit(limit).all()

    return [PriorAuthCheckResponse.from_orm_with_lists(check) for check in checks]


@router.post("/{check_id}/human-decision", response_model=PriorAuthCheckResponse)
async def record_human_decision(
    check_id: str,
    decision_request: HumanDecisionRequest,
    db: Session = Depends(get_db),
    engine: PriorAuthDecisionEngine = Depends(get_decision_engine)
):
    """
    Record human decision on prior-auth check.

    Human reviews AI recommendation and makes final decision:
    - APPROVED: Proceed with appointment
    - RESCHEDULED: Reschedule appointment
    - ESCALATED: Need more investigation
    - OVERRIDDEN: Override AI recommendation

    Transitions check to appropriate terminal state per Claude.md Section 2 state machine.
    """
    logger.info(f"Recording human decision for check {check_id}: {decision_request.decision}")

    check = db.query(PriorAuthCheck).filter(PriorAuthCheck.check_id == check_id).first()

    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prior-auth check {check_id} not found"
        )

    # Validate current state allows human decision
    if check.status not in [CheckStatus.AWAITING_HUMAN_REVIEW, CheckStatus.ESCALATED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot record decision for check in status {check.status}"
        )

    # Record human decision
    check.human_decision = decision_request.decision
    check.human_decision_by = decision_request.decision_by
    check.human_decision_at = datetime.utcnow()
    check.human_decision_notes = decision_request.notes

    # Transition to appropriate state per decision
    try:
        if decision_request.decision == HumanDecision.APPROVED:
            check.transition_to(CheckStatus.APPROVED)
            check.transition_to(CheckStatus.COMPLETED)

            # Write verification note to EHR
            await engine.athena_adapter.write_verification_note(
                check.appointment_id,
                {
                    "prior_auth_status": str(check.prior_auth_status),
                    "ai_recommendation": str(check.ai_recommendation),
                    "human_decision": str(check.human_decision),
                    "confidence_score": str(check.confidence_score),
                    "verified_at": check.human_decision_at.isoformat(),
                    "verified_by": check.human_decision_by,
                }
            )
            await engine.athena_adapter.update_prior_auth_flag(check.appointment_id, True)

        elif decision_request.decision == HumanDecision.RESCHEDULED:
            check.transition_to(CheckStatus.RESCHEDULED)
            check.transition_to(CheckStatus.COMPLETED)

        elif decision_request.decision == HumanDecision.ESCALATED:
            if check.status != CheckStatus.ESCALATED:
                check.transition_to(CheckStatus.ESCALATED, reason=decision_request.notes)

        elif decision_request.decision == HumanDecision.OVERRIDDEN:
            check.transition_to(CheckStatus.APPROVED)
            check.transition_to(CheckStatus.COMPLETED)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid state transition: {str(e)}"
        )

    db.commit()
    db.refresh(check)

    logger.info(f"Human decision recorded, check now in status {check.status}")

    return PriorAuthCheckResponse.from_orm_with_lists(check)


@router.get("/appointments/{appointment_id}/check", response_model=PriorAuthCheckResponse)
def get_check_by_appointment(appointment_id: str, db: Session = Depends(get_db)):
    """
    Get prior-auth check for a specific appointment.

    Useful for retrieving check status by appointment ID.
    """
    check = db.query(PriorAuthCheck).filter(
        PriorAuthCheck.appointment_id == appointment_id
    ).first()

    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No prior-auth check found for appointment {appointment_id}"
        )

    return PriorAuthCheckResponse.from_orm_with_lists(check)
