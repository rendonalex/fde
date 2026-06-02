# CLAUDE.md

This file configures Claude Code's behavior when building the Agentic Adverse Event Triage System for Helix Therapeutics.

---

## Project Purpose

Agentic adverse event triage system for Helix Therapeutics' three marketed products (Solivian, Tezarimab, Phaedora): automates intake/extraction from heterogeneous report formats (HCP reports, patient webforms, social media, trial sites, literature) and produces medical triage recommendations (seriousness classification per ICH E2A, expectedness assessment against product RSI, reportability recommendation per FDA 21 CFR 314.80) with medical safety officer sign-off on 100% of cases.

**Key Entities**: `AECasePackage` (extracted structured data with span citations and confidence scores), `TriageRecommendation` (seriousness classification, expectedness signal, reportability recommendation with chain-of-thought reasoning), `extraction_status` (AUTO_COMPLETE, HUMAN_REQUIRED, PENDING_DUPLICATE, EXCEPTION_NOTE, REPORTER_FOLLOWUP), `routing_mode` (SHADOW, LIVE).

**For detailed entity definitions, state machines, validation rules, and integration contracts, see:**
- `specs/05a-capability-spec-intake.md` — ADR-1 (AE Intake & Data Extraction Agent)
- `specs/05b-capability-spec-triage.md` — ADR-2 (Medical Triage Agent)

---

## Repository Structure

```
g-week5/
├── specs/
│   ├── CLAUDE.md                         # This file
│   ├── 05a-capability-spec-intake.md     # ADR-1 full specification
│   ├── 05b-capability-spec-triage.md     # ADR-2 full specification
│   └── assumptions.md                    # Assumptions register with validation plan
├── input-docs/
│   ├── scenario.md                       # Engagement context (Dr. Carmichael's brief)
│   └── production-spec-checklist.md      # Specification quality criteria
├── mock-data/
│   ├── intake-queue/                     # 8 mock AE reports across format spectrum
│   ├── product-information/              # RSI profiles for 3 products
│   └── prior-cases/                      # Historical case examples
└── src/                                  # Agent implementation (to be built)
```

---

## Scope: What You SHOULD Build

### ADR-1: AE Intake & Data Extraction Agent (Prototype Phase)

1. **Format Classification** — Identify report source: HCP_TEXT, PATIENT_WEBFORM, PHONE_VTT, SOCIAL_MEDIA, TRIAL_REPORT, LITERATURE
2. **Structured Data Extraction** — Extract patient demographics, suspect drug (dose, indication, temporal relationship), AE description (narrative, MedDRA PT if coded, onset, outcome), concomitant medications, medical history
3. **Terminology Normalization** — Map suspect drug to RxNorm, AE narrative to MedDRA PT (via API or local dictionary)
4. **Confidence Scoring** — Per-field confidence [0.0, 1.0]; threshold ≥0.85 for required fields (AUTO_COMPLETE vs. HUMAN_REQUIRED)
5. **Span Citations** — Link each extracted field to source text character ranges (e.g., `"patient_age": { "value": 62, "span": "source:45-47" }`)
6. **Duplicate Detection** — Fuzzy match against recent cases (≥0.8 similarity → PENDING_DUPLICATE)
7. **Scope Routing** — Identify mis-routed device complaints (→ EXCEPTION_NOTE), insufficient minimum info (→ REPORTER_FOLLOWUP)
8. **AECasePackage Assembly** — Structured JSON output with `case_id` (UUID, idempotency key), `received_at` (immutable, anchors 15-day clock), `extraction_status`, nested entities, `span_citations`

**For full activity catalog, autonomy matrix, and validation scenarios, see `specs/05a-capability-spec-intake.md` Sections 3-4 and Section 9 (Validation Design).**

### ADR-2: Medical Triage Agent (Prototype Phase)

1. **Seriousness Classification** — Apply ICH E2A criteria (death, life-threatening, hospitalization, disability, congenital anomaly, other medically important) with chain-of-thought reasoning and span citations
2. **Expectedness Assessment** — Match AE term to product RSI using MedDRA hierarchy (exact, synonym, broader, narrower term matching); flag novel AE terms (not in RSI) as unexpected with confidence 0.0
3. **Reportability Recommendation** — Apply FDA 21 CFR 314.80 logic (serious + unexpected → 15-day expedited) and multi-jurisdictional rules (EMA, MHRA, PMDA) with rule-based justification
4. **Conservative Fallback** — When ambiguous: classify as serious, flag as unexpected, set confidence <0.70 (triggers MSO deep review)
5. **Novel Case Guardrail** — Unmatched CPT/ICD-10 → route to MSO with confidence 0.0, flag for clinical review
6. **TriageRecommendation Assembly** — Structured JSON output with `case_id` (foreign key to AECasePackage), nested entities (SeriousnessClassification, ExpectednessSignal, ReportabilityRecommendation, MSOFlags), `audit_trail` (CoT reasoning, span citations, regulatory references)

**For full activity catalog, autonomy matrix, codebook logic, and validation scenarios, see `specs/05b-capability-spec-triage.md` Sections 3-4 and Section 9 (Validation Design).**

---

## Out of Scope: What You Should NOT Build

- **Never write production PV API integrations in prototype phase** (mock data only; use JSON file reads for AECasePackage retrieval and local file writes for TriageRecommendation output)
- **Never make final reportability decisions** (MSO reviews 100% of recommendations per CMO mandate; agent provides recommendation only)
- **Never bypass confidence thresholds** (ADR-1: <0.85 required field → HUMAN_REQUIRED; ADR-2: <0.70 → MSO deep review)
- **Never modify received_at timestamp** (immutable 15-day clock anchor per FDA 21 CFR 314.80)
- **Never process device complaints** (out-of-scope; route to EXCEPTION_NOTE)
- **Never communicate with reporters, patients, or regulators** (agent-to-system communication only)
- **Never implement causality assessment decision logic** (ADR-2 surfaces causality context but does not make final causality determination; MSO decides)

---

## Critical Guard Rails

### ADR-1: Confidence-Based HITL (BLOCKING)
```python
# Required field confidence threshold
for field in REQUIRED_FIELDS:
    if extraction_confidence[field] < 0.85:
        extraction_status = "HUMAN_REQUIRED"
        route_to_case_processor_queue()
        return  # Do NOT write to PV API
```

### ADR-1: Duplicate Detection (ALWAYS)
```python
# Fuzzy match against recent cases
similarity = fuzzy_match(current_case, recent_cases)
if similarity >= 0.8:
    extraction_status = "PENDING_DUPLICATE"
    route_to_manual_review_queue()
    return  # Do NOT create new case_id
```

### ADR-1: Scope Guardrail (ALWAYS)
```python
# Device complaints route to separate system
if report_contains_device_complaint():
    extraction_status = "EXCEPTION_NOTE"
    reason = "Device complaint mis-routed to AE intake"
    route_to_device_complaint_team()
    return  # Do NOT process as AE
```

### ADR-2: Conservative Fallback (ALWAYS)
```python
# When ambiguous, classify as serious/unexpected (over-reporting safer than under-reporting)
if confidence < 0.70:
    seriousness_classification.serious = True  # Override to serious
    expectedness_signal.unexpected = True      # Override to unexpected
    mso_flags.deep_review_required = True
    log_event("CONSERVATIVE_FALLBACK_APPLIED")
```

### ADR-2: Novel AE Guardrail (ALWAYS)
```python
# Unmatched AE term → flag for MSO review
if ae_term not in product_rsi and ae_term not in meddra_dictionary:
    expectedness_signal.unexpected = True
    expectedness_signal.rsi_match = "none"
    confidence = 0.0  # Zero confidence triggers MSO deep review
    mso_flags.novel_ae_detected = True
    log_event("NOVEL_AE_FLAGGED")
```

### ADR-2: MSO Sign-Off Requirement (NON-NEGOTIABLE)
```python
# Agent outputs recommendation; MSO makes final decision
# NEVER auto-submit reportability decision to regulators
recommendation_output = {
    "recommendation": "15_DAY_EXPEDITED",  # Agent recommendation
    "mso_reviewed_at": None,                # MSO must sign off
    "mso_override": None,                   # MSO can override
    "final_decision": None                  # MSO decision required
}
```

---

## Escalation Triggers

### ADR-1 → Case Processor HITL (Human Re-Key)
- Any required field extraction confidence <0.85 → `HUMAN_REQUIRED`
- Missing minimum required information (no patient identifier, no suspect drug, no AE description) → `REPORTER_FOLLOWUP`
- Duplicate case detected (fuzzy match ≥0.8) → `PENDING_DUPLICATE`, do not create new case

### ADR-1 → Exception Queue (Mis-Routed)
- Device complaint detected → `EXCEPTION_NOTE`, route to device complaint team
- Clinical trial AE for pipeline asset detected → `EXCEPTION_NOTE`, route to sponsor obligations team
- Quality complaint with no AE component → `EXCEPTION_NOTE`, route to quality complaints team

### ADR-1 → Ops Alert
- RxNorm API failure (timeout or 3 consecutive 500 errors) → buffer drug name as-is, alert ops
- MedDRA API failure (401 unauthorized) → block all ADR-1 processing, alert ops immediately
- Exception queue overflow (>15% of volume over 24 hours) → alert ops to investigate root cause

### ADR-2 → MSO Deep Review (Patient Safety Fallback)
- Confidence <0.70 after classification → `mso_flags.deep_review_required = True`
- Novel AE term not in product RSI → `mso_flags.novel_ae_detected = True`, confidence = 0.0
- "Other medically important" criterion matched with ambiguous evidence → flag for MSO clinical judgment
- Concomitant medication causality complexity → `mso_flags.causality_complex = True`

### ADR-2 → Ops Alert
- Product RSI file not found (missing Tezarimab_RSI.md) → block ADR-2 processing, alert ops immediately
- MedDRA API failure (>50% of queries failing) → alert ops, degrade to narrative-only classification
- Novel AE rate >50% over 5-minute window → alert ops (indicates missing/corrupted RSI)

**For full escalation logic and autonomy matrices, see:**
- `specs/05a-capability-spec-intake.md` Section 4 (Autonomy Matrix)
- `specs/05b-capability-spec-triage.md` Section 4 (Autonomy Matrix)

---

## Integration Constraints

### ADR-1 Integrations (Prototype Phase — Mock Data Only)

**PV Case Management System API** (production endpoint; mock in prototype):
- Write: `POST /api/v1/cases` (ADR-1 creates AECasePackage)
- Read: `GET /api/v1/cases/{case_id}` (duplicate check)
- Authentication: To be confirmed in production (assume OAuth 2.0 for spec)
- **Prototype Behavior**: Write AECasePackage to local JSON file (`output/adr1/{case_id}.json`), read recent cases from `mock-data/prior-cases/` for duplicate detection

**RxNorm API** (normalize suspect drug terminology):
- Endpoint: `GET /REST/rxcui.json?name={drug_name}`
- Response: `{ "idGroup": { "rxnormId": ["123456"] } }`
- Timeout: 5 seconds; if timeout → use drug name as-is, set `drug_normalized = False`, do NOT block processing
- Retry: On 500 error, retry once after 2 seconds; if still fails → use drug name as-is
- **Prototype Behavior**: Use RxNorm REST API directly (public endpoint, no auth required)

**MedDRA API** (code AE narrative to Preferred Terms):
- Endpoint: `GET /api/v1/terms?query={ae_narrative}&hierarchy=PT`
- Response: `{ "preferred_term": "Headache", "pt_code": "10019211", "soc": "Nervous system disorders" }`
- Authentication: API key (MedDRA subscription required)
- Timeout: 5 seconds; if timeout → use narrative as-is, set `meddra_coded = False`, do NOT block processing
- **Prototype Behavior**: Use local MedDRA dictionary file (`mock-data/meddra_dictionary.json`) for PT lookup

**For complete error handling (HTTP status codes, fallback behavior, rate limits), see `specs/05a-capability-spec-intake.md` Section 10 (Integration Contracts).**

### ADR-2 Integrations (Prototype Phase — Mock Data Only)

**PV Case Management System API** (production endpoint; mock in prototype):
- Read: `GET /api/v1/cases/{case_id}` (ADR-2 retrieves AECasePackage from ADR-1)
- Write: `POST /api/v1/triage-recommendations` (ADR-2 creates TriageRecommendation)
- **Prototype Behavior**: Read AECasePackage from `output/adr1/{case_id}.json`, write TriageRecommendation to `output/adr2/{case_id}_triage.json`

**Product RSI Database** (retrieve Reference Safety Information):
- Read: Local file system, `/mock-data/product-information/{product_name}_RSI.md`
- Format: Markdown with AE term list (one term per line under `## Adverse Events` section)
- **Error Handling**: If RSI file not found → block ADR-2 processing, alert ops, do NOT proceed with null RSI
- **Prototype Behavior**: Read RSI files directly from `mock-data/product-information/` (Solivian_RSI.md, Tezarimab_RSI.md, Phaedora_RSI.md)

**MedDRA API** (hierarchy queries for expectedness matching):
- Endpoint: `GET /api/v1/hierarchy?pt_code={pt_code}&direction=broader`
- Response: `{ "pt": "Headache", "hlt": "Headaches", "soc": "Nervous system disorders" }`
- **Prototype Behavior**: Use local MedDRA dictionary file (`mock-data/meddra_dictionary.json`) with hierarchy relationships

**Audit Trail Store** (write classification reasoning for FDA inspection):
- Write: `POST /api/v1/audit-trail` (structured JSON: case_id, classification_reasoning, span_citations, regulatory_references, timestamps)
- **Prototype Behavior**: Write audit trail to `output/adr2/{case_id}_audit.json`
- **CRITICAL**: Audit trail write failure must NOT block MSO review; buffer locally, emit alert, retry asynchronously

**For complete error handling and fallback behavior, see `specs/05b-capability-spec-triage.md` Section 10 (Integration Contracts).**

---

## Naming Conventions

### Entity and Field Names
- **Entities**: PascalCase (AECasePackage, TriageRecommendation, SeriousnessClassification, ExpectednessSignal)
- **Field names**: snake_case (case_id, received_at, extraction_status, suspect_drug, ae_description, seriousness_classification)
- **Nested objects**: PascalCase type, snake_case attributes (Patient.age, SuspectDrug.rxnorm_code, AEDescription.meddra_pt)

### Enums
- **extraction_status**: SCREAMING_SNAKE_CASE (AUTO_COMPLETE, HUMAN_REQUIRED, PENDING_DUPLICATE, EXCEPTION_NOTE, REPORTER_FOLLOWUP)
- **ICH E2A criteria**: snake_case (death, life_threatening, hospitalization, disability, congenital_anomaly, other_medically_important)
- **Reportability recommendation**: SCREAMING_SNAKE_CASE (15_DAY_EXPEDITED, PERIODIC, NON_REPORTABLE)
- **RSI match types**: snake_case (exact, broader, narrower, synonym, none)

### Timestamps
- **Format**: ISO 8601 with timezone (e.g., "2026-06-01T14:30:00Z")
- **Immutable fields**: received_at (ADR-1), created_at (both agents)
- **Audit fields**: created_at, updated_at, created_by, updated_by (for state tracking)

### Identifiers
- **case_id**: UUID v4, primary key, idempotency key for PV API writes
- **Format**: HCP_TEXT, PATIENT_WEBFORM, PHONE_VTT, SOCIAL_MEDIA, TRIAL_REPORT, LITERATURE (SCREAMING_SNAKE_CASE)

---

## When to Ask vs When to Decide

### Decide Alone (Do NOT Ask)

**ADR-1**:
- Route to HUMAN_REQUIRED when any required field confidence <0.85
- Route to PENDING_DUPLICATE when fuzzy match ≥0.8
- Route to EXCEPTION_NOTE when device complaint detected
- Route to REPORTER_FOLLOWUP when minimum required information missing
- Normalize drug name via RxNorm (use as-is if API fails)
- Code AE narrative via MedDRA (use narrative as-is if API fails)
- Set received_at timestamp on ingestion (immutable)
- Generate case_id UUID (idempotency key)
- Extract span citations for every field

**ADR-2**:
- Apply ICH E2A criteria with CoT reasoning
- Match AE term to product RSI using MedDRA hierarchy
- Recommend reportability per FDA 21 CFR 314.80 logic
- Override to serious/unexpected when confidence <0.70
- Flag novel AE terms with confidence 0.0 for MSO review
- Generate audit trail with span citations and regulatory references

### Ask the User Before Proceeding

**ADR-1**:
- RxNorm API down (all retries exhausted): "Should I proceed with un-normalized drug names or wait for API restoration?"
- MedDRA API 401 unauthorized: "MedDRA license expired. Should I block ADR-1 processing or proceed with narrative-only extraction?"
- Exception queue overflow (>15% rate): "Exception rate elevated. Should I investigate root cause or continue processing?"

**ADR-2**:
- Product RSI file not found: "Tezarimab RSI missing. Should I block ADR-2 processing or treat all AEs as novel (confidence 0.0)?"
- MedDRA API failure (>50% queries failing): "MedDRA API degraded. Should I proceed with narrative-only expectedness assessment (all cases flagged for MSO review) or wait for API restoration?"

### Never Ask (Always Apply Guard Rail)

- "Should I calculate seriousness if confidence is 0.65?" → NO. Always override to serious + MSO deep review when confidence <0.70.
- "Should I proceed with null product RSI?" → NO. Always block ADR-2 processing if RSI unavailable (cannot assess expectedness).
- "Should I auto-submit reportability decision to FDA?" → NO. MSO reviews 100% of recommendations per CMO mandate.
- "Should I modify received_at timestamp?" → NO. Immutable 15-day clock anchor per FDA regulation.

---

## Assumptions & Risks

**Critical assumptions** (see `specs/assumptions.md` for full register):

| ID | Assumption | Confidence | Risk if Wrong | Validation Plan |
|----|-----------|-----------|---------------|-----------------|
| [A1] | 6,000 AE reports/year volume | High (80%) | Volume spike → capacity bottleneck | Week 1: Validate with actual intake logs |
| [A2] | 70% EDI / 30% non-EDI channel split | Medium (65%) | HITL rate and IDP build scope shift | Week 1: Sample 50 recent cases |
| [A3] | 88% auto-extraction rate (12% HITL) | Medium (65%) | Higher HITL → economics erode | Prototype validation: 8 mock cases |
| [A4] | RxNorm API available (public endpoint) | High (85%) | Drug normalization blocked | Week 1: Test API reliability |
| [A5] | MedDRA license active and API accessible | Low (50%) | AE coding blocked → narrative-only | Week 1: Confirm subscription status |
| [A6] | ICH E2A criteria explicitly codifiable | Medium (70%) | "Other medically important" ambiguity → MSO override rate rises | Prototype: Test ambiguous cases |
| [A7] | Product RSI files complete and up-to-date | Medium (60%) | Novel AE false-positives → MSO workload increases | Week 1: Validate RSI against last 6 months of cases |
| [A8] | MSO accepts 88% of recommendations as-is | Medium (65%) | Higher override rate → ROI erodes | Prototype: 8-case acceptance test with Dr. Iyer |

**Prototype-specific risks**:
- [A9] Mock data representativeness: 8 cases may not cover full heterogeneity spectrum (mitigation: select cases across all formats and complexity levels)
- [A10] MedDRA hierarchy completeness: Local dictionary may lack recent updates (mitigation: use 2025 Q4 MedDRA release)

**For full assumptions register, confidence levels, and validation owners, see `specs/assumptions.md`.**

---

## Validation Design

### ADR-1 Validation (Happy Path, Edge Cases, Failure Modes)

**Happy Path Scenarios**:
- HP-1: Structured HCP report → AUTO_COMPLETE with confidence ≥0.85, span citations 100% complete
- HP-2: Patient webform JSON → AUTO_COMPLETE, RxNorm normalization successful, MedDRA coding successful
- HP-3: Duplicate detection (high confidence) → PENDING_DUPLICATE, no new case_id created

**Edge Cases**:
- EC-1: Missing optional fields (medical history null) → AUTO_COMPLETE (does NOT trigger HUMAN_REQUIRED)
- EC-2: Ambiguous date estimation ("a few weeks ago") → estimate as received_at - 21 days, set `date_estimated = True`
- EC-3: Brand vs. generic drug name variation → RxNorm normalization handles via synonym matching
- EC-4: Concomitant medication extraction from table format → parse structured table, extract drug names with dosage
- EC-5: Ambiguous duplicate (fuzzy match 0.5-0.8) → route to manual review queue for case processor adjudication

**Failure Modes**:
- FM-1: RxNorm API timeout → use drug name as-is, set `drug_normalized = False`, proceed
- FM-2: MedDRA API 401 unauthorized → block ADR-1 processing, alert ops immediately
- FM-3: Missing minimum required information → REPORTER_FOLLOWUP, do not create case
- FM-4: Exception queue overflow (>15% rate) → alert ops to investigate root cause

**For complete validation scenarios with inputs, expected outputs, and pass criteria, see `specs/05a-capability-spec-intake.md` Section 9 (Validation Design).**

### ADR-2 Validation (Happy Path, Edge Cases, Failure Modes)

**Happy Path Scenarios**:
- HP-1: Serious AE classification (death criterion) → serious = True, criteria_matched = ["death"], confidence ≥0.95
- HP-3: Expectedness assessment (exact RSI match) → unexpected = False, rsi_match = "exact", confidence ≥0.95
- HP-5: Reportability recommendation (serious + unexpected) → 15_DAY_EXPEDITED, jurisdictions = ["FDA", "EMA", "MHRA"]

**Edge Cases**:
- EC-1: Ambiguous "other medically important" criterion → serious = True, confidence 0.60-0.75, override to MSO deep review if <0.70
- EC-2: Novel AE term (not in RSI, not in MedDRA) → unexpected = True, confidence = 0.0, MSO deep review required
- EC-3: Term specificity variance (Stevens-Johnson Syndrome vs. Rash) → unexpected = True (SJS more severe), MSO deep review

**Failure Modes**:
- FM-1: Product RSI file not found → block ADR-2 processing, alert ops, do NOT proceed with null RSI
- FM-2: MedDRA API failure (3 retries exhausted) → alert ops, use narrative for classification, set confidence = 0.0, MSO deep review
- FM-3: Audit trail write failure → buffer locally, alert ops, do NOT block MSO review

**For complete validation scenarios, see `specs/05b-capability-spec-triage.md` Section 9 (Validation Design).**

---

## Document Control

- **Version**: 1.0
- **Created**: 2026-06-01
- **Owner**: FDE Engagement Lead
- **Engagement Context**: Final Exam, Gate 5b (8-hour practical)
- **Active Specifications**: 
  - `specs/05a-capability-spec-intake.md` (ADR-1)
  - `specs/05b-capability-spec-triage.md` (ADR-2)
- **Prototype Deliverable**: End-to-end processing of 8 mock cases with validation report
- **Next Milestone**: Curveball adaptation at 13:30 CET, final submission at 17:00 CET
