# Handling Ambiguity and Escalation

**Implements**: PA-CHECK-001 Section 5  
**Last Updated**: 2026-04-22  

This document describes how the system recognizes ambiguity, when to escalate to humans, and the escalation protocol.

---

## Recognizing Ambiguity  

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

## When to Ask vs. When to Decide  

### The agent should DECIDE (proceed with recommendation) when:

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

### The agent should ASK (escalate to human) when:

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

## Escalation Protocol  

### When the agent escalates, it must provide the following information to the human reviewer:

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

### Human Review Interface (front-desk staff sees):

- Clear summary of issue (why escalated)  
- All data gathered by AI (prior-auth records, appointment details)  
- AI's best assessment (even if low confidence)  
- Action buttons: Approve / Reschedule / Investigate / Request Physician Input  
- Free-text field for human to document decision rationale  

### Human Actions:

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

## Escalation Triggers (Comprehensive List)  

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
