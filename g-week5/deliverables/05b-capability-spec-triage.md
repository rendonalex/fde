# Capability Specification: ADR-2 — Medical Triage Agent

**Document Version**: 1.0  
**Date**: 2026-06-01  
**Project**: Helix Therapeutics Agentic Adverse Event Triage System  
**ADR**: ADR-2 — Medical Triage Agent (Seriousness, Expectedness, Reportability)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Agent Purpose](#agent-purpose)
3. [Agent Activity Catalog](#agent-activity-catalog)
4. [Autonomy Matrix](#autonomy-matrix)
5. [Entity Definitions](#entity-definitions)
6. [System and Data Inventory](#system-and-data-inventory)
7. [Context Engineering Design](#context-engineering-design)
8. [Compounding Roadmap](#compounding-roadmap)
9. [Validation Design](#validation-design)
10. [Integration Contracts](#integration-contracts)

---

## Executive Summary

**ADR-2** is an agent-led medical triage system that classifies AE seriousness per ICH E2A criteria, assesses expectedness against product Reference Safety Information (RSI), recommends reportability per FDA 21 CFR 314.80 and multi-jurisdictional rules, and generates machine-readable audit trails with chain-of-thought reasoning and span-level citations. The medical safety officer (MSO) reviews 100% of recommendations and makes final reportability decisions (non-negotiable per CMO mandate).

**Value Proposition**:
- Reduces per-case medical triage time from 30-35 min → 10-15 min agent processing + 15 min MSO review (total 25-30 min, 20-25% reduction)
- MSO accepts 88% of recommendations as-is, revises 12% for edge cases [A9]
- Automates audit trail generation (0% baseline → 100% machine-generated with FDA-ready span citations per [A10])
- Standardizes ICH E2A classification logic across all cases (reduces MSO-to-MSO variance)

**Delegation Archetype**: Agent-led + MSO Sign-Off

**Expected Outcomes**:
- 100% of cases receive seriousness classification, expectedness signal, and reportability recommendation with CoT reasoning
- 88% of recommendations accepted by MSO as-is (12% revised for clinical judgment edge cases)
- 100% audit trail completeness (span-level citations, CoT reasoning, rule-based justification for FDA inspection)
- 15-day compliance improvement from 92% → 99.5% (combined with ADR-1 queue acceleration)

**Integration Dependencies**:
- PV case management system API (read `AECasePackage` from ADR-1, write `TriageRecommendation`) [A16]
- Product RSI/CCSI database (retrieve safety profiles for Solivian, Tezarimab, Phaedora)
- MedDRA API (hierarchy queries for expectedness term matching)
- Audit Trail Store (write classification reasoning, span citations, timestamps)

---

## Agent Purpose

### Agent Name
Medical Triage Agent (ADR-2)

### Job to be Done
Classify AE seriousness per ICH E2A criteria, assess expectedness against product Reference Safety Information (RSI) with MedDRA hierarchy matching, recommend reportability per FDA 21 CFR 314.80 and multi-jurisdictional rules (EMA, MHRA, PMDA), generate chain-of-thought reasoning with span-level citations, and produce machine-readable audit trail for medical safety officer review and FDA inspection readiness.

### Business Context
Pharmacovigilance medical triage for Helix Therapeutics' three marketed products (Solivian, Tezarimab, Phaedora). Current manual medical triage consumes 30-35 min per case (40-47% of 75-min baseline per [A1]). Medical safety officers apply ICH E2A criteria, cross-reference product RSI for expectedness, and determine reportability per FDA regulations. This work is rule-bound but not automated — requires medical terminology reasoning, MedDRA hierarchy matching, and multi-jurisdictional regulatory knowledge. Dr. Carmichael (CMO) mandate: "We are not asking AI to make the reportability decision. That's our medical safety officer's call. But if AI can do the synthesis and the classification recommendation in 5 minutes instead of 60, the safety officer can focus on the medical assessment."

### Primary Objectives

1. **Seriousness classification**: Apply ICH E2A criteria (death, life-threatening, hospitalization, disability, congenital anomaly, other medically important) to AE description with CoT reasoning and span-level citations. Conservative fallback: when ambiguous, classify as serious (over-reporting is safer than under-reporting).

2. **Expectedness assessment**: Match AE term to product RSI/CCSI using MedDRA hierarchy (exact, synonym, broader, narrower term relationships). Flag novel AE terms (not in RSI) as unexpected with confidence 0.0 for MSO deep review. Handle term specificity variance (e.g., "Stevens-Johnson syndrome" vs. "rash").

3. **Reportability recommendation**: Apply FDA 21 CFR 314.80 logic (serious + unexpected → 15-day expedited reporting) and multi-jurisdictional rules (EMA, MHRA, PMDA). Include causality assessment context (but recommend expedited reporting for serious-unexpected regardless of causality per FDA guidance). Generate rule-based justification with regulatory citations.

4. **Audit trail generation**: Produce machine-readable audit trail with span-level citations (which text in source report supports each classification), CoT reasoning (step-by-step logic), and regulatory rule references. 100% completeness required for FDA inspection per [A10].

5. **MSO decision support**: Present synthesis (classification + reasoning + citations) in structured format for MSO review within 15 minutes. MSO reviews all recommendations, accepts 88% as-is, revises 12% for clinical judgment edge cases [A9].

### KPIs

| Metric | Target | Acceptable Ceiling | Measurement |
|--------|--------|-------------------|-------------|
| **Seriousness classification accuracy** (vs. MSO adjudication) | ≥96% | ≥90% | Audit sample: 50 cases monthly |
| **Expectedness signal precision** (flagged unexpected that are truly unexpected per RSI) | ≥85% | ≥80% | MSO review: serious-unexpected cases |
| **Reportability recommendation acceptance** (MSO accepts as-is) | ≥88% | ≥80% | Track MSO override rate weekly |
| **Throughput** | 10-15 min per case (agent processing) | ≤20 min | Median processing time |
| **Cost per case** | $23.22 (token + MSO review weighted) | ≤$30 | Track token usage + MSO hours |
| **Audit trail completeness** | 100% (all classifications have span citations + CoT reasoning) | 100% | Automated schema validation |
| **Novel AE term detection** | 100% (all novel terms flagged for MSO deep review) | 100% | Zero false negatives on novel terms |

### Failure Modes

| Failure Mode | Consequence | Recovery Path |
|-------------|-------------|---------------|
| **False-negative seriousness** (serious AE classified as non-serious) | 15-day reporting miss → FDA compliance violation → patient safety risk | Conservative fallback: ambiguous cases → classify as serious. MSO reviews 100% of recommendations (safety net). Weekly audit: 5% spot-check for systematic errors. |
| **False-negative expectedness** (unexpected AE flagged as expected) | 15-day reporting miss → FDA compliance violation | Conservative fallback: novel AE terms (not in RSI) → flag as unexpected with confidence 0.0. MSO reviews all serious-unexpected recommendations. |
| **Multi-jurisdictional reportability miss** (FDA-only recommendation, misses EMA/PMDA requirement) | Global compliance failure in non-U.S. markets | Codify all global requirements in system prompt (FDA, EMA, MHRA, PMDA). Carolina Núñez-Reyes (VP Regulatory Affairs) validates multi-jurisdictional logic in Week 1. |
| **Overconfidence on "other medically important" criterion** (agent classifies ambiguous case as serious without MSO review) | Over-reporting (acceptable per [A4]) but wastes MSO time | Agent flags low-confidence seriousness (<0.70) for MSO deep review (~10-15% of cases per [A12]). |
| **Causality assessment misinterpretation** (agent recommends "not reportable" based on "unrelated" causality) | 15-day reporting miss (FDA requires expedited reporting for serious-unexpected regardless of causality) | System prompt: "Always recommend expedited reporting for serious-unexpected, regardless of causality. Include causality in reasoning but do not override reportability logic." |

### Delegation Archetype
**Agent-led + MSO Sign-Off**

**Rationale**: ICH E2A criteria, MedDRA hierarchy matching, and FDA reportability rules are explicitly codifiable. Agent can apply rules systematically with CoT reasoning and span-level citations. However, judgment-dependent criteria ("other medically important," term specificity variance, causality influence) require medical interpretation. High compliance risk requires MSO final sign-off. Per CMO mandate (Dr. Carmichael): "We are not asking AI to make the reportability decision. That's our medical safety officer's call."

**Human Oversight Model**:
- **MSO Reviews All Recommendations**: Agent outputs `TriageRecommendation` (seriousness classification, expectedness signal, reportability recommendation, CoT reasoning, span-level citations). MSO reviews all 6,000 cases annually but accepts 88% as-is, revises 12% for edge cases per [A9].
- **Confidence Signaling**: Agent flags low-confidence cases (ambiguous seriousness, novel AE term, multi-jurisdictional complexity) for MSO deep review (estimated ~10-15% of cases per [A12]).
- **Override Authority**: MSO can override any agent classification with clinical judgment. Override is logged in audit trail with MSO reasoning.
- **Audit**: Medical safety officer spot-checks 5% of agent recommendations monthly for systematic error patterns.

### Escalation Triggers

**Agent → MSO Deep Review (Flagged for Complex Medical Judgment)**:
- Seriousness confidence <0.70 (ambiguous "other medically important" criterion, requires clinical interpretation)
- Novel AE term (not in product RSI, not in MedDRA hierarchy) → unexpected with confidence 0.0
- Multi-jurisdictional complexity (case requires EMA + PMDA + MHRA reportability assessment with rule conflicts)
- Causality "unrelated" + serious-unexpected (agent recommends expedited reporting, but MSO should verify causality reasoning)

**Agent → MSO Standard Review (All Cases)**:
- MSO reviews 100% of recommendations per CMO mandate (non-negotiable)
- MSO SLA: review within 24 hours (all cases), within 4 hours (serious-unexpected flagged by agent)
- MSO accepts 88% as-is, revises 12% for clinical judgment edge cases

**Agent → Ops Alert**:
- Product RSI read failure (file not found, malformed data) → alert ops immediately, block processing
- MedDRA API failure (3 consecutive retries exhausted) → alert ops, use extracted AE term as-is + flag for manual MedDRA coding
- Audit trail write failure → buffer locally, emit `AUDIT_TRAIL_WRITE_FAILED` event, alert ops

**Agent → Exception Queue**:
- Precondition failure: `AECasePackage` from ADR-1 has `extraction_status != AUTO_COMPLETE` → return to ADR-1 queue with error
- Schema validation failure: `AECasePackage` missing required fields (patient, suspect_drug, ae_description) → route to exception queue

---

## Agent Activity Catalog

The table below enumerates every micro-task ADR-2 performs, with delegation level, data required, tool required, and risk level.

| # | Task | Type | Delegation Level | Data Required | Tool Required | Risk Level |
|---|------|------|-----------------|---------------|---------------|------------|
| 3.1 | Retrieve ICH E2A criteria (death, life-threatening, hospitalization, disability, congenital anomaly, other medically important) | Retrieval | Fully agentic | ICH E2A guideline (codified in system prompt) | None (static reference) | Low |
| 3.2 | Match AE description to ICH E2A death criterion | Decision | Fully agentic | AE outcome ("fatal," "death") | None (LLM reasoning) | Medium |
| 3.3 | Match AE description to life-threatening criterion | Decision | Agent-led + MSO deep review on ambiguous | AE narrative ("required intervention to prevent death") | None (LLM reasoning) | High |
| 3.4 | Match AE description to hospitalization criterion | Decision | Fully agentic | AE outcome ("hospitalized," "admission") | None (LLM reasoning) | Medium |
| 3.5 | Match AE description to disability criterion | Decision | Agent-led + MSO deep review on ambiguous | AE outcome ("persistent disability") | None (LLM reasoning) | High |
| 3.6 | Match AE description to congenital anomaly criterion | Decision | Fully agentic | Patient demographics (newborn), AE description ("birth defect") | None (LLM reasoning) | Medium |
| 3.7 | Match AE description to "other medically important" criterion | Decision | Agent-led + MSO deep review (confidence <0.70) | AE narrative (medical intervention required?) | None (LLM reasoning + clinical judgment) | High |
| 3.8 | Generate seriousness classification reasoning with CoT | Generation | Fully agentic | ICH E2A criteria match results | None (LLM reasoning) | Low |
| 3.9 | Generate span-level citations for seriousness classification | Generation | Fully agentic | AE narrative text, extracted AE description | None (LLM span detection) | Low |
| 4.1 | Retrieve product RSI/CCSI for suspect drug | Retrieval | Fully agentic | Suspect drug name, product database (Solivian/Tezarimab/Phaedora RSI) | Product RSI database read (file or API) | Medium |
| 4.2 | Match AE term to RSI-listed terms (exact match) | Decision | Fully agentic | AE MedDRA PT, RSI AE term list | None (string comparison) | Low |
| 4.3 | Query MedDRA hierarchy for synonym/broader/narrower term relationships | Retrieval | Fully agentic | AE MedDRA PT, RSI AE terms | MedDRA API (hierarchy query) | Medium |
| 4.4 | Match AE term to RSI via MedDRA hierarchy (broader/narrower/synonym) | Decision | Agent-led + MSO review on ambiguous | MedDRA hierarchy results, RSI AE terms | None (LLM reasoning on hierarchy relationships) | High |
| 4.5 | Handle term specificity variance (e.g., "Stevens-Johnson syndrome" vs. "rash") | Decision | Agent-led + MSO deep review | MedDRA hierarchy (LLT → PT → HLT → SOC), clinical reasoning on term severity | None (LLM reasoning + clinical judgment) | High |
| 4.6 | Flag novel AE term (not in RSI, not in MedDRA hierarchy) | Decision | Fully agentic (conservative fallback: flag as unexpected) | AE term, RSI term list, MedDRA query result | None (logic check) | Medium |
| 4.7 | Generate expectedness signal reasoning with CoT | Generation | Fully agentic | RSI match results, MedDRA hierarchy path | None (LLM reasoning) | Low |
| 4.8 | Generate span-level citations for expectedness assessment | Generation | Fully agentic | RSI text, AE description text | None (LLM span detection) | Low |
| 5.1 | Apply FDA 21 CFR 314.80 logic (serious + unexpected → 15-day expedited) | Decision | Fully agentic | Seriousness classification, expectedness signal | None (rule-based logic) | Medium |
| 5.2 | Apply EMA reportability rules | Decision | Fully agentic | Seriousness, expectedness, product marketing in EU | None (rule-based logic) | Medium |
| 5.3 | Apply MHRA reportability rules (UK) | Decision | Fully agentic | Seriousness, expectedness, product marketing in UK | None (rule-based logic) | Medium |
| 5.4 | Apply PMDA reportability rules (Japan) | Decision | Agent-led + Carolina Núñez-Reyes validation | Seriousness, expectedness, product marketing in Japan | None (rule-based logic with global variance) | Medium |
| 5.5 | Account for causality assessment influence on reportability | Reasoning | Agent-led + MSO review | Causality assessment (if available), FDA guidance (causality does not exempt serious-unexpected from expedited reporting) | None (LLM reasoning) | High |
| 5.6 | Generate reportability recommendation with rule-based justification | Generation | Fully agentic | Seriousness, expectedness, reportability rules (FDA/EMA/MHRA/PMDA), causality | None (LLM reasoning + regulatory citation) | Low |
| 5.7 | Generate span-level citations for reportability recommendation | Generation | Fully agentic | Regulatory rule text (FDA 21 CFR 314.80, EMA Directive 2001/83/EC) | None (LLM span detection from system prompt) | Low |
| 6.1 | Assemble `TriageRecommendation` entity (structured JSON) | Generation | Fully agentic | All classification results, reasoning, citations | None (JSON serialization) | Low |
| 6.2 | Write audit trail to audit trail store | Action | Agentic + retry on failure | `TriageRecommendation` JSON, case ID, timestamp | Audit Trail Store write API | Medium |
| 6.3 | Buffer audit trail locally on write failure | Action | Fully agentic (failure handling) | `TriageRecommendation` JSON | Local file buffer | Low |
| 6.4 | Route `TriageRecommendation` to MSO review queue | Action | Fully agentic | `TriageRecommendation` JSON, MSO queue | PV case management API write or queue system | Medium |
| 6.5 | Emit classification complete event | Action | Fully agentic | Event type, case ID, timestamp, confidence scores | Event log | Low |

**Task Type Legend**:
- **Retrieval**: Fetch and return data from external source
- **Decision**: Choose between outcomes based on rules or reasoning
- **Reasoning**: Apply multi-step logic or clinical judgment
- **Generation**: Produce structured output (JSON, citations, CoT reasoning)
- **Action**: Write to system, trigger process, or route to queue

---

## Autonomy Matrix

This matrix defines what ADR-2 decides alone vs. what requires human approval or review.

### AGENT DECIDES ALONE (No MSO Review Required Before Action)

- **Explicit ICH E2A criteria matching** (death, hospitalization, congenital anomaly) → classify as serious (no ambiguity)
- **Exact RSI term matching** (AE MedDRA PT is listed verbatim in product RSI) → classify as expected
- **FDA 21 CFR 314.80 logic** (serious + unexpected → 15-day expedited reporting) → apply rule deterministically
- **MedDRA API query** for hierarchy matching (synonym, broader, narrower term relationships)
- **Span-level citation generation** (link classification to source text location)
- **Audit trail write** (store classification reasoning, CoT, citations in audit trail store)
- **Conservative fallback logic**:
  - Novel AE term (not in RSI) → flag as unexpected with confidence 0.0
  - Ambiguous seriousness (confidence <0.70) → override to serious + flag for MSO deep review
  - Causality "unrelated" but serious-unexpected → recommend expedited reporting (per FDA guidance)

### AGENT PROPOSES, MSO REVIEWS ALL RECOMMENDATIONS

**All cases receive MSO review** (100% of 6,000 cases annually per CMO mandate, non-negotiable):
- MSO reviews agent `TriageRecommendation` (seriousness classification, expectedness signal, reportability recommendation, CoT reasoning, span citations)
- MSO accepts 88% as-is, revises 12% for clinical judgment edge cases per [A9]
- MSO SLA: review within 24 hours (all cases), within 4 hours (serious-unexpected flagged by agent)
- MSO override logged in audit trail with MSO reasoning (FDA inspection requirement)

**[CURVEBALL - FDA May 2026 Guidance]** Regulatory Requirements Now Mandate MSO Review:
- **FDA Requirement 2 (Human Review of All Serious AE Classifications)**: "Any AE that the AI system classifies as serious per ICH E2A criteria must receive human safety physician review and signature before the seriousness classification is final." MSO reviews 100% of ADR-2 recommendations (already in design, now regulatory requirement). MSO must document **substantive review** (not rubber stamp) — audit record must capture MSO rationale for accept/modify/override.
- **FDA Requirement 4 (Expectedness Determination Boundary)**: "AI-assisted expectedness signals may inform but may not substitute for the marketing-authorisation holder's determination of expectedness against the Reference Safety Information. Final expectedness determination remains the safety physician's responsibility. AI-assisted recommendations of 'unexpected' must include the specific RSI section consulted and the specific span in the case from which the unexpectedness is inferred." (ADR-2 generates expectedness signal with RSI term matched + span citations, MSO makes final determination — already in design, now mandatory per FDA.)
- **FDA Requirement 5 (15-day Clock Attribution)**: "When AI-assisted intake first receives an AE meeting expedited reporting criteria, the 15-day FDA reporting clock is attributed to the timestamp of AI receipt, regardless of when the human safety physician opens the case. Architectural design must ensure that AI receipt timestamps are preserved as the clock-start, not human-open timestamps." (`received_at` timestamp is immutable from ADR-1 intake — already in design, now regulatory requirement.)

**Cases flagged for MSO deep review** (~10-15% per [A12]):
- Ambiguous "other medically important" criterion (confidence <0.70)
- Novel AE term (not in RSI, confidence 0.0)
- Term specificity variance ("Stevens-Johnson syndrome" vs. "rash" — is this expected or unexpected?)
- Multi-jurisdictional complexity (EMA + PMDA + MHRA rule conflicts)
- Causality "unrelated" but serious-unexpected (MSO verifies causality reasoning before sign-off)

### MSO DECIDES (Agent Supports, Does Not Decide)

**Final reportability determination** (agent provides recommendation, MSO signs):
- Agent outputs: seriousness classification, expectedness signal, reportability recommendation (15-day expedited / periodic / non-reportable), rule-based justification per FDA 21 CFR 314.80
- MSO: reviews recommendation, applies clinical judgment, makes final reportability decision
- MSO signature required for all reportability determinations (legal accountability, regulatory requirement)

**Medical assessment authoring** (agent does not write, MSO writes):
- Agent outputs: classification synthesis (seriousness + expectedness + reportability + reasoning)
- MSO: writes medical assessment narrative for FDA MedWatch 3500A form (causality, clinical interpretation, significance)
- Dr. Iyer: "I do not want AI to write my medical assessment. I want AI to do the boring synthesis so I can write the assessment."

**Causality assessment final determination** (agent surfaces signal, MSO decides):
- Agent outputs: causality assessment context (temporal relationship, concomitant meds, medical history) with reasoning
- MSO: makes causality determination (certain, probable/likely, possible, unlikely, unrelated) based on WHO-UMC criteria

---

### AGENT TRIGGERS ESCALATION (FDA Signal-Detection Requirement)

**[CURVEBALL - FDA May 2026 Guidance]** Added per FDA Requirement 3 (Signal-Detection Escalation):

**FDA Requirement 3 (Signal-Detection Escalation)**: "When the AI system identifies that an incoming AE matches a pattern with three or more cases of the same MedDRA Preferred Term and same suspect product in a rolling 90-day window, the system must escalate the case for safety physician signal-detection review within 5 business days of the third case."

**Architectural Impact**:
- **Pattern Detection Query**: After each ADR-2 classification, agent queries PV case history:
  - Query: `GET /api/v1/cases?product={product_name}&meddra_pt={ae_meddra_code}&date_range=90days`
  - If case count ≥ 3 (including current case) → pattern detected
- **Escalation Event**: Emit `SIGNAL_DETECTION_ESCALATION` event with case_id, pattern details (product + MedDRA PT), case count
- **MSO Signal-Detection Queue**: Route to separate MSO signal-detection review queue (distinct from standard MSO review queue) with **5-business-day SLA**
- **MSO Investigation**: MSO investigates aggregate pattern:
  - Is this a new safety signal not in product RSI?
  - Does product RSI need updating?
  - Does this require aggregate reporting to FDA beyond individual 15-day reports?
  - Should product label be revised?

**New Data Contract** (ADR-2 outputs):
- `signal_detection_flag`: boolean (true if 3-cases-in-90-days pattern detected)
- `signal_pattern`: object (product name, MedDRA PT, case count, date range) if flag true

**Escalation Triggers**:
- Pattern detected (≥3 cases same product + MedDRA PT in 90 days) → route to MSO signal-detection queue
- MSO SLA: 5 business days for signal-detection review (per FDA Req 3)

---

## Entity Definitions

This section provides complete data models for all entities created or manipulated by ADR-2.

### TriageRecommendation

**Purpose**: Structured output from ADR-2 medical triage, input to MSO review queue. Contains seriousness classification, expectedness signal, reportability recommendation with CoT reasoning and span citations.

**Attributes**:
- `case_id`: UUID, foreign key to AECasePackage, immutable (links to ADR-1 extraction)
- `seriousness_classification`: nested object (SeriousnessClassification, see below), required
- `expectedness_signal`: nested object (ExpectednessSignal, see below), required
- `reportability_recommendation`: nested object (ReportabilityRecommendation, see below), required
- `mso_flags`: nested object (MSOFlags, see below), required
- `audit_trail`: nested object (AuditTrail, see below), required
- **[CURVEBALL - FDA May 2026 Guidance]** `signal_detection_flag`: boolean, required, default false (true if 3-cases-in-90-days pattern detected per FDA Req 3)
- **[CURVEBALL - FDA May 2026 Guidance]** `signal_pattern`: nested object (SignalPattern, see below), nullable (only populated if `signal_detection_flag == true`)
- **[CURVEBALL - FDA May 2026 Guidance]** `model_version_adr2`: string, required, immutable, set at classification time (e.g., "ADR-2 v1.0.3") (FDA Req 1: model version tracking)
- `created_at`: ISO 8601 timestamp, set on creation, immutable
- `created_by`: string constant `ADR-2`, immutable
- `mso_reviewed_at`: ISO 8601 timestamp, nullable, set when MSO completes review
- `mso_reviewed_by`: string (MSO user ID), nullable, set when MSO signs off
- `mso_override`: boolean, default false, set true if MSO overrides agent recommendation
- `mso_override_reason`: string, nullable, max 1000 characters (MSO clinical judgment justification for override)
- **[CURVEBALL - FDA May 2026 Guidance]** `mso_action`: enum [`accepted`, `modified`, `overridden`], nullable, set when MSO reviews (FDA Req 1: human action tracking)
- **[CURVEBALL - FDA May 2026 Guidance]** `mso_rationale`: string, nullable, max 1000 characters (MSO substantive review documentation per FDA Req 2 — not rubber stamp)

**State Machine** (implicit via mso_reviewed_at field):
- Initial state: Created by ADR-2 (`mso_reviewed_at == null`)
- `mso_reviewed_at == null` → MSO review pending (routed to MSO queue)
- `mso_reviewed_at != null` → MSO review complete (MSO signed off, ready for reportability determination)
- Terminal state: MSO reviewed (no further ADR-2 processing)

**Validation Rules**:
- `case_id` must reference existing `AECasePackage` with `extraction_status == AUTO_COMPLETE`
- All nested objects (seriousness_classification, expectedness_signal, reportability_recommendation) must be present (required)
- `mso_reviewed_at` must be >= `created_at` (MSO review cannot precede agent processing)
- If `mso_override == true`, `mso_override_reason` must be non-null (MSO must document clinical judgment)
- **[CURVEBALL - FDA May 2026 Guidance]** If `signal_detection_flag == true`, `signal_pattern` must be non-null (pattern details required for MSO signal-detection review)
- **[CURVEBALL - FDA May 2026 Guidance]** If `mso_action == modified` or `mso_action == overridden`, `mso_rationale` must be non-null (MSO must document substantive review per FDA Req 2)

**Foreign Key Constraints**:
- `case_id` → `AECasePackage.case_id` (foreign key, on delete: restrict — cannot delete AECasePackage if TriageRecommendation exists)

**Cascade Behavior**:
- Deletion: soft-delete only (set `deleted_at` timestamp), never hard-delete (FDA audit requirement: 7-year retention)

---

### SeriousnessClassification (nested in TriageRecommendation)

**Attributes**:
- `serious`: boolean, required (true = serious per ICH E2A, false = non-serious)
- `criteria_matched`: array of enum values, required (empty array if non-serious)
  - Enum values: [`death`, `life_threatening`, `hospitalization`, `disability`, `congenital_anomaly`, `other_medically_important`]
- `reasoning`: string, required, max 2000 characters (CoT step-by-step reasoning for classification)
- `span_citations`: object, required (links each criterion to source text span in AE narrative)
  - Structure: `{ "criterion_name": "source_span" }` (e.g., `{ "hospitalization": "ae_narrative:45-67" }`)
- `confidence`: float, required, range [0.0, 1.0]

**Validation Rules**:
- If `serious == true`, `criteria_matched` must have at least one value (cannot be empty array)
- If `serious == false`, `criteria_matched` must be empty array
- `confidence` <0.70 triggers `mso_flags.deep_review_required == true` (ambiguous seriousness)
- `reasoning` must reference ICH E2A criteria (validation: contains at least one ICH E2A criterion keyword)
- `span_citations` must have citation for each criterion in `criteria_matched` array (100% audit trail completeness)

---

### ExpectednessSignal (nested in TriageRecommendation)

**Attributes**:
- `unexpected`: boolean, required (true = AE not in product RSI, false = AE is in RSI)
- `rsi_match`: enum [`exact`, `broader`, `narrower`, `synonym`, `none`], required
  - `exact`: AE MedDRA PT exactly matches RSI term
  - `broader`: RSI contains broader term (e.g., RSI has "rash", AE is "maculopapular rash")
  - `narrower`: RSI contains narrower term (rare, usually means AE is more general than RSI term)
  - `synonym`: AE term is synonym of RSI term per MedDRA hierarchy
  - `none`: No match (novel AE term, triggers `unexpected == true`, `confidence == 0.0`)
- `rsi_term_matched`: string, optional, max 200 characters (which RSI term matched, null if `rsi_match == none`)
- `reasoning`: string, required, max 2000 characters (CoT reasoning with MedDRA hierarchy path if hierarchy match)
- `span_citations`: object, required
  - Structure: `{ "rsi_term": "RSI_text_span", "ae_term": "ae_narrative_span" }`
- `confidence`: float, required, range [0.0, 1.0]

**Validation Rules**:
- If `unexpected == true` and `rsi_match == none`, `confidence` must be 0.0 (novel AE term → zero confidence, requires MSO deep review)
- If `unexpected == false`, `rsi_match` must be one of [`exact`, `broader`, `narrower`, `synonym`] (cannot be `none`)
- If `rsi_match == none`, `rsi_term_matched` must be null
- If `rsi_match != none`, `rsi_term_matched` must be non-null (which RSI term matched)
- `reasoning` must reference product RSI and MedDRA hierarchy (if applicable)
- `span_citations` must link to both RSI text and AE narrative (audit trail completeness)

---

### ReportabilityRecommendation (nested in TriageRecommendation)

**Attributes**:
- `recommendation`: enum [`15_DAY_EXPEDITED`, `PERIODIC`, `NON_REPORTABLE`], required
- `jurisdictions`: array of enum values, required (which regulators require expedited reporting)
  - Enum values: [`FDA`, `EMA`, `MHRA`, `PMDA`]
  - Empty array if `recommendation == PERIODIC` or `NON_REPORTABLE`
- `rule_justification`: string, required, max 1000 characters (FDA 21 CFR 314.80 citation, EMA Directive citation)
- `causality_context`: string, optional, max 1000 characters (causality assessment influence on reportability, if available)
- `reasoning`: string, required, max 2000 characters (CoT reasoning for reportability logic)
- `span_citations`: object, required
  - Structure: `{ "regulatory_rule": "system_prompt:FDA_21_CFR_314.80" }` (links to regulatory rule reference in system prompt)
- `confidence`: float, required, range [0.0, 1.0]

**Validation Rules**:
- If `seriousness_classification.serious == true` AND `expectedness_signal.unexpected == true`, `recommendation` must be `15_DAY_EXPEDITED` (per FDA 21 CFR 314.80)
- If `recommendation == 15_DAY_EXPEDITED`, `jurisdictions` must have at least one value (cannot be empty)
- If `recommendation == PERIODIC` or `NON_REPORTABLE`, `jurisdictions` must be empty array
- `rule_justification` must cite specific regulatory rule (validation: contains at least one regulatory citation like "FDA 21 CFR 314.80")
- `reasoning` must explain serious + unexpected → 15-day logic (if applicable)
- `causality_context` must clarify that causality does NOT override serious-unexpected reportability (per FDA guidance)

---

### MSOFlags (nested in TriageRecommendation)

**Attributes**:
- `deep_review_required`: boolean, required (true = MSO must perform deep review, false = standard review)
- `reason`: enum values (array), required if `deep_review_required == true`
  - Enum values: [`ambiguous_seriousness`, `novel_ae_term`, `term_specificity_variance`, `multi_jurisdictional_complexity`, `causality_unrelated`]
  - Empty array if `deep_review_required == false`

**Validation Rules**:
- If `seriousness_classification.confidence <0.70`, `deep_review_required == true` and `reason` includes `ambiguous_seriousness`
- If `expectedness_signal.rsi_match == none`, `deep_review_required == true` and `reason` includes `novel_ae_term`
- If `deep_review_required == true`, `reason` must have at least one value (cannot be empty)

---

### AuditTrail (nested in TriageRecommendation)

**Attributes**:
- `timestamp`: ISO 8601 timestamp, required (when ADR-2 completed classification)
- `agent_version`: string, required (e.g., "ADR-2 v1.0", for traceability if prompt changes) **[Note: superseded by `model_version_adr2` at parent TriageRecommendation level per FDA Req 1]**
- `regulatory_references`: array of strings, required (which regulations cited: "ICH E2A", "FDA 21 CFR 314.80", etc.)

**Validation Rules**:
- `timestamp` must be <= current_timestamp (cannot be future date)
- `agent_version` must match deployed ADR-2 version (validation: check against version registry)
- `regulatory_references` must include at least "ICH E2A" and "FDA 21 CFR 314.80" (minimum required for FDA inspection)

---

### SignalPattern (nested in TriageRecommendation)

**[CURVEBALL - FDA May 2026 Guidance]** Added per FDA Requirement 3 (Signal-Detection Escalation for 3-cases-in-90-days patterns).

**Purpose**: Captures aggregate AE pattern details for MSO signal-detection review when ≥3 cases of same product + MedDRA PT detected in rolling 90-day window.

**Attributes**:
- `product`: string, required (suspect drug product name, e.g., "Tezarimab")
- `meddra_pt`: string, required (MedDRA Preferred Term, e.g., "Hepatotoxicity")
- `meddra_code`: string, required (8-digit MedDRA PT code)
- `case_count`: integer, required, minimum 3 (total cases matching pattern including current case)
- `window_start`: ISO 8601 date, required (start of 90-day window)
- `window_end`: ISO 8601 date, required (end of 90-day window, typically current date)

**Validation Rules**:
- `case_count` must be >= 3 (signal detection only triggers at 3+ cases)
- `window_end` must be >= `window_start`
- Date range (`window_end` - `window_start`) should be <= 90 days (rolling 90-day window per FDA Req 3)
- Only populated when `signal_detection_flag == true`

---

### AECasePackage (read from ADR-1)

**ADR-2 Precondition**: Only processes `AECasePackage` with `extraction_status == AUTO_COMPLETE`.

**Validation on Read**:
- `extraction_status` must be `AUTO_COMPLETE` (if not, return error to ADR-1 queue)
- Required fields must be present: `patient`, `suspect_drug`, `ae_description`, `temporal`
- `suspect_drug.name` must match one of Helix marketed products (Solivian, Tezarimab, Phaedora) or have valid RxNorm code for product matching
- If validation fails, route to exception queue with error message

**See ADR-1 spec (Section: Entity Definitions) for complete AECasePackage data model.**

---

## System and Data Inventory

This section maps all data sources and systems ADR-2 requires, with access type, availability, gaps, and shared status (for compounding reuse).

| System / Data Source | Data Needed | Access Type | Availability | Auth Method | Gap / Risk | Shared |
|---------------------|-------------|-------------|--------------|-------------|------------|--------|
| **PV Case Management System** | Read `AECasePackage` from ADR-1, write `TriageRecommendation` | Read/Write | Assumed available [A16] (Week 1 validation required) | OAuth 2.0 (assumed) | Week 1 Go/No-Go: confirm API endpoints, SLA. ADR-2 requires read access to ADR-1 output. | ✅ Shared with ADR-1 |
| **Product RSI/CCSI Database** | Retrieve safety profile (AE term list) for suspect drug (Solivian, Tezarimab, Phaedora) | Read | Mock data: structured markdown files (Solivian_RSI.md, Tezarimab_RSI.md, Phaedora_RSI.md) in `mock-data/product-information/` | File read (local) | Prototype: file read. Production: database query or API (versioned RSI per label update ~1-2x/year). | ✅ Shared with future agents (multi-product expansion) |
| **MedDRA API** | AE term hierarchy queries (PT → HLT → SOC, synonym/broader/narrower relationships) | Read | Licensed (subscription required, assumed available per [A16]) | API key (assumed) | Week 1 validation: confirm license, API access. Fallback: local MedDRA database export (MSSQL). | ✅ Shared with ADR-1 |
| **ICH E2A Criteria** | Seriousness classification rules (death, life-threatening, hospitalization, disability, congenital anomaly, other medically important) | Read | Public ICH guideline (codified in system prompt) | None (static reference) | No gap. ICH E2A stable since 1994 (last revision 2010). | ✅ Shared with all PV agents |
| **FDA 21 CFR 314.80** | Reportability rules (serious + unexpected → 15-day expedited) | Read | Public FDA regulation (codified in system prompt) | None (static reference) | No gap. FDA rule stable (last revision 2012). | ✅ Shared with all PV agents |
| **EMA Directive 2001/83/EC** | EU reportability rules (serious + unexpected → 15-day expedited to EMA) | Read | Public EMA regulation (codified in system prompt) | None (static reference) | No gap. EMA rule aligned with FDA (ICH E2A harmonization). | ✅ Shared with all PV agents |
| **MHRA Guidance** | UK reportability rules (similar to EMA, post-Brexit variance) | Read | Public MHRA guidance (codified in system prompt) | None (static reference) | Week 1 validation: confirm no post-Brexit rule changes with Carolina Núñez-Reyes. | ✅ Shared with all PV agents |
| **PMDA Guidance** | Japan reportability rules (seriousness criteria differ from ICH E2A) | Read | Public PMDA guidance (codified in system prompt, translated) | None (static reference) | Week 1 validation: confirm PMDA-specific criteria with Carolina Núñez-Reyes. Risk: rule translation errors. | ✅ Shared with all PV agents |
| **Audit Trail Store** | Write classification reasoning, CoT, span citations, timestamps | Write | Buildable (shared with ADR-1, same schema) | Internal | Build: 2 days (reuses ADR-1 asset). Schema: case_id, classification_type (seriousness/expectedness/reportability), decision, reasoning, span_citations, confidence, timestamp. | ✅ Shared with ADR-1 |
| **MSO Review Queue** | Route `TriageRecommendation` to MSO for review + sign-off | Write | Buildable (queue system or PV case management workflow) | Internal | Build: 1 day. UI for MSO to review agent recommendations, override with clinical judgment, sign reportability determination. | ✅ Shared with future agents (any MSO review workflow) |

**Shared Asset Summary**:
- **5 shared integrations** (reused from ADR-1): PV case management API, MedDRA API, Product RSI Database, Audit Trail Store
- **5 ADR-2-specific assets** (codified in system prompt, no external API): ICH E2A Criteria, FDA 21 CFR 314.80, EMA Directive 2001/83/EC, MHRA Guidance, PMDA Guidance
- **1 ADR-2-specific integration**: MSO Review Queue (UI + workflow)

**Week 1 Go/No-Go Validations**:
- PV case management API: confirm ADR-2 can read `AECasePackage` from ADR-1 output (schema alignment)
- Product RSI database: confirm file read access to Solivian_RSI.md, Tezarimab_RSI.md, Phaedora_RSI.md (or production API endpoint)
- MedDRA API: confirm hierarchy query endpoints (PT → HLT → SOC, synonym lookup)
- Multi-jurisdictional reportability: validate MHRA (post-Brexit) and PMDA (Japan-specific criteria) rules with Carolina Núñez-Reyes

---

## Context Engineering Design

### Memory Architecture

ADR-2 is stateless per case (no multi-turn conversation, no customer history). Context is single-invocation per case.

| Memory Type | Content | Storage | Lifecycle |
|-------------|---------|---------|-----------|
| **In-context** (per invocation) | `AECasePackage` from ADR-1 (patient, drug, AE narrative, temporal relationships), ICH E2A criteria, product RSI for suspect drug, MedDRA hierarchy results | Prompt window (input + output tokens) | Per case (single invocation) |
| **Semantic** (static reference) | ICH E2A criteria (6 seriousness types), FDA/EMA/MHRA/PMDA reportability rules, MedDRA hierarchy matching logic, confidence threshold rules | System prompt (version-controlled) | Updated on regulatory rule change (~annually) or prompt refinement |
| **Procedural** (static instructions) | Classification logic, CoT reasoning structure, span citation generation, conservative fallback rules, MSO escalation triggers | System prompt (version-controlled) | Updated on prompt refinement |
| **Episodic** (not used) | No customer history or prior case memory required | N/A | N/A |

### Retrieval Strategy

ADR-2 uses **targeted retrieval** (not RAG vector search) for specific data sources:

1. **Product RSI retrieval** (per case):
   - **Trigger**: After `AECasePackage` ingestion, extract suspect drug name
   - **Query**: File read `mock-data/product-information/{product_name}_RSI.md` (prototype) or API call `GET /api/v1/products/{product_id}/rsi` (production)
   - **Target**: Product-specific AE term list (Solivian RSI has ~150 AE terms, Tezarimab RSI has ~120 terms, Phaedora RSI has ~100 terms per industry norms)
   - **Relevance**: Exact match on AE MedDRA PT first, then hierarchy matching via MedDRA API
   - **Cost**: Single file read per case (negligible) or single API call (~50ms latency)

2. **MedDRA hierarchy query** (conditional):
   - **Trigger**: If AE MedDRA PT not found in RSI (exact match fails), query MedDRA hierarchy for synonym/broader/narrower relationships
   - **Query**: `GET /api/v1/meddra/hierarchy?pt={ae_meddra_pt}&levels=HLT,SOC` + `GET /api/v1/meddra/synonyms?pt={ae_meddra_pt}`
   - **Target**: MedDRA hierarchy path (PT → HLT → SOC), synonym list (Preferred Term alternatives)
   - **Relevance**: Check if any RSI term is a parent (broader term), child (narrower term), or synonym of AE term
   - **Cost**: 1-2 API calls per case (10-15% of cases require hierarchy matching per [A13])

**No RAG vector search**: RSI term list is small (~100-150 terms per product), structured (MedDRA PT codes), and exact-match-first. Vector embedding adds cost without accuracy benefit.

### Prompt / Context Engineering Principles

**System Prompt Structure** (ADR-2):

```
1. ROLE AND PURPOSE
   "You are a medical triage agent for Helix Therapeutics pharmacovigilance system. Your job: classify
   AE seriousness per ICH E2A criteria, assess expectedness against product RSI with MedDRA hierarchy
   matching, recommend reportability per FDA 21 CFR 314.80 and multi-jurisdictional rules (EMA, MHRA,
   PMDA), and generate CoT reasoning with span-level citations for medical safety officer review."

2. SCOPE (What you may and may not do)
   - MAY: Classify seriousness (serious/non-serious) with ICH E2A criteria matching. Assess expectedness
     (expected/unexpected) with RSI + MedDRA hierarchy. Recommend reportability (15-day expedited / periodic
     / non-reportable) with FDA/EMA/MHRA/PMDA rule application. Generate CoT reasoning and span citations.
     Flag low-confidence cases for MSO deep review.
   - MAY NOT: Make final reportability decision (MSO signs). Write medical assessment narrative. Make
     causality determination (MSO decides). Contact reporters or regulators.

3. INPUT SCHEMA (`AECasePackage` from ADR-1)
   {
     "case_id": "UUID",
     "received_at": "ISO 8601 timestamp",
     "patient": { "age": int, "sex": "M|F|Unknown", ... },
     "suspect_drug": { "name": string, "dose": string, "indication": string, "rxnorm_code": string, ... },
     "ae_description": { "narrative": string, "meddra_pt": string, "meddra_code": string, "onset_date": string, "outcome": string, ... },
     "temporal": { "drug_start_date": string, "ae_onset_date": string, ... },
     "concomitant_meds": [ { "name": string, ... } ],
     "medical_history": { "narrative": string, ... },
     "span_citations": { ... }
   }

4. ICH E2A SERIOUSNESS CRITERIA (Apply to AE description)
   - **Death**: AE outcome is "fatal" or "death" → SERIOUS
   - **Life-threatening**: AE "required intervention to prevent death" or "patient at immediate risk of death" → SERIOUS
   - **Hospitalization**: AE resulted in "hospitalization" or "prolonged existing hospitalization" → SERIOUS
   - **Disability**: AE resulted in "persistent or significant disability/incapacity" → SERIOUS
   - **Congenital anomaly**: AE is "congenital anomaly or birth defect" in newborn → SERIOUS
   - **Other medically important**: AE "required medical intervention to prevent serious outcome" (e.g., severe
     allergic reaction requiring epinephrine, seizure requiring anticonvulsant) → SERIOUS (requires clinical judgment)
   - If none of above criteria met → NON-SERIOUS

   **Conservative fallback**: If ambiguous (especially "other medically important"), classify as SERIOUS and flag
   for MSO deep review with confidence <0.70.

5. EXPECTEDNESS ASSESSMENT (Match AE term to product RSI)
   **Step 1**: Retrieve product RSI for suspect drug (Solivian_RSI.md / Tezarimab_RSI.md / Phaedora_RSI.md)
   **Step 2**: Exact match — Check if AE MedDRA PT is listed in RSI AE term list
     - If exact match found → EXPECTED
   **Step 3**: Hierarchy match (if exact match fails) — Query MedDRA API for hierarchy and synonyms
     - If RSI contains a broader term (e.g., RSI has "rash", AE is "maculopapular rash") → EXPECTED
     - If RSI contains a synonym (e.g., RSI has "headache", AE is "cephalgia") → EXPECTED
     - If AE is a narrower/more specific term of RSI term BUT significantly more severe (e.g., RSI has "rash",
       AE is "Stevens-Johnson syndrome") → UNEXPECTED (requires MSO clinical judgment, flag for deep review)
   **Step 4**: Novel AE term (not in RSI, not in MedDRA hierarchy match) → UNEXPECTED with confidence 0.0, flag
     for MSO deep review

   **Conservative fallback**: If uncertain about term specificity variance, flag as UNEXPECTED and route to MSO.

6. REPORTABILITY RECOMMENDATION (Apply FDA 21 CFR 314.80 + Multi-Jurisdictional Rules)
   **FDA 21 CFR 314.80**: Serious + Unexpected → 15-day expedited reporting to FDA
   **EMA Directive 2001/83/EC**: Serious + Unexpected → 15-day expedited reporting to EMA (aligned with FDA)
   **MHRA Guidance (UK)**: Serious + Unexpected → 15-day expedited reporting to MHRA (similar to EMA)
   **PMDA Guidance (Japan)**: [Include Japan-specific seriousness criteria differences if any, validated with
     Carolina Núñez-Reyes in Week 1]

   **Causality context**: Include causality assessment in reasoning (if available from `AECasePackage`), but do NOT
   exempt serious-unexpected from expedited reporting based on "unrelated" causality. FDA guidance: causality does
   not override reportability for serious-unexpected AEs.

   **Output**:
   - 15-day expedited (serious + unexpected) with jurisdiction list (FDA / EMA / MHRA / PMDA)
   - Periodic reporting only (serious + expected, or non-serious)
   - Non-reportable (only if non-serious + expected + confirmed non-drug-related per SOP)

7. CHAIN OF THOUGHT REASONING
   "First, retrieve product RSI for suspect drug. Then, apply ICH E2A criteria step-by-step (death? life-threatening?
   hospitalization? disability? congenital anomaly? other medically important?). Generate seriousness classification
   with reasoning and span citations. Then, match AE term to RSI (exact match first, then MedDRA hierarchy). Generate
   expectedness signal with reasoning and span citations. Then, apply FDA 21 CFR 314.80 logic (serious + unexpected
   → 15-day expedited). Apply multi-jurisdictional rules (EMA, MHRA, PMDA). Account for causality context (but do
   not override reportability). Generate reportability recommendation with rule-based justification and citations."

8. FEW-SHOT EXAMPLES
   [3 examples:
    - Straightforward serious-unexpected case (death, novel AE term) → 15-day expedited with CoT
    - Ambiguous "other medically important" case → serious with confidence <0.70, flag for MSO deep review
    - Term specificity variance case ("Stevens-Johnson syndrome" vs. "rash" in RSI) → unexpected, MSO deep review]

9. GUARDRAILS AND ESCALATION TRIGGERS
   - If seriousness confidence <0.70 → override to SERIOUS + flag for MSO deep review
   - If novel AE term (not in RSI, not in MedDRA) → UNEXPECTED with confidence 0.0 + flag for MSO deep review
   - If multi-jurisdictional complexity (FDA + EMA + PMDA all require expedited, but PMDA seriousness differs)
     → flag for Carolina Núñez-Reyes review
   - If causality "unrelated" but serious-unexpected → recommend 15-day expedited + flag for MSO to verify causality
   - If product RSI read fails → alert ops, block processing (cannot assess expectedness without RSI)

10. OUTPUT SCHEMA (Structured JSON: `TriageRecommendation`)
    {
      "case_id": "UUID",
      "seriousness_classification": {
        "serious": boolean,
        "criteria_matched": [ "death" | "life-threatening" | "hospitalization" | "disability" | "congenital_anomaly" | "other_medically_important" ],
        "reasoning": "CoT step-by-step reasoning",
        "span_citations": { "criteria": "source text span" },
        "confidence": float
      },
      "expectedness_signal": {
        "unexpected": boolean,
        "rsi_match": "exact | broader | narrower | synonym | none",
        "rsi_term_matched": string (or null),
        "reasoning": "CoT reasoning with MedDRA hierarchy path",
        "span_citations": { "rsi_term": "RSI text span", "ae_term": "AE narrative span" },
        "confidence": float
      },
      "reportability_recommendation": {
        "recommendation": "15_DAY_EXPEDITED | PERIODIC | NON_REPORTABLE",
        "jurisdictions": [ "FDA", "EMA", "MHRA", "PMDA" ],
        "rule_justification": "FDA 21 CFR 314.80: serious + unexpected → 15-day expedited",
        "causality_context": "causality assessment (if available), but does not override reportability",
        "reasoning": "CoT reasoning",
        "span_citations": { "regulatory_rule": "FDA 21 CFR 314.80 citation" },
        "confidence": float
      },
      "mso_flags": {
        "deep_review_required": boolean,
        "reason": "ambiguous seriousness | novel AE term | term specificity variance | multi-jurisdictional complexity | causality unrelated"
      },
      "signal_detection_flag": boolean,
      "signal_pattern": {
        "product": "Tezarimab",
        "meddra_pt": "Hepatotoxicity",
        "meddra_code": "10019692",
        "case_count": 3,
        "window_start": "2026-03-01",
        "window_end": "2026-05-30"
      },
      "model_version_adr2": "ADR-2 v1.0",
      "mso_action": "accepted | modified | overridden",
      "mso_rationale": "MSO substantive review documentation (required if modified/overridden)",
      "audit_trail": {
        "timestamp": "ISO 8601",
        "agent_version": "ADR-2 v1.0",
        "regulatory_references": [ "ICH E2A", "FDA 21 CFR 314.80", "EMA Directive 2001/83/EC", ... ]
      }
    }

    **[CURVEBALL - FDA May 2026 Guidance]**: Added `signal_detection_flag` (FDA Req 3: 3-cases-in-90-days pattern detection), `signal_pattern` (pattern details for MSO signal-detection review), `model_version_adr2` (FDA Req 1: model version tracking), `mso_action` and `mso_rationale` (FDA Req 1 & 2: human accept/modify/override action with substantive review documentation) to output schema.

11. TOKEN DISCIPLINE
    - Concise system prompt (<3,000 tokens)
    - ICH E2A criteria: bullet list (not verbose paragraphs)
    - Reportability rules: structured logic (not full regulatory text)
    - Few-shot examples: 3 max (cover ambiguous cases, not exhaustive)
```

**Token Budget per Case**:
- System prompt: 3,000 tokens (static, reused across all cases)
- Input (`AECasePackage` from ADR-1): 2,000 tokens (structured JSON, compact)
- Product RSI context: 1,500 tokens (AE term list for suspect drug)
- MedDRA hierarchy context (conditional): 500 tokens (10-15% of cases)
- Output (`TriageRecommendation` JSON): 2,500 tokens (classification + CoT reasoning + span citations)
- Total: ~9,500 tokens/case avg → $0.27/case at Claude Opus 4.7 pricing per [A5]

---

## Compounding Roadmap

ADR-2 reuses 5 integrations built by ADR-1 (Wave 1), reducing marginal build cost by ~40%.

### Wave 1 — Compounding Agent (ADR-2)

**Agent**: Medical Triage Agent  
**Wave Rationale**: Pipeline dependency (requires ADR-1 output), integrated value proposition (75→20 min requires both agents), self-financing (payback 3.1 months standalone, 2.1 months combined).

**Reuses from ADR-1** (Wave 1 foundation):
1. ✅ **PV case management API** (read `AECasePackage`, write `TriageRecommendation`)
2. ✅ **MedDRA API** (hierarchy queries for expectedness assessment)
3. ✅ **Product Information Database** (retrieve product list, confirm suspect drug in-scope)
4. ✅ **Audit Trail Store** (write classification reasoning, CoT, span citations)
5. ✅ **RxNorm API** (optional: for concomitant med normalization in causality assessment)

**New Integrations Built** (ADR-2 specific, reusable for future agents):
6. **Product RSI/CCSI Database** (retrieve safety profiles for Solivian, Tezarimab, Phaedora)
   - Prototype: file read from `mock-data/product-information/*.md`
   - Production: database query or API with versioned RSI (updated 1-2x/year per label changes)
   - **Reusable**: Any agent requiring product safety profile (e.g., causality assessment agent, signal detection agent)
7. **ICH E2A Criteria** (codified in system prompt, no external API)
   - **Reusable**: Any agent requiring seriousness classification (e.g., clinical trial AE triage)
8. **Reportability Rules Engine** (FDA 21 CFR 314.80, EMA, MHRA, PMDA codified in system prompt)
   - **Reusable**: Any agent requiring reportability determination (e.g., multi-product expansion, literature surveillance)
9. **MSO Review Queue** (UI + workflow for MSO to review recommendations, override, sign)
   - **Reusable**: Any agent requiring MSO sign-off (e.g., causality assessment agent, ADR-9 denial communication in future waves)

**Build Cost**: $30K (1.5 weeks FDE, system prompt $8K, RSI integration $3K, testing $4K per [A18])

**Annual Savings**: $116K (eliminates 15 min medical synthesis per case × 6,000 cases, minus token + MSO review costs)

---

### Integration Reuse Matrix (Updated with ADR-2)

| Integration / Asset | ADR-1 (Wave 1) | ADR-2 (Wave 1) | Future ADR-3 (Wave 2) | Notes |
|---------------------|----------------|----------------|----------------------|-------|
| **PV case management API** | ✓ Build | ✓ Reuse | ✓ Reuse | Shared across all PV agents |
| **RxNorm API** | ✓ Build | ✓ Reuse | ✓ Reuse | Drug nomenclature standard |
| **MedDRA API** | ✓ Build | ✓ Reuse | ✓ Reuse | AE term coding + hierarchy |
| **Product Information DB** | ✓ Build | ✓ Reuse | ✓ Reuse | Static product list |
| **Audit Trail Store** | ✓ Build | ✓ Reuse | ✓ Reuse | FDA inspection requirement |
| **Product RSI Database** | | ✓ Build | ✓ Reuse | Safety profile (expectedness) |
| **ICH E2A Criteria** | | ✓ Build (system prompt) | ✓ Reuse | Seriousness classification |
| **Reportability Rules** | | ✓ Build (system prompt) | ✓ Reuse | FDA/EMA/MHRA/PMDA regulations |
| **MSO Review Queue** | | ✓ Build (UI + workflow) | ✓ Reuse | Any MSO sign-off workflow |
| **Text parsing pipeline** | ✓ Build | | ✓ Reuse (literature) | Handles text/JSON/VTT |
| **HITL validation workflow** | ✓ Build | | ✓ Reuse | Confidence-gated agents |

**Compounding Effect (Wave 1 → Wave 2)**:
- ADR-1 built 5 integrations ($50K)
- ADR-2 reused 5, built 4 new ($30K, 40% reduction vs. standalone)
- Future Wave 2 agents will reuse 9 integrations → marginal cost $20-25K per agent (50-60% reduction vs. ADR-1)

---

### Potential Wave 2 Agents (Enabled by ADR-2 Assets)

**Out of current exam scope**, but planning for compounding:

1. **Causality Assessment Agent**
   - Reuses: PV API, RxNorm, MedDRA, Product RSI, Audit Trail Store, ICH E2A, MSO Review Queue
   - New: WHO-UMC causality criteria (certain/probable/possible/unlikely/unrelated), Naranjo algorithm
   - Value: Automates causality assessment synthesis (currently manual, ~10 min per case [A12])

2. **Multi-Product Expansion** (Pipeline Assets)
   - Reuses: All ADR-1 + ADR-2 integrations (zero new build)
   - New: Product list expansion (add 7 pipeline assets to product database)
   - Value: Expands capacity from 6K cases/year (3 marketed products) to 13K+ cases/year (3 marketed + 7 pipeline) with zero marginal integration cost

3. **Signal Detection Agent** (Aggregate AE Patterns)
   - Reuses: PV API (read all cases), MedDRA (SOC grouping), Product RSI, Audit Trail Store
   - New: Statistical signal detection algorithms (PRR, ROR, EBGM), data warehouse for aggregate queries
   - Value: Automates periodic safety signal detection (currently manual quarterly review)

4. **Literature Surveillance Agent**
   - Reuses: PV API, MedDRA, Text parsing pipeline (add PDF parsing), Product RSI, Reportability Rules, Audit Trail Store
   - New: PubMed API, PDF extraction, citation management
   - Value: Automates 10% of intake volume (literature alerts per [A2])

---

## Validation Design

This section specifies testable scenarios for happy path, edge cases, and failure modes.

### Happy Path Scenarios

#### HP-1: Serious AE Classification (Death Criterion)
**Input**: `AECasePackage` with `ae_description.outcome == "fatal"`, narrative: "patient died 3 days after drug administration"  
**Expected Output**:
- `seriousness_classification.serious == true`
- `seriousness_classification.criteria_matched == ["death"]`
- `seriousness_classification.reasoning`: "AE outcome is fatal. Matches ICH E2A death criterion. Classified as serious."
- `seriousness_classification.span_citations`: `{ "death": "ae_narrative:8-12" }` (span for word "died")
- `seriousness_classification.confidence >= 0.95` (death is unambiguous)
- Routed to MSO standard review (not deep review, clear criterion)

**Pass Criteria**: 100% accuracy on death criterion (false negative = patient safety risk)

---

#### HP-2: Serious AE Classification (Hospitalization Criterion)
**Input**: `AECasePackage` with narrative: "patient hospitalized for severe allergic reaction"  
**Expected Output**:
- `seriousness_classification.serious == true`
- `seriousness_classification.criteria_matched == ["hospitalization"]`
- `seriousness_classification.confidence >= 0.90`
- Routed to MSO standard review

**Pass Criteria**: Hospitalization keyword detection accuracy ≥96%

---

#### HP-3: Expectedness Assessment (Exact RSI Match)
**Input**: `AECasePackage` with suspect_drug="tezarimab", ae_description.meddra_pt="Headache", Tezarimab RSI lists "Headache" (MedDRA PT 10019211)  
**Expected Output**:
- `expectedness_signal.unexpected == false` (expected)
- `expectedness_signal.rsi_match == "exact"`
- `expectedness_signal.rsi_term_matched == "Headache"`
- `expectedness_signal.reasoning`: "AE term 'Headache' (MedDRA PT 10019211) exactly matches Tezarimab RSI term 'Headache'. Classified as expected."
- `expectedness_signal.confidence >= 0.95`

**Pass Criteria**: Exact match detection accuracy 100% (no false negatives)

---

#### HP-4: Expectedness Assessment (MedDRA Hierarchy Match, Broader Term)
**Input**: `AECasePackage` with suspect_drug="solivimab", ae_description.meddra_pt="Maculopapular rash", Solivimab RSI lists "Rash" (MedDRA PT 10037844)  
**Expected Output**:
- MedDRA API query returns: "Maculopapular rash" (PT) → parent HLT includes "Rash" (PT)
- `expectedness_signal.unexpected == false` (expected, broader term match)
- `expectedness_signal.rsi_match == "broader"`
- `expectedness_signal.rsi_term_matched == "Rash"`
- `expectedness_signal.reasoning`: "AE term 'Maculopapular rash' is narrower term of RSI 'Rash' per MedDRA hierarchy. Classified as expected."
- `expectedness_signal.confidence >= 0.85`

**Pass Criteria**: MedDRA hierarchy matching accuracy ≥85% (allows for clinical judgment on term specificity)

---

#### HP-5: Reportability Recommendation (Serious + Unexpected → 15-day Expedited)
**Input**: `seriousness_classification.serious == true`, `expectedness_signal.unexpected == true`  
**Expected Output**:
- `reportability_recommendation.recommendation == "15_DAY_EXPEDITED"`
- `reportability_recommendation.jurisdictions == ["FDA", "EMA", "MHRA"]` (Helix markets in US, EU, UK)
- `reportability_recommendation.rule_justification`: "FDA 21 CFR 314.80: Serious + Unexpected → 15-day expedited reporting required."
- `reportability_recommendation.confidence >= 0.90`
- Routed to MSO review with 4-hour SLA (serious-unexpected priority)

**Pass Criteria**: FDA 21 CFR 314.80 logic applied correctly 100% (serious + unexpected → 15-day expedited, no exceptions)

---

#### HP-6: End-to-End Case Processing
**Input**: `AECasePackage` with all required fields, serious-unexpected case  
**Expected Output**:
- Seriousness classified, expectedness assessed, reportability recommended
- Audit trail 100% complete (span citations, CoT reasoning, regulatory references)
- `TriageRecommendation` written to PV API
- Routed to MSO review queue
- Processing time: ≤15 min

**Pass Criteria**: End-to-end processing success rate ≥99%, audit trail completeness 100%

---

### Edge Cases

#### EC-6: Signal-Detection Escalation (3 Cases in 90 Days)

**[CURVEBALL - FDA May 2026 Guidance]** Added per FDA Requirement 3 (Signal-Detection Escalation).

**Input**: Third case of "Hepatotoxicity" (MedDRA PT 10019692) for Tezarimab within 90 days  
**Expected Output**:
- ADR-2 queries PV case history: `GET /api/v1/cases?product=Tezarimab&meddra_pt=10019692&date_range=90days`
- Query returns `case_count: 3` (including current case)
- `signal_detection_flag == true`
- `signal_pattern == { "product": "Tezarimab", "meddra_pt": "Hepatotoxicity", "meddra_code": "10019692", "case_count": 3, "window_start": "2026-03-01", "window_end": "2026-05-30" }`
- Case routed to MSO signal-detection queue (separate from standard MSO review queue) with **5-business-day SLA**
- Event emitted: `SIGNAL_DETECTION_ESCALATION, case_id={}, pattern={Tezarimab + Hepatotoxicity}, case_count=3`
- MSO investigates aggregate pattern:
  - Is this a new safety signal not in Tezarimab RSI?
  - Does Tezarimab RSI need updating?
  - Does this require aggregate reporting to FDA beyond individual 15-day reports?
  - Should product label be revised?

**Pass Criteria**: 100% of 3-cases-in-90-days patterns flagged (zero false negatives on signal detection), MSO signal-detection queue routing correct, 5-business-day SLA tracked

---

### Edge Cases (Continued)

#### EC-1: Ambiguous "Other Medically Important" Criterion (Pre-Curveball)
**Input**: AE narrative: "patient required emergency room visit for severe abdominal pain, no hospitalization"  
**Expected Output**:
- `seriousness_classification.serious == true` (ER visit suggests medical intervention required, meets "other medically important")
- `seriousness_classification.criteria_matched == ["other_medically_important"]`
- `seriousness_classification.confidence == 0.60-0.75` (ambiguous, requires clinical judgment)
- If confidence <0.70, override to `serious == true` + flag for MSO deep review
- `mso_flags.deep_review_required == true`, `mso_flags.reason == ["ambiguous_seriousness"]`

**Pass Criteria**: Ambiguous cases flagged for MSO deep review (confidence <0.70 triggers deep review 100% of time)

---

#### EC-2: Novel AE Term (Not in RSI, Not in MedDRA)
**Input**: AE description.meddra_pt == null (MedDRA API 404), narrative: "patient experienced rare autoimmune reaction"  
**Expected Output**:
- `expectedness_signal.unexpected == true` (novel AE term)
- `expectedness_signal.rsi_match == "none"`
- `expectedness_signal.rsi_term_matched == null`
- `expectedness_signal.confidence == 0.0` (zero confidence, requires MSO deep review)
- `mso_flags.deep_review_required == true`, `mso_flags.reason == ["novel_ae_term"]`

**Pass Criteria**: 100% of novel AE terms flagged for MSO deep review (zero false negatives on novel terms)

---

#### EC-3: Term Specificity Variance (Stevens-Johnson Syndrome vs. Rash)
**Input**: AE "Stevens-Johnson syndrome" (MedDRA PT 10042033), RSI lists "Rash" (MedDRA PT 10037844)  
**Expected Output**:
- MedDRA hierarchy shows "Stevens-Johnson syndrome" is narrower/more specific than "Rash"
- Clinical judgment: SJS is significantly more severe than rash → should be flagged unexpected despite hierarchy match
- `expectedness_signal.unexpected == true` (agent overrides hierarchy match due to severity difference)
- `expectedness_signal.rsi_match == "narrower"` (hierarchy match exists)
- `expectedness_signal.confidence == 0.60-0.75` (ambiguous, requires MSO deep review)
- `mso_flags.deep_review_required == true`, `mso_flags.reason == ["term_specificity_variance"]`

**Pass Criteria**: Term specificity variance cases flagged for MSO deep review (confidence <0.75 triggers deep review)

---

#### EC-4: Causality "Unrelated" but Serious-Unexpected
**Input**: Causality assessment (from concomitant meds) suggests "unrelated", but serious + unexpected criteria met  
**Expected Output**:
- `reportability_recommendation.recommendation == "15_DAY_EXPEDITED"` (causality does NOT override reportability per FDA guidance)
- `reportability_recommendation.causality_context`: "Causality assessment suggests unrelated. However, FDA 21 CFR 314.80 requires expedited reporting for serious-unexpected regardless of causality."
- `mso_flags.deep_review_required == true`, `mso_flags.reason == ["causality_unrelated"]` (MSO verifies causality reasoning)

**Pass Criteria**: Causality does NOT exempt serious-unexpected from 15-day expedited reporting (100% of cases follow FDA guidance)

---

#### EC-5: Multi-Jurisdictional Complexity (PMDA-Specific Seriousness Criteria)
**Input**: Case markets in Japan (PMDA jurisdiction), PMDA seriousness criteria differ from ICH E2A  
**Expected Output**:
- Agent applies both ICH E2A and PMDA criteria
- `reportability_recommendation.jurisdictions == ["FDA", "EMA", "MHRA", "PMDA"]`
- `mso_flags.deep_review_required == true`, `mso_flags.reason == ["multi_jurisdictional_complexity"]`
- MSO or Carolina Núñez-Reyes (VP Regulatory) reviews PMDA-specific requirements

**Pass Criteria**: Multi-jurisdictional cases flagged for regulatory review (100% of PMDA cases flagged)

---

### Failure Modes and Recovery

#### FM-1: Product RSI Read Failure (File Not Found)
**Input**: ADR-2 attempts to read Tezarimab_RSI.md, file not found (404 error)  
**Expected Behavior**:
- Immediate ops alert: "RSI_NOT_FOUND, product=Tezarimab"
- Block processing for all Tezarimab cases (cannot assess expectedness without RSI)
- Route case to exception queue with error message
- Do NOT continue with null RSI (expectedness assessment would be meaningless)

**Recovery**:
- Ops investigates: RSI file missing? Incorrect file path? Product name mismatch?
- Restore RSI file or fix path configuration
- Re-process exception queue cases after RSI restored

**Pass Criteria**: RSI missing detected immediately, no cases processed with missing RSI, ops alerted within 1 minute

---

#### FM-2: MedDRA API Failure (3 Consecutive Retries Exhausted)
**Input**: MedDRA API returns 500 Internal Server Error, retry 3 times, all fail  
**Expected Behavior**:
- Alert ops: "MEDDRA_API_UNAVAILABLE, retry_count=3"
- Use `ae_description.narrative` for classification (proceed without MedDRA hierarchy matching)
- Set `expectedness_signal.rsi_match == "none"` (cannot perform hierarchy match without MedDRA API)
- Flag as novel AE term: `expectedness_signal.unexpected == true`, `confidence == 0.0`
- `mso_flags.deep_review_required == true`, `mso_flags.reason == ["novel_ae_term"]`
- Continue processing (degrade gracefully, flag for MSO review)

**Recovery**:
- Ops investigates MedDRA API downtime
- If local MedDRA database available, switch to local lookup
- Re-process flagged cases with restored MedDRA API (refine expectedness assessment)

**Pass Criteria**: MedDRA API failure does not block processing, cases flagged for MSO review, ops alerted

---

#### FM-3: Audit Trail Write Failure (503 Service Unavailable)
**Input**: ADR-2 completes classification, attempts to write audit trail, receives HTTP 503  
**Expected Behavior**:
- Buffer `TriageRecommendation` audit trail locally (JSON log file)
- Emit event: "AUDIT_TRAIL_WRITE_FAILED, case_id={}"
- Alert ops (audit trail critical for FDA inspection)
- Do NOT block MSO review (MSO can review `TriageRecommendation` JSON which includes reasoning + citations inline)

**Recovery**:
- Ops investigates audit trail store downtime
- Once restored, re-submit buffered audit trails
- Validate 100% audit trail completeness for all cases

**Pass Criteria**: Audit trail write failure does not block MSO review, buffered locally, ops alerted within 2 minutes

---

#### FM-4: Precondition Failure (extraction_status != AUTO_COMPLETE)
**Input**: ADR-2 reads `AECasePackage` with `extraction_status == HUMAN_REQUIRED`  
**Expected Behavior**:
- Validation fails (ADR-2 precondition not met)
- Return error to ADR-1 queue: "Precondition failure: extraction_status must be AUTO_COMPLETE"
- Route case back to ADR-1 HITL validation queue
- Do NOT proceed with classification (incomplete extraction data)

**Recovery**:
- Case processor completes HITL validation (re-keys low-confidence fields)
- Transitions `extraction_status` to `AUTO_COMPLETE`
- Re-submits to ADR-2 for classification

**Pass Criteria**: Precondition validation enforced 100% (no cases with incomplete extraction processed by ADR-2)

---

#### FM-5: MSO Queue Overflow (>50 Cases Pending)
**Input**: MSO review queue exceeds 50 cases (capacity bottleneck)  
**Expected Behavior**:
- Alert CMO and Dr. Iyer: "MSO_QUEUE_OVERFLOW, queue_size=50+"
- Prioritize serious-unexpected cases (4-hour SLA) over non-serious cases (24-hour SLA)
- Display queue size to MSO team (dashboard)
- If queue >100 cases, alert ops to investigate root cause (agent accuracy drop? Staffing shortage?)

**Recovery**:
- CMO allocates additional MSO capacity (temporary staff, overtime)
- Investigate agent accuracy: if deep review rate >20%, audit agent classification logic
- Adjust MSO SLA temporarily if sustained backlog

**Pass Criteria**: MSO queue monitored continuously, prioritization enforced, CMO alerted if capacity exceeded

---

### Concurrency and Idempotency

#### Concurrency Test: Simultaneous Classification of Same Case
**Scenario**: Two ADR-2 agents process same case_id simultaneously (race condition)  
**Expected Behavior**:
- PV API enforces uniqueness constraint on case_id (only one `TriageRecommendation` per case_id)
- First agent writes `TriageRecommendation` successfully
- Second agent receives 409 Conflict (case_id already has triage recommendation)
- Second agent treats as success (idempotency: classification already complete), logs "duplicate classification prevented", exits

**Pass Criteria**: No duplicate `TriageRecommendation` records, race condition handled gracefully

---

#### Idempotency Test: Duplicate Audit Trail Write
**Scenario**: ADR-2 writes audit trail, network timeout, retries with same case_id + timestamp  
**Expected Behavior**:
- Audit trail store deduplicates by case_id + classification_type (e.g., case_id="abc-123", classification_type="seriousness")
- First write succeeds (audit trail created)
- Second write with same case_id + classification_type returns success (idempotent, no duplicate audit entry)

**Pass Criteria**: No duplicate audit trail entries, retry is safe

---

## Integration Contracts

### ADR-2 → PV Case Management System (Read `AECasePackage`)

**Endpoint**: `GET /api/v1/cases/{case_id}`

**Response Schema** (ADR-1 output = ADR-2 input):
```json
{
  "case_id": "UUID",
  "received_at": "ISO 8601 timestamp",
  "format": "HCP_TEXT | PATIENT_WEBFORM | ...",
  "extraction_status": "AUTO_COMPLETE",
  "patient": { "age": 45, "sex": "F", ... },
  "suspect_drug": { "name": "tezarimab", "rxnorm_code": "123456", ... },
  "ae_description": { "narrative": "severe headache", "meddra_pt": "Headache", "meddra_code": "10019211", ... },
  "temporal": { "drug_start_date": "2026-04-15", "ae_onset_date": "2026-05-28", ... },
  "concomitant_meds": [ { "name": "ibuprofen", ... } ],
  "medical_history": { "narrative": "no significant medical history", ... },
  "span_citations": { ... }
}
```

**Precondition Check**: ADR-2 validates `extraction_status == AUTO_COMPLETE` before processing. If `extraction_status != AUTO_COMPLETE`, return error to ADR-1 queue.

**Error Handling** (complete status code mapping):
- **200 OK**: `AECasePackage` retrieved successfully, proceed with classification
- **400 Bad Request**: Schema validation failure (missing required fields in `AECasePackage`)
  - Action: Log error with validation details
  - Route to exception queue with error message: "AECasePackage schema invalid"
  - Alert ops (indicates ADR-1 schema drift or bug)
  - Do NOT retry (client error)
- **404 Not Found**: case_id does not exist in PV database
  - Action: Alert ops immediately ("case_id not found, ADR-1 write may have failed")
  - Route to exception queue
  - Investigate: Did ADR-1 write fail? Is case_id incorrect?
  - Do NOT retry (case does not exist)
- **409 Conflict**: `extraction_status != AUTO_COMPLETE` (precondition failure)
  - Action: Return error to ADR-1 queue: "Precondition failure: extraction_status must be AUTO_COMPLETE"
  - Route case back to ADR-1 HITL validation queue
  - Do NOT proceed with classification (incomplete extraction data)
- **503 Service Unavailable**: PV API temporarily down
  - Action: Retry 3 times with exponential backoff (1s, 2s, 4s)
  - After 3 failures, route to exception queue + alert ops
  - Do NOT buffer locally (READ operation, no data to preserve)
- **Network Timeout** (no response within 5 seconds):
  - Action: Retry once after 1s delay
  - If fails, route to exception queue + alert ops

**Fallback Behavior**:
- If PV API persistently unavailable (>50% read failures over 1 hour), alert ops immediately
- Block ADR-2 processing until PV API restored (cannot classify without ADR-1 extraction data)
- Display alert to MSO team: "ADR-2 processing paused due to PV API unavailability"

---

### ADR-2 → Product RSI Database (Read)

**Endpoint** (Prototype): File read `mock-data/product-information/{product_name}_RSI.md`  
**Endpoint** (Production): `GET /api/v1/products/{product_id}/rsi?version=latest`

**Request**: Suspect drug name (extracted by ADR-1, normalized via RxNorm)

**Response** (structured markdown or JSON):
```markdown
# Solivian Reference Safety Information

## Adverse Events

### Common (≥1%)
- Headache (MedDRA PT: 10019211)
- Nausea (MedDRA PT: 10028813)
- Fatigue (MedDRA PT: 10016256)

### Uncommon (<1%, ≥0.1%)
- Rash (MedDRA PT: 10037844)
- Dizziness (MedDRA PT: 10013573)

### Rare (<0.1%)
- Hepatotoxicity (MedDRA PT: 10019692)
```

**Error Handling** (complete error mapping):
- **Success** (file read or HTTP 200): RSI content retrieved, parse AE term list, proceed with expectedness assessment
- **File Not Found** (prototype): Tezarimab_RSI.md missing at expected path
  - Action: Immediate ops alert: "RSI_NOT_FOUND, product=Tezarimab, path=mock-data/product-information/Tezarimab_RSI.md"
  - Block processing for all Tezarimab cases (cannot assess expectedness without RSI)
  - Route case to exception queue with error: "RSI file missing for product: Tezarimab"
  - Do NOT proceed with null RSI (expectedness assessment would be meaningless)
  - Do NOT retry (file missing, not transient)
- **404 Not Found** (production API): Product ID invalid or RSI version not found
  - Action: Same as File Not Found above
  - Investigate: Is product_id correct? Is RSI version parameter wrong?
- **Malformed Data** (parse error): RSI file corrupted, invalid markdown format, missing AE term section
  - Action: Alert ops: "RSI_PARSE_ERROR, product=Tezarimab"
  - Log parse error details (which line, what format expected)
  - Block processing (malformed RSI cannot be used for expectedness assessment)
  - Route to exception queue
- **Permission Denied** (file read error): Insufficient file system permissions
  - Action: Alert ops: "RSI_PERMISSION_DENIED, path=..."
  - Block processing, fix permissions
- **Network Timeout** (production API, no response within 3 seconds):
  - Action: Retry once after 1s delay
  - If fails, treat as RSI unavailable (block processing, alert ops)

**Fallback Behavior**:
- Primary: Block processing if RSI unavailable (cannot assess expectedness without safety profile)
- Secondary (if ops approves): Process case with `expectedness_signal.rsi_match == "none"`, `unexpected == true`, `confidence == 0.0`, flag for MSO deep review
  - This fallback treats missing RSI as "novel AE term" → serious-unexpected → 15-day expedited
  - Safer than under-reporting (over-reporting is acceptable per [A4])
  - Only use if RSI downtime >4 hours and backlog is critical

**Data Mapping**:
- RSI markdown structure: `## Adverse Events` section → parse bullet list of AE terms
- Each AE term format: "Term Name (MedDRA PT: code)" → extract term name and MedDRA code
- Internal `suspect_drug.name` → filename mapping: "tezarimab" → "Tezarimab_RSI.md" (case-insensitive match with capitalization)

**Cost**: Single file read per case (negligible, <1ms) or single API call (~50ms latency). Annual cost: $0 (file read) or minimal (API call latency only).

---

### ADR-2 → MedDRA API (Hierarchy Query)

**Endpoint**: `GET /api/v1/meddra/hierarchy?pt={meddra_code}&levels=HLT,SOC`

**Request**: AE MedDRA PT code (extracted by ADR-1)

**Response**:
```json
{
  "pt": { "code": "10019211", "term": "Headache" },
  "hlt": { "code": "10019231", "term": "Headaches" },
  "soc": { "code": "10029205", "term": "Nervous system disorders" }
}
```

**Synonym Query** (conditional):
**Endpoint**: `GET /api/v1/meddra/synonyms?pt={meddra_code}`

**Response**:
```json
{
  "pt": "10019211",
  "synonyms": [ "Cephalgia", "Cephalalgia" ]
}
```

**Error Handling** (complete status code mapping):
- **200 OK**: MedDRA hierarchy or synonym data retrieved, use for expectedness assessment
- **404 Not Found**: MedDRA PT code not found (invalid code from ADR-1 extraction, novel term not in MedDRA)
  - Action: Log warning: "MedDRA PT code not found: {meddra_code}"
  - Use `ae_description.narrative` as-is for classification
  - Set `expectedness_signal.rsi_match == "none"` (cannot perform hierarchy match)
  - Flag as novel AE term: `expectedness_signal.unexpected == true`, `confidence == 0.0`
  - `mso_flags.deep_review_required == true`, `mso_flags.reason == ["novel_ae_term"]`
  - Do NOT block processing (proceed with conservative classification)
- **401 Unauthorized**: Auth token expired, license expired, or API key invalid
  - Action: Alert ops immediately (email + Slack: "MEDDRA_API_AUTH_FAILED")
  - Do NOT retry (auth must be fixed first)
  - Block all new ADR-2 processing until MedDRA API restored
  - Display alert to MSO team: "ADR-2 paused due to MedDRA API auth failure"
- **429 Too Many Requests**: Rate limit exceeded (assumed ~100 req/min)
  - Action: Exponential backoff, retry after 500ms
  - Max 3 retries
  - If still 429, treat as 404 (proceed without hierarchy match, flag as novel AE term)
- **500 Internal Server Error**: MedDRA API down
  - Action: Retry once after 1s delay
  - If fails, treat as 404 (proceed without hierarchy match)
  - Alert ops if >10% MedDRA hierarchy queries fail over 1 hour (systemic issue)
- **Network Timeout** (no response within 3 seconds):
  - Action: Retry once after 500ms delay
  - If fails, treat as 404 (proceed without hierarchy match)

**Fallback Behavior**:
- If MedDRA API persistently unavailable (401 Unauthorized or >50% failures over 1 hour):
  - Primary: Alert ops, block ADR-2 processing (MedDRA hierarchy critical for expectedness assessment accuracy)
  - Secondary (if local MedDRA database available): Switch to local hierarchy queries
    - Requires: MedDRA database version match (MedDRA updated quarterly Q1/Q2/Q3/Q4)
    - Query performance: <100ms per hierarchy query
    - Validate local fallback in Week 1 IT discovery
  - Tertiary (if no local fallback): Process cases with `rsi_match == "none"`, flag all as novel AE terms (over-reporting is safer than under-reporting)
- If >20% of cases flagged as novel AE terms over 24 hours, alert ops (may indicate MedDRA API issue or RSI missing terms)

**Rate Limiting** (client-side):
- Assumed rate limit: 100 requests/minute (validate in Week 1)
- Implement request queue with rate limiter (token bucket algorithm)
- Batch processing: max 90 req/min (10% buffer below limit)
- Only 10-15% of cases require hierarchy matching per [A13] → ~10 req/min avg load (well below limit)

**Data Mapping**:
- Internal `ae_description.meddra_code` → MedDRA API `pt` parameter (8-digit PT code)
- MedDRA API `hlt` (High-Level Term) → used for broader term matching
- MedDRA API `soc` (System Organ Class) → used for very broad term matching (rare)
- MedDRA API `synonyms` → used for synonym matching

**Cost**: 1-2 API calls per case × 10-15% of cases requiring hierarchy queries = ~0.1-0.3 API calls per case avg. Licensed API (annual subscription required per [A16]). Latency: ~100ms per query.

---

### ADR-2 → PV Case Management System (Write `TriageRecommendation`)

**Endpoint**: `POST /api/v1/cases/{case_id}/triage`

**Request Schema**:
```json
{
  "case_id": "UUID",
  "seriousness_classification": {
    "serious": true,
    "criteria_matched": [ "other_medically_important" ],
    "reasoning": "Severe allergic reaction requiring epinephrine administration. Meets ICH E2A 'other medically important' criterion (medical intervention required to prevent serious outcome).",
    "span_citations": { "criteria": "ae_narrative:45-67" },
    "confidence": 0.72
  },
  "expectedness_signal": {
    "unexpected": true,
    "rsi_match": "none",
    "rsi_term_matched": null,
    "reasoning": "AE term 'anaphylaxis' (MedDRA PT 10002198) not found in Tezarimab RSI. MedDRA hierarchy query shows no broader term match (checked HLT 'Hypersensitivity conditions'). Novel AE term flagged as unexpected.",
    "span_citations": { "ae_term": "ae_narrative:12-23" },
    "confidence": 0.0
  },
  "reportability_recommendation": {
    "recommendation": "15_DAY_EXPEDITED",
    "jurisdictions": [ "FDA", "EMA", "MHRA" ],
    "rule_justification": "FDA 21 CFR 314.80: Serious (other medically important) + Unexpected (novel AE term) → 15-day expedited reporting required.",
    "causality_context": "Temporal relationship supports drug-related (AE onset 30 min post-dose). No concomitant medications with known anaphylaxis risk.",
    "reasoning": "Combination of serious + unexpected triggers 15-day expedited reporting per FDA regulation.",
    "span_citations": { "regulatory_rule": "system_prompt:FDA_21_CFR_314.80" },
    "confidence": 0.95
  },
  "mso_flags": {
    "deep_review_required": true,
    "reason": "novel AE term (confidence 0.0)"
  },
  "audit_trail": {
    "timestamp": "2026-06-01T14:23:45Z",
    "agent_version": "ADR-2 v1.0",
    "regulatory_references": [ "ICH E2A", "FDA 21 CFR 314.80", "EMA Directive 2001/83/EC" ]
  }
}
```

**Response** (success):
```json
{
  "status": "triage_complete",
  "case_id": "UUID",
  "mso_review_required": true,
  "timestamp": "ISO 8601"
}
```

**Response** (failure):
```json
{
  "status": "error",
  "error_code": "503 | 400",
  "message": "Service unavailable | Invalid schema"
}
```

**Error Handling** (complete status code mapping):
- **200 OK**: `TriageRecommendation` written successfully, proceed to MSO routing
- **201 Created**: `TriageRecommendation` created successfully (alternative success code), proceed
- **400 Bad Request**: Schema validation failure (missing required field, invalid data type in `TriageRecommendation`)
  - Action: Log error with validation details
  - Route to exception queue with error message: "TriageRecommendation schema invalid"
  - Alert ops (indicates ADR-2 output schema bug)
  - Do NOT retry (client error, fix schema issue first)
- **401 Unauthorized**: Auth token expired or invalid
  - Action: Alert ops immediately (email + Slack: "PV_API_AUTH_FAILED")
  - Do NOT retry (auth must be fixed first)
  - Block all new ADR-2 processing until auth restored
- **409 Conflict**: case_id already has `TriageRecommendation` (duplicate classification attempt)
  - Action: Treat as success (idempotency: classification already complete)
  - Log "duplicate TriageRecommendation prevented"
  - Proceed (no error, expected behavior during retry after timeout)
- **429 Too Many Requests**: Rate limit exceeded
  - Action: Exponential backoff, wait for Retry-After header value (default 30s if header missing)
  - Retry once after backoff
  - If rate limit persists, buffer locally + alert ops
- **503 Service Unavailable**: PV API temporarily down
  - Action: Retry 3 times with exponential backoff (1s, 2s, 4s)
  - After 3 failures: buffer `TriageRecommendation` JSON locally with case_id
  - Alert ops: "PV_API_WRITE_FAILED, case_id={}, retry_count=3"
  - Buffer retention: 7 days, re-submit when API restored
- **504 Gateway Timeout**: PV API processing timeout
  - Action: Same as 503 (retry 3 times, buffer locally, alert ops)
- **500 Internal Server Error**: PV API internal error
  - Action: Retry once after 2s delay (may be transient)
  - If fails again, buffer locally + alert ops
- **Network Timeout** (no response within 10 seconds):
  - Action: Retry once after 2s delay
  - If fails, buffer locally + alert ops

**Fallback Behavior**:
- Local buffer location: `/var/data/adr2/buffer/`
- Buffer file format: JSON (one file per case, filename: `{case_id}_triage.json`)
- Buffer monitoring: Ops dashboard shows buffered case count, alerts if >10 cases buffered
- Re-submission: Automated retry every 15 minutes for buffered cases (use case_id uniqueness to prevent duplicates)
- MSO review can proceed with buffered `TriageRecommendation` JSON (includes all reasoning + citations inline)
  - Buffer write does NOT block MSO review (MSO can review from local JSON file if PV API down)

**Rate Limiting** (client-side):
- Max 100 concurrent writes (throttle at application layer)
- If PV API rate limit unknown, start with 10 writes/second, increase gradually based on 429 responses

**Data Mapping**:
- Internal `TriageRecommendation.case_id` → PV API `triage.case_id` (foreign key to case table)
- Internal nested entities (seriousness_classification, expectedness_signal, reportability_recommendation) → PV API flattened fields OR nested JSON (depends on PV API schema, validate in Week 1)

**SLA**: <500ms response time (p95), 99.5% availability per [A16].

---

### ADR-2 → Audit Trail Store (Write)

**Endpoint**: `POST /api/v1/audit-trail`

**Request Schema**:
```json
{
  "case_id": "UUID",
  "classification_type": "seriousness | expectedness | reportability",
  "decision": "serious | unexpected | 15_day_expedited",
  "reasoning": "CoT step-by-step reasoning",
  "span_citations": { "field_name": "source text span" },
  "confidence": 0.72,
  "timestamp": "ISO 8601",
  "agent_version": "ADR-2 v1.0",
  "regulatory_references": [ "ICH E2A", "FDA 21 CFR 314.80" ]
}
```

**Response** (success):
```json
{
  "status": "audit_trail_written",
  "audit_id": "UUID"
}
```

**Error Handling** (complete status code mapping):
- **200 OK** or **201 Created**: Audit trail written successfully
- **400 Bad Request**: Schema validation failure (missing required field in audit trail)
  - Action: Log error with validation details
  - Alert ops: "AUDIT_TRAIL_SCHEMA_ERROR"
  - Buffer audit trail locally (JSON log file)
  - Do NOT block ADR-2 classification (audit trail is supplementary, `TriageRecommendation` includes reasoning inline)
- **401 Unauthorized**: Auth token expired or invalid
  - Action: Alert ops immediately: "AUDIT_TRAIL_API_AUTH_FAILED"
  - Buffer audit trail locally
  - Do NOT block ADR-2 classification
- **429 Too Many Requests**: Rate limit exceeded
  - Action: Exponential backoff, retry after 500ms
  - Max 3 retries
  - If still fails, buffer locally + alert ops
- **503 Service Unavailable**: Audit trail store temporarily down
  - Action: Buffer locally (JSON log file: `/var/data/adr2/audit_buffer/{case_id}_audit.json`)
  - Emit event: "AUDIT_TRAIL_WRITE_FAILED, case_id={}"
  - Alert ops (audit trail critical for FDA inspection, must be restored ASAP)
  - Do NOT block ADR-2 classification (MSO review can proceed)
- **500 Internal Server Error** or **Network Timeout**:
  - Action: Same as 503 (buffer locally, alert ops, do not block)

**Fallback Behavior**:
- Audit trail write failure must NOT block ADR-2 classification or MSO review
- `TriageRecommendation` JSON includes all reasoning + span citations inline (self-contained for MSO review)
- Buffered audit trails re-submitted when audit trail store restored (automated retry every 15 minutes)
- Validate 100% audit trail completeness after API restored (query buffered files, confirm all re-submitted)

**Failure Mode**: Audit trail is critical for FDA inspection but not critical for operational workflow. Degrade gracefully: buffer locally, alert ops, continue MSO review. Restore audit trail completeness before any FDA inspection (monitor buffered audit trail count, escalate if >50 cases buffered).

---

### ADR-2 → MSO Review Queue (Internal Queue)

**Trigger**: `TriageRecommendation` complete

**Data Contract**: `TriageRecommendation` JSON (full schema above)

**SLA**: MSO reviews within 24 hours (all cases), within 4 hours (serious-unexpected flagged by agent with `mso_flags.deep_review_required: true`)

**Precondition Check**: None (MSO review is always required per CMO mandate, 100% of cases)

**Failure Mode**: If MSO queue exceeds 50 cases, prioritize serious-unexpected cases + alert CMO (capacity bottleneck)

---

### ADR-2 → PV Case History Query (Signal Detection)

**[CURVEBALL - FDA May 2026 Guidance]** Added per FDA Requirement 3 (Signal-Detection Escalation for 3-cases-in-90-days patterns).

**Endpoint**: `GET /api/v1/cases?product={product_name}&meddra_pt={ae_meddra_code}&date_range=90days`

**Purpose**: Query PV case history for pattern matching to detect ≥3 cases of same product + MedDRA PT in rolling 90-day window (FDA Req 3 signal-detection escalation).

**Trigger**: After each `TriageRecommendation` complete, before MSO routing.

**Request Parameters**:
- `product`: string, required (suspect drug product name, e.g., "Tezarimab")
- `meddra_pt`: string, required (8-digit MedDRA PT code, e.g., "10019692" for Hepatotoxicity)
- `date_range`: string, required, value "90days" (rolling 90-day window from current date backward)

**Response**:
```json
{
  "case_count": 3,
  "cases": [
    { "case_id": "UUID-1", "received_at": "2026-03-15T10:00:00Z" },
    { "case_id": "UUID-2", "received_at": "2026-04-22T14:30:00Z" },
    { "case_id": "UUID-3", "received_at": "2026-05-30T09:15:00Z" }
  ]
}
```

**Logic**:
- If `case_count >= 3`, set `signal_detection_flag: true` in `TriageRecommendation`
- Populate `signal_pattern` object with product, meddra_pt, meddra_code, case_count, window_start (earliest case received_at), window_end (current date)
- Emit event: `SIGNAL_DETECTION_ESCALATION, case_id={current_case_id}, pattern={product + MedDRA PT}, case_count={count}`
- Route case to MSO signal-detection queue (separate from standard MSO review queue) with 5-business-day SLA

**Error Handling** (complete status code mapping):
- **200 OK**: Query successful, pattern detection logic proceeds
- **400 Bad Request**: Invalid query parameters (e.g., meddra_pt not 8-digit code)
  - Action: Log error with parameter details
  - Set `signal_detection_flag: false` (cannot detect pattern without valid query)
  - Proceed with standard MSO review (signal detection is supplementary, not blocking)
  - Alert ops if query parameter errors >5% over 1 hour (indicates ADR-2 bug)
- **404 Not Found**: No cases found matching pattern (case_count = 0)
  - Action: Set `signal_detection_flag: false` (no pattern detected)
  - Proceed with standard MSO review
  - This is expected behavior for first or second case of a given product + MedDRA PT
- **503 Service Unavailable**: PV API temporarily down
  - Action: Log warning: "PV case history query failed (signal detection), case_id={}, error=503"
  - Set `signal_detection_flag: false` (cannot detect pattern due to API failure)
  - Proceed with standard MSO review (do NOT block classification due to signal detection query failure)
  - Alert ops if query failure rate >10% over 1 hour (PV API availability issue)
- **Network Timeout** (no response within 3 seconds):
  - Action: Same as 503 (log warning, set flag false, proceed with MSO review, alert ops if persistent)

**Fallback Behavior**:
- Signal detection query failure must NOT block ADR-2 classification or MSO review
- If query fails, proceed with `signal_detection_flag: false` (conservative: assume no pattern until confirmed)
- Alert ops if query failure rate >10% over 1 hour
- MSO can manually query case history during review if signal detection flag is false but MSO suspects pattern

**Performance**:
- Query latency target: <50ms (p95) for 90-day window query
- Index required: PV case database must have composite index on (product, meddra_pt, received_at) for efficient 90-day range queries
- Query cost: Single API call per case (~50ms). Annual cost: 6,000 queries/year × $0 (internal PV API).

**Data Mapping**:
- Internal `suspect_drug.name` → Query parameter `product`
- Internal `ae_description.meddra_code` → Query parameter `meddra_pt`
- Query response `case_count` → Internal `signal_pattern.case_count`
- Query response `cases[0].received_at` (earliest) → Internal `signal_pattern.window_start`
- Current date → Internal `signal_pattern.window_end`

---

**Document Owner**: FDE Engagement Lead  
**Next Review**: After Week 1 IT discovery (validate PV API, Product RSI database, MedDRA API, multi-jurisdictional reportability rules with Carolina Núñez-Reyes)  
**[CURVEBALL - FDA May 2026 Guidance]**: Validate PV case history query endpoint availability and performance for signal detection (FDA Req 3)
