# Agent Purpose Documents, Autonomy Matrices, and Escalation Triggers

**Document Version**: 1.0  
**Date**: 2026-06-01  
**Project**: Helix Therapeutics Agentic Adverse Event Triage System

---

## Table of Contents

### ADR-1: AE Intake & Data Extraction Agent
1. [Agent Purpose (ADR-1)](#agent-purpose-adr-1)
   - [Agent Name](#agent-name)
   - [Job to be Done](#job-to-be-done)
   - [Business Context](#business-context)
   - [Primary Objectives](#primary-objectives)
   - [KPIs](#kpis)
   - [Failure Modes](#failure-modes)
   - [Delegation Archetype](#delegation-archetype)
2. [Escalation Triggers (ADR-1)](#escalation-triggers-adr-1)
3. [Autonomy Matrix (ADR-1)](#autonomy-matrix-adr-1)
   - [AGENT DECIDES ALONE (No HITL Required)](#agent-decides-alone-no-hitl-required)
   - [AGENT ACTS, HUMAN NOTIFIED AFTER](#agent-acts-human-notified-after)
   - [AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION](#agent-proposes-human-approves-before-action)
   - [HUMAN TAKES OVER (Agent Supports, Does Not Decide)](#human-takes-over-agent-supports-does-not-decide)

### ADR-2: Medical Triage Agent
4. [Agent Purpose (ADR-2)](#agent-purpose-adr-2)
   - [Agent Name](#agent-name-1)
   - [Job to be Done](#job-to-be-done-1)
   - [Business Context](#business-context-1)
   - [Primary Objectives](#primary-objectives-1)
   - [KPIs](#kpis-1)
   - [Failure Modes](#failure-modes-1)
   - [Delegation Archetype](#delegation-archetype-1)
5. [Escalation Triggers (ADR-2)](#escalation-triggers-adr-2)
6. [Autonomy Matrix (ADR-2)](#autonomy-matrix-adr-2)
   - [AGENT DECIDES ALONE (No MSO Review Required Before Action)](#agent-decides-alone-no-mso-review-required-before-action)
   - [AGENT PROPOSES, MSO REVIEWS ALL RECOMMENDATIONS](#agent-proposes-mso-reviews-all-recommendations)
   - [MSO DECIDES (Agent Supports, Does Not Decide)](#mso-decides-agent-supports-does-not-decide)

---

# ADR-1: AE Intake & Data Extraction Agent

## Agent Purpose (ADR-1)

### Agent Name
AE Intake & Data Extraction Agent (ADR-1)

### Job to be Done
Receive heterogeneous adverse event reports from any channel, validate minimum required information, extract all structured data elements per ICH E2D, normalize to standard nomenclatures (RxNorm, MedDRA), generate per-field confidence scores, and route to medical triage or HITL validation based on extraction quality.

### Business Context
Pharmacovigilance adverse event triage system for Helix Therapeutics' three marketed products (Solivian, Tezarimab, Phaedora). AE reports arrive via 5 channels: HCP text reports (30%), patient webforms/phone (25%), social media monitoring (20%), clinical trial sites (15%), medical literature (10%) per [A2]. Every report must be triaged within 15 calendar days for FDA compliance (21 CFR 314.80). Current manual intake+extraction consumes 40-45 min per case (47% of 75-min baseline per [A1]).

### Primary Objectives

1. **Comprehensive extraction**: Extract all ICH E2D required data elements (patient demographics, suspect drug + dose + indication, AE description + onset + outcome, concomitant medications, medical history, temporal relationships) from heterogeneous text formats with per-field confidence scoring.

2. **Quality-gated processing**: Process 88% of cases end-to-end autonomously (high-confidence extraction); route 12% to HITL validation when any required field confidence < 0.85 [A15].

3. **Zero data loss**: Detect duplicates (route to `PENDING_DUPLICATE`), flag mis-routed complaints (route to `EXCEPTION_NOTE`), request reporter follow-up when minimum information missing (route to `REPORTER_FOLLOWUP`).

4. **Audit trail generation**: Generate span-level citations for every extracted field, linking each data element to source text location (FDA inspection requirement per [A10]).

5. **15-day clock anchoring**: Anchor immutable `received_at` timestamp on report ingestion (clock starts at first receipt by any Helix employee, per FDA 21 CFR 314.80).

### KPIs

| Metric | Target | Acceptable Ceiling | Measurement |
|--------|--------|-------------------|-------------|
| **Extraction accuracy** (required fields match case processor validation) | ≥96% | ≥90% | Spot-check 5% weekly |
| **HITL rate** (% cases requiring human validation) | 12% | ≤20% | Count HITL queue entries daily |
| **Throughput** | 5-10 min per case (agent processing) | ≤15 min | Median processing time |
| **Cost per case** | $0.83 (token + HITL weighted) | ≤$2.00 | Track token usage + HITL hours |
| **Duplicate detection precision** | ≥95% (true duplicates flagged) | ≥90% | Manual review of `PENDING_DUPLICATE` queue |
| **Audit trail completeness** | 100% (all fields have span citations) | 100% | Automated schema validation |

### Failure Modes

| Failure Mode | Consequence | Recovery Path |
|-------------|-------------|---------------|
| **False-negative confidence score** (low-quality extraction flagged as high-confidence) | Downstream classification errors in ADR-2 → 15-day reporting risk | Weekly spot-check 5% of auto-processed cases; retrain confidence calibration if precision drops below 90% |
| **False-positive duplicate detection** (unique case flagged as duplicate) | Case blocked from processing, requires manual override | Manual review of `PENDING_DUPLICATE` queue within 4 hours; adjust fuzzy-match threshold if false-positive rate >5% |
| **Patient identifier extraction error** (GDPR/HIPAA violation in social media extracts) | Compliance violation, potential regulatory action | Red-team social media cases in validation; implement PII masking layer before token transmission |
| **Temporal relationship estimation error** ("a few weeks ago" → incorrect date) | Causality assessment errors in downstream analysis | Flag all estimated dates in audit trail with `date_estimated: true`; request reporter follow-up |
| **Exception queue overflow** (mis-routed complaints >15% of volume) | Queue backlog, intake capacity bottleneck | Alert ops if exception rate >15% over 24 hours; investigate root cause (format change, new channel) |

### Delegation Archetype
**Fully Agentic with Confidence-Based HITL**

**Rationale**: Format classification, duplicate detection, and scope routing are deterministic (rule-based logic). Structured field extraction from semi-structured formats (HCP reports with field labels, JSON webforms, trial reports) is high-accuracy with LLM. Unstructured narrative extraction (patient phone transcripts, social media posts) is less deterministic but achievable with per-field confidence scoring [A8]. High compliance risk requires HITL validation when confidence is low. High volume (6,000 cases/year) justifies full automation with safety guardrail.

**Human Oversight Model**:
- **Confidence Threshold**: Any required field confidence < 0.85 → route to case processor HITL validation queue [A15]
- **Optional Field Threshold**: Optional field confidence < 0.70 → flag as "needs follow-up" but do not block processing
- **Exception Handling**: Mis-routed complaints → exception queue. Insufficient minimum info → reporter follow-up queue. Ambiguous duplicates (fuzzy match confidence 0.5-0.8) → manual review.
- **Audit**: Spot-check 5% of intake+extraction decisions weekly for quality assurance

---

## Escalation Triggers (ADR-1)

**Agent → HITL Validation Queue (Case Processor Re-key)**:
- Any required field extraction confidence < 0.85
- Missing patient identifier (no name, no medical record number)
- Missing suspect drug name or AE description (insufficient minimum information per ICH E2A)
- Concomitant medication extraction: confidence < 0.80 (lower threshold due to under-reporting in source reports)

**Agent → Exception Queue (Ops Review)**:
- Mis-routed medical device complaint (no AE component)
- Mis-routed quality complaint (no AE component)
- Out-of-scope product (clinical trial asset, not marketed product)
- Format classification failure (unknown file type, empty file, corrupted data)

**Agent → Reporter Follow-up Queue**:
- Insufficient minimum required information (no patient identifier, no suspect drug, no AE description)
- Missing temporal relationship data (drug start date, AE onset date unknown → cannot assess causality)

**Agent → Ops Alert**:
- PV case management API 3 consecutive write failures → alert ops + buffer locally with idempotency key
- Exception rate >15% over 24 hours (indicates format change or new channel issue) [A11]
- HITL queue >20 cases (capacity bottleneck, prioritize serious-unexpected cases)

---

## Autonomy Matrix (ADR-1)

This matrix defines what ADR-1 decides alone vs. what requires human approval or review.

### AGENT DECIDES ALONE (No HITL Required)

- **Format classification** (text/JSON/VTT) based on file extension and content structure
- **Duplicate detection** when fuzzy match confidence ≥0.8 (high-confidence duplicate)
- **Scope routing** (in-scope vs. out-of-scope product) based on product list
- **15-day clock timestamp anchoring** (`received_at`) at report ingestion
- **Drug nomenclature normalization** (brand → generic via RxNorm API)
- **AE term MedDRA coding** (lay term → preferred term via MedDRA API)
- **Span-level citation generation** (field → source text location)
- **Audit event emission** (intake complete, exception routed, HITL flagged)
- **PV API write retry logic** (exponential backoff, local buffer on failure)
- **Extraction for all fields when confidence ≥0.85** (required fields) or ≥0.70 (optional fields)

### AGENT ACTS, HUMAN NOTIFIED AFTER

- **Route to ADR-2** when `extraction_status == AUTO_COMPLETE` (all required fields confidence ≥0.85)
- **Route to exception queue** when mis-routed complaint or out-of-scope product detected
- **Route to reporter follow-up queue** when minimum required information missing
- **Buffer locally** on PV API failure (3 consecutive retries exhausted) → alert ops

### AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION

- **HITL validation required** when any required field extraction confidence <0.85
  - Case processor reviews low-confidence fields, re-keys corrections, releases to ADR-2
  - SLA: 2-hour turnaround for HITL validation
- **Duplicate case resolution** when fuzzy match confidence 0.5-0.8 (ambiguous duplicate)
  - Case processor reviews patient demographics, drug, AE description, temporal relationship
  - Decides: unique case (release to ADR-2) or link to existing case
- **Exception queue triage** when mis-routed complaint or out-of-scope product detected
  - Ops reviews exception type, decides routing (return to sender, forward to device complaint team, archive)

### HUMAN TAKES OVER (Agent Supports, Does Not Decide)

- **Reporter follow-up communication** (agent flags missing information, human contacts reporter)
  - Agent outputs: list of missing required fields per ICH E2D
  - Human: writes follow-up email to reporter, tracks response
- **PV API integration failure escalation** (agent buffers locally, human investigates root cause)
  - Agent outputs: buffered `AECasePackage` JSON with idempotency key, error message, retry count
  - Human: troubleshoots API authentication, network connectivity, SLA breach
- **Novel format handling** (agent encounters unknown file type or structure)
  - Agent outputs: raw file content, classification failure error
  - Human: develops new parser, updates format classification logic
- **Patient identifier de-identification errors** (agent extracts PII from social media post that should be masked)
  - Agent outputs: extracted patient identifiers with confidence scores
  - Human: red-teams social media cases, implements PII masking layer if needed

---

# ADR-2: Medical Triage Agent

## Agent Purpose (ADR-2)

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

---

## Escalation Triggers (ADR-2)

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

## Autonomy Matrix (ADR-2)

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

**Document Owner**: FDE Engagement Lead  
**Last Updated**: 2026-06-01
