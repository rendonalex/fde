"""
Core decision logic engine implementing the 5-step prior-auth check process.

Implements Claude.md Section 3: Core Decision Logic.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging

from app.models.prior_auth_check import (
    PriorAuthCheck,
    CheckStatus,
    PriorAuthStatus,
    AIRecommendation,
    ConfidenceScore,
)
from app.adapters import AthenaHealthAdapter, PriorAuthDBAdapter, InsuranceRequirementsAdapter
from app.services.fuzzy_matcher import FuzzyMatcher
from app.database import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PriorAuthDecisionEngine:
    """
    Core decision logic for prior-authorization checks.

    Implements the 5-step process per Claude.md Section 3:
    1. Determine if prior-auth is required
    2. Locate prior-auth documentation
    3. Validate prior-auth matches procedure
    4. Check expiration status
    5. Generate recommendation and confidence score
    """

    def __init__(
        self,
        athena_adapter: AthenaHealthAdapter,
        prior_auth_adapter: PriorAuthDBAdapter,
        insurance_adapter: InsuranceRequirementsAdapter,
    ):
        self.athena_adapter = athena_adapter
        self.prior_auth_adapter = prior_auth_adapter
        self.insurance_adapter = insurance_adapter
        self.fuzzy_matcher = FuzzyMatcher(threshold=settings.fuzzy_match_threshold)
        logger.info("Initialized PriorAuthDecisionEngine")

    async def execute_check(self, check: PriorAuthCheck, appointment_data: Dict[str, Any]) -> PriorAuthCheck:
        """
        Execute complete 5-step prior-auth check.

        Args:
            check: PriorAuthCheck entity to populate
            appointment_data: Appointment details from EHR

        Returns:
            Updated PriorAuthCheck entity with AI recommendation
        """
        logger.info(f"Starting prior-auth check {check.check_id} for appointment {check.appointment_id}")

        try:
            # Transition to CHECKING state
            check.transition_to(CheckStatus.CHECKING)

            # Step 1: Determine if prior-auth required
            result = await self.step1_determine_requirement(check, appointment_data)
            if result["exit"]:
                return check

            # Step 2: Locate prior-auth documentation
            prior_auth_records = await self.step2_locate_prior_auths(check, appointment_data)
            if check.status != CheckStatus.CHECKING:
                return check  # Escalated or failed

            # Step 3: Validate match
            matched_record = await self.step3_validate_match(check, prior_auth_records, appointment_data)
            if check.status != CheckStatus.CHECKING:
                return check  # Escalated

            # Step 4: Check expiration
            await self.step4_check_expiration(check, matched_record, appointment_data)
            if check.status != CheckStatus.CHECKING:
                return check  # May have escalated

            # Step 5: Generate final recommendation
            self.step5_generate_recommendation(check)

            # Transition to human review
            if check.status == CheckStatus.CHECKING:
                check.transition_to(CheckStatus.AWAITING_HUMAN_REVIEW)

            logger.info(
                f"Prior-auth check {check.check_id} completed: "
                f"recommendation={check.ai_recommendation}, confidence={check.confidence_score}"
            )

        except Exception as e:
            logger.error(f"Error during prior-auth check {check.check_id}: {e}", exc_info=True)
            check.transition_to(CheckStatus.FAILED, reason=f"System error: {str(e)}")
            check.escalation_reason = f"System error during check: {str(e)}"

        return check

    async def step1_determine_requirement(
        self, check: PriorAuthCheck, appointment_data: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        Step 1: Determine if prior-authorization is required [per Claude.md Section 3, Step 1].

        Returns:
            {"exit": bool} - True if check should exit early
        """
        logger.info(f"Step 1: Determining prior-auth requirement for {check.procedure_code}")

        # Check if procedure codes are empty
        if not check.procedure_code or check.procedure_code.strip() == "":
            logger.info("No procedures scheduled, prior-auth not applicable")
            check.prior_auth_required = False
            check.transition_to(CheckStatus.COMPLETED)
            check.confidence_rationale = "No procedures scheduled, prior-auth not applicable"
            return {"exit": True}

        # Query insurance requirements database
        try:
            requirement_data = await self.insurance_adapter.check_prior_auth_requirement(
                check.insurance_policy_id, check.procedure_code
            )

            if requirement_data["prior_auth_required"] is True:
                logger.info(f"Prior-auth required for CPT {check.procedure_code}")
                check.prior_auth_required = True
                return {"exit": False}  # Continue to Step 2

            elif requirement_data["prior_auth_required"] is False:
                logger.info(f"Prior-auth not required for CPT {check.procedure_code}")
                check.prior_auth_required = False
                check.transition_to(CheckStatus.COMPLETED)
                check.confidence_rationale = f"Procedure {check.procedure_code} does not require prior-authorization"
                return {"exit": True}

            else:  # None or unknown
                logger.warning(f"Cannot determine prior-auth requirement for CPT {check.procedure_code}")
                check.confidence_score = ConfidenceScore.LOW
                check.transition_to(
                    CheckStatus.ESCALATED,
                    reason=f"Cannot determine if prior-auth required for CPT {check.procedure_code}"
                )
                return {"exit": True}

        except Exception as e:
            logger.error(f"Error checking insurance requirements: {e}")
            check.confidence_score = ConfidenceScore.LOW
            check.transition_to(
                CheckStatus.ESCALATED,
                reason=f"Insurance requirements database error: {str(e)}"
            )
            return {"exit": True}

    async def step2_locate_prior_auths(
        self, check: PriorAuthCheck, appointment_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Step 2: Locate prior-authorization documentation [per Claude.md Section 3, Step 2].

        Returns:
            List of prior-auth records found
        """
        logger.info(f"Step 2: Locating prior-auths for patient {check.patient_id}")

        try:
            prior_auth_records = await self.prior_auth_adapter.query_prior_auths(
                check.patient_id,
                check.insurance_policy_id,
                check.scheduled_date
            )

            # Store record IDs
            record_ids = [rec["prior_auth_id"] for rec in prior_auth_records]
            check.set_prior_auth_records_list(record_ids)

            if len(prior_auth_records) == 0:
                logger.warning(f"No prior-auth found for patient {check.patient_id}")
                check.prior_auth_status = PriorAuthStatus.MISSING
                check.ai_recommendation = AIRecommendation.ESCALATE
                check.confidence_score = ConfidenceScore.HIGH  # High confidence it's missing
                check.transition_to(
                    CheckStatus.AWAITING_HUMAN_REVIEW,
                    reason=f"No active prior-auth found for patient {check.patient_id}, procedure {check.procedure_code}"
                )
                return []

            logger.info(f"Found {len(prior_auth_records)} prior-auth record(s)")
            return prior_auth_records

        except Exception as e:
            logger.error(f"Prior-auth database query failed: {e}")
            check.transition_to(
                CheckStatus.FAILED,
                reason="Prior-auth database unavailable, manual check required"
            )
            return []

    async def step3_validate_match(
        self, check: PriorAuthCheck, prior_auth_records: List[Dict[str, Any]], appointment_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Step 3: Validate prior-authorization matches scheduled procedure [per Claude.md Section 3, Step 3].

        Returns:
            Matched prior-auth record or None
        """
        logger.info(f"Step 3: Validating prior-auth match for CPT {check.procedure_code}")

        if not prior_auth_records:
            return None

        # Case 1: Single prior-auth record
        if len(prior_auth_records) == 1:
            prior_auth = prior_auth_records[0]
            match_result = self._check_cpt_match(check, prior_auth)

            if match_result["exact_match"]:
                logger.info(f"Exact CPT match found with prior-auth {prior_auth['prior_auth_id']}")
                check.matched_prior_auth_id = prior_auth["prior_auth_id"]
                check.confidence_score = ConfidenceScore.HIGH
                return prior_auth

            elif match_result["fuzzy_match"]:
                logger.info(f"Fuzzy match found with prior-auth {prior_auth['prior_auth_id']}")
                check.matched_prior_auth_id = prior_auth["prior_auth_id"]
                check.confidence_score = ConfidenceScore.MEDIUM
                check.escalation_reason = (
                    f"Prior-auth CPT codes don't exactly match procedure, but service description similar "
                    f"(score: {match_result['fuzzy_score']:.2f})"
                )
                return prior_auth

            else:
                logger.warning("Prior-auth found but CPT code mismatch")
                check.prior_auth_status = PriorAuthStatus.AMBIGUOUS
                check.ai_recommendation = AIRecommendation.ESCALATE
                check.confidence_score = ConfidenceScore.LOW
                check.transition_to(
                    CheckStatus.AWAITING_HUMAN_REVIEW,
                    reason=f"Prior-auth CPT mismatch: covers {prior_auth.get('approved_cpt_codes')}, "
                           f"appointment is {check.procedure_code}"
                )
                return None

        # Case 2: Multiple prior-auth records
        else:
            matched_records = []
            for prior_auth in prior_auth_records:
                match_result = self._check_cpt_match(check, prior_auth)
                if match_result["exact_match"]:
                    matched_records.append(prior_auth)

            if len(matched_records) == 1:
                logger.info(f"Single exact match found among {len(prior_auth_records)} records")
                check.matched_prior_auth_id = matched_records[0]["prior_auth_id"]
                check.confidence_score = ConfidenceScore.HIGH
                return matched_records[0]

            elif len(matched_records) > 1:
                logger.warning(f"Multiple prior-auths match procedure: {len(matched_records)}")
                check.prior_auth_status = PriorAuthStatus.AMBIGUOUS
                check.ai_recommendation = AIRecommendation.ESCALATE
                check.confidence_score = ConfidenceScore.LOW
                approval_numbers = [rec.get("approval_number") for rec in matched_records]
                check.transition_to(
                    CheckStatus.AWAITING_HUMAN_REVIEW,
                    reason=f"Multiple prior-auths match procedure: {approval_numbers}"
                )
                return None

            else:
                logger.warning("Multiple prior-auths found but none match procedure CPT code")
                check.prior_auth_status = PriorAuthStatus.AMBIGUOUS
                check.ai_recommendation = AIRecommendation.ESCALATE
                check.confidence_score = ConfidenceScore.LOW
                check.transition_to(
                    CheckStatus.AWAITING_HUMAN_REVIEW,
                    reason="Multiple prior-auths found but none match scheduled procedure CPT code"
                )
                return None

    def _check_cpt_match(self, check: PriorAuthCheck, prior_auth: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if prior-auth CPT codes match procedure.

        Returns:
            {
                "exact_match": bool,
                "fuzzy_match": bool,
                "fuzzy_score": float
            }
        """
        approved_codes = prior_auth.get("approved_cpt_codes", [])

        # Check exact CPT match
        if check.procedure_code in approved_codes:
            return {"exact_match": True, "fuzzy_match": False, "fuzzy_score": 1.0}

        # Check fuzzy match on service description
        if check.procedure_description and prior_auth.get("approved_service_description"):
            is_match, score = self.fuzzy_matcher.is_match(
                check.procedure_description,
                prior_auth["approved_service_description"]
            )
            if is_match:
                return {"exact_match": False, "fuzzy_match": True, "fuzzy_score": score}

        return {"exact_match": False, "fuzzy_match": False, "fuzzy_score": 0.0}

    async def step4_check_expiration(
        self, check: PriorAuthCheck, prior_auth: Optional[Dict[str, Any]], appointment_data: Dict[str, Any]
    ) -> None:
        """
        Step 4: Check prior-authorization expiration status [per Claude.md Section 3, Step 4].
        """
        if not prior_auth:
            return

        logger.info(f"Step 4: Checking expiration for prior-auth {prior_auth['prior_auth_id']}")

        # Parse dates
        expiration_date = datetime.fromisoformat(prior_auth["expiration_date"].replace("Z", "+00:00"))
        scheduled_date = check.scheduled_date

        # Calculate days until expiration
        days_until_expiration = (expiration_date.date() - scheduled_date.date()).days

        logger.info(f"Days until expiration: {days_until_expiration}")

        # Apply expiration logic per Claude.md A44
        if days_until_expiration < 0:
            # Expired
            check.prior_auth_status = PriorAuthStatus.EXPIRED
            check.ai_recommendation = AIRecommendation.RESCHEDULE
            check.confidence_score = ConfidenceScore.HIGH
            check.confidence_rationale = (
                f"Prior-auth expired on {expiration_date.date()}, appointment scheduled for {scheduled_date.date()}"
            )

        elif days_until_expiration == 0:
            # Expires on appointment day - escalate per Claude.md A43
            check.prior_auth_status = PriorAuthStatus.EXPIRING_SOON
            check.ai_recommendation = AIRecommendation.ESCALATE
            check.confidence_score = ConfidenceScore.MEDIUM
            check.confidence_rationale = "Prior-auth expires on appointment date, recommend human review"
            check.escalation_reason = "Prior-auth expires same day as appointment"

        elif 0 < days_until_expiration <= settings.expiration_warning_days:
            # Expiring soon
            check.prior_auth_status = PriorAuthStatus.EXPIRING_SOON
            check.ai_recommendation = AIRecommendation.ESCALATE
            check.confidence_score = ConfidenceScore.MEDIUM
            check.confidence_rationale = f"Prior-auth expires in {days_until_expiration} days, within warning threshold"
            check.escalation_reason = f"Prior-auth expires within {settings.expiration_warning_days} days of appointment"

        else:
            # Valid
            check.prior_auth_status = PriorAuthStatus.VALID
            check.ai_recommendation = AIRecommendation.PROCEED
            # Confidence depends on match quality from Step 3
            if check.confidence_score != ConfidenceScore.MEDIUM:
                check.confidence_score = ConfidenceScore.HIGH
            check.confidence_rationale = (
                f"Prior-auth valid until {expiration_date.date()}, {days_until_expiration} days after appointment"
            )

    def step5_generate_recommendation(self, check: PriorAuthCheck) -> None:
        """
        Step 5: Generate final recommendation and confidence score [per Claude.md Section 3, Step 5].

        Synthesizes Steps 1-4 into final recommendation.
        """
        logger.info("Step 5: Generating final recommendation")

        # Confidence and recommendation already set by previous steps
        # This step synthesizes and ensures consistency

        if not check.confidence_rationale:
            # Generate default rationale
            check.confidence_rationale = (
                f"Prior-auth status: {check.prior_auth_status}, "
                f"AI recommendation: {check.ai_recommendation}, "
                f"Confidence: {check.confidence_score}"
            )

        logger.info(
            f"Final recommendation: {check.ai_recommendation} (confidence: {check.confidence_score})"
        )
