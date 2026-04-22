# Business Case: Prior-Authorization Check

**Parent Spec**: [../Claude.md](../Claude.md)  
**Version**: 2.0  
**Last Updated**: 2026-04-22  

---

## Overview

This document contains the economic justification for the Prior-Authorization Check capability, including:
- Current state costs (manual process)
- Proposed state costs (AI-assisted with human-in-loop)
- ROI analysis and payback period
- Sensitivity analysis
- Risk register for assumptions

**Referenced by**: Claude.md Section 1 (Success Criteria) and Assumptions A47-A48

---

## Table of Contents

1. [Economic Model](#economic-model)
   - Current State Costs
   - Proposed State Costs
   - Net Annual Savings
   - Implementation Costs
   - ROI Analysis
   - Sensitivity Analysis
   - Economic Justification
2. [Risk Register for Assumptions](#risk-register-for-assumptions)

---

## 12. Economic Model  
  
### Current State Costs (Manual Process)  
  
**Labor Cost**:  
- **Time per patient**: 2.5 min [per A3]  
- **Labor rate**: $22/hour [per A5]  
- **Calculation**: 2.5 min × ($22/hour ÷ 60 min) = **$0.92 per patient**  
- **Volume**: 90 patients/day requiring prior-auth [per A47: 180 patients × 50% assumed, was U3]  
- **Daily labor cost**: $0.92 × 90 patients = **$82.80 per day**  
- **Annual labor cost**: $82.80/day × 220 workdays = **$18,216 per year**  
  
**Error Cost**:  
- **Current error rate**: 3% [per A2, assuming prior-auth errors are proportional to overall intake errors]  
  - Note: Scenario states prior-auth is "most commonly" the error type, so actual error rate may be higher (see Sensitivity Analysis)  
- **Errors per day**: 90 patients × 3% = **2.7 errors/day**  
- **Cost per error**:  
  - **Claim denial cost**: $500-5,000 per scenario; using conservative estimate of **$1,500 per claim denial**  
    - Assumes 10% of prior-auth errors result in claim denial (other 90% are caught by physician during visit)  
    - Expected claim denial cost per error: 10% × $1,500 = **$150**  
  - **Staff resolution time**: 30 min to investigate, contact insurance, resubmit claim  
    - 30 min × ($22/hour ÷ 60 min) = **$11**  
  - **Physician time waste**: 4 min per error [per A6] to discover issue during visit and redirect workflow  
    - 4 min × ($120/hour ÷ 60 min) = **$8**  
  - **Average cost per error**: $150 + $11 + $8 = **$169 per error**  
- **Daily error cost**: 2.7 errors × $169 = **$456.30 per day**  
- **Annual error cost**: $456.30/day × 220 workdays = **$100,386 per year**  
  
**Total Current Annual Cost**: $18,216 (labor) + $100,386 (errors) = **$118,602 per year**  
  
---  
  
### Proposed State Costs (AI-Assisted with Human-in-Loop)  
  
**AI Cost**:  
- **Token usage per prior-auth check**: Estimated 3,000 tokens  
  - EHR data retrieval (read appointment, patient, insurance): 500 tokens  
  - Prior-auth database query and response parsing: 800 tokens  
  - Matching logic (CPT code comparison, fuzzy matching): 700 tokens  
  - Expiration validation and confidence scoring: 500 tokens  
  - Recommendation generation (human-readable summary): 500 tokens  
  - **Total**: 3,000 tokens per check  
- **Token cost**: $0.08 per patient for entire intake [per A7], allocated to prior-auth based on complexity  
  - Prior-auth is 31% of total token budget (most complex step per delegation analysis)  
  - $0.08 × 0.31 = **$0.025 per patient**  
- **Daily AI cost**: $0.025 × 90 patients = **$2.25 per day**  
- **Annual AI cost**: $2.25/day × 220 workdays = **$495 per year**  
  
**Human Oversight Cost**:  
- **Time per patient (human review)**: 0.5 min [per A8]  
  - Breakdown:  
    - HIGH confidence cases (80%): 0.3 min average (quick review, click "Approve")  
    - MEDIUM/LOW confidence cases (20%): 1.5 min average (investigate, decide)  
    - Weighted average: (0.8 × 0.3) + (0.2 × 1.5) = 0.54 min ≈ **0.5 min**  
- **Labor rate**: $22/hour [per A5]  
- **Calculation**: 0.5 min × ($22/hour ÷ 60 min) = **$0.18 per patient**  
- **Daily oversight cost**: $0.18 × 90 patients = **$16.20 per day**  
- **Annual oversight cost**: $16.20/day × 220 workdays = **$3,564 per year**  
  
**Reduced Error Cost**:  
- **Target error rate**: 0.75% [per A9, 75% reduction from 3%]  
- **Errors per day**: 90 patients × 0.75% = **0.675 errors/day**  
- **Cost per error**: $169 per error (same as current state)  
- **Daily error cost**: 0.675 errors × $169 = **$114.08 per day**  
- **Annual error cost**: $114.08/day × 220 workdays = **$25,097 per year**  
  
**Total Proposed Annual Cost**: $495 (AI) + $3,564 (oversight) + $25,097 (reduced errors) = **$29,156 per year**  
  
---  
  
### Net Annual Savings  
  
- **Total current cost**: $118,602  
- **Total proposed cost**: $29,156  
- **Net annual savings**: $118,602 - $29,156 = **$89,446 per year**  
  
**Breakdown**:  
- **Labor savings**: $18,216 (current labor) - $3,564 (proposed oversight) = **$14,652 per year** (16% of total savings)  
- **Error reduction savings**: $100,386 (current errors) - $25,097 (reduced errors) = **$75,289 per year** (84% of total savings)  
  
**Key Insight**: Error reduction is the primary value driver (84% of savings), validating that prior-auth is a quality problem, not just an efficiency problem.  
  
---  
  
### Implementation Costs  
  
**One-Time Build Cost**:  
  
1. **Prior-auth database integration**: $4,000  
   - API development and testing (if API exists)  
   - Database schema analysis and query optimization  
   - Error handling and retry logic  
   - Assumption: Prior-auth database has API [per A36, internal PostgreSQL with REST wrapper]  
  
2. **athenahealth EHR integration**: $5,000  
   - Read access: Appointment, patient, insurance data  
   - Write access: Prior-auth verification notes  
   - OAuth 2.0 authentication setup  
   - Error handling and retry logic  
   - Assumption: athenahealth API access is enabled [per A39, OAuth 2.0 REST API]  
  
3. **Human review interface**: $3,000  
   - Web application UI (React or Vue)  
   - Display AI recommendations and prior-auth details  
   - Action buttons (Approve, Reschedule, Escalate)  
   - Free-text notes field  
   - Responsive design (desktop and tablet)  
  
4. **State machine implementation**: $2,000  
   - Entity modeling (PriorAuthCheck, PriorAuthRecord, Appointment)  
   - State transition logic and validation  
   - Invalid transition prevention  
  
5. **HIPAA compliance audit**: $2,000  
   - Security review (encryption, access control, audit logging)  
   - BAA setup with vendors (athenahealth, prior-auth database, cloud hosting)  
   - Compliance documentation  
  
6. **Testing and validation**: $3,000  
   - Test data creation (50 prior-auth records, 100 appointments)  
   - Unit tests, integration tests, end-to-end tests  
   - Performance testing (response time, throughput)  
   - User acceptance testing with front-desk staff  
  
**Total One-Time Implementation Cost**: $4,000 + $5,000 + $3,000 + $2,000 + $2,000 + $3,000 = **$19,000**  
  
**Ongoing Monthly Costs**:  
  
1. **AI token costs**: $495/year ÷ 12 = **$41 per month**  
  
2. **Infrastructure (hosting, monitoring)**: $150 per month  
   - Cloud hosting (AWS, Azure, or GCP): $100/month  
   - Database hosting (PostgreSQL): $30/month  
   - Monitoring and alerting (Datadog, New Relic): $20/month  
  
3. **API costs (prior-auth database, EHR)**: $50 per month  
   - athenahealth API: $30/month (estimated, may be included in EHR subscription)  
   - Prior-auth database API: $20/month (if third-party tool)  
  
4. **Maintenance and iteration**: $200 per month (amortized)  
   - Bug fixes, performance tuning, feature enhancements  
   - Assumes 10 hours/month at $120/hour (developer time)  
  
**Total Monthly Ongoing Cost**: $41 + $150 + $50 + $200 = **$441 per month**  
  
**Total Annual Ongoing Cost**: $441 × 12 = **$5,292 per year**  
  
---  
  
### ROI Analysis  
  
**Payback Period**:  
- **Implementation cost**: $19,000  
- **Monthly net savings**: $89,446/year ÷ 12 = **$7,454 per month**  
- **Payback period**: $19,000 ÷ $7,454 = **2.5 months**  
  
**5-Year ROI**:  
- **Total 5-year savings**: $89,446/year × 5 years = **$447,230**  
- **Total 5-year costs**: $19,000 (implementation) + ($5,292/year × 5 years) = $19,000 + $26,460 = **$45,460**  
- **Net 5-year value**: $447,230 - $45,460 = **$401,770**  
- **5-year ROI**: ($401,770 ÷ $45,460) × 100 = **884%**  
  
---  
  
### Sensitivity Analysis  
  
**Scenario 1: Lower Prior-Auth Volume** (30% of patients require prior-auth, not 50% per A47)  
  
- **Adjusted daily volume**: 180 patients × 30% = **54 patients/day**  
- **Adjusted annual labor cost (current)**: 54 × $0.92 × 220 = **$10,930**  
- **Adjusted annual error cost (current)**: 54 × 3% × $169 × 220 = **$60,232**  
- **Total current cost**: $10,930 + $60,232 = **$71,162**  
- **Adjusted annual oversight cost (proposed)**: 54 × $0.18 × 220 = **$2,138**  
- **Adjusted annual error cost (proposed)**: 54 × 0.75% × $169 × 220 = **$15,058**  
- **Total proposed cost**: $495 (AI) + $2,138 (oversight) + $15,058 (errors) = **$17,691**  
- **Adjusted annual savings**: $71,162 - $17,691 = **$53,471**  
- **Adjusted payback period**: $19,000 ÷ ($53,471 ÷ 12) = **4.3 months**  
  
**Impact**: ROI decreases but remains strong. Payback extends from 2.5 to 4.3 months. Still economically justified.  
  
---  
  
**Scenario 2: Higher Error Rate** (5% current error rate, not 3%)  
  
- **Adjusted errors per day**: 90 × 5% = **4.5 errors/day**  
- **Adjusted annual error cost (current)**: 4.5 × $169 × 220 = **$167,310**  
- **Total current cost**: $18,216 (labor) + $167,310 (errors) = **$185,526**  
- **Adjusted target error rate**: 5% × 25% (75% reduction) = **1.25%**  
- **Adjusted errors per day (proposed)**: 90 × 1.25% = **1.125 errors/day**  
- **Adjusted annual error cost (proposed)**: 1.125 × $169 × 220 = **$41,828**  
- **Total proposed cost**: $495 (AI) + $3,564 (oversight) + $41,828 (errors) = **$45,887**  
- **Adjusted annual savings**: $185,526 - $45,887 = **$139,639**  
- **Adjusted payback period**: $19,000 ÷ ($139,639 ÷ 12) = **1.6 months**  
  
**Impact**: ROI increases significantly. Error reduction becomes even more valuable. Payback shortens from 2.5 to 1.6 months. Urgency increases.  
  
---  
  
**Scenario 3: Lower Error Reduction** (50% reduction, not 75% per A9)  
  
- **Adjusted target error rate**: 3% × 50% (50% reduction) = **1.5%**  
- **Adjusted errors per day (proposed)**: 90 × 1.5% = **1.35 errors/day**  
- **Adjusted annual error cost (proposed)**: 1.35 × $169 × 220 = **$50,193**  
- **Total proposed cost**: $495 (AI) + $3,564 (oversight) + $50,193 (errors) = **$54,252**  
- **Adjusted annual savings**: $118,602 - $54,252 = **$64,350**  
- **Adjusted payback period**: $19,000 ÷ ($64,350 ÷ 12) = **3.5 months**  
  
**Impact**: ROI decreases but remains acceptable. Payback extends from 2.5 to 3.5 months. Still economically justified.  
  
---  
  
**Scenario 4: Higher Implementation Cost** (2× estimated cost due to integration complexity)  
  
- **Adjusted implementation cost**: $19,000 × 2 = **$38,000**  
- **Adjusted payback period**: $38,000 ÷ ($89,446 ÷ 12) = **5.1 months**  
- **Adjusted 5-year ROI**: ($447,230 - $64,460) ÷ $64,460 × 100 = **594%**  
  
**Impact**: Payback extends from 2.5 to 5.1 months. 5-year ROI decreases from 884% to 594%. Still economically justified, but integration complexity is a risk factor.  
  
---  
  
### Economic Justification  
  
**Is this capability worth building?**  
  
- **Base case payback period**: 2.5 months (excellent)  
- **Worst-case payback period** (combining pessimistic scenarios: 30% volume + 50% error reduction + 2× implementation cost):  
  - Savings: $53,471/year (from Scenario 1, but with 50% error reduction instead of 75%)  
  - Adjusted savings: $53,471 × 0.67 (proportional reduction) = **$35,826/year**  
  - Payback: $38,000 ÷ ($35,826 ÷ 12) = **12.7 months**  
- **Recommendation**: **PROCEED** - Even in worst-case scenario, payback is <13 months and 5-year ROI exceeds 200%  
  
**What makes this economically viable?**  
  
1. **Error reduction is the primary value driver** (84% of savings in base case)  
   - Prior-auth errors are costly ($169 per error) due to claim denials and physician time waste  
   - 75% error reduction translates to $75,289/year savings  
   - Even 50% error reduction (conservative) yields $50,193/year savings  
  
2. **High-volume, high-stakes workflow**  
   - 90 checks/day (base case) or 54 checks/day (conservative) is sufficient volume to justify automation  
   - Each error has downstream costs (claim denial, staff time, physician time)  
  
3. **Low ongoing costs**  
   - AI token costs are minimal ($495/year)  
   - Infrastructure costs are reasonable ($5,292/year)  
   - Human oversight time is reduced by 80% (2.5 min → 0.5 min)  
  
4. **Risk-adjusted ROI is strong**  
   - Even in worst-case scenario (low volume, low error reduction, high implementation cost), payback is <13 months  
   - Base case payback is 2.5 months (extremely fast)  
  
5. **Strategic value beyond financial ROI**:  
   - **Physician satisfaction**: Physicians no longer discover prior-auth errors during visits (reduces frustration, improves workflow)  
   - **Patient experience**: Fewer appointment delays or rescheduling due to prior-auth issues  
   - **Competitive advantage**: Practice can market "streamlined intake process" to attract patients  
   - **Scalability**: System supports practice growth (can handle 2× volume without additional staff)  
  
**What could make this economically unviable?**  
  
1. **If prior-auth volume is <20% of patients** (36 checks/day instead of 90):  
   - Annual savings drop to ~$35,000  
   - Payback extends to ~6.5 months (still acceptable, but less compelling)  
   - **Decision**: Defer to Phase 2 if volume is <20%; prioritize higher-volume steps (insurance verification, medication reconciliation)  
  
2. **If implementation cost exceeds $40,000** (2× base estimate):  
   - Payback extends to ~5 months (base case) or ~13 months (worst case)  
   - **Decision**: Re-evaluate implementation approach; consider phased rollout or simplified scope  
  
3. **If error reduction is <25%** (not 75%):  
   - Error cost savings drop from $75,289 to $25,096  
   - Total annual savings drop from $89,446 to $39,253  
   - Payback extends to ~5.8 months  
   - **Decision**: Still economically justified, but value proposition weakens; may need to improve AI accuracy  
  
4. **If prior-auth database has no API** (manual portal access only):  
   - Step 2 (locate prior-auth) cannot be automated  
   - Capability scope reduces to Step 4 (expiration checking) and Step 5 (recommendation generation) only  
   - Time savings drop from 2.0 min to ~0.5 min per patient  
   - **Decision**: Redesign capability as "prior-auth expiration reminder" (simpler scope) OR defer to Phase 2 until API access is available  
  
**Decision Rule**:  
  
- **Proceed with build if**:  
  - Prior-auth volume ≥30% of patients (54 checks/day)  
  - Prior-auth database has API access [per A36, internal PostgreSQL with REST API assumed]  
  - Implementation cost ≤$30,000  
  - Expected error reduction ≥50%  
  
- **Defer to Phase 2 if**:  
  - Prior-auth volume <20% of patients (36 checks/day) → Prioritize higher-volume steps first  
  - Prior-auth database has no API (manual portal only) → Wait for API access or negotiate with vendor  
  
- **Redesign if**:  
  - Implementation cost exceeds $40,000 → Simplify scope (e.g., expiration checking only, defer matching logic)  
  - Error reduction is <25% in pilot → Improve AI accuracy before full rollout  
  
---  
  
### Assumptions Referenced in Economic Model  
  
- **A2**: Current error rate (3%)  
- **A3**: Time per patient manual process (2.5 min)  
- **A5**: Front-desk staff hourly cost ($22/hour)  
- **A6**: Physician hourly cost ($120/hour)  
- **A7**: Token cost per intake ($0.08 total, 31% allocated to prior-auth)  
- **A8**: Human oversight time (0.5 min)  
- **A9**: Target error rate (0.75%, 75% reduction)  
- **A19**: Percentage of patients requiring prior-auth (50% per A47, was U3 - critical assumption)  
- **U3**: Percentage of patients requiring prior-auth (assumed 50%, must validate during discovery)  
- **U4**: Prior-auth database API access (assumed available, must validate during discovery)  
  
**Note**: All economic calculations must be updated once **U3** (prior-auth volume) is resolved during discovery. If actual volume is 30% or 70%, ROI changes significantly (see Sensitivity Analysis).  
  
---  
  
**End of Capability Specification**  

---

## 14. RISK REGISTER FOR ASSUMPTIONS  
  
| Assumption | Risk Level | Impact if Wrong | Mitigation |  
|------------|------------|-----------------|------------|  
| A36: Prior-Auth DB is PostgreSQL with REST API | HIGH | Complete integration rewrite | Validate in discovery; use interface pattern |  
| A37: Prior-Auth data is structured | HIGH | Matching accuracy drops to ~70% | Inspect sample records; plan NLP fallback |  
| A38: Insurance requirements DB exists | MEDIUM | Use hardcoded rules (acceptable) | Validate; fallback logic ready |  
| A39: athenahealth API uses OAuth 2.0 | LOW | Auth logic change (~1 day work) | Review API docs early |  
| A40: Levenshtein algorithm | LOW | Swap algorithm (~2 hours) | Easy to change |  
| A41: Standalone UI | MEDIUM | UI rewrite if embedded needed | Plan Phase 2 refactor |  
| A42: No RBAC needed | LOW | Add RBAC later (~3 days) | Simple to add incrementally |  
| A43: Escalate same-day expiration | LOW | Change business rule (~30 min) | Configurable parameter |  
| A47: 50% prior-auth volume | HIGH | ROI changes; infrastructure sizing | Measure actual volume week 1 |  
  
---  
  
### Open Questions - STATUS: RESOLVED WITH ASSUMPTIONS  
  
✅ **All open questions have been resolved with explicit assumptions (A36-A52).** The specification is now buildable. These assumptions MUST be validated during discovery, and the spec may require updates if assumptions are incorrect.  
  
---  
  
#### Resolved Questions Summary  
  
**From Previous Analysis** (U1-U7) → **RESOLVED**:  
- ✅ **U1**: Actual current error rate → **RESOLVED with A48** (assumed 3%, measure baseline before deployment)  
- ✅ **U2**: Distribution of errors by type → **ACCEPTED AS-IS** (prior-auth is "most common" per scenario)  
- ✅ **U3**: Percentage of patients requiring prior-auth → **RESOLVED with A47** (assumed 50%, measure week 1 of pilot)  
- ✅ **U4**: Insurance eligibility tool API capabilities → **RESOLVED with A38** (internal mapping table + hardcoded fallback)  
- ✅ **U5**: athenahealth EHR data structure → **RESOLVED with A39** (OAuth 2.0 REST API, see Section 13.2)  
- ✅ **U6**: Human escalation tolerance → **ACCEPTED AS-IS** (<20% escalation rate target)  
- ✅ **U7**: Physician willingness to trust AI verification → **ACCEPTED AS-IS** (trust but verify model)  
  
**Critical Questions** (Q1-Q10) → **RESOLVED**:  
- ✅ **Q1**: Same-day expiration policy → **RESOLVED with A43** (escalate to human for judgment, confidence = MEDIUM)  
- ✅ **Q2**: Authorization to override → **RESOLVED with A42** (all front-desk staff can override, no RBAC for MVP)  
- ✅ **Q3**: UI location → **RESOLVED with A41** (standalone web dashboard, embedded deferred to Phase 2)  
- ✅ **Q4**: Prior-auth database type → **RESOLVED with A36** (internal PostgreSQL + REST API, see Section 13.1)  
- ✅ **Q5**: Prior-auth data structure → **RESOLVED with A37** (structured data assumed, fallback if unstructured)  
- ✅ **Q6**: Insurance requirements database → **RESOLVED with A38** (internal table + hardcoded fallback rules)  
- ✅ **Q7**: Expiration warning threshold → **RESOLVED with A44** (7 days, tunable parameter)  
- ✅ **Q8**: Multiple procedures handling → **RESOLVED with A45** (separate checks per procedure)  
- ✅ **Q9**: Physician notification → **RESOLVED with A50** (no notification for MVP, front-desk handles)  
- ✅ **Q10**: Re-verification on reschedule → **RESOLVED with A46** (new check if rescheduled >7 days)  
  
---  
  
#### Validation Checklist for Discovery Phase  
  
Before implementation begins, validate these HIGH-RISK assumptions:  
  
| Assumption | What to Validate | How to Validate |  
|------------|------------------|-----------------|  
| **A36** | Prior-auth database is PostgreSQL with REST API | Meet with database admin; inspect schema and API docs |  
| **A37** | Prior-auth data is structured | Review sample prior-auth records; check if CPT codes in separate fields |  
| **A38** | Insurance requirements can use internal table or hardcoded rules | Interview staff; understand current lookup process |  
| **A47** | 50% of patients require prior-auth | Pull appointment data for past month; calculate actual % |  
| **A48** | 3% current error rate | Audit recent prior-auth errors; measure baseline |  
  
**If any HIGH-RISK assumption is wrong**, refer to Section 14 (Risk Register) for mitigation strategies.  
  
---  
  

---

**End of Business Case**
