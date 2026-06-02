"""
ADR-2 Triage Agent for Adverse Event Classification

Implements seriousness classification (ICH E2A), expectedness assessment (RSI matching),
reportability recommendation (FDA 21 CFR 314.80), and signal detection (FDA May 2026 Guidance).

Key responsibilities:
- Seriousness: Classify per ICH E2A criteria (death, life-threatening, hospitalization, etc.)
- Expectedness: Match AE terms against product RSI using MedDRA hierarchy
- Reportability: Determine expedited (15-day) vs periodic vs non-reportable
- Signal Detection: Flag 3-cases-in-90-days patterns (FDA Requirement 3)
- MSO Review: Track human review actions and rationale (FDA Requirement 2)
"""

import json
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from agents.models import (
    AECasePackage,
    TriageRecommendation,
    SeriousnessClassification,
    ExpectednessSignal,
    ReportabilityRecommendation,
    MSOFlags,
    AuditTrail,
    SignalPattern,
    SeriousnessCriterion,
    RSIMatchType,
    ReportabilityType,
    Jurisdiction,
    DeepReviewReason,
    MSOAction
)
from agents.mock_apis import (
    MockMedDRAAPI,
    MockPVCaseManagementAPI,
    MockProductRSIDatabase,
    APIResponse
)


class ADR2TriageAgent:
    """
    ADR-2 Triage Agent: Classifies AE cases for seriousness, expectedness, and reportability.
    Consumes AECasePackage from ADR-1, outputs TriageRecommendation.
    """

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        meddra_api: Optional[MockMedDRAAPI] = None,
        pv_api: Optional[MockPVCaseManagementAPI] = None,
        rsi_database: Optional[MockProductRSIDatabase] = None
    ):
        """
        Initialize ADR-2 agent with API clients.

        Args:
            anthropic_api_key: Anthropic API key for Claude integration
            meddra_api: MedDRA API client (defaults to mock)
            pv_api: PV Case Management API (defaults to mock)
            rsi_database: Product RSI database (defaults to mock)
        """
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")

        # Initialize API clients
        self.meddra_api = meddra_api or MockMedDRAAPI()
        self.pv_api = pv_api or MockPVCaseManagementAPI()
        self.rsi_database = rsi_database or MockProductRSIDatabase()

        # Model version for FDA audit trail
        self.model_version = "ADR2-v1.0-sonnet4.6"

    def classify_case(self, case_package: AECasePackage) -> Tuple[TriageRecommendation, Dict[str, Any]]:
        """
        Classify AE case for seriousness, expectedness, and reportability.

        Args:
            case_package: AECasePackage from ADR-1 intake agent

        Returns:
            Tuple of (TriageRecommendation, classification_log)
        """
        classification_log = {
            "case_id": case_package.case_id,
            "started_at": datetime.now().isoformat(),
            "model_version": self.model_version
        }

        # Step 1: Seriousness classification
        seriousness = self._classify_seriousness(case_package)
        classification_log["seriousness"] = {
            "serious": seriousness.serious,
            "criteria_matched": [c.value for c in seriousness.criteria_matched],
            "confidence": seriousness.confidence
        }

        # Step 2: Expectedness assessment
        expectedness = self._assess_expectedness(case_package)
        classification_log["expectedness"] = {
            "unexpected": expectedness.unexpected,
            "rsi_match": expectedness.rsi_match.value,
            "confidence": expectedness.confidence
        }

        # Step 3: Signal detection
        signal_pattern = self._detect_signal_pattern(case_package)
        signal_detected = signal_pattern is not None
        classification_log["signal_detection"] = {
            "signal_detected": signal_detected,
            "case_count": signal_pattern.case_count if signal_pattern else 0
        }

        # Step 4: Reportability recommendation
        reportability = self._determine_reportability(
            seriousness=seriousness,
            expectedness=expectedness,
            case_package=case_package
        )
        classification_log["reportability"] = {
            "recommendation": reportability.recommendation.value,
            "jurisdictions": [j.value for j in reportability.jurisdictions],
            "confidence": reportability.confidence
        }

        # Step 5: MSO flags (deep review triggers)
        mso_flags = self._determine_mso_flags(
            seriousness=seriousness,
            expectedness=expectedness,
            signal_detected=signal_detected,
            case_package=case_package
        )
        classification_log["mso_flags"] = {
            "deep_review_required": mso_flags.deep_review_required,
            "reasons": [r.value for r in mso_flags.reason]
        }

        # Step 6: Audit trail
        audit_trail = self._build_audit_trail(
            case_package=case_package,
            seriousness=seriousness,
            expectedness=expectedness,
            reportability=reportability
        )

        # Build final recommendation
        recommendation = TriageRecommendation(
            case_id=case_package.case_id,
            seriousness_classification=seriousness,
            expectedness_signal=expectedness,
            reportability_recommendation=reportability,
            signal_detection_flag=signal_detected,
            signal_pattern=signal_pattern,
            mso_flags=mso_flags,
            audit_trail=audit_trail,
            model_version_adr2=self.model_version
        )

        classification_log["completed_at"] = datetime.now().isoformat()
        classification_log["recommendation"] = recommendation.dict()

        return recommendation, classification_log

    def _classify_seriousness(self, case_package: AECasePackage) -> SeriousnessClassification:
        """
        Classify seriousness using ICH E2A criteria via Claude.
        Returns: SeriousnessClassification with criteria matched and confidence.
        """
        # Build system prompt for seriousness classification
        system_prompt = self._build_seriousness_prompt()

        # Build user prompt with case data
        user_prompt = f"""
Classify the seriousness of this adverse event case per ICH E2A criteria.

**Case Data:**
- **Patient**: {case_package.patient.age or 'unknown'} years, {case_package.patient.sex}
- **Suspect Drug**: {case_package.suspect_drug.name}, dose: {case_package.suspect_drug.dose}
- **AE Description**: {case_package.ae_description.narrative}
- **AE Onset**: {case_package.temporal.ae_onset_date or 'unknown'}
- **Outcome**: {case_package.ae_description.outcome.value if case_package.ae_description.outcome else 'unknown'}

**Medical History**: {case_package.medical_history.narrative if case_package.medical_history else 'None reported'}

**Instructions:**
1. Determine if case meets ANY ICH E2A seriousness criterion
2. List ALL criteria that are met (may be multiple)
3. Provide confidence score (0.0-1.0)
4. Provide reasoning for each criterion matched

Output valid JSON only (no markdown):
{{
  "serious": true/false,
  "criteria_matched": ["DEATH", "LIFE_THREATENING", ...],
  "confidence": 0.95,
  "reasoning": "Explanation of classification decision"
}}
"""

        # Call Claude API
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)

            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            # Parse JSON response
            response_text = response.content[0].text
            classification_data = json.loads(response_text)

            # Map string criteria to enum
            criteria_enums = [
                SeriousnessCriterion(c) for c in classification_data["criteria_matched"]
            ]

            return SeriousnessClassification(
                serious=classification_data["serious"],
                criteria_matched=criteria_enums,
                confidence=classification_data["confidence"],
                reasoning=classification_data["reasoning"]
            )

        except Exception as e:
            # Fallback: Conservative classification (assume serious if uncertainty)
            return SeriousnessClassification(
                serious=True,
                criteria_matched=[SeriousnessCriterion.OTHER_MEDICALLY_IMPORTANT],
                confidence=0.50,
                reasoning=f"Classification failed due to error: {str(e)}. Defaulting to serious (conservative)."
            )

    def _assess_expectedness(self, case_package: AECasePackage) -> ExpectednessSignal:
        """
        Assess expectedness by matching AE terms against product RSI.
        Uses MedDRA hierarchy for broader/narrower term matching.
        Returns: ExpectednessSignal with match type and confidence.
        """
        product_name = case_package.suspect_drug.name
        ae_narrative = case_package.ae_description.narrative

        # Step 1: Get MedDRA PT for AE narrative
        meddra_response = self.meddra_api.search_preferred_term(ae_narrative)

        if meddra_response.status_code != 200:
            # MedDRA lookup failed → novel term
            return ExpectednessSignal(
                unexpected=True,
                rsi_match=RSIMatchType.NONE,
                confidence=0.0,
                rsi_term_matched=None,
                span_citations={},
                reasoning=f"MedDRA lookup failed: {meddra_response.error_message}"
            )

        ae_pt = meddra_response.data["preferred_term"]

        # Step 2: Check RSI for exact match
        rsi_exact_match = self.rsi_database.is_expected(product_name, ae_pt)

        if rsi_exact_match:
            return ExpectednessSignal(
                unexpected=False,
                rsi_match=RSIMatchType.EXACT,
                confidence=0.95,
                rsi_term_matched=ae_pt,
                span_citations={},
                reasoning=f"AE term '{ae_pt}' found as exact match in {product_name} RSI"
            )

        # Step 3: Try synonym matching
        synonym_response = self.meddra_api.search_hierarchy(ae_pt, search_type="synonym")

        if synonym_response.status_code == 200:
            synonym_term = synonym_response.data.get("matched_term")
            if synonym_term and self.rsi_database.is_expected(product_name, synonym_term):
                return ExpectednessSignal(
                    unexpected=False,
                    rsi_match=RSIMatchType.SYNONYM,
                    confidence=0.85,
                    rsi_term_matched=synonym_term,
                    span_citations={},
                    reasoning=f"AE term '{ae_pt}' matched RSI synonym '{synonym_term}'"
                )

        # Step 4: Try broader term (SOC) matching
        broader_response = self.meddra_api.search_hierarchy(ae_pt, search_type="broader")

        if broader_response.status_code == 200:
            soc = broader_response.data.get("broader_term")
            if soc and self.rsi_database.is_expected(product_name, soc):
                return ExpectednessSignal(
                    unexpected=False,
                    rsi_match=RSIMatchType.BROADER,
                    confidence=0.70,
                    rsi_term_matched=soc,
                    span_citations={},
                    reasoning=f"AE term '{ae_pt}' matched RSI broader term (SOC) '{soc}'"
                )

        # Step 5: No match found → novel/unexpected
        return ExpectednessSignal(
            unexpected=True,
            rsi_match=RSIMatchType.NONE,
            confidence=0.0,
            rsi_term_matched=None,
            span_citations={},
            reasoning=f"AE term '{ae_pt}' not found in {product_name} RSI (novel event)"
        )

    def _detect_signal_pattern(self, case_package: AECasePackage) -> Optional[SignalPattern]:
        """
        Detect signal pattern per FDA Requirement 3.
        Queries PV system for 3-cases-in-90-days with same product + AE term.
        Returns: SignalPattern if detected, None otherwise.
        """
        product_name = case_package.suspect_drug.name
        ae_narrative = case_package.ae_description.narrative

        # Get MedDRA PT for AE term
        meddra_response = self.meddra_api.search_preferred_term(ae_narrative)
        if meddra_response.status_code != 200:
            return None

        meddra_pt = meddra_response.data["preferred_term"]
        meddra_code = meddra_response.data["meddra_code"]

        # Query PV API for signal pattern
        signal_response = self.pv_api.search_signal_pattern(
            product_name=product_name,
            ae_term=ae_narrative,
            lookback_days=90
        )

        if signal_response.status_code != 200:
            return None

        signal_data = signal_response.data

        if not signal_data["signal_detected"]:
            return None

        # Calculate window dates
        matching_cases = signal_data["matching_cases"]
        received_dates = [case["received_at"] for case in matching_cases]

        # Build SignalPattern entity
        return SignalPattern(
            product=product_name,
            meddra_pt=meddra_pt,
            meddra_code=meddra_code,
            case_count=signal_data["case_count"],
            window_start=min(received_dates),
            window_end=max(received_dates)
        )

    def _determine_reportability(
        self,
        seriousness: SeriousnessClassification,
        expectedness: ExpectednessSignal,
        case_package: AECasePackage
    ) -> ReportabilityRecommendation:
        """
        Determine reportability per FDA 21 CFR 314.80.
        Logic: serious + unexpected → 15-day expedited, else periodic or non-reportable.
        Returns: ReportabilityRecommendation with type, jurisdictions, and timeline.
        """
        # FDA 15-day rule: serious AND unexpected
        if seriousness.serious and expectedness.unexpected:
            return ReportabilityRecommendation(
                recommendation=ReportabilityType.EXPEDITED_15_DAY,
                jurisdictions=[Jurisdiction.FDA],
                rule_justification="FDA 21 CFR 314.80(c)(1)(i): Serious and unexpected adverse drug experience",
                causality_context=None,
                reasoning=f"Serious (criteria: {[c.value for c in seriousness.criteria_matched]}) and unexpected (RSI match: {expectedness.rsi_match.value}) per FDA regulations - expedited 15-day reporting required",
                span_citations={},
                confidence=min(seriousness.confidence, expectedness.confidence)
            )

        # Serious but expected → periodic reporting
        if seriousness.serious and not expectedness.unexpected:
            return ReportabilityRecommendation(
                recommendation=ReportabilityType.PERIODIC,
                jurisdictions=[],
                rule_justification="FDA 21 CFR 314.80(c)(2): Serious but expected adverse drug experience",
                causality_context=None,
                reasoning=f"Serious but expected (RSI match: {expectedness.rsi_match.value}) - include in next periodic adverse drug experience report",
                span_citations={},
                confidence=min(seriousness.confidence, expectedness.confidence)
            )

        # Not serious → non-reportable (or periodic only)
        return ReportabilityRecommendation(
            recommendation=ReportabilityType.NON_REPORTABLE,
            jurisdictions=[],
            rule_justification="Non-serious adverse event - no expedited reporting requirement",
            causality_context=None,
            reasoning="Non-serious adverse event - does not meet FDA 21 CFR 314.80 expedited reporting criteria",
            span_citations={},
            confidence=seriousness.confidence
        )

    def _determine_mso_flags(
        self,
        seriousness: SeriousnessClassification,
        expectedness: ExpectednessSignal,
        signal_detected: bool,
        case_package: AECasePackage
    ) -> MSOFlags:
        """
        Determine MSO deep review flags per FDA Requirement 2.
        Triggers: novel events, signal patterns, death/life-threatening, low confidence.
        Returns: MSOFlags with deep review requirement and reasons.
        """
        reasons = []

        # Trigger 1: Novel event (not in RSI)
        if expectedness.rsi_match == RSIMatchType.NONE:
            reasons.append(DeepReviewReason.NOVEL_AE_TERM)

        # Trigger 2: Signal detected (3-cases-in-90-days)
        if signal_detected:
            reasons.append(DeepReviewReason.SIGNAL_DETECTION)

        # Trigger 3: Death or life-threatening
        if SeriousnessCriterion.DEATH in seriousness.criteria_matched:
            reasons.append(DeepReviewReason.AMBIGUOUS_SERIOUSNESS)
        if SeriousnessCriterion.LIFE_THREATENING in seriousness.criteria_matched:
            reasons.append(DeepReviewReason.AMBIGUOUS_SERIOUSNESS)

        # Trigger 4: Low confidence in classification
        if seriousness.confidence < 0.70 or expectedness.confidence < 0.70:
            reasons.append(DeepReviewReason.AMBIGUOUS_SERIOUSNESS)

        deep_review_required = len(reasons) > 0

        return MSOFlags(
            deep_review_required=deep_review_required,
            reason=reasons
        )

    def _build_audit_trail(
        self,
        case_package: AECasePackage,
        seriousness: SeriousnessClassification,
        expectedness: ExpectednessSignal,
        reportability: ReportabilityRecommendation
    ) -> AuditTrail:
        """
        Build audit trail per FDA Requirement 1.
        Includes reasoning, regulatory references, and timestamp.
        Returns: AuditTrail entity.
        """
        regulatory_references = [
            "ICH E2A: Guidelines for Clinical Safety Data Management - Definitions and Standards for Expedited Reporting",
            "FDA 21 CFR 314.80: Postmarketing reporting of adverse drug experiences",
            "FDA May 2026 Guidance on AI-Assisted Pharmacovigilance - Requirements 1-5"
        ]

        return AuditTrail(
            timestamp=datetime.now().isoformat(),
            agent_version=self.model_version,
            regulatory_references=regulatory_references
        )

    def _build_seriousness_prompt(self) -> str:
        """
        Build system prompt for seriousness classification.
        Includes ICH E2A criteria definitions and classification instructions.
        """
        return """You are an expert adverse event classification agent trained on ICH E2A criteria.

**ICH E2A Seriousness Criteria:**
A serious adverse event (SAE) is any untoward medical occurrence that:

1. **DEATH**: Results in death of the patient
2. **LIFE_THREATENING**: Places the patient at immediate risk of death at the time of the event (not an event that hypothetically might have caused death if more severe)
3. **HOSPITALIZATION**: Requires inpatient hospitalization or prolongation of existing hospitalization
4. **DISABILITY**: Results in persistent or significant disability/incapacity (substantial disruption of ability to conduct normal life functions)
5. **CONGENITAL_ANOMALY**: Results in a congenital anomaly/birth defect
6. **OTHER_MEDICALLY_IMPORTANT**: Requires medical or surgical intervention to prevent one of the above outcomes (e.g., intensive treatment in ER without admission)

**Classification Rules:**
- An event is serious if it meets ANY of the above criteria (not all)
- List ALL criteria that are met
- If outcome is "death" → DEATH criterion matched
- If outcome is "hospitalization" → HOSPITALIZATION criterion matched
- If narrative describes "life-threatening", "risk of death", "could have died" → LIFE_THREATENING criterion matched
- If narrative describes "emergency surgery", "ICU admission", "intensive treatment" without hospitalization → OTHER_MEDICALLY_IMPORTANT
- If no criteria met → serious = false, criteria_matched = []

**Confidence Scoring:**
- High confidence (0.90-1.0): Explicit statement in narrative (e.g., "patient died", "admitted to hospital")
- Medium confidence (0.70-0.89): Strong implication from context (e.g., "emergency surgery required")
- Low confidence (0.50-0.69): Ambiguous language or missing outcome data

**Output Format:**
Return ONLY valid JSON (no markdown, no code blocks):
{
  "serious": true/false,
  "criteria_matched": ["DEATH", ...],
  "confidence": 0.95,
  "reasoning": "Brief explanation of decision"
}
"""
