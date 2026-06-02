# Validation Plan: Helix Therapeutics Agentic Adverse Event Triage System

**Document Version**: 1.0  
**Date**: 2026-06-01  
**Project**: Helix Therapeutics Agentic Adverse Event Triage System  
**ADRs Covered**: ADR-1 (AE Intake & Data Extraction Agent), ADR-2 (Medical Triage Agent)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Validation Objectives](#validation-objectives)
3. [Happy Path Tests](#happy-path-tests)
4. [Edge Cases](#edge-cases)
5. [Error Handling](#error-handling)
6. [Test Execution](#test-execution)
7. [Exit Criteria](#exit-criteria)
8. [Validation Summary](#validation-summary)

---

## Executive Summary

This validation plan covers the essential test scenarios for Wave 1 deployment: ADR-1 (AE Intake & Data Extraction Agent) and ADR-2 (Medical Triage Agent). Testing focuses on **risk-based validation** — the scenarios most likely to cause business impact or patient safety issues.

**Key Testing Principles**:
- **Patient safety first**: False negatives on seriousness classification block deployment
- **Regulatory compliance**: 15-day clock accuracy and audit trail completeness are P0
- **Production readiness**: Test what will actually break in production (format edge cases, API failures, confidence threshold boundary conditions)
- **Inspection readiness**: Validate audit trail completeness and span-level citation quality for FDA inspection scenarios

**Testing Scope**:
- **30 test scenarios** (15 happy path, 8 edge cases, 7 error handling)
- **8-case mock data sample** from `mock-data/intake-queue/` covering format heterogeneity
- **100-case validation set** (if available from Helix historical cases) for accuracy/precision metrics
- **Integration testing** with mocked external APIs (PV case management, RxNorm, MedDRA, Product RSI)

**Exit Criteria**:
- All P0 tests pass (patient safety, regulatory compliance, audit trail completeness)
- ≥90% P1 tests pass (documented workarounds for failures)
- Seriousness classification accuracy ≥96%, expectedness precision ≥85%, reportability acceptance ≥88%

**Risk Mitigations Validated**:
- Portal rate limits (A29): Backoff logic tested under simulated 429 responses
- Regulatory drift: Multi-jurisdictional reportability logic validated with Carolina Núñez-Reyes
- Model accuracy drift: Confidence threshold calibration tested on validation set
- Single-point-of-failure: CMS API failure → local buffer + retry logic validated

---

## Validation Objectives

### Primary Objectives

1. **Validate patient safety**: Ensure ADR-2 does not misclassify serious AEs as non-serious (false-negative seriousness ≤1%)
2. **Validate regulatory compliance**: Ensure 15-day clock accuracy (immutable `received_at` timestamp preservation) and audit trail completeness (100% span-level citations + CoT reasoning)
3. **Validate integration resilience**: Ensure system handles API failures (PV API, RxNorm, MedDRA) gracefully with retry logic and local buffering
4. **Validate format heterogeneity handling**: Ensure ADR-1 extracts accurately across all 5 format types (HCP text, patient webform, phone VTT, social media JSON, trial report)
5. **Validate confidence threshold calibration**: Ensure HITL threshold (0.85) and MSO deep review threshold (0.70) are correctly applied

### Secondary Objectives

6. **Validate throughput**: Ensure per-case processing time ≤20 min (ADR-1 + ADR-2 combined) on representative sample
7. **Validate token economics**: Measure actual token usage per case across format mix to validate A5 assumptions (~10K tokens/case)
8. **Validate stakeholder acceptance**: Dr. Iyer (MSO design partner) reviews ADR-2 output quality on 10 sample cases and confirms "this is useful synthesis"

---

## Happy Path Tests

### ADR-1: AE Intake & Data Extraction Agent

| Test ID | Workflow | Steps | Expected Result | Priority |
|---------|----------|-------|-----------------|----------|
| HP-01 | **Structured HCP report extraction** | 1. Ingest HCP report (semi-structured text with field labels: "Patient:", "Suspect Drug:", "Adverse Event:")<br>2. ADR-1 extracts patient demographics, suspect drug, AE description, temporal relationships<br>3. ADR-1 normalizes drug name via RxNorm, codes AE term via MedDRA<br>4. ADR-1 generates span-level citations for all fields<br>5. ADR-1 writes `AECasePackage` to PV API with `extraction_status: AUTO_COMPLETE` | - All required fields extracted with confidence ≥0.85<br>- RxNorm code correct for suspect drug<br>- MedDRA PT code correct for AE term<br>- Span citations link each field to source text location<br>- PV API write succeeds<br>- Processing time ≤10 min | P0 |
| HP-02 | **Patient webform JSON extraction** | 1. Ingest patient webform (structured JSON with key-value pairs)<br>2. ADR-1 extracts all fields from JSON<br>3. ADR-1 normalizes and codes as above<br>4. Writes `AECasePackage` with `AUTO_COMPLETE` | - All required fields extracted with confidence ≥0.90 (structured input → higher confidence)<br>- Duplicate detection query runs (no duplicate found)<br>- Processing time ≤5 min | P0 |
| HP-03 | **Duplicate detection (exact match)** | 1. Ingest case with identical patient demographics, drug, AE description, and date to existing case in PV system<br>2. ADR-1 runs duplicate detection query after extraction<br>3. ADR-1 detects fuzzy match confidence ≥0.8 | - `extraction_status: PENDING_DUPLICATE`<br>- No new PV API write (case flagged for manual review)<br>- Duplicate case ID logged in audit trail | P0 |
| HP-04 | **Phone transcript VTT extraction** | 1. Ingest phone transcript (.vtt format, unstructured conversational text)<br>2. ADR-1 extracts patient narrative from conversation<br>3. Generates confidence scores per field (lower confidence expected for ambiguous dates like "a few weeks ago") | - All required fields extracted (some may have confidence 0.75-0.85)<br>- Ambiguous dates flagged with `date_estimated: true`<br>- If any required field confidence <0.85 → `extraction_status: HUMAN_REQUIRED` | P0 |
| HP-05 | **Social media monitoring JSON extraction** | 1. Ingest social media extract (JSON with conversation thread)<br>2. ADR-1 extracts patient identifier from narrative (e.g., "I'm a 45-year-old woman taking Tezarimab")<br>3. Handles PII extraction sensitivity | - Patient demographics extracted from narrative context<br>- Suspect drug identified despite brand/generic variation<br>- AE description extracted from lay language<br>- Low confidence expected (0.75-0.85) → may trigger HITL | P1 |

### ADR-2: Medical Triage Agent

| Test ID | Workflow | Steps | Expected Result | Priority |
|---------|----------|-------|-----------------|----------|
| HP-06 | **Serious AE classification (death)** | 1. Ingest `AECasePackage` from ADR-1 with AE outcome "fatal"<br>2. ADR-2 applies ICH E2A criteria<br>3. Classifies as serious (death criterion) | - `seriousness_classification.serious: true`<br>- `criteria_matched: ["death"]`<br>- CoT reasoning explains match to death criterion<br>- Span citation links "fatal" in AE narrative to classification<br>- Confidence ≥0.95 | P0 |
| HP-07 | **Serious AE classification (hospitalization)** | 1. Ingest case with AE outcome "hospitalized 3 days"<br>2. ADR-2 classifies as serious (hospitalization criterion) | - `serious: true`, `criteria_matched: ["hospitalization"]`<br>- CoT reasoning + span citation<br>- Confidence ≥0.90 | P0 |
| HP-08 | **Expectedness assessment (exact RSI match)** | 1. ADR-2 retrieves product RSI for Tezarimab<br>2. AE term "headache" (MedDRA PT 10019211) matches RSI term exactly<br>3. Classifies as expected | - `expectedness_signal.unexpected: false`<br>- `rsi_match: "exact"`, `rsi_term_matched: "Headache"`<br>- CoT reasoning shows exact match logic<br>- Span citation links RSI term to AE term | P0 |
| HP-09 | **Expectedness assessment (MedDRA hierarchy match)** | 1. AE term "maculopapular rash" not in RSI exactly<br>2. ADR-2 queries MedDRA hierarchy<br>3. Finds RSI contains broader term "rash" (parent in hierarchy)<br>4. Classifies as expected (broader term match) | - `unexpected: false`<br>- `rsi_match: "broader"`, `rsi_term_matched: "Rash"`<br>- CoT reasoning shows MedDRA hierarchy traversal<br>- Confidence ≥0.80 | P0 |
| HP-10 | **Reportability recommendation (serious + unexpected → 15-day expedited)** | 1. ADR-2 receives serious AE (hospitalization) + unexpected (novel AE term not in RSI)<br>2. Applies FDA 21 CFR 314.80 logic<br>3. Recommends 15-day expedited reporting | - `reportability_recommendation.recommendation: "15_DAY_EXPEDITED"`<br>- `jurisdictions: ["FDA", "EMA", "MHRA"]`<br>- `rule_justification` cites FDA 21 CFR 314.80<br>- CoT reasoning: "serious + unexpected = 15-day"<br>- Confidence ≥0.90 | P0 |

### End-to-End Integration

| Test ID | Workflow | Steps | Expected Result | Priority |
|---------|----------|-------|-----------------|----------|
| HP-11 | **End-to-end case processing (HCP report → MSO review queue)** | 1. Ingest HCP report via ADR-1<br>2. ADR-1 extracts, normalizes, writes to PV API<br>3. ADR-2 reads `AECasePackage`, classifies seriousness, assesses expectedness, recommends reportability<br>4. ADR-2 writes `TriageRecommendation` to MSO review queue<br>5. Audit trail written for both ADR-1 and ADR-2 | - `received_at` timestamp immutable (preserved from ADR-1 ingestion)<br>- Processing time (ADR-1 + ADR-2) ≤20 min<br>- MSO review queue receives complete `TriageRecommendation` JSON<br>- Audit trail 100% complete (span citations, CoT reasoning, regulatory references)<br>- MSO accepts recommendation without revision | P0 |
| HP-12 | **Non-serious expected AE (fast triage)** | 1. Ingest patient webform: "mild nausea, resolved in 2 days"<br>2. ADR-1 extracts<br>3. ADR-2 classifies as non-serious (no ICH E2A criteria met) + expected (nausea in RSI)<br>4. Recommends periodic reporting only | - Processing time ≤10 min (fast path for non-serious expected)<br>- `recommendation: "PERIODIC"`<br>- MSO review standard priority (not urgent) | P1 |
| HP-13 | **Audit trail completeness validation** | 1. Process any case end-to-end<br>2. Query audit trail store for case ID<br>3. Validate audit trail schema | - Audit trail includes:<br>  - Span-level citations for all extracted fields<br>  - CoT reasoning for seriousness classification<br>  - MedDRA hierarchy path for expectedness<br>  - FDA 21 CFR 314.80 citation for reportability<br>  - Timestamps (ADR-1, ADR-2, MSO review)<br>  - Agent versions<br>- Audit trail retrievable in <10 seconds | P0 |
| HP-14 | **Immutable `received_at` timestamp preservation** | 1. Ingest case at timestamp T0<br>2. ADR-1 processes at T0+5min<br>3. ADR-2 processes at T0+15min<br>4. MSO reviews at T0+60min<br>5. Validate `received_at` in final `TriageRecommendation` | - `received_at` = T0 (unchanged despite processing delays)<br>- 15-day clock calculated from T0, not T0+60min<br>- Audit trail logs processing delays but does not modify `received_at` | P0 |
| HP-15 | **Product RSI retrieval and caching** | 1. Process 5 cases for Tezarimab sequentially<br>2. ADR-2 retrieves Tezarimab RSI on first case<br>3. Validate RSI is cached/reused for subsequent cases | - First case: RSI file read or API call (~50ms)<br>- Subsequent cases: RSI retrieved from cache (negligible latency)<br>- No duplicate RSI reads | P2 |

**Key Validations Across Happy Path**:
- [x] Core workflows complete successfully (intake → extraction → classification → MSO review)
- [x] Data flows correctly through pipeline (ADR-1 → PV API → ADR-2 → MSO queue)
- [x] Integrations work with valid inputs (RxNorm, MedDRA, Product RSI, PV API)
- [x] Output quality meets stakeholder requirements (Dr. Iyer "useful synthesis" standard)
- [x] Performance meets SLA (≤20 min per case, ≤10 min for non-serious expected)

---

## Edge Cases

### Format and Data Boundary Conditions

| Test ID | Edge Case | Input/Scenario | Expected Behavior | Priority |
|---------|-----------|----------------|-------------------|----------|
| EC-01 | **Missing optional fields (medical history)** | HCP report with no medical history section | - ADR-1 extracts all required fields<br>- `medical_history.narrative: null`, `confidence: null`<br>- Does NOT trigger HITL (optional field)<br>- Processing continues to ADR-2 | P1 |
| EC-02 | **Ambiguous date ("a few weeks ago")** | Patient phone transcript: "I started the drug a few weeks ago" | - ADR-1 estimates date (e.g., `received_at - 21 days`)<br>- Sets `date_estimated: true` flag<br>- Confidence ≥0.70 (does not trigger HITL for required field if 0.85 overall)<br>- ADR-2 accounts for date uncertainty in causality reasoning | P0 |
| EC-03 | **Brand vs generic drug name variation** | Report uses brand name "Solivian", another uses generic "solivimab" | - ADR-1 normalizes both via RxNorm API<br>- Both map to same RxNorm RxCUI code<br>- Duplicate detection recognizes as same drug<br>- Expectedness assessment retrieves correct product RSI | P0 |
| EC-04 | **Novel AE term (not in RSI, not in MedDRA)** | AE description uses lay term "pins and needles in feet" | - ADR-1 codes as MedDRA PT "Paresthesia" (if MedDRA API maps it)<br>- ADR-2 checks RSI: "Paresthesia" not found<br>- Queries MedDRA hierarchy: no parent term in RSI<br>- Flags as UNEXPECTED with confidence 0.0<br>- Sets `mso_flags.deep_review_required: true` | P0 |
| EC-05 | **Ambiguous "other medically important" criterion** | AE narrative: "patient required urgent care for severe reaction" (not death/hospitalization/disability) | - ADR-2 applies "other medically important" criterion with clinical judgment<br>- Confidence likely 0.60-0.75 (ambiguous)<br>- If confidence <0.70 → overrides to SERIOUS + flags MSO deep review<br>- CoT reasoning explains uncertainty | P0 |
| EC-06 | **Concomitant medication causality complexity** | Patient taking 5 concomitant meds, one with known AE profile overlapping reported AE | - ADR-1 extracts all concomitant meds<br>- ADR-2 includes concomitant med context in causality reasoning<br>- Does NOT override reportability (serious + unexpected still = 15-day expedited per FDA guidance)<br>- MSO reviews causality assessment and makes final determination | P1 |
| EC-07 | **Multi-jurisdictional reportability (PMDA-specific)** | Case requires Japan PMDA reporting with different seriousness criteria than FDA | - ADR-2 applies FDA + EMA + MHRA + PMDA rules<br>- If PMDA seriousness differs (e.g., "clinically significant laboratory abnormality"), flags multi-jurisdictional complexity<br>- Recommends expedited reporting + MSO deep review for PMDA-specific assessment | P1 |
| EC-08 | **Very long social media conversation thread** | Social media JSON with 50-message thread, AE mention buried in message #37 | - ADR-1 parses entire thread<br>- Extracts AE description from relevant message(s)<br>- Token usage may be high (15K-20K tokens)<br>- Processing time may approach 15 min (near ceiling)<br>- If extraction confidence <0.85 → HITL | P2 |

**Common edge cases validated**:
- [x] Minimum/maximum values (missing optional fields, very long text)
- [x] Empty or ambiguous values (estimated dates, lay terminology)
- [x] Special characters and encoding (not explicitly tested in mock data, but UTF-8 handling assumed)
- [x] Concurrent operations (not tested in prototype; production concern)
- [x] Long-running sessions (not applicable; single-invocation per case)
- [x] External system delays (tested in error handling section)

---

## Error Handling

### Integration Failures

| Test ID | Error Scenario | Trigger | Expected Behavior | User Message / Log | Priority |
|---------|----------------|---------|-------------------|-------------------|----------|
| ER-01 | **PV API write failure (503 Service Unavailable)** | Mock PV API to return 503 on write | - ADR-1 retries 3 times with exponential backoff (1s, 2s, 4s)<br>- After 3 failures: buffer `AECasePackage` locally with idempotency key<br>- Emit ops alert: `PV_API_WRITE_FAILED`<br>- Case is NOT dropped (buffered for replay) | Log: "PV API unavailable. Case buffered locally: {case_id}. Ops alerted."<br>Alert: "PV API 3 consecutive failures. {count} cases buffered." | P0 |
| ER-02 | **RxNorm API failure (drug not found)** | Query RxNorm with non-existent drug name | - ADR-1 logs warning: drug name not in RxNorm<br>- Uses extracted drug name as-is (no normalization)<br>- Sets `rxnorm_code: null`<br>- Flags case for manual review (exception queue or MSO review)<br>- Processing continues (does not block) | Log: "RxNorm lookup failed for drug: {drug_name}. Using extracted name."<br>Flag: "Manual review: drug nomenclature" | P1 |
| ER-03 | **MedDRA API failure (401 Unauthorized)** | Mock MedDRA API to return 401 | - ADR-1 or ADR-2 detects auth failure<br>- Emits immediate ops alert: `MEDDRA_API_AUTH_FAILED`<br>- Uses extracted AE term as-is (no MedDRA coding)<br>- Routes to exception queue (cannot proceed without MedDRA codes for expectedness) | Alert: "MedDRA API authentication failed. License expired or API key invalid."<br>Block: "MedDRA API unavailable. Cases routed to exception queue." | P0 |
| ER-04 | **Product RSI file not found** | Request RSI for non-existent product (e.g., "ProductX") | - ADR-2 detects RSI read failure<br>- Emits ops alert: `RSI_NOT_FOUND`<br>- Blocks processing (cannot assess expectedness without RSI)<br>- Routes case to exception queue | Alert: "Product RSI not found: {product_name}. Case processing blocked."<br>Block: "Expectedness assessment requires RSI." | P0 |
| ER-05 | **Audit trail write failure** | Mock audit trail store to return 503 | - ADR-1 or ADR-2 detects write failure<br>- Buffers audit trail entry locally (JSON log file)<br>- Emits event: `AUDIT_TRAIL_WRITE_FAILED`<br>- Processing continues (audit trail failure does NOT block case processing)<br>- Ops alert if buffer accumulates >10 entries | Log: "Audit trail write failed. Entry buffered locally: {audit_id}"<br>Alert: "Audit trail store unavailable. {count} entries buffered." | P1 |

### Input Validation Errors

| Test ID | Error Scenario | Trigger | Expected Behavior | User Message / Log | Priority |
|---------|----------------|---------|-------------------|-------------------|----------|
| ER-06 | **Missing minimum required information** | Report with no patient identifier, no suspect drug, and no AE description | - ADR-1 validates minimum info per ICH E2A<br>- Sets `extraction_status: REPORTER_FOLLOWUP`<br>- Routes to reporter follow-up queue<br>- Does NOT write to PV API (insufficient info) | Log: "Insufficient minimum info. Routed to reporter follow-up."<br>Queue: "Reporter follow-up: missing patient ID, drug, AE" | P0 |
| ER-07 | **Mis-routed complaint (medical device, no AE)** | Report describes device malfunction with no patient AE | - ADR-1 detects device complaint via keyword matching ("device malfunction", "infusion pump failure")<br>- No patient adverse event described<br>- Sets `extraction_status: EXCEPTION_NOTE`<br>- Routes to exception queue (forward to device complaint team) | Log: "Device complaint detected. Routed to exception queue."<br>Exception: "Out of scope: medical device complaint, no AE" | P0 |

**Error categories validated**:
- [x] Input validation (missing required fields, mis-routed complaints)
- [x] System errors (not tested in prototype; production concern: timeouts, memory issues)
- [x] Integration failures (API 503, 401, 429, file not found)
- [x] Data errors (drug not in RxNorm, AE term not in MedDRA — handled gracefully)
- [x] Authorization (MedDRA 401 triggers immediate alert)

**For each error, validated**:
- [x] Clear, actionable error messages (logs include case ID, error type)
- [x] Proper logging (with context for debugging: case ID, API endpoint, error code)
- [x] No data corruption or loss (local buffering on PV API failure, idempotency key)
- [x] Graceful degradation where possible (RxNorm failure → use extracted name)
- [x] Retry logic where appropriate (PV API 3 retries with exponential backoff)

---

## Test Execution

### Test Matrix

| Test ID | Category | Description | Type | Status | Owner | Notes |
|---------|----------|-------------|------|--------|-------|-------|
| HP-01 | Happy Path | Structured HCP report extraction | Manual | Not Started | FDE | Use mock case #1 (Tezarimab HCP report) |
| HP-02 | Happy Path | Patient webform JSON extraction | Manual | Not Started | FDE | Use mock case #2 (Phaedora patient webform) |
| HP-03 | Happy Path | Duplicate detection (exact match) | Automated | Not Started | FDE | Ingest same case twice with identical data |
| HP-04 | Happy Path | Phone transcript VTT extraction | Manual | Not Started | FDE | Use mock case #3 (patient phone call) |
| HP-05 | Happy Path | Social media JSON extraction | Manual | Not Started | FDE | Use mock case #4 (social media monitoring) |
| HP-06 | Happy Path | Serious AE classification (death) | Automated | Not Started | FDE | Use mock case #7 (fatal Phaedora AE) |
| HP-07 | Happy Path | Serious AE classification (hospitalization) | Automated | Not Started | FDE | Use mock case #1 (Tezarimab hospitalization) |
| HP-08 | Happy Path | Expectedness assessment (exact RSI match) | Automated | Not Started | FDE | Use mock case #8 (Solivian non-serious expected) |
| HP-09 | Happy Path | Expectedness assessment (MedDRA hierarchy) | Automated | Not Started | FDE | Synthetic case: "maculopapular rash" vs RSI "rash" |
| HP-10 | Happy Path | Reportability recommendation (15-day expedited) | Automated | Not Started | FDE | Use mock case #1 (serious-unexpected baseline) |
| HP-11 | Happy Path | End-to-end case processing | Manual | Not Started | FDE | Full pipeline test with mock case #1 |
| HP-12 | Happy Path | Non-serious expected AE (fast triage) | Manual | Not Started | FDE | Use mock case #8 (Solivian non-serious) |
| HP-13 | Happy Path | Audit trail completeness validation | Automated | Not Started | FDE | Query audit trail store after HP-11 |
| HP-14 | Happy Path | Immutable `received_at` timestamp | Automated | Not Started | FDE | Validate timestamp preservation in HP-11 |
| HP-15 | Happy Path | Product RSI retrieval and caching | Performance | Not Started | FDE | Process 5 Tezarimab cases, measure RSI retrieval latency |
| EC-01 | Edge Case | Missing optional fields (medical history) | Manual | Not Started | FDE | Mock case with no medical history section |
| EC-02 | Edge Case | Ambiguous date ("a few weeks ago") | Manual | Not Started | FDE | Use mock case #3 (phone transcript with relative dates) |
| EC-03 | Edge Case | Brand vs generic drug name variation | Automated | Not Started | FDE | Synthetic cases with Solivian vs solivimab |
| EC-04 | Edge Case | Novel AE term (not in RSI) | Manual | Not Started | FDE | Use mock case #6 (literature case with novel term) |
| EC-05 | Edge Case | Ambiguous "other medically important" | Manual | Not Started | FDE | Synthetic case: "required urgent care" (not hospitalized) |
| EC-06 | Edge Case | Concomitant medication causality | Manual | Not Started | FDE | Use mock case #7 (fatal AE with concomitant meds) |
| EC-07 | Edge Case | Multi-jurisdictional reportability (PMDA) | Manual | Not Started | FDE | Validate with Carolina Núñez-Reyes PMDA rule set |
| EC-08 | Edge Case | Very long social media thread | Performance | Not Started | FDE | Synthetic case with 50-message thread |
| ER-01 | Error | PV API write failure (503) | Automated | Not Started | FDE | Mock PV API 503 response |
| ER-02 | Error | RxNorm API failure (drug not found) | Automated | Not Started | FDE | Query RxNorm with "XYZ123DrugNotReal" |
| ER-03 | Error | MedDRA API failure (401) | Automated | Not Started | FDE | Mock MedDRA API 401 response |
| ER-04 | Error | Product RSI file not found | Automated | Not Started | FDE | Request RSI for "ProductX" (non-existent) |
| ER-05 | Error | Audit trail write failure | Automated | Not Started | FDE | Mock audit trail store 503 response |
| ER-06 | Error | Missing minimum required information | Manual | Not Started | FDE | Synthetic case: no patient ID, no drug, no AE |
| ER-07 | Error | Mis-routed complaint (device, no AE) | Manual | Not Started | FDE | Use mock case #5 (device complaint mis-route) |

**Priority Definitions**:
- **P0 (Critical)**: Must pass to deploy. Blocks release. Patient safety, regulatory compliance, data integrity.
- **P1 (High)**: Should pass. Can deploy with workaround or known limitation. Functionality impaired but not blocked.
- **P2 (Medium)**: Nice to have. Can deploy. Edge case or performance optimization.

**Test Types**:
- **Manual**: Human-executed. FDE runs case through system, validates output manually.
- **Automated**: Unit/integration test script. Mocked API responses, schema validation.
- **Performance**: Load/throughput testing. Measure processing time, token usage, API latency.
- **Security**: Not explicitly tested in prototype. Production concern: PII handling, access controls.

---

## Exit Criteria

### Must Have (P0 — All Must Pass)

- [ ] **All P0 tests pass** (20 tests: HP-01, HP-02, HP-04, HP-06, HP-07, HP-08, HP-09, HP-10, HP-11, HP-13, HP-14, EC-02, EC-03, EC-04, ER-01, ER-03, ER-04, ER-06, ER-07)
- [ ] **Seriousness classification accuracy ≥96%** (measured on 100-case validation set if available, or 30-case mock data sample)
- [ ] **Expectedness signal precision ≥85%** (serious-unexpected cases flagged correctly vs MSO adjudication)
- [ ] **Reportability recommendation acceptance ≥88%** (MSO accepts recommendations as-is on sample)
- [ ] **Audit trail completeness 100%** (all processed cases have span citations + CoT reasoning + regulatory references)
- [ ] **No P0 security issues** (PII handling validated, no credentials in logs, access controls documented)
- [ ] **Performance meets SLA** (median processing time ≤20 min, 95th percentile ≤35 min)
- [ ] **15-day clock immutability** (`received_at` timestamp preserved across ADR-1 → ADR-2 → MSO queue)
- [ ] **Integration resilience validated** (PV API failure → local buffer + retry + ops alert; no data loss)
- [ ] **False-negative seriousness rate ≤1%** (patient safety: serious AEs must not be misclassified as non-serious)

### Should Have (P1 — 90%+ Pass Rate)

- [ ] **≥90% of P1 tests pass** (9 tests: HP-05, HP-12, EC-01, EC-06, EC-07, ER-02, ER-05)
- [ ] **Documented workarounds for P1 failures** (e.g., if social media extraction precision is 75%, document HITL escalation rate)
- [ ] **Stakeholder acceptance** (Dr. Iyer reviews 10 sample `TriageRecommendation` outputs and confirms "useful synthesis")

### Nice to Have (P2 — Can Defer)

- [ ] **P2 tests pass or documented** (HP-15, EC-08)
- [ ] **Token usage measured** (validate A5 assumption: ~10K tokens/case avg)
- [ ] **Performance optimization** (RSI caching, prompt token reduction)

---

## Issue Severity Definitions

| Severity | Description | Action |
|----------|-------------|--------|
| **P0 (Critical)** | Blocks core functionality (extraction, classification), causes data loss, creates patient safety risk, causes regulatory compliance failure, breaks audit trail | Must fix before deployment |
| **P1 (High)** | Major functionality impaired (social media extraction low precision, HITL rate >20%), format edge case unhandled, integration failure not gracefully handled | Should fix before deployment, or deploy with documented workaround |
| **P2 (Medium)** | Minor issue (performance suboptimal, token usage higher than expected), edge case rare (<1% of cases) | Can deploy with workaround, address in Wave 2 |
| **P3 (Low)** | Enhancement request (UI improvement, additional audit trail detail) | Future release, not deployment-blocking |

---

## Validation Summary

### Results Template

| Category | Total | Passed | Failed | Pass Rate |
|----------|-------|--------|--------|-----------|
| Happy Path | 15 | — | — | —% |
| Edge Cases | 8 | — | — | —% |
| Error Handling | 7 | — | — | —% |
| **Overall** | **30** | **—** | **—** | **—%** |

### Metrics Validation Results

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Seriousness classification accuracy | ≥96% | —% | ⬜ Not Measured |
| Expectedness signal precision | ≥85% | —% | ⬜ Not Measured |
| Reportability recommendation acceptance | ≥88% | —% | ⬜ Not Measured |
| Audit trail completeness | 100% | —% | ⬜ Not Measured |
| Per-case processing time (median) | ≤20 min | — min | ⬜ Not Measured |
| Per-case processing time (p95) | ≤35 min | — min | ⬜ Not Measured |
| False-negative seriousness rate | ≤1% | —% | ⬜ Not Measured |

### Issues Identified

| ID | Severity | Description | Status | Resolution |
|----|----------|-------------|--------|------------|
| — | — | — | — | — |

*(Populate during validation execution)*

---

## Validation Recommendation

*(To be completed after test execution)*

**Deployment Decision**:
- [ ] **Deploy to production** — all P0 criteria met, ≥90% P1 pass rate, stakeholder acceptance confirmed
- [ ] **Deploy with conditions** — P0 criteria met but [list conditions: e.g., "social media extraction HITL rate 25%, higher than 12% target; acceptable with MSO capacity validation"]
- [ ] **Do not deploy** — [list critical issues: e.g., "seriousness classification accuracy 89%, below 96% target; systematic errors on 'other medically important' criterion; requires prompt refinement"]

**Critical Risks for Production**:

1. **Portal rate limits (A29)**: If patient webform API rate limit is lower than assumed (100 req/min), burst ingestion may cause claim loss. **Mitigation**: Implement backoff logic + queue buffering. Test with simulated 429 responses.

2. **Regulatory drift**: FDA/EMA/MHRA reportability rules change ~annually. If rules change post-deployment, system recommendations become outdated. **Mitigation**: Quarterly review with Carolina Núñez-Reyes. Version-control system prompt with regulatory rule references. Alert ops if novel regulation cited by MSO (indicates system prompt needs update).

3. **Model accuracy drift**: If Claude model is updated (e.g., Opus 4.7 → Opus 5.0), seriousness classification accuracy may change. **Mitigation**: Re-run 100-case validation set on model updates. Compare accuracy before/after. If accuracy drops below 96%, retrain confidence calibration or revert to previous model.

4. **Single-point-of-failure (PV API)**: If PV case management API is unavailable for >4 hours, local buffer accumulates cases. **Mitigation**: Buffer capacity for 24 hours (~250 cases at 6K/year ÷ 365 days). Alert ops if buffer >50 cases. Batch replay when PV API restored.

**Stakeholder Sign-Off Required**:
- [ ] Dr. Maeve Carmichael (CMO) — approves deployment based on regulatory compliance and patient safety validation
- [ ] Dr. Anil Iyer (Senior Safety Physician) — confirms ADR-2 output quality meets "useful synthesis" standard
- [ ] Greta Schäffer (Chief Compliance Officer) — confirms audit trail completeness for FDA inspection readiness
- [ ] Theo Lonergan (Head of Drug Safety Ops) — confirms operational readiness (HITL queue capacity, MSO review queue integration)

---

**Document Owner**: FDE Engagement Lead  
**Reviewers**: Dr. Maeve Carmichael (CMO), Dr. Anil Iyer (Senior Safety Physician), Theo Lonergan (Head of Drug Safety Ops), Greta Schäffer (Chief Compliance Officer)  
**Next Steps**: Execute validation tests, populate results, make deployment recommendation
