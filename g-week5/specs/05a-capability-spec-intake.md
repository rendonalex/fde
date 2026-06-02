# Capability Specification: ADR-1 — AE Intake & Data Extraction Agent

**Document Version**: 1.0  
**Date**: 2026-06-01  
**Project**: Helix Therapeutics Agentic Adverse Event Triage System  
**ADR**: ADR-1 — AE Intake & Data Extraction Agent

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

**ADR-1** is a fully agentic intake and extraction agent that receives heterogeneous adverse event (AE) reports, classifies format, routes appropriately, extracts structured data per ICH E2D standards, normalizes terminology, and generates per-field confidence scores with span-level citations. The agent handles 88% of cases autonomously; 12% require human-in-the-loop (HITL) validation when extraction confidence < 0.85 on required fields [A15].

**Value Proposition**:
- Reduces per-case intake+extraction time from 40-45 min → 5-10 min (85-87% reduction)
- Eliminates queue delay component of 15-day compliance failures (50% of baseline failures per [A7])
- Processes 6,000 cases/year with consistent quality (standardized extraction logic across all formats)
- Generates span-level audit trail (compliance requirement per [A10])

**Delegation Archetype**: Fully Agentic with Confidence-Based HITL

**Expected Outcomes**:
- 88% cases processed end-to-end without human intervention
- 12% cases flagged for HITL validation (case processor re-keys low-confidence fields within 2 hours)
- Zero data loss (duplicate detection + exception queue routing)
- 100% audit trail completeness (span-level citations for every extracted field)

**Integration Dependencies**:
- PV case management system API (write `AECasePackage` record) [A16]
- RxNorm API (drug nomenclature normalization)
- MedDRA API (AE term coding)
- Web form API, email parser, VTT parser, JSON parser (intake channels)

---

## Agent Purpose

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

### Escalation Triggers

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

## Agent Activity Catalog

The table below enumerates every micro-task ADR-1 performs, with delegation level, data required, tool required, and risk level.

| # | Task | Type | Delegation Level | Data Required | Tool Required | Risk Level |
|---|------|------|-----------------|---------------|---------------|------------|
| 1.1 | Receive report from intake channel | Retrieval | Fully agentic | Email, webform API, phone transcript, social media API, literature feed | Channel-specific API/parser | Low |
| 1.2 | Classify report format (text/JSON/VTT) | Decision | Fully agentic | File extension, MIME type, content structure | File type detection | Low |
| 1.3 | Validate minimum required info (patient ID, drug, AE) | Decision | Fully agentic | Report content | None (LLM reasoning) | Medium |
| 1.4 | Detect duplicate case (hash + fuzzy match) | Decision | Agentic (high-confidence) + HITL (ambiguous) | Existing case records (patient, drug, AE, date) | PV case management API read | Medium |
| 1.5 | Route scope determination (in-scope marketed product vs. out-of-scope) | Decision | Fully agentic | Product list (Solivian, Tezarimab, Phaedora), suspect drug name | Product database | Low |
| 1.6 | Anchor 15-day clock timestamp (`received_at`) | Action | Fully agentic | Current timestamp, source channel receipt time | None (system timestamp) | High |
| 2.1 | Parse text from HCP report files | Retrieval | Fully agentic | HCP report text file content | Text parser | Low |
| 2.2 | Extract patient demographics (age, sex, weight, race) | Extraction | Agentic + HITL on confidence <0.85 | Report text | LLM extraction | Medium |
| 2.3 | Extract suspect drug name + dose + indication | Extraction | Agentic + HITL on confidence <0.85 | Report text | LLM extraction | High |
| 2.4 | Extract AE description narrative | Extraction | Agentic + HITL on confidence <0.85 | Report text | LLM extraction | High |
| 2.5 | Extract temporal relationships (drug start, AE onset, outcome dates) | Extraction | Agentic + HITL on confidence <0.85 | Report text, ambiguous date strings ("a few weeks ago") | LLM extraction + date parsing | High |
| 2.6 | Extract concomitant medications | Extraction | Agentic + HITL on confidence <0.80 | Report text, medication tables | LLM extraction | Medium |
| 2.7 | Extract medical history | Extraction | Agentic (optional field, no HITL block) | Report text | LLM extraction | Low |
| 2.8 | Normalize drug names to standard nomenclature (generic, brand → RxNorm) | Action | Fully agentic | Extracted drug names | RxNorm API | Medium |
| 2.9 | Code AE terms to MedDRA (preferred term) | Action | Fully agentic | Extracted AE description | MedDRA API | Medium |
| 2.10 | Generate per-field confidence scores (0.0-1.0) | Decision | Fully agentic | Extraction results, model logits | LLM confidence scoring | Low |
| 2.11 | Flag missing required fields for follow-up | Decision | Fully agentic | Extracted data, required fields list per ICH E2D | None (schema validation) | Low |
| 3.1 | Generate span-level citations (field → source text location) | Generation | Fully agentic | Extracted fields, source text | LLM span detection | Low |
| 3.2 | Assemble `AECasePackage` entity (structured JSON) | Generation | Fully agentic | All extracted data + confidence + citations | None (JSON serialization) | Low |
| 3.3 | Route to ADR-2 (if `extraction_status == AUTO_COMPLETE`) or HITL (if confidence <0.85) | Decision | Fully agentic | Confidence scores, extraction status | Queue routing logic | Medium |
| 3.4 | Write `AECasePackage` to PV case management system | Action | Agentic + retry on failure | `AECasePackage` JSON, idempotency key | PV case management API write | High |
| 3.5 | Buffer locally on PV API failure | Action | Fully agentic (failure handling) | `AECasePackage` JSON, idempotency key | Local file buffer | Medium |
| 3.6 | Emit audit event (intake complete, HITL flagged, exception routed) | Action | Fully agentic | Event type, case ID, timestamp | Audit trail store write | Low |

**Task Type Legend**:
- **Retrieval**: Fetch and return data from external source
- **Extraction**: Parse unstructured text to structured fields
- **Decision**: Choose between outcomes based on rules or reasoning
- **Action**: Write to system, trigger process, or route to queue
- **Generation**: Produce structured output (JSON, citations)

---

## Autonomy Matrix

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

## Entity Definitions

This section provides complete data models for all entities created or manipulated by ADR-1.

### AECasePackage

**Purpose**: Structured output from ADR-1 extraction, input to ADR-2 triage. System of record for extracted AE data.

**Attributes**:
- `case_id`: UUID, primary key, immutable, generated on creation (idempotency key for PV API writes)
- `received_at`: ISO 8601 timestamp with timezone (UTC), immutable, set at report ingestion (anchors 15-day clock)
- `format`: enum [`HCP_TEXT`, `PATIENT_WEBFORM`, `PHONE_VTT`, `SOCIAL_MEDIA`, `TRIAL_REPORT`, `LITERATURE`], required, immutable
- `extraction_status`: enum [`AUTO_COMPLETE`, `HUMAN_REQUIRED`, `PENDING_DUPLICATE`, `EXCEPTION_NOTE`, `REPORTER_FOLLOWUP`], required, mutable (transitions from HUMAN_REQUIRED → AUTO_COMPLETE after case processor re-key)
- `patient`: nested object (Patient entity, see below), required
- `suspect_drug`: nested object (SuspectDrug entity, see below), required
- `ae_description`: nested object (AEDescription entity, see below), required
- `temporal`: nested object (Temporal entity, see below), required
- `concomitant_meds`: array of nested objects (ConcomitantMed entity, see below), optional (empty array if none)
- `medical_history`: nested object (MedicalHistory entity, see below), optional (null if not provided)
- `span_citations`: nested object (SpanCitations entity, see below), required (100% audit trail completeness)
- `created_at`: ISO 8601 timestamp, set on creation, immutable
- `updated_at`: ISO 8601 timestamp, updated on any modification (e.g., case processor re-key)
- `created_by`: string enum [`ADR-1`, `CASE_PROCESSOR`], immutable
- `updated_by`: string enum [`ADR-1`, `CASE_PROCESSOR`], updated on modification

**State Machine** (extraction_status):
- Initial state: Determined during extraction
  - High-confidence extraction (all required fields ≥0.85) → `AUTO_COMPLETE`
  - Low-confidence extraction (any required field <0.85) → `HUMAN_REQUIRED`
  - Duplicate detected (fuzzy match ≥0.8) → `PENDING_DUPLICATE`
  - Mis-routed complaint → `EXCEPTION_NOTE`
  - Insufficient minimum information → `REPORTER_FOLLOWUP`
- `HUMAN_REQUIRED` → `AUTO_COMPLETE` (case processor re-keys low-confidence fields, releases to ADR-2)
- `PENDING_DUPLICATE` → `AUTO_COMPLETE` (case processor confirms unique, releases to ADR-2)
- `PENDING_DUPLICATE` → terminal (case processor links to existing case, no new record)
- `EXCEPTION_NOTE` → terminal (routed to exception queue, no further processing)
- `REPORTER_FOLLOWUP` → `AUTO_COMPLETE` (after reporter provides missing information)
- `AUTO_COMPLETE` is terminal (passed to ADR-2)

**Validation Rules**:
- `case_id` must be unique (idempotency: duplicate write with same case_id returns existing record, does not create duplicate)
- `received_at` must be <= current_timestamp (cannot anchor future date)
- `extraction_status == AUTO_COMPLETE` requires all required fields (patient, suspect_drug, ae_description, temporal) to have confidence ≥0.85
- `extraction_status == HUMAN_REQUIRED` requires at least one required field confidence <0.85
- ADR-2 precondition: only accepts `extraction_status == AUTO_COMPLETE`

**Foreign Key Constraints**:
- None (root entity, no foreign keys to other tables)

**Cascade Behavior**:
- Deletion: soft-delete only (set `deleted_at` timestamp), never hard-delete (FDA audit requirement: 7-year retention)

---

### Patient (nested in AECasePackage)

**Attributes**:
- `age`: integer, optional, range [0, 120], unit: years
- `sex`: enum [`M`, `F`, `Unknown`], required, default `Unknown`
- `weight`: float, optional, range [0.1, 500.0], unit: kg (kilograms)
- `race`: string, optional, max 50 characters (when reported; GDPR: collect only if voluntarily provided)
- `confidence`: float, required, range [0.0, 1.0] (per-field confidence score)

**Validation Rules**:
- If `age` provided, must be non-negative integer ≤120
- If `weight` provided, must be positive float ≤500.0 kg
- `confidence` ≥0.85 required for `extraction_status == AUTO_COMPLETE` (sex is always extractable from demographics, even if Unknown)
- `confidence` <0.85 triggers `extraction_status == HUMAN_REQUIRED`

---

### SuspectDrug (nested in AECasePackage)

**Attributes**:
- `name`: string, required, max 200 characters (generic name preferred, brand name acceptable)
- `dose`: string, required, max 100 characters (dose + unit, e.g., "150 mg", "2 tablets")
- `route`: string, optional, max 50 characters (e.g., "oral", "subcutaneous", "intravenous")
- `indication`: string, optional, max 200 characters (why patient was taking the drug)
- `rxnorm_code`: string, optional, RxNorm RxCUI (normalized drug code from RxNorm API)
- `confidence`: float, required, range [0.0, 1.0]

**Validation Rules**:
- `name` must be non-empty (required for all AE reports per ICH E2A minimum information)
- `dose` must be non-empty (required for causality assessment)
- `rxnorm_code` is optional (if RxNorm API lookup fails, agent uses extracted name as-is)
- `confidence` ≥0.85 required for `extraction_status == AUTO_COMPLETE`
- `confidence` <0.85 triggers `extraction_status == HUMAN_REQUIRED`

---

### AEDescription (nested in AECasePackage)

**Attributes**:
- `narrative`: string, required, max 5000 characters (free-text AE description from reporter)
- `meddra_pt`: string, optional, max 200 characters (MedDRA Preferred Term)
- `meddra_code`: string, optional, MedDRA PT code (8-digit code)
- `onset_date`: ISO 8601 date (not timestamp), optional (date AE started)
- `outcome`: enum [`recovered`, `recovering`, `not_recovered`, `fatal`, `unknown`], optional
- `confidence`: float, required, range [0.0, 1.0]

**Validation Rules**:
- `narrative` must be non-empty (required for seriousness classification in ADR-2)
- `meddra_pt` and `meddra_code` are optional (if MedDRA API lookup fails, ADR-2 uses narrative for classification)
- `onset_date` must be ≤ current_date (cannot be future date), ≥ (received_at - 10 years) (sanity check: AE within past 10 years)
- `outcome == fatal` triggers high-priority serious classification in ADR-2
- `confidence` ≥0.85 required for `extraction_status == AUTO_COMPLETE`
- `confidence` <0.85 triggers `extraction_status == HUMAN_REQUIRED`

---

### Temporal (nested in AECasePackage)

**Attributes**:
- `drug_start_date`: ISO 8601 date, optional (date suspect drug was first administered)
- `ae_onset_date`: ISO 8601 date, optional (date AE first occurred, may duplicate ae_description.onset_date if provided)
- `outcome_date`: ISO 8601 date, optional (date AE outcome determined, e.g., recovery date, death date)
- `date_estimated`: boolean, required, default false (true if any date was estimated from ambiguous text like "a few weeks ago")
- `confidence`: float, required, range [0.0, 1.0]

**Validation Rules**:
- If `drug_start_date` and `ae_onset_date` both provided: `ae_onset_date` must be ≥ `drug_start_date` (AE cannot precede drug exposure)
- If `outcome_date` and `ae_onset_date` both provided: `outcome_date` must be ≥ `ae_onset_date` (outcome cannot precede AE onset)
- All dates must be ≤ current_date (cannot be future dates)
- All dates must be ≥ (received_at - 10 years) (sanity check)
- If `date_estimated == true`, ADR-2 factors uncertainty into causality assessment
- `confidence` ≥0.85 required for `extraction_status == AUTO_COMPLETE`
- `confidence` <0.85 triggers `extraction_status == HUMAN_REQUIRED`

---

### ConcomitantMed (nested in AECasePackage, array)

**Attributes**:
- `name`: string, required, max 200 characters (concomitant medication name)
- `dose`: string, optional, max 100 characters (dose + unit)
- `route`: string, optional, max 50 characters
- `confidence`: float, required, range [0.0, 1.0]

**Validation Rules**:
- `name` must be non-empty
- `confidence` threshold: 0.80 (lower than suspect drug due to under-reporting in source reports per [A14])
- `confidence` <0.80 triggers `extraction_status == HUMAN_REQUIRED`
- Empty array is valid (no concomitant medications reported)

---

### MedicalHistory (nested in AECasePackage)

**Attributes**:
- `narrative`: string, optional, max 2000 characters (free-text medical history)
- `confidence`: float, required, range [0.0, 1.0]

**Validation Rules**:
- Optional field (does not block `extraction_status == AUTO_COMPLETE` if confidence <0.85)
- `confidence` <0.70 triggers flag for follow-up (logged but does not block processing)
- Null is valid (no medical history provided)

---

### SpanCitations (nested in AECasePackage)

**Purpose**: Links each extracted field to source text location for FDA audit trail (100% completeness requirement).

**Structure**: Object with keys = field names, values = citation objects

**Attributes** (per field):
- `value`: string, required (extracted value)
- `source_span`: string, required, format "start_char-end_char" (character indices in source text, 0-indexed)

**Example**:
```json
{
  "patient.age": { "value": "45", "source_span": "23-25" },
  "suspect_drug.name": { "value": "tezarimab", "source_span": "67-76" },
  "ae_description.narrative": { "value": "severe headache", "source_span": "120-135" }
}
```

**Validation Rules**:
- All required fields (patient, suspect_drug, ae_description, temporal) must have corresponding span citations
- `source_span` must be valid (start_char < end_char, both non-negative integers)
- 100% completeness required for `extraction_status == AUTO_COMPLETE` (FDA inspection readiness)

---

## System and Data Inventory

This section maps all data sources and systems ADR-1 requires, with access type, availability, gaps, and shared status (for compounding reuse).

| System / Data Source | Data Needed | Access Type | Availability | Auth Method | Gap / Risk | Shared |
|---------------------|-------------|-------------|--------------|-------------|------------|--------|
| **PV Case Management System** | Case records (read for duplicate detection), write `AECasePackage` | Read/Write | Assumed available [A16] (Week 1 validation required) | OAuth 2.0 (assumed) | Week 1 Go/No-Go: confirm API endpoints, SLA, auth. Fallback: batch file integration (XML) if API unavailable. | ✅ Shared with ADR-2 |
| **RxNorm API** (National Library of Medicine) | Drug nomenclature lookup (brand name → generic, RxNorm RxCUI) | Read | Publicly available (REST API) | None (public) | Rate limits: 20 req/sec. Handle 429 with exponential backoff. | ✅ Shared with ADR-2 |
| **MedDRA API** (Medical Dictionary for Regulatory Activities) | AE term coding (lay term → preferred term, MedDRA LLT → PT) | Read | Licensed (subscription required, assumed available) | API key (assumed) | Week 1 validation: confirm license, API access. Fallback: local MedDRA database export (MSSQL). | ✅ Shared with ADR-2 |
| **Product Information Database** | Marketed product list (Solivian, Tezarimab, Phaedora) for scope routing | Read | Structured list (3 products) | Internal (file read or DB query) | No gap. Static data (product list rarely changes). | ✅ Shared with ADR-2 |
| **Intake Channels** | |  |  |  |  |  |
| — Email parser | HCP report text from email body/attachment | Read | Buildable (IMAP client + text extraction) | Email credentials | Build: 2 days. Handle attachments (.txt, .docx). | ⬜ ADR-1 only |
| — Web form API | Patient direct report JSON (structured) | Read | API endpoint provided (assumed) | API key | Week 1 validation: confirm endpoint, rate limits. | ⬜ ADR-1 only |
| — Phone transcript parser | VTT (video text track) format transcripts | Read | Buildable (VTT parser + text extraction) | File system access | Build: 1 day. Standard VTT format. | ⬜ ADR-1 only |
| — Social media monitoring API | JSON extracts with conversation threads | Read | External vendor API (assumed available) | API key | Week 1 validation: confirm vendor, API SLA. Risk: PII extraction from public posts. | ⬜ ADR-1 only |
| — Literature alert feed | Published case reports (text or PDF) | Read | External vendor feed or manual upload | API key or file upload | Build: 3 days if PDF parsing required. Mock data has .txt format (no PDF). | ⬜ ADR-1 only |
| **Audit Trail Store** | Span-level citations, CoT reasoning, timestamps | Write | Buildable (database or JSON log store) | Internal | Build: 2 days. Schema: case_id, field_name, extracted_value, source_span, confidence, timestamp. | ✅ Shared with ADR-2 |
| **HITL Validation Queue** | Low-confidence `AECasePackage` for case processor review | Write | Buildable (queue system or PV case management workflow) | Internal | Build: 1 day. UI for case processor to review flagged fields, re-key corrections, release to ADR-2. | ⬜ ADR-1 only |
| **Exception Queue** | Mis-routed complaints, out-of-scope products | Write | Buildable (queue system or PV case management workflow) | Internal | Build: 1 day. Ops review UI. | ⬜ ADR-1 only |

**Shared Asset Summary**:
- **5 shared integrations** (reused by ADR-2): PV case management API, RxNorm API, MedDRA API, Product Information DB, Audit Trail Store
- **4 ADR-1-specific integrations**: Email parser, webform API, phone transcript parser, social media API, literature feed (intake channels)
- **1 ADR-1-specific asset**: HITL validation queue (case processor UI)

**Week 1 Go/No-Go Validations**:
- PV case management API availability, SLA, auth method [A16]
- MedDRA API license and access confirmation
- Webform API, social media API endpoints and rate limits
- Literature feed vendor confirmation (or fallback to manual upload for prototype)

---

## Context Engineering Design

### Memory Architecture

ADR-1 is stateless per case (no multi-turn conversation, no customer history). Context is single-invocation per report.

| Memory Type | Content | Storage | Lifecycle |
|-------------|---------|---------|-----------|
| **In-context** (per invocation) | Current AE report text, extracted fields in progress | Prompt window (input + output tokens) | Per case (single invocation) |
| **Semantic** (static reference) | ICH E2D required fields schema, product list (Solivian/Tezarimab/Phaedora), MedDRA coding guidelines, confidence threshold rules | System prompt (version-controlled) | Updated on schema change or product launch |
| **Procedural** (static instructions) | Extraction logic, confidence scoring formula, HITL routing rules, exception handling, audit trail generation | System prompt (version-controlled) | Updated on prompt refinement |
| **Episodic** (not used) | No customer history or prior case memory required | N/A | N/A |

### Retrieval Strategy

ADR-1 does **not use RAG** (no vector search, no knowledge base retrieval). All context is provided in the input (AE report text) or system prompt (ICH E2D schema, product list).

**Exception**: Duplicate detection requires read query to PV case management system:
- **Trigger**: After patient + drug + AE extraction complete
- **Query**: `GET /api/v1/cases?patient_id={}&drug_name={}&ae_term={}&date_range=30days`
- **Target**: Existing case records with fuzzy match on patient demographics, drug, AE description
- **Relevance scoring**: Fuzzy match confidence 0.0-1.0 (Levenshtein distance on patient name, exact match on drug + AE term)
- **Cost**: Single API call per case (negligible latency ~50ms)

### Prompt / Context Engineering Principles

**System Prompt Structure** (ADR-1):

```
1. ROLE AND PURPOSE
   "You are an adverse event intake and extraction agent for Helix Therapeutics pharmacovigilance system.
   Your job: extract structured data from heterogeneous AE reports per ICH E2D standards, generate per-field
   confidence scores, and route to medical triage or HITL validation based on extraction quality."

2. SCOPE (What you may and may not do)
   - MAY: Extract patient demographics, suspect drug + dose, AE description, temporal relationships,
     concomitant meds, medical history from text/JSON/VTT formats. Normalize drug names via RxNorm.
     Code AE terms via MedDRA. Generate span-level citations. Route to HITL when confidence <0.85.
   - MAY NOT: Make medical judgments (seriousness, expectedness, reportability). Contact reporters.
     Modify source reports. Write to PV system if extraction incomplete.

3. INPUT FORMATS (Explicit list with examples)
   - HCP report text: semi-structured with field labels ("Patient:", "Suspect Drug:", "Adverse Event:")
   - Patient webform JSON: structured with key-value pairs
   - Phone transcript VTT: unstructured conversational text
   - Social media JSON: conversational threads with patient identifiers in narrative
   - Clinical trial report text: structured with MedDRA codes

4. EXTRACTION SCHEMA (ICH E2D Required Fields)
   - Patient: age (years), sex (M/F/Unknown), weight (kg), race (when reported)
   - Suspect drug: name (generic preferred), dose + unit, route, indication
   - AE: description (narrative), MedDRA PT code, onset date, outcome (recovered/fatal/ongoing)
   - Temporal: drug start date, AE onset date, outcome date (estimate if ambiguous with flag)
   - Concomitant meds: list (name + dose + route)
   - Medical history: narrative (optional)

5. CONFIDENCE SCORING LOGIC
   - Score 0.0-1.0 per field based on: explicit field labels (high), unambiguous extraction (high),
     ambiguous dates or lay terminology (medium), missing data or conflicting information (low).
   - Required field confidence <0.85 → HITL flag
   - Optional field confidence <0.70 → flag for follow-up (do not block)

6. FEW-SHOT EXAMPLES
   [3 examples: HCP text → structured JSON, patient webform → extraction, social media → patient ID extraction]

7. GUARDRAILS
   - If no patient identifier and no suspect drug → route to REPORTER_FOLLOWUP (insufficient minimum info)
   - If medical device complaint detected (no drug, device mentioned) → route to EXCEPTION_NOTE
   - If out-of-scope product (not Solivian/Tezarimab/Phaedora) → route to EXCEPTION_NOTE
   - If duplicate detected (fuzzy match confidence ≥0.8) → route to PENDING_DUPLICATE
   - If ambiguous date ("a few weeks ago") → estimate date + flag `date_estimated: true`

8. OUTPUT SCHEMA (Structured JSON)
   {
     "case_id": "generated UUID",
     "received_at": "ISO 8601 timestamp",
     "format": "HCP_TEXT | PATIENT_WEBFORM | PHONE_VTT | SOCIAL_MEDIA | TRIAL_REPORT | LITERATURE",
     "extraction_status": "AUTO_COMPLETE | HUMAN_REQUIRED | PENDING_DUPLICATE | EXCEPTION_NOTE | REPORTER_FOLLOWUP",
     "patient": { "age": int, "sex": "M|F|Unknown", "weight": float, "race": string, "confidence": float },
     "suspect_drug": { "name": string, "dose": string, "route": string, "indication": string, "rxnorm_code": string, "confidence": float },
     "ae_description": { "narrative": string, "meddra_pt": string, "meddra_code": string, "onset_date": "ISO date", "outcome": string, "confidence": float },
     "temporal": { "drug_start_date": "ISO date", "ae_onset_date": "ISO date", "outcome_date": "ISO date", "date_estimated": boolean, "confidence": float },
     "concomitant_meds": [ { "name": string, "dose": string, "route": string, "confidence": float } ],
     "medical_history": { "narrative": string, "confidence": float },
     "span_citations": { "field_name": { "value": string, "source_span": "start_char-end_char" } }
   }

9. CHAIN OF THOUGHT (for complex extractions)
   "First, classify report format. Then, extract patient demographics with span citations. Then, extract
   suspect drug and normalize via RxNorm. Then, extract AE description and code via MedDRA. Then, parse
   temporal relationships and flag if date estimated. Then, generate per-field confidence scores. Then,
   check confidence thresholds and route accordingly."

10. TOKEN DISCIPLINE
    - Concise system prompt (<2,000 tokens)
    - No verbose instructions or repetition
    - Few-shot examples: 3 max (cover edge cases: ambiguous dates, social media PII, concomitant med tables)
```

**Token Budget per Case**:
- System prompt: 2,000 tokens (static, reused across all cases)
- Input (AE report): 3,000-15,000 tokens (avg 8,000 per [A5])
- Output (`AECasePackage` JSON): 1,500 tokens
- Total: ~11,500 tokens/case avg → $0.23/case at Claude Opus 4.7 pricing

---

## Compounding Roadmap

ADR-1 builds foundational integrations and platform assets that amplify future agents (Wave 2+).

### Wave 1 — Foundation Agent (ADR-1)

**Agent**: AE Intake & Data Extraction Agent  
**Wave Rationale**: Self-financing (payback 1.8 months, ROI 574% Year 1), eliminates queue delay (50% of 15-day compliance failures), builds 5 shared integrations for ADR-2.

**Key Integrations Built** (reusable):
1. **PV case management API** (read for duplicate detection, write `AECasePackage`)
2. **RxNorm API** (drug nomenclature normalization)
3. **MedDRA API** (AE term coding)
4. **Product Information Database** (marketed product list)
5. **Audit Trail Store** (span-level citations, CoT reasoning, timestamps)

**Shared Assets Created** (reusable):
- Text parsing pipeline (handles text/JSON/VTT heterogeneity) — reusable for any unstructured PV document
- Per-field confidence scoring logic — reusable for any extraction task
- HITL validation workflow (UI, queue routing, case processor re-key) — reusable for any confidence-gated agent
- Duplicate detection logic (fuzzy match + hash comparison) — reusable for any case deduplication
- Exception queue routing (mis-routed complaints, out-of-scope products) — reusable for any intake triage

**Build Cost**: $50K (2 weeks FDE, text parsing $15K, integration $10K, testing $5K per [A18])

**Annual Savings**: $337K (eliminates 35 min per case × 6,000 cases, minus token + HITL costs)

---

### Wave 1 Continued — Compounding Agent (ADR-2)

**Agent**: Medical Triage Agent  
**Wave Rationale**: Pipeline dependency (requires ADR-1 output), integrated value proposition (75→20 min requires both agents), self-financing (payback 3.1 months).

**Reuses from ADR-1**:
1. ✅ PV case management API (read `AECasePackage`, write `TriageRecommendation`)
2. ✅ RxNorm API (for causality assessment with concomitant meds)
3. ✅ MedDRA API (for expectedness hierarchy matching)
4. ✅ Product Information Database (retrieve product RSI)
5. ✅ Audit Trail Store (append classification reasoning, span citations)

**New Integrations (ADR-2 specific)**:
6. **Product RSI/CCSI Database** (retrieve safety profile for expectedness assessment)
7. **ICH E2A Criteria** (codified in system prompt, no external API)
8. **Reportability Rules Engine** (FDA 21 CFR 314.80, EMA, MHRA, PMDA regulations codified in system prompt)

**Build Cost**: $30K (1.5 weeks FDE, system prompt $8K, RSI integration $3K, testing $4K per [A18])

**Annual Savings**: $116K (eliminates 30 min per case × 6,000 cases, minus token + MSO review costs)

**Combined Wave 1 Savings**: $453K (payback 2.1 months on $80K build cost, ROI 466% Year 1)

---

### Integration Reuse Matrix

| Integration / Asset | ADR-1 (Wave 1) | ADR-2 (Wave 1) | Future ADR-3 (Wave 2) | Notes |
|---------------------|----------------|----------------|----------------------|-------|
| **PV case management API** | ✓ Build (read + write) | ✓ Reuse (read + write) | ✓ Reuse | Shared across all PV agents |
| **RxNorm API** | ✓ Build | ✓ Reuse | ✓ Reuse | Drug nomenclature standard |
| **MedDRA API** | ✓ Build | ✓ Reuse | ✓ Reuse | AE term coding standard |
| **Product Information DB** | ✓ Build | ✓ Reuse | ✓ Reuse | Static product list |
| **Audit Trail Store** | ✓ Build | ✓ Reuse | ✓ Reuse | FDA inspection requirement |
| **Text parsing pipeline** | ✓ Build | | ✓ Reuse (literature surveillance) | Handles text/JSON/VTT |
| **HITL validation workflow** | ✓ Build | | ✓ Reuse (any confidence-gated agent) | Queue + UI + case processor |
| **Duplicate detection logic** | ✓ Build | | ✓ Reuse (any deduplication task) | Fuzzy match + hash |
| **Product RSI Database** | | ✓ Build | ✓ Reuse | Safety profile for expectedness |
| **Reportability Rules Engine** | | ✓ Build (system prompt) | ✓ Reuse | FDA/EMA/MHRA/PMDA regulations |

**Compounding Effect**: 5 integrations built in ADR-1 are reused by ADR-2, reducing ADR-2 marginal build cost by ~40%. Future Wave 2 agents (reporter follow-up, causality assessment, literature surveillance) will reuse 6-8 integrations → marginal cost per new agent drops from $50K (ADR-1) to $20-30K (Wave 2 agents).

---

### Potential Wave 2 Agents (Enabled by Wave 1 Assets)

**Out of current exam scope**, but planning for compounding:

1. **Reporter Follow-up Automation Agent**
   - Reuses: PV API, RxNorm, MedDRA, Audit Trail Store, Text parsing pipeline
   - New: Email generation, reporter contact database
   - Value: Addresses 20% of 15-day compliance failures (missing information follow-up) per [A7]

2. **Literature Surveillance Agent**
   - Reuses: PV API, MedDRA, Text parsing pipeline (add PDF parsing), Product RSI
   - New: PubMed API, PDF extraction
   - Value: Automates 10% of intake volume (literature alerts) per [A2]

3. **Social Media Monitoring Enhancement**
   - Reuses: PV API, Text parsing pipeline, Duplicate detection, HITL workflow
   - New: PII masking layer (GDPR/HIPAA), sentiment analysis for AE severity signals
   - Value: Improves 20% of intake volume (social media extracts) with better PII handling

4. **Multi-Product Expansion**
   - Reuses: All ADR-1 + ADR-2 integrations (no new build)
   - New: Product list expansion (add 7 pipeline assets)
   - Value: Expands capacity to 13,000+ cases/year (6K marketed + 7K pipeline) with zero marginal integration cost

---

## Validation Design

This section specifies testable scenarios for happy path, edge cases, and failure modes.

### Happy Path Scenarios

#### HP-1: Structured HCP Report Extraction
**Input**: HCP report text with explicit field labels ("Patient:", "Suspect Drug:", "Adverse Event:")  
**Expected Output**:
- All required fields extracted with confidence ≥0.85
- `extraction_status == AUTO_COMPLETE`
- RxNorm normalization: "Tezarimab" → RxCUI "123456"
- MedDRA coding: "severe headache" → PT "Headache" (10019211)
- Span citations: 100% complete (all required fields linked to source text)
- Processing time: ≤10 min
- Routed to ADR-2 automatically

**Pass Criteria**: Agent processes end-to-end without HITL, all fields match case processor validation (96% accuracy target)

---

#### HP-2: Patient Webform JSON Extraction
**Input**: Structured JSON from patient webform with key-value pairs  
**Expected Output**:
- All required fields extracted with confidence ≥0.90 (structured input → higher confidence)
- `extraction_status == AUTO_COMPLETE`
- Duplicate detection query returns no matches
- Processing time: ≤5 min (structured parsing faster than text extraction)
- Routed to ADR-2 automatically

**Pass Criteria**: Zero extraction errors, 100% span citation completeness

---

#### HP-3: Duplicate Detection (High Confidence)
**Input**: AE report matching existing case (same patient name, drug, AE term, date within 30 days)  
**Expected Output**:
- Fuzzy match confidence ≥0.8 (high-confidence duplicate)
- `extraction_status == PENDING_DUPLICATE`
- No PV API write (does not create duplicate case record)
- Routed to case processor for manual review
- Case processor links to existing case or releases as unique

**Pass Criteria**: Duplicate detection precision ≥95% (true duplicates flagged, false positives ≤5%)

---

### Edge Cases

#### EC-1: Missing Optional Fields (Medical History Null)
**Input**: HCP report with all required fields but no medical history section  
**Expected Output**:
- `medical_history.narrative == null`
- `medical_history.confidence == 0.0` (no extraction attempted)
- Does NOT trigger `extraction_status == HUMAN_REQUIRED` (optional field)
- Routed to ADR-2 with `medical_history == null`

**Pass Criteria**: Processing continues without blocking, null is valid for optional fields

---

#### EC-2: Ambiguous Date Estimation ("a few weeks ago")
**Input**: AE onset date described as "a few weeks ago" in narrative text  
**Expected Output**:
- `temporal.ae_onset_date` estimated as `received_at - 21 days` (3 weeks = 21 days)
- `temporal.date_estimated == true`
- Flag in audit trail: "Date estimated from ambiguous text"
- Confidence ≥0.70 (estimated date acceptable for processing)
- Does NOT trigger `extraction_status == HUMAN_REQUIRED`

**Pass Criteria**: Date estimation is consistent (same phrase → same calculation), flag is set for ADR-2 awareness

---

#### EC-3: Brand vs. Generic Drug Name Variation
**Input**: Report uses brand name "Solivian" instead of generic "solivimab"  
**Expected Output**:
- `suspect_drug.name == "Solivian"` (extracted as-is)
- RxNorm API normalizes to RxCUI "789012"
- `suspect_drug.rxnorm_code == "789012"`
- ADR-2 uses RxCUI for product RSI matching (handles brand/generic variance)

**Pass Criteria**: Brand and generic names normalize to same RxCUI, product routing is consistent

---

#### EC-4: Concomitant Medication Extraction from Table Format
**Input**: HCP report with concomitant meds in table (| Med Name | Dose | Route |)  
**Expected Output**:
- `concomitant_meds` array extracted with all table rows
- Each med has `name`, `dose`, `route` with confidence ≥0.80
- Span citations link to table cell locations
- If any med confidence <0.80 → `extraction_status == HUMAN_REQUIRED`

**Pass Criteria**: Table parsing extracts all rows, confidence threshold enforced per-field

---

#### EC-5: Ambiguous Duplicate (Fuzzy Match 0.5-0.8)
**Input**: Report similar to existing case but with differences (e.g., same patient, different drug dose)  
**Expected Output**:
- Fuzzy match confidence 0.65 (ambiguous duplicate)
- `extraction_status == PENDING_DUPLICATE`
- Routed to case processor for manual review
- Case processor decides: unique (release to ADR-2) or link to existing

**Pass Criteria**: Ambiguous cases are not auto-rejected, manual review decision is logged

---

### Failure Modes and Recovery

#### FM-1: PV API Write Failure (503 Service Unavailable)
**Input**: Agent completes extraction, attempts PV API write, receives HTTP 503  
**Expected Behavior**:
- Retry 3 times with exponential backoff (1s, 2s, 4s)
- After 3 failures: buffer `AECasePackage` JSON locally with idempotency key
- Emit ops alert: "PV_API_WRITE_FAILED, case_id={}, retry_count=3"
- Do NOT drop case (zero data loss requirement)

**Recovery**:
- Ops investigates PV API (network, auth, SLA breach)
- Once PV API restored, re-submit buffered cases with idempotency keys (no duplicate creation)
- Validate all buffered cases processed within 24 hours

**Pass Criteria**: No case loss, idempotency prevents duplicate records, ops alerted within 2 minutes

---

#### FM-2: RxNorm API Failure (Drug Not Found)
**Input**: Extracted drug name "investigational_drug_XYZ" not in RxNorm database (returns HTTP 404)  
**Expected Behavior**:
- Log warning: "RxNorm lookup failed for drug: investigational_drug_XYZ"
- `suspect_drug.name == "investigational_drug_XYZ"` (use extracted name as-is)
- `suspect_drug.rxnorm_code == null`
- Flag for manual review: "RxNorm_code_missing"
- Do NOT block processing (continue to ADR-2 with null rxnorm_code)

**Recovery**:
- Case processor manually maps drug name to product (Solivian/Tezarimab/Phaedora) during HITL review
- ADR-2 handles null rxnorm_code (uses extracted name for product RSI matching)

**Pass Criteria**: Processing continues, missing RxNorm code flagged but does not block workflow

---

#### FM-3: MedDRA API Failure (401 Unauthorized)
**Input**: MedDRA API returns HTTP 401 (license expired or API key invalid)  
**Expected Behavior**:
- Immediate ops alert: "MEDDRA_API_AUTH_FAILED"
- Do NOT continue processing (cannot code AE terms without MedDRA)
- Route all cases to exception queue until MedDRA API restored
- Block new case processing (alert displayed to intake team)

**Recovery**:
- Ops renews MedDRA license or rotates API key
- Validate MedDRA API access restored
- Re-process all exception queue cases

**Pass Criteria**: Auth failure detected immediately, no cases processed with missing MedDRA codes, ops alerted within 1 minute

---

#### FM-4: Missing Minimum Required Information
**Input**: Report has patient name but no suspect drug name and no AE description (insufficient minimum info per ICH E2A)  
**Expected Behavior**:
- `extraction_status == REPORTER_FOLLOWUP`
- Routed to reporter follow-up queue (not ADR-2, not HITL validation)
- Flag: "missing_suspect_drug, missing_ae_description"
- Case processor contacts reporter for additional information

**Recovery**:
- Reporter provides missing information (email, phone)
- Case processor re-keys report with complete data
- Re-submit to ADR-1 for extraction (or manually complete extraction)
- Transition to `extraction_status == AUTO_COMPLETE` after reporter follow-up

**Pass Criteria**: Incomplete cases routed correctly, do not block ADR-2 queue, reporter follow-up SLA tracked

---

#### FM-5: Exception Queue Overflow (>15% Exception Rate)
**Input**: 50 cases processed, 10 routed to exception queue (20% exception rate over 24 hours, exceeds 15% threshold)  
**Expected Behavior**:
- Ops alert: "EXCEPTION_RATE_EXCEEDED, rate=20%, threshold=15%"
- Investigate root cause: new report format? New intake channel? Mis-routing from device complaint team?
- Adjust format classification logic or intake routing as needed

**Recovery**:
- Ops identifies root cause (e.g., new webform format not recognized)
- Update format classification rules or parser
- Re-process exception queue cases with updated logic

**Pass Criteria**: Exception rate monitored continuously, alert triggers investigation, root cause identified within 4 hours

---

### Concurrency and Idempotency

#### Concurrency Test: Simultaneous Duplicate Detection
**Scenario**: Two agents process similar reports simultaneously (same patient, drug, AE, within 1 second)  
**Expected Behavior**:
- First agent completes extraction, queries PV API for duplicates (returns none), writes `AECasePackage`
- Second agent completes extraction, queries PV API for duplicates (returns first agent's case), flags `PENDING_DUPLICATE`
- No duplicate case record created (only first agent writes)

**Pass Criteria**: Race condition handled by PV API uniqueness constraint on patient+drug+AE+date (within same day), duplicate detection query is eventually consistent

---

#### Idempotency Test: Duplicate PV API Write with Same case_id
**Scenario**: Agent writes `AECasePackage` with case_id="abc-123", network timeout, agent retries with same case_id  
**Expected Behavior**:
- First write succeeds (case created)
- Second write with same case_id returns existing record (HTTP 200, no duplicate creation)
- `case_id` is idempotency key (guaranteed unique in PV database)

**Pass Criteria**: No duplicate case records, retry is safe, idempotency enforced by PV API

---

## Integration Contracts

### ADR-1 → PV Case Management System (Write)

**Endpoint**: `POST /api/v1/cases`

**Request Schema**:
```json
{
  "case_id": "UUID (idempotency key)",
  "received_at": "ISO 8601 timestamp",
  "format": "HCP_TEXT | PATIENT_WEBFORM | PHONE_VTT | SOCIAL_MEDIA | TRIAL_REPORT | LITERATURE",
  "extraction_status": "AUTO_COMPLETE | HUMAN_REQUIRED | PENDING_DUPLICATE | EXCEPTION_NOTE | REPORTER_FOLLOWUP",
  "patient": {
    "age": 45,
    "sex": "F",
    "weight": 68.5,
    "race": "Caucasian",
    "confidence": 0.92
  },
  "suspect_drug": {
    "name": "tezarimab",
    "dose": "150 mg",
    "route": "subcutaneous",
    "indication": "multiple sclerosis",
    "rxnorm_code": "123456",
    "confidence": 0.95
  },
  "ae_description": {
    "narrative": "severe headache with photophobia",
    "meddra_pt": "Headache",
    "meddra_code": "10019211",
    "onset_date": "2026-05-28",
    "outcome": "recovered",
    "confidence": 0.89
  },
  "temporal": {
    "drug_start_date": "2026-04-15",
    "ae_onset_date": "2026-05-28",
    "outcome_date": "2026-05-30",
    "date_estimated": false,
    "confidence": 0.87
  },
  "concomitant_meds": [
    { "name": "ibuprofen", "dose": "400 mg", "route": "oral", "confidence": 0.88 }
  ],
  "medical_history": {
    "narrative": "no significant medical history",
    "confidence": 0.75
  },
  "span_citations": {
    "patient.age": { "value": "45", "source_span": "23-25" },
    "suspect_drug.name": { "value": "tezarimab", "source_span": "67-76" }
  }
}
```

**Response** (success):
```json
{
  "status": "created",
  "case_id": "UUID",
  "received_at": "ISO 8601 timestamp"
}
```

**Response** (failure):
```json
{
  "status": "error",
  "error_code": "503 | 400 | 401",
  "message": "Service unavailable | Invalid schema | Unauthorized"
}
```

**Error Handling** (complete status code mapping):
- **200 OK**: Case created successfully, proceed to next case
- **201 Created**: Case created successfully (alternative success code), proceed
- **400 Bad Request**: Schema validation failure (missing required field, invalid data type)
  - Action: Log error with validation details, route to exception queue with error message
  - Do NOT retry (client error, will fail again)
  - Alert: Email case ID + validation errors to ops team
- **401 Unauthorized**: Auth token expired or invalid
  - Action: Alert ops immediately (email + Slack: "PV_API_AUTH_FAILED")
  - Do NOT retry (auth must be fixed first)
  - Block all new case processing until auth restored (display alert to intake team)
- **409 Conflict**: case_id already exists (idempotency: duplicate write with same case_id)
  - Action: Treat as success (case already written), log "duplicate write prevented", proceed
  - This is expected behavior during retry after timeout
- **429 Too Many Requests**: Rate limit exceeded
  - Action: Exponential backoff, wait for Retry-After header value (default 30s if header missing)
  - Retry once after backoff
  - If rate limit persists, buffer locally + alert ops (rate limit may need adjustment)
- **503 Service Unavailable**: PV API temporarily down (maintenance, network issue, overload)
  - Action: Retry 3 times with exponential backoff (1s, 2s, 4s)
  - After 3 failures: buffer `AECasePackage` JSON locally with idempotency key
  - Alert ops: "PV_API_WRITE_FAILED, case_id={}, retry_count=3"
  - Buffer retention: 7 days (FDA audit requirement), re-submit when API restored
- **504 Gateway Timeout**: PV API processing timeout
  - Action: Same as 503 (retry 3 times, buffer locally, alert ops)
- **500 Internal Server Error**: PV API internal error
  - Action: Retry once after 2s delay (may be transient)
  - If fails again, buffer locally + alert ops
- **Network Timeout** (no response within 10 seconds): Connection timeout
  - Action: Retry once after 2s delay
  - If fails again, buffer locally + alert ops

**Fallback Behavior**:
- Local buffer location: `/var/data/adr1/buffer/`
- Buffer file format: JSON (one file per case, filename: `{case_id}.json`)
- Buffer monitoring: Ops dashboard shows buffered case count, alerts if >10 cases buffered
- Re-submission: Automated retry every 15 minutes for buffered cases (use idempotency key to prevent duplicates)
- Manual intervention: If PV API down >4 hours, ops evaluates batch file fallback (XML export to PV system file intake)

**Rate Limiting** (client-side):
- Max 100 concurrent case writes (throttle at application layer)
- If PV API rate limit unknown, start with 10 writes/second, increase gradually based on 429 responses

**Data Mapping** (internal entity → PV API schema):
- Internal `AECasePackage.case_id` → PV API `case.id` (UUID primary key)
- Internal `AECasePackage.received_at` → PV API `case.receipt_timestamp` (ISO 8601, immutable)
- Internal `AECasePackage.extraction_status` → PV API `case.workflow_status` (maps AUTO_COMPLETE → READY_FOR_TRIAGE)
- Internal nested entities (patient, suspect_drug, ae_description) → PV API flattened fields (case.patient_age, case.drug_name, etc.) OR nested JSON (depends on PV API schema, validate in Week 1)

**SLA**: <500ms response time (p95), 99.5% availability per [A16] (Week 1 validation required).

---

### ADR-1 → RxNorm API (Read)

**Endpoint**: `GET https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}`

**Request**: Drug name (brand or generic)

**Response**:
```json
{
  "idGroup": {
    "rxnormId": [ "123456" ],
    "name": "tezarimab"
  }
}
```

**Error Handling** (complete status code mapping):
- **200 OK**: RxCUI found, use rxnorm_code in `suspect_drug.rxnorm_code`
- **404 Not Found**: Drug name not in RxNorm database (investigational drug, typo, foreign drug name)
  - Action: Log warning with drug name
  - Set `suspect_drug.rxnorm_code == null`
  - Use `suspect_drug.name` as-is (extracted name)
  - Flag for manual review: "RxNorm_code_missing" (case processor or ADR-2 can handle)
  - Do NOT block processing (RxNorm is enhancement, not requirement)
- **429 Too Many Requests**: Rate limit exceeded (20 req/sec limit)
  - Action: Exponential backoff, retry after 500ms
  - Max 3 retries
  - If still 429 after 3 retries, treat as 404 (use extracted name, flag for manual review)
- **500 Internal Server Error**: RxNorm API down
  - Action: Retry once after 1s delay
  - If fails, treat as 404 (use extracted name, proceed without RxCUI)
  - Log: "RxNorm API unavailable" (ops monitors for systemic issue)
- **Network Timeout** (no response within 5 seconds):
  - Action: Retry once after 1s delay
  - If fails, treat as 404 (proceed without RxCUI)

**Fallback Behavior**:
- If RxNorm API persistently unavailable (>10% lookup failures over 1 hour), alert ops
- Fallback: Use extracted drug names without normalization (ADR-2 can still match to product list using string similarity)
- No local buffer (RxNorm lookup is optional enhancement, not critical path)

**Rate Limiting** (client-side):
- Max 20 requests/second (public API limit)
- Implement request queue with rate limiter (token bucket algorithm)
- Batch processing: if >100 cases pending, process in batches of 20/sec

**Data Mapping**:
- Internal `suspect_drug.name` → RxNorm API `name` parameter (brand or generic)
- RxNorm API `rxnormId[0]` → Internal `suspect_drug.rxnorm_code` (first RxCUI if multiple returned)

**Cost**: Free (public API). Latency: ~100ms per lookup. Annual cost: $0 (6,000 lookups/year × $0/lookup).

---

### ADR-1 → MedDRA API (Read)

**Endpoint**: `GET /api/v1/meddra/search?term={ae_term}&level=PT`

**Request**: AE term (lay language or medical terminology)

**Response**:
```json
{
  "preferred_term": "Headache",
  "meddra_code": "10019211",
  "soc": "Nervous system disorders"
}
```

**Error Handling** (complete status code mapping):
- **200 OK**: MedDRA PT found, use meddra_pt and meddra_code
- **404 Not Found**: AE term not in MedDRA database (novel term, typo, non-medical language)
  - Action: Log warning with AE term
  - Set `ae_description.meddra_pt == null`, `ae_description.meddra_code == null`
  - Use `ae_description.narrative` as-is
  - Flag for ADR-2 review: "MedDRA_code_missing" (ADR-2 will flag as novel AE term, confidence 0.0)
  - Do NOT block processing (ADR-2 can classify seriousness from narrative without MedDRA code)
- **401 Unauthorized**: Auth token expired, license expired, or API key invalid
  - Action: Alert ops immediately (email + Slack: "MEDDRA_API_AUTH_FAILED")
  - Do NOT retry (auth must be fixed first)
  - Block all new case processing until MedDRA API restored
  - Route all pending cases to exception queue (cannot code AE terms without MedDRA)
- **429 Too Many Requests**: Rate limit exceeded (assumed ~100 req/min)
  - Action: Exponential backoff, retry after 1s delay
  - Max 3 retries
  - If still 429, treat as 404 (proceed without MedDRA code, flag for manual coding)
- **500 Internal Server Error**: MedDRA API down
  - Action: Retry once after 1s delay
  - If fails, treat as 404 (proceed without MedDRA code)
  - Alert ops if >10% MedDRA lookups fail over 1 hour (systemic issue)
- **Network Timeout** (no response within 5 seconds):
  - Action: Retry once after 1s delay
  - If fails, treat as 404 (proceed without MedDRA code)

**Fallback Behavior**:
- If MedDRA API persistently unavailable (401 Unauthorized or >50% failures over 1 hour):
  - Primary: Alert ops, block processing until API restored (MedDRA coding is critical for ADR-2 expectedness assessment)
  - Secondary: If PV system has local MedDRA database export (MSSQL or PostgreSQL), switch to local lookup
    - Local fallback requires: MedDRA database version match (MedDRA updated quarterly), local query performance <100ms
    - Validate local fallback in Week 1 IT discovery
- If local fallback unavailable: process cases without MedDRA codes, flag for manual coding by case processor during HITL review

**Rate Limiting** (client-side):
- Assumed rate limit: 100 requests/minute (validate in Week 1)
- Implement request queue with rate limiter
- Batch processing: process cases at 90 req/min (10% buffer below limit)

**Data Mapping**:
- Internal `ae_description.narrative` → MedDRA API `term` parameter (lay language or medical term)
- MedDRA API `preferred_term` → Internal `ae_description.meddra_pt`
- MedDRA API `meddra_code` → Internal `ae_description.meddra_code` (8-digit PT code)

**Cost**: Licensed API (annual subscription required per [A16]). Week 1 validation: confirm license active, API access, rate limits.

---

### ADR-1 → ADR-2 Handoff (Internal Queue)

**Trigger**: `extraction_status == AUTO_COMPLETE`

**Data Contract**: `AECasePackage` JSON (full schema above)

**Precondition Check**: ADR-2 validates `extraction_status == AUTO_COMPLETE` before processing. If `extraction_status == HUMAN_REQUIRED`, return to ADR-1 HITL queue with error.

**Failure Mode**: If ADR-1 output schema invalid (missing required fields, malformed JSON), route to exception queue + alert ops.

**SLA**: ADR-2 begins processing within 5 minutes (async queue, not real-time).

---

**Document Owner**: FDE Engagement Lead  
**Next Review**: After Week 1 IT discovery (validate PV API, RxNorm, MedDRA, intake channel APIs)
