# Capability Specification: Prior-Authorization Check (PA-CHECK-001)  

**VERSION**: 2.0 (Refactored - Main Spec)  
**LAST UPDATED**: 2026-04-22  

---

**📚 DETAILED DOCUMENTATION**

This is the main specification. For implementation details, see:
- **[Core Decision Logic](specs/decision-logic.md)** - 5-step prior-auth verification process
- **[Ambiguity and Escalation](specs/ambiguity-and-escalation.md)** - When to escalate, escalation protocol
- **[Assumptions](specs/assumptions.md)** - All assumptions, validation requirements, criticality
- **[API Specifications](specs/api-specifications.md)** - REST APIs, database schemas, algorithms
- **[Requirements](specs/requirements.md)** - Functional & non-functional requirements  
- **[Edge Cases & Testing](specs/edge-cases-and-testing.md)** - Test scenarios & validation  
- **[Integration Guide](specs/integration-guide.md)** - EHR, database, UI integration  
- **[Business Case](specs/business-case.md)** - ROI analysis & risk register  

---

## 1. Capability Overview  
  
### Purpose  
  
This capability solves the problem of **physicians discovering expired or missing prior-authorizations during patient visits**, which wastes physician time (4 min per error per A6), creates patient friction, and results in claim denials costing $500-5,000 per incident. Currently, 3% of intake processes have prior-auth errors [per A2], with prior-auth being identified as "most commonly" the error type in the scenario.  
  
The capability automates prior-auth lookup, matching, and validity assessment while preserving human decision-making authority for proceed/reschedule decisions.  
  
### Scope  
  
**In Scope**:  
- Automated determination of whether scheduled procedure requires prior-authorization  
- Retrieval of prior-auth records from prior-auth database/system  
- Matching prior-auth records to scheduled procedures (CPT code matching, date range validation)  
- Expiration status assessment (valid, expired, expiring soon)  
- Confidence scoring for AI recommendations  
- Human review interface for front-desk staff to approve/override/escalate  
- EHR documentation of prior-auth verification status and decisions  
- Escalation workflow for ambiguous cases  
- Audit logging of all checks, recommendations, and human decisions  
  
**Out of Scope**:  
- Obtaining new prior-authorizations from insurance companies (remains manual process)  
- Appealing denied prior-authorization requests  
- Modifying or updating prior-auth records in external systems  
- Direct patient communication about prior-auth status  
- Clinical judgment about medical necessity of procedures  
- Scheduling or rescheduling appointments (human decides, system documents)  
- Contacting insurance companies for clarification  
  
### Success Criteria  
  
**Quantified Metrics** (from delegation analysis):  
  
1. **Error Rate Reduction**: Reduce prior-auth errors from 3% [per A2] to ≤0.75% [per A9] (75% reduction)  
   - Measurement: Weekly audit of physician-reported prior-auth issues discovered during visits  
   - Target: <1 prior-auth error per 133 patients checked  
  
2. **Time Efficiency**: Reduce human time from 2.5 min [per A3] to ≤0.5 min [per A8] per patient requiring prior-auth  
   - Measurement: Time-motion study of front-desk staff review time  
   - Target: 80% time reduction  
  
3. **Escalation Rate**: AI handles ≥80% of cases with high confidence (escalation rate <20%)  
   - Measurement: Daily tracking of escalation rate (cases flagged for human investigation)  
   - Target: <20% of prior-auth checks escalate beyond routine human review  
  
4. **Accuracy**: AI recommendation accuracy ≥95% when confidence score = High  
   - Measurement: Weekly audit comparing AI recommendations to human decisions  
   - Target: When AI says "Proceed" with high confidence, human agrees ≥95% of time  
  
5. **Availability**: System available ≥99% of business hours (8am-6pm, Mon-Fri)  
   - Measurement: Uptime monitoring, system health checks  
   - Target: <2.2 hours downtime per month  
  
### Constraints  
  
**Hard Constraints** (must be respected):  
  
1. **No Clinical Judgment by AI**: The agent must NOT make clinical decisions about medical necessity, appropriateness of procedures, or alternative treatments. Prior-auth verification is purely administrative (does a valid prior-auth exist for this procedure?).  
  
2. **Human Final Decision Authority**: The agent produces recommendations (Proceed / Reschedule / Escalate), but humans make all final proceed/reschedule decisions. AI cannot auto-approve or auto-reschedule appointments.  
  
3. **HIPAA Compliance**: All patient data access must be logged, encrypted (at rest and in transit), and governed by Business Associate Agreements (BAAs) with all vendors. Access limited to authorized personnel only.  
  
4. **Existing Tech Stack Integration**: Must integrate with athenahealth EHR and existing prior-auth database/system without requiring replacement of core systems.  
  
5. **Audit Trail Requirement**: Every prior-auth check, AI recommendation, and human decision must be traceable with timestamp, user ID, and rationale.  
  
---  
  
## 2. Core Entities and State Machine  
  
### Entity 1: PriorAuthCheck  
  
**Purpose**: Represents a single prior-authorization verification workflow for a scheduled appointment.  
  
**Attributes**:  
```typescript  
{  
  check_id: string (required, unique, format: "PAC-{timestamp}-{patient_id}-{appointment_id}")  
  patient_id: string (required, matches athenahealth patient ID format)  
  appointment_id: string (required, unique, matches athenahealth appointment ID)  
  scheduled_date: date (required, ISO 8601 format)  
  procedure_code: string (required, valid CPT code format: 5 digits)  
  procedure_description: string (optional, human-readable procedure name)  
  insurance_policy_id: string (required, patient's active insurance policy)  
    
  // Status tracking  
  status: enum (required, see state machine below)  
  prior_auth_required: boolean (null until determined, then true/false)  
  prior_auth_status: enum (null | VALID | EXPIRED | EXPIRING_SOON | MISSING | AMBIGUOUS)  
    
  // AI analysis results  
  ai_recommendation: enum (null | PROCEED | RESCHEDULE | ESCALATE)  
  confidence_score: enum (null | HIGH | MEDIUM | LOW)  
  confidence_rationale: string (explanation of confidence score)  
    
  // Human decision  
  human_decision: enum (null | APPROVED | RESCHEDULED | ESCALATED | OVERRIDDEN)  
  human_decision_by: string (user ID of front-desk staff member)  
  human_decision_at: timestamp (when decision was made)  
  human_decision_notes: string (optional, free-text rationale)  
    
  // Audit trail  
  created_at: timestamp (when check was initiated)  
  completed_at: timestamp (when check reached terminal state)  
  last_updated_at: timestamp (last state change)  
  escalation_reason: string (if escalated, specific reason)  
    
  // Related entities  
  prior_auth_records_found: array<string> (IDs of prior-auth records retrieved)  
  matched_prior_auth_id: string (null if no match, ID of matched prior-auth)  
}  
```  
  
**State Machine**:  
  
```  
States:  
  - PENDING_CHECK: Initial state when prior-auth check is triggered  
  - CHECKING: AI is actively querying systems and analyzing data  
  - AWAITING_HUMAN_REVIEW: AI has produced recommendation, waiting for human decision  
  - APPROVED: Human has approved AI recommendation to proceed with appointment  
  - RESCHEDULED: Human has decided to reschedule due to prior-auth issue  
  - ESCALATED: Case escalated for further investigation (prior-auth unclear/missing)  
  - COMPLETED: Prior-auth check completed and documented in EHR (terminal state)  
  - FAILED: System error prevented completion (terminal state, requires manual fallback)  
  
Valid Transitions:  
  - PENDING_CHECK → CHECKING  
    Trigger: Appointment scheduled or patient check-in (48 hours before appointment per A11)  
      
  - CHECKING → AWAITING_HUMAN_REVIEW  
    Trigger: AI completes analysis and generates recommendation  
    Condition: AI successfully retrieved data and produced recommendation  
      
  - CHECKING → ESCALATED  
    Trigger: AI encounters unresolvable ambiguity (confidence = LOW)  
    Condition: Missing data, conflicting information, or multiple prior-auths with no clear match  
      
  - CHECKING → FAILED  
    Trigger: System error (database unavailable, API timeout, EHR write failure)  
    Condition: Technical failure prevents AI from completing analysis  
      
  - CHECKING → COMPLETED  
    Trigger: Prior-auth check determined not required for procedure  
    Condition: Procedure code does not require prior-authorization per insurance policy, or no procedures scheduled  
      
  - AWAITING_HUMAN_REVIEW → APPROVED  
    Trigger: Human reviews AI output and approves "Proceed" recommendation  
    Condition: Human agrees with AI assessment, appointment proceeds as scheduled  
      
  - AWAITING_HUMAN_REVIEW → RESCHEDULED  
    Trigger: Human reviews AI output and decides to reschedule  
    Condition: Prior-auth expired/missing, human decides to wait for new prior-auth  
      
  - AWAITING_HUMAN_REVIEW → ESCALATED  
    Trigger: Human requests further investigation  
    Condition: Human uncertain about AI recommendation, needs more information  
      
  - ESCALATED → AWAITING_HUMAN_REVIEW  
    Trigger: Investigation resolved (staff contacted insurance, obtained clarification)  
    Condition: Ambiguity resolved, human can now make proceed/reschedule decision  
      
  - ESCALATED → COMPLETED  
    Trigger: Investigation completed and decision documented  
    Condition: Complex case resolved, final decision recorded  
      
  - APPROVED → COMPLETED  
    Trigger: Verification documented in EHR  
    Condition: Prior-auth status written to patient record, audit log created  
      
  - RESCHEDULED → COMPLETED  
    Trigger: Reschedule decision documented in EHR  
    Condition: Appointment rescheduled, prior-auth issue noted in patient record  
      
  - FAILED → COMPLETED  
    Trigger: Manual fallback completed  
    Condition: Front-desk staff performed manual prior-auth check, documented result  
  
Invalid Transitions (system must prevent):  
  - COMPLETED → any other state (terminal state, immutable)  
  - FAILED → any state except COMPLETED (cannot retry after failure, must complete manually)  
  - PENDING_CHECK → APPROVED (cannot skip AI analysis and human review)  
  - PENDING_CHECK → RESCHEDULED (cannot skip AI analysis and human review)  
  - AWAITING_HUMAN_REVIEW → CHECKING (cannot go backwards, must escalate if more info needed)  
```  
  
**Relationships**:  
- `PriorAuthCheck` belongs to one `Patient` (via `patient_id`)  
- `PriorAuthCheck` belongs to one `Appointment` (via `appointment_id`)  
- `PriorAuthCheck` references zero or more `PriorAuthRecord` (via `prior_auth_records_found`)  
- `PriorAuthCheck` references zero or one `PriorAuthRecord` (via `matched_prior_auth_id`)  
- `PriorAuthCheck` belongs to one `InsurancePolicy` (via `insurance_policy_id`)  
  
---  
  
### Entity 2: PriorAuthRecord  
  
**Purpose**: Represents a prior-authorization approval record from the insurance company, stored in the prior-auth database.  
  
**Attributes**:  
```typescript  
{  
  prior_auth_id: string (required, unique, format varies by insurance company)  
  patient_id: string (required, matches athenahealth patient ID)  
  insurance_policy_id: string (required, policy under which prior-auth was obtained)  
    
  // Approval details  
  approval_number: string (required, insurance company's approval reference number)  
  approval_date: date (required, when prior-auth was granted)  
  expiration_date: date (required, when prior-auth expires)  
  approval_status: enum (required: ACTIVE | EXPIRED | REVOKED | PENDING)  
    
  // Covered services  
  approved_cpt_codes: array<string> (CPT codes covered by this prior-auth)  
  approved_service_description: string (insurance company's description of approved services)  
  service_category: string (e.g., "imaging", "surgery", "therapy")  
    
  // Limitations  
  approved_units: integer (null if unlimited, otherwise max number of procedures/visits)  
  units_used: integer (how many procedures/visits have been performed under this prior-auth)  
    
  // Source metadata  
  source_system: string (where this record came from: "prior_auth_db" | "insurance_portal" | "manual_entry")  
  last_verified_at: timestamp (when this record was last confirmed with insurance)  
    
  // Audit  
  created_at: timestamp  
  updated_at: timestamp  
}  
```  
  
**State Machine**: Not applicable (PriorAuthRecord is a data entity, not a workflow entity)  
  
**Relationships**:  
- `PriorAuthRecord` belongs to one `Patient` (via `patient_id`)  
- `PriorAuthRecord` belongs to one `InsurancePolicy` (via `insurance_policy_id`)  
- `PriorAuthRecord` can be referenced by multiple `PriorAuthCheck` (one prior-auth can cover multiple appointments)  
  
---  
  
### Entity 3: Appointment  
  
**Purpose**: Represents a scheduled patient visit (sourced from athenahealth EHR).  
  
**Attributes** (subset relevant to prior-auth checking):  
```typescript  
{  
  appointment_id: string (required, unique, athenahealth appointment ID)  
  patient_id: string (required, athenahealth patient ID)  
  scheduled_date: date (required, ISO 8601 format)  
  scheduled_time: time (required)  
  appointment_type: string (e.g., "office_visit", "procedure", "imaging")  
    
  // Procedure details  
  procedure_codes: array<string> (CPT codes for scheduled procedures, can be empty for routine visits)  
  procedure_descriptions: array<string> (human-readable procedure names)  
    
  // Insurance  
  insurance_policy_id: string (patient's active insurance at time of scheduling)  
    
  // Status  
  appointment_status: enum (SCHEDULED | CHECKED_IN | IN_PROGRESS | COMPLETED | CANCELLED)  
    
  // Prior-auth tracking  
  prior_auth_check_id: string (null until check is performed, then links to PriorAuthCheck)  
  prior_auth_verified: boolean (false until check completed)  
  prior_auth_verified_at: timestamp (when verification completed)  
}  
```  
  
**State Machine**: Not applicable (Appointment state machine is owned by EHR, not this capability)  
  
**Relationships**:  
- `Appointment` belongs to one `Patient` (via `patient_id`)  
- `Appointment` has zero or one `PriorAuthCheck` (via `prior_auth_check_id`)  
- `Appointment` belongs to one `InsurancePolicy` (via `insurance_policy_id`)  
  
---  
  
## 3. Core Decision Logic  

**For complete decision logic details, see: [Core Decision Logic](specs/decision-logic.md)**

This section describes the 5-step decision process:
1. **Determine if Prior-Authorization is Required** - Check if procedure requires prior-auth
2. **Locate Prior-Authorization Documentation** - Query prior-auth database
3. **Validate Prior-Authorization Matches Scheduled Procedure** - CPT code matching (exact and fuzzy)
4. **Check Prior-Authorization Expiration Status** - Date validation and expiration warnings
5. **Generate Recommendation and Confidence Score** - Synthesize results into HIGH/MEDIUM/LOW confidence

**Key Decision Points**:
- No prior-auth required → COMPLETED (bypass remaining steps)
- Prior-auth expired → RESCHEDULE (HIGH confidence)
- Prior-auth valid & exact match → PROCEED (HIGH confidence)
- Ambiguous or missing data → ESCALATE (LOW confidence)

---  
  
## 4. What the Agent Should NOT Do  
  
### Clinical Decisions  
  
❌ **The agent must NOT make clinical judgments about whether a procedure is medically necessary**  
- Rationale: Medical necessity determination requires physician expertise and review of clinical context. This violates the "no clinical judgment by AI" constraint.  
- Example: Agent must NOT say "This MRI is unnecessary, recommend canceling appointment"  
  
❌ **The agent must NOT recommend alternative procedures or treatments**  
- Rationale: Treatment decisions are clinical judgments reserved for physicians.  
- Example: Agent must NOT say "CT scan doesn't require prior-auth, recommend switching from MRI to CT"  
  
❌ **The agent must NOT interpret clinical notes to determine appropriate procedure codes**  
- Rationale: CPT code assignment based on clinical documentation is a clinical coding function requiring human expertise.  
- Example: Agent must NOT read physician notes and infer "patient needs CPT 70553" if appointment has no procedure code  
  
❌ **The agent must NOT assess urgency or medical priority of procedures**  
- Rationale: Urgency assessment is clinical judgment (relates to reason-for-visit triage, which is human-led per delegation analysis).  
- Example: Agent must NOT say "This is urgent, proceed without prior-auth"  
  
### Authorization Decisions  
  
❌ **The agent must NOT make final proceed/reschedule decisions without human approval**  
- Rationale: Human-in-loop delegation archetype requires human decision authority. AI recommends, human decides.  
- Example: Agent must NOT auto-reschedule appointments even if prior-auth is expired  
  
❌ **The agent must NOT override human decisions**  
- Rationale: Humans have final authority; AI cannot reverse human judgment.  
- Example: If human approves "Proceed" despite AI recommending "Reschedule," agent must accept human decision and document it  
  
❌ **The agent must NOT contact insurance companies to obtain or expedite prior-authorizations**  
- Rationale: Out of scope (obtaining new prior-auths is manual process); also creates liability risk if AI miscommunicates with insurers.  
- Example: Agent must NOT call insurance company to request prior-auth approval  
  
❌ **The agent must NOT approve procedures without valid prior-auth**  
- Rationale: Agent can only verify existence and validity of prior-auth; cannot grant authorization.  
- Example: Agent must NOT say "Proceed anyway" if prior-auth is missing  
  
### Data Modifications  
  
❌ **The agent must NOT modify prior-auth records in external systems**  
- Rationale: Prior-auth records are source of truth from insurance companies; AI should not alter external data.  
- Example: Agent must NOT update expiration date in prior-auth database  
  
❌ **The agent must NOT delete or archive prior-auth documentation**  
- Rationale: Audit trail and regulatory compliance require preserving all prior-auth records.  
- Example: Agent must NOT delete expired prior-auths from database  
  
❌ **The agent must NOT change appointment dates or times**  
- Rationale: Scheduling is out of scope; human decides to reschedule, scheduling system executes.  
- Example: Agent must NOT move appointment to later date if prior-auth is expiring  
  
❌ **The agent must NOT modify patient insurance information**  
- Rationale: Insurance data is master data in EHR; AI should not alter patient demographics.  
- Example: Agent must NOT change patient's insurance policy ID  
  
### Patient Communication  
  
❌ **The agent must NOT communicate directly with patients about prior-auth status**  
- Rationale: Patient communication requires human judgment, empathy, and ability to answer questions. Also creates liability risk.  
- Example: Agent must NOT send automated email to patient saying "Your prior-auth is expired, appointment cancelled"  
  
❌ **The agent must NOT make promises about coverage or reimbursement**  
- Rationale: Coverage determination is complex and involves insurance company policies; AI should not make guarantees.  
- Example: Agent must NOT tell patient "This procedure is fully covered" even if prior-auth exists (prior-auth ≠ guaranteed payment)  
  
### Rationale Summary  
  
These boundaries exist to:  
1. **Comply with constraints**: "No clinical judgment by AI" and "human final decision authority"  
2. **Manage risk**: Incorrect clinical decisions or patient communication could cause patient harm or legal liability  
3. **Respect scope**: Obtaining prior-auths, scheduling, and patient communication are separate workflows with their own requirements  
4. **Preserve data integrity**: External systems (prior-auth database, EHR) are sources of truth; AI should read, not write  
5. **Meet regulatory requirements**: HIPAA, medical practice regulations, insurance contracts require human accountability for authorization decisions  
  
---  
  
## 5. Handling Ambiguity and Escalation  

**For complete escalation details, see: [Ambiguity and Escalation](specs/ambiguity-and-escalation.md)**

This section defines how the system recognizes ambiguity and when to escalate to humans.

**Types of Ambiguity**:
- **Data Ambiguity**: Multiple prior-auths, vague approval language, missing fields
- **Temporal Ambiguity**: Expiration date within 7 days or on appointment date
- **Matching Ambiguity**: Fuzzy matches, similar but non-matching CPT codes
- **System Ambiguity**: Partial data, database errors
- **Policy Ambiguity**: Unknown practice policies for edge cases

**When to Decide vs. Escalate**:
- **DECIDE (HIGH confidence)**: Complete data, exact CPT match, >7 days until expiration
- **ASK (MEDIUM/LOW confidence)**: Missing data, fuzzy matches, expiring soon, multiple matches, system errors

**Escalation Protocol**:
- Target escalation rate: <20%
- Human actions: Approve Proceed / Reschedule / Investigate / Request Physician Input
- Output includes: all gathered data, AI recommendation, confidence rationale, escalation reason

---

## 11. Assumptions and Open Questions  

**For complete assumptions list, see: [Assumptions and Open Questions](specs/assumptions.md)**

This section catalogs all assumptions made during specification, with validation requirements and criticality levels.

**Assumption Categories**:
- **A1-A10**: From previous delegation analysis (error rates, costs, performance)
- **A11-A35**: Capability-specific assumptions (trigger windows, thresholds, policies)
- **A36-A52**: Buildable assumptions (database types, API specs, architecture decisions)

**Critical Assumptions** (HIGH criticality, require validation):
- **A1**: Prior-auth database has structured data
- **A12**: System response time <2 seconds
- **A15**: Confidence thresholds achieve <20% escalation rate
- **A19**: 50% of patients require prior-auth checks
- **A36**: PostgreSQL database with REST API
- **A37**: Structured prior-auth data (vs. unstructured free-text)

**Tunable Parameters**:
- **A11**: 48-hour trigger window (can adjust 24-72 hours)
- **A14**: 0.8 fuzzy matching threshold
- **A44**: 7-day expiration warning threshold

See [Assumptions](specs/assumptions.md) for complete details including fallback options and validation requirements.

---


## DETAILED DOCUMENTATION  

**For implementation details, refer to separate specification documents:**  

📄 **[Core Decision Logic](specs/decision-logic.md)**  
- Step 1: Determine if Prior-Authorization is Required
- Step 2: Locate Prior-Authorization Documentation
- Step 3: Validate Prior-Authorization Matches Scheduled Procedure
- Step 4: Check Prior-Authorization Expiration Status
- Step 5: Generate Recommendation and Confidence Score

📄 **[Ambiguity and Escalation](specs/ambiguity-and-escalation.md)**  
- Recognizing Ambiguity (Data, Temporal, Matching, System, Policy)
- When to Ask vs. When to Decide
- Escalation Protocol and Human Review Interface
- Escalation Triggers (10 comprehensive conditions)

📄 **[Assumptions and Open Questions](specs/assumptions.md)**  
- Assumptions A1-A10 (from delegation analysis)
- Assumptions A11-A35 (capability-specific)
- Buildable Assumptions A36-A52 (architecture decisions)
- Validation requirements and criticality levels

📄 **[API Specifications](specs/api-specifications.md)**  
- Prior-Auth Database REST API (endpoints, auth, request/response formats)  
- athenahealth EHR API (endpoints, auth, field mappings)  
- Insurance Requirements Database (schema, queries)  
- Fuzzy Matching Algorithm (complete TypeScript implementation)  
- Database Schema (PostgreSQL DDL)  
- Human Review Interface Backend API  
- Error Code Taxonomy  

📄 **[Requirements Specification](specs/requirements.md)**  
- Functional Requirements (REQ-PA-001 through REQ-PA-010)  
- Non-Functional Requirements (Performance, Reliability, Security, Auditability, Scalability)  

📄 **[Edge Cases and Testing](specs/edge-cases-and-testing.md)**  
- Edge Case Scenarios (1-8)  
- Unit-Level Validation (Tests 1-5)  
- Integration Validation (Tests 6-10)  
- End-to-End Validation (Tests 11-15)  
- Acceptance Criteria and Test Data Requirements  

📄 **[Integration Guide](specs/integration-guide.md)**  
- athenahealth EHR Integration  
- Prior-Authorization Database Integration  
- Insurance Eligibility Tool Integration  
- Human Review Interface  

📄 **[Business Case](specs/business-case.md)**  
- Economic Model (Current vs Proposed State Costs)  
- ROI Analysis and Payback Period  
- Sensitivity Analysis  
- Risk Register for Assumptions  

---  

**End of Main Specification**  
