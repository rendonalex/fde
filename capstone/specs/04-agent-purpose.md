# Agent Purpose, Autonomy Matrix, and Activity Catalog
## Greenfield Health Systems AI Claims Processing Transformation

**Compiled from:** specs/06a-capability-spec-intake.md (ADR-1) and specs/06b-capability-spec-triage.md (ADR-4)  
**Date:** 2026-05-27  
**Purpose:** Consolidated view of agent purpose definitions, autonomy design, and activity catalogs per capability specification

---

## Table of Contents

1. [ADR-1: Claim Intake and Format Validation Agent](#adr-1-claim-intake-and-format-validation-agent)
   - [Agent Purpose Document](#agent-purpose-document)
   - [Autonomy Matrix](#autonomy-matrix)
   - [Agent Activity Catalog](#agent-activity-catalog)
2. [ADR-4: Clinical Content Triage Agent](#adr-4-clinical-content-triage-agent)
   - [Agent Purpose Document](#agent-purpose-document-1)
   - [Autonomy Matrix](#autonomy-matrix-1)
   - [Agent Activity Catalog](#agent-activity-catalog-1)

---

## ADR-1: Claim Intake and Format Validation Agent

### Agent Purpose Document

```
Agent Name:       Claim Intake and Format Validation Agent
Job to be Done:   Transform every incoming claim submission into a validated, normalized,
                  SLA-prioritized record in the CMS — the structured input prerequisite
                  for all downstream agents.
Business context: Zone 1 (Intake) — the entry point of the claims processing workflow;
                  handles all 1,667 claims/day [U1] across EDI 837P/I, portal JSON,
                  FHIR R4, CMS-1500 PDF (scanned and pre-OCR'd), email (.eml),
                  fax PDF, fax-email, and exception-note channels.

Primary objectives:
  1. Parse and normalize all EDI 837P and 837I submissions end-to-end without human involvement.
  2. Extract structured fields from non-EDI submissions via IDP; escalate unresolvable
     extractions to a human exception queue with per-field confidence detail.
  3. Validate required field completeness and assign every claim to an SLA-prioritized
     queue before releasing it for downstream processing.

KPIs:
  - Accuracy:    ≥98% field extraction accuracy on EDI path;
                 ≥90% on non-EDI path (per-field confidence ≥ 0.85 threshold)
  - Coverage:    ≥90% of all claims processed to CMS without human intervention
                 (EDI path: 100%; non-EDI path: ~80% [A14])
  - Throughput:  1,667 claims/day queued within 1 hour of receipt
  - Cost/claim:  ~$0.05 API cost [A4]
  - HITL rate:   ≤10% of non-EDI volume (~50 claims/day human re-key)

Failure modes:
  - Extraction failure (required field unresolvable): pend claim with specific
    missing-field flag; do NOT deny; route to exception queue for re-key.
  - CMS write failure [A12]: hold claim locally with idempotency key; retry on
    API recovery; alert ops team after 3 failed retries.
  - Duplicate claim detected (same claim ID + member + DOS): pend
    with duplicate flag; notify submitting processor for resolution.
  - Exception note detected (EXCEPTION_NOTE channel): extract claim_id if present;
    attach note text to existing CMS claim record as annotation; do NOT create a
    new NormalizedClaimRecord.
  - Novel format (not any recognized channel): route to exception queue with
    format-unrecognized flag; do not attempt extraction.

Delegation archetype:
  Agent-led + Human Oversight — split by sub-path:
    - EDI sub-path: Fully Agentic (no human involvement for well-formed EDI 837)
    - Non-EDI sub-path: Agent-led + Human Oversight (HITL only on extraction failures)

Escalation triggers:
  - Any required field extraction confidence < 0.85 → human re-key queue
  - CMS API unavailable after 3 retries [A12] → ops alert
  - Duplicate claim detected → processor notification queue
  - Claim volume spike >2× daily average → ops alert for capacity check
```

---

### Autonomy Matrix

```
AGENT DECIDES ALONE (no HITL required):
  - EDI 837 parsing and field extraction
  - Completeness validation against required field list
  - Duplicate claim detection
  - SLA-priority queue assignment
  - CMS record creation for validated claims
  - Exception flag generation with per-field detail
  - Routing of below-threshold extractions to human queue
    (escalation decision is autonomous; human executes re-key)
  - Audit log entry for every processed claim

AGENT ACTS, HUMAN NOTIFIED AFTER:
  - Non-EDI extraction where all fields resolve above confidence threshold
    (extraction result logged; processor receives notification of new claim in queue)
  - Duplicate hold (processor notified after pend is placed)

AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:
  - Non-EDI extraction where ≥1 required field confidence < 0.85:
    agent presents extracted fields with confidence scores;
    human reviews, corrects, and approves before CMS write
  - (No approvals required on EDI path)

HUMAN TAKES OVER (agent supports):
  - CMS API failure that exceeds retry budget [A12] — ops team manages
    batch recovery; agent queues claims locally and provides status log
  - Claims in unrecognized formats — agent flags format + provides
    available metadata; human determines handling
  - Batch import of legacy backlog claims — human-managed with agent
    assisting field extraction
```

---

### Agent Activity Catalog

| Task | Type | Delegation Level | Data Required | Tool Required | Risk Level |
|------|------|:----------------:|---------------|---------------|:----------:|
| Detect incoming claim format (EDI 837 / PDF / portal) | Reasoning | Fully agentic | Incoming file/message headers | Format detection library | Low |
| Parse EDI 837P transaction set (segments: CLM, NM1, SV1, DTP, etc.) | Retrieval | Fully agentic | EDI 837P `.edi` file | EDI 837 parser | Low |
| Parse EDI 837I transaction set (segments: SV2, HI*DRG, revenue codes, etc.) | Retrieval | Fully agentic | EDI 837I `.edi` file | EDI 837 parser | Low |
| Parse FHIR R4 Claim resource JSON into NormalizedClaimRecord fields | Retrieval | Fully agentic | FHIR R4 `.json` file | FHIR R4 parser (§8.7) | Low |
| Extract RFC 5322 headers from email (.eml) — X-Submitter-NPI, X-Submitter-TaxID | Retrieval | Fully agentic | `.eml` file headers | RFC 5322 header parser | Low |
| Extract required claim fields from PDF/portal/email/fax body via IDP [A14] | Retrieval | Agent-led + HITL on low-confidence | PDF, portal JSON, email body, fax, fax-email, OCR text | IDP extraction pipeline | Medium |
| Route exception note to existing CMS claim record as annotation | Action | Fully agentic (HITL if claim_id absent) | Exception note PDF or text | CMS write API (annotation) | Low |
| Score per-field extraction confidence | Reasoning | Fully agentic | IDP extraction result | Confidence scoring model | Medium |
| Validate required field completeness against CMS field schema | Decision | Fully agentic | Extracted fields + CMS schema | Field validation rules engine | Medium |
| Check for duplicate submission (claim ID, member ID, DOS) | Decision | Fully agentic | Normalized claim fields | CMS read API | Low |
| Flag completeness exception with per-field detail | Generation | Fully agentic | Validation result | CMS write API (exception flag) | Low |
| Write normalized claim record to CMS | Action | Fully agentic | Validated + normalized claim data | CMS write API | Medium |
| Assign claim to SLA-prioritized processing queue [A17] | Action | Fully agentic | Claim receipt timestamp, payer SLA config | Queue management module | Low |
| Route low-confidence extractions to human exception queue | Action | Fully agentic (escalation decision) | Per-field confidence scores | Exception queue API | Medium |
| Log intake decision and extraction metadata for audit trail | Action | Fully agentic | All above fields + confidence scores | Audit log store | Medium |

**Task type legend:** Reasoning (model does cognitive work) · Retrieval (fetch/return data) · Decision (choose between outcomes) · Action (write to system or trigger process) · Generation (produce structured output)

**Key design notes:**
- MT-1.2 (non-EDI extraction) is the only task with meaningful HITL. The IDP pipeline handles ~80% of PDFs automatically [A14]; the remaining ~20% require human re-key and are the source of the $46,875/year HITL cost (Section 4 of the Volume × Value Analysis).
- MT-1.4 (queue assignment) implements the SLA-aware prioritization described in [A17] — claims nearest the 7-day penalty threshold surface first. This is a new capability not present in the current process.
- MT-1.3 (completeness validation) uses the CMS required-field schema as a deterministic rule set — no LLM reasoning required here; the agent wraps the rules engine.

---

## ADR-4: Clinical Content Triage Agent

### Agent Purpose Document

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

### Autonomy Matrix

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

### Agent Activity Catalog

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

*See `specs/assumptions.md` for full definitions of all [A#] assumption references.*  
*See `specs/06a-capability-spec-intake.md` and `specs/06b-capability-spec-triage.md` for complete capability specifications including integration contracts, entity models, and validation scenarios.*
