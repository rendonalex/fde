"""
Chase Engine: Core reasoning logic for PA chase timing recommendations
"""
from datetime import date, timedelta
from typing import Optional, Tuple
from .models import (
    PriorAuthorization, ChaseRecommendation, PAStatus,
    ActionType, ConfidenceLevel, InsurerPattern
)
from .pattern_library import PatternLibrary


class ChaseEngine:
    """
    Core reasoning engine for PA chase timing.
    Implements the decision tree from agent mapping Autonomy Matrix.
    """

    def __init__(self, pattern_library: PatternLibrary):
        self.pattern_library = pattern_library
        self.learning_phase = True  # Set to False when agent transitions to production

    def generate_recommendation(self, pa: PriorAuthorization, current_date: date) -> ChaseRecommendation:
        """
        Main entry point: Generate chase recommendation for a PA.
        Implements decision tree from agent mapping Section 3 (Autonomy Matrix).
        """

        # Step 1: Check escalation triggers first (highest priority)
        escalation = self._check_escalation_triggers(pa, current_date)
        if escalation:
            return escalation

        # Step 2: Retrieve insurer pattern
        pattern = self.pattern_library.get_pattern(pa.insurer)
        if not pattern:
            # Unknown insurer → escalate to Dana
            return self._escalate_unknown_insurer(pa)

        # Step 3: Calculate chase date and predicted approval date
        chase_date, predicted_approval = self._calculate_chase_timing(pa, pattern)

        # Step 4: Determine action based on current date vs chase date
        if current_date < chase_date:
            # Too early to chase
            return self._recommend_wait(pa, chase_date, predicted_approval, pattern)

        elif current_date >= chase_date:
            # Time to chase (or overdue)
            return self._recommend_chase(pa, chase_date, predicted_approval, pattern, current_date)

    def _check_escalation_triggers(self, pa: PriorAuthorization, current_date: date) -> Optional[ChaseRecommendation]:
        """
        Check escalation triggers from agent mapping Section 1 (Escalation Triggers).
        Returns escalation recommendation if any trigger fires, else None.
        """

        # Trigger 1: Unpredictable insurer (Aetna)
        unpredictable = self.pattern_library.get_unpredictable_insurers()
        if pa.insurer in unpredictable:
            return ChaseRecommendation(
                action=ActionType.ESCALATE_TO_DANA,
                pa_id=pa.pa_id,
                patient_name=pa.patient_name,
                insurer=pa.insurer,
                procedure=pa.procedure_type,
                submission_date=pa.submission_date,
                procedure_date=pa.procedure_date,
                recommended_chase_date=None,
                rationale=f"{pa.insurer} has unpredictable timing (no stable pattern). Recommend manual timing decision by Dana.",
                confidence=ConfidenceLevel.HIGH,
                predicted_approval_date=None,
                escalation_reason="Unpredictable insurer (no stable SLA pattern)"
            )

        # Trigger 2: PA pending <3 days before procedure (urgent)
        days_until_procedure = (pa.procedure_date - current_date).days
        if days_until_procedure < 3 and pa.status == PAStatus.PENDING:
            return ChaseRecommendation(
                action=ActionType.URGENT_FLAG,
                pa_id=pa.pa_id,
                patient_name=pa.patient_name,
                insurer=pa.insurer,
                procedure=pa.procedure_type,
                submission_date=pa.submission_date,
                procedure_date=pa.procedure_date,
                recommended_chase_date=current_date,  # Chase immediately
                rationale=f"URGENT: Procedure in {days_until_procedure} days, PA still pending. Recommend immediate phone chase to insurer.",
                confidence=ConfidenceLevel.HIGH,
                predicted_approval_date=None,
                escalation_reason=f"PA pending <3 days before procedure (high risk of visit abort)"
            )

        # Trigger 3: PA status = denied (escalate for denial resolution)
        if pa.status == PAStatus.DENIED:
            # Check for known denial pattern
            pattern = self.pattern_library.find_denial_pattern(
                pa.insurer, pa.procedure_type, pa.denial_reason or ""
            )
            workaround = pattern.workaround_suggestion if pattern else "No known pattern; recommend Dana review denial reason and coordinate resubmission."

            return ChaseRecommendation(
                action=ActionType.ESCALATE_TO_DANA,
                pa_id=pa.pa_id,
                patient_name=pa.patient_name,
                insurer=pa.insurer,
                procedure=pa.procedure_type,
                submission_date=pa.submission_date,
                procedure_date=pa.procedure_date,
                recommended_chase_date=None,
                rationale=f"PA denied. Suggested workaround: {workaround}",
                confidence=ConfidenceLevel.MEDIUM if pattern else ConfidenceLevel.LOW,
                predicted_approval_date=None,
                escalation_reason="PA denial requires human review and resubmission decision"
            )

        # No escalation triggers fired
        return None

    def _escalate_unknown_insurer(self, pa: PriorAuthorization) -> ChaseRecommendation:
        """Escalate PA with unknown insurer"""
        return ChaseRecommendation(
            action=ActionType.ESCALATE_TO_DANA,
            pa_id=pa.pa_id,
            patient_name=pa.patient_name,
            insurer=pa.insurer,
            procedure=pa.procedure_type,
            submission_date=pa.submission_date,
            procedure_date=pa.procedure_date,
            recommended_chase_date=None,
            rationale=f"No historical data for {pa.insurer}. Recommend manual timing decision by Dana.",
            confidence=ConfidenceLevel.LOW,
            predicted_approval_date=None,
            escalation_reason="Unknown insurer (not in pattern library)"
        )

    def _calculate_chase_timing(self, pa: PriorAuthorization, pattern: InsurerPattern) -> Tuple[date, date]:
        """
        Calculate optimal chase date and predicted approval date.
        Chase date = submission date + (SLA - 1) day
        Predicted approval = submission date + SLA days

        Rationale: Chase 1 day before expected approval to give insurer time to process.
        """
        predicted_approval = pa.submission_date + timedelta(days=pattern.sla_days)
        chase_date = pa.submission_date + timedelta(days=pattern.sla_days - 1)

        # Guardrail: Never chase before day 3 (insurers don't process that fast)
        earliest_chase = pa.submission_date + timedelta(days=3)
        if chase_date < earliest_chase:
            chase_date = earliest_chase

        return chase_date, predicted_approval

    def _recommend_wait(self, pa: PriorAuthorization, chase_date: date, predicted_approval: date, pattern: InsurerPattern) -> ChaseRecommendation:
        """Generate "wait" recommendation (too early to chase)"""
        return ChaseRecommendation(
            action=ActionType.WAIT,
            pa_id=pa.pa_id,
            patient_name=pa.patient_name,
            insurer=pa.insurer,
            procedure=pa.procedure_type,
            submission_date=pa.submission_date,
            procedure_date=pa.procedure_date,
            recommended_chase_date=chase_date,
            rationale=f"Too early to chase. {pa.insurer} typically approves in {pattern.sla_days} days (pattern based on {pattern.sample_size} cases). Recommend chase on {chase_date.isoformat()}.",
            confidence=pattern.confidence,
            predicted_approval_date=predicted_approval
        )

    def _recommend_chase(self, pa: PriorAuthorization, chase_date: date, predicted_approval: date, pattern: InsurerPattern, current_date: date) -> ChaseRecommendation:
        """Generate "chase now" recommendation"""
        days_overdue = (current_date - chase_date).days

        if days_overdue == 0:
            timing_note = "Chase recommended today."
        elif days_overdue > 0:
            timing_note = f"Chase is {days_overdue} day(s) overdue. Recommend immediate follow-up."
        else:
            timing_note = "Chase recommended now."

        return ChaseRecommendation(
            action=ActionType.RECOMMEND_CHASE,
            pa_id=pa.pa_id,
            patient_name=pa.patient_name,
            insurer=pa.insurer,
            procedure=pa.procedure_type,
            submission_date=pa.submission_date,
            procedure_date=pa.procedure_date,
            recommended_chase_date=chase_date,
            rationale=f"{timing_note} {pa.insurer} pattern: approves in {pattern.sla_days} days (±{pattern.variance_days:.1f} days, {pattern.sample_size} cases). Predicted approval: {predicted_approval.isoformat()}.",
            confidence=pattern.confidence,
            predicted_approval_date=predicted_approval
        )

    def detect_anomaly(self, pa: PriorAuthorization, actual_approval_date: date) -> Optional[str]:
        """
        Detect if actual approval timing deviates >2 days from predicted.
        Returns anomaly message if detected, else None.
        """
        pattern = self.pattern_library.get_pattern(pa.insurer)
        if not pattern:
            return None

        predicted_approval = pa.submission_date + timedelta(days=pattern.sla_days)
        deviation_days = (actual_approval_date - predicted_approval).days

        if abs(deviation_days) > 2:
            direction = "earlier" if deviation_days < 0 else "later"
            return f"ANOMALY: {pa.insurer} approved {abs(deviation_days)} days {direction} than predicted ({predicted_approval.isoformat()}). Actual: {actual_approval_date.isoformat()}. Possible SLA policy change?"

        return None

    def process_dana_correction(self, pa_id: str, agent_recommended: date, dana_corrected: date, insurer: str) -> str:
        """
        Log Dana's correction and determine if pattern update needed.
        In production, this would store to episodic memory (vector DB).
        For prototype, returns message indicating action taken.
        """
        correction_days = (dana_corrected - agent_recommended).days

        if abs(correction_days) <= 1:
            return f"Minor correction ({correction_days} days) logged. No pattern update needed."

        elif abs(correction_days) > 1:
            direction = "later" if correction_days > 0 else "earlier"
            return f"Significant correction: Dana recommended chase {abs(correction_days)} days {direction}. Flag for pattern review after 3+ similar corrections for {insurer}."
