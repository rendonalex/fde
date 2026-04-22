# Integration Guide: Prior-Authorization Check

**Parent Spec**: [../Claude.md](../Claude.md)  
**Version**: 2.0  
**Last Updated**: 2026-04-22  

---

## Overview

This document describes all integration points for the Prior-Authorization Check capability, including:
- athenahealth EHR integration (read appointments, write verification results)
- Prior-Authorization Database integration (query prior-auth records)
- Insurance Eligibility Tool integration (determine if prior-auth required)
- Human Review Interface (display AI output, capture decisions)

**Referenced by**: Claude.md Section 3 (Core Decision Logic) and Assumptions A36-A41

---

## Table of Contents

1. [athenahealth EHR Integration](#athenahealth-ehr-integration)
2. [Prior-Authorization Database Integration](#prior-authorization-database-integration)
3. [Insurance Eligibility Tool Integration](#insurance-eligibility-tool-integration)
4. [Human Review Interface](#human-review-interface)

---

## athenahealth EHR Integration  

**Purpose**: Read appointment data, write prior-auth verification results  

**Data Read from EHR**:  
- `Appointment` entity:  
  - `appointment_id`, `patient_id`, `scheduled_date`, `scheduled_time`  
  - `procedure_codes[]`, `procedure_descriptions[]`  
  - `insurance_policy_id`  
  - `appointment_status`  
- `Patient` entity:  
  - `patient_id`, `patient_name`, `date_of_birth`  
  - `active_insurance_policy_id`  

**Data Written to EHR**:  
- `PriorAuthCheck` summary note in appointment record:  
  - Prior-auth verification status (VALID | EXPIRED | MISSING | etc.)  
  - AI recommendation (PROCEED | RESCHEDULE | ESCALATE)  
  - Human decision (APPROVED | RESCHEDULED | ESCALATED)  
  - Timestamp of verification  
  - Matched prior-auth approval number (if found)  
- Update `appointment.prior_auth_verified = true` and `appointment.prior_auth_verified_at = {timestamp}`  

**API Endpoints** (athenahealth API):  
- `GET /appointments/{appointment_id}` - Retrieve appointment details  
- `GET /patients/{patient_id}` - Retrieve patient demographics and insurance  
- `POST /appointments/{appointment_id}/notes` - Write prior-auth verification note  
- `PUT /appointments/{appointment_id}` - Update prior-auth verification flag  

**Authentication & Authorization**:  
- OAuth 2.0 authentication with athenahealth API  
- Service account with read access to appointments/patients, write access to appointment notes  
- API key stored in secure credential vault (not hardcoded)  

**Error Handling**:  
```  
IF athenahealth API call fails (timeout, 500 error, authentication failure):  
  - Log error with details (endpoint, error code, timestamp)  
  - Retry up to 3 times with exponential backoff (1s, 2s, 4s)  
  - If all retries fail:  
    → Set status = FAILED  
    → Notify front-desk staff: "EHR unavailable, perform manual prior-auth check"  
    → Create manual fallback task in queue  

IF athenahealth API returns 404 (appointment not found):  
  - Log error: "Appointment {appointment_id} not found in EHR"  
  - Set status = FAILED  
  - Notify system admin (potential data sync issue)  

IF athenahealth API write fails (cannot document verification result):  
  - Complete prior-auth check in memory  
  - Store result in local database (fallback)  
  - Retry EHR write every 5 minutes until successful  
  - Alert staff if EHR write fails for >1 hour  
```  

**Assumptions Referenced**:  
- **U5**: Assumes athenahealth API access is enabled and practice has API credentials (must validate during discovery)  
- **A12**: Assumes EHR API response time <2 seconds (affects overall 10-second performance target)  

**See also**: [api-specifications.md](api-specifications.md) Section 2 for complete API contracts

---  

## Prior-Authorization Database Integration  

**Purpose**: Query prior-auth records, retrieve approval details  

**System Type**: Assumed [per A36] to be internal PostgreSQL with REST API wrapper. Could alternatively be:  
- Internal database (practice maintains prior-auth records)  
- Insurance portal API (query insurer's system directly)  
- Third-party prior-auth management tool (e.g., Availity, Change Healthcare)  

**Data Retrieved**:  
- `PriorAuthRecord` entity (see Claude.md Section 2):  
  - `prior_auth_id`, `approval_number`, `approval_date`, `expiration_date`  
  - `approved_cpt_codes[]`, `approved_service_description`  
  - `approval_status` (ACTIVE | EXPIRED | REVOKED)  

**Query Logic**:  
```sql  
SELECT * FROM prior_auth_records  
WHERE patient_id = {patient_id}  
  AND insurance_policy_id = {insurance_policy_id}  
  AND approval_status = 'ACTIVE'  
  AND expiration_date >= {appointment_date}  
ORDER BY expiration_date DESC  
```  

**API Access Method** (depends on system type):  
- **If internal database**: Direct SQL query or REST API  
- **If insurance portal**: HTTPS API with authentication (varies by insurer)  
- **If third-party tool**: REST API with OAuth 2.0 or API key  

**Error Handling**:  
```  
IF prior_auth_database query fails (timeout, connection error, authentication failure):  
  - Log error with details (query, error code, timestamp)  
  - Retry up to 3 times with exponential backoff (1s, 2s, 4s)  
  - If all retries fail:  
    → Set status = FAILED  
    → escalation_reason = "Prior-auth database unavailable, manual check required"  
    → Notify front-desk staff: "System error - perform manual prior-auth check"  
    → Create manual fallback task  

IF prior_auth_database returns empty result set:  
  - This is NOT an error (no prior-auth found is a valid result)  
  - Proceed to Step 2 logic: prior_auth_status = MISSING  

IF prior_auth_database returns malformed data (missing required fields):  
  - Log data quality issue  
  - Attempt to use partial data if possible  
  - If critical fields missing (approval_number, expiration_date):  
    → Set confidence_score = LOW  
    → escalation_reason = "Prior-auth data incomplete: {list missing fields}"  
    → Escalate to human  
```  

**Data Quality Validation**:  
```  
FOR EACH prior_auth_record retrieved:  
  IF prior_auth.approval_number is null OR empty:  
    → Flag data quality issue, log warning  
    
  IF prior_auth.expiration_date is null:  
    → Cannot assess validity, escalate to human  
    
  IF prior_auth.approved_cpt_codes is null OR empty:  
    → Cannot match to procedure, escalate to human  
    
  IF prior_auth.approval_date > prior_auth.expiration_date:  
    → Data integrity error, log critical warning, escalate to human  
```  

**Assumptions Referenced**:  
- **A1**: Prior-auth database has structured data (approval number, CPT codes, date ranges) - if data is unstructured free-text, matching logic will fail  
- **A12**: Prior-auth database response time <2 seconds per query  
- **A36**: Assumes prior-auth database is accessible via API (internal PostgreSQL with REST wrapper assumed; if manual portal access only, use manual fallback for Phase 1)  

**See also**: [api-specifications.md](api-specifications.md) Section 1 for complete API contracts

---  

## Insurance Eligibility Tool Integration  

**Purpose**: Determine if scheduled procedure requires prior-authorization per insurance policy  

**System Type**: Assumed [per A36] to be internal PostgreSQL with REST API wrapper. Could alternatively be:  
- Integrated with prior-auth database (same system)  
- Separate insurance eligibility verification tool (e.g., Availity, Waystar)  
- Insurance company's online portal  

**Data Retrieved**:  
- Insurance requirements mapping:  
  - `insurance_policy_id` → `procedure_code` → `prior_auth_required` (boolean)  
  - `procedure_category` (e.g., "imaging", "surgery") → `prior_auth_required`  

**Query Logic**:  
```  
GET /insurance_requirements  
  ?policy_id={insurance_policy_id}  
  &procedure_code={procedure_code}  

Response:  
{  
  "prior_auth_required": true | false,  
  "requirement_type": "always" | "sometimes" | "never",  
  "notes": "Prior-auth required for all MRI procedures"  
}  
```  

**Error Handling**:  
```  
IF insurance_requirements query fails (timeout, API error):  
  - Log error  
  - Retry up to 2 times  
  - If all retries fail:  
    → Cannot determine if prior-auth required  
    → Set confidence_score = LOW  
    → escalation_reason = "Cannot determine if prior-auth required for CPT {procedure_code}"  
    → Escalate to human (human must look up requirement manually)  

IF insurance_requirements returns "requirement_type = sometimes":  
  - Prior-auth may be required depending on clinical context  
  - Agent cannot determine (requires clinical judgment)  
  - Set confidence_score = MEDIUM  
  - Proceed with prior-auth check (assume required, better safe than sorry)  
```  

**Fallback Logic** (if insurance tool unavailable):  
```  
IF insurance_requirements_database is unavailable:  
  - Use hardcoded rule set for common procedures:  
    - All imaging procedures (CPT 70000-79999): Assume prior-auth required  
    - All surgical procedures (CPT 10000-69999): Assume prior-auth required  
    - Office visits (CPT 99201-99499): Assume prior-auth NOT required  
  - Log warning: "Using fallback rules, insurance requirements database unavailable"  
  - Set confidence_score = MEDIUM (fallback rules are approximations)  
```  

**Assumptions Referenced**:  
- **A13**: Assumes insurance requirements database exists and is accessible [per A38, if no API exists, use hardcoded rules fallback]  
- **A38**: Assumes insurance tool has API access (if not, Step 1 logic uses hardcoded rules)  

**See also**: [api-specifications.md](api-specifications.md) Section 3 for database schema

---  

## Human Review Interface  

**Purpose**: Display AI output to front-desk staff, capture human decisions  

**Interface Type**: Standalone web dashboard (React SPA) [per A41]. Embedded EHR widget deferred to Phase 2.  

**Display Location** (options):  
- **Option A**: Embedded widget in athenahealth appointment screen (requires athenahealth integration)  
- **Option B**: Standalone web dashboard accessible via browser (separate from EHR) ← **SELECTED per A41**  
- **Option C**: Pop-up notification when front-desk staff opens appointment in EHR  

**What Front-Desk Staff See**:  

**For HIGH confidence cases** (80% of cases):  
```  
=== PRIOR-AUTH VERIFICATION ===  

✅ READY TO PROCEED  

Patient: Jane Doe (ID: 12345)  
Appointment: Jan 15, 2025 at 10:00 AM  
Procedure: MRI Brain with Contrast (CPT: 70553)  

Prior-Auth Status: VALID  
- Approval Number: PA-2024-987654  
- Approved Services: MRI Brain with Contrast (CPT: 70553)  
- Expiration Date: Feb 28, 2025 (44 days after appointment)  

AI Recommendation: PROCEED  
Confidence: HIGH  

[ Approve & Proceed ]  [ Reschedule ]  [ Need More Info ]  

Review Time: <30 seconds [per A4]  
```  

**For MEDIUM/LOW confidence cases** (20% of cases):  
```  
=== PRIOR-AUTH VERIFICATION ===  

⚠️ REVIEW REQUIRED  

Patient: John Smith (ID: 67890)  
Appointment: Jan 20, 2025 at 2:00 PM  
Procedure: MRI Lumbar Spine (CPT: 72148)  

Prior-Auth Status: EXPIRING SOON  
- Approval Number: PA-2024-555123  
- Approved Services: MRI Spine (CPT: 72148)  
- Expiration Date: Jan 22, 2025 (2 days after appointment)  

⚠️ ESCALATION REASON:  
Prior-auth expires within 7 days of appointment. Recommend reviewing with office manager or contacting insurance to extend approval.  

AI Recommendation: ESCALATE  
Confidence: MEDIUM  

Data Sources Checked:  
- Prior-auth database: ✅ Retrieved 1 record  
- Insurance requirements: ✅ Confirmed prior-auth required  

[ Approve & Proceed ]  [ Reschedule ]  [ Investigate Further ]  [ Request Physician Input ]  

Notes: {free-text field for human to document decision rationale}  
```  

**Actions Available**:  

1. **Approve & Proceed**: Human agrees with AI recommendation, appointment proceeds  
   - Records: `human_decision = APPROVED`, `human_decision_at = {timestamp}`, `human_decision_by = {user_id}`  
   - Updates EHR: `appointment.prior_auth_verified = true`  
   - Transitions state: AWAITING_HUMAN_REVIEW → APPROVED → COMPLETED  

2. **Reschedule**: Human decides to reschedule appointment  
   - Records: `human_decision = RESCHEDULED`, `human_decision_notes = {free-text}`  
   - Does NOT modify appointment in EHR (human uses EHR scheduling tool separately)  
   - Transitions state: AWAITING_HUMAN_REVIEW → RESCHEDULED → COMPLETED  

3. **Need More Info / Investigate Further**: Human needs to investigate before deciding  
   - Records: `human_decision = ESCALATED`, `escalation_reason = {free-text}`  
   - Transitions state: AWAITING_HUMAN_REVIEW → ESCALATED  
   - Case remains in queue until investigation complete  

4. **Request Physician Input**: Human needs physician to weigh in  
   - Records: `human_decision = ESCALATED`, `escalation_reason = "Physician input requested"`  
   - Notifies physician (via EHR message or email) [Note: per A50, no physician notification in MVP]  
   - Transitions state: AWAITING_HUMAN_REVIEW → ESCALATED  

**Decision Recording**:  
- All human decisions logged in `PriorAuthCheck` entity  
- Audit trail includes: user_id, timestamp, decision, rationale (free-text notes)  
- Human can override AI recommendation (e.g., approve "Proceed" even if AI said "Reschedule")  
- Override reason must be documented in notes field  

**Assumptions Referenced**:  
- **A4**: Assumes front-desk staff can review HIGH confidence cases in <30 seconds  
- **A41**: Standalone web dashboard selected (embedded EHR widget deferred to Phase 2)  
- **A42**: All front-desk staff can review and override (no RBAC for MVP)  

**See also**: [api-specifications.md](api-specifications.md) Section 6 for backend API specification

---

**End of Integration Guide**
