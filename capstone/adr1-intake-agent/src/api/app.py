"""FastAPI application for ADR-1 Claim Intake Agent."""

import os
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ..mocks import EDI837Parser, MockCMSAPI, MockIDPPipeline
from ..models import ExtractionResult, IntakeChannel, NormalizedClaimRecord
from ..services import IntakeAgent, ClaimValidator

# Load environment variables
load_dotenv()


# Initialize services
cms_api = MockCMSAPI()
edi_parser = EDI837Parser()
idp_pipeline = MockIDPPipeline()
agent = IntakeAgent()
validator = ClaimValidator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management."""
    print("✓ ADR-1 Intake Agent started")
    print(f"✓ Agent version: {agent.agent_version}")
    print(f"✓ Claude model: {agent.model}")
    yield
    print("✓ ADR-1 Intake Agent shut down")


# Create FastAPI app
app = FastAPI(
    title="ADR-1 Claim Intake Agent",
    description="Claim Intake and Format Validation Agent for Greenfield Health Systems",
    version="1.0.0",
    lifespan=lifespan,
)


# Request/Response models
class SubmitClaimRequest(BaseModel):
    """Request to submit a claim for processing."""

    extraction_result: dict


class SubmitClaimResponse(BaseModel):
    """Response from claim submission."""

    claim_id: Optional[str]
    extraction_status: str
    low_confidence_fields: list
    message: str


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "ADR-1 Claim Intake Agent",
        "version": agent.agent_version,
        "status": "operational",
    }


@app.post("/api/v1/claims/submit", response_model=SubmitClaimResponse)
async def submit_claim(request: SubmitClaimRequest):
    """
    Submit a claim for intake processing.

    Accepts extraction result from EDI parser or IDP pipeline,
    processes through ADR-1 agent, and writes to CMS if validated.
    """
    try:
        # Parse extraction result
        extraction = ExtractionResult(**request.extraction_result)

        # Process through agent
        claim = await agent.process_extraction(extraction)

        # Validate claim
        is_valid, errors = validator.validate_claim(claim)
        if not is_valid:
            raise HTTPException(status_code=422, detail={"validation_errors": errors})

        # Write to CMS (if AUTO_COMPLETE)
        extraction_status_str = claim.extraction_status.value if hasattr(claim.extraction_status, 'value') else claim.extraction_status
        if extraction_status_str == "AUTO_COMPLETE":
            cms_response = await cms_api.create_claim(claim)

            if "error" in cms_response:
                return SubmitClaimResponse(
                    claim_id=None,
                    extraction_status="PENDING_DUPLICATE",
                    low_confidence_fields=[],
                    message=f"Duplicate claim: {cms_response['existing_claim_id']}",
                )

            return SubmitClaimResponse(
                claim_id=cms_response["claim_id"],
                extraction_status=extraction_status_str,
                low_confidence_fields=claim.low_confidence_fields,
                message="Claim queued successfully",
            )
        else:
            # HUMAN_REQUIRED
            return SubmitClaimResponse(
                claim_id=None,
                extraction_status=extraction_status_str,
                low_confidence_fields=claim.low_confidence_fields,
                message=f"Human review required for {len(claim.low_confidence_fields)} fields",
            )

    except Exception as e:
        import traceback
        print(f"ERROR in submit_claim: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/claims/{claim_id}")
async def get_claim(claim_id: str):
    """Get claim by ID."""
    from uuid import UUID

    try:
        claim_uuid = UUID(claim_id)
        claim = await cms_api.get_claim(claim_uuid)
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        return claim.model_dump()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid claim_id format")


@app.get("/api/v1/stats")
async def get_stats():
    """Get processing statistics."""
    total_claims = len(cms_api.claims)
    auto_complete = sum(
        1 for c in cms_api.claims.values() if c.extraction_status.value == "AUTO_COMPLETE"
    )
    human_required = total_claims - auto_complete

    return {
        "total_claims": total_claims,
        "auto_complete": auto_complete,
        "human_required": human_required,
        "hitl_rate": human_required / total_claims if total_claims > 0 else 0.0,
    }


class RevalidateClaimRequest(BaseModel):
    """Request to re-validate a corrected claim after human review."""

    claim_data: dict


@app.post("/api/v1/claims/revalidate", response_model=SubmitClaimResponse)
async def revalidate_claim(request: RevalidateClaimRequest):
    """
    Re-validate a claim after human corrections.

    Used when a claim was routed to HUMAN_REQUIRED, corrected by a human,
    and now needs to be re-checked for completeness before ADR-4 triage.

    Validates required fields and updates extraction_status accordingly.
    """
    try:
        claim_data = request.claim_data

        # Debug: print received claim data
        print(f"\n=== Re-validation Request ===")
        print(f"Claim: {claim_data.get('source_claim_ref', 'unknown')}")
        print(f"Extraction status: {claim_data.get('extraction_status')}")

        # Required fields that must be present and non-empty
        required_fields = [
            "member_id", "member_name_last", "member_name_first",
            "date_of_service_start", "date_of_service_end", "claim_type",
            "icd10_codes", "cpt_codes", "prior_auth_required", "payer_name"
        ]

        missing_fields = []
        for field in required_fields:
            value = claim_data.get(field)
            # Debug: print field values
            print(f"  {field}: {repr(value)} (type: {type(value).__name__})")

            if value is None or value == "" or value == "MISSING":
                missing_fields.append(field)
            elif isinstance(value, list) and len(value) == 0:
                missing_fields.append(field)
            elif isinstance(value, list) and len(value) == 1 and value[0] == "MISSING":
                missing_fields.append(field)

        # If still missing required fields, return HUMAN_REQUIRED
        if missing_fields:
            return SubmitClaimResponse(
                claim_id=claim_data.get("claim_id"),
                extraction_status="HUMAN_REQUIRED",
                low_confidence_fields=missing_fields,
                message=f"Still missing required fields: {', '.join(missing_fields)}. Claim remains in human review."
            )

        # All required fields present → update to AUTO_COMPLETE
        claim_data["extraction_status"] = "AUTO_COMPLETE"
        claim_data["low_confidence_fields"] = []

        # Try to construct NormalizedClaimRecord to validate format
        try:
            # Remove fields that might cause validation issues
            clean_claim_data = claim_data.copy()

            # Ensure claim_id is UUID or None
            if "claim_id" in clean_claim_data and clean_claim_data["claim_id"]:
                from uuid import UUID
                try:
                    UUID(clean_claim_data["claim_id"])
                except:
                    clean_claim_data["claim_id"] = None

            # Add required metadata fields if missing
            from datetime import datetime, timedelta
            if "sla_queue" not in clean_claim_data:
                from ..models import SLAQueue
                clean_claim_data["sla_queue"] = SLAQueue.STANDARD
            if "sla_deadline" not in clean_claim_data:
                clean_claim_data["sla_deadline"] = datetime.utcnow() + timedelta(days=7)
            if "intake_agent_version" not in clean_claim_data:
                clean_claim_data["intake_agent_version"] = agent.agent_version
            if "created_by" not in clean_claim_data:
                clean_claim_data["created_by"] = "AGENT:ADR-1"

            claim = NormalizedClaimRecord(**clean_claim_data)

            # Validate claim
            is_valid, errors = validator.validate_claim(claim)
            if not is_valid:
                return SubmitClaimResponse(
                    claim_id=claim_data.get("claim_id"),
                    extraction_status="HUMAN_REQUIRED",
                    low_confidence_fields=list(errors.keys()),
                    message=f"Validation errors: {errors}"
                )

            # Write to CMS
            cms_response = await cms_api.create_claim(claim)

            if "error" in cms_response:
                return SubmitClaimResponse(
                    claim_id=None,
                    extraction_status="PENDING_DUPLICATE",
                    low_confidence_fields=[],
                    message=f"Duplicate claim: {cms_response['existing_claim_id']}",
                )

            return SubmitClaimResponse(
                claim_id=cms_response["claim_id"],
                extraction_status="AUTO_COMPLETE",
                low_confidence_fields=[],
                message="Claim re-validated successfully and queued for triage"
            )

        except Exception as e:
            # Pydantic validation failed
            print(f"⚠️  Pydantic validation error: {e}")
            import traceback
            print(traceback.format_exc())

            return SubmitClaimResponse(
                claim_id=claim_data.get("claim_id"),
                extraction_status="HUMAN_REQUIRED",
                low_confidence_fields=["validation_error"],
                message=f"Validation error: {str(e)}"
            )

    except Exception as e:
        import traceback
        print(f"ERROR in revalidate_claim: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
