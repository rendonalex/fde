# Assumptions and Open Questions

**Implements**: PA-CHECK-001 Section 11  
**Last Updated**: 2026-04-22  

This document catalogs all assumptions made during specification and implementation, along with their validation requirements and criticality.

---

## Assumptions (Continued from Delegation Analysis)  

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

---

## New Assumptions for This Capability (A11-A35)  

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

## BUILDABLE ASSUMPTIONS (A36-A52)  

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
- **See**: [API Specifications](api-specifications.md) for detailed endpoint definitions  

**A40: Fuzzy Matching Algorithm** ⚠️ **ASSUMPTION**  
- **Assumed Value**: Levenshtein distance with normalization (lowercase, remove punctuation)  
- **Reasoning**: Simple, deterministic, well-understood; threshold of 0.8 maps to "80% character similarity"  
- **Alternative**: Cosine similarity with TF-IDF (more complex, similar results)  
- **Criticality**: LOW - Easy to swap algorithms if needed  
- **Validation Required**: YES - Tune threshold based on real prior-auth data during pilot  
- **Implementation**: See [API Specifications](api-specifications.md) for algorithm details  

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
- **Impact**: See [Business Case](business-case.md) for sensitivity analysis; ROI remains positive even at 30% volume  

**A48: Actual Error Rate** ⚠️ **ASSUMPTION**  
- **Assumed Value**: 3% current error rate for prior-auth checks  
- **Reasoning**: Scenario states 8% overall intake errors, prior-auth is "most common" type  
- **Alternative**: Could be 2% (less severe) or 5% (more severe)  
- **Criticality**: MEDIUM - Affects ROI but not implementation  
- **Validation Required**: YES - Measure baseline error rate before deploying AI  
- **Impact**: See [Business Case](business-case.md) for sensitivity analysis; higher error rate = stronger ROI  

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
