# Patient Intake Agentic Transformation: Problem Statement & Success Metrics  
  
## 1. Problem Statement  
  
### Current State (Quantified)  
A 6-physician family medicine practice processes **180 patient visits per day** across 2 locations using a **4-person front-desk team**. This yields:  
- **45 intakes per staff member per day**  
- **30 patients per physician per day** (assuming equal distribution)  
  
The intake process comprises 6 distinct verification and documentation steps: insurance verification, prior-authorization check, pre-visit questionnaire completion, reason-for-visit triage, medication reconciliation, and allergy-flag review.  
  
### The Actual Problem (Not the Stated Request)  
**The stated request** is to "offload administrative load to an agentic workflow."  
  
**The actual problem** is a **systematic quality failure in intake verification** that manifests as physician-discovered errors during clinical encounters. The practice manager has diagnosed this as a capacity problem, but the evidence suggests it's a **cognitive load and error propagation problem**:  
  
1. **Error Discovery Point**: Physicians discover intake gaps *during the visit* (expired prior-auth, unreviewed medication changes)  
2. **Error Type**: These are not random errors—they are *systematic omissions* in verification steps  
3. **Impact**: Each error discovered mid-visit causes physician time waste, visit delays, potential clinical risk, and patient friction  
  
**What they actually need**: A system that ensures **verification completeness** for routine administrative checks while preserving human judgment for ambiguous or clinical decisions. The goal is not to reduce headcount but to **eliminate systematic verification gaps** that waste physician time and create clinical risk.  
  
### Hard Constraints  
1. **No clinical judgment by AI agent** (clinical decisions remain human-only)  
2. **Human escalation path required** for any visit-reason assessment  
3. **HIPAA and state medical-records compliance** (non-negotiable)  
4. **Tech stack**: athenahealth EHR + separate insurance eligibility tool  
5. **No existing AI infrastructure** (greenfield implementation)  
  
---  
  
## 2. Assumptions  
  
### A1: Time per Intake Task (Current Manual Process)  
**Assumed Value**: 12 minutes per patient (average across all 6 steps)  
  
**Reasoning**:   
- 4 staff × 8-hour workday = 32 staff-hours/day  
- Accounting for breaks, administrative overhead, phone calls: ~85% productive time = 27.2 hours  
- 27.2 hours × 60 min = 1,632 productive minutes  
- 1,632 min ÷ 180 patients = **9.07 minutes per patient** (theoretical minimum)  
- Adding buffer for interruptions, patient questions, system delays: **12 minutes is a reasonable working estimate**  
  
This aligns with industry benchmarks for multi-step intake processes in small practices (10-15 min range per MGMA data).  
  
---  
  
### A2: Error Rate in Current Process  
**Assumed Value**: 8% of intakes have at least one verification gap discovered by physician  
  
**Reasoning**:  
- Scenario states physicians "regularly discover" errors, with "most commonly" being expired prior-auth or unreviewed med changes  
- "Regularly" suggests this is not rare (>5%) but not majority (>20%)  
- For a 45-intake-per-day workload with 6 verification steps per intake (270 verification tasks/day/person), cognitive load research suggests error rates of 5-10% for routine verification tasks under time pressure  
- **8% is mid-range estimate**: ~14-15 patients per day have discoverable errors  
  
---  
  
### A3: Distribution of Intake Work Across Steps  
**Assumed Value**:  
- Insurance verification: 3 min (25%)  
- Prior-auth check: 2.5 min (21%)  
- Pre-visit questionnaire: 1.5 min (13%)  
- Reason-for-visit triage: 2 min (17%)  
- Medication reconciliation: 2 min (17%)  
- Allergy-flag review: 1 min (8%)  
  
**Reasoning**:   
- Insurance verification and prior-auth checks involve external system queries (slowest)  
- Medication reconciliation requires cross-referencing patient history (moderate complexity)  
- Allergy review is binary flag check (fastest)  
- Triage requires human judgment (moderate time, cannot be fully automated per constraint #2)  
  
---  
  
### A4: Physician Time Lost per Intake Error  
**Assumed Value**: 4 minutes per error discovered during visit  
  
**Reasoning**:  
- Physician must pause clinical workflow  
- Look up missing information (prior-auth status, medication change)  
- Potentially delay or reschedule procedure  
- Document the gap  
- Industry data (JAMA Network Open, 2019) shows administrative interruptions during visits average 3-6 minutes per incident  
- **4 minutes is conservative mid-range**  
  
---  
  
### A5: Front-Desk Staff Hourly Cost (Fully Loaded)  
**Assumed Value**: $22/hour (fully loaded with benefits, taxes, overhead)  
  
**Reasoning**:  
- Medical administrative assistants in family practice: $16-18/hour base wage (BLS 2024)  
- Fully loaded cost (benefits, payroll taxes, overhead): 1.3-1.4× multiplier  
- $17/hour × 1.3 = **$22.10/hour** (rounded to $22)  
  
---  
  
### A6: Physician Hourly Cost (Fully Loaded)  
**Assumed Value**: $120/hour (opportunity cost basis)  
  
**Reasoning**:  
- Family medicine physicians generate $200-250/hour in practice revenue (MGMA median)  
- Direct compensation: $100-120/hour  
- Using **$120/hour as physician time opportunity cost** (conservative, does not include full revenue impact)  
  
---  
  
### A7: Token Cost for AI-Driven Verification  
**Assumed Value**: $0.08 per patient intake (full 6-step verification)  
  
**Reasoning**:  
- Each verification step requires API calls to LLM for:  
  - Data extraction from EHR (athenahealth API)  
  - Insurance eligibility check (separate tool API)  
  - Structured verification output  
- Estimated token usage per intake: ~8,000 tokens (input + output)  
  - Insurance verification: 2,000 tokens  
  - Prior-auth check: 2,500 tokens  
  - Questionnaire processing: 1,000 tokens  
  - Med reconciliation: 1,500 tokens  
  - Allergy review: 500 tokens  
  - Triage escalation logic: 500 tokens  
- Using Claude 3.5 Sonnet pricing: ~$3 per million input tokens, ~$15 per million output tokens  
- Assuming 60% input / 40% output: (4,800 × $3 + 3,200 × $15) / 1,000,000 = **$0.062 per intake**  
- Adding 30% buffer for retries, validation loops: **$0.08 per intake**  
  
---  
  
### A8: Human Oversight Time Required (AI-Assisted Model)  
**Assumed Value**: 3 minutes per patient (down from 12 min in fully manual process)  
  
**Reasoning**:  
- AI handles routine verification (insurance, prior-auth, allergy flags, med reconciliation)  
- Human reviews AI output for accuracy  
- Human handles triage decisions (per constraint #2)  
- Human escalates ambiguous cases  
- **3 minutes = 25% of current time**, consistent with human-in-the-loop automation benchmarks (70-80% time reduction for routine verification tasks)  
  
---  
  
### A9: Error Rate with AI-Assisted Verification  
**Assumed Value**: 2% (down from 8%)  
  
**Reasoning**:  
- AI eliminates systematic omissions (doesn't "forget" to check prior-auth)  
- Remaining errors are edge cases, data quality issues, or human review gaps  
- **75% error reduction** is conservative for rule-based verification tasks with AI assistance  
- 8% × 0.25 = 2%  
  
---  
  
### A10: Implementation and Maintenance Cost  
**Assumed Value**: $15,000 initial build + $800/month ongoing  
  
**Reasoning**:  
- **Initial build** ($15,000):  
  - EHR integration (athenahealth API): $5,000  
  - Insurance eligibility tool integration: $3,000  
  - Agentic workflow specification and build: $4,000  
  - HIPAA compliance audit and BAA setup: $2,000  
  - Testing and validation: $1,000  
- **Ongoing monthly** ($800):  
  - Token costs: 180 patients/day × 22 workdays × $0.08 = $317/month  
  - Infrastructure (hosting, monitoring, logging): $200/month  
  - API costs (athenahealth, insurance tool): $150/month  
  - Human oversight and iteration: $133/month (amortized)  
  
---  
  
## 3. Success Metrics  
  
### Metric 1: Physician-Discovered Intake Errors per Day  
**Description**: Number of intake verification gaps discovered by physicians during clinical encounters  
  
**Current Baseline**: 14.4 errors/day (180 patients × 8% error rate per A2)  
  
**Target**: ≤3.6 errors/day (180 patients × 2% error rate per A9)  
  
**Measurement Method**:   
- Physicians flag intake errors via EHR encounter note (structured field)  
- Weekly report aggregates flagged errors by type (prior-auth, medication, insurance, other)  
- Measured over rolling 4-week period to smooth daily variance  
  
**Dependencies**: A2 (current error rate), A9 (target error rate with AI)  
  
**Type**: Lagging indicator (outcome metric)  
  
---  
  
### Metric 2: Front-Desk Staff Time per Patient Intake  
**Description**: Average time front-desk staff spend per patient from intake start to completion  
  
**Current Baseline**: 12 minutes per patient (per A1)  
  
**Target**: 3 minutes per patient (per A8)  
  
**Measurement Method**:  
- Time-stamped workflow tracking in intake system  
- Start: Patient check-in logged  
- End: Intake marked "complete" and patient ready for physician  
- Measured via median (not mean) to account for outliers  
- Sampled daily, reported weekly  
  
**Dependencies**: A1 (current time), A8 (target time with AI assistance)  
  
**Type**: Leading indicator (process metric)  
  
---  
  
### Metric 3: Physician Time Lost to Intake Errors per Day  
**Description**: Total physician time spent resolving intake gaps discovered during visits  
  
**Current Baseline**: 57.6 minutes/day (14.4 errors × 4 min per error, per A2 and A4)  
  
**Target**: ≤14.4 minutes/day (3.6 errors × 4 min per error, per A9 and A4)  
  
**Measurement Method**:  
- Physicians log time spent on intake-related interruptions via EHR timer  
- Categorized as "administrative interruption - intake error"  
- Aggregated daily across all 6 physicians  
- Reported as total minutes/day and average minutes per physician per day  
  
**Dependencies**: A2, A4 (current state), A9, A4 (target state)  
  
**Type**: Lagging indicator (outcome metric)  
  
---  
  
### Metric 4: Cost per Patient Intake (Fully Loaded)  
**Description**: Total cost to complete one patient intake, including labor, technology, and overhead  
  
**Current Baseline**: $4.40 per patient  
- Labor: 12 min × ($22/hour ÷ 60 min) = $4.40 (per A1, A5)  
- Technology: $0 (no AI costs)  
- **Total: $4.40**  
  
**Target**: $1.18 per patient  
- Labor: 3 min × ($22/hour ÷ 60 min) = $1.10 (per A8, A5)  
- Technology: $0.08 (per A7)  
- **Total: $1.18**  
  
**Measurement Method**:  
- Labor cost: (Total staff hours on intake per day ÷ 180 patients) × $22/hour  
- Technology cost: Monthly token + infrastructure costs ÷ total patients processed  
- Calculated monthly, trended over time  
  
**Dependencies**: A1, A5, A7, A8  
  
**Type**: Leading indicator (process metric)  
  
---  
  
### Metric 5: Return on Investment (ROI) - 12 Month Payback Period  
**Description**: Net savings after accounting for implementation cost, ongoing costs, and labor savings  
  
**Current Baseline**: N/A (no AI system)  
  
**Target**: Positive ROI within 12 months of deployment  
  
**Calculation**:  
- **Annual labor savings**:   
  - Time saved per patient: 9 min (12 min - 3 min, per A1 and A8)  
  - Daily savings: 180 patients × 9 min = 1,620 min = 27 hours  
  - Annual savings: 27 hours/day × 220 workdays × $22/hour = **$130,680**  
  
- **Annual physician time recovered**:  
  - Time saved per day: 43.2 min (57.6 - 14.4, per current vs target for Metric 3)  
  - Annual savings: 43.2 min/day × 220 days × $120/hour ÷ 60 min = **$19,008**  
  
- **Total annual savings**: $130,680 + $19,008 = **$149,688**  
  
- **Total annual cost**:  
  - Implementation (amortized over 12 months): $15,000  
  - Ongoing: $800/month × 12 = $9,600  
  - **Total: $24,600**  
  
- **Net annual savings**: $149,688 - $24,600 = **$125,088**  
- **Payback period**: $15,000 ÷ ($125,088 ÷ 12) = **1.4 months**  
  
**Measurement Method**:  
- Track actual labor hours saved (from Metric 2)  
- Track actual error reduction (from Metric 1 → physician time saved in Metric 3)  
- Track actual technology costs (token usage, infrastructure)  
- Calculate monthly net savings vs. baseline  
- Report cumulative ROI monthly  
  
**Dependencies**: A1, A5, A6, A7, A8, A9, A10  
  
**Type**: Lagging indicator (outcome metric)  
  
---  
  
## 4. Unknowns  
  
### Critical Unknowns (High Risk if Wrong)  
  
**U1: Actual Current Error Rate**  
- **What we don't know**: The scenario says physicians "regularly discover" errors, but we don't have quantified data  
- **Risk**: If actual error rate is 3% (not 8%), ROI case weakens significantly; if it's 15%, urgency increases  
- **Discovery question**: "Over the past month, how many times per day do physicians flag intake errors during visits? Can we review EHR encounter notes for documented intake gaps?"  
- **Must resolve before**: Architecture decisions (determines whether full automation or human-in-loop is justified)  
  
---  
  
**U2: Distribution of Errors by Type**  
- **What we don't know**: Scenario mentions "most commonly expired prior-auth or unreviewed med changes" but no breakdown  
- **Risk**: If 90% of errors are prior-auth (not 50%), we should prioritize that verification step differently  
- **Discovery question**: "Of the intake errors physicians discover, what percentage are: (1) prior-auth issues, (2) medication reconciliation gaps, (3) insurance verification failures, (4) other?"  
- **Must resolve before**: Specification (determines which capabilities to build first, which require highest validation rigor)  
  
---  
  
**U3: Prior-Authorization Workflow Complexity**  
- **What we don't know**: How many patients require prior-auth checks? What percentage of procedures need prior-auth? How often do prior-auths expire between scheduling and visit?  
- **Risk**: If only 10% of patients need prior-auth checks (not 50%), time savings estimates are overstated  
- **Discovery question**: "What percentage of daily patients have scheduled procedures requiring prior-auth? How do you currently track prior-auth expiration dates?"  
- **Must resolve before**: Specification (determines whether prior-auth is a separate capability or integrated into every intake)  
  
---  
  
**U4: Insurance Eligibility Tool API Capabilities**  
- **What we don't know**: Does the "separate tool for insurance eligibility" have an API? What data does it return? What's the query latency?  
- **Risk**: If no API exists, integration cost could be 3-5× higher; if API is slow (>5 sec response), user experience degrades  
- **Discovery question**: "What insurance eligibility tool do you use? Does it have an API we can integrate with? What's the typical response time for an eligibility check?"  
- **Must resolve before**: Architecture decisions (determines whether we can automate insurance verification or need human fallback)  
  
---  
  
**U5: athenahealth EHR Data Structure and API Access**  
- **What we don't know**: What data fields are accessible via athenahealth API? Is medication history structured or free-text? Are allergy flags standardized?  
- **Risk**: If medication data is unstructured free-text, AI accuracy drops significantly; if API access is restricted, integration becomes manual  
- **Discovery question**: "Do you have API access enabled for your athenahealth instance? Can we review sample patient records to understand data structure for medications, allergies, and visit history?"  
- **Must resolve before**: Specification (determines feasibility of automated medication reconciliation and allergy review)  
  
---  
  
**U6: Human Escalation Tolerance**  
- **What we don't know**: What percentage of intakes can be "escalated to human" before the system becomes useless?  
- **Risk**: If AI escalates 40% of cases (not 10%), staff time savings disappear  
- **Discovery question**: "For reason-for-visit triage, what percentage of patients fall into clear 'routine' vs. 'urgent' categories vs. ambiguous cases requiring judgment?"  
- **Must resolve before**: Validation design (determines acceptable escalation rate threshold)  
  
---  
  
**U7: Physician Willingness to Trust AI Verification**  
- **What we don't know**: Will physicians trust that AI-verified intake is complete, or will they re-verify everything anyway?  
- **Risk**: If physicians don't trust AI output, they'll duplicate verification work, eliminating time savings  
- **Discovery question**: "How do physicians currently know intake is complete? What would give them confidence that an AI-verified intake is trustworthy?"  
- **Must resolve before**: Validation design (determines what validation evidence physicians need to see)  
  
---  
  
### Moderate Unknowns (Can Be Refined During Build)  
  
**U8: Patient Volume Variance by Day/Location**  
- **What we don't know**: Is 180 patients/day evenly distributed across 5 workdays and 2 locations, or are there spikes (Monday mornings, one location busier)?  
- **Risk**: If one location handles 120 patients/day and the other 60, staffing and system load differ significantly  
- **Discovery question**: "What's the patient volume distribution by day of week and by location?"  
- **Can defer until**: Build-loop oversight (affects capacity planning but not core specification)  
  
---  
  
**U9: Staff Technical Proficiency**  
- **What we don't know**: How comfortable is the front-desk team with new software? What's their learning curve?  
- **Risk**: If staff struggle with new system, adoption fails regardless of technical quality  
- **Discovery question**: "How did the team adapt to athenahealth when it was implemented? What training approach worked best?"  
- **Can defer until**: Validation design (affects training plan but not core capability specification)  
  
---  
  
**U10: State Medical Records Compliance Specifics**  
- **What we don't know**: Which state(s) is the practice in? What are the specific state-level requirements beyond HIPAA?  
- **Risk**: Some states have stricter requirements (e.g., California CMIA, New York SHIELD Act) that affect data handling  
- **Discovery question**: "What state(s) are your locations in? Have you had any compliance audits in the past 2 years?"  
- **Can defer until**: Architecture decisions (affects data retention, audit logging, but not core workflow)  
  
---  
  
### Low-Risk Unknowns (Safe to Defer)  
  
**U11: Pre-Visit Questionnaire Content**  
- **What we don't know**: What questions are on the pre-visit questionnaire? Are they standardized or physician-specific?  
- **Risk**: Low—questionnaire processing is likely the simplest step to automate  
- **Can defer until**: Specification (affects implementation details but not architecture)  
  
---  
  
**U12: Current Staff Satisfaction and Turnover**  
- **What we don't know**: Is the front-desk team burned out? Is turnover high?  
- **Risk**: Low for technical specification; high for change management  
- **Can defer until**: Client engagement (affects communication strategy but not technical design)  
  
---  
  
## Summary: What We Know vs. What We Need to Discover  
  
### We Know (From Scenario):  
- Practice size: 6 physicians, 2 locations  
- Volume: 180 patients/day  
- Current staffing: 4-person front-desk team  
- Process steps: 6 distinct verification tasks  
- Failure mode: Physicians discover errors during visits  
- Constraints: No clinical judgment by AI, human escalation required, HIPAA compliance  
- Tech stack: athenahealth EHR, separate insurance tool  
  
### We Don't Know (Critical for Specification):  
- Actual error rate and distribution by type (U1, U2)  
- Prior-auth workflow details (U3)  
- API capabilities of existing tools (U4, U5)  
- Acceptable escalation rate (U6)  
- Physician trust requirements (U7)  
  
### Next Step:  
**Discovery engagement with practice manager and front-desk lead** to resolve U1-U7 before producing detailed specifications. Without this data, we risk building a system that solves the wrong problem or fails adoption due to misaligned assumptions.  
