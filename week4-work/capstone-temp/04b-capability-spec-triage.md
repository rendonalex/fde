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

This matrix is consistent with `specs/04a-capability-spec-intake.md`.

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

*See `specs/assumptions.md` for full definitions of [A2], [A4], [A6], [A10], [A12], [A15], [A17], [A24], [A25], [U1].*  
*See `specs/volume-×-value-analysis.md` Section 8 for full wave sequencing logic and fallback positions.*  
*See `specs/00-stakeholder-alignment-memo.md` for Phase 1 gate commitment between CFO, CMO, and VP Operations.*  
*Shared entities (CMS API, normalized record schema, reuse matrix) are consistent with `specs/04a-capability-spec-intake.md`.*
