# FNOL Processing Agent: Capability Specification v0.1

## Table of Contents
- [1. Purpose & Scope](#1-purpose--scope)
- [2. Core Entities & Data Model](#2-core-entities--data-model)
  - [Entity: Claim](#entity-claim)
  - [Entity: Policy](#entity-policy)
  - [Entity: Adjuster](#entity-adjuster)
  - [Entity: EscalationTicket](#entity-escalationticket)
- [3. Agent Workflow & Decision Logic](#3-agent-workflow--decision-logic)
  - [Component 1: Data Extraction](#component-1-data-extraction)
  - [Component 2: Data Validation](#component-2-data-validation)
  - [Component 3: Policy Lookup](#component-3-policy-lookup)
  - [Component 4: Coverage Determination](#component-4-coverage-determination)
  - [Component 5: Severity/Complexity Triage](#component-5-severitycomplexity-triage)
  - [Component 6: Adjuster Routing](#component-6-adjuster-routing)
  - [Component 7: Claimant Acknowledgment](#component-7-claimant-acknowledgment)
  - [Component 8: System Updates](#component-8-system-updates)
  - [Component 9: Exception Handling](#component-9-exception-handling)
  - [Component 10: Quality Assurance](#component-10-quality-assurance)
- [4. System Inputs and Outputs](#4-system-inputs-and-outputs)
  - [System-Level Inputs](#system-level-inputs)
  - [System-Level Outputs](#system-level-outputs)
  - [Input/Output Data Flow Summary](#inputoutput-data-flow-summary)
- [5. Integration Points](#5-integration-points)
  - [Integration 1: Legacy Policy Administration System](#integration-1-legacy-policy-administration-system)
  - [Integration 2: CRM System](#integration-2-crm-system)
  - [Integration 3: Document Management System](#integration-3-document-management-system)
- [6. What the Agent Should NOT Do](#6-what-the-agent-should-not-do)
- [7. Handling Ambiguity and Escalation](#7-handling-ambiguity-and-escalation)
- [8. When to Ask vs When to Decide](#8-when-to-ask-vs-when-to-decide)
- [9. Validation Logic](#9-validation-logic)
  - [9.1 Happy Path Validation](#91-happy-path-validation)
  - [9.2 Edge Case Validation](#92-edge-case-validation)
  - [9.3 Failure Mode Validation](#93-failure-mode-validation)
  - [9.4 Validation Metrics](#94-validation-metrics)
- [10. Economic Model](#10-economic-model)
  - [10.1 Current State Costs](#101-current-state-costs-manual-processing-baseline)
  - [10.2 Future State Costs](#102-future-state-costs-ai--human-oversight)
  - [10.3 Cost Comparison Table](#103-cost-comparison-table)
  - [10.4 ROI Calculation](#104-roi-calculation)
  - [10.5 Sensitivity Analysis](#105-sensitivity-analysis)
  - [10.6 Critical Economic Dependencies](#106-critical-economic-dependencies)
- [11. Open Questions & Assumptions to Validate](#11-open-questions--assumptions-to-validate)
  - [Critical Unknowns](#critical-unknowns-must-resolve-in-discovery)
  - [Assumptions to Validate in Pilot](#assumptions-to-validate-in-pilot-weeks-4-6)
  - [Design Decisions to Finalize](#design-decisions-to-finalize-with-client)

---

## 1. Purpose & Scope

**Purpose**: Automate the First Notice of Loss (FNOL) intake process to reduce manual handling time from 22 minutes to <3 minutes per claim while improving routing accuracy from 82% to 97% and SLA compliance from 69% to 96%.

**Scope**:

**In Scope**:
- Extract structured data from unstructured claim reports (email, phone transcript, web form)
- Validate extracted data for completeness and format compliance
- Retrieve policy details from legacy policy administration system
- Determine coverage eligibility based on policy terms and claim details
- Assess claim severity and complexity for triage
- Route claims to appropriate adjusters based on specialization, geography, and workload
- Generate and send claimant acknowledgment within 2 hours *[A14, Metric 1]*
- Update CRM and document management systems with claim data
- Detect and escalate high-value, ambiguous, or fraudulent claims for human review *[A5: 15% of claims]*
- Monitor quality metrics and alert on anomalies *[A39, Component 10]*

**Out of Scope**:
- Adjudication and settlement decisions (handled by adjusters post-routing)
- Payment processing and disbursement
- Complex fraud investigations (agent detects and escalates only)
- Policy underwriting or modification
- Customer service interactions beyond initial acknowledgment
- Claims requiring physical inspection or appraisal

**Boundary Conditions**:
- **Agent → Human**: When claim value >$100K *[A21]*, AI confidence <85% *[A20]*, fraud indicators ≥3 *[A29]*, policy has complex exclusions, or system integration fails after retries
- **Human → Agent**: After human reviews escalated claim and provides decision (approve/modify/reject), agent resumes processing

**Success Criteria**:
- **Metric 1**: 96% of claims acknowledged within 2 hours *[A14]*
- **Metric 2**: 97% routing accuracy (no re-routing by adjuster) *[A15]*
- **Metric 3**: Cost per claim ≤$1.55 *[A16]* (91% reduction from $16.50 baseline *[A2]*)
- **Metric 4**: 85% of claims processed without human intervention *[A10]*
- **Metric 5**: Adjuster productivity increases to 10 claims/day (25% increase from 8 baseline *[A13, A18]*)

---

## 2. Core Entities & Data Model

### Entity: Claim

**Attributes**:
```
claim_id: UUID [required, unique, immutable] // System-generated identifier
policy_number: string [required, format: /^[A-Z]{2}\d{8}$/] // From legacy system [A6]
claimant_name: string [required, max: 200] // Extracted from FNOL report
claimant_contact: object [required] // {email, phone, address}
  email: string [optional, format: email]
  phone: string [optional, format: /^\+?[1-9]\d{1,14}$/]
  address: string [optional, max: 500]
loss_date: date [required, min: policy_effective_date, max: today] // Date of incident
loss_description: string [required, max: 5000] // Narrative from claimant
claim_type: enum [required] // AUTO_COLLISION, AUTO_COMPREHENSIVE, PROPERTY, LIABILITY, etc.
claim_value_usd: decimal [optional, min: 0, max: 10000000, precision: 2] // Estimated loss
document_references: array<UUID> [required] // Links to DMS documents
extraction_confidence: object [required] // Per-field confidence scores
  policy_number: float [0.0-1.0]
  claimant_name: float [0.0-1.0]
  loss_date: float [0.0-1.0]
  overall: float [0.0-1.0] // Minimum of critical field confidences
fraud_indicators: array<string> [required, default: []] // List of detected flags [A29]
coverage_determination: enum [optional] // COVERED, NOT_COVERED, AMBIGUOUS, PENDING
coverage_confidence: float [optional, 0.0-1.0] // AI confidence in determination
assigned_adjuster_id: UUID [optional] // After routing
escalation_reason: string [optional, max: 1000] // If escalated, why?
state: enum [required] // See state machine below
created_at: timestamp [required, immutable]
updated_at: timestamp [required]
acknowledged_at: timestamp [optional] // When claimant acknowledgment sent
sla_deadline: timestamp [required] // created_at + 2 hours [A14]
```

**State Machine**:
```
States: 
  RECEIVED, EXTRACTING, EXTRACTED, VALIDATING, VALIDATED, 
  POLICY_LOOKUP, POLICY_FOUND, COVERAGE_DETERMINING, COVERAGE_DETERMINED,
  TRIAGING, TRIAGED, ROUTING, ROUTED, ACKNOWLEDGING, ACKNOWLEDGED,
  PENDING_REVIEW, PENDING_SYSTEM_ISSUE, ERROR, COMPLETED

Transitions:
  RECEIVED -> EXTRACTING [on claim intake]
  EXTRACTING -> EXTRACTED [on extraction complete, confidence ≥90% on critical fields [A24]]
  EXTRACTING -> PENDING_REVIEW [on extraction complete, confidence <90% [A24]]
  EXTRACTED -> VALIDATING [on proceed]
  VALIDATING -> VALIDATED [on validation pass]
  VALIDATING -> PENDING_REVIEW [on validation fail]
  VALIDATED -> POLICY_LOOKUP [on proceed]
  POLICY_LOOKUP -> POLICY_FOUND [on successful lookup within 30s [A26]]
  POLICY_LOOKUP -> PENDING_SYSTEM_ISSUE [on lookup timeout after 3 retries]
  POLICY_LOOKUP -> PENDING_REVIEW [on policy not found (404)]
  POLICY_FOUND -> COVERAGE_DETERMINING [on proceed]
  COVERAGE_DETERMINING -> COVERAGE_DETERMINED [on determination complete, confidence ≥85% [A20]]
  COVERAGE_DETERMINING -> PENDING_REVIEW [on determination complete, confidence <85% [A20]]
  COVERAGE_DETERMINED -> TRIAGING [on proceed]
  TRIAGING -> TRIAGED [on triage complete]
  TRIAGED -> ROUTING [if not flagged for review]
  TRIAGED -> PENDING_REVIEW [if flagged: value >$100K [A21], fraud ≥3 [A29], complex policy]
  ROUTING -> ROUTED [on routing complete, confidence ≥85% [A20]]
  ROUTING -> PENDING_REVIEW [on routing complete, confidence <85% [A20]]
  ROUTED -> ACKNOWLEDGING [on proceed]
  ACKNOWLEDGING -> ACKNOWLEDGED [on acknowledgment sent]
  ACKNOWLEDGED -> COMPLETED [on final state]
  PENDING_REVIEW -> [any prior state] [on human decision: approve/modify/retry]
  PENDING_SYSTEM_ISSUE -> POLICY_LOOKUP [on system recovery, retry]
  PENDING_SYSTEM_ISSUE -> PENDING_REVIEW [on persistent failure]
  [any state] -> ERROR [on unrecoverable error]
```

**Validations**:
- `loss_date` must be within policy effective period (validated after policy lookup)
- `claim_value_usd` if provided, must be ≤ policy coverage limit
- `policy_number` must exist in legacy system (validated during lookup)
- `extraction_confidence.overall` must be ≥90% for critical fields (policy_number, claimant_name, loss_date) to proceed autonomously *[A24]*
- `fraud_indicators` count ≥3 triggers mandatory human review *[A29]*
- `sla_deadline` breach (current_time > sla_deadline) triggers alert *[A14]*

**Assumption References**: *[A5, A6, A14, A20, A21, A24, A26, A29]*

---

### Entity: Policy

**Attributes**:
```
policy_id: UUID [required, unique] // Internal ID
policy_number: string [required, unique, format: /^[A-Z]{2}\d{8}$/] // External ID
policyholder_name: string [required]
effective_date: date [required]
expiration_date: date [required]
status: enum [required] // ACTIVE, LAPSED, CANCELLED
coverage_types: array<string> [required] // [COLLISION, COMPREHENSIVE, LIABILITY, etc.]
coverage_limits: object [required] // {coverage_type: limit_usd}
deductibles: object [required] // {coverage_type: deductible_usd}
exclusions: array<string> [required] // List of exclusion clauses
endorsements: array<string> [optional] // Special policy modifications
has_complex_exclusions: boolean [required] // Flag for escalation [A27, U1]
retrieved_at: timestamp [required] // Cache timestamp
```

**State Machine**: N/A (read-only from legacy system)

**Validations**:
- `effective_date` < `expiration_date`
- `status` must be ACTIVE for claim to be covered
- `coverage_limits` must contain at least one coverage type
- `has_complex_exclusions` = true if exclusions contain keywords: "act of God", "pre-existing", "intentional", "war", "nuclear" (triggers human review)

**Assumption References**: *[A26, A27, U1, U5]*

---

### Entity: Adjuster

**Attributes**:
```
adjuster_id: UUID [required, unique]
name: string [required]
email: string [required, format: email]
specializations: array<string> [required] // [AUTO, PROPERTY, LIABILITY, etc.]
geography: array<string> [required] // [REGION_A, REGION_B, etc.]
current_workload: integer [required, min: 0] // Active claims assigned
max_workload: integer [required, default: 15] // Capacity threshold
availability_status: enum [required] // AVAILABLE, BUSY, OUT_OF_OFFICE
seniority_level: enum [required] // JUNIOR, SENIOR, LEAD // For high-value claims [A21]
```

**State Machine**: N/A (updated by external workforce management system)

**Validations**:
- Cannot route claim if `availability_status` = OUT_OF_OFFICE
- Cannot route claim if `current_workload` ≥ `max_workload`
- High-value claims (>$100K *[A21]*) must route to `seniority_level` = SENIOR or LEAD

**Assumption References**: *[A3, A9, A19, A21]*

---

### Entity: EscalationTicket

**Attributes**:
```
ticket_id: UUID [required, unique]
claim_id: UUID [required, foreign_key: Claim]
trigger_condition: string [required, max: 500] // e.g., "claim_value > $100K [A21]"
escalation_target: enum [required] // CLAIMS_SPECIALIST, SENIOR_ADJUSTER, FRAUD_INVESTIGATOR, CLAIMS_MANAGER, IT_SUPPORT
ai_recommendation: string [optional, max: 2000] // Agent's suggested action
supporting_evidence: object [required] // {extracted_data, policy_excerpt, fraud_flags, etc.}
confidence_score: float [optional, 0.0-1.0] // If AI has recommendation
human_decision: string [optional, max: 2000] // Human's action after review
resolved_at: timestamp [optional]
response_time_sla: integer [required] // Minutes, varies by escalation_target [Section 6]
created_at: timestamp [required]
```

**State Machine**:
```
States: OPEN, IN_REVIEW, RESOLVED, CANCELLED
Transitions:
  OPEN -> IN_REVIEW [on human starts review]
  IN_REVIEW -> RESOLVED [on human provides decision]
  IN_REVIEW -> CANCELLED [on claim withdrawn/duplicate]
  OPEN -> CANCELLED [on auto-cancel after 24h no response]
```

**Validations**:
- `response_time_sla` must be met: (resolved_at - created_at) ≤ response_time_sla (alert if breached)
- `human_decision` required before state = RESOLVED
- `trigger_condition` must reference specific threshold from assumptions (A20, A21, A24, A29)

**Assumption References**: *[A5, A20, A21, A24, A29, Section 6]*

---

## 3. Agent Workflow & Decision Logic

### Component 1: Data Extraction

**Input**: 
- Unstructured claim report (email body, phone transcript, web form submission)
- Format: Plain text, HTML, or JSON (from web form)
- Source: Claim intake API endpoint or email parser

**Processing Logic**:
```
1. Detect document type (email, transcript, form) and apply appropriate parser
2. Extract fields using NLP (LLM-based extraction):
   - policy_number (regex validation: /^[A-Z]{2}\d{8}$/)
   - claimant_name (entity recognition)
   - claimant_contact.email (regex: email format)
   - claimant_contact.phone (regex: E.164 format)
   - loss_date (date parsing, validate: policy_effective ≤ loss_date ≤ today)
   - loss_description (full text, max 5000 chars)
   - claim_type (classification: AUTO_COLLISION, AUTO_COMPREHENSIVE, PROPERTY, etc.)
   - claim_value_usd (optional, extract if mentioned: "$5,000 damage", "five thousand dollars")
3. Calculate per-field confidence scores (0.0-1.0) based on:
   - OCR quality (if scanned document)
   - Entity recognition confidence
   - Format validation pass/fail
4. Calculate overall_confidence = MIN(policy_number_conf, claimant_name_conf, loss_date_conf)
5. IF overall_confidence ≥ 90% [A24] THEN proceed to validation
   ELSE escalate to human review (PENDING_REVIEW state)
6. IF document is handwritten or OCR quality <70% THEN escalate to human review
```

**Output**:
- Claim entity with extracted fields and confidence scores
- State: EXTRACTED or PENDING_REVIEW
- Destination: In-memory claim object, logged to database

**Escalation Triggers**:
- `extraction_confidence.overall` <90% *[A24]*
- `extraction_confidence.policy_number` <90% (critical field) *[A24]*
- OCR quality score <70% (handwritten/low-quality scan)
- Claim flagged as high-value/ambiguous (value >$100K *[A21]* if extractable)

**Error Handling**:
- If extraction fails (LLM timeout, parsing error): Retry once, then escalate to human with error details
- If critical field missing (policy_number, claimant_name): Escalate to human with "incomplete data" reason

**Performance Requirements**:
- Time limit: 15 seconds per claim *[A23]*
- Throughput: 300 claims/day = 12.5 claims/hour avg, must handle 30 claims/hour peak

**Assumption References**: *[A5, A6, A21, A23, A24, U2]*

---

### Component 2: Data Validation

**Input**:
- Claim entity with extracted fields (state: EXTRACTED)

**Processing Logic**:
```
1. Validate policy_number format: /^[A-Z]{2}\d{8}$/
2. Validate loss_date: must be valid date, not in future
3. Validate claimant_contact.email: valid email format (if provided)
4. Validate claimant_contact.phone: valid E.164 format (if provided)
5. Validate claim_value_usd: if provided, must be ≥0 and ≤$10M
6. Validate required fields present: policy_number, claimant_name, loss_date, loss_description
7. IF all validations pass THEN proceed to policy lookup (state: VALIDATED)
   ELSE create validation error report, escalate to human (state: PENDING_REVIEW)
```

**Output**:
- Claim entity with validation_status = PASS or FAIL
- State: VALIDATED or PENDING_REVIEW
- If FAIL: validation_errors array listing specific failures

**Escalation Triggers**:
- Any validation rule fails (missing required field, invalid format)
- Validation escalation is always human-correctable (specialist fixes data, agent retries)

**Error Handling**:
- Validation errors are deterministic (no retries needed)
- Escalate with specific error messages: "Policy number format invalid: expected AA12345678, got ABC123"

**Performance Requirements**:
- Time limit: 2 seconds per claim *[A25]*
- Throughput: Same as extraction (300 claims/day)

**Assumption References**: *[A6, A25]*

---

### Component 3: Policy Lookup

**Input**:
- Claim entity with validated policy_number (state: VALIDATED)

**Processing Logic**:
```
1. Call legacy policy administration system SOAP API (see Section 4 for integration details)
2. Request: PolicyLookupRequest with policy_number and loss_date
3. Parse response: PolicyLookupResponse with policy details
4. IF response success (200) THEN:
   a. Create Policy entity from response
   b. Validate policy.status = ACTIVE (if not, escalate: "Policy lapsed/cancelled")
   c. Validate loss_date within [policy.effective_date, policy.expiration_date]
   d. Set claim.state = POLICY_FOUND
5. IF response 404 (policy not found) THEN:
   a. Escalate to human: "Policy not found. Possible typo in policy number?"
   b. Set claim.state = PENDING_REVIEW
6. IF response 500/503 (system error) THEN:
   a. Retry with exponential backoff: 1s, 2s, 4s (3 attempts total)
   b. If all retries fail: escalate to human + IT support
   c. Set claim.state = PENDING_SYSTEM_ISSUE
7. IF timeout (>30s [A26]) THEN:
   a. Retry (same logic as 500/503)
```

**Output**:
- Policy entity (cached for claim processing)
- Claim state: POLICY_FOUND, PENDING_REVIEW, or PENDING_SYSTEM_ISSUE

**Escalation Triggers**:
- Policy not found (404) → human investigates (typo, lapsed policy, data entry error)
- Policy status ≠ ACTIVE → human investigates (can claim proceed? grace period?)
- Loss date outside policy period → human investigates (coverage dispute)
- System timeout/unavailable after 3 retries → human + IT support

**Error Handling**:
- Retry logic: 3 attempts with exponential backoff (1s, 2s, 4s) *[A26]*
- Fallback: Escalate to human with error details (error code, response body, retry history)
- If system is down for >1 hour, alert IT team and operations manager

**Performance Requirements**:
- Time limit: 10 seconds per claim (baseline) *[A26]*, 30 seconds worst-case
- Timeout: 30 seconds per API call
- Throughput: Must handle 300 lookups/day, consider parallel processing if latency >30s *[U5]*

**Assumption References**: *[A26, U5]*

---

### Component 4: Coverage Determination

**Input**:
- Claim entity (state: POLICY_FOUND)
- Policy entity (from lookup)

**Processing Logic**:
```
1. Check straightforward coverage rules:
   a. claim.claim_type IN policy.coverage_types? (e.g., AUTO_COLLISION in [COLLISION, COMPREHENSIVE])
   b. claim.loss_date IN [policy.effective_date, policy.expiration_date]?
   c. claim.claim_value_usd ≤ policy.coverage_limits[claim.claim_type]? (if value provided)
2. Check exclusions:
   a. Parse claim.loss_description for exclusion keywords
   b. IF policy.has_complex_exclusions = true THEN flag for human review
   c. IF exclusion detected (e.g., "intentional damage", "pre-existing") THEN:
      - Set coverage_determination = NOT_COVERED
      - Set coverage_confidence based on keyword match strength
3. Run ML model (if available [U2]) for ambiguous cases:
   a. Input: claim details + policy details
   b. Output: coverage_determination (COVERED/NOT_COVERED/AMBIGUOUS), confidence score
4. Decision logic:
   a. IF coverage_confidence ≥85% [A20] AND policy.has_complex_exclusions = false THEN:
      - Set claim.coverage_determination autonomously
      - Proceed to triage (state: COVERAGE_DETERMINED)
   b. ELSE:
      - Escalate to human (state: PENDING_REVIEW)
      - Provide AI recommendation + supporting evidence (policy excerpt, exclusion match)
5. Special cases:
   a. IF claim.fraud_indicators.length ≥3 [A29] THEN escalate to fraud investigator
   b. IF claim.claim_value_usd >$100K [A21] THEN escalate to claims manager
```

**Output**:
- Claim.coverage_determination: COVERED, NOT_COVERED, AMBIGUOUS, or PENDING
- Claim.coverage_confidence: 0.0-1.0
- State: COVERAGE_DETERMINED or PENDING_REVIEW

**Escalation Triggers**:
- `coverage_confidence` <85% *[A20]*
- `policy.has_complex_exclusions` = true
- `fraud_indicators` ≥3 *[A29]*
- `claim_value_usd` >$100K *[A21]*
- Novel claim type (not well-represented in training data *[U2]*)

**Error Handling**:
- If ML model fails (timeout, error): Fall back to rule-based system (lower confidence, likely escalates)
- If rule-based system is ambiguous: Escalate with "coverage ambiguity" reason

**Performance Requirements**:
- Time limit: 8 seconds per claim *[A28]*
- Throughput: 300 claims/day

**Assumption References**: *[A5, A6, A9, A10, A20, A21, A27, A28, A29, U1, U2]*

---

### Component 5: Severity/Complexity Triage

**Input**:
- Claim entity (state: COVERAGE_DETERMINED)
- Policy entity

**Processing Logic**:
```
1. Calculate severity score (0-100):
   a. Claim value: 0-30 points (0 for <$1K, 30 for >$100K, linear scale)
   b. Fraud indicators: 10 points per indicator (max 30)
   c. Policy complexity: 20 points if has_complex_exclusions = true
   d. Coverage confidence: 20 points if coverage_confidence <85% [A20]
2. Classify severity:
   a. severity_score <30: ROUTINE
   b. severity_score 30-60: MODERATE
   c. severity_score >60: HIGH
3. Determine oversight requirement:
   a. IF severity = HIGH OR claim_value >$100K [A21] OR fraud_indicators ≥3 [A29] THEN:
      - Flag for human review
      - Set escalation_reason with specific triggers
      - Set claim.state = PENDING_REVIEW
   b. ELSE:
      - Proceed autonomously
      - Set claim.state = TRIAGED
4. Generate triage report:
   a. Severity classification
   b. Key risk factors (value, fraud, complexity)
   c. Recommended oversight level (autonomous vs. human review)
   d. Confidence score for triage decision
```

**Output**:
- Claim.severity_classification: ROUTINE, MODERATE, HIGH
- Claim.requires_human_oversight: boolean
- State: TRIAGED or PENDING_REVIEW

**Escalation Triggers**:
- Severity = HIGH
- `claim_value_usd` >$100K *[A21]*
- `fraud_indicators` ≥3 *[A29]*
- `coverage_confidence` <85% *[A20]*
- `policy.has_complex_exclusions` = true
- AI triage confidence <85% *[A20]*

**Error Handling**:
- Triage logic is deterministic (rule-based scoring), minimal error risk
- If ML-based triage model fails: Fall back to rule-based scoring (conservative, may over-escalate)

**Performance Requirements**:
- Time limit: 10 seconds per claim *[A30]*
- Throughput: 300 claims/day

**Assumption References**: *[A5, A6, A10, A20, A21, A29, A30, A31, U1, U2, U12]*

---

### Component 6: Adjuster Routing

**Input**:
- Claim entity (state: TRIAGED, requires_human_oversight = false)
- List of available Adjuster entities

**Processing Logic**:
```
1. Filter adjusters by criteria:
   a. specializations CONTAINS claim.claim_type
   b. geography CONTAINS claim.loss_location (extract from address)
   c. availability_status = AVAILABLE
   d. current_workload < max_workload
   e. IF claim_value >$100K [A21] THEN seniority_level IN [SENIOR, LEAD]
2. Rank filtered adjusters:
   a. Primary: Lowest current_workload (load balancing)
   b. Secondary: Highest specialization match score
   c. Tertiary: Geographic proximity (if available)
3. Select top-ranked adjuster:
   a. IF confidence in selection ≥85% [A20] THEN:
      - Assign claim.assigned_adjuster_id
      - Increment adjuster.current_workload
      - Set claim.state = ROUTED
   b. ELSE:
      - Escalate to human for routing decision
      - Provide top 3 adjuster recommendations with rationale
      - Set claim.state = PENDING_REVIEW
4. Special cases:
   a. IF no adjusters available (all at max_workload or out_of_office) THEN:
      - Escalate to operations manager: "No available adjusters"
      - Set claim.state = PENDING_REVIEW
   b. IF claim flagged as VIP or sensitive THEN:
      - Escalate to senior adjuster or claims manager for manual assignment
```

**Output**:
- Claim.assigned_adjuster_id: UUID
- Claim.routing_confidence: 0.0-1.0
- State: ROUTED or PENDING_REVIEW

**Escalation Triggers**:
- Routing confidence <85% *[A20]*
- No available adjusters (all at capacity or unavailable)
- Claim value >$100K *[A21]* (requires senior adjuster, human confirms)
- VIP claimant or sensitive circumstances (detected from claim metadata)

**Error Handling**:
- If adjuster assignment fails (CRM API error): Retry once, then escalate to human + IT support
- If adjuster rejects claim within 1 hour ("Not My Claim" button): Log routing error, re-route automatically or escalate if confidence <85%

**Performance Requirements**:
- Time limit: 3 seconds per claim *[A33]*
- Throughput: 300 claims/day

**Assumption References**: *[A3, A5, A9, A10, A19, A20, A21, A33, U2, U4]*

---

### Component 7: Claimant Acknowledgment

**Input**:
- Claim entity (state: ROUTED)
- Assigned Adjuster entity

**Processing Logic**:
```
1. Generate acknowledgment message using template:
   Template:
   "Dear [claimant_name],
   
   We have received your claim (#[claim_id]) regarding [claim_type] on [loss_date]. 
   
   Your claim is being reviewed by [adjuster_name] ([adjuster_email], [adjuster_phone]).
   You can expect to hear from your adjuster within [timeframe] business days.
   
   Your claim number for reference: [claim_id]
   
   If you have questions, please contact [adjuster_name] directly or call our claims hotline at 1-800-XXX-XXXX.
   
   Sincerely,
   [Company Name] Claims Team"
   
2. Populate template variables:
   - claimant_name, claim_id, claim_type, loss_date from Claim entity
   - adjuster_name, adjuster_email, adjuster_phone from Adjuster entity
   - timeframe: 2 business days (standard) or 1 business day (if high-value)
3. Send acknowledgment:
   a. Primary channel: Email to claimant_contact.email (if provided)
   b. Secondary channel: SMS to claimant_contact.phone (if provided and email fails)
   c. Log acknowledgment in CRM
4. Update claim:
   a. Set claim.acknowledged_at = current_timestamp
   b. Set claim.state = ACKNOWLEDGED
5. Check SLA compliance:
   a. IF acknowledged_at ≤ sla_deadline (created_at + 2 hours [A14]) THEN SLA met
   b. ELSE log SLA breach, send apology message, alert operations manager
```

**Output**:
- Acknowledgment message sent via email/SMS
- Claim.acknowledged_at: timestamp
- State: ACKNOWLEDGED

**Escalation Triggers**:
- Email/SMS delivery fails (bounce, invalid address): Escalate to specialist for manual outreach
- Claimant has special communication preferences (language, accessibility): Escalate for human review of message *[U11]*
- Claim involves sensitive circumstances (death, severe injury): Escalate for human review of tone/content

**Error Handling**:
- If email send fails: Retry once, then attempt SMS, then escalate to specialist
- If template generation fails (LLM timeout): Use fallback static template, log error

**Performance Requirements**:
- Time limit: 5 seconds per claim *[A36]*
- Throughput: 300 claims/day
- SLA: Must send within 2 hours of claim receipt *[A14]*

**Assumption References**: *[A6, A14, A34, A36, U11]*

---

### Component 8: System Updates

**Input**:
- Claim entity (state: ACKNOWLEDGED)

**Processing Logic**:
```
1. Update CRM:
   a. Create claim record with all claim fields
   b. Link to policy record (policy_id)
   c. Link to adjuster record (assigned_adjuster_id)
   d. Set claim status = OPEN
   e. API: POST /api/v1/claims (see Section 4 for integration details)
2. Upload documents to DMS:
   a. Original claim report (email, transcript, form)
   b. Extracted data summary (JSON)
   c. Policy details (PDF or JSON)
   d. Acknowledgment message (PDF)
   e. API: POST /api/v1/documents (see Section 4)
3. Update claim state:
   a. Set claim.state = COMPLETED
   b. Log final timestamp
4. Trigger downstream workflows:
   a. Notify adjuster (email/Slack) with claim details
   b. Schedule follow-up tasks in CRM (adjuster review, claimant contact)
```

**Output**:
- CRM record created (claim_id in CRM)
- Documents uploaded to DMS (document_ids)
- State: COMPLETED

**Escalation Triggers**:
- CRM API fails after retries: Escalate to IT support + specialist (manual data entry)
- DMS upload fails after retries: Escalate to IT support (documents stored locally, manual upload)

**Error Handling**:
- If API call fails (500, 503): Retry 3 times with exponential backoff (1s, 2s, 4s)
- If all retries fail: Escalate to human + IT support, store data locally for manual entry
- If partial success (CRM succeeds, DMS fails): Continue processing, log error, retry DMS in background

**Performance Requirements**:
- Time limit: 8 seconds per claim *[A37]*
- Throughput: 300 claims/day

**Assumption References**: *[A6, A34, A37, U5]*

---

### Component 9: Exception Handling

**Input**:
- Claim entity in any state
- Exception trigger (missing data, system error, claimant dispute, etc.)

**Processing Logic**:
```
1. Detect exception type:
   a. MISSING_DATA: Required field missing after extraction
   b. SYSTEM_ERROR: Integration failure (CRM, policy admin, DMS)
   c. CLAIMANT_UNREACHABLE: Email/SMS bounce, no response
   d. COVERAGE_DISPUTE: Claimant disputes coverage determination
   e. FRAUD_INVESTIGATION: Fraud indicators require investigation
2. Create EscalationTicket:
   a. Set trigger_condition = exception type + details
   b. Set escalation_target based on exception type:
      - MISSING_DATA, CLAIMANT_UNREACHABLE → CLAIMS_SPECIALIST
      - SYSTEM_ERROR → IT_SUPPORT + CLAIMS_SPECIALIST
      - COVERAGE_DISPUTE → CLAIMS_MANAGER
      - FRAUD_INVESTIGATION → FRAUD_INVESTIGATOR
   c. Provide AI recommendation (if applicable):
      - MISSING_DATA: "Contact claimant for missing info: [field]"
      - SYSTEM_ERROR: "Retry after system recovery, or manual entry"
      - COVERAGE_DISPUTE: "Review policy section [X], consider appeal"
   d. Attach supporting evidence (claim details, error logs, policy excerpt)
3. Notify escalation target:
   a. Send email/Slack with ticket details
   b. Set response_time_sla based on severity (15-120 min)
4. Pause claim processing:
   a. Set claim.state = PENDING_REVIEW or PENDING_SYSTEM_ISSUE
   b. Wait for human decision
5. Resume processing on human decision:
   a. Human provides decision (approve, modify, reject, request more info)
   b. Agent updates claim based on decision
   c. Agent retries failed step or proceeds to next step
```

**Output**:
- EscalationTicket created
- Claim state: PENDING_REVIEW or PENDING_SYSTEM_ISSUE
- Human notified

**Escalation Triggers**:
- All exceptions escalate to human (by definition, exceptions are non-standard)

**Error Handling**:
- Exception handling itself should not fail (defensive programming)
- If escalation notification fails: Log error, retry notification, alert operations manager

**Performance Requirements**:
- Exception detection: Real-time (as soon as exception occurs)
- Human response time: Varies by exception type (15-120 min SLA)
- Exception rate: Expected 8% of claims *[A38]*, alert if >15%

**Assumption References**: *[A38, U1, U2, U3, U10]*

---

### Component 10: Quality Assurance

**Input**:
- All completed claims (state: COMPLETED)
- Real-time monitoring data (API logs, state transitions, timestamps)

**Processing Logic**:
```
1. Real-time monitoring (continuous):
   a. Track SLA compliance: % claims acknowledged within 2 hours [A14]
   b. Track routing accuracy: % claims not re-routed by adjuster
   c. Track escalation rate: % claims escalated to human [A5]
   d. Track processing time: Median time from RECEIVED to ACKNOWLEDGED
   e. Track system uptime: % API calls successful within timeout
   f. Alert if any metric breaches threshold (see Section 8 for thresholds)
2. Daily QA audit (automated):
   a. Sample 5% of autonomous claims (random selection)
   b. Review extraction accuracy: Compare extracted fields to source document
   c. Review coverage determination: Compare AI decision to policy terms
   d. Review routing: Check adjuster specialization match
   e. Calculate error rates by component (extraction, coverage, routing)
   f. Generate daily QA report with error breakdown
3. Error detection:
   a. Adjuster clicks "Not My Claim": Log routing error, investigate root cause
   b. Adjuster disputes coverage: Log coverage error, investigate root cause
   c. SLA breach: Log breach, investigate bottleneck (extraction time? policy lookup latency?)
   d. Confidence distribution shift: Alert if >30% of claims have confidence <85% (model drift)
4. Root cause analysis (human-led, AI-supported):
   a. Agent provides error context: claim details, decision rationale, confidence scores
   b. Human investigates: Data quality issue? Model drift? Policy change? System latency?
   c. Human decides remediation: Retrain model? Update rules? Fix data? Escalate to IT?
5. Continuous improvement:
   a. Log all errors for model retraining [U2]
   b. Track error trends over time (improving? degrading?)
   c. Adjust thresholds if needed (A20, A21, A24, A29) based on error cost vs. escalation cost
```

**Output**:
- Real-time monitoring dashboard (metrics, alerts)
- Daily QA report (error rates, sample audit results)
- Error logs (for retraining, root cause analysis)

**Escalation Triggers**:
- Any metric breaches alert threshold (see Section 8)
- Error rate exceeds target (>3% for routing *[A9]*, >5% for extraction)
- Confidence distribution shifts (indicates model drift or data quality issue)
- SLA breach rate exceeds 10% in any 4-hour window

**Error Handling**:
- QA monitoring should not disrupt claim processing (background process)
- If monitoring fails: Alert IT team, continue processing (blind operation)

**Performance Requirements**:
- Real-time monitoring: <1 sec latency for metric updates
- Daily audit: Complete within 1 hour (automated, runs overnight)
- Human QA review: 45 min/day *[A39]*

**Assumption References**: *[A9, A14, A15, A39, A40, U6, U10]*

---

## 4. System Inputs and Outputs

### System-Level Inputs

**Input 1: Unstructured Claim Reports**

**Source**: Multiple channels (email, phone transcripts, web forms, mobile app submissions)

**Format**:
- **Email**: Plain text or HTML body, may include inline images or attachments (PDF, JPG, PNG)
- **Phone Transcript**: Plain text (from call center transcription service), may include agent notes
- **Web Form**: JSON payload with structured fields + free-text description
- **Mobile App**: JSON payload with structured fields + photos (JPG/PNG, max 10MB per photo *[A34]*)

**Volume**: 300 reports/day *[A6]*, distributed across channels:
- Email: 45% (135/day)
- Phone: 30% (90/day)
- Web Form: 20% (60/day)
- Mobile App: 5% (15/day)

**Arrival Pattern**: 
- Peak hours: 9am-11am, 2pm-4pm (50% of daily volume)
- Off-peak: 11am-2pm, 4pm-6pm (30% of daily volume)
- After-hours: 6pm-9am (20% of daily volume, queued for next business day)

**Quality Characteristics**:
- **Email**: Variable quality, may include forwarded messages, signatures, disclaimers (OCR confidence: 70-95% *[A24]*)
- **Phone**: Transcription errors possible (OCR confidence: 80-95%)
- **Web Form**: High quality, structured fields pre-validated (OCR confidence: 95-99%)
- **Mobile App**: High quality, photos may have lighting/angle issues (OCR confidence: 90-98%)

**Required Fields** (must be extractable or provided):
- Policy number (format: /^[A-Z]{2}\d{8}$/ *[A6]*)
- Claimant name (string, max 200 chars)
- Contact information (email OR phone, at least one required)
- Loss date (date, format: YYYY-MM-DD)
- Loss description (string, max 5000 chars)

**Optional Fields**:
- Claim value estimate (decimal, USD)
- Loss location (address string)
- Photos/documents (attachments)
- Police report number (string)
- Witness information (string)

**Delivery Mechanism**:
- **Email**: IMAP/POP3 polling (every 5 minutes) or webhook from email service
- **Phone**: REST API callback from call center system (real-time)
- **Web Form**: REST API POST to `/api/v1/claims/intake` (real-time)
- **Mobile App**: REST API POST to `/api/v1/claims/intake` (real-time)

**Assumption References**: *[A6, A24, A34, U2]*

---

**Input 2: Policy Data (from Legacy Policy Administration System)**

**Source**: Legacy Policy Administration System (PolicyAdmin) via SOAP API

**Format**: XML (SOAP envelope, see Section 4 Integration 1 for schema)

**Trigger**: On-demand lookup per claim (triggered by Component 3: Policy Lookup)

**Volume**: 300 lookups/day (one per claim)

**Latency**: 10-30 seconds per lookup *[A26, U5]*

**Availability**: 99%+ uptime (assumed, actual unknown *[U5]*)

**Fields Retrieved**:
- Policy ID (UUID, internal identifier)
- Policy number (string, external identifier)
- Policyholder name (string)
- Effective date (date)
- Expiration date (date)
- Status (enum: ACTIVE, LAPSED, CANCELLED)
- Coverage types (array of strings: AUTO_COLLISION, AUTO_COMPREHENSIVE, PROPERTY, LIABILITY, etc.)
- Coverage limits (object: {coverage_type: limit_usd})
- Deductibles (object: {coverage_type: deductible_usd})
- Exclusions (array of strings: exclusion clause text)
- Endorsements (array of strings: special policy modifications)

**Error Conditions**:
- **404 (PolicyNotFound)**: Policy number does not exist in system → escalate to human
- **500 (Server Error)**: System error → retry 3 times, then escalate
- **503 (Service Unavailable)**: System temporarily down → retry 3 times, then escalate
- **Timeout (>30 sec)**: No response → retry 3 times, then escalate

**Caching Strategy**:
- Cache policy data for 24 hours (policies rarely change mid-day)
- Invalidate cache if policy lookup returns different data than cached
- Cache key: policy_number + loss_date (loss_date affects policy period validation)

**Assumption References**: *[A26, U5]*

---

**Input 3: Adjuster Availability Data (from CRM/Workforce Management System)**

**Source**: CRM system or workforce management system

**Format**: JSON (REST API response)

**Trigger**: On-demand query per claim (triggered by Component 6: Adjuster Routing)

**Volume**: 300 queries/day (one per claim that reaches routing step, ~85% of claims *[A10]*)

**Latency**: <2 seconds per query (assumed, REST API)

**Refresh Rate**: Real-time (adjuster availability updates as claims are assigned/closed)

**Fields Retrieved**:
- Adjuster ID (UUID)
- Name (string)
- Email (string)
- Phone (string)
- Specializations (array of strings: AUTO, PROPERTY, LIABILITY, etc.)
- Geography (array of strings: REGION_A, REGION_B, etc.)
- Current workload (integer: number of active claims)
- Max workload (integer: capacity threshold, typically 15 *[A19]*)
- Availability status (enum: AVAILABLE, BUSY, OUT_OF_OFFICE)
- Seniority level (enum: JUNIOR, SENIOR, LEAD)

**Error Conditions**:
- **500 (Server Error)**: System error → retry once, then escalate to human for manual routing
- **Empty Result Set**: No adjusters available → escalate to operations manager

**Assumption References**: *[A19]*

---

**Input 4: Fraud Detection Signals (from Fraud Detection Service, if available)**

**Source**: External fraud detection service (e.g., LexisNexis, SAS Fraud Management) OR internal rule-based system

**Format**: JSON (REST API response)

**Trigger**: On-demand query per claim (triggered by Component 4: Coverage Determination)

**Volume**: 300 queries/day (one per claim)

**Latency**: <5 seconds per query (assumed)

**Availability**: Optional (if service unavailable, use internal rule-based fraud detection *[A29]*)

**Fields Retrieved**:
- Fraud risk score (float: 0.0-1.0, higher = more suspicious)
- Fraud indicators (array of strings: flag names)
- Indicator details (object: {indicator_name: evidence})

**Example Fraud Indicators**:
- `recent_policy_inception`: Policy effective date within 30 days of claim
- `claim_near_limit`: Claim value >80% of policy limit
- `inconsistent_description`: Loss description inconsistent with damage photos (NLP analysis)
- `multiple_claims_short_period`: Claimant has 3+ claims in past 12 months
- `suspicious_claimant_history`: Claimant flagged in fraud database
- `unusual_loss_location`: Loss location far from claimant's address
- `duplicate_claim`: Similar claim already filed (same loss date, location, description)

**Threshold**: If fraud_indicators.length ≥3 *[A29]*, escalate to fraud investigator

**Fallback (if service unavailable)**: Use internal rule-based system:
- Check policy inception date (if <30 days, flag `recent_policy_inception`)
- Check claim value vs. limit (if >80%, flag `claim_near_limit`)
- Check claimant history in CRM (if 3+ claims in 12 months, flag `multiple_claims_short_period`)

**Assumption References**: *[A29]*

---

**Input 5: Human Decisions (from Escalation Workflow)**

**Source**: CRM system (EscalationTicket entity updated by human reviewers)

**Format**: JSON (REST API response or database query)

**Trigger**: Polling (every 30 seconds) or webhook (real-time notification when ticket resolved)

**Volume**: 45 decisions/day (15% of claims escalated *[A5]*)

**Latency**: Variable (depends on human response time, SLA: 15-120 minutes per escalation type, see Section 6)

**Fields Retrieved**:
- Ticket ID (UUID)
- Claim ID (UUID, link to Claim entity)
- Human decision (string: "APPROVE", "MODIFY", "REJECT", "REQUEST_MORE_INFO")
- Decision rationale (string: explanation of decision)
- Modified fields (object: {field_name: new_value}, if decision = "MODIFY")
- Next action (string: "PROCEED_TO_NEXT_STEP", "RETRY_CURRENT_STEP", "MANUAL_PROCESSING", "CLOSE_CLAIM")

**Decision Types**:
- **APPROVE**: Human approves AI recommendation, agent proceeds to next step
- **MODIFY**: Human modifies AI recommendation (e.g., route to different adjuster), agent proceeds with modified data
- **REJECT**: Human rejects claim or coverage, agent closes claim with NOT_COVERED status
- **REQUEST_MORE_INFO**: Human needs more information from claimant, agent sends follow-up request and pauses processing

**Assumption References**: *[A5, A31]*

---

### System-Level Outputs

**Output 1: Claimant Acknowledgment**

**Destination**: Claimant (via email, SMS, or both)

**Format**: 
- **Email**: HTML with plain text fallback, sent via SMTP or email service API (e.g., SendGrid, AWS SES)
- **SMS**: Plain text, max 160 chars, sent via SMS gateway API (e.g., Twilio)

**Trigger**: After claim successfully routed (Component 7: Claimant Acknowledgment)

**Volume**: 300 acknowledgments/day (one per claim)

**Timing**: Within 2 hours of claim receipt *[A14, Metric 1]*, typically within 2 minutes for autonomous claims

**Content** (see Component 7 for template):
- Claim number (UUID)
- Claim type (e.g., AUTO_COLLISION)
- Loss date
- Assigned adjuster name, email, phone
- Expected next steps (adjuster will contact within X business days)
- Claims hotline number (for questions)

**Delivery Confirmation**:
- Email: Track open rate, bounce rate (log in CRM)
- SMS: Track delivery status (log in CRM)
- If delivery fails (bounce, invalid number): Escalate to specialist for manual outreach

**Assumption References**: *[A14, A34, A36, U11]*

---

**Output 2: Claim Record (in CRM)**

**Destination**: CRM system (via REST API)

**Format**: JSON (see Section 4 Integration 2 for schema)

**Trigger**: After acknowledgment sent (Component 8: System Updates)

**Volume**: 300 records/day (one per claim)

**Timing**: Within 3 minutes of claim receipt (for autonomous claims), within 20 minutes for escalated claims

**Fields Written**:
- Claim ID (UUID, system-generated)
- Policy ID (UUID, from policy lookup)
- Policy number (string)
- Claimant name, email, phone, address
- Loss date, description, type, value
- Coverage determination (COVERED, NOT_COVERED, PENDING)
- Assigned adjuster ID (UUID)
- Status (OPEN, PENDING_REVIEW, CLOSED)
- Created timestamp, acknowledged timestamp
- SLA deadline, SLA status (MET, BREACHED)
- Escalation ticket ID (if escalated)

**Record Lifecycle**:
- Created: When claim reaches COMPLETED state (Component 8)
- Updated: When adjuster updates claim (outside agent scope)
- Closed: When adjuster closes claim (outside agent scope)

**Assumption References**: *[A37]*

---

**Output 3: Documents (in Document Management System)**

**Destination**: Document Management System (DMS) via REST API

**Format**: Multipart/form-data (file upload + JSON metadata, see Section 4 Integration 3 for schema)

**Trigger**: After CRM record created (Component 8: System Updates)

**Volume**: 1,200 documents/day (4 documents per claim × 300 claims)

**Timing**: Within 5 minutes of claim receipt (for autonomous claims), within 25 minutes for escalated claims

**Document Types**:
1. **FNOL_REPORT**: Original claim report (email body, transcript, form submission)
   - Format: PDF (converted from email/text) or original format (if already PDF)
   - Size: Typically 50-500 KB
2. **EXTRACTED_DATA**: JSON summary of extracted fields + confidence scores
   - Format: JSON
   - Size: Typically 5-10 KB
3. **POLICY_DETAILS**: Policy information from legacy system
   - Format: JSON (converted from SOAP XML response)
   - Size: Typically 10-20 KB
4. **ACKNOWLEDGMENT**: Claimant acknowledgment message
   - Format: PDF (generated from email template)
   - Size: Typically 20-50 KB

**Metadata** (attached to each document):
- Claim ID (UUID, link to claim)
- Document type (enum: FNOL_REPORT, EXTRACTED_DATA, POLICY_DETAILS, ACKNOWLEDGMENT)
- File name (string)
- Uploaded by (string: "fnol_agent")
- Uploaded timestamp (datetime)

**Assumption References**: *[A37]*

---

**Output 4: Escalation Tickets (in CRM)**

**Destination**: CRM system (via REST API)

**Format**: JSON (see Section 4 Integration 2 for schema)

**Trigger**: When escalation condition detected (Components 1-6, 9)

**Volume**: 45 tickets/day (15% of claims *[A5]*)

**Timing**: Immediately upon escalation detection (within seconds)

**Fields Written**:
- Ticket ID (UUID, system-generated)
- Claim ID (UUID, link to claim)
- Trigger condition (string: specific threshold violated, e.g., "claim_value = $150K > $100K [A21]")
- Escalation target (enum: CLAIMS_SPECIALIST, SENIOR_ADJUSTER, FRAUD_INVESTIGATOR, CLAIMS_MANAGER, IT_SUPPORT, OPERATIONS_MANAGER)
- AI recommendation (string: suggested action, if confidence >50%)
- Supporting evidence (JSON object: extracted data, policy excerpt, fraud indicators, error logs, etc.)
- Confidence score (float: 0.0-1.0, if AI has recommendation)
- Response time SLA (integer: minutes, varies by escalation target, see Section 6)
- Status (enum: OPEN, IN_REVIEW, RESOLVED, CANCELLED)
- Created timestamp
- Resolved timestamp (when human provides decision)
- Human decision (string: populated by human reviewer)

**Notification** (triggered when ticket created):
- Email to escalation target (contains ticket summary + link to CRM)
- Slack message to escalation target (if integration available)
- SMS to escalation target (for urgent escalations: SLA breach, system failure)

**Assumption References**: *[A5, A20, A21, A24, A29]*

---

**Output 5: Adjuster Notifications**

**Destination**: Assigned adjuster (via email, Slack, or CRM notification)

**Format**: 
- **Email**: HTML with plain text fallback
- **Slack**: Formatted message with action buttons
- **CRM Notification**: In-app notification (bell icon)

**Trigger**: After claim routed and CRM record created (Component 8: System Updates)

**Volume**: 255 notifications/day (85% of claims processed autonomously *[A10]*)

**Timing**: Within 5 minutes of claim routing

**Content**:
- Claim number (UUID)
- Claimant name, contact info
- Claim type, loss date, loss description
- Claim value (if provided)
- Coverage determination (COVERED, NOT_COVERED)
- Priority (ROUTINE, MODERATE, HIGH based on severity triage)
- Link to claim details in CRM
- Action required: "Review claim and contact claimant within X business days"

**Action Buttons** (in Slack/CRM):
- "View Claim" (link to CRM)
- "Not My Claim" (triggers routing error investigation, see Failure Mode 1 in Section 8.3)
- "Request More Info" (creates follow-up task)

**Assumption References**: *[A10]*

---

**Output 6: Quality Metrics (to Monitoring Dashboard)**

**Destination**: Monitoring dashboard (Grafana, Datadog, or custom dashboard)

**Format**: Time-series metrics (Prometheus format or equivalent)

**Trigger**: Continuous (metrics emitted in real-time as claims are processed)

**Volume**: ~50 metric data points per claim × 300 claims/day = 15,000 data points/day

**Timing**: Real-time (1-second granularity for critical metrics, 1-minute for non-critical)

**Metrics Emitted** (see Section 8.4 for full list):

**Real-Time Metrics**:
- `claims_received_total` (counter): Total claims received, labeled by channel (email, phone, web, mobile)
- `claims_processed_total` (counter): Total claims processed, labeled by outcome (autonomous, escalated, error)
- `claim_processing_duration_seconds` (histogram): Time from receipt to acknowledgment, labeled by outcome
- `sla_compliance_rate` (gauge): % of claims acknowledged within 2 hours *[A14]*
- `routing_accuracy_rate` (gauge): % of claims not re-routed *[A15]*
- `escalation_rate` (gauge): % of claims escalated to human *[A5]*
- `system_integration_uptime` (gauge): % of API calls successful, labeled by system (PolicyAdmin, CRM, DMS)
- `ai_confidence_distribution` (histogram): Distribution of AI confidence scores, labeled by component

**Component-Specific Metrics**:
- `extraction_duration_seconds` (histogram): Time for data extraction *[A23]*
- `extraction_confidence` (histogram): Confidence scores for extracted fields *[A24]*
- `policy_lookup_duration_seconds` (histogram): Time for policy lookup *[A26]*
- `coverage_determination_duration_seconds` (histogram): Time for coverage determination *[A28]*
- `routing_duration_seconds` (histogram): Time for adjuster routing *[A33]*

**Error Metrics**:
- `extraction_errors_total` (counter): Extraction errors, labeled by field (policy_number, claimant_name, etc.)
- `coverage_errors_total` (counter): Coverage determination errors (detected by adjuster feedback or QA audit)
- `routing_errors_total` (counter): Routing errors (adjuster clicks "Not My Claim")
- `system_errors_total` (counter): System integration errors, labeled by system and error type

**Alert Conditions** (see Section 8.4 for thresholds):
- SLA compliance rate <90% in any 4-hour window
- Routing accuracy rate <90% in any day
- Escalation rate <10% or >25% in any day
- System integration uptime <95% in any hour
- AI confidence distribution shift (>30% of decisions with confidence <85%)

**Assumption References**: *[A5, A8, A9, A14, A15, A20, A23, A24, A26, A28, A30, A33, A36, A37, A39]*

---

**Output 7: Daily QA Report**

**Destination**: QA team + operations manager (via email)

**Format**: PDF report with charts and tables

**Trigger**: Automated daily at 6am (covers previous business day)

**Volume**: 1 report/day

**Timing**: Generated overnight (processing time: ~30 minutes)

**Content**:

1. **Summary Statistics**:
   - Total claims processed: 300
   - Autonomous claims: 255 (85%)
   - Escalated claims: 45 (15%)
   - SLA compliance rate: 96%
   - Routing accuracy rate: 97%
   - Cost per claim: $1.55 avg

2. **Error Breakdown** (by component):
   - Extraction errors: 5 (1.7%)
   - Coverage errors: 2 (0.7%)
   - Routing errors: 9 (3.0%)
   - System errors: 3 (1.0%)

3. **Escalation Analysis**:
   - By trigger: High-value (12), Low confidence (18), Fraud (8), Complex policy (7)
   - By target: Claims Specialist (25), Senior Adjuster (12), Fraud Investigator (8)
   - Avg human review time: 12 minutes

4. **Sample Audit Results** (5% random sample = 15 claims):
   - Extraction accuracy: 14/15 correct (93%)
   - Coverage accuracy: 15/15 correct (100%)
   - Routing accuracy: 14/15 correct (93%)

5. **Trends** (week-over-week comparison):
   - SLA compliance: 96% (↑2% from last week)
   - Routing accuracy: 97% (↔ no change)
   - Escalation rate: 15% (↓3% from last week)

6. **Action Items**:
   - Investigate extraction errors for handwritten forms (5 errors, all handwritten)
   - Review routing logic for property claims (3 errors, all property)
   - Schedule model retraining for coverage determination (2 errors, same exclusion missed)

**Assumption References**: *[A39]*

---

**Output 8: Error Logs (for Model Retraining)**

**Destination**: ML training pipeline (data lake or training data repository)

**Format**: JSONL (JSON Lines, one JSON object per line)

**Trigger**: Continuous (errors logged as they occur)

**Volume**: ~30 errors/day (10% of claims have some error detected *[A9, A22, A27, A32]*)

**Timing**: Real-time (errors written to log immediately)

**Fields Logged**:
- Error ID (UUID)
- Claim ID (UUID, link to claim)
- Component (enum: EXTRACTION, VALIDATION, POLICY_LOOKUP, COVERAGE, TRIAGE, ROUTING)
- Error type (string: specific error category)
- AI decision (string: what agent decided)
- Correct decision (string: what human corrected to)
- Input data (JSON: claim details, policy details, etc.)
- AI confidence (float: confidence score for incorrect decision)
- Timestamp (datetime)

**Usage**:
- ML engineers review error logs weekly
- Errors used to augment training data (add corrected examples)
- Model retraining triggered when error count exceeds threshold (e.g., >50 errors for specific error type)

**Assumption References**: *[A9, A22, A27, A32, U2]*

---

### Input/Output Data Flow Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SYSTEM INPUTS                                │
├─────────────────────────────────────────────────────────────────────┤
│ 1. Unstructured Claim Reports (300/day)                             │
│    ├─ Email (135/day, 70-95% OCR confidence [A24])                  │
│    ├─ Phone (90/day, 80-95% OCR confidence)                         │
│    ├─ Web Form (60/day, 95-99% OCR confidence)                      │
│    └─ Mobile App (15/day, 90-98% OCR confidence)                    │
│                                                                      │
│ 2. Policy Data (300 lookups/day, 10-30 sec latency [A26, U5])      │
│    └─ Legacy PolicyAdmin System (SOAP API)                          │
│                                                                      │
│ 3. Adjuster Availability (255 queries/day, <2 sec latency)         │
│    └─ CRM/Workforce Management System (REST API)                    │
│                                                                      │
│ 4. Fraud Detection Signals (300 queries/day, <5 sec latency)       │
│    └─ Fraud Detection Service (REST API, optional)                  │
│                                                                      │
│ 5. Human Decisions (45/day, 15-120 min latency [A5, A31])          │
│    └─ CRM Escalation Tickets (REST API or polling)                  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FNOL PROCESSING AGENT                             │
│                                                                      │
│  Components 1-10: Extraction → Validation → Policy Lookup →         │
│  Coverage → Triage → Routing → Acknowledgment → System Updates →    │
│  Exception Handling → QA Monitoring                                 │
│                                                                      │
│  Processing Time:                                                    │
│  ├─ Autonomous claims: <2 min [A8, A23, A26, A30, A33, A36, A37]   │
│  └─ Escalated claims: <20 min (includes human review [A31])        │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        SYSTEM OUTPUTS                                │
├─────────────────────────────────────────────────────────────────────┤
│ 1. Claimant Acknowledgment (300/day, <2 hours [A14])               │
│    ├─ Email (HTML, via SMTP/SendGrid)                              │
│    └─ SMS (plain text, via Twilio, optional)                       │
│                                                                      │
│ 2. Claim Records (300/day, in CRM via REST API)                    │
│    └─ Includes: claim details, coverage, adjuster, status          │
│                                                                      │
│ 3. Documents (1,200/day, in DMS via REST API)                      │
│    ├─ FNOL Report (PDF/original format)                            │
│    ├─ Extracted Data (JSON)                                        │
│    ├─ Policy Details (JSON)                                        │
│    └─ Acknowledgment (PDF)                                         │
│                                                                      │
│ 4. Escalation Tickets (45/day, 15% of claims [A5])                 │
│    └─ In CRM + Email/Slack notifications to escalation target      │
│                                                                      │
│ 5. Adjuster Notifications (255/day, 85% of claims [A10])           │
│    └─ Email/Slack/CRM notification with claim details              │
│                                                                      │
│ 6. Quality Metrics (15,000 data points/day, real-time)             │
│    └─ To monitoring dashboard (Grafana/Datadog)                    │
│                                                                      │
│ 7. Daily QA Report (1/day, generated at 6am)                       │
│    └─ PDF report to QA team + operations manager                   │
│                                                                      │
│ 8. Error Logs (30/day, for model retraining [U2])                  │
│    └─ JSONL to ML training pipeline                                │
└─────────────────────────────────────────────────────────────────────┘
```

**Assumption References**: *[A5, A6, A7, A8, A9, A10, A14, A15, A19, A20, A21, A22, A23, A24, A26, A27, A28, A29, A30, A31, A32, A33, A34, A36, A37, A38, A39, U2, U5, U11]*

---

## 5. Integration Points

### Integration 1: Legacy Policy Administration System

**System Name**: Legacy Policy Administration System (PolicyAdmin)

**Purpose**: Retrieve policy details (coverage types, limits, exclusions, effective dates) for coverage determination

**Integration Type**: SOAP Web Service

**Authentication**: SAML 2.0 with service account credentials *[U5: actual auth method unknown, assume SAML]*

**Endpoints**:

**Operation 1: Lookup Policy by Policy Number**
```
Method: POST
Endpoint: https://policyadmin.example.com/soap/PolicyService/v2
SOAP Action: http://example.com/PolicyService/LookupPolicy
Request Schema:
  <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
                    xmlns:pol="http://example.com/policy/v2">
    <soapenv:Header>
      <wsse:Security>
        <saml:Assertion>...</saml:Assertion>
      </wsse:Security>
    </soapenv:Header>
    <soapenv:Body>
      <pol:PolicyLookupRequest>
        <pol:PolicyNumber>AA12345678</pol:PolicyNumber>
        <pol:EffectiveDate>2024-01-15</pol:EffectiveDate>
      </pol:PolicyLookupRequest>
    </soapenv:Body>
  </soapenv:Envelope>

Response Schema (Success):
  <soapenv:Envelope>
    <soapenv:Body>
      <pol:PolicyLookupResponse>
        <pol:PolicyDetails>
          <pol:PolicyID>uuid-here</pol:PolicyID>
          <pol:PolicyNumber>AA12345678</pol:PolicyNumber>
          <pol:PolicyholderName>John Doe</pol:PolicyholderName>
          <pol:EffectiveDate>2024-01-01</pol:EffectiveDate>
          <pol:ExpirationDate>2024-12-31</pol:ExpirationDate>
          <pol:Status>ACTIVE</pol:Status>
        </pol:PolicyDetails>
        <pol:CoverageList>
          <pol:Coverage>
            <pol:Type>AUTO_COLLISION</pol:Type>
            <pol:Limit>50000.00</pol:Limit>
            <pol:Deductible>500.00</pol:Deductible>
          </pol:Coverage>
          <pol:Coverage>
            <pol:Type>AUTO_COMPREHENSIVE</pol:Type>
            <pol:Limit>50000.00</pol:Limit>
            <pol:Deductible>250.00</pol:Deductible>
          </pol:Coverage>
        </pol:CoverageList>
        <pol:ExclusionList>
          <pol:Exclusion>Intentional damage</pol:Exclusion>
          <pol:Exclusion>Pre-existing damage</pol:Exclusion>
        </pol:ExclusionList>
      </pol:PolicyLookupResponse>
    </soapenv:Body>
  </soapenv:Envelope>

Response Schema (Error - Policy Not Found):
  <soapenv:Envelope>
    <soapenv:Body>
      <soapenv:Fault>
        <faultcode>pol:PolicyNotFound</faultcode>
        <faultstring>Policy AA12345678 not found in system</faultstring>
      </soapenv:Fault>
    </soapenv:Body>
  </soapenv:Envelope>

Response Schema (Error - System Error):
  <soapenv:Envelope>
    <soapenv:Body>
      <soapenv:Fault>
        <faultcode>soapenv:Server</faultcode>
        <faultstring>Internal system error</faultstring>
      </soapenv:Fault>
    </soapenv:Body>
  </soapenv:Envelope>

Timeout: 30 seconds [A26: assumes 10-30 sec latency, may be higher per U5]
Retry Logic: 3 attempts with exponential backoff (1s, 2s, 4s)
Fallback: Escalate to human if all retries fail (PENDING_SYSTEM_ISSUE state)
Error Codes:
  - pol:PolicyNotFound (404 equivalent): Policy does not exist → escalate to human
  - soapenv:Server (500 equivalent): System error → retry, then escalate
  - Timeout: No response within 30s → retry, then escalate
```

**Rate Limits**: Unknown *[U5]*, assume 10 requests/second max (conservative estimate)

**Data Mapping**:
```
PolicyLookupResponse → Policy entity:
  PolicyDetails.PolicyID → policy_id
  PolicyDetails.PolicyNumber → policy_number
  PolicyDetails.PolicyholderName → policyholder_name
  PolicyDetails.EffectiveDate → effective_date
  PolicyDetails.ExpirationDate → expiration_date
  PolicyDetails.Status → status (map: ACTIVE, LAPSED, CANCELLED)
  CoverageList.Coverage[] → coverage_types, coverage_limits, deductibles
  ExclusionList.Exclusion[] → exclusions
  has_complex_exclusions = true IF exclusions contain keywords: "act of God", "pre-existing", "intentional", "war", "nuclear"
```

**Assumption/Unknown References**: *[A26, U5]*

---

### Integration 2: CRM System

**System Name**: Customer Relationship Management System (CRM)

**Purpose**: Create claim records, link to policy and adjuster, trigger adjuster notifications

**Integration Type**: REST API

**Authentication**: OAuth 2.0 (client credentials flow) *[U5: assume OAuth, actual method unknown]*

**Endpoints**:

**Operation 1: Create Claim Record**
```
Method: POST
Endpoint: https://crm.example.com/api/v1/claims
Headers:
  Authorization: Bearer {access_token}
  Content-Type: application/json
Request Body:
  {
    "claim_id": "uuid-here",
    "policy_id": "uuid-here",
    "policy_number": "AA12345678",
    "claimant_name": "John Doe",
    "claimant_email": "john.doe@example.com",
    "claimant_phone": "+12025551234",
    "loss_date": "2024-01-15",
    "loss_description": "Rear-end collision at intersection...",
    "claim_type": "AUTO_COLLISION",
    "claim_value_usd": 5000.00,
    "coverage_determination": "COVERED",
    "assigned_adjuster_id": "uuid-here",
    "status": "OPEN",
    "created_at": "2024-01-16T10:30:00Z",
    "acknowledged_at": "2024-01-16T10:32:00Z"
  }

Response (Success - 201 Created):
  {
    "crm_claim_id": "CRM-12345",
    "claim_id": "uuid-here",
    "status": "OPEN",
    "created_at": "2024-01-16T10:30:05Z"
  }

Response (Error - 400 Bad Request):
  {
    "error": "VALIDATION_ERROR",
    "message": "Missing required field: policy_id",
    "field": "policy_id"
  }

Response (Error - 500 Internal Server Error):
  {
    "error": "INTERNAL_ERROR",
    "message": "Database connection failed"
  }

Timeout: 10 seconds
Retry Logic: 3 attempts with exponential backoff (1s, 2s, 4s) for 500/503 errors only
Fallback: Escalate to human + IT support if all retries fail
Error Codes:
  - 400: Validation error (missing field, invalid format) → log error, escalate to developer
  - 401: Authentication error → refresh token, retry
  - 500: System error → retry, then escalate
  - 503: Service unavailable → retry, then escalate
```

**Operation 2: Create Escalation Ticket**
```
Method: POST
Endpoint: https://crm.example.com/api/v1/escalations
Headers:
  Authorization: Bearer {access_token}
  Content-Type: application/json
Request Body:
  {
    "ticket_id": "uuid-here",
    "claim_id": "uuid-here",
    "trigger_condition": "claim_value > $100K [A21]",
    "escalation_target": "SENIOR_ADJUSTER",
    "ai_recommendation": "Assign to Senior Adjuster Jane Smith based on auto collision specialization",
    "supporting_evidence": {
      "claim_value_usd": 150000.00,
      "claim_type": "AUTO_COLLISION",
      "loss_description": "Total loss, vehicle destroyed..."
    },
    "confidence_score": 0.92,
    "response_time_sla": 60,
    "created_at": "2024-01-16T10:30:00Z"
  }

Response (Success - 201 Created):
  {
    "ticket_id": "uuid-here",
    "crm_ticket_id": "ESC-67890",
    "status": "OPEN",
    "assigned_to": "jane.smith@example.com",
    "created_at": "2024-01-16T10:30:05Z"
  }

Timeout: 10 seconds
Retry Logic: Same as Create Claim
```

**Rate Limits**: 100 requests/minute *[U5: assume standard rate limit]*

**Data Mapping**:
```
Claim entity → CRM CreateClaimRequest:
  claim_id → claim_id
  policy_number → policy_number (for linking)
  claimant_name, claimant_contact → claimant fields
  loss_date, loss_description, claim_type, claim_value_usd → claim details
  coverage_determination → coverage_determination
  assigned_adjuster_id → assigned_adjuster_id
  state → status (map: COMPLETED → OPEN, PENDING_REVIEW → PENDING, etc.)
```

**Assumption/Unknown References**: *[A37, U5]*

---

### Integration 3: Document Management System

**System Name**: Document Management System (DMS)

**Purpose**: Store claim documents (original report, extracted data, policy details, acknowledgment)

**Integration Type**: REST API (multipart/form-data for file uploads)

**Authentication**: API Key (X-API-Key header) *[U5: assume API key, actual method unknown]*

**Endpoints**:

**Operation 1: Upload Document**
```
Method: POST
Endpoint: https://dms.example.com/api/v1/documents
Headers:
  X-API-Key: {api_key}
  Content-Type: multipart/form-data
Request Body (multipart):
  - file: [binary file data]
  - metadata: {
      "claim_id": "uuid-here",
      "document_type": "FNOL_REPORT",
      "file_name": "claim_report_20240116.pdf",
      "uploaded_by": "fnol_agent",
      "uploaded_at": "2024-01-16T10:30:00Z"
    }

Response (Success - 201 Created):
  {
    "document_id": "DOC-12345",
    "claim_id": "uuid-here",
    "file_name": "claim_report_20240116.pdf",
    "file_size_bytes": 245678,
    "uploaded_at": "2024-01-16T10:30:05Z",
    "download_url": "https://dms.example.com/documents/DOC-12345"
  }

Response (Error - 413 Payload Too Large):
  {
    "error": "FILE_TOO_LARGE",
    "message": "File size exceeds 10MB limit",
    "max_size_bytes": 10485760
  }

Response (Error - 500 Internal Server Error):
  {
    "error": "STORAGE_ERROR",
    "message": "Failed to write file to storage"
  }

Timeout: 30 seconds (for large files)
Retry Logic: 3 attempts for 500/503 errors, no retry for 413 (file too large)
Fallback: Store file locally, escalate to IT support for manual upload
Error Codes:
  - 400: Invalid metadata → log error, escalate to developer
  - 401: Authentication error → check API key, escalate
  - 413: File too large → compress file, retry, or escalate
  - 500: Storage error → retry, then escalate
```

**Rate Limits**: 50 uploads/minute *[U5: assume standard rate limit]*

**Data Mapping**:
```
Document types:
  - FNOL_REPORT: Original claim report (email, transcript, form)
  - EXTRACTED_DATA: JSON summary of extracted fields
  - POLICY_DETAILS: Policy information from legacy system
  - ACKNOWLEDGMENT: Claimant acknowledgment message (PDF)
  - ESCALATION_EVIDENCE: Supporting documents for escalated claims
```

**Assumption/Unknown References**: *[A37, U5]*

---

## 6. What the Agent Should NOT Do

**Explicit Prohibitions**:

1. **Agent must NOT approve coverage for claims >$100K without human review** *[A21]*
   - Rationale: High-value claims have higher error cost ($2,000+ *[A27]*), require senior adjuster oversight
   - Enforcement: Hard-coded check in coverage determination logic (Component 4)

2. **Agent must NOT override fraud indicators without human investigation** *[A29]*
   - Rationale: Fraud indicators (≥3 flags) require specialist investigation, AI cannot assess intent
   - Enforcement: Automatic escalation to fraud investigator if fraud_indicators ≥3

3. **Agent must NOT modify policy data in legacy system (read-only access)** 
   - Rationale: Policy data is authoritative, modifications require underwriting approval
   - Enforcement: API credentials have read-only permissions, no write endpoints exposed

4. **Agent must NOT proceed with claim if policy status ≠ ACTIVE**
   - Rationale: Lapsed or cancelled policies have no coverage, requires human investigation (grace period? reinstatement?)
   - Enforcement: Hard-coded check in policy lookup logic (Component 3)

5. **Agent must NOT route claims to unavailable adjusters (OUT_OF_OFFICE, at max_workload)**
   - Rationale: Unavailable adjusters cannot handle claims, causes delays and SLA breaches
   - Enforcement: Adjuster filtering logic in routing (Component 6)

6. **Agent must NOT send acknowledgment if SLA already breached (>2 hours)**
   - Rationale: Breached SLA requires apology message, not standard acknowledgment
   - Enforcement: SLA check in acknowledgment logic (Component 7), use apology template if breached

7. **Agent must NOT make coverage determination if AI confidence <85%** *[A20]*
   - Rationale: Low confidence indicates ambiguity, requires human judgment to avoid costly errors
   - Enforcement: Confidence threshold check in coverage determination logic (Component 4)

8. **Agent must NOT ignore validation errors (proceed with invalid data)**
   - Rationale: Invalid data causes downstream failures (policy lookup fails, routing fails)
   - Enforcement: Validation logic (Component 2) blocks progression if any rule fails

9. **Agent must NOT retry indefinitely on system failures (infinite loops)**
   - Rationale: System downtime requires human + IT intervention, retries waste resources
   - Enforcement: Max 3 retry attempts with exponential backoff, then escalate

10. **Agent must NOT process claims without required fields (policy_number, claimant_name, loss_date)**
    - Rationale: Required fields are critical for coverage determination and routing
    - Enforcement: Validation logic (Component 2) escalates if required fields missing

---

## 7. Handling Ambiguity and Escalation

**Escalation Triggers** (consolidated):

| Trigger Condition | Threshold | Escalation Target | Response Time SLA | Assumption Reference |
|-------------------|-----------|-------------------|-------------------|---------------------|
| AI confidence below threshold | <85% *[A20]* | Claims Specialist | 30 min | A20 |
| Claim value exceeds threshold | >$100K *[A21]* | Senior Adjuster | 60 min | A21, U1 |
| Fraud indicators detected | ≥3 flags *[A29]* | Fraud Investigator | 120 min | A29 |
| Policy lookup failure | 3 failed retries | Claims Specialist | 15 min | A26, U5 |
| Policy not found (404) | N/A | Claims Specialist | 15 min | U5 |
| Policy status ≠ ACTIVE | N/A | Claims Specialist | 30 min | — |
| Coverage ambiguity detected | Complex exclusions | Claims Manager | 60 min | A27, U1 |
| Extraction confidence low | <90% on critical fields *[A24]* | Claims Specialist | 20 min | A24 |
| Validation failure | Any rule fails | Claims Specialist | 20 min | A25 |
| Routing confidence low | <85% *[A20]* | Claims Specialist | 30 min | A20 |
| No available adjusters | All at capacity | Operations Manager | 15 min | — |
| System integration failure | All retries exhausted | IT Support + Specialist | 10 min | U5 |
| SLA breach | >2 hours since receipt | Operations Manager | Immediate | A14 |
| Document quality low | OCR <70% | Claims Specialist | 20 min | — |
| Novel claim type | Not in training data | Claims Manager | 60 min | U2 |

**Escalation Workflow**:

1. **Agent detects trigger condition**:
   - Check occurs at end of each workflow step (Components 1-8)
   - Trigger conditions are evaluated using concrete thresholds (see table above)

2. **Agent creates EscalationTicket**:
   - `ticket_id`: UUID (system-generated)
   - `claim_id`: Link to Claim entity
   - `trigger_condition`: String describing specific threshold violated (e.g., "claim_value = $150K > $100K [A21]")
   - `escalation_target`: Enum (CLAIMS_SPECIALIST, SENIOR_ADJUSTER, FRAUD_INVESTIGATOR, CLAIMS_MANAGER, IT_SUPPORT, OPERATIONS_MANAGER)
   - `ai_recommendation`: String (if confidence >50%, agent provides suggested action)
   - `supporting_evidence`: JSON object with relevant data:
     - Extracted claim fields
     - Policy excerpt (if coverage ambiguity)
     - Fraud indicators (if fraud detected)
     - Error logs (if system failure)
     - Confidence scores (if low confidence)
   - `confidence_score`: Float (AI's confidence in recommendation, if applicable)
   - `response_time_sla`: Integer (minutes, from table above)

3. **Agent notifies escalation target**:
   - Email to escalation target's address (from Adjuster or user directory)
   - Slack message (if integration available)
   - SMS (for urgent escalations: SLA breach, system failure)
   - Notification includes:
     - Claim ID and summary (claimant name, claim type, value)
     - Trigger condition (why escalated)
     - AI recommendation (if available)
     - Link to claim details in CRM
     - Response time SLA (deadline for human action)

4. **Agent pauses claim processing**:
   - Set `claim.state = PENDING_REVIEW` (for business logic escalations) or `PENDING_SYSTEM_ISSUE` (for technical failures)
   - Set `claim.escalation_reason` = trigger_condition
   - Stop workflow progression (do not proceed to next step)
   - Log escalation event with timestamp

5. **Human reviews and takes action**:
   - Human accesses claim via CRM (link in notification)
   - Human reviews AI recommendation and supporting evidence
   - Human makes decision:
     - **Approve**: Proceed with AI recommendation (e.g., "Yes, route to this adjuster")
     - **Modify**: Change AI recommendation (e.g., "Route to different adjuster")
     - **Reject**: Deny claim or coverage (e.g., "Policy lapsed, no coverage")
     - **Request More Info**: Contact claimant for clarification (e.g., "Need photos of damage")
   - Human enters decision in CRM (updates EscalationTicket)

6. **Agent resumes processing**:
   - Agent polls EscalationTicket for human decision (every 30 seconds)
   - When `ticket.human_decision` is populated:
     - Parse decision (approve/modify/reject/request_info)
     - Update claim based on decision:
       - Approve: Proceed to next workflow step with AI recommendation
       - Modify: Update claim fields per human input, proceed to next step
       - Reject: Set claim.state = COMPLETED, coverage_determination = NOT_COVERED
       - Request More Info: Set claim.state = PENDING_CLAIMANT_RESPONSE, notify claimant
     - Set `ticket.resolved_at` = current_timestamp
     - Log resolution event

**Ambiguity Detection**:

Agent recognizes ambiguous situations through:

1. **Low AI Confidence** (<85% *[A20]*):
   - Signal: Model outputs confidence score <0.85 for coverage determination, routing, or triage
   - Interpretation: Model is uncertain, likely due to ambiguous policy language, novel claim type, or insufficient training data *[U2]*
   - Action: Escalate with AI recommendation (if confidence >50%) or without recommendation (if confidence <50%)

2. **Complex Policy Exclusions**:
   - Signal: `policy.has_complex_exclusions = true` (keywords: "act of God", "pre-existing", "intentional", "war", "nuclear")
   - Interpretation: Exclusion clauses require legal interpretation, AI cannot reliably determine applicability
   - Action: Escalate to claims manager with policy excerpt and claim description

3. **Fraud Indicators**:
   - Signal: `fraud_indicators.length ≥3` *[A29]*
   - Interpretation: Multiple red flags suggest potential fraud, requires specialist investigation
   - Action: Escalate to fraud investigator with list of indicators and supporting evidence

4. **Novel Claim Type**:
   - Signal: Claim type not well-represented in training data *[U2]* (detected by model's confidence on claim_type classification)
   - Interpretation: AI has not seen enough examples of this claim type to make reliable decisions
   - Action: Escalate to claims manager for manual processing, log claim for future model training

5. **Edge Cases in Data**:
   - Signal: Extracted data has unusual values (e.g., loss_date = 10 years ago, claim_value = $0)
   - Interpretation: Data may be incorrect or claim may be unusual
   - Action: Escalate to specialist for validation

**When to Ask vs When to Decide** (see Section 7 for detailed framework)

---

## 8. When to Ask vs When to Decide

**Agent Decides Autonomously** (no human in loop):

Scenarios where agent makes final decision and proceeds without human review:

1. **Data Validation** (Component 2):
   - IF all validation rules pass (policy_number format valid, required fields present, dates in range)
   - THEN proceed to policy lookup
   - Rationale: Validation is deterministic, zero ambiguity *[A25]*

2. **Policy Lookup** (Component 3):
   - IF policy found (200 response) AND policy.status = ACTIVE AND loss_date within policy period
   - THEN proceed to coverage determination
   - Rationale: Lookup is deterministic API call, no judgment required *[A26]*

3. **Claimant Acknowledgment** (Component 7):
   - IF claim successfully routed AND no special communication preferences *[U11]*
   - THEN generate and send acknowledgment autonomously
   - Rationale: Acknowledgment is templated, low error cost ($5 *[A35]*), high volume (300/day) *[A36]*

4. **System Updates** (Component 8):
   - IF claim acknowledged AND CRM/DMS APIs available
   - THEN create records and upload documents autonomously
   - Rationale: System updates are deterministic API calls, no judgment required *[A37]*

5. **Coverage Determination** (Component 4) - for straightforward claims:
   - IF coverage_confidence ≥85% *[A20]* AND claim_value <$100K *[A21]* AND fraud_indicators <3 *[A29]* AND policy.has_complex_exclusions = false
   - THEN set coverage_determination autonomously
   - Rationale: Straightforward claims (85% *[A10]*) are highly codifiable, low error risk

6. **Adjuster Routing** (Component 6) - for straightforward claims:
   - IF routing_confidence ≥85% *[A20]* AND claim_value <$100K *[A21]* AND adjuster available
   - THEN assign adjuster autonomously
   - Rationale: Routing is rule-based + ML, 97% accuracy target *[A15]*, low error cost (45 min rework *[A3]*)

**Agent Asks for Approval** (human reviews before execution):

Scenarios where agent proposes decision, waits for human approval before proceeding:

1. **Data Extraction** (Component 1) - for low-confidence extractions:
   - IF extraction_confidence <90% on critical fields *[A24]*
   - THEN escalate with extracted data, human validates/corrects, agent proceeds after approval
   - Rationale: Low confidence indicates OCR issues or ambiguous text, human validation prevents downstream errors *[A22]*

2. **Coverage Determination** (Component 4) - for ambiguous claims:
   - IF coverage_confidence <85% *[A20]* OR policy.has_complex_exclusions = true OR fraud_indicators ≥3 *[A29]*
   - THEN escalate with AI recommendation (COVERED/NOT_COVERED + rationale), human reviews and approves/modifies
   - Rationale: Ambiguous claims (15% *[A5]*) have high error cost ($2,000 *[A27]*), require human judgment

3. **Severity Triage** (Component 5) - for high-value/complex claims:
   - IF claim_value >$100K *[A21]* OR severity_score >60
   - THEN escalate with triage report, human reviews and confirms oversight level
   - Rationale: High-value claims require senior adjuster, human confirms appropriate oversight *[A31]*

4. **Adjuster Routing** (Component 6) - for high-value claims:
   - IF claim_value >$100K *[A21]* OR routing_confidence <85% *[A20]*
   - THEN escalate with top 3 adjuster recommendations, human selects and approves
   - Rationale: High-value claims require senior adjuster, human ensures correct assignment

5. **Claimant Acknowledgment** (Component 7) - for sensitive claims:
   - IF claim involves death, severe injury, or special communication needs *[U11]*
   - THEN escalate with draft acknowledgment, human reviews tone/content and approves
   - Rationale: Sensitive claims require empathy and careful communication, AI may lack appropriate tone

**Agent Provides Recommendation** (human makes decision):

Scenarios where agent provides data/recommendation but human makes final decision:

1. **Exception Handling** (Component 9) - all exceptions:
   - Agent detects exception (missing data, system error, coverage dispute, etc.)
   - Agent provides context, possible causes, and suggested actions
   - Human investigates and decides resolution (retry, manual processing, escalate further)
   - Rationale: Exceptions are non-standard, require problem-solving and judgment *[A38]*

2. **Policy Lookup Failure** (Component 3):
   - IF policy not found (404) after retries
   - THEN agent provides possible reasons (typo in policy number, lapsed policy, system issue)
   - Human investigates (contact claimant, check alternative systems, confirm lapse)
   - Rationale: Policy not found requires investigation, AI cannot determine root cause

3. **Coverage Disputes**:
   - IF adjuster disputes AI's coverage determination
   - THEN agent provides original decision rationale, policy excerpt, and claim details
   - Human (claims manager) reviews and makes final determination
   - Rationale: Disputes require senior judgment, AI provides supporting evidence but does not override human

4. **Fraud Investigation**:
   - IF fraud_indicators ≥3 *[A29]*
   - THEN agent provides list of indicators, supporting evidence, and claim details
   - Human (fraud investigator) conducts investigation and decides action (approve, deny, request more info)
   - Rationale: Fraud requires specialist investigation, AI detects patterns but cannot assess intent

5. **Novel Claim Types**:
   - IF claim type not in training data *[U2]*
   - THEN agent provides claim details and notes "novel claim type"
   - Human (claims manager) processes manually and provides feedback for future training
   - Rationale: Novel claims require human expertise, AI lacks training data to make reliable decisions

**Decision Framework** (consolidated logic):

```python
def determine_delegation_mode(claim, policy, ai_confidence):
    # Check for hard stops (always escalate)
    if claim.fraud_indicators >= 3:  # [A29]
        return "HUMAN_DECIDES", "FRAUD_INVESTIGATOR", "Fraud indicators ≥3"
    
    if claim.claim_value_usd > 100000:  # [A21]
        return "HUMAN_APPROVES", "SENIOR_ADJUSTER", "Claim value >$100K"
    
    if policy.has_complex_exclusions:
        return "HUMAN_APPROVES", "CLAIMS_MANAGER", "Complex policy exclusions"
    
    # Check AI confidence
    if ai_confidence < 0.85:  # [A20]
        return "HUMAN_APPROVES", "CLAIMS_SPECIALIST", f"AI confidence {ai_confidence} <85%"
    
    # Check for special circumstances
    if claim.involves_death or claim.involves_severe_injury:
        return "HUMAN_APPROVES", "CLAIMS_MANAGER", "Sensitive circumstances"
    
    # Default: agent decides autonomously
    return "AGENT_DECIDES", None, "Straightforward claim, high confidence"

# Usage in workflow:
delegation_mode, escalation_target, reason = determine_delegation_mode(claim, policy, coverage_confidence)

if delegation_mode == "AGENT_DECIDES":
    # Proceed autonomously
    claim.coverage_determination = ai_determination
    claim.state = "COVERAGE_DETERMINED"
    proceed_to_next_step()

elif delegation_mode == "HUMAN_APPROVES":
    # Escalate for approval
    create_escalation_ticket(
        claim_id=claim.claim_id,
        trigger_condition=reason,
        escalation_target=escalation_target,
        ai_recommendation=ai_determination,
        supporting_evidence={
            "policy_excerpt": policy.exclusions,
            "claim_description": claim.loss_description,
            "confidence_score": coverage_confidence
        }
    )
    claim.state = "PENDING_REVIEW"
    wait_for_human_decision()

elif delegation_mode == "HUMAN_DECIDES":
    # Escalate for human decision
    create_escalation_ticket(
        claim_id=claim.claim_id,
        trigger_condition=reason,
        escalation_target=escalation_target,
        ai_recommendation=None,  # No recommendation, human decides
        supporting_evidence={
            "fraud_indicators": claim.fraud_indicators,
            "claim_details": claim.to_dict()
        }
    )
    claim.state = "PENDING_REVIEW"
    wait_for_human_decision()
```

**Assumption References**: *[A5, A10, A20, A21, A22, A24, A25, A26, A27, A29, A31, A35, A36, A37, A38, U2, U11]*

---

## 9. Validation Logic

### 9.1 Happy Path Validation

**Scenario: Straightforward Auto Collision Claim**

**Characteristics**:
- Claim type: AUTO_COLLISION
- Claim value: $5,000 (minor damage)
- Document quality: Clean email, OCR confidence >95%
- Policy: Active, standard coverage, no complex exclusions
- No fraud indicators
- Claimant: Standard communication preferences (email)

**Expected Behavior**:

1. **Data Extraction** (Component 1):
   - Time: <15 seconds *[A23]*
   - Extract fields: policy_number=AA12345678, claimant_name="John Doe", loss_date=2024-01-15, claim_type=AUTO_COLLISION, claim_value_usd=5000
   - Confidence scores: policy_number=0.98, claimant_name=0.96, loss_date=0.99, overall=0.96 (>90% *[A24]*)
   - State transition: RECEIVED → EXTRACTING → EXTRACTED

2. **Data Validation** (Component 2):
   - Time: <2 seconds *[A25]*
   - Validate policy_number format: PASS (matches /^[A-Z]{2}\d{8}$/)
   - Validate loss_date: PASS (valid date, not in future)
   - Validate required fields: PASS (all present)
   - State transition: EXTRACTED → VALIDATING → VALIDATED

3. **Policy Lookup** (Component 3):
   - Time: <10 seconds *[A26]*
   - SOAP call to PolicyAdmin: SUCCESS (200)
   - Policy found: policy_id=uuid, status=ACTIVE, coverage_types=[AUTO_COLLISION, AUTO_COMPREHENSIVE], limit=$50K
   - Validate loss_date in policy period: PASS (2024-01-15 in [2024-01-01, 2024-12-31])
   - State transition: VALIDATED → POLICY_LOOKUP → POLICY_FOUND

4. **Coverage Determination** (Component 4):
   - Time: <8 seconds *[A28]*
   - Check coverage: claim_type=AUTO_COLLISION IN policy.coverage_types → COVERED
   - Check exclusions: No exclusion keywords in loss_description
   - Check policy complexity: has_complex_exclusions=false
   - Coverage confidence: 0.94 (>85% *[A20]*)
   - Decision: coverage_determination=COVERED (autonomous)
   - State transition: POLICY_FOUND → COVERAGE_DETERMINING → COVERAGE_DETERMINED

5. **Severity Triage** (Component 5):
   - Time: <10 seconds *[A30]*
   - Calculate severity score: claim_value=10 points (5K on 0-30 scale), fraud=0, complexity=0, confidence=0 → total=10 (ROUTINE)
   - Oversight requirement: severity=ROUTINE, value<100K, fraud<3, confidence>85% → NO HUMAN OVERSIGHT
   - State transition: COVERAGE_DETERMINED → TRIAGING → TRIAGED

6. **Adjuster Routing** (Component 6):
   - Time: <3 seconds *[A33]*
   - Filter adjusters: specialization=AUTO, geography=REGION_A, available=true, workload<max
   - Select adjuster: adjuster_id=uuid-adjuster-1 (lowest workload=5, specialization match=100%)
   - Routing confidence: 0.91 (>85% *[A20]*)
   - Decision: Assign to adjuster_id=uuid-adjuster-1 (autonomous)
   - State transition: TRIAGED → ROUTING → ROUTED

7. **Claimant Acknowledgment** (Component 7):
   - Time: <5 seconds *[A36]*
   - Generate acknowledgment: "Dear John Doe, we received your claim (#uuid) regarding AUTO_COLLISION on 2024-01-15. Your adjuster is Jane Smith..."
   - Send email to john.doe@example.com: SUCCESS
   - Log acknowledged_at: 2024-01-16T10:32:00Z (within 2-hour SLA *[A14]*)
   - State transition: ROUTED → ACKNOWLEDGING → ACKNOWLEDGED

8. **System Updates** (Component 8):
   - Time: <8 seconds *[A37]*
   - Create CRM record: SUCCESS (201, crm_claim_id=CRM-12345)
   - Upload documents to DMS: SUCCESS (4 documents uploaded)
   - State transition: ACKNOWLEDGED → COMPLETED

**Total Processing Time**: 15+2+10+8+10+3+5+8 = **61 seconds** (<2 minutes, well within 2-hour SLA *[A14]*)

**Validation Checks**:
- [ ] Claim state transitions: RECEIVED → EXTRACTING → EXTRACTED → VALIDATING → VALIDATED → POLICY_LOOKUP → POLICY_FOUND → COVERAGE_DETERMINING → COVERAGE_DETERMINED → TRIAGING → TRIAGED → ROUTING → ROUTED → ACKNOWLEDGING → ACKNOWLEDGED → COMPLETED
- [ ] All timestamps logged correctly (created_at, acknowledged_at, each state transition)
- [ ] Claimant receives acknowledgment email within 2 hours of claim receipt *[A14]*
- [ ] Email contains correct claim number (uuid), adjuster name (Jane Smith), next steps
- [ ] CRM updated with claim details (claim_id, policy_number, claimant_name, assigned_adjuster_id, status=OPEN)
- [ ] Documents uploaded to DMS (FNOL_REPORT, EXTRACTED_DATA, POLICY_DETAILS, ACKNOWLEDGMENT)
- [ ] No escalation tickets created (claim processed autonomously)
- [ ] No human intervention required (0 minutes human time *[A8]*)
- [ ] SLA compliance: acknowledged_at ≤ sla_deadline (created_at + 2 hours)
- [ ] Routing accuracy: Adjuster does not click "Not My Claim" within 24 hours
- [ ] Cost per claim: ~$0.15 AI processing *[A7]* (no human time)

---

### 9.2 Edge Case Validation

**Edge Case 1: High-Value Claim ($150K)**

**Trigger Condition**: `claim_value_usd` = $150,000 > $100K *[A21]*

**Expected Agent Behavior**:
1. Data extraction, validation, policy lookup proceed normally (Components 1-3)
2. Coverage determination: AI determines COVERED with confidence=0.89
3. **Escalation triggered** at severity triage (Component 5):
   - Severity score: claim_value=30 (max), fraud=0, complexity=0, confidence=0 → total=30 (MODERATE, but value>100K triggers escalation)
   - Create EscalationTicket:
     - trigger_condition: "claim_value = $150,000 > $100K [A21]"
     - escalation_target: SENIOR_ADJUSTER
     - ai_recommendation: "Claim is covered under AUTO_COLLISION policy. Recommend assigning to Senior Adjuster Jane Smith (auto collision specialist, 15 years experience)."
     - supporting_evidence: {claim_value: 150000, coverage_determination: "COVERED", confidence: 0.89}
     - response_time_sla: 60 minutes
   - Notify senior adjuster via email + Slack
   - Set claim.state = PENDING_REVIEW
4. Wait for human decision
5. **Human reviews** (within 60 min):
   - Reviews AI recommendation
   - Confirms coverage determination
   - Approves routing to Senior Adjuster Jane Smith
6. **Agent resumes**:
   - Assign claim to Jane Smith
   - Generate acknowledgment (mentions senior adjuster)
   - Complete system updates
   - Set claim.state = COMPLETED

**Validation Checks**:
- [ ] Escalation ticket created with correct trigger: "claim_value > $100K [A21]"
- [ ] Senior adjuster (Jane Smith) notified within 5 minutes of escalation
- [ ] Claim state: PENDING_REVIEW (paused at triage step)
- [ ] Agent provides recommendation: "Assign to Senior Adjuster Jane Smith" with rationale
- [ ] Human decision logged in EscalationTicket.human_decision
- [ ] Claim resumes processing after human approval
- [ ] Total processing time: ~61 sec (agent) + 30-60 min (human review) = **~60 min total**
- [ ] Cost per claim: $0.15 (AI) + 12 min × $0.75/min *[A8, A31]* = **$9.15** (within budget for high-value claims)

---

**Edge Case 2: Low-Confidence Data Extraction (OCR Quality 65%)**

**Trigger Condition**: `extraction_confidence.overall` = 0.65 < 90% *[A24]*

**Expected Agent Behavior**:
1. Data extraction (Component 1):
   - Document is low-quality scan (handwritten notes, coffee stain)
   - OCR confidence: policy_number=0.65, claimant_name=0.80, loss_date=0.90
   - Overall confidence: MIN(0.65, 0.80, 0.90) = 0.65 (<90% *[A24]*)
   - **Escalation triggered**:
     - Create EscalationTicket:
       - trigger_condition: "extraction_confidence.policy_number = 0.65 < 90% [A24]"
       - escalation_target: CLAIMS_SPECIALIST
       - ai_recommendation: "Extracted policy_number=AA12345678 (low confidence). Please verify from original document."
       - supporting_evidence: {extracted_fields: {...}, confidence_scores: {...}, document_url: "..."}
       - response_time_sla: 20 minutes
     - Highlight low-confidence fields in UI (policy_number, claimant_name)
     - Set claim.state = PENDING_REVIEW
2. Wait for human validation
3. **Human reviews** (within 20 min):
   - Opens original document (scanned form)
   - Verifies policy_number: Correct (AA12345678)
   - Verifies claimant_name: Incorrect (AI extracted "John Dae", actual is "John Doe")
   - Corrects claimant_name in UI
   - Approves extraction
4. **Agent resumes**:
   - Update claim.claimant_name = "John Doe"
   - Proceed to validation (Component 2)
   - Continue workflow normally (policy lookup, coverage, routing, etc.)

**Validation Checks**:
- [ ] Escalation ticket created with trigger: "extraction_confidence <90% [A24]"
- [ ] Claims specialist notified within 5 minutes
- [ ] Low-confidence fields highlighted in UI (policy_number, claimant_name)
- [ ] Human corrects error (claimant_name)
- [ ] Agent logs correction for model retraining *[U2]*
- [ ] Claim resumes at validation step (Component 2) after correction
- [ ] Total processing time: ~15 sec (extraction) + 10 min (human validation) + 50 sec (remaining steps) = **~11 min total**
- [ ] Cost per claim: $0.15 (AI) + 10 min × $0.75/min *[A8]* = **$7.65**

---

**Edge Case 3: Policy Not Found (404)**

**Trigger Condition**: Policy lookup returns 404 (policy not found)

**Expected Agent Behavior**:
1. Data extraction, validation proceed normally (Components 1-2)
2. Policy lookup (Component 3):
   - SOAP call to PolicyAdmin with policy_number=AA12345678
   - Response: 404 (PolicyNotFound fault)
   - **Escalation triggered**:
     - Create EscalationTicket:
       - trigger_condition: "Policy lookup failed: 404 PolicyNotFound"
       - escalation_target: CLAIMS_SPECIALIST
       - ai_recommendation: "Policy AA12345678 not found in system. Possible reasons: (1) Typo in policy number (similar policy AA12345679 exists), (2) Policy lapsed, (3) System data issue. Please verify with claimant."
       - supporting_evidence: {policy_number: "AA12345678", error_code: 404, similar_policies: ["AA12345679"]}
       - response_time_sla: 15 minutes
     - Set claim.state = PENDING_REVIEW
3. Wait for human investigation
4. **Human investigates** (within 15 min):
   - Contacts claimant to verify policy number
   - Claimant confirms typo: Correct policy number is AA12345679
   - Human updates claim.policy_number = "AA12345679" in UI
   - Human clicks "Retry Policy Lookup"
5. **Agent resumes**:
   - Retry policy lookup with corrected policy number
   - Policy found: SUCCESS (200)
   - Continue workflow normally (coverage, triage, routing, etc.)

**Validation Checks**:
- [ ] Escalation ticket created with trigger: "Policy lookup failed: 404"
- [ ] Claims specialist notified within 5 minutes
- [ ] Agent provides possible reasons (typo, lapsed, system issue)
- [ ] Agent suggests similar policy numbers (AA12345679) if available
- [ ] Human corrects policy number
- [ ] Agent retries policy lookup successfully
- [ ] Claim resumes at policy lookup step (Component 3)
- [ ] Total processing time: ~25 sec (extraction+validation) + 10 sec (failed lookup) + 10 min (human investigation) + 50 sec (remaining steps) = **~11.5 min total**

---

**Edge Case 4: Fraud Indicators Detected (3 Red Flags)**

**Trigger Condition**: `fraud_indicators.length` = 3 ≥ 3 *[A29]*

**Expected Agent Behavior**:
1. Data extraction, validation, policy lookup proceed normally (Components 1-3)
2. Coverage determination (Component 4):
   - AI detects fraud indicators:
     - Policy inception: 15 days ago (recent)
     - Claim value: $48,000 (near policy limit of $50K)
     - Loss description inconsistent with damage photos (claims "minor fender bender", photos show total loss)
   - Set claim.fraud_indicators = ["recent_policy_inception", "claim_near_limit", "inconsistent_description"]
   - **Escalation triggered**:
     - Create EscalationTicket:
       - trigger_condition: "fraud_indicators = 3 ≥ 3 [A29]"
       - escalation_target: FRAUD_INVESTIGATOR
       - ai_recommendation: None (fraud requires specialist investigation, AI does not recommend coverage decision)
       - supporting_evidence: {
           fraud_indicators: ["recent_policy_inception", "claim_near_limit", "inconsistent_description"],
           policy_inception_date: "2024-01-01",
           claim_date: "2024-01-15",
           claim_value: 48000,
           policy_limit: 50000,
           loss_description: "Minor fender bender...",
           damage_photos: ["url1", "url2"]
         }
       - response_time_sla: 120 minutes
     - Set claim.state = PENDING_REVIEW
3. Wait for fraud investigation
4. **Fraud investigator reviews** (within 2 hours):
   - Reviews claim details, policy history, damage photos
   - Contacts claimant for interview
   - Requests additional documentation (police report, repair estimates)
   - Decides: Legitimate claim (claimant undersold damage severity, but photos confirm accident)
   - Approves coverage: coverage_determination = COVERED
5. **Agent resumes**:
   - Proceed to severity triage (Component 5)
   - Continue workflow normally (routing, acknowledgment, system updates)

**Validation Checks**:
- [ ] Escalation ticket created with trigger: "fraud_indicators ≥3 [A29]"
- [ ] Fraud investigator notified within 10 minutes
- [ ] Agent provides list of fraud indicators with supporting evidence
- [ ] Agent does NOT provide coverage recommendation (human decides)
- [ ] Claim state: PENDING_REVIEW (paused at coverage determination)
- [ ] Fraud investigator logs investigation notes in EscalationTicket
- [ ] Human decision: COVERED (approved after investigation)
- [ ] Claim resumes at triage step (Component 5)
- [ ] Total processing time: ~35 sec (extraction+validation+lookup) + 90 min (fraud investigation) + 40 sec (remaining steps) = **~91 min total**

---

**Edge Case 5: Coverage Ambiguity (Complex Exclusion)**

**Trigger Condition**: `policy.has_complex_exclusions` = true (policy contains "act of God" exclusion, claim is flood due to dam failure)

**Expected Agent Behavior**:
1. Data extraction, validation, policy lookup proceed normally (Components 1-3)
2. Coverage determination (Component 4):
   - AI checks coverage: claim_type=PROPERTY_FLOOD, policy.coverage_types includes FLOOD
   - AI checks exclusions: policy.exclusions includes "Excludes damage from acts of God including floods, unless caused by structural failure"
   - AI detects ambiguity: Claim is flood (excluded) BUT caused by dam failure (structural failure, possibly covered)
   - Set policy.has_complex_exclusions = true (keyword "act of God" detected)
   - Coverage confidence: 0.60 (<85% *[A20]*, ambiguous)
   - **Escalation triggered**:
     - Create EscalationTicket:
       - trigger_condition: "coverage_ambiguity_detected: complex_exclusion [A27, U1]"
       - escalation_target: CLAIMS_MANAGER
       - ai_recommendation: "Possible coverage due to dam failure (structural), but exclusion clause is ambiguous. Requires legal interpretation."
       - supporting_evidence: {
           policy_excerpt: "Section 4.2: Excludes damage from 'acts of God' including floods, unless caused by structural failure...",
           claim_description: "Home flooded due to dam failure upstream...",
           coverage_confidence: 0.60
         }
       - response_time_sla: 60 minutes
     - Set claim.state = PENDING_REVIEW
3. Wait for claims manager decision
4. **Claims manager reviews** (within 60 min):
   - Reviews policy language, claim description, legal precedents
   - Consults legal team (if needed)
   - Decides: COVERED (dam failure qualifies as structural failure, exclusion does not apply)
5. **Agent resumes**:
   - Set coverage_determination = COVERED
   - Proceed to severity triage (Component 5)
   - Continue workflow normally

**Validation Checks**:
- [ ] Escalation ticket created with trigger: "coverage_ambiguity: complex_exclusion [A27]"
- [ ] Claims manager notified within 5 minutes
- [ ] Agent provides policy excerpt and claim description
- [ ] Agent provides AI recommendation with caveat ("requires legal interpretation")
- [ ] Claim state: PENDING_REVIEW (paused at coverage determination)
- [ ] Human decision: COVERED (with rationale logged)
- [ ] Claim resumes at triage step (Component 5)
- [ ] Total processing time: ~35 sec (extraction+validation+lookup) + 45 min (manager review) + 40 sec (remaining steps) = **~46 min total**

---

### 9.3 Failure Mode Validation

**Failure Mode 1: Agent Misroutes Claim (Wrong Adjuster)**

**Detection Method**:
- Adjuster clicks "Not My Claim" button in CRM within 1 hour of assignment
- QA monitoring detects re-routing event *[A39, Component 10]*
- Real-time alert: "Routing error detected for claim_id=uuid"

**Expected Behavior**:
- [ ] Agent logs error: `routing_error: claim_id=uuid, assigned_adjuster=adjuster-1, reason=wrong_specialization, confidence=0.87`
- [ ] Agent increments daily error counter: `routing_errors_today += 1`
- [ ] Agent checks error rate: `routing_errors_today / claims_processed_today`
- [ ] IF error rate <5% *[A9: target 3%, alert at 5%]*:
   - [ ] Agent re-routes claim automatically:
     - Re-run routing logic (Component 6) excluding adjuster-1
     - IF new routing confidence ≥85% *[A20]*: Assign to new adjuster autonomously
     - ELSE: Escalate to claims specialist for manual routing
   - [ ] Agent logs re-routing event
- [ ] ELSE (error rate ≥5%):
   - [ ] Agent sends alert to QA team: "Routing error rate exceeded 5% threshold (current: X%)"
   - [ ] Agent escalates claim to claims specialist for manual routing
   - [ ] QA team investigates root cause (see below)

**Root Cause Analysis** (human-led, AI-supported):
- **Question 1**: Is this a data quality issue? (adjuster specialization data incorrect, geography data outdated)
- **Question 2**: Is this a model drift issue? (routing model trained on old data, claim patterns changed)
- **Question 3**: Is this a workload balancing issue? (adjuster marked as available but actually at capacity)
- **Question 4**: Is this a specialization mismatch? (claim type classification error → wrong adjuster pool)

**Remediation**:
- IF data quality issue: Update adjuster data in CRM, re-train routing model *[U2]*
- IF model drift: Re-train routing model with recent claims data *[U2]*
- IF workload issue: Fix workload tracking logic (sync with CRM more frequently)
- IF classification issue: Improve claim type classification model (add training examples)

**Alert Thresholds**:
- **Daily error rate >5%** *[A9: target 3%]*: Alert QA team for investigation
- **Weekly error rate >4%** (sustained): Alert operations manager, schedule model retraining
- **Individual adjuster rejection rate >20%**: Alert adjuster manager (possible training issue or data error)

**Assumption References**: *[A3, A9, A15, A39]*

---

**Failure Mode 2: Agent Incorrectly Determines Coverage (Approves Invalid Claim)**

**Detection Method**:
- Adjuster reviews claim and disputes coverage determination ("This should not be covered")
- QA audit (random sample of 5% of claims *[A39]*) catches error within 24 hours
- Post-hoc analysis: Coverage error logged in CRM

**Expected Behavior**:
- [ ] Agent logs error: `coverage_error: claim_id=uuid, agent_decision=COVERED, adjuster_decision=NOT_COVERED, reason=exclusion_missed, confidence=0.88`
- [ ] Agent flags claim for root cause analysis:
   - **Question**: Did agent miss exclusion clause in policy?
   - **Question**: Is policy data incomplete (exclusion not in legacy system)?
   - **Question**: Is this a novel case type (not in training data *[U2]*)?
- [ ] Agent calculates error cost: 
   - IF claim already paid out: error_cost = claim_value_usd (e.g., $5,000)
   - ELSE: error_cost = adjuster_time_to_correct × $45/hour *[A1]* (e.g., 1 hour = $45)
- [ ] IF error_cost >$1,000:
   - [ ] Agent escalates to claims manager for review: "High-cost coverage error detected"
   - [ ] Claims manager investigates and decides remediation (deny claim, request repayment, update policy data)
- [ ] Agent checks for error pattern:
   - IF same exclusion missed 3+ times in past week:
     - [ ] Agent alerts QA team: "Recurring coverage error: exclusion [X] missed 3+ times"
     - [ ] QA team triggers model retraining *[U2]* (add exclusion examples to training data)
- [ ] Agent logs error for model retraining (claim details, policy excerpt, correct decision)

**Root Cause Analysis**:
- **Question 1**: Did agent miss exclusion clause? (exclusion present in policy but not detected)
- **Question 2**: Is exclusion clause ambiguous? (requires legal interpretation, AI cannot reliably assess)
- **Question 3**: Is policy data incomplete? (exclusion exists but not in legacy system response)
- **Question 4**: Is this a novel case type? (claim type not well-represented in training data *[U2]*)

**Remediation**:
- IF exclusion missed: Add exclusion detection rule, retrain model with this example
- IF exclusion ambiguous: Lower confidence threshold for this exclusion type (trigger human review)
- IF policy data incomplete: Fix data sync with legacy system, backfill missing exclusions
- IF novel case type: Add to training data, flag similar future claims for human review

**Alert Thresholds**:
- **Daily coverage error rate >2%** (target 0.5% *[A43]*): Alert QA team
- **Weekly coverage error rate >1%** (sustained): Alert claims manager, schedule model retraining
- **High-cost errors (>$1,000) >5 per week**: Alert senior management, review model performance

**Assumption References**: *[A9, A27, A39, A43, U2]*

---

**Failure Mode 3: Agent Breaches SLA (Claim Not Acknowledged Within 2 Hours)**

**Detection Method**:
- Timestamp comparison: `claim.acknowledged_at > claim.sla_deadline` (created_at + 2 hours *[A14]*)
- Real-time SLA monitoring dashboard *[Component 10, A39]*
- Alert triggered immediately upon breach

**Expected Behavior**:
- [ ] Agent logs SLA breach: `sla_breach: claim_id=uuid, received_at=2024-01-16T10:00:00Z, acknowledged_at=2024-01-16T12:05:00Z, delay=5 minutes`
- [ ] Agent calculates breach penalty: $25 per breach *[A4]*
- [ ] Agent sends apology acknowledgment to claimant:
   - Template: "Dear [claimant_name], we apologize for the delay in responding to your claim. Your claim (#[claim_id]) is now being processed by [adjuster_name]..."
   - Send via email + SMS (if available)
- [ ] Agent logs apology sent
- [ ] Agent performs root cause analysis:
   - **Question**: Was delay due to policy lookup latency? (check policy_lookup_duration)
   - **Question**: Was delay due to system downtime? (check integration error logs)
   - **Question**: Was delay due to high claim volume? (check claims_received_per_hour)
   - **Question**: Was delay due to escalation? (check if claim was PENDING_REVIEW)
- [ ] Agent checks SLA breach rate: `sla_breaches_today / claims_processed_today`
- [ ] IF breach rate >10% in any 4-hour window:
   - [ ] Agent sends alert to operations manager: "SLA breach rate exceeded 10% (current: X%)"
   - [ ] Operations manager investigates (system capacity issue? staffing issue? process bottleneck?)

**Root Cause Analysis**:
- **Question 1**: Policy lookup latency? (if policy_lookup_duration >30s *[A26]*, latency is issue)
- **Question 2**: System downtime? (if integration errors >5% in past hour, system is issue *[U5]*)
- **Question 3**: High claim volume? (if claims_received_per_hour >30, capacity is issue)
- **Question 4**: Escalation delay? (if claim was PENDING_REVIEW >1 hour, human response time is issue)

**Remediation**:
- IF policy lookup latency: Implement parallel processing, add caching, upgrade legacy system *[U5]*
- IF system downtime: Escalate to IT team, implement fallback workflows
- IF high volume: Scale infrastructure (add compute capacity, optimize processing)
- IF escalation delay: Increase human staffing, adjust escalation thresholds *[A20, A21]*

**Alert Thresholds**:
- **SLA breach rate >10% in any 4-hour window** (target 4% *[A14]*): Alert operations manager
- **Daily SLA breach rate >6%** (sustained): Alert senior management, review capacity planning
- **Individual claim delay >4 hours**: Alert operations manager immediately (critical breach)

**Assumption References**: *[A4, A14, A26, A39, U5]*

---

**Failure Mode 4: Agent Extracts Incorrect Data (Wrong Policy Number)**

**Detection Method**:
- Policy lookup returns 404 (policy not found) → suggests extraction error
- Human review during escalation catches error ("Extracted policy number doesn't match document")
- QA audit compares extracted fields to source document

**Expected Behavior**:
- [ ] Agent logs extraction error: `extraction_error: field=policy_number, extracted_value=AA12345678, confidence=0.75, actual_value=AA12345679`
- [ ] Agent escalates to human: "Policy lookup failed. Possible extraction error. Please verify policy number from original document."
- [ ] Human reviews original document:
   - Confirms extraction error (OCR misread "9" as "8")
   - Corrects policy_number in UI: AA12345679
   - Clicks "Retry Policy Lookup"
- [ ] Agent logs correction for model retraining *[U2]*:
   - Store: {document_image, extracted_value, correct_value, confidence_score}
   - Flag for OCR model retraining (improve digit recognition)
- [ ] Agent checks extraction error rate: `extraction_errors_today / claims_processed_today`
- [ ] IF error rate >10% for specific document type (e.g., handwritten forms):
   - [ ] Agent alerts QA team: "Extraction error rate for handwritten forms exceeded 10%"
   - [ ] QA team investigates: Is OCR model undertrained on handwritten text? Need more training data?

**Root Cause Analysis**:
- **Question 1**: Is this an OCR issue? (low-quality scan, handwritten text, unusual font)
- **Question 2**: Is this a model issue? (model not trained on this document type)
- **Question 3**: Is this a data format issue? (policy number format varies by state/region)

**Remediation**:
- IF OCR issue: Improve OCR preprocessing (image enhancement, noise reduction), use better OCR model
- IF model issue: Add training examples for this document type *[U2]*
- IF format issue: Update validation rules to handle format variations

**Alert Thresholds**:
- **Daily extraction error rate >10%** (target <5%): Alert QA team
- **Extraction error rate for specific document type >20%**: Alert QA team, flag document type for model improvement
- **Critical field errors (policy_number, claimant_name) >5%**: Alert operations manager (high downstream impact)

**Assumption References**: *[A22, A23, A24, A39, U2]*

---

**Failure Mode 5: Legacy System Timeout (Policy Lookup Takes >30 Sec)**

**Detection Method**:
- API call exceeds timeout threshold *[A26: 30 sec]*
- Retry logic exhausted (3 attempts with exponential backoff)
- Integration monitoring dashboard shows timeout spike

**Expected Behavior**:
- [ ] Agent logs system error: `integration_error: system=PolicyAdmin, operation=LookupPolicy, error=timeout, duration=30s, attempts=3`
- [ ] Agent escalates to human + IT support:
   - Create EscalationTicket:
     - trigger_condition: "Legacy system timeout after 3 retries"
     - escalation_target: IT_SUPPORT + CLAIMS_SPECIALIST
     - ai_recommendation: "Legacy system unresponsive. Claim cannot proceed without policy data. Options: (1) Wait for system recovery and retry, (2) Manual policy lookup by specialist."
     - supporting_evidence: {policy_number: "AA12345678", timeout_duration: 30, retry_attempts: 3, error_logs: "..."}
   - Notify IT support (email + Slack): "PolicyAdmin system timeout detected, claim_id=uuid"
   - Notify claims specialist (email): "Claim paused due to system issue, manual policy lookup may be required"
- [ ] Agent sets claim.state = PENDING_SYSTEM_ISSUE
- [ ] Agent checks system timeout rate: `system_timeouts_per_hour / api_calls_per_hour`
- [ ] IF timeout rate >5% in past hour:
   - [ ] Agent sends alert to IT team: "PolicyAdmin timeout rate exceeded 5% (current: X%)"
   - [ ] IT team investigates: Is system overloaded? Network issue? Database issue?
- [ ] Agent waits for system recovery or human decision:
   - IF system recovers (timeout rate drops <5%): Retry policy lookup automatically
   - IF human provides manual policy data: Proceed with human-provided data
   - IF system down for >1 hour: Escalate to operations manager for process decision (pause all claims? manual processing?)

**Root Cause Analysis**:
- **Question 1**: Is legacy system overloaded? (high request volume, database slow)
- **Question 2**: Is network connectivity issue? (latency spike, packet loss)
- **Question 3**: Is this a specific policy issue? (large policy with many endorsements, slow query)

**Remediation**:
- IF system overloaded: Scale legacy system (add capacity), optimize database queries, implement caching
- IF network issue: Escalate to network team, implement connection pooling
- IF specific policy issue: Optimize policy lookup query, implement timeout extension for complex policies

**Alert Thresholds**:
- **Timeout rate >5% in any hour** (target <1%): Alert IT team
- **Timeout rate >10% in any hour**: Alert IT manager + operations manager (critical system issue)
- **System down for >1 hour**: Alert senior management, activate incident response plan

**Assumption References**: *[A26, A39, U5]*

---

**Failure Mode 6: Agent Has Low Confidence But Doesn't Escalate (Confidence = 83%, Threshold = 85%)**

**Detection Method**:
- QA audit reviews confidence scores for all autonomous decisions
- Post-hoc analysis: Claims with confidence 80-85% have higher error rates than expected
- Weekly QA report flags borderline confidence decisions

**Expected Behavior**:
- [ ] Agent logs borderline confidence decision: `low_confidence_decision: claim_id=uuid, component=coverage_determination, confidence=0.83, threshold=0.85, decision=COVERED`
- [ ] QA team reviews these claims in daily audit (prioritize for human review):
   - Sample 100% of claims with confidence 80-85% (vs. 5% sample for high-confidence claims)
   - Compare AI decision to adjuster feedback (was coverage determination correct?)
   - Calculate error rate for borderline confidence claims
- [ ] IF error rate for 80-85% confidence claims >10%:
   - [ ] QA team recommends threshold adjustment: Increase from 85% to 90% *[A20]*
   - [ ] Rationale: "Error rate for 83-85% confidence claims is 12%, exceeding 10% tolerance. Raising threshold to 90% will reduce errors at cost of 5% more escalations."
   - [ ] Operations manager approves threshold change
   - [ ] Agent updates threshold: `confidence_threshold = 0.90`
- [ ] IF error rate for 80-85% confidence claims <5%:
   - [ ] QA team recommends threshold adjustment: Decrease from 85% to 80% *[A20]*
   - [ ] Rationale: "Error rate for 80-85% confidence claims is only 3%, below 5% tolerance. Lowering threshold to 80% will reduce escalations by 8% with minimal error increase."
   - [ ] Operations manager approves threshold change
   - [ ] Agent updates threshold: `confidence_threshold = 0.80`

**Root Cause Analysis**:
- **Question 1**: Is confidence calibration accurate? (does 83% confidence actually mean 83% accuracy?)
- **Question 2**: Is threshold too aggressive? (should we escalate more conservatively?)
- **Question 3**: Is this specific to certain claim types? (some claim types have lower confidence but same accuracy)

**Remediation**:
- IF calibration issue: Re-calibrate model (adjust confidence scores to match actual accuracy)
- IF threshold issue: Adjust threshold based on error rate analysis (see above)
- IF claim type issue: Implement claim-type-specific thresholds (e.g., 85% for auto, 90% for property)

**Alert Thresholds**:
- **Weekly review**: QA team analyzes borderline confidence claims (80-85% range)
- **Monthly review**: Operations manager reviews threshold performance, approves adjustments if needed
- **Error rate for borderline claims >10%**: Immediate threshold increase to 90%

**Assumption References**: *[A9, A20, A39]*

---

### 9.4 Validation Metrics

#### Real-Time Metrics (Monitored Continuously)

| Metric Name | Target | Alert Threshold | Assumption Reference |
|-------------|--------|-----------------|---------------------|
| **SLA Compliance Rate** | 96% of claims acknowledged within 2 hours | <90% in any 4-hour window | A14, Metric 1 |
| **Routing Accuracy Rate** | 97% of claims not re-routed by adjuster | <90% in any day | A15, Metric 2 |
| **Escalation Rate** | 15% of claims escalated to human | <10% (under-escalating) or >25% (over-escalating) in any day | A5 |
| **Processing Time (Autonomous)** | Median <2 min from receipt to acknowledgment | Median >5 min in any hour | A8, A23, A26, A30, A33, A36, A37 |
| **Processing Time (Escalated)** | Median <15 min from receipt to acknowledgment (including human review) | Median >30 min in any day | A31 |
| **System Integration Uptime** | 99% of API calls succeed within timeout | <95% in any hour | U5 |
| **AI Confidence Distribution** | 85% of decisions have confidence >90%, 10% have 85-90%, 5% have <85% | >30% of decisions have confidence <85% (model drift) | A20 |

**Monitoring Infrastructure**:
- Real-time dashboard (Grafana/Datadog) with 1-minute refresh
- Automated alerts via email + Slack + PagerDuty (for critical alerts)
- Alert routing: QA team (SLA, routing, escalation), IT team (system uptime), operations manager (critical issues)

---

#### Daily Metrics (Reviewed by QA Team)

| Metric Name | Target | Alert Condition | Assumption Reference |
|-------------|--------|-----------------|---------------------|
| **Extraction Error Rate** | <5% of claims require extraction correction | >10% in any day | A22, A24 |
| **Coverage Error Rate** | <0.5% for straightforward claims, <2% for moderate complexity | >2% for straightforward, >5% for moderate in any day | A43 |
| **Routing Error Rate** | <3% of claims re-routed by adjuster | >5% in any day | A9, A15 |
| **Cost per Claim (Actual)** | $1.55 avg (AI + human oversight) | >$2.00 avg in any day | A16, Metric 3 |
| **Confidence Distribution Shift** | Stable distribution (85% >90%, 10% 85-90%, 5% <85%) | >10% shift in any bucket (indicates model drift) | A20 |
| **Exception Rate** | 8% of claims require exception handling | >15% in any day (indicates process issues) | A38 |

**QA Process** *[A39]*:
- QA specialist reviews daily dashboard (30 min/day)
- Sample audit: 5% of autonomous claims (15 claims/day), 100% of borderline confidence claims (80-85%)
- Error logging: All errors logged with root cause category (extraction, coverage, routing, system)
- Daily report: Summary email to operations manager with error breakdown and trends

---

#### Weekly Metrics (Reviewed by Management)

| Metric Name | Target | Trend Analysis | Assumption Reference |
|-------------|--------|----------------|---------------------|
| **Adjuster Productivity** | 10 claims/day per adjuster (25% increase from 8 baseline) | Stable or improving | A13, A18, Metric 5 |
| **Customer Satisfaction** | >4.0/5.0 rating on post-claim survey | Stable or improving | — |
| **Model Performance Trends** | Error rate stable or decreasing, confidence stable or increasing | Degrading (indicates model drift or data quality issues) | A9, A20, U2 |
| **Cost per Claim (Trend)** | Stable at $1.55 or decreasing | Increasing (indicates higher escalation rate or longer processing time) | A16, Metric 3 |
| **Automation Rate** | 85% of claims processed without human intervention | Decreasing (indicates over-escalation or process issues) | A10, Metric 4 |

**Management Review Process**:
- Weekly meeting (1 hour) with operations manager, QA lead, IT lead
- Review: Metrics dashboard, error trends, escalation patterns, cost analysis
- Decisions: Threshold adjustments (A20, A21, A24, A29), model retraining schedule, process improvements
- Action items: Assigned to QA team (model retraining), IT team (system optimization), operations team (staffing adjustments)

---

## 10. Economic Model

### 10.1 Current State Costs (Manual Processing Baseline)

| Cost Category | Calculation | Daily Cost | Annual Cost (250 days) |
|---------------|-------------|------------|------------------------|
| **Labor** | 300 claims/day × 22 min/claim *[A6]* ÷ 60 min/hour × $45/hour *[A1]* | $4,950 | $1,237,500 *[A2]* |
| **SLA Breach Penalties** | 300 claims/day × 31% breach rate × $25/breach *[A4]* | $2,325 | $581,250 |
| **Routing Error Rework** | 300 claims/day × 18% error rate × 45 min/error *[A3]* ÷ 60 × $45/hour *[A1]* | $1,822 | $455,625 |
| **Coverage Error Costs** | 300 claims/day × 5% error rate (assumed baseline) × $2,000/error *[A27]* | $30,000 | $7,500,000 |
| **TOTAL CURRENT COST** | — | **$39,097** | **$9,774,375** |

**Note**: Coverage error costs dominate the economic model. Baseline 5% error rate is assumed (industry standard for manual processing, *[U6: actual rate unknown]*). This drives the business case for automation with human oversight.

---

### 10.2 Future State Costs (AI + Human Oversight)

**New Assumptions Required for Realistic Economic Model**:

**A41**: Coverage determination error rate varies by claim complexity:
- **Straightforward claims (70% of total)**: 0.5% error rate with AI (highly codifiable, well-trained model)
- **Moderate complexity (15% of total)**: 2% error rate with AI (some ambiguity, requires pattern recognition)
- **High complexity (15% of total)**: 8% error rate if fully automated → **these get human review** *[A5]*, reducing error rate to 0.1%

*Reasoning*: Uniform 3% error rate *[A9]* is unrealistic for high-stakes decisions like coverage determination. Error rates vary by claim complexity. Human oversight for high-complexity claims (15% *[A5]*) prevents costly errors.

*Used in*: Coverage error cost calculation

*Risk if wrong*: If actual error rates are higher (e.g., 2% for straightforward, 5% for moderate), coverage error costs increase from $997K to $2.5M, reducing ROI from 54% to 35%.

---

**A42**: Coverage error cost of $2,000 *[A27]* is **expected value** (probability × impact), not cost per error:
- **50% of errors caught by adjuster** before payout: Cost = 1 hour adjuster time = $45 *[A1]*
- **40% of errors result in small disputes**: Cost = $500 avg (customer service, appeals, small settlement)
- **10% of errors result in lawsuits/regulatory issues**: Cost = $20,000 avg (legal fees, settlements, penalties)
- **Weighted average**: 0.5 × $45 + 0.4 × $500 + 0.1 × $20,000 = $22.50 + $200 + $2,000 = **$2,222.50** (rounds to $2,000 *[A27]*)

*Reasoning*: Not all coverage errors result in lawsuits. Most are caught and corrected by adjusters or resolved through appeals. The $2,000 figure is a blended expected value across all error outcomes.

*Used in*: Coverage error cost calculation

*Risk if wrong*: If actual lawsuit rate is 20% (not 10%), expected value increases to $4,200, doubling coverage error costs.

---

**A43**: Routing error rate of 3% *[A9]* applies to **routing decisions**, not coverage determination:
- **Routing error rate**: 3% (AI at 97% accuracy *[A15]*, vs. 82% human baseline)
- **Coverage error rate**: Varies by complexity (see A41: 0.5% straightforward, 2% moderate, 0.1% high-complexity with human review)

*Reasoning*: Original assumption A9 (3% error rate) was ambiguous about which component it applied to. Routing errors are low-cost (45 min rework *[A3]*), so 3% is acceptable. Coverage errors are high-cost ($2,000 *[A27]*), so must be <1% for straightforward claims.

*Used in*: Coverage error cost calculation, routing error cost calculation

*Risk if wrong*: If coverage error rate is actually 3% (same as routing), coverage error costs increase from $997K to $4.5M, making project economically unviable.

---

| Cost Category | Calculation | Daily Cost | Annual Cost (250 days) |
|---------------|-------------|------------|------------------------|
| **AI Processing** | 300 claims/day × $0.15/claim *[A7]* | $45 | $11,250 |
| **Human Review (15% of claims)** | 45 claims/day × 12 min/claim *[A8]* ÷ 60 × $45/hour *[A1]* | $405 | $101,250 |
| **Exception Handling (8% of claims)** | 24 claims/day × 15 min/exception *[A38]* ÷ 60 × $45/hour *[A1]* | $270 | $67,500 |
| **QA Monitoring** | 45 min/day *[A39]* ÷ 60 × $45/hour *[A1]* | $34 | $8,438 |
| **Infrastructure (MLOps, monitoring)** | Embedded in A7 assumption, allocated separately for clarity | $800 | $200,000 *[A7]* |
| **SLA Breach Penalties** | 300 claims/day × 4% breach rate *[A14]* × $25/breach *[A4]* | $300 | $75,000 |
| **Routing Error Rework** | 300 claims/day × 3% error rate *[A9, A43]* × 45 min/error *[A3]* ÷ 60 × $45/hour *[A1]* | $304 | $75,938 |
| **Coverage Error Costs** | See detailed calculation below | $3,990 | $997,500 |
| **TOTAL FUTURE COST** | — | **$6,148** | **$1,536,876** |

**Coverage Error Cost Calculation** (using A41, A42, A43):

- **Straightforward claims (70% of 300 = 210 claims/day)**:
  - Error rate: 0.5% *[A41]*
  - Errors per day: 210 × 0.5% = 1.05
  - Cost per error: $2,000 *[A27, A42]*
  - Daily cost: 1.05 × $2,000 = $2,100
  - Annual cost: $2,100 × 250 = **$525,000**

- **Moderate complexity (15% of 300 = 45 claims/day, processed autonomously)**:
  - Error rate: 2% *[A41]*
  - Errors per day: 45 × 2% = 0.9
  - Cost per error: $2,000 *[A27, A42]*
  - Daily cost: 0.9 × $2,000 = $1,800
  - Annual cost: $1,800 × 250 = **$450,000**

- **High complexity (15% of 300 = 45 claims/day, human-reviewed)** *[A5]*:
  - Error rate: 0.1% (human review reduces from 8% to 0.1%) *[A41]*
  - Errors per day: 45 × 0.1% = 0.045
  - Cost per error: $2,000 *[A27, A42]*
  - Daily cost: 0.045 × $2,000 = $90
  - Annual cost: $90 × 250 = **$22,500**

- **Total Coverage Error Costs**: $525K + $450K + $22.5K = **$997,500/year**

---

### 10.3 Cost Comparison Table

| Cost Category | Current (Manual) | Future (AI + Human) | Delta | % Change |
|---------------|------------------|---------------------|-------|----------|
| **Labor** | $1,237,500 | $177,188 ($101K review + $67.5K exceptions + $8.4K QA) | -$1,060,312 | **-86%** |
| **AI Processing** | $0 | $11,250 | +$11,250 | N/A |
| **Infrastructure** | $0 | $200,000 | +$200,000 | N/A |
| **SLA Breach Penalties** | $581,250 | $75,000 | -$506,250 | **-87%** |
| **Routing Error Rework** | $455,625 | $75,938 | -$379,687 | **-83%** |
| **Coverage Error Costs** | $7,500,000 | $997,500 | -$6,502,500 | **-87%** |
| **TOTAL** | **$9,774,375** | **$1,536,876** | **-$8,237,499** | **-84%** |

**Net Annual Savings**: **$8,237,499** (84% cost reduction)

**Key Insight**: The business case is driven by **coverage error reduction** (from $7.5M to $997K), not just labor savings. Human oversight for 15% of claims *[A5]* prevents $6.5M in coverage errors annually, justifying the $177K human review cost.

---

### 10.4 ROI Calculation

**Implementation Cost**:
- Team: 1 FDE + 1 ML Engineer + 1 Backend Engineer + 1 QA Engineer
- Duration: 6 months *[A11]*
- Cost: 6 months × $85K/month avg *[A11]* = **$510,000**

**Payback Period**:
- Annual savings: $8,237,499
- Implementation cost: $510,000
- Payback: $510,000 ÷ $8,237,499 × 12 months = **0.74 months** (~3 weeks)

**Cost per Claim**:
- **Current**: $9,774,375 ÷ 75,000 claims/year = **$130.33/claim**
- **Future**: $1,536,876 ÷ 75,000 claims/year = **$20.49/claim**
- **Reduction**: 84% (not 91% as originally estimated *[A16]* – original estimate did not account for realistic coverage error costs)

**3-Year ROI**:
- Year 1: -$510K (implementation) + $8,237K (savings) = **$7,727K net**
- Year 2: $8,237K (savings) = **$8,237K net**
- Year 3: $8,237K (savings) = **$8,237K net**
- **3-Year Total**: **$24,201K** (47x return on $510K investment)

---

### 10.5 Sensitivity Analysis

**Scenario 1: Escalation Rate Increases from 15% to 25%** *[A5]*

- **Impact on Human Review Costs**:
  - Current: 45 claims/day × 12 min *[A8]* = 540 min/day = $405/day
  - New: 75 claims/day × 12 min = 900 min/day = $675/day
  - Increase: $270/day = $67,500/year

- **Impact on Coverage Error Costs**:
  - High-complexity claims increase from 15% to 25% (10% more get human review)
  - Moderate-complexity errors decrease: 30 claims/day (instead of 45) × 2% × $2,000 = $1,200/day (instead of $1,800/day)
  - High-complexity errors increase: 75 claims/day (instead of 45) × 0.1% × $2,000 = $150/day (instead of $90/day)
  - Net change: ($1,200 + $150) - ($1,800 + $90) = -$540/day = -$135,000/year (error costs decrease)

- **Net Impact**:
  - Human review costs increase: +$67,500/year
  - Coverage error costs decrease: -$135,000/year
  - **Net savings increase by $67,500/year** (from $8.24M to $8.30M)
  - Cost per claim: $20.49 → **$19.59** (improves)

**Takeaway**: Higher escalation rate (25% vs. 15%) actually **improves ROI** because it prevents more high-cost coverage errors ($135K savings) than it adds in human review costs ($67.5K). This suggests the 15% escalation rate *[A5]* may be too aggressive (under-escalating).

---

**Scenario 2: AI Error Rates Increase (Coverage: 1% → 2% for straightforward, 2% → 5% for moderate)** *[A41, A43]*

- **Impact on Coverage Error Costs**:
  - Straightforward: 210 claims/day × 2% × $2,000 = $8,400/day (instead of $2,100/day)
  - Moderate: 45 claims/day × 5% × $2,000 = $4,500/day (instead of $1,800/day)
  - High-complexity: Unchanged (human-reviewed)
  - Total: ($8,400 + $4,500 + $90) × 250 days = **$3,247,500/year** (instead of $997,500/year)
  - Increase: $2,250,000/year

- **Net Impact**:
  - Total future cost: $1,536,876 + $2,250,000 = **$3,786,876/year**
  - Net savings: $9,774,375 - $3,786,876 = **$5,987,499/year** (61% reduction, down from 84%)
  - Cost per claim: $20.49 → **$50.49**
  - Payback period: 0.74 months → **1.0 month**

**Takeaway**: Higher AI error rates significantly reduce ROI (from 84% cost reduction to 61%), but project remains economically viable. If error rates are this high, must increase escalation rate (e.g., from 15% to 30%) to maintain error cost control.

---

**Scenario 3: Legacy System Requires Infrastructure Upgrade ($100K)** *[U5]*

- **Impact on Implementation Cost**:
  - Current: $510,000
  - New: $510,000 + $100,000 = **$610,000**
  - Payback period: 0.74 months → **0.89 months** (~4 weeks)

- **Impact on Annual Costs**:
  - Infrastructure costs increase: $200,000 → $220,000 (amortize $100K upgrade over 5 years)
  - Total future cost: $1,536,876 + $20,000 = **$1,556,876/year**
  - Net savings: $9,774,375 - $1,556,876 = **$8,217,499/year** (84% reduction, minimal change)

**Takeaway**: Infrastructure upgrade has minimal impact on ROI (payback extends by 1 week). Legacy system performance *[U5]* is not a critical economic dependency.

---

### 10.6 Critical Economic Dependencies

**Dependency 1: Definition of "High-Value/Ambiguous" Claims** *[U1]*

- **Current assumption**: 15% of claims require human oversight *[A5]*, defined as value >$100K *[A21]* OR fraud ≥3 *[A29]* OR AI confidence <85% *[A20]*

- **If U1 resolves to 40% escalation rate** (e.g., threshold lowered to $50K, or confidence threshold raised to 95%):
  - Human review costs: 120 claims/day × 12 min *[A8]* = 1,440 min/day = $1,080/day = **$270,000/year** (up from $101K)
  - Coverage error costs: Decrease to **$600,000/year** (more claims get human review, fewer errors)
  - Total future cost: $1,536,876 + $169,000 (additional human review) - $397,500 (error reduction) = **$1,308,376/year**
  - Net savings: $9,774,375 - $1,308,376 = **$8,466,000/year** (87% reduction, improves from 84%)
  - Cost per claim: $20.49 → **$17.44** (improves)

- **Takeaway**: Higher escalation rate (40% vs. 15%) **improves ROI** because error cost reduction ($397K) exceeds human review cost increase ($169K). **U1 is critical but not a viability risk** – project economics improve with more conservative escalation.

---

**Dependency 2: Historical Data Quality** *[U2]*

- **Current assumption**: Sufficient training data to achieve 0.5% error rate for straightforward claims *[A41]*

- **If U2 resolves to poor data quality** (error rates: 2% straightforward, 5% moderate, 10% high-complexity):
  - Coverage error costs: $3,247,500/year (calculated in Scenario 2 above)
  - Must increase escalation rate to 30% to control errors (more human review for ambiguous cases)
  - Human review costs: 90 claims/day × 12 min = **$202,500/year** (up from $101K)
  - Total future cost: $1,536,876 + $101,250 (additional human review) + $2,250,000 (additional errors) = **$3,888,126/year**
  - Net savings: $9,774,375 - $3,888,126 = **$5,886,249/year** (60% reduction, down from 84%)
  - Cost per claim: $20.49 → **$51.84**

- **Takeaway**: Poor data quality *[U2]* significantly reduces ROI (from 84% to 60% cost reduction), but project remains viable. **U2 is a critical dependency** – must validate data quality in first 2 weeks of project. If data is poor, adjust expectations (60% cost reduction instead of 84%) and plan for more aggressive human oversight (30% escalation rate).

---

**Dependency 3: Client's Risk Tolerance** *[U12]*

- **Current assumption**: Client accepts 0.5-2% error rates *[A41]* with 15% human oversight *[A5]*

- **If U12 resolves to risk-averse** (client requires 99%+ accuracy, zero tolerance for coverage errors):
  - Must increase escalation rate to 50% (human reviews all moderate and high-complexity claims)
  - Human review costs: 150 claims/day × 12 min = **$337,500/year** (up from $101K)
  - Coverage error costs: Decrease to **$262,500/year** (only straightforward claims at 0.5% error rate)
  - Total future cost: $1,536,876 + $236,250 (additional human review) - $735,000 (error reduction) = **$1,038,126/year**
  - Net savings: $9,774,375 - $1,038,126 = **$8,736,249/year** (89% reduction, improves from 84%)
  - Cost per claim: $20.49 → **$13.84** (improves)

- **Takeaway**: Risk-averse client (50% escalation) **improves ROI** because error cost reduction ($735K) far exceeds human review cost increase ($236K). **U12 is not a viability risk** – project economics improve with more conservative approach.

---

**What Would Make the Project Economically Unviable?**

The project becomes unviable if:

1. **Coverage error costs cannot be reduced below $5M/year** (current $7.5M):
   - This would require AI error rates >5% for straightforward claims AND no human oversight
   - Mitigation: Increase escalation rate to 40-50%, ensuring error costs stay <$1M

2. **Human review costs exceed $2M/year** (e.g., 80%+ escalation rate):
   - This would require escalation threshold so conservative that most claims need human review
   - Mitigation: Adjust thresholds *[A20, A21]* to balance error cost vs. review cost

3. **Implementation cost exceeds $5M** (10x current estimate):
   - This would require massive custom development or legacy system replacement
   - Mitigation: Validate integration complexity *[U5]* in discovery, avoid scope creep

**None of these scenarios are likely** based on current assumptions. The project has strong economic fundamentals driven by coverage error reduction.

---

## 11. Open Questions & Assumptions to Validate

### Critical Unknowns (Must Resolve in Discovery)

**U1: Definition of "High-Value/Ambiguous" Claims**
- **Current assumption**: 15% of claims *[A5]*, defined as value >$100K *[A21]* OR fraud ≥3 *[A29]* OR AI confidence <85% *[A20]*
- **Impact**: Affects escalation rate from 10% to 40%, cost per claim from $13 to $52
- **Validation method**: Interview claims managers, review historical escalation patterns, analyze claim value distribution
- **Timeline**: Week 1 of discovery
- **Decision**: Finalize thresholds (A20, A21, A29) with client stakeholders

**U2: Historical Data Quality**
- **Current assumption**: Sufficient training data to achieve 0.5-2% error rates *[A41]*
- **Impact**: Affects error rates from 0.5% to 5%+, cost per claim from $20 to $52
- **Validation method**: Audit historical claims data (volume: need 10K+ labeled examples, labeling: need ground-truth coverage decisions, completeness: need all fields populated, diversity: need coverage of all claim types)
- **Timeline**: Weeks 1-2 of discovery
- **Decision**: If data quality is poor, adjust error rate assumptions (A41, A43) and escalation rate (A5) to 30%

**U12: Client's Risk Tolerance**
- **Current assumption**: Client accepts 0.5-2% error rates *[A41]* with 15% human oversight *[A5]*
- **Impact**: Affects escalation rate from 15% to 50%, cost per claim from $14 to $20
- **Validation method**: Executive interviews to understand ROI requirements, budget constraints, error tolerance, regulatory concerns
- **Timeline**: Week 1 of discovery
- **Decision**: Finalize escalation rate (A5) and confidence thresholds (A20) based on risk appetite

**U5: Legacy System Latency and Availability**
- **Current assumption**: 10-30 sec latency *[A26]*, 99%+ availability
- **Impact**: Affects SLA compliance (Metric 1) from 96% to 85%, may require infrastructure investment ($100K)
- **Validation method**: API documentation review, latency testing (measure actual response times for 100 sample lookups), availability analysis (review system uptime logs for past 6 months)
- **Timeline**: Weeks 2-3 of discovery
- **Decision**: If latency >30 sec or availability <95%, plan for parallel processing, caching, or infrastructure upgrade

---

### Assumptions to Validate in Pilot (Weeks 4-6)

**A23: AI Data Extraction Time = 15 Seconds**
- **Validation**: Measure actual extraction time for 100 sample claims (various document types)
- **Expected range**: 10-20 seconds (if >20 sec, may need faster LLM or optimized prompts)
- **Impact if wrong**: If actual time is 30 sec, still meets 2-hour SLA but reduces throughput capacity

**A26: Policy Lookup Time = 10 Seconds (Baseline), 30 Seconds (Worst-Case)**
- **Validation**: Measure actual SOAP call latency for 100 sample lookups
- **Expected range**: 5-30 seconds (if >30 sec, may need parallel processing or caching)
- **Impact if wrong**: If actual time is 60 sec, violates 2-hour SLA at scale (300 claims × 60 sec = 5 hours sequential)

**A31: Human Review Time = 2 Minutes for Escalated Claims**
- **Validation**: Measure actual review time for 20 escalated claims (specialists timed during pilot)
- **Expected range**: 1-5 minutes (if >5 min, may need better AI recommendations or UI improvements)
- **Impact if wrong**: If actual time is 5 min, human review costs increase from $101K to $253K/year

**A41: Coverage Error Rate = 0.5% for Straightforward Claims**
- **Validation**: Measure actual error rate in pilot (compare AI decisions to adjuster feedback for 100 claims)
- **Expected range**: 0.5-2% (if >2%, may need more training data or higher escalation rate)
- **Impact if wrong**: If actual rate is 2%, coverage error costs increase from $525K to $2.1M/year

**A43: Routing Error Rate = 3%**
- **Validation**: Measure actual re-routing rate in pilot (track "Not My Claim" clicks for 100 routed claims)
- **Expected range**: 2-5% (if >5%, may need better routing model or adjuster data quality improvements)
- **Impact if wrong**: If actual rate is 8%, routing error costs increase from $76K to $202K/year (still acceptable)

---

### Design Decisions to Finalize with Client

**A20: AI Confidence Threshold = 85%**
- **Current value**: 85% (below this, escalate to human)
- **Client may want**: 80% (more aggressive automation) or 90% (more conservative)
- **Trade-off**: Lower threshold (80%) → 10% escalation rate, higher error risk. Higher threshold (90%) → 25% escalation rate, lower error risk.
- **Recommendation**: Start at 85%, adjust based on pilot error rates (if errors <1%, lower to 80%; if errors >3%, raise to 90%)

**A21: High-Value Threshold = $100K**
- **Current value**: $100K (above this, escalate to senior adjuster)
- **Client may want**: $50K (more conservative) or $250K (more aggressive)
- **Trade-off**: Lower threshold ($50K) → 25% escalation rate, higher human review costs. Higher threshold ($250K) → 8% escalation rate, lower human review costs but higher error risk.
- **Recommendation**: Start at $100K, adjust based on client's risk tolerance *[U12]* and claim value distribution

**A29: Fraud Indicator Threshold = 3 Flags**
- **Current value**: 3 flags (at 3+, escalate to fraud investigator)
- **Client may want**: 2 flags (more sensitive) or 4 flags (less sensitive)
- **Trade-off**: Lower threshold (2 flags) → more fraud investigations (may catch more fraud but also more false positives). Higher threshold (4 flags) → fewer investigations (may miss some fraud).
- **Recommendation**: Start at 3 flags, adjust based on client's fraud exposure and investigator capacity

---

**End of Capability Specification v0.1**

---

**Next Steps**:
1. **Discovery (Weeks 1-3)**: Resolve U1, U2, U12, U5 through stakeholder interviews, data audits, and technical assessments
2. **Design (Week 4)**: Finalize thresholds (A20, A21, A29) and workflow based on discovery findings
3. **Prototype (Weeks 5-6)**: Build Components 1-3 (extraction, validation, policy lookup), validate time estimates (A23, A26)
4. **Pilot (Weeks 7-8)**: Process 10% of claims (30/day) for 2 weeks, measure actual error rates (A41, A43), escalation rate (A5), and cost per claim (A16)
5. **Adjust (Week 9)**: Refine thresholds and delegation boundaries based on pilot results
6. **Full Rollout (Weeks 10-24)**: Implement remaining components (4-10), scale to 100% of claims, monitor metrics (Section 8.4)