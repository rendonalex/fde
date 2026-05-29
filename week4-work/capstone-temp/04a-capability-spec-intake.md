# Capability Specification: Claim Intake and Format Validation Agent
## ADR-1 — Greenfield Health Systems AI Claims Processing Transformation

**Prepared by:** FDE Engagement Lead  
**Date:** 2026-05-21  
**Wave:** Wave 1 (Phase 1, Months 1–3)  
**Delegation Archetype:** Agent-led + Human Oversight  
**Status:** Active — specification finalized pending [A12] CMS API confirmation

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

ADR-1 is the foundational intake layer for the entire dual-path claims architecture. It transforms raw claim submissions — EDI 837, PDF, and portal formats — into validated, normalized, SLA-prioritized records in the Claims Management System (CMS), ready for downstream agent processing.

The intake agent runs on two sub-paths. The **EDI path** (70% of volume [A7]) is fully agentic: EDI 837 transactions are structured by HIPAA mandate, machine-parsable, and flow through without human involvement. The **non-EDI path** (30% of volume [A7]) uses an Intelligent Document Processing (IDP) pipeline — currently not in place [A14] — to extract required fields from PDF and portal submissions. Extractions above a per-field confidence threshold proceed automatically; those below route to a human exception queue for re-key. The target HITL rate is ≤10% of non-EDI volume (~50 claims/day).

ADR-1 is sequenced Wave 1 for two reasons: (1) the intake pipeline is the structural prerequisite for ADR-4 triage — the clinical classification model requires normalized, structured claim records as input; and (2) it generates the only Wave 1 autonomous savings (~$117K/year [A21]) while ADR-4 runs in shadow mode without adjudicating any claims.

The primary platform assets created by ADR-1 — the CMS API integration, normalized claim record schema, IDP extraction pipeline, and SLA-aware queue module — are reused by every Wave 2 and Wave 3 agent. The marginal build cost of downstream agents is materially reduced by this foundation.

**Key metrics:**
- Throughput: 1,667 claims/day processed to queue-assigned status within 1 hour of receipt [U1]
- Accuracy: ≥98% field extraction on EDI path; ≥90% on non-EDI path
- HITL rate: ≤10% of non-EDI volume (~50 claims/day escalated to human queue)
- Cost per claim: ~$0.05 API cost [A4]; $46,875/year HITL residual
- Payback contribution: ~$117K/year from intake automation (9% of admin baseline [A21])

---

## 2. Agent Purpose Document

```
Agent Name:       Claim Intake and Format Validation Agent
Job to be Done:   Transform every incoming claim submission into a validated, normalized,
                  SLA-prioritized record in the CMS — the structured input prerequisite
                  for all downstream agents.
Business context: Zone 1 (Intake) — the entry point of the claims processing workflow;
                  handles all 1,667 claims/day [U1] across EDI, PDF, and portal channels.

Primary objectives:
  1. Parse and normalize all EDI 837 submissions end-to-end without human involvement.
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
  - Duplicate claim detected (same claim ID + member + DOS + provider): pend
    with duplicate flag; notify submitting processor for resolution.
  - Novel format (not EDI, not standard PDF): route to exception queue with
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

## 3. Agent Activity Catalog

| Task | Type | Delegation Level | Data Required | Tool Required | Risk Level |
|------|------|:----------------:|---------------|---------------|:----------:|
| Detect incoming claim format (EDI 837 / PDF / portal) | Reasoning | Fully agentic | Incoming file/message headers | Format detection library | Low |
| Parse EDI 837 transaction set (segments: CLM, NM1, SV1, DTP, etc.) | Retrieval | Fully agentic | EDI 837 file | EDI 837 parser | Low |
| Extract required claim fields from PDF/portal via IDP [A14] | Retrieval | Agent-led + HITL on low-confidence | PDF or portal submission | IDP extraction pipeline | Medium |
| Score per-field extraction confidence | Reasoning | Fully agentic | IDP extraction result | Confidence scoring model | Medium |
| Validate required field completeness against CMS field schema | Decision | Fully agentic | Extracted fields + CMS schema | Field validation rules engine | Medium |
| Check for duplicate submission (claim ID, member ID, DOS, provider NPI) | Decision | Fully agentic | Normalized claim fields | CMS read API | Low |
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

## 4. Autonomy Matrix

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

## 5. System and Data Inventory

| System | Data Needed | Access Type | Availability | Gap / Risk |
|--------|-------------|:-----------:|--------------|------------|
| CMS (Claims Management System) | Claim record create; queue assignment; duplicate lookup by claim ID, member ID, DOS, provider NPI | Read / Write | Assumed API available [A12] | **Primary Wave 1 blocker** — integration scope and API maturity must be confirmed in Week 1 IT discovery sprint |
| EDI 837 parser | EDI transaction segments: CLM, NM1, SV1, DTP, REF, HI/HCP diagnosis and procedure codes | Read | Commercially available (e.g., StediStudio, Centauri Health) | No gap — standard healthcare tooling; license cost only |
| IDP extraction pipeline | Claim fields from PDF/portal submissions: provider NPI, member ID, DOS, ICD-10, CPT, billed amount | Read | **Must be built** — not currently in place [A14] | Wave 1 build deliverable (~$35K in build cost budget); scope depends on PDF structure variety |
| Queue management module | SLA age, payer priority config, queue position assignment | Read / Write | Part of CMS or standalone | SLA-aware config may not exist [A17]; may require new CMS configuration or standalone module |
| Audit log store | Intake decision, extraction confidence scores, timestamps, routing outcome, operator ID for re-key | Write | Standard infrastructure (e.g., structured log to data warehouse) | No gap — standard logging infrastructure |
| Exception queue | Human re-key routing; per-field extraction detail passed to processor UI | Read / Write | Assumed existing ops queue workflow | Ops process integration required; UI for displaying per-field confidence scores to processor needs design |

**Shared with ADR-4 (Clinical Content Triage Agent):** CMS read API and normalized claim record schema. ADR-4 ingests ADR-1 output directly — the canonical claim record format designed in Wave 1 must accommodate triage classification metadata fields (clinical indicator flags, routing decision) without schema changes in Wave 2.

---

## 6. Context Engineering Design

### Memory Architecture

| Memory Type | Content | Storage | Lifecycle |
|-------------|---------|:-------:|-----------|
| **In-context** (short-term) | Current claim fields, IDP extraction result, validation status, confidence scores | Prompt window | Per claim — stateless; no cross-claim context |
| **Procedural** (static) | Required field list, CMS field schema, validation rules, duplicate detection logic, confidence threshold (0.85), escalation decision rules | System prompt | Version-controlled; updated on schema change |
| **Episodic** (medium-term) | Per-claim extraction history (confidence scores, prior rejection flags, re-submission count) | CMS claim record metadata | Per claim; used for re-submission handling and audit |

ADR-1 does not require semantic memory (RAG) — all decisions are deterministic rule application. The system prompt carries the complete rulebook.

### Retrieval Strategy

- **Field schema lookup:** Deterministic. Required field list and CMS schema loaded into system prompt at deployment time — not retrieved per claim. Updated on CMS schema change via prompt versioning.
- **Duplicate check:** Structured CMS query by claim ID + member ID + DOS + provider NPI — exact match via CMS read API. Not semantic retrieval.
- **Payer SLA config:** Loaded into queue management module at startup; refreshed daily. Not per-claim retrieval.
- **Retrieval cost management:** No RAG required; zero retrieval overhead per claim. Agent cost is dominated by IDP extraction calls (non-EDI path only).

### Prompt / Context Engineering Principles

1. **Role and scope first:** System prompt opens with agent identity and the exact list of permitted actions: parse, validate, deduplicate, log, queue-assign, escalate. Prohibited actions stated explicitly: "Do not make clinical decisions. Do not deny claims. Do not modify billing codes."
2. **Structured output required:** Agent outputs a JSON record conforming to the CMS write API contract. Field: `extraction_status` ∈ {`AUTO_COMPLETE`, `HUMAN_REQUIRED`, `PENDING_DUPLICATE`}; field `field_confidence` is a map of required fields to confidence scores.
3. **Guardrail for escalation:** "If any required field in the attached schema resolves at confidence < 0.85, set `extraction_status: HUMAN_REQUIRED` and populate `field_confidence` with per-field scores. Do not write to CMS until human confirmation is received."
4. **No few-shot examples needed on EDI path** — parsing is deterministic. Non-EDI path benefits from 3–5 extraction examples covering PDF layout variants common in Greenfield's provider mix.
5. **Token discipline:** System prompt is minimal (~300 tokens for rules + schema). Claim data (EDI transaction or extracted fields) passed as structured input. Avoid prose descriptions in the system prompt; prefer field-level rules.
6. **No chain-of-thought required** — intake is rule-bound; step-by-step reasoning instructions add cost without accuracy benefit. Reserve CoT for ADR-4 triage where clinical reasoning is required.

---

## 7. Compounding Roadmap

ADR-1 is Wave 1's platform-building agent. Every integration and asset it creates is reused by Wave 2 and Wave 3 agents — reducing marginal build cost and ensuring schema consistency across the pipeline.

### Wave Sequencing

**Wave 1 — ADR-1 builds the foundation (Months 1–3):**
- CMS API integration (read/write) — the single shared integration point for all downstream agents
- Normalized claim record schema — the canonical data contract; must be designed with downstream ADR field requirements in mind
- EDI 837 parser — reused if a future EDI output path is needed (e.g., ADR-8 payment trigger)
- IDP extraction pipeline — reused by ADR-6 for clinical documentation extraction
- SLA-aware queue management module — reused by ADR-4 (triage routing queue) and ADR-5 (Fast Path adjudication queue)
- Audit log infrastructure — reused by ADR-4 (shadow mode logging) and all Wave 2 agents

**Wave 2 — All Wave 2 agents reuse ADR-1 assets (Months 4–6):**
- ADR-4 (triage): ingests normalized claim record from ADR-1; uses CMS API to write routing decision
- ADR-2 (eligibility): reads member and provider fields from ADR-1 normalized record via CMS API
- ADR-3 (coding validation): reads ICD-10/CPT fields from ADR-1 normalized record via CMS API
- ADR-5 (Fast Path adjudication): reads validated claim record; writes adjudication decision to CMS
- ADR-6 (clinical pre-screening): reuses IDP extraction pipeline for unstructured clinical documentation

**Wave 3 — Continued reuse (Month 7+):**
- ADR-9 (denial letters): reads claim record and denial rationale from CMS; writes denial communication
- ADR-8 (payment): reads approved adjudication outcome; triggers payment engine via CMS event

### Integration Reuse Matrix

| Integration / Asset | ADR-1 (Intake) | ADR-4 (Triage) | ADR-2 (Elig.) | ADR-3 (Coding) | ADR-5 (Fast Path) | ADR-6 (Pre-Screen) | ADR-9 (Denial) | ADR-8 (Payment) |
|--------------------|:--------------:|:--------------:|:-------------:|:--------------:|:-----------------:|:-----------------:|:--------------:|:---------------:|
| CMS read/write API [A12] | **✓ Build** | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| Normalized claim record schema | **✓ Build** | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| EDI 837 parser | **✓ Build** | — | — | — | — | — | — | — |
| IDP extraction pipeline | **✓ Build** | — | — | — | — | ✓ Reuse | — | — |
| SLA-aware queue module [A17] | **✓ Build** | ✓ Reuse | — | — | ✓ Reuse | ✓ Reuse | — | — |
| Audit log store | **✓ Build** | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| Clinical classification model | — | ✓ Build (ADR-4) | — | — | — | ✓ Reuse | — | — |
| Clinical criteria codebook [A15] | — | ✓ Build (ADR-4) | — | — | — | ✓ Reuse | — | — |
| Shadow evaluation pipeline | — | ✓ Build (ADR-4) | — | — | — | — | — | — |

**Maximising the matrix:** The CMS API, normalized claim record, and audit log are shared across all eight agents. The IDP extraction pipeline built for non-EDI intake in ADR-1 avoids a duplicate build in ADR-6 — both deal with unstructured document inputs. Every integration that ADR-1 resolves in Wave 1 is a Wave 2 acceleration.

### Critical Path Note

ADR-1 is a prerequisite for ADR-4. The clinical triage shadow pipeline ingests normalized claim records — it cannot run until ADR-1's CMS integration and claim record schema are in place. Wave 1 build order: ADR-1 intake pipeline → ADR-4 shadow mode wiring. The two can develop concurrently in sprint, but ADR-4 shadow evaluation cannot begin until ADR-1 is delivering records to CMS.

---

*See `specs/assumptions.md` for full definitions of [A4], [A7], [A12], [A14], [A17], [A21], [U1].*  
*See `specs/volume-×-value-analysis.md` Section 4 for HITL cost derivation and build cost allocation.*  
*Shared entities (CMS API, normalized record schema, reuse matrix) are consistent with `specs/04b-capability-spec-triage.md`.*
