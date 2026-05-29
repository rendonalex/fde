"""Core ADR-1 Intake Agent with Claude API integration."""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Optional

from anthropic import AsyncAnthropic
from pydantic import ValidationError

from ..models import (
    ExtractionResult,
    ExtractionStatus,
    NormalizedClaimRecord,
    RoutingDecision,
    SLAQueue,
)
from ..prompts import get_system_prompt


class IntakeAgent:
    """ADR-1 Claim Intake and Format Validation Agent."""

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        model: str = "claude-haiku-4-5-20251001",
        agent_version: str = "1.0.0",
    ):
        """
        Initialize the intake agent.

        Args:
            anthropic_api_key: Anthropic API key (or from env)
            model: Claude model to use
            agent_version: Agent version for audit trail
        """
        api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY required")

        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.agent_version = agent_version
        self.system_prompt = get_system_prompt()

    async def process_extraction(
        self, extraction_result: ExtractionResult
    ) -> NormalizedClaimRecord:
        """
        Process extraction result and return validated claim record.

        This is the core agent inference call.

        Args:
            extraction_result: Output from EDI parser or IDP pipeline

        Returns:
            Validated NormalizedClaimRecord
        """
        # Pre-validation: Check for null required fields
        # Per spec: "Any required field is absent or null → HUMAN_REQUIRED"
        required_fields = [
            "member_id", "member_name_last", "member_name_first",
            "date_of_service_start", "date_of_service_end", "claim_type",
            "icd10_codes", "cpt_codes", "prior_auth_required", "payer_name"
        ]

        missing_fields = []
        for field in required_fields:
            if field not in extraction_result.extracted_fields:
                missing_fields.append(field)
            else:
                field_obj = extraction_result.extracted_fields[field]
                value = field_obj.value if hasattr(field_obj, 'value') else field_obj.get('value') if isinstance(field_obj, dict) else field_obj
                if value is None or (isinstance(value, list) and len(value) == 0):
                    missing_fields.append(field)

        # If any required field is missing/null, skip LLM and return HUMAN_REQUIRED immediately
        if missing_fields:
            print(f"⚠️  Required fields missing or null: {missing_fields}")
            print(f"⚠️  Routing to HUMAN_REQUIRED without LLM call")

            # Build minimal HUMAN_REQUIRED response
            return self._build_human_required_claim(extraction_result, missing_fields)

        # Normalize prior_auth fields in extraction BEFORE sending to LLM
        # ADR-1 does NOT validate clinical correctness - ADR-4 will override based on codebook
        extraction_result = self._normalize_prior_auth(extraction_result)

        # Build user message from extraction result
        user_message = self._build_user_message(extraction_result)

        # Call Claude API
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self.system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        # Parse JSON response
        response_text = response.content[0].text

        # Extract JSON robustly — the model sometimes adds a sentence before or after the JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            raise ValueError(f"Agent returned no JSON object:\n{response_text}")

        try:
            claim_data = json.loads(json_match.group())
        except json.JSONDecodeError as e:
            raise ValueError(f"Agent returned invalid JSON: {e}\n{json_match.group()}")

        # Convert to NormalizedClaimRecord
        # Catch Pydantic validation errors and route to HUMAN_REQUIRED
        try:
            claim = self._build_claim_record(claim_data, extraction_result.intake_channel)
        except (ValueError, ValidationError) as e:
            # Validation error (e.g., prior_auth_number required but missing)
            print(f"⚠️  Pydantic validation failed: {e}")
            print(f"⚠️  Routing to HUMAN_REQUIRED due to validation error")
            return self._build_human_required_claim(extraction_result, ["validation_error"])

        return claim

    def _build_user_message(self, extraction: ExtractionResult) -> str:
        """Build user message JSON for Claude."""
        # Convert ExtractionResult to the format expected by system prompt
        message_data = {
            "source_format": extraction.source_format,
            "source_claim_ref": extraction.source_claim_ref,
            "extracted_fields": {
                field_name: {"value": field.value, "confidence": field.confidence}
                for field_name, field in extraction.extracted_fields.items()
            },
        }

        if extraction.rfc5322_headers:
            message_data["rfc5322_headers"] = extraction.rfc5322_headers

        return json.dumps(message_data, indent=2)

    def _normalize_prior_auth(self, extraction: ExtractionResult) -> ExtractionResult:
        """
        Normalize prior_auth fields based on prior_auth_number validity.
        ADR-1 does NOT validate clinical correctness - ADR-4 will override based on codebook.

        Logic:
        - Valid prior_auth_number (alphanumeric, 6-30 chars) → prior_auth_required=true
        - Invalid/missing prior_auth_number → prior_auth_required=false
        """
        def is_valid_prior_auth_number(value):
            if not value or not isinstance(value, str):
                return False
            if value.strip() == "":
                return False
            if len(value) < 6 or len(value) > 30:
                return False
            if not value.replace("-", "").replace("_", "").isalnum():
                return False
            return True

        # Get prior_auth_number from extracted fields
        prior_auth_num_field = extraction.extracted_fields.get("prior_auth_number")
        if prior_auth_num_field:
            prior_auth_num = prior_auth_num_field.value if hasattr(prior_auth_num_field, 'value') else prior_auth_num_field.get('value') if isinstance(prior_auth_num_field, dict) else prior_auth_num_field
        else:
            prior_auth_num = None

        # Normalize based on validity
        if is_valid_prior_auth_number(prior_auth_num):
            # Valid number: set required=true
            extraction.extracted_fields["prior_auth_required"] = type(prior_auth_num_field)(
                value=True,
                confidence=1.0
            ) if hasattr(prior_auth_num_field, 'value') else {"value": True, "confidence": 1.0}
        else:
            # Invalid/missing: set required=false, number=None
            extraction.extracted_fields["prior_auth_required"] = type(prior_auth_num_field)(
                value=False,
                confidence=1.0
            ) if hasattr(prior_auth_num_field, 'value') and prior_auth_num_field else {"value": False, "confidence": 1.0}

            if "prior_auth_number" in extraction.extracted_fields:
                extraction.extracted_fields["prior_auth_number"] = type(prior_auth_num_field)(
                    value=None,
                    confidence=1.0
                ) if hasattr(prior_auth_num_field, 'value') else {"value": None, "confidence": 1.0}

        return extraction

    def _build_claim_record(self, claim_data: dict, intake_channel: str) -> NormalizedClaimRecord:
        """Build NormalizedClaimRecord from agent output."""
        # Compute SLA queue and deadline (simplified logic)
        sla_queue, sla_deadline = self._compute_sla(claim_data)

        # Build record
        record = NormalizedClaimRecord(
            source_claim_ref=claim_data["source_claim_ref"],
            member_id=claim_data["member_id"],
            member_dob=claim_data.get("member_dob"),
            member_name_last=claim_data["member_name_last"],
            member_name_first=claim_data["member_name_first"],
            rendering_provider_npi=claim_data.get("rendering_provider_npi"),
            billing_provider_npi=claim_data.get("billing_provider_npi"),
            billing_provider_tax_id=claim_data.get("billing_provider_tax_id"),
            date_of_service_start=claim_data["date_of_service_start"],
            date_of_service_end=claim_data["date_of_service_end"],
            place_of_service_code=claim_data.get("place_of_service_code"),
            claim_type=claim_data["claim_type"],
            icd10_codes=claim_data["icd10_codes"],
            cpt_codes=claim_data["cpt_codes"],
            revenue_codes=claim_data.get("revenue_codes", []),
            drg_code=claim_data.get("drg_code"),
            billed_amount=claim_data.get("billed_amount"),
            currency=claim_data.get("currency", "USD"),
            payer_id=claim_data.get("payer_id"),
            payer_name=claim_data["payer_name"],
            plan_id=claim_data.get("plan_id"),
            prior_auth_required=claim_data["prior_auth_required"],
            prior_auth_number=claim_data.get("prior_auth_number"),
            intake_channel=intake_channel,
            extraction_status=ExtractionStatus(claim_data["extraction_status"]),
            field_confidence=claim_data.get("field_confidence"),
            low_confidence_fields=claim_data.get("low_confidence_fields", []),
            sla_queue=sla_queue,
            sla_deadline=sla_deadline,
            intake_agent_version=self.agent_version,
            created_by=f"AGENT:ADR-1",
            routing_decision=RoutingDecision.PENDING_TRIAGE,
        )

        return record

    def _build_human_required_claim(
        self, extraction_result: ExtractionResult, missing_fields: list[str]
    ) -> NormalizedClaimRecord:
        """Build HUMAN_REQUIRED claim when required fields are missing/null."""
        # Extract available values
        fields = extraction_result.extracted_fields

        def get_value(field_name, default=None):
            if field_name not in fields:
                return default
            field_obj = fields[field_name]
            value = field_obj.value if hasattr(field_obj, 'value') else field_obj.get('value') if isinstance(field_obj, dict) else field_obj
            # Return default if None OR empty list (for required list fields like cpt_codes, icd10_codes)
            if value is None or (isinstance(value, list) and len(value) == 0):
                return default
            return value

        def sanitize_string(value, max_length=None, pattern=None, default=None):
            """Sanitize string values to meet format constraints."""
            if value is None:
                return default
            if not isinstance(value, str):
                return default
            # Truncate if too long
            if max_length and len(value) > max_length:
                return value[:max_length]
            # Check pattern match (for tax_id, NPI, etc)
            if pattern:
                import re
                if not re.match(pattern, value):
                    return default
            return value

        # Use placeholders for missing required fields
        sla_queue = SLAQueue.STANDARD
        sla_deadline = datetime.utcnow() + timedelta(days=7)

        # Sanitize values that may violate format constraints
        billing_tax_id = sanitize_string(
            get_value("billing_provider_tax_id"),
            pattern=r"^\d{9}$",
            default=None
        )
        payer_name_value = sanitize_string(
            get_value("payer_name", "MISSING"),
            max_length=100,
            default="MISSING"
        )

        # No special prior_auth handling needed - validator removed

        return NormalizedClaimRecord(
            source_claim_ref=extraction_result.source_claim_ref,
            member_id=get_value("member_id", "MISSING"),
            member_dob=get_value("member_dob"),
            member_name_last=get_value("member_name_last", "MISSING"),
            member_name_first=get_value("member_name_first", "MISSING"),
            rendering_provider_npi=get_value("rendering_provider_npi"),
            billing_provider_npi=get_value("billing_provider_npi"),
            billing_provider_tax_id=billing_tax_id,
            date_of_service_start=get_value("date_of_service_start", "2026-01-01"),
            date_of_service_end=get_value("date_of_service_end", "2026-01-01"),
            place_of_service_code=get_value("place_of_service_code"),
            claim_type=get_value("claim_type", "PROFESSIONAL"),
            icd10_codes=get_value("icd10_codes", ["MISSING"]),
            cpt_codes=get_value("cpt_codes", ["MISSING"]),
            revenue_codes=get_value("revenue_codes", []),
            drg_code=get_value("drg_code"),
            billed_amount=get_value("billed_amount"),
            currency="USD",
            payer_id=get_value("payer_id"),
            payer_name=payer_name_value,
            plan_id=get_value("plan_id"),
            prior_auth_required=get_value("prior_auth_required", False),
            prior_auth_number=get_value("prior_auth_number"),
            intake_channel=extraction_result.intake_channel,
            extraction_status=ExtractionStatus.HUMAN_REQUIRED,
            field_confidence=None,
            low_confidence_fields=missing_fields,
            sla_queue=sla_queue,
            sla_deadline=sla_deadline,
            intake_agent_version=self.agent_version,
            created_by=f"AGENT:ADR-1",
            routing_decision=RoutingDecision.PENDING_TRIAGE,
        )

    def _compute_sla(self, claim_data: dict) -> tuple[SLAQueue, datetime]:
        """
        Compute SLA queue tier and deadline.

        Simplified: PRIORITY if prior_auth_required, else STANDARD.
        Deadline: 7 days from now.
        """
        if claim_data.get("prior_auth_required"):
            sla_queue = SLAQueue.PRIORITY
        else:
            sla_queue = SLAQueue.STANDARD

        sla_deadline = datetime.utcnow() + timedelta(days=7)

        return sla_queue, sla_deadline
