"""
ADR-4 Clinical Content Triage Agent.
Per specs/06b-capability-spec-triage.md Section 6 (Context Engineering Design).
"""

import os
import json
import re
from typing import Optional
from anthropic import Anthropic
from .models import (
    NormalizedClaimRecord,
    RoutingDecisionOutput,
    RoutingDecision,
    RoutingMode,
    ExtractionStatus
)
from .codebook import get_codebook_loader


class TriageAgent:
    """
    Clinical Content Triage Agent.
    Classifies claims as FAST_PATH or CLINICAL_PATH.
    """

    def __init__(
        self,
        mode: str = "SHADOW",
        confidence_threshold: float = 0.70,
        agent_version: str = "1.0.0"
    ):
        self.mode = RoutingMode(mode)
        self.confidence_threshold = confidence_threshold
        self.agent_version = agent_version

        # Load codebook
        self.codebook_loader = get_codebook_loader()
        self.codebook = self.codebook_loader.codebook

        # Initialize Anthropic client (required for LLM calls, but not for precondition checks)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = None  # Will raise error if classify() is called without precondition failure

        # Build system prompt with embedded codebook
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """
        Build system prompt with embedded codebook.
        Per specs/06b-capability-spec-triage.md Section 6.3.
        """
        # Serialize codebook provisions for prompt
        codebook_text = self._serialize_codebook()

        prompt = f"""MODE: {self.mode.value}
SYSTEM PROMPT — ADR-4 Clinical Content Triage Agent
Prompt version: {self.agent_version}
Criteria codebook version: {self.codebook.codebook_version}
Confidence threshold: {self.confidence_threshold}

## Role
You are the Clinical Content Triage Agent for Greenfield Health Systems. You classify every
normalized claim record as FAST_PATH or CLINICAL_PATH.

  FAST_PATH:     No clinical content. Claim can be adjudicated without physician review.
  CLINICAL_PATH: Clinical content is present. Claim requires physician review.

## Operating mode: {self.mode.value}
SHADOW — Your classification is logged for evaluation only. It does NOT route the claim.
  The current processor routing continues unchanged. Set routing_mode: SHADOW in your output.
LIVE   — Your classification IS the routing decision. It is written to CMS and determines
  the claim's processing path. Set routing_mode: LIVE in your output.
CRITICAL: Never set routing_mode: LIVE when MODE is SHADOW.

## Safety rule — false negative is the critical failure
A false negative classifies a clinical claim as FAST_PATH. This sends a patient care decision
through adjudication without physician review.

A false positive classifies an administrative claim as CLINICAL_PATH. It wastes physician time
but causes no patient harm.

WHEN IN DOUBT: route to CLINICAL_PATH.

## Clinical Content Criteria Codebook
Use the provisions below as your primary classification reference. A claim routes CLINICAL_PATH
if ANY of its fields match ANY provision's trigger conditions.

{codebook_text}

Each provision includes:
  provision_id          — cite this in criteria_provisions_matched
  clinical_category     — type of clinical content
  trigger_icd10_patterns — ICD-10 code prefixes or exact codes that trigger this provision
  trigger_cpt_patterns  — CPT code prefixes or exact codes that trigger this provision
  trigger_prior_auth_required — if true, prior_auth_required = true alone triggers this provision

## Classification procedure — follow all 6 steps before producing output
Step 1: List every clinical indicator present in the claim.
        Include: all ICD-10 codes, all CPT codes, prior_auth_required value.
Step 2: For each indicator, check whether it matches any provision's trigger conditions.
        An ICD-10 code matches if it starts with any string in trigger_icd10_patterns.
        A CPT code matches if it starts with any string in trigger_cpt_patterns.
Step 3: If any indicator matches any provision → routing_decision = CLINICAL_PATH.
        If no indicators match any provision → routing_decision = FAST_PATH.

        IMPORTANT: When no matches found, affirmatively state that the procedures/diagnoses
        do NOT require prior authorization or clinical review per codebook provisions.
        Don't just say "no match" - confirm the FAST_PATH decision is correct.
        Example: "No provisions matched. CPT 99214 (routine office visit) and diagnoses
        F41.1, M79.7 do not require prior authorization or clinical review per payer policy.
        FAST_PATH is correct."
Step 4: Compute confidence: how certain is this classification?
        Consider BOTH match specificity AND clinical coherence:

        Match specificity:
        - Exact code match (e.g., CPT 96413) = high specificity
        - Broad prefix match (e.g., CPT 70-79) = lower specificity

        Clinical coherence:
        - Do diagnosis codes align with procedures?
        - Example: J20.9 (bronchitis) + 96413 (chemotherapy) = MISMATCH
        - Mismatched diagnosis/procedure should LOWER confidence

        Scoring guidance:
        1.0 = exact match AND clinically coherent
        0.7-0.85 = exact match BUT clinically questionable/contradictory
        0.5 = broad-prefix match with clinical coherence
        0.3-0.5 = broad-prefix match with clinical questions
        0.0 = no match found at all (novel case)
Step 5: Apply fallback rule:
        If confidence < {self.confidence_threshold}:
          routing_decision = CLINICAL_PATH (override Step 3 if it said FAST_PATH)
          confidence_fallback = true
        Otherwise: confidence_fallback = false
Step 6: Output the structured JSON below. The reasoning_trace must contain your step-by-step
        work from Steps 1–5, written out. This trace is required for physician audit.

## Novel case rule
If the claim contains procedure types, diagnosis codes, or clinical documentation that no
codebook provision covers:
  routing_decision = CLINICAL_PATH
  confidence = 0.0
  criteria_provisions_matched = ["NOVEL_CASE"]
Do not attempt to infer a classification when no provision applies.

## Output format
Respond with a single JSON object only. No prose before or after the JSON.

{{
  "claim_id":                     "string — copy from input",
  "source_claim_ref":             "string — copy from input",
  "routing_decision":             "FAST_PATH | CLINICAL_PATH",
  "confidence":                   0.00,
  "confidence_fallback":          true | false,
  "clinical_indicators_detected": ["string — each indicator found in the claim"],
  "criteria_provisions_matched":  ["string — provision IDs from codebook, or ['NOVEL_CASE']"],
  "reasoning_trace":              "string — your step-by-step reasoning, Steps 1–5",
  "routing_mode":                 "{self.mode.value}"
}}
"""
        return prompt

    def _serialize_codebook(self) -> str:
        """Serialize codebook provisions for system prompt."""
        lines = []
        for provision in self.codebook_loader.provisions:
            lines.append(f"\nProvision: {provision.provision_id} — {provision.provision_name}")
            lines.append(f"  Category: {provision.clinical_category.value}")
            lines.append(f"  ICD-10 patterns: {provision.trigger_icd10_patterns}")
            lines.append(f"  CPT patterns: {provision.trigger_cpt_patterns}")
            lines.append(f"  Prior auth trigger: {provision.trigger_prior_auth_required}")
            lines.append(f"  Description: {provision.description}")

        return "\n".join(lines)

    def classify(self, claim: NormalizedClaimRecord) -> RoutingDecisionOutput:
        """
        Classify a normalized claim record using LLM with codebook reasoning.
        Per specs/06b-capability-spec-triage.md Section 6.3.

        Args:
            claim: Normalized claim record from ADR-1

        Returns:
            Routing decision with confidence and reasoning trace

        Note:
            On any error (precondition failure, JSON parse error, shadow isolation violation),
            returns safe fallback: CLINICAL_PATH with confidence=0.0 and alert logged to ops.
            Never drops a claim - patient safety requires all claims get reviewed.
        """
        # Precondition: extraction_status must be AUTO_COMPLETE
        if claim.extraction_status != ExtractionStatus.AUTO_COMPLETE:
            # Safe fallback: route to CLINICAL_PATH, alert ops
            print(f"⚠️  PRECONDITION_FAILED: Claim {claim.claim_id} has extraction_status={claim.extraction_status.value}")
            print(f"⚠️  OPS ALERT: Queue filter may be broken - HUMAN_REQUIRED claim entered triage")
            print(f"⚠️  Safe fallback: Routing to CLINICAL_PATH")

            return RoutingDecisionOutput(
                claim_id=claim.claim_id,
                source_claim_ref=claim.source_claim_ref,
                routing_decision=RoutingDecision.CLINICAL_PATH,
                confidence=0.0,
                confidence_fallback=True,
                clinical_indicators_detected=[],
                criteria_provisions_matched=["PRECONDITION_FAILED"],
                reasoning_trace=f"PRECONDITION_FAILED: extraction_status={claim.extraction_status.value}, expected AUTO_COMPLETE. Safe fallback to CLINICAL_PATH.",
                routing_mode=self.mode
            )

        # LLM-based classification (Jupyter notebook approach)
        return self._classify_with_llm(claim)

    def _classify_with_llm(self, claim: NormalizedClaimRecord) -> RoutingDecisionOutput:
        """
        Classify using LLM with system prompt (Jupyter notebook approach).
        """
        # Check if API key was provided
        if self.client is None:
            print(f"⚠️  CLASSIFICATION_FAILED: ANTHROPIC_API_KEY not set")
            print(f"⚠️  OPS ALERT: Cannot call LLM without API key")
            print(f"⚠️  Safe fallback: Routing to CLINICAL_PATH")

            return RoutingDecisionOutput(
                claim_id=claim.claim_id,
                source_claim_ref=claim.source_claim_ref,
                routing_decision=RoutingDecision.CLINICAL_PATH,
                confidence=0.0,
                confidence_fallback=True,
                clinical_indicators_detected=[],
                criteria_provisions_matched=["API_KEY_MISSING"],
                reasoning_trace="API_KEY_MISSING: ANTHROPIC_API_KEY environment variable not set. Safe fallback to CLINICAL_PATH.",
                routing_mode=self.mode
            )

        # Build user message with claim data
        user_message = json.dumps({
            "claim_id": claim.claim_id,
            "source_claim_ref": claim.source_claim_ref,
            "intake_channel": claim.intake_channel,
            "extraction_status": claim.extraction_status.value,
            "member_id": claim.member_id,
            "icd10_codes": claim.icd10_codes,
            "cpt_codes": claim.cpt_codes,
            "prior_auth_required": claim.prior_auth_required,
            "prior_auth_number": claim.prior_auth_number,
            "payer_id": claim.payer_id,
            "place_of_service": claim.place_of_service,
            "billed_amount": claim.billed_amount
        }, indent=2)

        try:
            # Call Claude with system prompt + claim data
            response = self.client.messages.create(
                model="claude-sonnet-4-6",  # or "claude-opus-4-7" for higher accuracy
                max_tokens=2000,
                temperature=0.0,  # Deterministic output
                system=self.system_prompt,  # System prompt separate in Anthropic API
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            # Parse Claude response
            result_text = response.content[0].text

            # Extract JSON robustly - the model sometimes adds text before or after the JSON
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if not json_match:
                raise ValueError(f"Agent returned no JSON object:\n{result_text}")

            # Parse JSON
            result_dict = json.loads(json_match.group())

            # Convert to RoutingDecisionOutput
            output = RoutingDecisionOutput(
                claim_id=result_dict["claim_id"],
                source_claim_ref=result_dict["source_claim_ref"],
                routing_decision=RoutingDecision(result_dict["routing_decision"]),
                confidence=float(result_dict["confidence"]),
                confidence_fallback=bool(result_dict["confidence_fallback"]),
                clinical_indicators_detected=result_dict["clinical_indicators_detected"],
                criteria_provisions_matched=result_dict["criteria_provisions_matched"],
                reasoning_trace=result_dict["reasoning_trace"],
                routing_mode=RoutingMode(result_dict["routing_mode"])
            )

            # Validate routing_mode matches agent mode (shadow isolation check)
            if output.routing_mode != self.mode:
                # Safe fallback: route to CLINICAL_PATH, alert ops (critical security issue)
                print(f"⚠️  SHADOW_ISOLATION_VIOLATION: LLM output routing_mode={output.routing_mode.value} but agent MODE={self.mode.value}")
                print(f"⚠️  OPS ALERT (CRITICAL): Shadow mode isolation breach detected")
                print(f"⚠️  Safe fallback: Routing to CLINICAL_PATH")

                return RoutingDecisionOutput(
                    claim_id=claim.claim_id,
                    source_claim_ref=claim.source_claim_ref,
                    routing_decision=RoutingDecision.CLINICAL_PATH,
                    confidence=0.0,
                    confidence_fallback=True,
                    clinical_indicators_detected=[],
                    criteria_provisions_matched=["SHADOW_ISOLATION_VIOLATION"],
                    reasoning_trace=f"SHADOW_ISOLATION_VIOLATION: Agent MODE={self.mode.value} but LLM returned routing_mode={output.routing_mode.value}. Safe fallback to CLINICAL_PATH.",
                    routing_mode=self.mode
                )

            # Apply confidence fallback (per spec §6.3)
            if output.confidence < self.confidence_threshold:
                output.routing_decision = RoutingDecision.CLINICAL_PATH
                output.confidence_fallback = True

            # Verify prior authorization requirements (override claim data based on codebook)
            output = self._verify_prior_auth_requirements(claim, output)

            return output

        except json.JSONDecodeError as e:
            # Safe fallback: route to CLINICAL_PATH, alert ops
            print(f"⚠️  OUTPUT_PARSE_FAILED: LLM returned invalid JSON for claim {claim.claim_id}")
            print(f"⚠️  Error: {e}")
            try:
                print(f"⚠️  Response text: {result_text[:500]}...")
            except:
                print(f"⚠️  Response text: (unable to display)")
            print(f"⚠️  OPS ALERT: Model may be producing malformed output")
            print(f"⚠️  Safe fallback: Routing to CLINICAL_PATH")

            return RoutingDecisionOutput(
                claim_id=claim.claim_id,
                source_claim_ref=claim.source_claim_ref,
                routing_decision=RoutingDecision.CLINICAL_PATH,
                confidence=0.0,
                confidence_fallback=True,
                clinical_indicators_detected=[],
                criteria_provisions_matched=["OUTPUT_PARSE_FAILED"],
                reasoning_trace=f"OUTPUT_PARSE_FAILED: {str(e)}. Safe fallback to CLINICAL_PATH.",
                routing_mode=self.mode
            )
        except KeyError as e:
            # Safe fallback: route to CLINICAL_PATH, alert ops
            print(f"⚠️  OUTPUT_PARSE_FAILED: LLM response missing required field for claim {claim.claim_id}")
            print(f"⚠️  Missing field: {e}")
            print(f"⚠️  OPS ALERT: Model may be producing incomplete output")
            print(f"⚠️  Safe fallback: Routing to CLINICAL_PATH")

            return RoutingDecisionOutput(
                claim_id=claim.claim_id,
                source_claim_ref=claim.source_claim_ref,
                routing_decision=RoutingDecision.CLINICAL_PATH,
                confidence=0.0,
                confidence_fallback=True,
                clinical_indicators_detected=[],
                criteria_provisions_matched=["OUTPUT_PARSE_FAILED"],
                reasoning_trace=f"OUTPUT_PARSE_FAILED: Missing required field {str(e)}. Safe fallback to CLINICAL_PATH.",
                routing_mode=self.mode
            )
        except Exception as e:
            # Catch-all safe fallback
            print(f"⚠️  CLASSIFICATION_FAILED: Unexpected error for claim {claim.claim_id}")
            print(f"⚠️  Error: {e}")
            print(f"⚠️  OPS ALERT: Unexpected error in classification")
            print(f"⚠️  Safe fallback: Routing to CLINICAL_PATH")

            return RoutingDecisionOutput(
                claim_id=claim.claim_id,
                source_claim_ref=claim.source_claim_ref,
                routing_decision=RoutingDecision.CLINICAL_PATH,
                confidence=0.0,
                confidence_fallback=True,
                clinical_indicators_detected=[],
                criteria_provisions_matched=["CLASSIFICATION_FAILED"],
                reasoning_trace=f"CLASSIFICATION_FAILED: {str(e)}. Safe fallback to CLINICAL_PATH.",
                routing_mode=self.mode
            )

    def _verify_prior_auth_requirements(
        self,
        claim: NormalizedClaimRecord,
        output: RoutingDecisionOutput
    ) -> RoutingDecisionOutput:
        """
        Verify prior authorization requirements based on codebook provisions.
        Override routing decision if prior auth is required but missing.

        Also warn if prior auth is provided but not required (possible unnecessary admin).
        """
        # Check if any matched provisions require prior auth
        matched_provisions = []
        for provision_id in output.criteria_provisions_matched:
            if provision_id in ["NOVEL_CASE", "SHADOW_ISOLATION_VIOLATION", "API_KEY_MISSING", "OUTPUT_PARSE_FAILED"]:
                continue  # Skip special markers

            # Find provision in codebook
            for provision in self.codebook.provisions:
                if provision.provision_id == provision_id:
                    matched_provisions.append(provision)
                    break

        # Check if any matched provision requires prior auth
        requires_prior_auth = any(p.requires_prior_auth for p in matched_provisions)

        # Helper: validate prior_auth_number format (same as ADR-1)
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

        has_valid_prior_auth = is_valid_prior_auth_number(claim.prior_auth_number)

        # Case 1: Codebook says prior auth required, but claim doesn't have it
        if requires_prior_auth and not has_valid_prior_auth:
            provision_names = ", ".join([p.provision_name for p in matched_provisions if p.requires_prior_auth])
            reasoning = f"PRIOR_AUTH_MISSING: Matched provisions require prior authorization ({provision_names}) but prior_auth_number is missing or invalid. Routing to CLINICAL_PATH for review."

            print(f"⚠️  Prior auth required but missing for claim {claim.claim_id}")
            print(f"⚠️  Matched provisions requiring prior auth: {provision_names}")
            print(f"⚠️  Overriding routing decision to CLINICAL_PATH")

            output.routing_decision = RoutingDecision.CLINICAL_PATH
            output.confidence_fallback = True
            output.reasoning_trace = f"{output.reasoning_trace}\n\n{reasoning}"

        # Case 2: Claim has prior auth, but codebook says not required (warning only)
        elif has_valid_prior_auth and not requires_prior_auth and output.routing_decision == RoutingDecision.FAST_PATH:
            print(f"⚠️  WARNING: Claim {claim.claim_id} has prior_auth_number but matched provisions don't require prior auth")
            print(f"⚠️  This may indicate unnecessary prior auth or misclassification")
            # Don't override routing, just log warning

        return output


def create_agent(
    mode: Optional[str] = None,
    confidence_threshold: Optional[float] = None,
    agent_version: str = "1.0.0"
) -> TriageAgent:
    """
    Factory function to create agent with environment variable fallbacks.

    Args:
        mode: SHADOW or LIVE (defaults to env var ADR4_MODE or "SHADOW")
        confidence_threshold: Threshold for fallback (defaults to env var or 0.70)
        agent_version: Agent version string

    Returns:
        TriageAgent instance configured with LLM-based classification

    Raises:
        ValueError: If OPENAI_API_KEY environment variable not set
    """
    if mode is None:
        mode = os.getenv("ADR4_MODE", "SHADOW")

    if confidence_threshold is None:
        confidence_threshold = float(os.getenv("ADR4_CONFIDENCE_THRESHOLD", "0.70"))

    return TriageAgent(
        mode=mode,
        confidence_threshold=confidence_threshold,
        agent_version=agent_version
    )
