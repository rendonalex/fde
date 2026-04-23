# Core Decision Logic

**Implements**: PA-CHECK-001 Section 3  
**Last Updated**: 2026-04-22  

This document describes the 5-step decision process for prior-authorization verification.

---

## Step 1: Determine if Prior-Authorization is Required  

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

## Step 2: Locate Prior-Authorization Documentation  

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

## Step 3: Validate Prior-Authorization Matches Scheduled Procedure  

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

## Step 4: Check Prior-Authorization Expiration Status  

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

## Step 5: Generate Recommendation and Confidence Score  

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
