# Requirements Specification: Prior-Authorization Check

**Parent Spec**: [../Claude.md](../Claude.md)  
**Version**: 2.0  
**Last Updated**: 2026-04-22  

---

## Overview

This document contains all functional and non-functional requirements for the Prior-Authorization Check capability.

**Referenced by**: Claude.md Sections 1 (Success Criteria) and 3 (Core Decision Logic)

---

## Table of Contents

**Functional Requirements**:
- REQ-PA-001: Automatic Prior-Auth Check Trigger
- REQ-PA-002: Prior-Auth Record Retrieval
- REQ-PA-003: CPT Code Matching Logic
- REQ-PA-004: Expiration Date Validation
- REQ-PA-005: Human Review Interface
- REQ-PA-006: EHR Documentation
- REQ-PA-007: Audit Logging
- REQ-PA-008: Manual Fallback Workflow
- REQ-PA-009: Confidence Score Calculation
- REQ-PA-010: State Machine Enforcement

**Non-Functional Requirements**:
- NFR-PA-001: Performance
- NFR-PA-002: Reliability
- NFR-PA-003: Security & Compliance
- NFR-PA-004: Auditability
- NFR-PA-005: Scalability

---

## 7. Functional Requirements  
  
### REQ-PA-001: Automatic Prior-Auth Check Trigger  
  
**Description**: The system must automatically initiate a prior-auth check for all appointments with scheduled procedures, triggered 48 hours before the appointment date.  
  
**Acceptance Criteria**:  
- When an appointment is scheduled with `procedure_codes[]` not empty, system creates a `PriorAuthCheck` entity with status = PENDING_CHECK  
- Check is triggered 48 hours before `appointment.scheduled_date` [per A11]  
- If appointment is scheduled <48 hours in advance, check is triggered immediately  
- System processes checks in batch (every 1 hour) to identify appointments requiring checks  
- 100% of appointments with procedures have prior-auth check initiated before patient arrives  
  
**Priority**: Must-Have  
  
**Dependencies**:  
- athenahealth EHR integration (read appointments)  
- Scheduling system must populate `appointment.procedure_codes[]`  
  
**Assumptions**:  
- **A11**: 48-hour trigger window gives practice time to resolve issues before patient arrives  
- **U5**: Assumes athenahealth API provides appointment data in structured format  
  
---  
  
### REQ-PA-002: Prior-Auth Record Retrieval  
  
**Description**: The system must retrieve all active prior-auth records for the patient from the prior-auth database within 5 seconds.  
  
**Acceptance Criteria**:  
- Query prior-auth database using `patient_id`, `insurance_policy_id`, and `appointment_date`  
- Retrieve all records where `approval_status = ACTIVE` and `expiration_date >= appointment_date`  
- Query completes in <5 seconds (95th percentile) [per A12]  
- If query fails, system retries up to 3 times with exponential backoff  
- If all retries fail, system sets status = FAILED and notifies front-desk staff for manual fallback  
  
**Priority**: Must-Have  
  
**Dependencies**:  
- Prior-auth database integration (API or direct database access)  
  
**Assumptions**:  
- **A1**: Prior-auth database has structured data (approval_number, CPT codes, expiration_date)  
- **A12**: Prior-auth database response time <2 seconds per query  
- **U4**: Assumes prior-auth database is accessible via API (if not, this requirement cannot be met)  
  
---  
  
### REQ-PA-003: CPT Code Matching Logic  
  
**Description**: The system must match prior-auth approved CPT codes to scheduled procedure CPT codes with exact match and fuzzy match capabilities.  
  
**Acceptance Criteria**:  
- **Exact match**: If `appointment.procedure_code` exactly matches one of `prior_auth.approved_cpt_codes[]`, confidence = HIGH  
- **Fuzzy match**: If exact match fails, compare `appointment.procedure_description` to `prior_auth.approved_service_description` using string similarity (Levenshtein distance or cosine similarity)  
  - Similarity score ≥0.8 → confidence = MEDIUM, proceed with caution  
  - Similarity score <0.8 → confidence = LOW, escalate to human  
- If multiple prior-auths match, escalate to human (cannot determine which applies)  
- If no prior-auths match, set `prior_auth_status = MISSING` and escalate  
  
**Priority**: Must-Have  
  
**Dependencies**:  
- Prior-auth database provides `approved_cpt_codes[]` and `approved_service_description`  
- EHR provides `procedure_code` and `procedure_description`  
  
**Assumptions**:  
- **A5**: CPT codes in EHR and prior-auth database use consistent 5-digit format  
- **A14**: Fuzzy match threshold of 0.8 balances false positives vs false negatives  
  
---  
  
### REQ-PA-004: Expiration Date Validation  
  
**Description**: The system must assess prior-auth expiration status and flag prior-auths expiring within 7 days of the appointment.  
  
**Acceptance Criteria**:  
- Calculate `days_until_expiration = (prior_auth.expiration_date - appointment.scheduled_date).days`  
- If `days_until_expiration < 0`: Set `prior_auth_status = EXPIRED`, recommend RESCHEDULE  
- If `days_until_expiration == 0`: Set `prior_auth_status = EXPIRING_SOON`, escalate to human [per A43]  
- If `0 < days_until_expiration <= 7`: Set `prior_auth_status = EXPIRING_SOON`, escalate to human [per A11]  
- If `days_until_expiration > 7`: Set `prior_auth_status = VALID`, recommend PROCEED  
- Expiration assessment completes in <1 second (simple date arithmetic)  
  
**Priority**: Must-Have  
  
**Dependencies**:  
- Prior-auth database provides `expiration_date` in ISO 8601 format  
  
**Assumptions**:  
- **A11**: 7-day expiration warning threshold (practice has time to obtain new prior-auth if needed)  
- **Q1**: Practice policy for same-day expiration is unknown; AI escalates for human judgment  
  
---  
  
### REQ-PA-005: Human Review Interface  
  
**Description**: The system must provide a user interface for front-desk staff to review AI recommendations and make proceed/reschedule decisions.  
  
**Acceptance Criteria**:  
- Interface displays: patient name, appointment date/time, procedure, prior-auth status, AI recommendation, confidence score  
- For escalated cases, interface displays: escalation reason, all prior-auth records found, data sources checked  
- Interface provides action buttons: Approve & Proceed, Reschedule, Investigate Further, Request Physician Input  
- Interface includes free-text notes field for human to document decision rationale  
- Human decision is recorded with user_id, timestamp, and notes  
- Interface loads in <2 seconds (95th percentile)  
- Interface is accessible via web browser (responsive design for desktop and tablet)  
  
**Priority**: Must-Have  
  
**Dependencies**:  
- Authentication system (user_id for audit trail)  
- Web application framework (React, Vue, or similar)  
  
**Assumptions**:  
- **A4**: Front-desk staff can review HIGH confidence cases in <30 seconds  
- **Q3**: Interface location (embedded in EHR vs standalone) to be determined during discovery  
  
---  
  
### REQ-PA-006: EHR Documentation  
  
**Description**: The system must document prior-auth verification results in the athenahealth EHR appointment record.  
  
**Acceptance Criteria**:  
- Write prior-auth verification note to `appointment.notes` via athenahealth API  
- Note includes: prior-auth status, AI recommendation, human decision, timestamp, matched prior-auth approval number  
- Update `appointment.prior_auth_verified = true` and `appointment.prior_auth_verified_at = {timestamp}`  
- EHR write completes in <3 seconds (95th percentile)  
- If EHR write fails, system retries every 5 minutes until successful (up to 12 retries = 1 hour)  
- If EHR write fails for >1 hour, alert system admin  
  
**Priority**: Must-Have  
  
**Dependencies**:  
- athenahealth EHR integration (write access to appointment notes)  
  
**Assumptions**:  
- **U5**: Assumes athenahealth API allows writing custom notes to appointment records  
- **A12**: EHR API response time <2 seconds  
  
---  
  
### REQ-PA-007: Audit Logging  
  
**Description**: The system must log all prior-auth checks, AI recommendations, and human decisions for audit and compliance purposes.  
  
**Acceptance Criteria**:  
- Log every prior-auth check with: check_id, patient_id, appointment_id, timestamp, status transitions  
- Log AI analysis: prior_auth_status, ai_recommendation, confidence_score, confidence_rationale  
- Log human decisions: human_decision, human_decision_by (user_id), human_decision_at (timestamp), human_decision_notes  
- Logs stored in secure database with encryption at rest  
- Logs retained for 7 years (HIPAA requirement)  
- Logs are queryable for audit reports (e.g., "show all prior-auth checks for patient X in 2024")  
- Log write completes in <500ms (does not block main workflow)  
  
**Priority**: Must-Have  
  
**Dependencies**:  
- Secure database for audit logs (PostgreSQL, MySQL, or similar)  
- Encryption at rest (database-level or application-level)  
  
**Assumptions**:  
- **Constraint**: HIPAA compliance requires audit trail of all patient data access  
- **A16**: 7-year retention period aligns with medical records retention requirements  
  
---  
  
### REQ-PA-008: Manual Fallback Workflow  
  
**Description**: The system must provide a manual fallback workflow when automated prior-auth check fails due to system errors.  
  
**Acceptance Criteria**:  
- If prior-auth database is unavailable, system sets status = FAILED and creates manual fallback task  
- Front-desk staff notified via interface: "System error - perform manual prior-auth check for patient {name}, appointment {date}"  
- Manual fallback task includes: patient name, appointment details, procedure, reason for fallback  
- Staff can manually enter prior-auth verification result (VALID | EXPIRED | MISSING) and approval number  
- Manual entry is logged with user_id and timestamp (same audit trail as automated checks)  
- Manual fallback completes in <5 minutes (staff performs manual lookup and enters result)  
  
**Priority**: Must-Have  
  
**Dependencies**:  
- Task queue system (for manual fallback tasks)  
- Human review interface (for manual entry)  
  
**Assumptions**:  
- **A13**: Manual fallback is acceptable when system errors occur (practice already performs manual checks today)  
- **A17**: Front-desk staff are trained to perform manual prior-auth checks (existing skill)  
  
---  
  
### REQ-PA-009: Confidence Score Calculation  
  
**Description**: The system must calculate a confidence score (HIGH | MEDIUM | LOW) for each AI recommendation based on data quality and matching certainty.  
  
**Acceptance Criteria**:  
- **HIGH confidence** when:  
  - Exact CPT code match between prior-auth and procedure  
  - Expiration date >7 days after appointment  
  - All required data fields present (approval_number, expiration_date, CPT codes)  
  - Single prior-auth record found (no ambiguity)  
  - No conflicting information across data sources  
- **MEDIUM confidence** when:  
  - Fuzzy match on service description (similarity ≥0.8 but not exact CPT match)  
  - Expiration date ≤7 days after appointment (expiring soon)  
  - Minor data quality issues (e.g., missing service description but CPT match exists)  
- **LOW confidence** when:  
  - No prior-auth found OR multiple prior-auths with no clear match  
  - CPT code mismatch (prior-auth covers different procedure)  
  - Missing critical data (no expiration date, no CPT codes)  
  - Conflicting information (database says active, portal says expired)  
- Confidence score is included in AI recommendation output  
- Confidence rationale (free-text explanation) is generated for all cases  
  
**Priority**: Must-Have  
  
**Dependencies**:  
- Matching logic (REQ-PA-003)  
- Expiration validation (REQ-PA-004)  
  
**Assumptions**:  
- **A15**: Confidence thresholds tuned to achieve <20% escalation rate while maintaining >95% accuracy  
- **A4**: HIGH confidence cases can be reviewed by humans in <30 seconds  
  
---  
  
### REQ-PA-010: State Machine Enforcement  
  
**Description**: The system must enforce valid state transitions for `PriorAuthCheck` entities and prevent invalid transitions.  
  
**Acceptance Criteria**:  
- System validates all state transitions against state machine definition (Section 2)  
- Invalid transitions are blocked with error message (e.g., "Cannot transition from COMPLETED to CHECKING")  
- State transitions are atomic (no partial transitions)  
- State transition history is logged (audit trail shows all state changes with timestamps)  
- If system attempts invalid transition, log error and alert system admin  
- State machine integrity: 100% of state transitions are valid (no invalid transitions in production)  
  
**Priority**: Must-Have  
  
**Dependencies**:  
- State machine implementation (entity modeling, transition logic)  
- Audit logging (REQ-PA-007)  
  
**Assumptions**:  
- **A18**: State machine enforcement prevents data corruption and ensures workflow integrity  
  
---  
  
## 8. Non-Functional Requirements  
  
### NFR-PA-001: Performance  
  
**Response Time**:  
- **End-to-end prior-auth check** (from trigger to AWAITING_HUMAN_REVIEW state): ≤10 seconds (95th percentile)  
  - Breakdown:  
    - EHR data retrieval: <2 seconds [per A12]  
    - Prior-auth database query: <2 seconds [per A12]  
    - Matching logic: <1 second  
    - Expiration validation: <1 second  
    - Confidence score calculation: <1 second  
    - EHR write (documentation): <3 seconds  
- **Human review interface load time**: <2 seconds (95th percentile)  
- **Manual fallback task creation**: <1 second  
  
**Throughput**:  
- System must handle **90 prior-auth checks per day** [per A47: 180 patients × 50% assumed, was U3]  
- Peak load: 20 checks per hour (during morning check-in rush, 8-10am)  
- System must process checks in batch (every 1 hour) without performance degradation  
  
**Priority**: Must-Have  
  
**Assumptions**:  
- **A12**: Prior-auth database response time <2 seconds per query  
- **A19**: 50% of patients require prior-auth checks [resolved with A47, was U3 - must validate during discovery]  
- **U3**: If actual volume is higher (e.g., 70% require prior-auth), system must scale to 126 checks/day  
  
---  
  
### NFR-PA-002: Reliability  
  
**Uptime**:  
- System must be available **≥99% of business hours** (8am-6pm Mon-Fri, 50 hours/week)  
  - Allowed downtime: <30 minutes per week (0.5 hours)  
- Scheduled maintenance windows: Saturdays 6am-8am (outside business hours)  
  
**Error Handling**:  
- If prior-auth database is unavailable, system must:  
  - Retry up to 3 times with exponential backoff (1s, 2s, 4s)  
  - If all retries fail, create manual fallback task  
  - Notify front-desk staff: "System error - perform manual prior-auth check"  
- If EHR is unavailable, system must:  
  - Store verification results in local database (fallback)  
  - Retry EHR write every 5 minutes until successful (up to 1 hour)  
  - Alert system admin if EHR write fails for >1 hour  
- System must gracefully degrade (manual fallback) rather than fail completely  
  
**Data Integrity**:  
- All state transitions are atomic (no partial transitions)  
- Database transactions use ACID properties (Atomicity, Consistency, Isolation, Durability)  
- If system crashes mid-check, check can be resumed from last saved state  
  
**Priority**: Must-Have  
  
**Assumptions**:  
- **A13**: Manual fallback is acceptable when system errors occur (practice already performs manual checks today)  
- **A20**: 99% uptime is acceptable for non-critical administrative workflow (not life-critical)  
  
---  
  
### NFR-PA-003: Security & Compliance  
  
**HIPAA Compliance**:  
- All patient data access must be logged with: user_id, timestamp, data accessed, action performed  
- Audit logs retained for 7 years [per A16]  
- Business Associate Agreements (BAAs) in place with all vendors (athenahealth, prior-auth database provider, cloud hosting provider)  
- Annual HIPAA compliance audit conducted by third-party auditor  
  
**Data Encryption**:  
- **At rest**: All patient data encrypted using AES-256 encryption  
  - Database encryption enabled (PostgreSQL native encryption or application-level)  
  - Backup files encrypted  
- **In transit**: All API calls use TLS 1.2 or higher (HTTPS)  
  - athenahealth API: TLS 1.2+  
  - Prior-auth database API: TLS 1.2+  
  - Human review interface: HTTPS only (no HTTP)  
  
**Access Control**:  
- Only authorized front-desk staff can view prior-auth details (role-based access control)  
- User authentication required (username/password or SSO)  
- Session timeout after 15 minutes of inactivity  
- Failed login attempts locked after 5 attempts (account locked for 30 minutes)  
  
**Data Minimization**:  
- System accesses only necessary patient data (patient_id, appointment details, insurance info)  
- System does NOT access clinical notes, diagnoses, or other sensitive medical information (not needed for prior-auth verification)  
  
**Priority**: Must-Have (regulatory requirement)  
  
**Assumptions**:  
- **Constraint**: HIPAA compliance is non-negotiable (regulatory requirement)  
- **A21**: Practice has existing BAA with athenahealth (EHR vendor)  
- **A22**: Cloud hosting provider (AWS, Azure, or GCP) is HIPAA-compliant and has signed BAA  
  
---  
  
### NFR-PA-004: Auditability  
  
**Logging Requirements**:  
- System must log all prior-auth checks with complete audit trail:  
  - Check initiated: timestamp, patient_id, appointment_id, triggered_by (system or user)  
  - AI analysis: prior_auth_status, ai_recommendation, confidence_score, data_sources_checked  
  - Human decision: human_decision, human_decision_by (user_id), human_decision_at (timestamp), human_decision_notes  
  - State transitions: from_state, to_state, transition_timestamp, transition_trigger  
- Logs are immutable (cannot be edited or deleted after creation)  
- Logs are queryable for audit reports and compliance reviews  
  
**Traceability**:  
- Each prior-auth check must be traceable to:  
  - Source data: which prior-auth records were retrieved, which data sources were queried  
  - Decision logic: why AI made specific recommendation (confidence_rationale)  
  - Human decision: who made decision, when, and why (human_decision_notes)  
- If physician questions prior-auth verification, staff can retrieve complete audit trail for that appointment  
  
**Reporting**:  
- System must generate audit reports:  
  - Daily summary: # checks completed, # escalated, # errors  
  - Weekly accuracy report: AI recommendation vs human decision (agreement rate)  
  - Monthly compliance report: # checks completed, error rate, escalation rate  
- Reports exportable to CSV or PDF  
  
**Priority**: Must-Have  
  
**Assumptions**:  
- **A16**: 7-year retention period aligns with medical records retention requirements  
- **A23**: Audit logs stored in separate database (not same database as operational data) for security  
  
---  
  
### NFR-PA-005: Scalability  
  
**Volume Growth**:  
- System must scale to handle **2× current volume** (180 checks/day) without performance degradation  
  - Future state: 360 checks/day (if practice grows to 12 physicians)  
- System architecture must support horizontal scaling (add more servers to handle increased load)  
  
**Data Growth**:  
- System must handle growing audit log database (estimated 90 checks/day × 365 days × 7 years = 230,000 records)  
- Database performance must not degrade as audit log grows (indexed queries, partitioning)  
  
**Geographic Expansion**:  
- System must support multiple practice locations (currently 2 locations, may expand to 5)  
- Each location has separate prior-auth database (or shared database with location_id filter)  
  
**Priority**: Should-Have (not critical for initial launch, but important for long-term viability)  
  
**Assumptions**:  
- **A24**: Practice may grow from 6 to 12 physicians in next 3 years (2× volume)  
- **A25**: Cloud infrastructure (AWS, Azure, GCP) provides horizontal scaling capabilities  
  
---  
  

---

**End of Requirements Specification**
