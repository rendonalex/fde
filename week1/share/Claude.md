# Capability Specification: Prior-Authorization Check (PA-CHECK-001)  

**VERSION**: 2.0 (Refactored - Main Spec)  
**LAST UPDATED**: 2026-04-22  

---

**📚 DETAILED DOCUMENTATION**

This is the main specification. For implementation details, see:
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
  
### Step 1: Determine if Prior-Authorization is Required  
  
**Trigger**: Appointment scheduled with procedure code(s) OR patient checks in 48 hours before appointment [per A11]  
  
**Logic**:  
```  
IF appointment.procedure_codes is empty OR null:  
  → prior_auth_required = false  
  → Set status = COMPLETED  
  → Document "No procedures scheduled, prior-auth not applicable"  
  → EXIT  
  
ELSE:  
  FOR EACH procedure_code in appointment.procedure_codes:  
    Query insurance_requirements_database:  
      WHERE insurance_policy_id = appointment.insurance_policy_id  
      AND procedure_code = procedure_code  
      
    IF query returns "prior_auth_required = true":  
      → prior_auth_required = true  
      → PROCEED to Step 2  
      
    IF query returns "prior_auth_required = false":  
      → prior_auth_required = false (for this specific code)  
      → Continue to next procedure_code  
      
    IF query returns no data OR error:  
      → confidence_score = LOW  
      → escalation_reason = "Cannot determine if prior-auth required for CPT {procedure_code}"  
      → Set status = ESCALATED  
      → EXIT (human must investigate)  
  
IF all procedure_codes checked AND none require prior-auth:  
  → prior_auth_required = false  
  → Set status = COMPLETED  
  → Document "Procedures do not require prior-authorization per insurance policy"  
  → EXIT  
```  
  
**Data Sources**:  
- `appointment.procedure_codes` from athenahealth EHR  
- `insurance_requirements_database` (internal or insurance tool API) - maps insurance policies to procedures requiring prior-auth  
  
**Decision**:  
- **Requires prior-auth** → Proceed to Step 2  
- **Does not require prior-auth** → Mark check as COMPLETED, document in EHR, exit  
- **Cannot determine** → Escalate to human (confidence = LOW)  
  
**Assumptions Referenced**:  
- **A11**: Check is triggered 48 hours before appointment to allow time for resolution if issues found  
- **A13**: Assumes insurance requirements database exists and is accessible [per A38, if no API exists, use hardcoded rules fallback]  
  
---  
  
### Step 2: Locate Prior-Authorization Documentation  
  
**Logic**:  
```  
Query prior_auth_database:  
  WHERE patient_id = appointment.patient_id  
  AND insurance_policy_id = appointment.insurance_policy_id  
  AND approval_status = "ACTIVE"  
  AND expiration_date >= appointment.scheduled_date  
  
Store results in prior_auth_records_found[]  
  
IF prior_auth_records_found.length == 0:  
  → prior_auth_status = MISSING  
  → ai_recommendation = ESCALATE  
  → confidence_score = HIGH (high confidence that prior-auth is missing)  
  → escalation_reason = "No active prior-auth found for patient {patient_id}, procedure {procedure_code}"  
  → Set status = AWAITING_HUMAN_REVIEW  
  → EXIT (human decides whether to reschedule or investigate further)  
  
IF prior_auth_records_found.length == 1:  
  → matched_prior_auth_id = prior_auth_records_found[0].prior_auth_id  
  → PROCEED to Step 3 (validate match)  
  
IF prior_auth_records_found.length > 1:  
  → PROCEED to Step 3 (attempt to match, may escalate if ambiguous)  
```  
  
**Data Sources**:  
- `prior_auth_database` (internal database or insurance portal API) [per A1, assumes structured data]  
  
**Decision**:  
- **Prior-auth found (single record)** → Proceed to Step 3 with matched record  
- **Multiple prior-auths found** → Proceed to Step 3, attempt matching logic  
- **No prior-auth found** → Escalate to human (recommend reschedule or investigate)  
  
**Error Handling**:  
```  
IF prior_auth_database query fails (timeout, API error, database unavailable):  
  → Set status = FAILED  
  → escalation_reason = "Prior-auth database unavailable, manual check required"  
  → Notify front-desk staff: "System error - perform manual prior-auth check"  
  → EXIT (manual fallback)  
```  
  
**Assumptions Referenced**:  
- **A1**: Prior-auth database has structured data (approval number, CPT codes, date ranges)  
- **A12**: Prior-auth database response time <2 seconds per query  
- **U4**: Assumes prior-auth database is accessible via API (if not, this step cannot be automated)  
  
---  
  
### Step 3: Validate Prior-Authorization Matches Scheduled Procedure  
  
**Logic** (handles single or multiple prior-auth records):  
  
```  
IF prior_auth_records_found.length == 1:  
  prior_auth = prior_auth_records_found[0]  
    
  // Exact CPT code match  
  IF appointment.procedure_codes[0] IN prior_auth.approved_cpt_codes:  
    → Match confirmed (exact match)  
    → matched_prior_auth_id = prior_auth.prior_auth_id  
    → confidence_score = HIGH  
    → PROCEED to Step 4  
    
  // Fuzzy match on service description  
  ELSE IF fuzzy_match(appointment.procedure_description, prior_auth.approved_service_description) > 0.8:  
    → Match possible but not exact  
    → matched_prior_auth_id = prior_auth.prior_auth_id  
    → confidence_score = MEDIUM  
    → escalation_reason = "Prior-auth CPT codes don't exactly match procedure, but service description similar"  
    → PROCEED to Step 4 (will escalate if other issues found)  
    
  // No match  
  ELSE:  
    → prior_auth_status = AMBIGUOUS  
    → ai_recommendation = ESCALATE  
    → confidence_score = LOW  
    → escalation_reason = "Prior-auth found but CPT code mismatch: prior-auth covers {prior_auth.approved_cpt_codes}, appointment scheduled for {appointment.procedure_codes}"  
    → Set status = AWAITING_HUMAN_REVIEW  
    → EXIT  
  
IF prior_auth_records_found.length > 1:  
  matched_records = []  
    
  FOR EACH prior_auth in prior_auth_records_found:  
    IF appointment.procedure_codes[0] IN prior_auth.approved_cpt_codes:  
      → Add prior_auth to matched_records[]  
    
  IF matched_records.length == 1:  
    → matched_prior_auth_id = matched_records[0].prior_auth_id  
    → confidence_score = HIGH  
    → PROCEED to Step 4  
    
  IF matched_records.length > 1:  
    → prior_auth_status = AMBIGUOUS  
    → ai_recommendation = ESCALATE  
    → confidence_score = LOW  
    → escalation_reason = "Multiple prior-auths found that match procedure: {list approval numbers}"  
    → Set status = AWAITING_HUMAN_REVIEW  
    → EXIT  
    
  IF matched_records.length == 0:  
    → prior_auth_status = AMBIGUOUS  
    → ai_recommendation = ESCALATE  
    → confidence_score = LOW  
    → escalation_reason = "Multiple prior-auths found but none match scheduled procedure CPT code"  
    → Set status = AWAITING_HUMAN_REVIEW  
    → EXIT  
```  
  
**Matching Criteria**:  
1. **Exact CPT code match** (highest confidence): `appointment.procedure_code` exactly matches one of `prior_auth.approved_cpt_codes`  
2. **Fuzzy service description match** (medium confidence): If CPT codes don't match but service descriptions are similar (e.g., "MRI of brain" vs "Brain MRI with contrast")  
3. **No match** (escalate): CPT codes don't match and service descriptions are dissimilar  
  
**Decision**:  
- **Match confirmed (exact CPT match, single prior-auth)** → Proceed to Step 4 with HIGH confidence  
- **Match possible (fuzzy match)** → Proceed to Step 4 with MEDIUM confidence (may escalate later)  
- **Mismatch or multiple matches** → Escalate to human (confidence = LOW)  
  
**Assumptions Referenced**:  
- **A5**: Assumes CPT codes in EHR and prior-auth database use consistent formatting (5-digit codes)  
- **A14**: Fuzzy matching threshold of 0.8 similarity score balances false positives vs false negatives  
  
---  
  
### Step 4: Check Prior-Authorization Expiration Status  
  
**Logic**:  
```  
prior_auth = get_prior_auth_by_id(matched_prior_auth_id)  
  
days_until_expiration = (prior_auth.expiration_date - appointment.scheduled_date).days  
  
IF days_until_expiration < 0:  
  → prior_auth_status = EXPIRED  
  → ai_recommendation = RESCHEDULE  
  → confidence_score = HIGH  
  → confidence_rationale = "Prior-auth expired on {prior_auth.expiration_date}, appointment scheduled for {appointment.scheduled_date}"  
  → Set status = AWAITING_HUMAN_REVIEW  
  → EXIT  
  
IF days_until_expiration == 0:  
  → prior_auth_status = EXPIRING_SOON  
  → ai_recommendation = ESCALATE  
  → confidence_score = MEDIUM  
  → confidence_rationale = "Prior-auth expires on appointment date, recommend human review to assess risk"  
  → escalation_reason = "Prior-auth expires same day as appointment"  
  → Set status = AWAITING_HUMAN_REVIEW  
  → EXIT  
  
IF 0 < days_until_expiration <= 7:  
  → prior_auth_status = EXPIRING_SOON  
  → ai_recommendation = ESCALATE  
  → confidence_score = MEDIUM  
  → confidence_rationale = "Prior-auth expires in {days_until_expiration} days, within warning threshold"  
  → escalation_reason = "Prior-auth expires within 7 days of appointment"  
  → Set status = AWAITING_HUMAN_REVIEW  
  → EXIT  
  
IF days_until_expiration > 7:  
  → prior_auth_status = VALID  
  → ai_recommendation = PROCEED  
  → confidence_score = (HIGH if exact CPT match, MEDIUM if fuzzy match from Step 3)  
  → confidence_rationale = "Prior-auth valid until {prior_auth.expiration_date}, {days_until_expiration} days after appointment"  
  → Set status = AWAITING_HUMAN_REVIEW  
  → EXIT  
```  
  
**Date Logic**:  
- **Expired** (expiration_date < appointment_date): Recommend RESCHEDULE  
- **Expires on appointment date** (expiration_date == appointment_date): Escalate for human judgment [per A43]  
- **Expiring soon** (0 < days_until_expiration ≤ 7): Escalate for human judgment [per A11]  
- **Valid** (days_until_expiration > 7): Recommend PROCEED  
  
**Decision**:  
- **Valid** → Recommend PROCEED (confidence = HIGH or MEDIUM based on Step 3 match quality)  
- **Expired** → Recommend RESCHEDULE (confidence = HIGH)  
- **Expiring soon** → Escalate to human (confidence = MEDIUM)  
  
**Assumptions Referenced**:  
- **A11**: 7-day expiration warning threshold (practice has time to obtain new prior-auth if needed)  
- **Q1**: Practice policy for same-day expiration is unknown; AI escalates for human judgment  
  
---  
  
### Step 5: Generate Recommendation and Confidence Score  
  
**Logic** (synthesizes Steps 1-4):  
  
```  
// Confidence score determination  
IF prior_auth_status == VALID   
   AND exact_cpt_match == true   
   AND days_until_expiration > 7  
   AND no_data_quality_issues:  
  → confidence_score = HIGH  
  → ai_recommendation = PROCEED  
  
IF prior_auth_status == VALID   
   AND (fuzzy_match == true OR days_until_expiration <= 7):  
  → confidence_score = MEDIUM  
  → ai_recommendation = ESCALATE (for human review)  
  
IF prior_auth_status == EXPIRED:  
  → confidence_score = HIGH  
  → ai_recommendation = RESCHEDULE  
  
IF prior_auth_status == MISSING OR AMBIGUOUS:  
  → confidence_score = LOW  
  → ai_recommendation = ESCALATE  
  
IF any_system_errors OR missing_required_data:  
  → confidence_score = LOW  
  → ai_recommendation = ESCALATE  
  
// Generate human-readable summary  
confidence_rationale = generate_summary({  
  prior_auth_status: prior_auth_status,  
  match_quality: (exact_cpt_match ? "Exact CPT match" : "Fuzzy match"),  
  days_until_expiration: days_until_expiration,  
  approval_number: prior_auth.approval_number,  
  approved_services: prior_auth.approved_service_description,  
  data_sources_checked: ["prior_auth_database", "insurance_requirements_db"]  
})  
  
Set status = AWAITING_HUMAN_REVIEW  
```  
  
**Confidence Criteria**:  
  
**HIGH Confidence** (AI recommendation is reliable, human can approve quickly):  
- All required data present and unambiguous  
- Exact CPT code match between prior-auth and procedure  
- Expiration date >7 days after appointment  
- No conflicting information across data sources  
- Single prior-auth record found  
  
**MEDIUM Confidence** (human should review carefully before approving):  
- Fuzzy match on service description (not exact CPT match)  
- Expiration date ≤7 days after appointment (expiring soon)  
- Minor data quality issues (e.g., missing service description but CPT match exists)  
  
**LOW Confidence** (human must investigate further, AI cannot make reliable recommendation):  
- Missing required data (no prior-auth found, no expiration date)  
- Multiple prior-auths with no clear match  
- Conflicting information (database says active, portal says expired)  
- System errors (database unavailable, API timeout)  
  
**Output**: PriorAuthCheck entity with all fields populated, status = AWAITING_HUMAN_REVIEW  
  
**Assumptions Referenced**:  
- **A4**: Assumes human can review HIGH confidence cases in <30 seconds  
- **A15**: Confidence thresholds tuned to achieve <20% escalation rate while maintaining >95% accuracy  
  
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
  
### Recognizing Ambiguity  
  
The agent has encountered ambiguity when any of the following signals are present:  
  
**Data Ambiguity**:  
- Multiple prior-auth records found; matching logic cannot determine which applies to scheduled procedure  
- Prior-auth approval language is vague (e.g., "approved for imaging" but unclear if MRI, CT, X-ray)  
- Conflicting information between prior-auth database and insurance portal (e.g., database says "active," portal says "expired")  
- Missing required data fields (approval number missing, expiration date missing, CPT codes missing)  
  
**Temporal Ambiguity**:  
- Prior-auth expiration date is within 7 days of appointment [per A11] (unclear if practice policy is to proceed or reschedule)  
- Prior-auth expires on the same day as appointment (edge case requiring human judgment [per A43])  
  
**Matching Ambiguity**:  
- Fuzzy match on service description but no exact CPT code match (e.g., prior-auth says "brain imaging," appointment is "MRI brain with contrast")  
- Procedure code in EHR doesn't match any prior-auth on file, but similar codes exist (e.g., prior-auth for CPT 70551, appointment for CPT 70553)  
  
**System Ambiguity**:  
- Prior-auth database returns partial data (some fields populated, others null)  
- Insurance requirements database cannot confirm whether procedure requires prior-auth (no data for this insurance/procedure combination)  
  
**Policy Ambiguity**:  
- Practice policy for edge cases is unknown (e.g., Q1: what to do when prior-auth expires on appointment day?)  
  
---  
  
### When to Ask vs. When to Decide  
  
**The agent should DECIDE (proceed with recommendation) when**:  
  
✅ **All required data is present and unambiguous**:  
- Prior-auth record found with complete fields (approval number, expiration date, CPT codes)  
- Single prior-auth record matches scheduled procedure  
- No conflicting information across data sources  
  
✅ **Prior-auth clearly matches procedure**:  
- Exact CPT code match between `prior_auth.approved_cpt_codes` and `appointment.procedure_codes`  
- Service description confirms match (e.g., both say "MRI brain")  
  
✅ **Expiration date is >7 days after scheduled appointment** [per A11]:  
- Sufficient time buffer; no risk of expiration before appointment  
- Example: Appointment on Jan 15, prior-auth expires Jan 30 → DECIDE (recommend PROCEED)  
  
✅ **Confidence score = HIGH**:  
- All criteria above met  
- No data quality issues  
- No system errors  
  
✅ **No conflicting information across data sources**:  
- Prior-auth database and insurance portal agree on status  
- EHR appointment details match prior-auth records  
  
**Example scenarios where agent should DECIDE**:  
1. Prior-auth found, exact CPT match, expires in 30 days → **DECIDE: Recommend PROCEED (HIGH confidence)**  
2. Prior-auth expired 10 days ago, clear expiration date → **DECIDE: Recommend RESCHEDULE (HIGH confidence)**  
3. No prior-auth found in database, procedure typically requires prior-auth → **DECIDE: Recommend ESCALATE (HIGH confidence that prior-auth is missing)**  
  
---  
  
**The agent should ASK (escalate to human) when**:  
  
⚠️ **Any required data field is missing or unclear**:  
- Prior-auth found but expiration date is null  
- Prior-auth found but approved CPT codes field is empty  
- Cannot determine if procedure requires prior-auth (insurance requirements database has no data)  
  
⚠️ **Prior-auth approval language doesn't exactly match procedure description**:  
- Prior-auth says "approved for imaging," appointment is "MRI brain with contrast"  
- Prior-auth CPT code is 70551 (MRI without contrast), appointment CPT is 70553 (MRI with contrast)  
- Fuzzy match score <0.8 (service descriptions are dissimilar)  
  
⚠️ **Multiple prior-auths found; matching logic cannot determine which applies**:  
- Patient has 3 active prior-auths for different imaging procedures  
- Two prior-auths both cover CPT 70553 (unclear which to use)  
  
⚠️ **Expiration date is ≤7 days from appointment** [per A11]:  
- Prior-auth expires in 5 days, appointment in 5 days (edge case)  
- Prior-auth expires on same day as appointment (policy resolved [per A43]: escalate to human for judgment)  
  
⚠️ **Confidence score = MEDIUM or LOW**:  
- Some ambiguity present (fuzzy match, expiring soon, minor data issues)  
- Agent uncertain about recommendation  
  
⚠️ **Conflicting information detected**:  
- Prior-auth database says "active," insurance portal says "expired"  
- EHR shows procedure CPT 70553, prior-auth database shows approval for CPT 70551  
- Approval date is after expiration date (data quality issue)  
  
⚠️ **System errors**:  
- Prior-auth database unavailable (timeout, API error)  
- Insurance requirements database returns error  
- EHR write fails (cannot document verification result)  
  
**Example scenarios where agent should ASK**:  
1. Prior-auth expires in 3 days, appointment in 5 days → **ASK: Escalate for human judgment (MEDIUM confidence)**  
2. Two prior-auths found, both cover "imaging" but unclear which applies → **ASK: Escalate for human to select correct prior-auth (LOW confidence)**  
3. Prior-auth says "approved for imaging," appointment is "MRI brain with contrast" → **ASK: Escalate for human to confirm match (MEDIUM confidence)**  
4. Prior-auth database unavailable → **ASK: Escalate for manual fallback (system error)**  
  
---  
  
### Escalation Protocol  
  
**When the agent escalates, it must provide the following information to the human reviewer**:  
  
**Escalation Output Structure**:  
```  
=== PRIOR-AUTH CHECK ESCALATION ===  
  
Patient: {patient_name} (ID: {patient_id})  
Appointment: {scheduled_date} at {scheduled_time}  
Procedure: {procedure_description} (CPT: {procedure_code})  
  
ESCALATION REASON:  
{specific_reason_for_escalation}  
  
DATA GATHERED:  
  Prior-Auth Records Found: {count}  
    
  [For each prior-auth record:]  
  - Approval Number: {approval_number}  
  - Approved Services: {approved_service_description}  
  - Approved CPT Codes: {approved_cpt_codes}  
  - Expiration Date: {expiration_date}  
  - Days Until Expiration: {days_until_expiration}  
  - Status: {approval_status}  
    
  Scheduled Procedure:  
  - CPT Code: {procedure_code}  
  - Description: {procedure_description}  
  - Date: {scheduled_date}  
    
  Ambiguity Detected:  
  {specific_description_of_what_is_unclear}  
    
  Data Sources Checked:  
  - Prior-auth database: {status}  
  - Insurance requirements database: {status}  
  - Insurance portal: {status if queried}  
  
AI RECOMMENDATION (LOW/MEDIUM CONFIDENCE):  
{ai_recommendation: PROCEED | RESCHEDULE | ESCALATE}  
  
Confidence Score: {confidence_score}  
Confidence Rationale: {confidence_rationale}  
  
HUMAN ACTIONS AVAILABLE:  
[ ] Approve Proceed - Override ambiguity, accept risk, proceed with appointment  
[ ] Reschedule - Wait for clarification or new prior-auth  
[ ] Investigate Further - Contact insurance, review additional documentation  
[ ] Request Physician Input - Clinical judgment needed  
  
NOTES:  
{any_additional_context}  
```  
  
**Human Review Interface** (front-desk staff sees):  
- Clear summary of issue (why escalated)  
- All data gathered by AI (prior-auth records, appointment details)  
- AI's best assessment (even if low confidence)  
- Action buttons: Approve / Reschedule / Investigate / Request Physician Input  
- Free-text field for human to document decision rationale  
  
**Human Actions**:  
  
1. **Approve Proceed**: Human decides to proceed with appointment despite ambiguity  
   - Use case: Prior-auth expires in 6 days, human judges risk is acceptable  
   - System records: `human_decision = APPROVED`, `human_decision_notes = "Proceeding despite expiring soon, patient needs procedure urgently"`  
  
2. **Reschedule**: Human decides to reschedule appointment  
   - Use case: Prior-auth expired, human will obtain new prior-auth before rescheduling  
   - System records: `human_decision = RESCHEDULED`, `human_decision_notes = "Prior-auth expired, rescheduling after new prior-auth obtained"`  
  
3. **Investigate Further**: Human needs more information before deciding  
   - Use case: Multiple prior-auths found, human will call insurance to clarify which applies  
   - System records: `human_decision = ESCALATED`, `escalation_reason = "Contacting insurance to clarify which prior-auth applies"`  
   - Workflow: Case remains in ESCALATED state until investigation complete, then returns to AWAITING_HUMAN_REVIEW  
  
4. **Request Physician Input**: Human needs physician to weigh in  
   - Use case: Unclear if procedure is medically necessary, physician should decide  
   - System records: `human_decision = ESCALATED`, `escalation_reason = "Physician input requested on medical necessity"`  
   - Workflow: Physician reviews, provides guidance, human makes final decision  
  
---  
  
### Escalation Triggers (Comprehensive List)  
  
**Automatic Escalation Conditions** (agent sets status = AWAITING_HUMAN_REVIEW or ESCALATED):  
  
1. **No prior-auth found in system AND procedure typically requires prior-auth**  
   - Confidence: HIGH (high confidence prior-auth is missing)  
   - Recommendation: ESCALATE  
   - Human action: Investigate (check if prior-auth was obtained but not entered in system) or Reschedule  
  
2. **Prior-auth found but expired** (expiration_date < appointment_date)  
   - Confidence: HIGH (clear expiration)  
   - Recommendation: RESCHEDULE  
   - Human action: Usually reschedule, but can override if urgent  
  
3. **Prior-auth expiring within 7 days of appointment** [per A11]  
   - Confidence: MEDIUM (unclear if practice policy is to proceed or reschedule)  
   - Recommendation: ESCALATE  
   - Human action: Assess risk, decide proceed or reschedule  
  
4. **Multiple prior-auths on file; cannot determine which applies**  
   - Confidence: LOW (ambiguous)  
   - Recommendation: ESCALATE  
   - Human action: Review prior-auth details, select correct one, or contact insurance  
  
5. **Prior-auth CPT code doesn't match scheduled procedure CPT code**  
   - Confidence: LOW (mismatch)  
   - Recommendation: ESCALATE  
   - Human action: Verify procedure code is correct, or determine if prior-auth covers similar procedure  
  
6. **Prior-auth approval language is ambiguous** (e.g., "approved for imaging" but unclear which type)  
   - Confidence: LOW (vague language)  
   - Recommendation: ESCALATE  
   - Human action: Contact insurance for clarification, or proceed if confident procedure is covered  
  
7. **Data quality issues** (missing approval number, missing expiration date, contradictory dates)  
   - Confidence: LOW (incomplete data)  
   - Recommendation: ESCALATE  
   - Human action: Investigate data source, contact insurance to obtain missing information  
  
8. **Prior-auth database unavailable or returns error**  
   - Confidence: N/A (system error)  
   - Status: FAILED  
   - Human action: Perform manual prior-auth check (fallback workflow)  
  
9. **Conflicting information between data sources** (database says "active," portal says "expired")  
   - Confidence: LOW (conflicting data)  
   - Recommendation: ESCALATE  
   - Human action: Contact insurance to resolve conflict, use most recent data source  
  
10. **Confidence score = LOW** (agent uncertainty exceeds threshold)  
    - Any scenario where agent cannot make reliable recommendation  
    - Human action: Review all data, make judgment call  
  
**Escalation Rate Target**: <20% of prior-auth checks should escalate [per success criteria]  
  
**Tuning**: If escalation rate exceeds 20%, review escalation triggers and adjust thresholds (e.g., reduce expiration warning from 7 days to 5 days) [per A15]  
  
---  
  

---

## 11. Assumptions and Open Questions  
  
### Assumptions (Continued from Delegation Analysis)  
  
**From Previous Analysis** (A1-A10):  
- A1: Prior-auth database has structured data (approval number, CPT codes, date ranges)  
- A2: Current error rate is 3% (8% overall intake errors, prior-auth is "most common" type)  
- A3: Manual prior-auth check takes 2.5 min per patient  
- A4: Front-desk staff can review AI output in <30 seconds for HIGH confidence cases  
- A5: Front-desk staff hourly cost is $22/hour  
- A6: Physician hourly cost is $120/hour  
- A7: Token cost per intake is $0.08 total (allocated across all 6 intake steps)  
- A8: Human oversight time with AI assistance is 0.5 min per patient  
- A9: Target error rate is 0.75% (75% reduction from current 3%)  
- A10: Implementation and maintenance costs (estimated in economic model)  
  
**New Assumptions for This Capability** (A11-A35):  
  
**A11: Prior-Auth Check Trigger Window**  
- **Value**: 48 hours before appointment  
- **Reasoning**: Gives practice time to resolve issues (contact insurance, obtain new prior-auth, reschedule) before patient arrives  
- **Criticality**: Medium (affects when checks run, but can be tuned)  
- **Validation Required**: Yes (practice may prefer 24 hours or 72 hours)  
  
**A12: System Response Time**  
- **Value**: Prior-auth database response time <2 seconds, EHR API response time <2 seconds  
- **Reasoning**: Allows total prior-auth check to complete in <10 seconds (includes all steps: EHR read, database query, matching logic, EHR write)  
- **Criticality**: High (affects performance requirement feasibility)  
- **Validation Required**: Yes (must test actual database and EHR API performance)  
  
**A13: Manual Fallback Acceptability**  
- **Value**: Manual fallback is acceptable when system errors occur  
- **Reasoning**: Practice already performs manual prior-auth checks today; manual fallback preserves workflow continuity  
- **Criticality**: Medium (affects error handling design)  
- **Validation Required**: No (reasonable assumption given current state)  
  
**A14: Fuzzy Matching Threshold**  
- **Value**: 0.8 similarity score (Levenshtein distance or cosine similarity)  
- **Reasoning**: Balances false positives (matching dissimilar procedures) vs false negatives (missing valid matches)  
- **Criticality**: Medium (affects matching accuracy, but can be tuned)  
- **Validation Required**: Yes (must test with real prior-auth data to optimize threshold)  
  
**A15: Confidence Score Thresholds**  
- **Value**: HIGH confidence when exact CPT match + valid expiration + complete data; MEDIUM when fuzzy match or expiring soon; LOW when missing data or ambiguous  
- **Reasoning**: Tuned to achieve <20% escalation rate while maintaining >95% accuracy  
- **Criticality**: High (affects escalation rate and human workload)  
- **Validation Required**: Yes (must tune thresholds based on production data)  
  
**A16: Audit Log Retention Period**  
- **Value**: 7 years  
- **Reasoning**: Aligns with medical records retention requirements (HIPAA and state regulations)  
- **Criticality**: High (regulatory compliance requirement)  
- **Validation Required**: No (standard healthcare requirement)  
  
**A17: Staff Training on Manual Checks**  
- **Value**: Front-desk staff are trained to perform manual prior-auth checks  
- **Reasoning**: Existing skill (practice performs manual checks today)  
- **Criticality**: Medium (affects manual fallback feasibility)  
- **Validation Required**: Yes (confirm staff can perform manual checks when system fails)  
  
**A18: State Machine Enforcement Prevents Data Corruption**  
- **Value**: Enforcing valid state transitions ensures workflow integrity  
- **Reasoning**: Invalid transitions (e.g., COMPLETED → CHECKING) indicate bugs or data corruption  
- **Criticality**: High (affects data integrity and audit trail)  
- **Validation Required**: No (standard software engineering practice)  
  
**A19: Prior-Auth Volume**  
- **Value**: 50% of patients require prior-auth checks (90 checks/day out of 180 patients)  
- **Reasoning**: Was unknown [U3], resolved with A47 using 50% as placeholder for economic model  
- **Criticality**: High (affects throughput requirements and ROI)  
- **Validation Required**: Yes (must validate during discovery - actual volume may be 30% or 70%)  
  
**A20: Uptime Requirement**  
- **Value**: 99% uptime is acceptable (non-critical administrative workflow)  
- **Reasoning**: Prior-auth verification is not life-critical; manual fallback exists  
- **Criticality**: Medium (affects infrastructure design and cost)  
- **Validation Required**: Yes (practice may require higher uptime)  
  
**A21: Existing BAA with athenahealth**  
- **Value**: Practice has existing Business Associate Agreement with athenahealth (EHR vendor)  
- **Reasoning**: Required for HIPAA compliance; standard for EHR vendors  
- **Criticality**: High (legal requirement for patient data access)  
- **Validation Required**: Yes (must confirm BAA is in place and covers API access)  
  
**A22: Cloud Hosting Provider is HIPAA-Compliant**  
- **Value**: AWS, Azure, or GCP is HIPAA-compliant and has signed BAA  
- **Reasoning**: Major cloud providers offer HIPAA-compliant infrastructure  
- **Criticality**: High (regulatory requirement)  
- **Validation Required**: Yes (must select HIPAA-compliant hosting and sign BAA)  
  
**A23: Audit Logs Stored Separately**  
- **Value**: Audit logs stored in separate database (not same as operational data)  
- **Reasoning**: Security best practice (prevents tampering with audit trail)  
- **Criticality**: Medium (affects database architecture)  
- **Validation Required**: No (standard security practice)  
  
**A24: Practice Growth Projection**  
- **Value**: Practice may grow from 6 to 12 physicians in next 3 years (2× volume)  
- **Reasoning**: Scalability requirement (system must handle future growth)  
- **Criticality**: Low (affects long-term architecture, not initial launch)  
- **Validation Required**: Yes (confirm growth projections with practice manager)  
  
**A25: Cloud Infrastructure Scalability**  
- **Value**: Cloud infrastructure (AWS, Azure, GCP) provides horizontal scaling  
- **Reasoning**: Standard cloud capability (add more servers to handle increased load)  
- **Criticality**: Low (affects long-term scalability)  
- **Validation Required**: No (standard cloud feature)  
  
**A26: Multiple Prior-Auths per Patient**  
- **Value**: Patients may have multiple active prior-auths for different procedures  
- **Reasoning**: Common for patients with chronic conditions (e.g., cancer patient with prior-auths for chemo, imaging, surgery)  
- **Criticality**: Medium (affects matching logic complexity)  
- **Validation Required**: Yes (confirm how often this occurs in practice)  
  
**A27: Human Review Time for Multiple Prior-Auths**  
- **Value**: Human can review multiple prior-auths and select correct one in <2 minutes  
- **Reasoning**: Front-desk staff are familiar with prior-auth details  
- **Criticality**: Low (affects escalation handling time)  
- **Validation Required**: Yes (time-motion study during pilot)  
  
**A28: Human Can Contact Insurance for Clarification**  
- **Value**: Front-desk staff can contact insurance companies to clarify vague approval language  
- **Reasoning**: Existing practice workflow (staff call insurance when needed)  
- **Criticality**: Medium (affects escalation resolution process)  
- **Validation Required**: Yes (confirm staff have access to insurance contact info and authority to call)  
  
**A29: Prior-Auth Database Downtime is Rare**  
- **Value**: <1% of checks affected by database downtime  
- **Reasoning**: Prior-auth database is critical system, likely has high uptime  
- **Criticality**: Medium (affects manual fallback frequency)  
- **Validation Required**: Yes (measure actual database uptime during pilot)  
  
**A30: Human Can Assess CPT Code Mismatch**  
- **Value**: Front-desk staff can determine if CPT code mismatch is acceptable (e.g., both codes covered under same prior-auth)  
- **Reasoning**: Staff have experience with CPT codes and insurance policies  
- **Criticality**: Medium (affects escalation resolution)  
- **Validation Required**: Yes (confirm staff knowledge of CPT codes)  
  
**A31: EHR Maintains Accurate Current Insurance**  
- **Value**: athenahealth EHR maintains accurate current insurance policy for each patient  
- **Reasoning**: Insurance information is master data in EHR, updated by front-desk staff  
- **Criticality**: High (affects prior-auth query accuracy)  
- **Validation Required**: Yes (audit EHR insurance data quality)  
  
**A32: Prior-Auth Database Links to Insurance Policies**  
- **Value**: Prior-auth database links prior-auths to specific insurance policies (not just patient_id)  
- **Reasoning**: Prior-auths are policy-specific (not transferable between policies)  
- **Criticality**: High (affects query logic)  
- **Validation Required**: Yes (confirm prior-auth database schema includes insurance_policy_id)  
  
**A33: Human Can Update Prior-Auth Database**  
- **Value**: Front-desk staff can update prior-auth database when missing data is obtained from insurance  
- **Reasoning**: Data quality maintenance requires human intervention  
- **Criticality**: Medium (affects data quality improvement process)  
- **Validation Required**: Yes (confirm staff have write access to prior-auth database)  
  
**A34: Multiple Procedure Codes per Appointment**  
- **Value**: Appointments may have multiple procedure codes (e.g., MRI Brain + MRI Spine in same visit)  
- **Reasoning**: Common for imaging studies (multiple body parts scanned in one visit)  
- **Criticality**: Medium (affects check logic complexity)  
- **Validation Required**: Yes (confirm how often this occurs, affects scope)  
  
**A35: Prior-Auth Database Indicates Covered Procedures**  
- **Value**: Prior-auth database has `approved_cpt_codes[]` array indicating which procedures are covered  
- **Reasoning**: Necessary for matching logic (must know what prior-auth covers)  
- **Criticality**: High (affects matching feasibility)  
- **Validation Required**: Yes (confirm prior-auth database schema includes CPT codes)  
  
---  
  
### BUILDABLE ASSUMPTIONS (A36-A52)  
  
**NOTE**: The following assumptions were added to resolve ambiguities and make the specification buildable. These are marked as ⚠️ **ASSUMPTIONS** and must be validated during discovery. If actual implementation differs, refactoring may be required.  
  
**A36: Prior-Auth Database System Type** ⚠️ **ASSUMPTION**  
- **Assumed Value**: Internal PostgreSQL database with REST API wrapper  
- **Reasoning**: Most flexible architecture; allows direct SQL queries for initial implementation and REST API for long-term maintainability  
- **Alternative**: If actual system is third-party (Availity, Change Healthcare), API integration approach remains similar (HTTP/JSON)  
- **Criticality**: HIGH - Wrong assumption requires integration layer rewrite  
- **Validation Required**: YES - Must confirm during discovery; if different, see "Fallback Options" below  
- **Fallback Options**:  
  - If insurance portal API: Adapt REST client to portal endpoints  
  - If no API exists: Phase 1 = manual fallback only; automated check deferred to Phase 2  
  
**A37: Prior-Auth Database Data Structure** ⚠️ **ASSUMPTION**  
- **Assumed Value**: Structured data with separate fields (approval_number, expiration_date, approved_cpt_codes[])  
- **Reasoning**: A1 assumes structured data; this confirms specific schema design  
- **Alternative**: If unstructured (free-text notes), requires NLP parsing layer (adds complexity and error rate)  
- **Criticality**: HIGH - Unstructured data reduces matching accuracy to ~70% (vs 95% structured)  
- **Validation Required**: YES - Inspect actual prior-auth records during discovery  
- **Fallback Options**:  
  - If semi-structured: Use structured fields where available, escalate when only free-text  
  - If fully unstructured: Defer to Phase 2; implement basic keyword matching for MVP  
  
**A38: Insurance Requirements Database Implementation** ⚠️ **ASSUMPTION**  
- **Assumed Value**: Internal mapping table (PostgreSQL) linking insurance_policy_id + procedure_code → prior_auth_required (boolean)  
- **Reasoning**: Simplest approach for MVP; practice can maintain their own mappings  
- **Alternative**: Use hardcoded rules for top 80% of procedures (CPT 70000-79999 = imaging = require prior-auth)  
- **Criticality**: MEDIUM - Fallback to hardcoded rules is acceptable for MVP  
- **Validation Required**: YES - If no database exists, use hardcoded rules approach  
- **Fallback Options**:  
  - If no database: Use hardcoded rules (see A38a below)  
  - If external API available: Integrate with API instead of internal table  
  
**A38a: Hardcoded Prior-Auth Requirement Rules** (if A38 database doesn't exist)  
```typescript  
// Default rules if insurance requirements database unavailable  
function requiresPriorAuth(cptCode: string, insurancePolicyId: string): boolean {  
  const cptNum = parseInt(cptCode);  
  
  // Imaging procedures (CPT 70000-79999): Require prior-auth  
  if (cptNum >= 70000 && cptNum <= 79999) return true;  
  
  // Surgical procedures (CPT 10000-69999): Require prior-auth  
  if (cptNum >= 10000 && cptNum <= 69999) return true;  
  
  // Office visits (CPT 99201-99499): Do NOT require prior-auth  
  if (cptNum >= 99201 && cptNum <= 99499) return false;  
  
  // Unknown: Escalate to human  
  return null; // null = cannot determine, escalate  
}  
```  
  
**A39: athenahealth API Specification** ⚠️ **ASSUMPTION**  
- **Assumed Value**: REST API with OAuth 2.0 authentication, JSON payloads  
- **Reasoning**: Based on athenahealth's publicly documented API patterns  
- **Criticality**: MEDIUM - athenahealth API is well-documented; assumptions are safe  
- **Validation Required**: YES - Review actual API documentation and credentials during setup  
- **See**: New "API Specifications" section below for detailed endpoint definitions  
  
**A40: Fuzzy Matching Algorithm** ⚠️ **ASSUMPTION**  
- **Assumed Value**: Levenshtein distance with normalization (lowercase, remove punctuation)  
- **Reasoning**: Simple, deterministic, well-understood; threshold of 0.8 maps to "80% character similarity"  
- **Alternative**: Cosine similarity with TF-IDF (more complex, similar results)  
- **Criticality**: LOW - Easy to swap algorithms if needed  
- **Validation Required**: YES - Tune threshold based on real prior-auth data during pilot  
- **Implementation**: See algorithm specification in new section below  
  
**A41: Human Review Interface Architecture** ⚠️ **ASSUMPTION**  
- **Assumed Value**: Standalone web dashboard (React SPA) accessed via browser  
- **Reasoning**: Faster to build, no athenahealth widget SDK required; staff can access via URL  
- **Alternative**: Embedded EHR widget (Phase 2 enhancement)  
- **Criticality**: MEDIUM - Architecture differs significantly; plan for potential Phase 2 refactor  
- **Validation Required**: YES - Confirm with practice staff which approach they prefer  
- **Tradeoff**: Standalone = context switching (EHR → dashboard); Embedded = seamless but more complex  
  
**A42: Authentication and Authorization** ⚠️ **ASSUMPTION**  
- **Assumed Value**: All front-desk staff can review and override AI recommendations (no RBAC required for MVP)  
- **Reasoning**: Simplifies implementation; audit trail tracks who made decisions  
- **Alternative**: Role-based access control (office manager only can override HIGH confidence cases)  
- **Criticality**: LOW - Can add RBAC in Phase 2 if needed  
- **Validation Required**: YES - Confirm practice policy on who can override  
  
**A43: Same-Day Expiration Policy** ⚠️ **ASSUMPTION**  
- **Assumed Value**: Escalate to human for judgment (confidence = MEDIUM)  
- **Reasoning**: Conservative approach; practice policy unknown  
- **Alternative**: Auto-reschedule (more aggressive) or auto-proceed (more permissive)  
- **Criticality**: LOW - Business rule, easy to change  
- **Validation Required**: YES - Ask practice manager for policy  
  
**A44: Expiration Warning Threshold** ⚠️ **ASSUMPTION**  
- **Assumed Value**: 7 days (escalate if prior-auth expires within 7 days of appointment)  
- **Reasoning**: Gives practice one week to obtain new prior-auth if needed  
- **Alternative**: 14 days (more conservative) or 3 days (more aggressive)  
- **Criticality**: LOW - Tunable parameter  
- **Validation Required**: YES - Tune based on practice feedback during pilot  
  
**A45: Multiple Procedures Handling** ⚠️ **ASSUMPTION**  
- **Assumed Value**: Create separate `PriorAuthCheck` for each procedure code (independent checks)  
- **Reasoning**: Ensures each procedure is verified; frequency unknown but safe default  
- **Alternative**: Single check covering all procedures (simpler but less granular)  
- **Criticality**: LOW - Logic handles both cases  
- **Validation Required**: YES - Measure frequency during pilot; optimize if >30% of appointments  
  
**A46: Re-Verification on Reschedule** ⚠️ **ASSUMPTION**  
- **Assumed Value**: Create new `PriorAuthCheck` if appointment rescheduled >7 days out (expiration status may change)  
- **Reasoning**: Expiration date relative to appointment date changes when appointment moves  
- **Alternative**: Always re-verify OR never re-verify (reuse existing check)  
- **Criticality**: LOW - Business rule, easy to change  
- **Validation Required**: YES - Confirm with practice workflow  
  
**A47: Prior-Auth Volume** ⚠️ **ASSUMPTION**  
- **Assumed Value**: 50% of patients require prior-auth checks (90 checks/day out of 180 patients)  
- **Reasoning**: Unknown [per U3]; 50% is midpoint estimate for economic modeling  
- **Alternative**: Could be 30% (54 checks/day) or 70% (126 checks/day)  
- **Criticality**: HIGH - Affects ROI and infrastructure sizing  
- **Validation Required**: YES - Measure actual volume during first week of pilot  
- **Impact**: See sensitivity analysis (Section 12); ROI remains positive even at 30% volume  
  
**A48: Actual Error Rate** ⚠️ **ASSUMPTION**  
- **Assumed Value**: 3% current error rate for prior-auth checks  
- **Reasoning**: Scenario states 8% overall intake errors, prior-auth is "most common" type  
- **Alternative**: Could be 2% (less severe) or 5% (more severe)  
- **Criticality**: MEDIUM - Affects ROI but not implementation  
- **Validation Required**: YES - Measure baseline error rate before deploying AI  
- **Impact**: See sensitivity analysis; higher error rate = stronger ROI  
  
**A49: Date/Time Format Specification** ⚠️ **ASSUMPTION**  
- **Assumed Value**:  
  - Dates: ISO 8601 `YYYY-MM-DD` (e.g., "2025-01-15")  
  - Timestamps: ISO 8601 `YYYY-MM-DDTHH:MM:SSZ` in UTC (e.g., "2025-01-15T14:30:00Z")  
  - Timezone: All calculations in practice local time (convert UTC to local for display)  
- **Reasoning**: Industry standard; unambiguous; handles DST correctly  
- **Criticality**: LOW - Standard approach  
- **Validation Required**: NO - Safe assumption  
  
**A50: Physician Notification** ⚠️ **ASSUMPTION**  
- **Assumed Value**: No physician notification for escalated cases (front-desk staff handles all escalations)  
- **Reasoning**: Keeps physicians focused on clinical work; front-desk resolves administrative issues  
- **Alternative**: Email/EHR message to physician when prior-auth missing (Phase 2 enhancement)  
- **Criticality**: LOW - Workflow preference  
- **Validation Required**: YES - Confirm with physicians and practice manager  
  
**A51: Database Platform** ⚠️ **ASSUMPTION**  
- **Assumed Value**: PostgreSQL 14+ for operational database and audit logs  
- **Reasoning**: HIPAA-compliant, excellent JSON support, mature ecosystem  
- **Alternative**: MySQL, SQL Server, MongoDB  
- **Criticality**: LOW - Schema is portable across SQL databases  
- **Validation Required**: NO - Safe choice; practice may have existing PostgreSQL infrastructure  
  
**A52: Cloud Infrastructure** ⚠️ **ASSUMPTION**  
- **Assumed Value**: AWS (Amazon Web Services) with HIPAA BAA  
- **Reasoning**: Most popular cloud provider, comprehensive HIPAA compliance, mature services  
- **Alternative**: Azure (good for Microsoft shops), GCP (good for AI/ML)  
- **Criticality**: LOW - Architecture is cloud-agnostic  
- **Validation Required**: YES - Confirm practice has existing cloud provider preference  
  
---  
  

---


## DETAILED DOCUMENTATION  

**For implementation details, refer to separate specification documents:**  

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
