# Capability Specification: Clinical Content Triage Agent
## ADR-4 — Greenfield Health Systems AI Claims Processing Transformation

**Prepared by:** FDE Engagement Lead  
**Date:** 2026-05-21  
**Wave:** Wave 1 (shadow mode) → Wave 2 (live, conditional on [A6] gate)  
**Delegation Archetype:** Human Only → Agent-led + Human Oversight (conditional)  
**Status:** Active — shadow mode design final; live deployment blocked on [A15] criteria definition and [A6] gate

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Agent Purpose Document](#2-agent-purpose-document)
3. [Agent Activity Catalog](#3-agent-activity-catalog)
4. [Autonomy Matrix](#4-autonomy-matrix)
5. [System and Data Inventory](#5-system-and-data-inventory)
6. [Context Engineering Design](#6-context-engineering-design)
7. [Compounding Roadmap](#7-compounding-roadmap)
8. [Integration Contracts](#8-integration-contracts)
9. [Entity Data Models](#9-entity-data-models)
10. [Validation Scenarios](#10-validation-scenarios)
11. [Governance](#11-governance)

---

## 1. Executive Summary

ADR-4 is the dual-path routing engine for the Greenfield claims architecture. It classifies every incoming claim as **Fast Path** (no clinical content, ~65% of volume [A2]) or **Clinical Path** (clinical content requiring physician review, ~35% of volume [A2]). This single decision gates the entire financial case: Fast Path adjudication delivers the CFO's 13 FTE headcount reduction; Clinical Path pre-screening delivers the CMO's physician oversight model. If ADR-4 routes incorrectly, both outcomes break.

The agent currently sits in **Human Only** state. Routing decisions are made today by admin processors using informal heuristics — no formal written criteria exist [A15]. A false negative (clinical claim classified as administrative) routes a patient care decision through the Fast Path without physician review — the CMO's explicit red line. The patient safety cost of a false negative is categorically higher than the operational cost of a false positive (unnecessary physician review), and the agent design enforces this asymmetry structurally.

**Phase 1 (Wave 1, shadow mode):** The agent runs in parallel with the existing process. It classifies every claim, logs its decision with confidence score and clinical indicator citations, but takes no routing action — all claims continue through current processor routing. The shadow pipeline measures the false-negative rate against a ground-truth dataset labeled by Dr. Webb's team [A25]. Gate condition: false-negative rate < 2% [A6] sustained over a 60-day window on ≥2,000 labeled examples.

**Phase 2+ (Wave 2 and later, live routing):** Upon gate clearance, the agent takes over routing. Claims with confidence ≥ threshold [A24] route automatically. Claims below the confidence threshold default to Clinical Path — the conservative fallback that trades false-positive cost for false-negative safety. A physician audit of a random 5% Fast Path sample runs monthly as the ongoing quality gate.

**Key metrics:**
- Phase 1: false-negative rate < 2% over 60-day shadow window; ≥2,000 labeled examples accumulated [A6]
- Phase 2 live: false-negative rate < 2% maintained (monthly audit confirmation); false-positive rate tracked for physician capacity planning [A10]
- Throughput: 1,667 claims/day classified end-to-end [U1]
- Confidence fallback rate: claims below threshold routed conservatively to Clinical Path [A24]
- Audit sample: 5% of Fast Path approvals reviewed monthly by clinical staff

ADR-4 has the highest value score in the portfolio (25/25) and the lowest feasibility score (13/30). The gap between value and feasibility is the central engineering challenge of this project: undefined criteria [A15], unstructured input, patient safety consequences, and an accuracy gate that blocks the entire Wave 2 deployment.

---

## 2. Agent Purpose Document

```
Agent Name:       Clinical Content Triage Agent
Job to be Done:   Classify every normalized claim record as Fast Path (no clinical content)
                  or Clinical Path (clinical content requiring physician review) — with a
                  confidence score and auditable clinical indicator citations for every
                  routing decision.
Business context: Zone 4 (Clinical Triage) — the highest-risk decision point in the claims
                  processing workflow [A15]; classifies all 1,667 claims/day [U1] after
                  coding validation; routes to Zone 5 (Fast Path) or Zone 6 (Clinical
                  Pre-Screening).

Primary objectives:
  1. In shadow mode (Wave 1): classify every claim and accumulate a labeled dataset
     that validates or corrects the 65/35 split assumption [A2] and measures
     false-negative rate toward the <2% Phase 1 gate [A6].
  2. In live mode (Wave 2+): route claims to the correct path with confidence ≥ threshold
     [A24]; default claims below the confidence threshold to Clinical Path.
  3. Produce an auditable reasoning trace for every routing decision — the specific
     clinical indicators detected and the criteria provisions they triggered [A15].

KPIs:
  - False-negative rate: < 2% (clinical claim classified as Fast Path) — Phase 1 gate [A6]
  - False-positive rate: tracked but not gated; acceptable ceiling TBD in Phase 1 calibration
  - Coverage: 100% of post-coding claims classified (no claims skip triage)
  - Confidence fallback rate: % of claims below threshold → routed to Clinical Path [A24]
  - Audit pass rate: ≥98% of audited Fast Path approvals confirmed correctly routed
    by monthly physician audit sample (5% of Fast Path volume)
  - Throughput: 1,667 claims/day processed in batch; target classification latency < 2 min/claim

Failure modes:
  - False negative (CRITICAL): Clinical claim classified as Fast Path.
    Consequence: claim adjudicated without physician review — patient care risk [A6].
    Recovery: monthly audit sample catches systematic false negatives; individual
    claim corrected via Fast Path appeals re-routing. Systemic pattern triggers
    model retraining and Wave 2 suspension pending re-evaluation.
  - False positive (operational): Administrative claim classified as Clinical Path.
    Consequence: unnecessary physician queue time; no patient harm.
    Recovery: false-positive tracking in monthly audit; if rate exceeds physician
    capacity threshold [A10], threshold calibration review.
  - Low-confidence flood: bulk of claims fall below confidence threshold [A24].
    Consequence: Clinical Path volume spike; physician bottleneck [A10].
    Recovery: criteria specification review with Dr. Webb; threshold recalibration.
  - Criteria ambiguity [A15]: edge cases where clinical content is present but
    below the criteria specification threshold.
    Recovery: escalate ambiguous cases to Dr. Webb's team for definitive labeling;
    update criteria codebook; retrain on labeled edge cases.

Delegation archetype:
  WAVE 1 — Human Only (shadow mode; agent classifies but does not route)
  WAVE 2+ — Agent-led + Human Oversight, conditional on [A6] gate clearance:
    - High-confidence classification: Fully Agentic routing decision
    - Below-threshold classification: Conservative fallback to Clinical Path [A24]
    - Ambiguous / novel case: Human escalation with agent reasoning trace

Escalation triggers:
  - Claim classification confidence < threshold [A24] → route to Clinical Path
    (conservative default; no human review required for the routing decision itself)
  - Clinical content detected that falls outside the criteria codebook [A15] →
    flag for Dr. Webb team adjudication; add to criteria review backlog
  - Monthly audit false-negative detection → immediate ops alert; suspend
    autonomous routing pending root cause review
  - Daily false-positive rate exceeds physician capacity ceiling [A10] →
    ops alert for threshold recalibration review
```

---

## 3. Agent Activity Catalog

| Task | Type | Delegation Level | Data Required | Tool Required | Risk Level |
|------|------|:----------------:|---------------|---------------|:----------:|
| Ingest normalized claim record from ADR-1 | Retrieval | Fully agentic | CMS claim record (post-coding validation) | CMS read API | Low |
| Extract clinical indicators from claim data (ICD-10 codes, CPT codes, procedure type flags, prior auth markers, free-text notes) | Reasoning | Fully agentic | Normalized claim record | Clinical indicator extraction module | High |
| Match extracted indicators against clinical criteria codebook [A15] | Reasoning | Fully agentic (criteria codebook in context) | Extracted indicators + codebook | Criteria lookup + LLM reasoning | High |
| Score classification confidence for Fast Path vs. Clinical Path | Reasoning | Fully agentic | Indicator match results | Confidence scoring model | High |
| Apply conservative routing fallback when confidence < threshold [A24] | Decision | Fully agentic | Confidence score vs. threshold | Threshold rules engine | High |
| Generate routing decision with clinical indicator citations | Generation | Fully agentic | Classification result + matched criteria | Structured output module | High |
| Write routing decision to CMS claim record | Action | **Shadow mode: logging only** / Live: CMS write | Routing decision, confidence, citations | CMS write API | High |
| Log shadow mode classification for comparison against processor decision | Action | Fully agentic (shadow mode only) | Agent routing decision + claim ID | Shadow evaluation log store | Medium |
| Flag criteria edge cases for Dr. Webb adjudication | Generation | Fully agentic | Classification result, confidence, indicator detail | Exception queue API | High |
| Provide reasoning trace for monthly audit sample | Generation | Fully agentic | Stored routing decision + indicator citations | Audit log read API | Medium |

**Task type notes:**

- **MT-4.1 (Clinical content identification):** The highest-risk task in the workflow per the Cognitive Load Map. Input is unstructured (clinical indicators embedded in codes and documentation); criteria are currently informal [A15]. The LLM does the cognitive work of matching claim content against the criteria codebook — this is the only task in the pipeline where LLM reasoning is the primary mechanism, not a wrapper around a rules engine.
- **MT-4.2 (Routing decision):** After MT-4.1 produces a confidence-scored classification, routing is rule-governed: confidence ≥ threshold → route per classification; confidence < threshold → Clinical Path regardless [A24]. This task is deterministic given the MT-4.1 output.
- **Shadow mode behavior (Wave 1):** The CMS write action logs the routing decision as a metadata field (not as an operative routing decision) — the claim continues through current processor routing unchanged. Shadow mode cannot affect live claim flow.

---

## 4. Autonomy Matrix

```
[SHADOW MODE — Wave 1 only]
  AGENT CLASSIFIES, HUMAN ROUTES:
    - Agent classifies every claim and logs decision + confidence + citations
    - Current processor routing continues unchanged for all claims
    - Shadow log accumulates labeled comparison data for [A6] gate measurement
    - No agent action modifies CMS claim routing during Wave 1

[LIVE MODE — Wave 2+, after [A6] gate passes]

AGENT DECIDES ALONE (no HITL required):
  - Clinical indicator extraction from normalized claim record
  - Criteria codebook matching
  - Confidence scoring
  - High-confidence Fast Path classification → CMS routing write
  - High-confidence Clinical Path classification → CMS routing write
  - Conservative fallback: below-threshold claim → Clinical Path (automatic;
    no human review of the routing decision required)

AGENT ACTS, HUMAN NOTIFIED AFTER:
  - All routing decisions (daily routing summary to ops; not per-claim)
  - Below-threshold fallback events (logged; not individually reviewed)

AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:
  - No approvals required per routing decision in live mode
    (the [A6] gate and ongoing audit are the approval mechanism for the
    class of decisions, not individual claim approval)

HUMAN TAKES OVER (agent supports):
  - Monthly audit sample: physician reviews 5% Fast Path routing decisions
    with full agent reasoning trace → corrects errors, validates accuracy
  - Criteria edge case: claim contains clinical content not covered by
    codebook → agent flags; Dr. Webb team adjudicates routing and
    updates criteria codebook
  - Monthly audit detects false-negative rate above 2% → autonomous routing
    suspended; all claims revert to processor routing until root cause resolved
  - Novel claim type with no precedent in training data → agent flags;
    processor routes manually; case added to criteria review backlog
```

---

## 5. System and Data Inventory

| System | Data Needed | Access Type | Availability | Gap / Risk |
|--------|-------------|:-----------:|--------------|------------|
| CMS (Claims Management System) | Normalized claim record (post-coding); routing decision write; audit metadata | Read / Write | Assumed API available [A12] | Shared dependency with ADR-1; integration built in Wave 1 by ADR-1 — ADR-4 reuses |
| Clinical criteria codebook [A15] | Formal specification of clinical content triggers: procedure types, diagnosis categories, prior auth flags, documentation markers requiring physician review | Read (procedural) | **Does not exist — must be built with Dr. Webb** | **Wave 1 blocker #1:** criteria must be documented before shadow mode prompt can be written; Week 1 deliverable |
| Shadow evaluation log store | Agent routing decisions (shadow mode): claim ID, classification, confidence, clinical indicator citations, timestamp | Write (shadow) / Read (evaluation) | Must be built | New infrastructure; stores parallel-run comparison data for [A6] false-negative rate calculation |
| Ground truth adjudication queue [A25] | Agent-vs-processor disagreements submitted to Dr. Webb's team for definitive labeling | Read / Write | Must be built | Lightweight queue (e.g., structured review portal); Dr. Webb team capacity is a gating constraint |
| Audit log store | All live routing decisions: claim ID, path assigned, confidence score, clinical indicators cited | Write | Shared with ADR-1 (same infrastructure) | No gap — reuses ADR-1 audit log infrastructure |
| Exception / escalation queue | Novel criteria edge cases flagged for Dr. Webb adjudication and codebook update | Read / Write | Assumed existing ops queue | Routing to correct clinical reviewer requires ops process definition |

**Shared with ADR-1 (Claim Intake Agent):** CMS read API, normalized claim record schema, audit log store. ADR-4 is a consumer of ADR-1 output — the normalized claim record is the triage agent's primary input. Schema consistency between these two agents is mandatory and must be designed jointly in Wave 1.

**Shared with ADR-6 (Clinical Pre-Screening Agent):** Clinical criteria codebook [A15]. Both agents operate on the definition of "clinical content" — ADR-4 uses it to detect the presence of clinical content; ADR-6 uses it to identify which content to extract. A single authoritative codebook maintained by Dr. Webb's team serves both agents.

---

## 6. Context Engineering Design

### Memory Architecture

| Memory Type | Content | Storage | Lifecycle |
|-------------|---------|:-------:|-----------|
| **In-context** (short-term) | Current claim's normalized fields: ICD-10 codes, CPT codes, procedure type, prior auth flags, clinical documentation excerpts; criteria codebook (procedural, small enough to include directly) | Prompt window | Per claim — stateless; no cross-claim context carried |
| **Procedural** (static) | Clinical criteria codebook [A15]: the complete formal specification of what constitutes "clinical content"; confidence threshold value [A24]; routing decision rules; shadow vs. live mode behavior; escalation conditions; output JSON schema | System prompt | Version-controlled; updated only when Dr. Webb approves a codebook revision |
| **Semantic** (long-term) | Clinical policy references; procedure-diagnosis pattern context; coverage policy provisions relevant to clinical content categories | Vector store (RAG) | Updated on policy change — queried when criteria codebook match is uncertain |
| **Episodic** (medium-term) | Per-claim routing decisions and confidence scores (stored in CMS + audit log); shadow mode false-negative history for calibration | CMS + audit log | Per claim; accessible for audit, retraining, and monthly review |

**Design note on criteria codebook in context:** The criteria codebook is the agent's decision rulebook. At the criteria complexity anticipated (~50–150 clinical content trigger categories), it is small enough to include in the system prompt directly — avoiding RAG latency on every claim. If the codebook grows beyond ~1,000 tokens, move it to a pre-prompt retrieval step with semantic indexing. The codebook must be treated as a versioned artifact: Dr. Webb must approve each revision before it is deployed to the system prompt.

### Retrieval Strategy

- **Clinical criteria codebook:** Loaded procedurally in the system prompt. Not retrieved per claim. Versioned separately from agent code — codebook changes do not require code deployments.
- **Clinical policy RAG:** Triggered when the claim contains clinical indicators that partially match criteria codebook entries — the agent queries the policy store for additional context on whether the procedure qualifies as clinically complex under Greenfield's coverage policies. Target: top-3 policy chunks by cosine similarity.
- **Audit trace retrieval:** Monthly audit physician reviews stored routing decisions via audit log read API — not part of per-claim inference loop.
- **Retrieval quality evaluation:** False-negative rate is the primary quality signal. If policy RAG queries are correlating with false-positive errors (over-routing administrative claims), chunk granularity should be refined.
- **Cost management:** RAG calls add ~$0.02–0.04/claim on the subset requiring policy context lookup (estimated 15–25% of claims). Total API cost remains within [A4] estimate.

### Prompt / Context Engineering Principles

1. **Role, mode, and purpose first:** System prompt opens with explicit mode declaration: `MODE: SHADOW` (Wave 1) or `MODE: LIVE` (Wave 2+). Mode controls whether CMS write is operative or logging-only. This prevents shadow mode agent from accidentally routing claims.

2. **Explicit scope and asymmetry:** State the failure cost asymmetry directly: "A false negative — classifying a clinical claim as Fast Path — routes a claim affecting patient care without physician review. This is the most serious failure mode. When in doubt, route to Clinical Path."

3. **Criteria codebook as primary decision reference:** "Use the attached Clinical Content Criteria Codebook as your primary classification reference. For each claim, enumerate the specific criteria provisions matched and cite them in your output."

4. **Confidence threshold instruction [A24]:** "If your classification confidence is below [THRESHOLD], output `path: CLINICAL` regardless of the marginal classification. State `confidence_fallback: true` in the output."

5. **Chain-of-thought required:** "Before outputting a routing decision, reason step-by-step: (1) list all clinical indicators present in the claim, (2) match each indicator against the codebook, (3) state whether any matched indicator triggers Clinical Path routing, (4) compute overall confidence, (5) apply fallback rule if below threshold, (6) output final routing decision." Chain-of-thought is required here because the cost of an incorrect routing decision is high and the reasoning must be auditable.

6. **Structured output required:** JSON schema enforced:
   ```json
   {
     "claim_id": "string",
     "routing_decision": "FAST_PATH | CLINICAL_PATH",
     "confidence": 0.0–1.0,
     "confidence_fallback": true | false,
     "clinical_indicators_detected": ["list of indicator strings"],
     "criteria_provisions_matched": ["list of codebook provision IDs"],
     "reasoning_trace": "string (chain-of-thought output)",
     "mode": "SHADOW | LIVE"
   }
   ```

7. **Guardrail for novel cases:** "If the claim contains clinical documentation or procedure types not covered by any codebook provision, do not infer a classification. Set `routing_decision: CLINICAL_PATH`, `confidence: 0.0`, and `criteria_provisions_matched: ['NOVEL_CASE']`. Flag for Dr. Webb adjudication."

8. **Few-shot examples:** Include 5–8 labeled examples spanning: (a) clear administrative claims (correct Fast Path), (b) clear clinical claims (correct Clinical Path), (c) boundary cases where a clinical indicator is present but minor (correct Clinical Path under conservative design), (d) a novel case triggering the guardrail. Examples are drawn from the Pre-Phase 1 historical analysis sample [A2].

### System Prompt Template

> **Versioning:** The prompt is a versioned deployment artifact stored in the config manager under key `ADR4_SYSTEM_PROMPT_V{N}`. The criteria codebook (`{{CRITERIA_CODEBOOK}}`) and confidence threshold (`0.70`) are substituted at deployment time, not at inference time. Any codebook revision approved by Dr. Webb requires a new prompt version and a redeployment — codebook content must never be modified at runtime.

> **Mode switching:** `{{MODE}}` is set to `SHADOW` for Wave 1 deployments and `LIVE` for Wave 2+ deployments. Switching from SHADOW to LIVE requires an explicit deployment step with a separate config change — it must not be achievable by modifying the prompt at runtime (see §11.3 Shadow Mode Isolation Guarantee).

> **Input format:** Pass only the following fields from NormalizedClaimRecord to minimize token cost: `claim_id`, `source_claim_ref`, `intake_channel`, `extraction_status`, `claim_type`, `icd10_codes`, `cpt_codes`, `prior_auth_required`, `prior_auth_number`. Do not pass SLA fields, provider identity fields, payer fields, or timestamps — ADR-4 does not use them for classification. The agent does not modify any intake fields.

> **Precondition — extraction_status gate:** ADR-4 expects claims where `extraction_status = AUTO_COMPLETE`. If a claim enters triage with `extraction_status != AUTO_COMPLETE` (queue filter failure), the agent applies safe fallback: routes to CLINICAL_PATH with `confidence = 0.0`, `criteria_provisions_matched = ["PRECONDITION_FAILED"]`, and alerts ops. This ensures no claims are dropped and patient safety is maintained while ops investigates the queue filter issue. The CMS triage queue must filter on `extraction_status = AUTO_COMPLETE AND routing_decision = PENDING_TRIAGE`. Claims in `HUMAN_REQUIRED` state remain in the human review queue; they enter the triage queue only after human review sets their clinical fields and transitions `extraction_status` to a complete state.

```
MODE: {{MODE}}
SYSTEM PROMPT — ADR-4 Clinical Content Triage Agent
Prompt version: {{ADR4_PROMPT_VERSION}}
Criteria codebook version: {{CRITERIA_CODEBOOK_VERSION}}
Confidence threshold: 0.70

## Role
You are the Clinical Content Triage Agent for Greenfield Health Systems. You classify every
normalized claim record as FAST_PATH or CLINICAL_PATH.

  FAST_PATH:     No clinical content. Claim can be adjudicated without physician review.
  CLINICAL_PATH: Clinical content is present. Claim requires physician review.

## Operating mode: {{MODE}}
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

{{CRITERIA_CODEBOOK}}

Each provision includes:
  provision_id          — cite this in criteria_provisions_matched
  clinical_category     — type of clinical content
  trigger_icd10_patterns — ICD-10 code prefixes or exact codes that trigger this provision
  trigger_cpt_patterns  — CPT code prefixes or exact codes that trigger this provision
  trigger_prior_auth_required — if true, prior_auth_required = true alone triggers this provision

## Classification procedure — follow all 6 steps before producing output
Step 1: List every clinical indicator present in the claim.
        Include: all ICD-10 codes, all CPT codes, prior_auth_required value. (Free-text note
        scanning is out of scope — NormalizedClaimRecord contains no free-text field.)
Step 2: For each indicator, check whether it matches any provision's trigger conditions.
        An ICD-10 code matches if it starts with any string in trigger_icd10_patterns.
        A CPT code matches if it starts with any string in trigger_cpt_patterns.
Step 3: If any indicator matches any provision → routing_decision = CLINICAL_PATH.
        If no indicators match any provision → routing_decision = FAST_PATH.
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
        
        Note: Policy RAG is not active in the current build. Classification is codebook-only.
Step 5: Apply fallback rule:
        If confidence < 0.70:
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
The application layer will flag this claim for Dr. Webb adjudication.
Do not attempt to infer a classification when no provision applies.

## Output format
Respond with a single JSON object only. No prose before or after the JSON.

{
  "claim_id":                     "string — copy from input",
  "source_claim_ref":             "string — copy from input",
  "routing_decision":             "FAST_PATH | CLINICAL_PATH",
  "confidence":                   0.00,
  "confidence_fallback":          true | false,
  "clinical_indicators_detected": ["string — each indicator found in the claim"],
  "criteria_provisions_matched":  ["string — provision IDs from codebook, or ['NOVEL_CASE']"],
  "reasoning_trace":              "string — your step-by-step reasoning, Steps 1–5",
  "routing_mode":                 "SHADOW | LIVE"
}

## Few-shot examples

--- EXAMPLE 1: Routine office visit — no clinical indicators → FAST_PATH ---
User message:
{
  "claim_id":            "a3f1e2d4-0c8b-4e6a-9f7d-1b2c3d4e5f60",
  "source_claim_ref":    "PDF-2026-0441",
  "intake_channel":      "CMS1500_PDF",
  "extraction_status":   "AUTO_COMPLETE",
  "member_id":           "M-4421908",
  "icd10_codes":         ["Z00.00"],
  "cpt_codes":           ["99213"],
  "prior_auth_required": false,
  "prior_auth_number":   null,
  "payer_id":            "BX-0042",
  "place_of_service":    "11",
  "billed_amount":       185.00
}
Assistant:
{
  "claim_id":                    "a3f1e2d4-0c8b-4e6a-9f7d-1b2c3d4e5f60",
  "source_claim_ref":            "PDF-2026-0441",
  "routing_decision":            "FAST_PATH",
  "confidence":                  0.96,
  "criteria_provisions_matched": [],
  "reasoning_trace": "Step 1 — ICD-10 scan: Z00.00 (routine adult health examination) has no match in any CLINICAL_PATH provision trigger list. Step 2 — CPT scan: 99213 (office visit, established patient, low complexity) has no match in any provision. Step 3 — Prior auth check: prior_auth_required is false and prior_auth_number is null; no prior auth provision triggered. Step 4 — Novel code check: both codes appear in standard codebook with no NOVEL_CASE flag. Step 5 — Codebook exhausted with zero provisions matched. Step 6 — Decision: no clinical indicators present; routing to FAST_PATH with high confidence.",
  "routing_mode":                "SHADOW"
}

--- EXAMPLE 2: Oncology chemotherapy administration — multiple clinical provisions → CLINICAL_PATH ---
User message:
{
  "claim_id":            "b7c2f3e5-1d9a-4f7b-8e0c-2c3d4e5f6a71",
  "source_claim_ref":    "EDI-20260412-00417",
  "intake_channel":      "EDI_837P",
  "extraction_status":   "AUTO_COMPLETE",
  "member_id":           "M-9938812",
  "icd10_codes":         ["C50.911", "Z79.899"],
  "cpt_codes":           ["96413", "96415"],
  "prior_auth_required": true,
  "prior_auth_number":   "PA-20260410-4421",
  "payer_id":            "UH-0017",
  "place_of_service":    "22",
  "billed_amount":       4200.00
}
Assistant:
{
  "claim_id":                    "b7c2f3e5-1d9a-4f7b-8e0c-2c3d4e5f6a71",
  "source_claim_ref":            "EDI-20260412-00417",
  "routing_decision":            "CLINICAL_PATH",
  "confidence":                  0.98,
  "criteria_provisions_matched": ["CC-003", "CC-006", "CC-001"],
  "reasoning_trace": "Step 1 — ICD-10 scan: C50.911 (malignant neoplasm, upper-outer quadrant, right female breast) matches CC-003 (oncology diagnosis) and CC-006 (complex systemic condition); Z79.899 (long-term drug therapy) matches CC-006. Step 2 — CPT scan: 96413 (chemotherapy administration, intravenous infusion) and 96415 (each additional hour) match CC-003 (oncology treatment). Step 3 — Prior auth check: prior_auth_required is true; CC-001 (prior authorization required) triggered regardless of other provisions. Step 4 — Novel code check: all codes are present in standard codebook. Step 5 — Provisions matched: CC-001, CC-003, CC-006. Step 6 — Decision: multiple clinical provisions matched; routing to CLINICAL_PATH with high confidence.",
  "routing_mode":                "SHADOW"
}

--- EXAMPLE 3: Diagnostic imaging with borderline confidence — conservative design → CLINICAL_PATH ---
User message:
{
  "claim_id":            "c9d4a5b6-2e0f-4a8c-7b1d-3d4e5f6a7b82",
  "source_claim_ref":    "PDF-2026-0589",
  "intake_channel":      "CMS1500_PDF",
  "extraction_status":   "AUTO_COMPLETE",
  "member_id":           "M-2194567",
  "icd10_codes":         ["R05.9"],
  "cpt_codes":           ["71046"],
  "prior_auth_required": false,
  "prior_auth_number":   null,
  "payer_id":            "AE-0031",
  "place_of_service":    "22",
  "billed_amount":       620.00
}
Assistant:
{
  "claim_id":                    "c9d4a5b6-2e0f-4a8c-7b1d-3d4e5f6a7b82",
  "source_claim_ref":            "PDF-2026-0589",
  "routing_decision":            "CLINICAL_PATH",
  "confidence":                  0.81,
  "criteria_provisions_matched": ["CC-007"],
  "reasoning_trace": "Step 1 — ICD-10 scan: R05.9 (cough, unspecified) does not independently match any high-specificity provision trigger. Step 2 — CPT scan: 71046 (chest X-ray, 2 views) matches CC-007 (diagnostic imaging requiring medical necessity review). Step 3 — Prior auth check: prior_auth_required is false; CC-001 not triggered. Step 4 — Novel code check: 71046 is present in codebook. Step 5 — Provisions matched: CC-007 via imaging CPT. Step 6 — Decision: one clinical provision matched; confidence is moderate (0.81) because R05.9 is a low-specificity symptom code that could accompany a range of conditions. Under conservative design, any provision match routes to CLINICAL_PATH regardless of confidence level.",
  "routing_mode":                "SHADOW"
}

--- EXAMPLE 4: Prior authorization required with no other clinical indicators → CLINICAL_PATH ---
User message:
{
  "claim_id":            "d1e5b6c7-3f1a-4b9d-8c2e-4e5f6a7b8c93",
  "source_claim_ref":    "PDF-2026-0631",
  "intake_channel":      "PORTAL_JSON",
  "extraction_status":   "AUTO_COMPLETE",
  "member_id":           "M-6672341",
  "icd10_codes":         ["M54.51"],
  "cpt_codes":           ["99214"],
  "prior_auth_required": true,
  "prior_auth_number":   null,
  "payer_id":            "BX-0042",
  "place_of_service":    "11",
  "billed_amount":       275.00
}
Assistant:
{
  "claim_id":                    "d1e5b6c7-3f1a-4b9d-8c2e-4e5f6a7b8c93",
  "source_claim_ref":            "PDF-2026-0631",
  "routing_decision":            "CLINICAL_PATH",
  "confidence":                  0.88,
  "criteria_provisions_matched": ["CC-001"],
  "reasoning_trace": "Step 1 — ICD-10 scan: M54.51 (vertebrogenic low back pain) has no match in diagnostic imaging, oncology, specialist authorization, or complex systemic condition provisions. Step 2 — CPT scan: 99214 (office visit, established patient, moderate complexity) has no match in specialty procedure or imaging provisions. Step 3 — Prior auth check: prior_auth_required is true and prior_auth_number is null (authorization number not yet obtained); CC-001 (prior authorization required) triggered. Step 4 — Novel code check: both codes present in codebook. Step 5 — Provisions matched: CC-001 only. Step 6 — Decision: prior auth required without a confirmed authorization number constitutes a clinical review trigger per CC-001; routing to CLINICAL_PATH.",
  "routing_mode":                "SHADOW"
}

--- EXAMPLE 5: Experimental CPT code not in codebook → NOVEL_CASE → CLINICAL_PATH ---
User message:
{
  "claim_id":            "e2f6c7d8-4a2b-4c0e-9d3f-5f6a7b8c9d04",
  "source_claim_ref":    "EDI-20260418-00892",
  "intake_channel":      "EDI_837I",
  "extraction_status":   "AUTO_COMPLETE",
  "member_id":           "M-8814459",
  "icd10_codes":         ["M79.3"],
  "cpt_codes":           ["0789T"],
  "prior_auth_required": false,
  "prior_auth_number":   null,
  "payer_id":            "UH-0017",
  "place_of_service":    "11",
  "billed_amount":       850.00
}
Assistant:
{
  "claim_id":                    "e2f6c7d8-4a2b-4c0e-9d3f-5f6a7b8c9d04",
  "routing_decision":            "CLINICAL_PATH",
  "confidence":                  0.0,
  "criteria_provisions_matched": ["NOVEL_CASE"],
  "reasoning_trace": "Step 1 — ICD-10 scan: M79.3 (panniculitis, unspecified) has no match in any provision trigger list. Step 2 — CPT scan: 0789T is not present in the criteria codebook. Step 3 — Prior auth check: prior_auth_required is false; CC-001 not triggered. Step 4 — Novel code check: 0789T is a Category III CPT code (emerging technology) not included in any provision's trigger_cpt_patterns. Novel case rule applies. Step 5 — Novel case rule: when a CPT code is not present in the codebook, the system cannot assess clinical significance. Confidence is set to 0.0 and NOVEL_CASE is flagged. Step 6 — Decision: routing to CLINICAL_PATH per novel case rule; adjudication queue entry will be created for Dr. Webb review to determine whether 0789T warrants a new codebook provision.",
  "routing_mode":                "SHADOW"
}
```

---

## 6.4 Error Handling and Safe Fallback Pattern

**Design principle: Never drop a claim.** All error conditions route to CLINICAL_PATH where physicians can review the claim normally while ops investigates the agent issue.

### Safe Fallback Behavior

When the agent encounters any error condition during classification, it applies a consistent safe fallback pattern:

1. Returns `RoutingDecisionOutput` with `routing_decision = CLINICAL_PATH`
2. Sets `confidence = 0.0` and `confidence_fallback = true`
3. Sets `criteria_provisions_matched = [error_type]` to identify the issue
4. Provides `reasoning_trace` explaining the error
5. Emits ops alert (console log/monitoring event)
6. Preserves claim for physician review

This pattern ensures the system degrades gracefully: claims continue to be reviewed by physicians (patient safety maintained) while ops addresses the agent issue (operational recovery path clear).

### Error Types

**PRECONDITION_FAILED** — `extraction_status != AUTO_COMPLETE`

**Trigger:** A claim enters the triage queue with `extraction_status = HUMAN_REQUIRED` or another non-complete status (queue filter bypass).

**Behavior:**
- Claim routes to CLINICAL_PATH with `confidence = 0.0`
- `criteria_provisions_matched = ["PRECONDITION_FAILED"]`
- `reasoning_trace` explains: "extraction_status=[value], expected AUTO_COMPLETE"
- Ops alert: Queue filter may be broken — HUMAN_REQUIRED claim entered triage
- Shadow log entry written with PRECONDITION_FAILED status (Wave 1)

**Recovery:** Ops investigates intake queue filter logic. Claim proceeds to physician review with no data loss.

**Patient safety:** Physician reviews claim normally; no impact on patient care.

---

**SHADOW_ISOLATION_VIOLATION** — `routing_mode` mismatch

**Trigger:** LLM outputs `routing_mode = LIVE` when agent deployment MODE is SHADOW.

**Behavior:**
- Claim routes to CLINICAL_PATH with `confidence = 0.0`
- `criteria_provisions_matched = ["SHADOW_ISOLATION_VIOLATION"]`
- `reasoning_trace` explains: "Agent MODE=SHADOW but LLM returned routing_mode=LIVE"
- Critical ops alert: Shadow mode isolation breach detected
- Shadow log entry written with violation status (Wave 1)
- No CMS routing write occurs (shadow mode preserved)

**Recovery:** Ops investigates model behavior and deployment config. This is a critical security issue — shadow mode isolation must never be breached, as it would corrupt the comparison dataset needed for [A6] gate validation.

**Patient safety:** Claim proceeds to physician review; comparison dataset integrity protected.

---

**OUTPUT_PARSE_FAILED** — Malformed LLM output

**Trigger:** LLM response cannot be parsed as valid JSON, or JSON is missing required fields (`JSONDecodeError`, `KeyError`).

**Behavior:**
- Claim routes to CLINICAL_PATH with `confidence = 0.0`
- `criteria_provisions_matched = ["OUTPUT_PARSE_FAILED"]`
- `reasoning_trace` includes parse error details
- Ops alert: Model may be producing malformed output
- Shadow log entry written with parse failure status (Wave 1)

**Recovery:** Ops investigates model output quality. If rate exceeds 1% over 15 minutes, escalate to model vendor or trigger prompt review.

**Patient safety:** Claim proceeds to physician review vs. silent failure; no claims dropped due to parse errors.

---

**API_KEY_MISSING** — ANTHROPIC_API_KEY not set

**Trigger:** Agent initialization or LLM call attempted without `ANTHROPIC_API_KEY` environment variable set.

**Behavior:**
- Claim routes to CLINICAL_PATH with `confidence = 0.0`
- `criteria_provisions_matched = ["API_KEY_MISSING"]`
- `reasoning_trace` explains: "ANTHROPIC_API_KEY environment variable not set"
- Ops alert: Cannot call LLM without API key
- Shadow log entry written with API key missing status (Wave 1)

**Recovery:** Ops checks deployment environment configuration. This is a deployment/configuration error.

**Patient safety:** Claim proceeds to physician review; no claims dropped due to misconfiguration.

---

**CLASSIFICATION_FAILED** — Unexpected exception

**Trigger:** Any unanticipated error during classification (catch-all for unhandled edge cases).

**Behavior:**
- Claim routes to CLINICAL_PATH with `confidence = 0.0`
- `criteria_provisions_matched = ["CLASSIFICATION_FAILED"]`
- `reasoning_trace` includes exception details
- Ops alert: Unexpected error in classification
- Shadow log entry written with failure status (Wave 1)

**Recovery:** Ops investigates root cause. Exception details logged for debugging.

**Patient safety:** Ensures no claim processing failures result in dropped claims; all claims proceed to physician review.

---

### Rationale

This error handling pattern is superior to raising exceptions or blocking operations because:

1. **No dropped claims:** All claims proceed to review (by physician if agent fails)
2. **No silent failures:** Ops has full visibility via alerts and reasoning traces
3. **No blocking failures:** System continues operating; claims queue does not back up
4. **Clear escalation path:** Physician reviews claim (patient safety); ops investigates issue (operational recovery)
5. **Traceable root cause:** `reasoning_trace` + `criteria_provisions_matched` provide debugging context

The pattern follows the core safety rule in Section 6.3: **"WHEN IN DOUBT: route to CLINICAL_PATH."** All error conditions are cases of doubt — the agent cannot confidently classify, so it routes conservatively to physician review.

---

## 7. Compounding Roadmap

ADR-4 builds two high-value assets in Wave 1 that compound into Wave 2 and beyond: the clinical classification model and the clinical criteria codebook.

### Wave Sequencing

**Wave 1 — ADR-4 shadow mode (Months 1–3):**
- Clinical criteria codebook: formal specification co-developed with Dr. Webb — primary input to the system prompt and shared with ADR-6
- Clinical classification model: the LLM-based indicator extraction and criteria matching pipeline
- Shadow evaluation pipeline: compares agent classifications against processor routing; accumulates labeled ground-truth [A25]; measures false-negative rate toward [A6] gate
- Platform asset: labeled ground-truth dataset from shadow mode feeds ADR-6 development (same clinical content boundary)

**Wave 2 — ADR-4 goes live; ADR-6 reuses ADR-4 assets (Months 4–6):**
- ADR-4 activates live routing once [A6] gate is cleared
- ADR-6 (Clinical Pre-Screening): ingests ADR-4's Clinical Path routing decision from CMS; reuses the clinical criteria codebook to identify which content to extract for the physician summary — the same criteria that define "clinical content present" (ADR-4) define "clinical content to extract" (ADR-6)
- ADR-5 (Fast Path Adjudication): ingests ADR-4's Fast Path routing decision from CMS; no direct reuse of classification model

**Wave 3 — ongoing monitoring:**
- Shadow evaluation pipeline transitions to production monitoring: periodic shadow re-runs on representative samples validate that live routing accuracy is stable as claim mix evolves
- Criteria codebook versioning: governed cadence for updates, driven by novel case accumulation and Dr. Webb review

### Integration Reuse Matrix

This matrix is consistent with `specs/06a-capability-spec-intake.md`.

| Integration / Asset | ADR-1 (Intake) | ADR-4 (Triage) | ADR-2 (Elig.) | ADR-3 (Coding) | ADR-5 (Fast Path) | ADR-6 (Pre-Screen) | ADR-9 (Denial) | ADR-8 (Payment) |
|--------------------|:--------------:|:--------------:|:-------------:|:--------------:|:-----------------:|:-----------------:|:--------------:|:---------------:|
| CMS read/write API [A12] | ✓ Build | **✓ Reuse** | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| Normalized claim record schema | ✓ Build | **✓ Reuse** | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| EDI 837 parser | ✓ Build | — | — | — | — | — | — | — |
| IDP extraction pipeline | ✓ Build | — | — | — | — | ✓ Reuse | — | — |
| SLA-aware queue module [A17] | ✓ Build | **✓ Reuse** | — | — | ✓ Reuse | ✓ Reuse | — | — |
| Audit log store | ✓ Build | **✓ Reuse** | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| Clinical classification model | — | **✓ Build** | — | — | — | ✓ Reuse | — | — |
| Clinical criteria codebook [A15] | — | **✓ Build** | — | — | — | ✓ Reuse | — | — |
| Shadow evaluation pipeline | — | **✓ Build** | — | — | — | — | — | — |
| Clinical policy vector store | — | **✓ Build** | — | — | — | ✓ Reuse | ✓ Reuse | — |

**ADR-4 compounds most directly into ADR-6.** The clinical criteria codebook and classification model built for triage define what clinical content exists (ADR-4) and what clinical content to extract (ADR-6). Building them for a single purpose (routing) and reusing them for a second purpose (pre-screening) is the primary compounding mechanism in the Wave 2 architecture.

### Prerequisite Chain

The ADR-4 build sequence has strict ordering. Skipping any step invalidates the gate:

```
Step 1  Define clinical content criteria with Dr. Webb [A15] — Week 1
        ↓
Step 2  Build criteria codebook and system prompt
        ↓
Step 3  Build ADR-1 intake pipeline → normalized claim records available
        ↓
Step 4  Wire ADR-4 shadow mode into CMS claim stream
        Filter: extraction_status = AUTO_COMPLETE AND routing_decision = PENDING_TRIAGE
        HUMAN_REQUIRED claims do not enter the triage queue until human review completes
        ↓
Step 5  Run shadow mode for 60-day window; accumulate ≥2,000 labeled examples
        with Dr. Webb adjudication of agent-vs-processor disagreements [A25]
        ↓
Step 6  Measure false-negative rate → Pass [A6] gate (<2%)
        ↓
Step 7  Activate live routing in Wave 2
        ↓
Step 8  Begin Wave 2 ADR development (ADR-3 → ADR-2 → ADR-5, ADR-6)
```

Any step that cannot be completed — criteria definition refused, CMS API unavailable, false-negative gate not cleared — blocks all subsequent steps. The [A15] criteria definition and [A12] CMS API are the two earliest blockers; both must be resolved in Week 1 before development begins.

---

---

## 8. Integration Contracts

> **Shared contracts:** The CMS Read/Write API (§8.1 in `specs/06a-capability-spec-intake.md`) is the primary integration for both ADR-1 and ADR-4. ADR-4 reuses the full CMS contract defined in 06a §8.1 without modification. This section documents only the ADR-4-specific CMS write (routing fields) and the three new integrations ADR-4 must build: the shadow evaluation log store, ground-truth adjudication queue, and clinical policy vector store.

### 8.1 CMS API — ADR-4 Routing Write

ADR-4 uses the same CMS base URL, authentication, retry logic, and error handling as ADR-1 (see `specs/06a-capability-spec-intake.md` §8.1). The only difference is the write payload: ADR-4 issues a `PUT /v1/claims/{claim_id}` to write routing fields onto an existing record.

**PUT /v1/claims/{claim_id} — ADR-4 Routing Write Request:**
```json
{
  "routing_decision":              "FAST_PATH | CLINICAL_PATH",
  "routing_confidence":            "float 0.0–1.0",
  "routing_confidence_fallback":   "boolean",
  "clinical_indicators_detected":  ["array of indicator strings"],
  "criteria_provisions_matched":   ["array of codebook provision IDs — or ['NOVEL_CASE'] if no match"],
  "routing_reasoning_trace":       "string — chain-of-thought output",
  "routing_agent_version":         "semver string",
  "routing_decided_at":            "ISO 8601 UTC",
  "routing_mode":                  "SHADOW | LIVE"
}
```

**Shadow mode constraint:** When `routing_mode = SHADOW`, the PUT payload must include `routing_mode: SHADOW`. The CMS system must accept this write as a metadata annotation — it must not change the claim's processing queue or `status` field. If the CMS system cannot distinguish shadow writes from operative writes, the shadow log store (§8.2) must be used exclusively and the CMS PUT must be omitted in Wave 1. This behavior is determined by the Week 1 IT discovery [A12].

**Idempotency:** ADR-4 must not write a routing decision to a claim already in `FAST_PATH` or `CLINICAL_PATH` status. Before issuing a PUT, the agent must verify `routing_decision = PENDING_TRIAGE` on the current record. If status is already set, log a `ROUTING_ALREADY_DECIDED` event and skip the write.

**Responses:** Same error handling as 04a §8.1 CMS contract. Additional case:
```
HTTP 409 Conflict (routing already written):
  { "error": "ROUTING_CONFLICT", "existing_routing_decision": "FAST_PATH | CLINICAL_PATH", "decided_at": "ISO 8601 UTC" }
  → Agent action: do NOT overwrite. Log ROUTING_ALREADY_DECIDED event. Skip write.
```

---

### 8.2 Shadow Evaluation Log Store

> **Build deliverable:** Must be built in Wave 1. This store is the data substrate for the [A6] false-negative gate measurement.

**Endpoint (internal service):**
```
POST {SHADOW_LOG_URL}/v1/shadow-log   — write shadow evaluation entry
GET  {SHADOW_LOG_URL}/v1/shadow-log?claim_id={}&date_from={}&date_to={}
                                      — query entries for gate measurement
```

**POST /v1/shadow-log — Request:**
```json
{
  "shadow_log_id":               "UUID — agent-generated; primary key",
  "claim_id":                    "UUID — NormalizedClaimRecord foreign key",
  "agent_routing_decision":      "FAST_PATH | CLINICAL_PATH",
  "agent_confidence":            "float 0.0–1.0",
  "agent_confidence_fallback":   "boolean",
  "clinical_indicators_detected":"array of strings",
  "criteria_provisions_matched": "array of strings",
  "reasoning_trace":             "string — full CoT output",
  "agent_version":               "semver",
  "logged_at":                   "ISO 8601 UTC"
}
```

**Response (HTTP 201):** `{ "shadow_log_id": "UUID" }`

**POST /v1/shadow-log — Processor decision update** (written after processor completes routing, for comparison):
```
PUT {SHADOW_LOG_URL}/v1/shadow-log/{shadow_log_id}/processor-decision
```
```json
{
  "processor_routing_decision": "FAST_PATH | CLINICAL_PATH",
  "processor_user_id":          "string",
  "processor_decided_at":       "ISO 8601 UTC",
  "agreement":                  "AGREE | DISAGREE — computed: agent_routing_decision == processor_routing_decision"
}
```

**Query response (GET):**
```json
{
  "total_entries":          "integer",
  "labeled_entries":        "integer — entries where processor_routing_decision is set",
  "disagreement_entries":   "integer — entries where agreement = DISAGREE",
  "false_negative_count":   "integer — disagreements where agent=FAST_PATH and processor=CLINICAL_PATH",
  "false_negative_rate":    "float 0.0–1.0 — false_negative_count / labeled_entries"
}
```

**[A6] gate query:** To measure gate readiness, query with `date_from = shadow_start_date` and verify: `labeled_entries ≥ 2000` AND `false_negative_rate < 0.02`.

**Timeout:** 5 seconds. Write failure handling: retry with backoff (1 s, 2 s, 4 s); if all fail, buffer locally; alert ops; do not block claim classification.

**Retention:** Shadow log entries retained for 24 months (training data archive). After gate passes, shadow log is the primary evidence artifact for [A6] gate validation sign-off.

---

### 8.3 Ground-Truth Adjudication Queue [A25]

> **Build deliverable:** Must be built in Wave 1. This is a lightweight review portal for Dr. Webb's team to adjudicate agent-vs-processor disagreements.

**Endpoint:**
```
POST {ADJUDICATION_QUEUE_URL}/v1/adjudication-items    — submit disagreement for labeling
PUT  {ADJUDICATION_QUEUE_URL}/v1/adjudication-items/{id} — record Dr. Webb's label
GET  {ADJUDICATION_QUEUE_URL}/v1/adjudication-items?status=PENDING — list open items
```

**POST /v1/adjudication-items — Request:**
```json
{
  "adjudication_id":             "UUID — agent-generated",
  "claim_id":                    "UUID",
  "shadow_log_id":               "UUID — reference to shadow log entry",
  "agent_routing_decision":      "FAST_PATH | CLINICAL_PATH",
  "processor_routing_decision":  "FAST_PATH | CLINICAL_PATH",
  "clinical_indicators_detected":"array of strings",
  "reasoning_trace":             "string",
  "submitted_at":                "ISO 8601 UTC"
}
```

**PUT /v1/adjudication-items/{id} — Dr. Webb label:**
```json
{
  "ground_truth_routing":  "FAST_PATH | CLINICAL_PATH",
  "adjudicator_id":        "string — Dr. Webb team member user ID",
  "adjudication_notes":    "string, optional, max 1000 chars — rationale or codebook clarification",
  "adjudicated_at":        "ISO 8601 UTC",
  "trigger_codebook_update": "boolean — true if adjudication reveals a gap in [A15] criteria"
}
```

**SLA:** Adjudication items must be reviewed within 5 business days of submission. Items pending > 5 days are flagged to Dr. Webb's supervisor. If the adjudication queue backlog exceeds 50 open items, the shadow evaluation rate is considered at risk and ops is alerted [A25].

**Capacity constraint [A25]:** Dr. Webb's team capacity for adjudication is not confirmed. Assume 10 items/day maximum throughput until confirmed. If the agent-vs-processor disagreement rate generates > 10 items/day, the shadow evaluation schedule must be reviewed.

---

### 8.4 Clinical Policy Vector Store

**Purpose:** Semantic retrieval of clinical policy provisions when a claim's indicators partially match the criteria codebook — provides additional context for boundary-case classifications.

**Embedding model:** [TODO: confirm with IT discovery. Recommend OpenAI `text-embedding-3-small` or equivalent; must be the same model used to embed the policy corpus.] Store in env var `EMBEDDING_MODEL_ID`.

**Endpoint (internal vector DB, e.g., Pinecone, Weaviate, or pgvector):**
```
POST {VECTOR_STORE_URL}/v1/query   — similarity search
```

**POST /v1/query — Request:**
```json
{
  "query_text":    "string — the clinical indicator or procedure description to match against policy",
  "top_k":         3,
  "min_similarity": 0.72,
  "namespace":     "clinical-policy-v{N}"
}
```

**POST /v1/query — Response:**
```json
{
  "results": [
    {
      "chunk_id":    "string",
      "text":        "string — policy provision text",
      "similarity":  "float 0.0–1.0",
      "source_doc":  "string — policy document name and section",
      "version":     "string — policy effective date"
    }
  ]
}
```

**Trigger condition:** ADR-4 only queries the policy vector store when a claim contains clinical indicators that partially match criteria codebook entries — estimated 15–25% of claims [A4]. For clear Fast Path or clear Clinical Path classifications (all indicators either clearly absent or clearly matched), the policy RAG step is skipped. Policy RAG is not active in the current build (demo). Classification is codebook-only.

**Timeout:** 3 seconds per query. On timeout or failure: proceed with criteria codebook match only; log `POLICY_RAG_UNAVAILABLE` event. The classification decision must still be made — policy RAG is a supporting retrieval, not the primary decision mechanism.

**Cost:** Each RAG query adds approximately $0.02–$0.04 per claim to API cost. Total remains within [A4] estimate when triggered for ≤ 25% of claims.

**Namespace versioning:** Policy corpus is versioned by effective date (e.g., `clinical-policy-v3`). ADR-4 reads the `POLICY_VECTOR_STORE_NAMESPACE` env var at startup. Updates to the policy corpus require a new namespace and a corresponding env var update — no in-place mutation of embeddings.

---

## 9. Entity Data Models

> **Shared entity:** The `NormalizedClaimRecord` entity — including ADR-4's routing fields (§9.1.2) — is defined in full in `specs/06a-capability-spec-intake.md` §9.1. ADR-4 reads and writes that entity. This section defines only the entities that ADR-4 builds and owns.

### 9.1 RoutingDecisionRecord (shadow log entry)

This is the ShadowEvalLogEntry defined in §8.2 above, formalized as an entity.

| Field | Type | Required | Constraints |
|---|---|:---:|---|
| `shadow_log_id` | UUID | Yes | Agent-generated; primary key; immutable |
| `claim_id` | UUID | Yes | Foreign key to NormalizedClaimRecord; immutable |
| `agent_routing_decision` | enum | Yes | `FAST_PATH \| CLINICAL_PATH`; immutable |
| `agent_confidence` | float | Yes | 0.0–1.0; immutable |
| `agent_confidence_fallback` | boolean | Yes | `true` if routed by fallback rule [A24]; immutable |
| `clinical_indicators_detected` | array\<string\> | Yes | List of indicator strings found in claim; immutable |
| `criteria_provisions_matched` | array\<string\> | Yes | Codebook provision IDs; `["NOVEL_CASE"]` if no match; immutable |
| `reasoning_trace` | string | Yes | Full CoT output text; immutable; max 5000 chars |
| `agent_version` | string | Yes | Semver; immutable |
| `logged_at` | timestamp | Yes | ISO 8601 UTC; immutable |
| `processor_routing_decision` | enum | No | `FAST_PATH \| CLINICAL_PATH`; written after processor routes claim |
| `processor_user_id` | string | No | Written when processor decision is recorded |
| `processor_decided_at` | timestamp | No | ISO 8601 UTC; written when processor decision is recorded |
| `agreement` | enum | No | `AGREE \| DISAGREE`; computed: agent == processor; written when processor decision recorded |
| `ground_truth_routing` | enum | No | `FAST_PATH \| CLINICAL_PATH`; written by Dr. Webb adjudication [A25] |
| `adjudication_id` | UUID | No | Foreign key to AdjudicationQueueEntry; present if disagreement was adjudicated |

**State machine:**
```
LOGGED              — agent classification written; awaiting processor decision
    ↓  (processor routes claim)
PROCESSOR_LABELED   — processor decision recorded; agreement field computed
    ↓  (if agreement = DISAGREE)
ADJUDICATION_PENDING — submitted to Dr. Webb adjudication queue [A25]
    ↓  (Dr. Webb labels)
GROUND_TRUTH_SET    — definitive label available for gate calculation
    ↓  (if agreement = AGREE; no adjudication needed)
GROUND_TRUTH_SET    — agreement counts as ground truth confirmation
```

**[A6] gate calculation:** Uses only entries in `GROUND_TRUTH_SET` state. False negative = `agent_routing_decision = FAST_PATH` AND `ground_truth_routing = CLINICAL_PATH`.

---

### 9.2 CriteriaCodebookEntry [A15]

> **Build deliverable:** Does not exist. Must be co-developed with Dr. Webb in Week 1. This entity definition specifies the data model the codebook must follow.

| Field | Type | Required | Constraints |
|---|---|:---:|---|
| `provision_id` | string | Yes | Primary key; format `CC-{NNN}` (e.g., `CC-001`); immutable once published |
| `provision_name` | string | Yes | Max 100 chars; human-readable name |
| `clinical_category` | enum | Yes | `DIAGNOSTIC_IMAGING \| SPECIALIST_AUTHORIZATION \| MEDICAL_NECESSITY \| PROCEDURE_COMPLEXITY \| PRIOR_AUTH_REQUIRED \| OTHER_CLINICAL` |
| `trigger_icd10_patterns` | array\<string\> | No | ICD-10 code prefixes or exact codes that trigger this provision (e.g., `["Z51.1", "C18"]`); empty array if not ICD-10-triggered |
| `trigger_cpt_patterns` | array\<string\> | No | CPT code prefixes or exact codes that trigger this provision; empty array if not CPT-triggered |
| `trigger_prior_auth_required` | boolean | No | `true` if prior_auth_required = true alone is sufficient to trigger this provision |
| `trigger_free_text_keywords` | array\<string\> | No | Keywords in unstructured claim notes that suggest this provision (used for partial-match RAG trigger) |
| `routing_outcome` | enum | Yes | `CLINICAL_PATH` — every provision in this codebook routes to Clinical Path. Fast Path is the default; provisions only override toward Clinical Path. |
| `description` | string | Yes | Max 500 chars; clinical rationale for why this provision requires physician review |
| `effective_date` | date | Yes | ISO 8601 `YYYY-MM-DD`; date provision took effect |
| `retired_date` | date | No | ISO 8601 `YYYY-MM-DD`; null if still active |
| `approved_by` | string | Yes | Dr. Webb's user ID; must be present before provision is deployed |
| `approved_at` | timestamp | Yes | ISO 8601 UTC; immutable once set |
| `codebook_version` | string | Yes | Semver of the codebook release this provision belongs to |

**Deployment rule:** A codebook entry must not be loaded into the ADR-4 system prompt until `approved_by` is populated by Dr. Webb and `effective_date` ≤ today. Entries with `retired_date` ≤ today must not appear in the active system prompt.

**Minimum viable codebook:** At least 1 provision per `clinical_category` must exist before shadow mode can begin. Dr. Webb's Week 1 deliverable is a codebook with at minimum 20 provisions covering the most common clinical content types in Greenfield's claim mix.

---

### 9.3 AdjudicationQueueEntry [A25]

| Field | Type | Required | Constraints |
|---|---|:---:|---|
| `adjudication_id` | UUID | Yes | Agent-generated; primary key; immutable |
| `claim_id` | UUID | Yes | Foreign key to NormalizedClaimRecord; immutable |
| `shadow_log_id` | UUID | Yes | Foreign key to RoutingDecisionRecord; immutable |
| `agent_routing_decision` | enum | Yes | `FAST_PATH \| CLINICAL_PATH`; immutable |
| `processor_routing_decision` | enum | Yes | `FAST_PATH \| CLINICAL_PATH`; immutable |
| `clinical_indicators_detected` | array\<string\> | Yes | Copied from shadow log; immutable |
| `reasoning_trace` | string | Yes | Copied from shadow log; immutable |
| `submitted_at` | timestamp | Yes | ISO 8601 UTC; immutable |
| `status` | enum | Yes | `PENDING \| IN_REVIEW \| RESOLVED`; default `PENDING` |
| `ground_truth_routing` | enum | Conditional | Required when `status = RESOLVED`; `FAST_PATH \| CLINICAL_PATH` |
| `adjudicator_id` | string | Conditional | Required when `status = RESOLVED`; Dr. Webb team member user ID |
| `adjudication_notes` | string | No | Max 1000 chars; rationale or codebook gap identification |
| `trigger_codebook_update` | boolean | Conditional | Required when `status = RESOLVED`; `true` if this case reveals a codebook gap |
| `adjudicated_at` | timestamp | Conditional | ISO 8601 UTC; required when `status = RESOLVED` |
| `sla_deadline` | timestamp | Yes | `submitted_at + 5 business days`; auto-escalated at deadline |

---

## 10. Validation Scenarios

### 10.1 Happy Path — Shadow Mode, Clinical Claim Correctly Identified

**Input (Wave 1, shadow mode):** Normalized claim record available in CMS with `routing_decision: PENDING_TRIAGE`. Claim contains ICD-10 code `Z51.11` (encounter for antineoplastic chemotherapy) and CPT code `96413`. Both codes map to CMS codebook provision `CC-003` (oncology diagnosis or treatment). `MODE: SHADOW` declared in system prompt.

**Expected outcome:**
1. ADR-4 reads claim from CMS via GET `/v1/claims/{claim_id}`.
2. Clinical indicators extracted: `["ICD-10: Z51.11", "CPT: 96413"]`.
3. Codebook match found: provision `CC-003` triggered by both ICD-10 and CPT patterns.
4. Confidence scored: 0.94 (high — both indicators match explicitly; no partial match).
5. Confidence ≥ threshold [A24] — fallback not triggered.
6. Routing decision: `CLINICAL_PATH`.
7. Shadow log entry written (NOT CMS operative routing): `agent_routing_decision: CLINICAL_PATH`, `mode: SHADOW`.
8. CMS claim record routing fields written with `routing_mode: SHADOW` — claim status remains `QUEUED`; processor routing continues unchanged.
9. Audit log entry: `event_type: ROUTING_DECISION_LOGGED`, `routing_mode: SHADOW`.
10. Processor independently routes claim to Clinical Path → agreement = `AGREE`.

---

### 10.2 Happy Path — Live Mode, Administrative Claim Correctly Routed Fast Path

**Input (Wave 2, live mode):** Normalized claim with `routing_decision: PENDING_TRIAGE`. Claim is a routine office visit: CPT `99213`, ICD-10 `Z00.00` (encounter for general adult medical exam without abnormal findings). No prior auth required. No free-text clinical notes. `MODE: LIVE` declared in system prompt.

**Expected outcome:**
1. Clinical indicators extracted: `["ICD-10: Z00.00", "CPT: 99213"]`.
2. Codebook matching: no provisions triggered — Z00.00 and 99213 match no Clinical Path provisions.
3. Confidence: 0.96. No fallback triggered.
4. Routing decision: `FAST_PATH`.
5. CMS PUT `/v1/claims/{claim_id}` issued with operative `routing_decision: FAST_PATH`, `routing_mode: LIVE`.
6. Claim status transitions to `FAST_PATH`.
7. Audit log entry: `event_type: ROUTING_DECISION_WRITTEN`, `outcome: SUCCESS`.
8. Daily routing summary batch includes this claim; no per-claim human notification.

---

### 10.3 Edge Cases

**EC-1: Confidence exactly at threshold boundary**
- Input: Claim with one ICD-10 code that partially matches a codebook provision. Policy RAG retrieval returns 2 of 3 results above `min_similarity: 0.72`. Agent CoT computes confidence exactly at the configured threshold value [A24].
- Expected: Threshold comparison is `confidence >= threshold` for Fast Path routing and `confidence < threshold` for fallback. At exactly the threshold value, the condition `confidence >= threshold` is `true` — claim routes per the primary classification (not fallback). `routing_confidence_fallback: false`. If the primary classification is FAST_PATH at exactly the threshold, the claim routes FAST_PATH. Note: this edge case must be explicitly covered in unit tests for the threshold comparison function.

**EC-2: Confidence below threshold — conservative fallback**
- Input: Claim with ambiguous indicators; agent CoT computes confidence 0.65 (below threshold of 0.70 [A24]).
- Expected: `routing_decision: CLINICAL_PATH`, `routing_confidence: 0.65`, `routing_confidence_fallback: true`. Criteria provisions matched still populated (partial matches cited). Reasoning trace explains fallback trigger. CMS write proceeds with `CLINICAL_PATH` decision. Logged in daily summary as fallback event.

**EC-3: Novel case — no codebook match**
- Input: Claim with CPT code `0789T` (a recently introduced AMA code not present in the criteria codebook at time of classification).
- Expected: CoT reaches Step 2 (codebook matching) with no provisions matched. Guardrail triggers: `routing_decision: CLINICAL_PATH`, `confidence: 0.0`, `criteria_provisions_matched: ["NOVEL_CASE"]`. Exception queue entry submitted for Dr. Webb adjudication. `trigger_codebook_update: true`. Claim safely routes to Clinical Path — no patient safety risk from novel case handling.

**EC-4: Prior auth required, marginal other indicators**
- Input: Claim with `prior_auth_required: true`; ICD-10 and CPT codes are all routine (no other codebook triggers).
- Expected: Codebook provision `CC-{N}` (prior_auth_required = true trigger) fires. Routing decision: `CLINICAL_PATH`. Even if all other indicators are administrative, prior auth requirement alone is sufficient to route Clinical Path per the codebook. This behavior must be explicitly covered in the few-shot examples.

**EC-5: Shadow mode — agent disagrees with processor**
- Input (Wave 1): Claim contains CPT `27447` (total knee arthroplasty). Agent classifies `CLINICAL_PATH` (confidence 0.89). Processor routes claim to `FAST_PATH`.
- Expected: Shadow log entry written with `agreement: DISAGREE`. AdjudicationQueueEntry submitted to Dr. Webb's review portal. Dr. Webb labels `ground_truth_routing: CLINICAL_PATH`. Shadow log entry transitions to `GROUND_TRUTH_SET`. This disagreement counts toward false-negative detection: processor routed FAST_PATH, ground truth is CLINICAL_PATH → this is a processor false negative (not an agent false negative). Agent was correct.

**EC-6: False negative detected in live mode monthly audit**
- Input: Physician audit of 5% Fast Path sample (Wave 2). Physician identifies claim `{claim_id}` as having clinical content (diagnostic imaging series, CPT 71250) that should have routed Clinical Path.
- Expected: (1) Physician flags claim in audit portal with `audit_finding: FALSE_NEGATIVE`. (2) Claim re-routed to Clinical Path via ops intervention. (3) Audit finding triggers ops alert: `FALSE_NEGATIVE_DETECTED`. (4) Root cause analysis: was the CPT code in the codebook? If not → codebook update. If yes → model misclassification → retrain review. (5) If audit finds ≥ 2 false negatives in the same monthly sample (5% of Fast Path), false-negative rate calculation is triggered against full Fast Path volume. If rate exceeds 2%, autonomous routing is suspended.

**EC-7: Criteria codebook missing from system prompt (deployment error)**
- Input: System prompt loads without the codebook content (deployment misconfiguration).
- Expected: Agent detects codebook absence (Step 2 of CoT: codebook is empty). All claims route to `CLINICAL_PATH` with `confidence: 0.0` and `criteria_provisions_matched: ["CODEBOOK_MISSING"]`. This is the safe failure mode — routing everything Clinical Path when codebook is unavailable prevents false negatives. Alert emitted: `CODEBOOK_LOAD_FAILURE`. Operations team must redeploy with correct system prompt before resuming normal operation.

---

### 10.4 Failure Mode Scenarios

**FM-1: False-negative rate exceeds 2% in monthly audit**
- Trigger: Monthly physician audit (5% Fast Path sample) identifies false-negative rate above 0.02.
- Expected: (1) Autonomous routing suspended immediately — all claims revert to processor routing. (2) Ops alert: `FN_GATE_EXCEEDED`, `measured_fn_rate: {value}`, `sample_size: {n}`. (3) Root cause analysis initiated within 1 business day: codebook gap vs. model error vs. audit methodology error. (4) Corrective action: update codebook AND/OR retrain on new labeled examples. (5) Routing cannot resume until a new shadow evaluation window (minimum 30 days, ≥ 500 labeled examples) clears the 2% threshold. (6) CFO and CMO notified per stakeholder alignment memo.

**FM-2: Shadow evaluation log store unavailable during Wave 1**
- Trigger: Shadow log store returns HTTP 5xx on POST; all retries exhausted.
- Expected: (1) Agent classification continues (classification logic does not depend on log store availability). (2) Shadow log entries buffered locally in durable queue (same pattern as CMS fallback in ADR-1). (3) `SHADOW_LOG_UNAVAILABLE` alert sent to ops. (4) On recovery, local buffer replayed with idempotency keys. (5) If shadow log is unavailable for > 24 hours, the shadow evaluation schedule must be extended by an equivalent period to preserve the integrity of the [A6] gate calculation (60-day window assumes continuous logging).

**FM-3: [A15] criteria codebook not delivered by Week 1 deadline**
- Trigger: Dr. Webb's team has not completed the clinical content criteria definition by the end of Week 1.
- Expected: (1) ADR-4 shadow mode cannot begin — the system prompt cannot be written without the codebook. (2) ADR-1 intake pipeline can proceed independently (it does not depend on ADR-4). (3) Project manager notifies CFO and CMO: shadow evaluation 60-day clock has not started; Phase 1 gate timeline shifts by number of weeks criteria definition is delayed. (4) This is the highest-likelihood delay risk in the Wave 1 schedule.

---

## 11. Governance

### 11.1 HIPAA Compliance

ADR-4 processes PHI including member IDs, diagnosis codes (ICD-10), procedure codes (CPT), and clinical documentation excerpts. The same HIPAA constraints as ADR-1 apply (see `specs/06a-capability-spec-intake.md` §11.1), plus the following ADR-4-specific requirements:

| Requirement | Implementation |
|---|---|
| Clinical reasoning trace contains PHI | The `reasoning_trace` field in routing decisions contains clinical indicator details that may constitute PHI. It must be stored only in the audit log store and shadow evaluation log (both are designated PHI systems). It must not be logged to general application logs. |
| Shadow log PHI | The shadow evaluation log store contains claim IDs and clinical indicators — PHI-adjacent data. Access must be restricted to the shadow evaluation pipeline and Dr. Webb's adjudication team. |
| Adjudication queue PHI | Dr. Webb's team accessing adjudication items is a covered use under HIPAA treatment operations. Each access must be logged with `adjudicator_id` and timestamp. |
| Model training data | Ground-truth labeled examples from the adjudication queue may be used for model retraining. Before use in any training pipeline, examples must be reviewed for PHI minimization — only clinically relevant fields (ICD-10, CPT, prior auth flag) are retained; member name, DOB, and member ID are replaced with synthetic values. |

### 11.2 Audit Trail Requirements

Every routing decision by ADR-4 must produce audit log entries (shared infrastructure with ADR-1):

| Event | When | Required Fields |
|---|---|---|
| `ROUTING_DECISION_LOGGED` | Shadow mode: after shadow log write | `claim_id`, `agent_routing_decision`, `agent_confidence`, `routing_mode: SHADOW`, `agent_version` |
| `ROUTING_DECISION_WRITTEN` | Live mode: after CMS PUT succeeds | `claim_id`, `routing_decision`, `routing_confidence`, `routing_confidence_fallback`, `routing_mode: LIVE`, `agent_version` |
| `ROUTING_FALLBACK_APPLIED` | When confidence_fallback = true | `claim_id`, `confidence`, `threshold_value`, `final_decision: CLINICAL_PATH` |
| `NOVEL_CASE_FLAGGED` | When NOVEL_CASE provisions matched | `claim_id`, `clinical_indicators_detected`, `adjudication_queue_id` |
| `FN_DETECTED_AUDIT` | When physician audit finds false negative | `claim_id`, `original_routing`, `corrected_routing`, `auditor_id` |

**Retention:** 7 years (same as ADR-1 audit log). Shadow evaluation log retained 24 months.

### 11.3 Shadow Mode Isolation Guarantee

The following technical constraints must be enforced in Wave 1 to ensure shadow mode cannot accidentally perform live routing:

1. `MODE: SHADOW` must appear as the **first line** of the system prompt in Wave 1 deployments. Any deployment without this line is a misconfiguration and must be rejected by a pre-deployment validation check.
2. The agent's CMS write in shadow mode must be a metadata-only annotation (routing fields with `routing_mode: SHADOW`). The claim's `status` field and `routing_decision` operative field must not change.
3. A pre-deployment integration test must verify that a claim's status is unchanged after ADR-4 runs in shadow mode.
4. Wave 2 live mode activation requires an explicit configuration change (`MODE: SHADOW → MODE: LIVE`) with a separate deployment step — it must not be achievable by modifying the prompt at runtime.

### 11.4 Live Mode Activation Gate

Autonomous routing (Wave 2) must not activate unless all of the following conditions are satisfied and documented:

| Gate Condition | Evidence Required | Sign-off |
|---|---|---|
| False-negative rate < 2% [A6] | Shadow evaluation log query showing `false_negative_rate < 0.02` over ≥ 60 calendar days and ≥ 2,000 labeled entries | Dr. Webb (CMO) |
| Criteria codebook approved [A15] | Codebook version with all provisions carrying `approved_by: Dr.Webb` | Dr. Webb (CMO) |
| CMS shadow write confirmed isolated | Integration test results showing no live routing occurred during shadow window | VP Operations (James Liu) |
| Stakeholder alignment confirmed | All three stakeholder sign-offs on Phase 1 results per §00-stakeholder-alignment-memo.md | CFO, CMO, VP Ops |

Any gate condition not met at the 60-day mark: wave 2 is deferred; shadow window extended; stakeholders notified with revised timeline.

---

*See `specs/assumptions.md` for full definitions of [A2], [A4], [A6], [A10], [A12], [A15], [A17], [A24], [A25], [U1].*  
*See `specs/volume-×-value-analysis.md` Section 8 for full wave sequencing logic and fallback positions.*  
*See `specs/00-stakeholder-alignment-memo.md` for Phase 1 gate commitment between CFO, CMO, and VP Operations.*  
*Shared entities (CMS API, normalized record schema, reuse matrix) are consistent with `specs/06a-capability-spec-intake.md`.*
