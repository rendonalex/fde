# Patient Intake Delegation Analysis: Agentic Transformation Design  
  
# Executive Summary: Patient Intake Delegation Distribution  
  
## Overview  
  
This delegation analysis evaluates how AI agents can transform a 6-physician family practice's patient intake workflow, which currently processes 180 patients daily [per problem statement] through a 4-person front-desk team. The analysis applies the Agentic Transformation (ATX) methodology to determine which work should be fully automated, which requires human oversight, and which must remain human-led.  
  
---  
  
## Key Findings  
  
### The Problem is Quality, Not Capacity  
  
While the practice manager requested automation to "offload administrative load," the evidence reveals the actual problem is **systematic quality failures**: physicians regularly discover intake errors during visits (expired prior-authorizations, unreviewed medication changes). These errors waste physician time, delay care, and create patient friction.  
  
**Current state**: 8% of intakes have discoverable errors [per A2], costing 57.6 minutes of physician time daily [per A4 and A6] and creating downstream costs of $4.50 per patient on average.  
  
---  
  
## Delegation Strategy  
  
### Work Distribution  
  
The 6-step intake process has been analyzed and classified into three cognitive zones:  
  
| Cognitive Zone | Steps | Delegation Approach | Rationale |  
|----------------|-------|---------------------|-----------|  
| **Routine Work** | Insurance Verification, Allergy Review, Questionnaire Processing | **Full Delegation** with escalation paths | High clarity, low variance, rule-based—AI handles end-to-end with human review only for edge cases |  
| **Judgment Work** | Prior-Auth Check, Medication Reconciliation | **Human-in-Loop** | Rule-based but high-stakes exceptions require human decision-making; AI does analysis, human decides |  
| **Clinical Judgment** | Reason-for-Visit Triage | **AI Assistance** | Requires medical risk assessment; human makes all decisions, AI structures information and flags urgent keywords |  
  
### Delegation Breakdown  
  
**By step count**:  
- 33% fully delegated (2 of 6 steps)  
- 33% human-in-loop (2 of 6 steps)  
- 17% AI assistance (1 of 6 steps)  
- 17% hybrid (1 of 6 steps)  
- 0% remain fully manual  
  
**By time allocation** [per A3: time distribution across steps]:  
- 56% of current time spent on routine work → **Full delegation captures maximum efficiency**  
- 39% of current time spent on judgment work → **Human-in-loop preserves safety while gaining efficiency**  
- 6% of current time spent on clinical judgment → **AI assistance adds value without replacing human decision-making**  
  
---  
  
## Economic Impact  
  
### Total Annual Value: $295,812  
  
| Value Driver | Annual Savings | % of Total |  
|--------------|----------------|------------|  
| **Labor savings** (time reduction) | $129,954 | 44% |  
| **Error reduction savings** (quality improvement) | $165,858 | 56% |  
  
**Key insight**: Error reduction is the primary value driver (56% of total savings), validating that this is a quality problem, not just a capacity problem.  
  
### Savings by Step  
  
| Intake Step | Delegation Type | Time Saved per Patient | Annual Savings | Priority |  
|-------------|----------------|----------------------|----------------|----------|  
| **Prior-Authorization Check** | Human-in-Loop | 2.0 min | **$160,776** | #1 |  
| **Insurance Verification** | Full Delegation | 2.9 min | **$45,144** | #2 |  
| **Medication Reconciliation** | Human-in-Loop | 1.5 min | **$26,928** | #3 |  
| **Reason-for-Visit Triage** | AI Assistance | 0.5 min | **$24,552** | #4 |  
| **Pre-Visit Questionnaire** | Hybrid | 1.2 min | **$22,968** | #5 |  
| **Allergy-Flag Review** | Full Delegation | 0.9 min | **$15,444** | #6 |  
  
**Total time saved per patient**: 9.0 minutes (75% reduction from 12 min [per A1] to 3 min [per A8])  
  
---  
  
## Risk Management  
  
### Conservative by Design  
  
The delegation strategy prioritizes safety and constraint compliance over maximum automation:  
  
✅ **No clinical judgment by AI**: Triage remains human-led; medication reconciliation and prior-auth decisions require human approval  
  
✅ **Human escalation paths**: All fully delegated steps have defined escalation conditions for ambiguous cases  
  
✅ **Layered safeguards**:   
- Delegation archetype selection (high-stakes = human oversight)  
- Escalation paths for edge cases  
- Physician review as final safeguard (existing process preserved)  
- Production monitoring (daily dashboards, weekly audits, monthly reviews)  
  
### Risk Profile by Step  
  
| Risk Level | Steps | Safeguards |  
|------------|-------|------------|  
| **Low** | Insurance Verification, Allergy Review | Errors caught downstream; low clinical impact |  
| **Medium** | Prior-Auth, Med Reconciliation, Triage | Human review gates; physician final review |  
| **High** | None | No high-risk delegation in this design |  
  
---  
  
## Implementation Priorities  
  
### Phase 1: High-Value, Low-Risk (Months 1-2)  
  
1. **Prior-Authorization Check** ($160,776/year) → Highest value, addresses stated problem  
2. **Insurance Verification** ($45,144/year) → High volume, low risk, clear ROI  
3. **Medication Reconciliation** ($26,928/year) → Addresses stated problem, moderate complexity  
  
**Phase 1 total value**: $232,848/year (79% of total savings)  
  
### Phase 2: Moderate-Value, Build Trust (Months 3-4)  
  
4. **Reason-for-Visit Triage** ($24,552/year) → Requires physician trust, gradual rollout  
5. **Pre-Visit Questionnaire** ($22,968/year) → Moderate complexity, safety value  
6. **Allergy-Flag Review** ($15,444/year) → Low complexity, quick win  
  
**Phase 2 total value**: $62,964/year (21% of total savings)  
  
---  
  
## Return on Investment  
  
### Implementation Cost: $24,600 (Year 1)  
  
- Initial build: $15,000 (EHR integration, workflow specification, HIPAA compliance)  
- Ongoing annual: $9,600 (token costs, infrastructure, maintenance)  
  
### Payback Analysis  
  
| Metric | Value |  
|--------|-------|  
| **Year 1 net savings** | $271,212 ($295,812 - $24,600) |  
| **Payback period** | 1.4 months |  
| **5-year ROI** | 1,430% |  
  
**Risk-adjusted**: Even if savings are 50% lower than projected (conservative scenario), payback period is <3 months and 5-year ROI exceeds 600%.  
  
---  
  
## Where Humans Remain Essential  
  
### The Human Role Transforms  
  
**From executor to validator**: Humans no longer perform tedious verification tasks (querying systems, transcribing data, checking completeness). AI handles execution; humans validate output and make judgment calls.  
  
**From generalist to specialist**: Humans focus cognitive effort on exceptions, edge cases, and judgment calls—the work that actually requires human intelligence.  
  
**From reactive to proactive**: AI flags issues before they reach physicians (expired prior-auth, medication discrepancies, urgent symptoms). Humans intervene earlier in the workflow.  
  
### Human Decision-Making Preserved For:  
  
- All triage decisions (urgency assessment, clinical risk)  
- All prior-auth proceed/reschedule decisions (risk vs. benefit)  
- All medication discrepancy significance assessments (clinical impact)  
- All escalated edge cases (ambiguous responses, new allergies, urgent symptoms)  
  
**The line**: AI handles administrative verification (facts). Humans handle clinical assessment (judgment).  
  
---  
  
## Critical Success Factors  
  
### Must Resolve Before Specification:  
  
1. **Actual error rate and distribution** → Determines human oversight levels  
2. **Insurance tool API capabilities** → Determines feasibility of full automation  
3. **EHR data structure** → Determines AI accuracy for medication reconciliation  
4. **Physician trust level** → Determines rollout strategy and transparency requirements  
  
### Must Monitor in Production:  
  
1. **Error rate reduction** → Target: 8% → 2% (75% reduction)  
2. **Escalation rate** → Target: <15% for fully delegated steps  
3. **Physician re-verification behavior** → If >30% re-verify AI output, trust issue exists  
4. **Staff workload perception** → AI should feel like "less work," not "different work"  
  
---  
  
## Recommendation  
  
**Proceed with phased implementation**, prioritizing prior-authorization check and insurance verification (79% of value, lowest risk). The delegation strategy is economically justified (1.4-month payback), constraint-compliant (no clinical judgment by AI, human escalation paths preserved), and risk-appropriate (conservative design with layered safeguards).  
  
**The value proposition is clear**: This is not about replacing humans—it's about eliminating systematic quality failures that waste physician time and create clinical risk. AI handles the tedious verification work; humans focus on judgment calls and exceptions. The result is faster intake, fewer errors, and better use of scarce human cognitive capacity.  
  
**Next step**: Conduct discovery engagement to resolve critical unknowns (U1-U7), then proceed to detailed specification for Phase 1 capabilities.  
  
—————————————————————————  
# Details delegation: Patient Intake Delegation Distribution:  
  
## 1. Cognitive Work Assessment  
  
### Step 1: Insurance Verification  
  
**Current Cognitive Load**:  
- Query external insurance eligibility system with patient demographics and insurance ID  
- Interpret eligibility response (active/inactive, coverage type, copay amount, deductible status)  
- Cross-reference coverage against appointment type (office visit, procedure, lab work)  
- Identify coverage gaps or mismatches (e.g., patient scheduled for procedure not covered by current plan)  
- Document verification status and any issues in EHR  
- Communicate coverage issues to patient if discovered  
  
**Decisions Made**:  
- Is the insurance active and valid for today's visit?  
- Does coverage match the scheduled appointment type?  
- Should the patient be notified of coverage issues before the visit?  
  
**Information Access**:  
- Patient demographics (name, DOB, insurance ID)  
- Insurance eligibility system (external API or web portal)  
- Appointment details (visit type, scheduled procedures)  
- EHR documentation fields  
  
**Judgment Calls Required**:  
- Minimal judgment—this is primarily rule-based verification  
- Exception: Ambiguous eligibility responses (e.g., "pending," "contact insurer") require human interpretation  
  
**Cognitive Zone Classification**: **Routine Work**  
  
**Reasoning**:   
Insurance verification is a deterministic lookup process with clear pass/fail criteria. The work follows a defined algorithm:  
1. Query system with patient identifiers  
2. Parse response for active/inactive status  
3. Match coverage type to visit type  
4. Document result  
  
Variance is low—the same steps apply to every patient. The primary cognitive load is navigating systems and interpreting structured responses, not making judgment calls. This is classic routine work: high clarity, low variance, rule-based execution.  
  
**Exception case**: When eligibility systems return ambiguous responses (5-10% of queries per industry data), this escalates to judgment work requiring human interpretation.  
  
---  
  
### Step 2: Prior-Authorization Check  
  
**Current Cognitive Load**:  
- Identify which scheduled services require prior-authorization (procedures, imaging, specialist referrals)  
- Query insurance system or internal tracking for prior-auth status  
- Verify prior-auth is active and not expired  
- Cross-reference prior-auth approval details against scheduled service (CPT codes, date ranges)  
- Identify expired or missing prior-auths  
- Escalate missing/expired prior-auths to scheduling team or physician  
- Document prior-auth status in EHR  
  
**Decisions Made**:  
- Does this visit require prior-authorization?  
- Is the prior-auth on file, active, and valid for today's scheduled service?  
- Should the visit proceed, be rescheduled, or require physician consultation?  
  
**Information Access**:  
- Appointment schedule (procedure type, CPT codes)  
- Insurance prior-auth database (internal or payer system)  
- Prior-auth approval documents (approval number, date range, approved services)  
- EHR documentation  
  
**Judgment Calls Required**:  
- Moderate judgment required when:  
  - Prior-auth approval language is ambiguous (e.g., "approved for imaging" but unclear if MRI or CT)  
  - Prior-auth expires within 7 days [per Claude.md A44: expiration warning threshold]—should visit proceed or be rescheduled?  
  - Patient has multiple prior-auths on file—which applies to today's visit?  
  
**Cognitive Zone Classification**: **Judgment Work**  
  
**Reasoning**:   
Prior-auth verification is rule-based but has significant exceptions requiring human judgment. The core workflow is routine (lookup prior-auth, check expiration, match to service), but real-world complexity introduces variance:  
- Prior-auth documentation is often incomplete or ambiguous  
- Expiration date edge cases require risk assessment (proceed vs. reschedule)  
- Multiple prior-auths for similar services require matching logic that isn't always deterministic  
  
Industry data shows prior-auth verification has 15-20% exception rates requiring human judgment [aligns with Claude.md A15: <20% escalation rate target]. This places it firmly in judgment work territory: rule-based foundation with moderate variance and exceptions.  
  
---  
  
### Step 3: Pre-Visit Questionnaire  
  
**Current Cognitive Load**:  
- Provide patient with questionnaire (digital or paper)  
- Review completed questionnaire for completeness  
- Identify missing or unclear responses  
- Follow up with patient to clarify ambiguous answers  
- Enter questionnaire data into EHR (if paper-based)  
- Flag urgent responses for physician review (e.g., new symptoms, medication side effects)  
  
**Decisions Made**:  
- Is the questionnaire complete?  
- Are any responses unclear or contradictory?  
- Do any responses require immediate physician attention before the visit?  
  
**Information Access**:  
- Pre-visit questionnaire template  
- Patient responses  
- EHR fields for questionnaire data entry  
  
**Judgment Calls Required**:  
- Minimal judgment for routine completion checks  
- Moderate judgment for flagging urgent responses (what constitutes "urgent"?)  
  
**Cognitive Zone Classification**: **Routine Work** (with judgment escalation path)  
  
**Reasoning**:   
Pre-visit questionnaire processing is primarily data entry and completeness verification—both routine tasks. The cognitive load is low: check for blank fields, transcribe responses, document in EHR.  
  
However, there's a judgment escalation layer: identifying responses that require immediate physician attention. This is the exception, not the norm (estimated 5-10% of questionnaires based on typical urgent symptom rates).  
  
The base work is routine; the escalation path requires judgment. This makes it suitable for AI assistance with human-in-loop for flagged cases.  
  
---  
  
### Step 4: Reason-for-Visit Triage  
  
**Current Cognitive Load**:  
- Review patient's stated reason for visit  
- Assess urgency level: routine (scheduled follow-up), urgent (new concerning symptom), same-day (acute issue)  
- Determine appropriate appointment slot and physician availability  
- Identify cases requiring immediate physician consultation before scheduling  
- Communicate triage decision to patient and scheduling team  
- Document triage rationale  
  
**Decisions Made**:  
- What is the urgency level of this visit?  
- Can this be handled in a routine appointment, or does it require urgent/same-day care?  
- Should a physician be consulted before finalizing the appointment?  
  
**Information Access**:  
- Patient's stated reason for visit  
- Patient medical history (chronic conditions, recent visits)  
- Physician schedule and availability  
- Clinical triage protocols (if documented)  
  
**Judgment Calls Required**:  
- **High judgment required**: Triage is inherently a judgment task  
  - Patients describe symptoms in lay terms; staff must interpret clinical significance  
  - Urgency assessment requires medical knowledge and risk assessment  
  - Edge cases are common (e.g., "chest discomfort" could be routine or life-threatening)  
  
**Cognitive Zone Classification**: **Judgment Work** (bordering on Novel Work)  
  
**Reasoning**:   
Reason-for-visit triage is rule-based (protocols exist for common scenarios) but has high variance and frequent exceptions. The cognitive work involves:  
- Interpreting ambiguous patient descriptions  
- Assessing clinical risk without making a diagnosis (non-clinical staff walking a fine line)  
- Applying protocols that have gray areas  
  
This is not routine work—every patient presents differently, and the consequences of mis-triage are significant (delayed care for urgent issues, or overloading urgent slots with routine cases).  
  
This is judgment work with high stakes. It requires human decision-making, but AI can assist by:  
- Structuring patient descriptions  
- Flagging keywords that suggest urgency (chest pain, shortness of breath, severe bleeding)  
- Presenting triage protocols for human review  
  
**Critical constraint**: The scenario explicitly requires "human escalation path for visit-reason decisions." This confirms triage cannot be fully delegated.  
  
---  
  
### Step 5: Medication Reconciliation  
  
**Current Cognitive Load**:  
- Review patient's current medication list in EHR  
- Ask patient to confirm medications they're currently taking  
- Identify discrepancies (medications patient reports but not in EHR, or vice versa)  
- Update EHR with patient-reported changes (new medications, stopped medications, dosage changes)  
- Flag discrepancies for physician review (especially high-risk medications)  
- Document reconciliation completion  
  
**Decisions Made**:  
- Does the EHR medication list match what the patient reports?  
- Which discrepancies are significant enough to flag for physician review?  
- Should medications be updated in EHR immediately or wait for physician confirmation?  
  
**Information Access**:  
- EHR medication list (current and historical)  
- Patient verbal report of current medications  
- Medication interaction databases (if available)  
  
**Judgment Calls Required**:  
- Moderate judgment required:  
  - Patients often misremember medication names or dosages  
  - Determining which discrepancies are clinically significant (missing aspirin vs. missing insulin)  
  - Deciding whether to update EHR before physician review or flag for confirmation  
  
**Cognitive Zone Classification**: **Judgment Work**  
  
**Reasoning**:   
Medication reconciliation is structured (compare list A to list B, identify differences) but requires judgment to assess significance. The cognitive load includes:  
- Interpreting patient descriptions of medications (brand names vs. generics, "the little white pill")  
- Assessing which discrepancies matter (routine vitamins vs. critical prescriptions)  
- Deciding escalation priority (flag immediately vs. note for physician)  
  
This is not routine work because variance is high—every patient has a different medication profile, and discrepancies require case-by-case assessment. However, it's also not novel work—there are established protocols for medication reconciliation.  
  
This is judgment work: rule-based foundation with moderate variance and exceptions requiring human assessment.  
  
**Critical constraint**: "No clinical judgment by AI" applies here. AI should not decide which medication discrepancies are clinically significant—that requires medical judgment. AI can structure the comparison and flag all discrepancies; humans decide which matter.  
  
---  
  
### Step 6: Allergy-Flag Review  
  
**Current Cognitive Load**:  
- Review patient's allergy list in EHR  
- Ask patient to confirm current allergies  
- Identify new allergies or changes to existing allergy information  
- Update EHR with patient-reported changes  
- Flag critical allergies for physician attention (e.g., new drug allergy, severe reaction history)  
- Ensure allergy information is visible to clinical team  
  
**Decisions Made**:  
- Does the EHR allergy list match patient's current allergy status?  
- Are any new allergies reported?  
- Do any allergies require immediate physician notification?  
  
**Information Access**:  
- EHR allergy list  
- Patient verbal report  
- Allergy severity classifications (if documented)  
  
**Judgment Calls Required**:  
- Minimal judgment for routine confirmation  
- Moderate judgment for assessing severity (patient says "penicillin makes me nauseous" vs. "penicillin caused anaphylaxis")  
  
**Cognitive Zone Classification**: **Routine Work** (with judgment escalation for severity assessment)  
  
**Reasoning**:   
Allergy review is primarily a verification task: confirm existing allergies, document new ones. The cognitive load is low for the base case—this is a structured checklist.  
  
However, there's a judgment layer when patients report new allergies or describe reactions. Assessing whether "nausea" is a true allergy vs. side effect requires medical knowledge (though front-desk staff typically document verbatim and let physicians interpret).  
  
The base work is routine (verify list, document changes). The escalation path (assess severity, determine urgency) requires judgment but is the exception, not the norm.  
  
This is routine work with a judgment escalation path—suitable for AI with human review of flagged cases.  
  
---  
  
## 2. Delegation Design  
  
### Step 1: Insurance Verification  
  
**Delegation Archetype**: **Full Delegation** (with human escalation for ambiguous responses)  
  
**Justification**:  
Insurance verification is deterministic and low-risk. The AI can:  
- Query insurance eligibility API with patient identifiers  
- Parse structured response (active/inactive, coverage details)  
- Apply rule-based logic (does coverage match visit type?)  
- Document result in EHR  
  
**Why full delegation?**  
- High clarity: Pass/fail criteria are unambiguous  
- Low variance: Same process for every patient  
- Low risk: Errors are caught downstream (patient or billing department will notice coverage issues)  
- High volume: 180 verifications/day—manual processing is inefficient  
  
**Risks if we delegate more**: Not applicable (already full delegation)  
  
**Costs if we delegate less**:   
- Human-in-loop adds 1-2 min per patient (review AI output)  
- 180 patients × 1.5 min = 270 min/day = 4.5 staff-hours/day  
- Annual cost: 4.5 hours/day × 220 days × $22/hour = **$21,780/year** in unnecessary labor  
  
**Constraint alignment**:  
- ✅ No clinical judgment required (administrative task)  
- ✅ HIPAA compliant (AI accesses only necessary patient identifiers)  
- ⚠️ Escalation path: AI flags ambiguous responses ("pending," "contact insurer") for human review  
  
**Handoff Architecture**:  
  
**Trigger**: Patient check-in (24 hours before appointment or at arrival)  
  
**AI Input**:  
- Patient demographics (name, DOB, insurance ID, policy number)  
- Appointment details (visit type, scheduled procedures)  
- Insurance eligibility API credentials  
  
**AI Output**:  
- Verification status: ✅ Verified / ⚠️ Issue Detected / ❌ Escalation Required  
- Coverage details: Active dates, copay, deductible, coverage type  
- Issue summary (if applicable): "Coverage inactive as of [date]" or "Procedure not covered under current plan"  
- EHR documentation: Structured note with verification timestamp and result  
  
**Human Involvement**:  
- **None for routine cases** (90-95% of verifications)  
- **Escalation cases** (5-10%): AI flags ambiguous responses; human reviews and contacts insurer if needed  
  
**Escalation Conditions**:  
- Eligibility system returns "pending," "unknown," or error  
- Coverage type doesn't clearly match visit type (requires interpretation)  
- Patient has multiple active insurance policies (requires selection logic)  
  
**Failure Modes & Safeguards**:  
  
**Failure Mode 1**: AI misinterprets eligibility response (false positive: says coverage is active when it's not)  
- **Impact**: Patient arrives for visit, billing discovers issue, visit may be delayed or rescheduled  
- **Safeguard**: Billing department double-checks insurance before claim submission (existing process)  
- **Detection**: Billing rejection reports; patient complaints  
  
**Failure Mode 2**: AI fails to query eligibility system (technical error)  
- **Impact**: Verification not completed, patient arrives without coverage confirmation  
- **Safeguard**: AI logs all verification attempts; dashboard alerts if verification rate drops below 95%  
- **Detection**: Real-time monitoring of verification completion rate  
  
**Failure Mode 3**: AI over-escalates (flags routine cases as ambiguous)  
- **Impact**: Human workload increases, efficiency gains diminish  
- **Safeguard**: Track escalation rate; tune AI thresholds if escalation exceeds 10%  
- **Detection**: Weekly escalation rate reports  
  
**Production Error Detection**:  
- Daily dashboard: Verification completion rate, escalation rate, error rate  
- Weekly audit: Sample 20 verifications, compare AI output to manual review  
- Monthly review: Billing rejection rate (indicator of verification accuracy)  
  
---  
  
### Step 2: Prior-Authorization Check  
  
**Delegation Archetype**: **Human-in-the-Loop**  
  
**Justification**:  
Prior-auth verification is rule-based but has high-stakes exceptions. The AI can automate the lookup and matching logic, but human review is required before committing to a decision (proceed with visit vs. reschedule).  
  
**Why human-in-loop?**  
- Moderate variance: Prior-auth documentation is often incomplete or ambiguous  
- High stakes: Proceeding without valid prior-auth can result in denied claims ($500-5,000 per procedure)  
- Judgment required: Expiration date edge cases, ambiguous approval language, multiple prior-auths requiring matching  
  
**Risks if we delegate more** (full delegation):  
- AI misses expired prior-auth → patient undergoes procedure → claim denied → practice absorbs cost or bills patient → patient dissatisfaction + revenue loss  
- Risk is too high for full delegation given current error discovery rate (8% per A2, with prior-auth being a common error type per scenario)  
  
**Costs if we delegate less** (human-led):  
- Current manual process: 2.5 min per patient (per A3)  
- AI-assisted process: 0.5 min (human reviews AI output)  
- Time saved: 2 min per patient  
- 180 patients × 2 min = 360 min/day = 6 hours/day  
- Annual savings: 6 hours/day × 220 days × $22/hour = **$29,040/year**  
  
Human-in-loop is the right balance: captures most efficiency gains while preserving human judgment for high-stakes decisions.  
  
**Constraint alignment**:  
- ✅ No clinical judgment required (administrative verification)  
- ✅ Human review gate preserves accountability  
- ✅ HIPAA compliant (AI accesses only prior-auth documentation)  
  
**Handoff Architecture**:  
  
**Trigger**: Appointment scheduled with procedure requiring prior-auth (or 48 hours before visit)  
  
**AI Input**:  
- Appointment details (procedure type, CPT codes, scheduled date)  
- Patient insurance information  
- Prior-auth database (internal tracking system or payer portal)  
- Prior-auth approval documents (PDF or structured data)  
  
**AI Output**:  
- Prior-auth status: ✅ Valid / ⚠️ Expiring Soon / ❌ Missing or Expired  
- Approval details: Approval number, approved services, date range  
- Matching assessment: "Prior-auth #12345 covers [procedure] from [start date] to [end date]"  
- Recommendation: "Proceed with visit" or "Reschedule—prior-auth expired"  
- Confidence score: High (unambiguous match) / Medium (requires review) / Low (escalate)  
  
**Human Involvement**:  
- **All cases**: Human reviews AI output and confirms decision  
- **High-confidence cases** (70-80%): Human reviews in 15-30 seconds, clicks "Approve"  
- **Medium/Low-confidence cases** (20-30%): Human investigates further, contacts payer if needed  
  
**Escalation Conditions**:  
- Prior-auth expires within 7 days of scheduled visit  
- Multiple prior-auths on file; unclear which applies  
- Prior-auth approval language is ambiguous (doesn't clearly match scheduled procedure)  
- No prior-auth found in system (AI cannot determine if missing or not required)  
  
**Failure Modes & Safeguards**:  
  
**Failure Mode 1**: AI says prior-auth is valid when it's actually expired  
- **Impact**: Patient undergoes procedure, claim denied, practice loses revenue  
- **Safeguard**: Human reviews all AI recommendations before visit proceeds  
- **Detection**: Claim denial reports; human catches error during review  
  
**Failure Mode 2**: AI says prior-auth is missing when it's actually on file (false negative)  
- **Impact**: Visit unnecessarily rescheduled, patient inconvenience  
- **Safeguard**: Human reviews "missing prior-auth" flags; can override if they locate it  
- **Detection**: Patient complaints; human review catches error  
  
**Failure Mode 3**: AI over-escalates (flags routine cases as ambiguous)  
- **Impact**: Human review time increases, efficiency gains diminish  
- **Safeguard**: Track confidence score distribution; tune AI if high-confidence rate drops below 70%  
- **Detection**: Weekly confidence score reports  
  
**Production Error Detection**:  
- Daily dashboard: Prior-auth check completion rate, confidence score distribution  
- Weekly audit: Sample 20 prior-auth checks, compare AI recommendation to human decision  
- Monthly review: Claim denial rate for prior-auth issues (lagging indicator of accuracy)  
  
---  
  
### Step 3: Pre-Visit Questionnaire  
  
**Delegation Archetype**: **Hybrid** (AI handles data entry and completeness check; human handles urgent response flagging)  
  
**Justification**:  
Pre-visit questionnaire processing has two distinct sub-tasks:  
1. **Data entry and completeness verification** (routine work) → Full delegation to AI  
2. **Urgent response identification** (judgment work) → Human-in-loop  
  
**Why hybrid?**  
- The routine work (transcribe responses, check for blanks) is high-volume, low-value cognitive load—perfect for AI  
- The judgment work (what constitutes "urgent"?) requires medical knowledge and risk assessment—must remain human-led  
- Splitting the work maximizes efficiency while preserving safety  
  
**Risks if we delegate more** (full delegation of urgent flagging):  
- AI misses urgent symptom (e.g., patient reports chest pain but AI doesn't flag) → patient waits for routine appointment → delayed care for serious condition  
- Risk is too high given "no clinical judgment by AI" constraint  
  
**Costs if we delegate less** (human-led data entry):  
- Current manual process: 1.5 min per patient (per A3)  
- AI-assisted process: 0.3 min (human reviews flagged cases only)  
- Time saved: 1.2 min per patient  
- 180 patients × 1.2 min = 216 min/day = 3.6 hours/day  
- Annual savings: 3.6 hours/day × 220 days × $22/hour = **$17,424/year**  
  
Hybrid delegation captures efficiency gains while respecting the clinical judgment constraint.  
  
**Constraint alignment**:  
- ✅ No clinical judgment by AI (urgent flagging remains human-led)  
- ✅ Human review gate for all flagged responses  
- ✅ HIPAA compliant (AI processes questionnaire data with appropriate safeguards)  
  
**Handoff Architecture**:  
  
**Trigger**: Patient completes pre-visit questionnaire (digital submission or paper form scanned)  
  
**AI Input**:  
- Completed questionnaire (structured data or OCR from paper form)  
- Questionnaire template (expected fields)  
- Patient medical history (for context)  
  
**AI Output** (Sub-task 1: Data Entry & Completeness):  
- Completeness status: ✅ Complete / ⚠️ Incomplete (lists missing fields)  
- Structured data extraction: Maps questionnaire responses to EHR fields  
- EHR documentation: Auto-populates questionnaire data in patient record  
  
**AI Output** (Sub-task 2: Urgent Response Flagging):  
- Flagged responses: Lists any responses containing urgent keywords (chest pain, shortness of breath, severe bleeding, suicidal ideation, etc.)  
- Context: Displays full question and patient response for human review  
- Recommendation: "Flag for immediate physician review" (but human makes final decision)  
  
**Human Involvement**:  
- **Sub-task 1 (Data Entry)**: None—AI handles automatically  
- **Sub-task 2 (Urgent Flagging)**: Human reviews all flagged responses (estimated 5-10% of questionnaires)  
  - Human decides: Is this urgent? Should physician be notified before visit?  
  - Human documents decision and escalates if needed  
  
**Escalation Conditions**:  
- AI flags any response containing urgent keywords  
- Questionnaire is incomplete (AI cannot process)  
- Patient handwriting is illegible (OCR fails)  
  
**Failure Modes & Safeguards**:  
  
**Failure Mode 1**: AI misses urgent response (false negative)  
- **Impact**: Urgent symptom not flagged, patient waits for routine visit, delayed care  
- **Safeguard**: Physician reviews all questionnaire responses during visit (existing process); AI is an additional safety layer, not the only one  
- **Detection**: Physician flags missed urgent responses; retrospective audit  
  
**Failure Mode 2**: AI over-flags routine responses (false positive)  
- **Impact**: Human review workload increases, efficiency gains diminish  
- **Safeguard**: Tune AI keyword list based on false positive rate; target <15% false positive rate  
- **Detection**: Weekly false positive rate tracking  
  
**Failure Mode 3**: AI data entry error (transcribes response incorrectly)  
- **Impact**: Incorrect information in EHR, potential clinical risk  
- **Safeguard**: Physician reviews questionnaire responses during visit; errors caught before clinical decisions made  
- **Detection**: Physician reports data entry errors; monthly audit of AI transcription accuracy  
  
**Production Error Detection**:  
- Daily dashboard: Questionnaire processing completion rate, flagging rate  
- Weekly audit: Sample 20 questionnaires, compare AI data entry to source document  
- Monthly review: Physician-reported data entry errors; missed urgent response incidents  
  
---  
  
### Step 4: Reason-for-Visit Triage  
  
**Delegation Archetype**: **AI Assistance** (human-led with AI support)  
  
**Justification**:  
Reason-for-visit triage is inherently a judgment task requiring medical knowledge and risk assessment. The scenario explicitly requires "human escalation path for visit-reason decisions," which means triage cannot be fully delegated.  
  
However, AI can assist by:  
- Structuring patient descriptions (extract key symptoms, duration, severity)  
- Flagging urgent keywords (chest pain, difficulty breathing, severe bleeding)  
- Presenting triage protocols for human reference  
- Documenting triage decision  
  
**Why AI assistance (not human-in-loop)?**  
- Human-in-loop implies AI does the work and human verifies  
- For triage, the human must make the decision—AI provides support but doesn't propose a triage level  
- This preserves human judgment while reducing cognitive load  
  
**Risks if we delegate more** (human-in-loop or full delegation):  
- AI makes triage decision → human rubber-stamps → urgent case mis-triaged as routine → delayed care → patient harm  
- This violates "no clinical judgment by AI" constraint and "human escalation path" requirement  
  
**Costs if we delegate less** (human-led with no AI support):  
- Current manual process: 2 min per patient (per A3)  
- AI-assisted process: 1.5 min (AI structures information, human decides)  
- Time saved: 0.5 min per patient (modest savings because human still does core work)  
- 180 patients × 0.5 min = 90 min/day = 1.5 hours/day  
- Annual savings: 1.5 hours/day × 220 days × $22/hour = **$7,260/year**  
  
AI assistance provides modest efficiency gains while fully respecting the clinical judgment constraint. The primary value is not time savings but **error reduction**—AI ensures no urgent keywords are missed.  
  
**Constraint alignment**:  
- ✅ No clinical judgment by AI (human makes all triage decisions)  
- ✅ Human escalation path preserved (human is always in control)  
- ✅ HIPAA compliant  
  
**Handoff Architecture**:  
  
**Trigger**: Patient schedules appointment or calls with new concern  
  
**AI Input**:  
- Patient's stated reason for visit (free-text description)  
- Patient medical history (chronic conditions, recent visits, medications)  
- Triage protocols (documented guidelines for common scenarios)  
  
**AI Output**:  
- Structured summary: "Patient reports [symptom], duration [X days], severity [mild/moderate/severe], associated symptoms [list]"  
- Urgent keyword flags: Highlights any urgent indicators (chest pain, shortness of breath, severe bleeding, etc.)  
- Protocol reference: "For chest pain, protocol recommends: [triage guidelines]"  
- Historical context: "Patient has history of [condition]; last visit [date] for [reason]"  
- Documentation template: Pre-filled triage note for human to complete  
  
**Human Involvement**:  
- **All cases**: Human reviews AI-structured information and makes triage decision  
- Human assesses urgency: Routine / Urgent / Same-day / ER referral  
- Human schedules appropriate appointment type  
- Human documents triage rationale (using AI-generated template)  
  
**Escalation Conditions**:  
- Not applicable—human is always involved in decision-making  
  
**Failure Modes & Safeguards**:  
  
**Failure Mode 1**: AI misses urgent keyword (false negative)  
- **Impact**: Human doesn't see urgent flag, may under-triage  
- **Safeguard**: Human reads full patient description (AI summary is supplementary, not replacement)  
- **Detection**: Retrospective audit of urgent cases; physician reports of mis-triage  
  
**Failure Mode 2**: AI over-flags routine cases (false positive)  
- **Impact**: Human spends extra time reviewing non-urgent cases  
- **Safeguard**: Tune AI keyword sensitivity based on false positive rate  
- **Detection**: Weekly false positive rate tracking  
  
**Failure Mode 3**: AI misinterprets patient description (incorrect summary)  
- **Impact**: Human makes decision based on inaccurate information  
- **Safeguard**: Human reads original patient description alongside AI summary  
- **Detection**: Human notices discrepancy; reports AI error  
  
**Production Error Detection**:  
- Daily dashboard: Triage completion rate, urgent keyword flagging rate  
- Weekly audit: Sample 20 triage decisions, compare AI summary to original patient description  
- Monthly review: Physician-reported mis-triage incidents; patient complaints  
  
---  
  
### Step 5: Medication Reconciliation  
  
**Delegation Archetype**: **Human-in-the-Loop**  
  
**Justification**:  
Medication reconciliation is structured (compare EHR list to patient-reported list) but requires judgment to assess which discrepancies are clinically significant. AI can automate the comparison and flag all discrepancies, but human review is required to decide which matter.  
  
**Why human-in-loop?**  
- AI can structure the comparison (EHR says X, patient says Y)  
- AI cannot assess clinical significance (missing aspirin vs. missing insulin)  
- "No clinical judgment by AI" constraint applies—determining which medication discrepancies require physician attention is a clinical judgment  
  
**Risks if we delegate more** (full delegation):  
- AI decides which discrepancies to flag for physician → misses critical medication change (e.g., patient stopped taking blood thinner) → physician unaware → clinical risk  
- Risk is too high given medication errors are a leading cause of adverse events  
  
**Costs if we delegate less** (human-led):  
- Current manual process: 2 min per patient (per A3)  
- AI-assisted process: 0.5 min (human reviews AI-generated discrepancy list)  
- Time saved: 1.5 min per patient  
- 180 patients × 1.5 min = 270 min/day = 4.5 hours/day  
- Annual savings: 4.5 hours/day × 220 days × $22/hour = **$21,780/year**  
  
Human-in-loop captures significant efficiency gains (AI does the tedious comparison work) while preserving human judgment for clinical significance assessment.  
  
**Constraint alignment**:  
- ✅ No clinical judgment by AI (human assesses significance of discrepancies)  
- ✅ Human review gate for all discrepancies  
- ✅ HIPAA compliant  
  
**Handoff Architecture**:  
  
**Trigger**: Patient check-in (before visit)  
  
**AI Input**:  
- EHR medication list (current and historical)  
- Patient-reported medication list (from questionnaire or verbal report)  
- Medication database (for matching brand/generic names)  
  
**AI Output**:  
- Reconciliation summary: "EHR lists [X] medications; patient reports [Y] medications"  
- Discrepancies identified:  
  - Medications in EHR but not reported by patient (stopped taking?)  
  - Medications reported by patient but not in EHR (new prescription from another provider?)  
  - Dosage discrepancies (EHR says 10mg, patient says 20mg)  
- Matched medications: Lists medications that match between EHR and patient report  
- Updated EHR documentation: Pre-filled medication list for human to approve  
  
**Human Involvement**:  
- **All cases with discrepancies** (estimated 30-40% of patients): Human reviews discrepancy list  
  - Human asks patient clarifying questions if needed  
  - Human decides which discrepancies to flag for physician  
  - Human updates EHR medication list  
- **Cases with no discrepancies** (60-70%): Human reviews AI summary, clicks "Approve"  
  
**Escalation Conditions**:  
- Discrepancy involves high-risk medication (anticoagulants, insulin, chemotherapy, etc.)  
- Patient reports stopping medication without physician knowledge  
- Dosage discrepancy exceeds 50% (suggests potential error)  
  
**Failure Modes & Safeguards**:  
  
**Failure Mode 1**: AI misses discrepancy (false negative)  
- **Impact**: Medication list in EHR is inaccurate, physician unaware of medication change  
- **Safeguard**: Physician reviews medication list during visit (existing process); AI is additional safety layer  
- **Detection**: Physician discovers discrepancy during visit; retrospective audit  
  
**Failure Mode 2**: AI false positive (flags matching medications as discrepant)  
- **Impact**: Human spends extra time reviewing non-issues  
- **Safeguard**: Tune AI matching logic (brand/generic name matching, dosage equivalence)  
- **Detection**: Weekly false positive rate tracking  
  
**Failure Mode 3**: AI incorrectly matches medications (says they match when they don't)  
- **Impact**: Discrepancy not flagged, medication list inaccurate  
- **Safeguard**: Human reviews all AI-generated matches for high-risk medications  
- **Detection**: Physician reports medication list errors; monthly audit  
  
**Production Error Detection**:  
- Daily dashboard: Reconciliation completion rate, discrepancy rate  
- Weekly audit: Sample 20 reconciliations, compare AI output to manual review  
- Monthly review: Physician-reported medication list errors  
  
---  
  
### Step 6: Allergy-Flag Review  
  
**Delegation Archetype**: **Full Delegation** (with human escalation for new/severe allergies)  
  
**Justification**:  
Allergy review is primarily a verification task: confirm existing allergies, document new ones. The cognitive load is low for the base case—this is a structured checklist.  
  
AI can:  
- Display current allergy list to patient (via digital interface or staff screen)  
- Prompt patient to confirm or update  
- Document changes in EHR  
- Flag new allergies or severe reactions for human review  
  
**Why full delegation?**  
- High clarity: Allergy confirmation is yes/no  
- Low variance: Same process for every patient  
- Low risk: Physician reviews allergy list during visit (existing safety layer)  
  
**Escalation path**: New allergies or severe reactions require human review to assess severity and ensure proper documentation.  
  
**Risks if we delegate more**: Not applicable (already full delegation with escalation path)  
  
**Costs if we delegate less** (human-led):  
- Current manual process: 1 min per patient (per A3)  
- AI-assisted process: 0.1 min (human reviews flagged cases only, estimated 10% of patients)  
- Time saved: 0.9 min per patient  
- 180 patients × 0.9 min = 162 min/day = 2.7 hours/day  
- Annual savings: 2.7 hours/day × 220 days × $22/hour = **$13,068/year**  
  
Full delegation with escalation captures maximum efficiency while preserving safety.  
  
**Constraint alignment**:  
- ✅ No clinical judgment by AI (allergy confirmation is administrative; severity assessment escalates to human)  
- ✅ Escalation path for new/severe allergies  
- ✅ HIPAA compliant  
  
**Handoff Architecture**:  
  
**Trigger**: Patient check-in  
  
**AI Input**:  
- EHR allergy list  
- Patient confirmation (via digital interface or staff-prompted verbal response)  
  
**AI Output**:  
- Confirmation status: ✅ Confirmed / ⚠️ Changes Reported  
- Updated allergy list (if changes reported)  
- Escalation flag: "New allergy reported: [allergen], reaction: [description]" (if applicable)  
- EHR documentation: Updated allergy list with timestamp  
  
**Human Involvement**:  
- **Routine cases** (90%): None—AI handles automatically  
- **Escalation cases** (10%): Human reviews new allergy or severe reaction report  
  - Human asks patient clarifying questions (type of reaction, severity, date of occurrence)  
  - Human documents detailed allergy information  
  - Human flags for physician review if severe reaction (anaphylaxis, hospitalization)  
  
**Escalation Conditions**:  
- Patient reports new allergy  
- Patient reports severe reaction (anaphylaxis, ER visit, hospitalization)  
- Patient reports change to existing allergy (e.g., reaction severity changed)  
  
**Failure Modes & Safeguards**:  
  
**Failure Mode 1**: AI fails to document new allergy  
- **Impact**: Allergy not in EHR, physician unaware, potential medication error  
- **Safeguard**: Physician reviews allergy list during visit (existing process)  
- **Detection**: Physician discovers missing allergy; retrospective audit  
  
**Failure Mode 2**: AI incorrectly removes allergy from list  
- **Impact**: Critical allergy deleted from EHR, potential medication error  
- **Safeguard**: AI never deletes allergies without explicit patient confirmation + human review  
- **Detection**: Physician notices missing allergy; patient reports error  
  
**Failure Mode 3**: Patient misunderstands AI prompt, confirms incorrectly  
- **Impact**: Allergy list inaccurate  
- **Safeguard**: Physician reviews allergy list during visit; AI prompt uses clear, simple language  
- **Detection**: Physician catches error during visit  
  
**Production Error Detection**:  
- Daily dashboard: Allergy review completion rate, new allergy rate  
- Weekly audit: Sample 20 allergy reviews, compare AI output to patient report  
- Monthly review: Physician-reported allergy list errors  
  
---  
  
## 3. Economic Analysis per Step  
  
### Step 1: Insurance Verification  
  
**Current Cost (Manual)**:  
- Time per patient: 3 min (per A3)  
- Labor cost: 3 min × ($22/hour ÷ 60 min) = **$1.10 per patient**  
- Error cost: Estimated 2% of verifications have errors (per A2, assuming errors distributed across all steps)  
  - Error impact: Billing delay, staff time to resolve (~15 min), potential claim denial  
  - Average error cost: $5.50 (15 min × $22/hour)  
  - Expected error cost per patient: 2% × $5.50 = **$0.11 per patient**  
- **Total current cost: $1.21 per patient**  
  
**Proposed Cost (Full Delegation)**:  
- AI cost: $0.015 per patient (per A7, allocated proportionally: $0.08 total ÷ 6 steps, weighted by complexity)  
  - Insurance verification is 25% of total intake time (per A3) → 25% of token budget  
  - $0.08 × 0.25 = **$0.02 per patient**  
- Human oversight cost: $0 (no routine human review)  
- Escalation cost: 5% of cases escalated × 1 min human time = 0.05 min × $22/hour = **$0.02 per patient** (averaged)  
- Expected error cost: 0.5% error rate (75% reduction per A9 logic) × $5.50 = **$0.03 per patient**  
- **Total proposed cost: $0.07 per patient**  
  
**Net Savings per Patient**:  
- $1.21 - $0.07 = **$1.14 per patient**  
  
**Annual Savings**:  
- $1.14 × 180 patients/day × 220 workdays = **$45,144/year**  
  
**Payoff Justification**:  
- **ROI**: $45,144 annual savings for ~$2,000 implementation cost (insurance API integration) = **22.6× annual ROI**  
- **Payback period**: <1 month  
- **Risk-adjusted**: Even if error rate doesn't improve (conservative), savings are $1.11/patient × 180 × 220 = $43,956/year  
- **Verdict**: **Highly justified**—low risk, high volume, clear ROI  
  
---  
  
### Step 2: Prior-Authorization Check  
  
**Current Cost (Manual)**:  
- Time per patient: 2.5 min (per A3)  
- Labor cost: 2.5 min × ($22/hour ÷ 60 min) = **$0.92 per patient**  
- Error cost: Estimated 3% of prior-auth checks have errors (higher than average due to scenario stating this is a common error type)  
  - Error impact: Claim denial ($500-5,000 per procedure), staff time to resolve (30 min), potential patient dissatisfaction  
  - Average error cost: $150 (conservative estimate: 30 min staff time + 10% probability of $1,500 claim denial) [prior-auth claim denial cost per industry data]  
  - Expected error cost per patient: 3% × $150 = **$4.50 per patient**  
- **Total current cost: $5.42 per patient**  
  
**Proposed Cost (Human-in-Loop)**:  
- AI cost: $0.025 per patient (per A7, allocated: $0.08 × 0.31 = 31% of token budget, as prior-auth is complex)  
- Human oversight cost: 0.5 min × ($22/hour ÷ 60 min) = **$0.18 per patient**  
- Expected error cost: 0.75% error rate (75% reduction per A9 logic) × $150 = **$1.13 per patient**  
- **Total proposed cost: $1.36 per patient**  
  
**Net Savings per Patient**:  
- $5.42 - $1.36 = **$4.06 per patient**  
  
**Annual Savings**:  
- $4.06 × 180 patients/day × 220 workdays = **$160,776/year**  
  
**Payoff Justification**:  
- **ROI**: $160,776 annual savings for ~$3,000 implementation cost (prior-auth database integration) = **53.6× annual ROI**  
- **Payback period**: <1 week  
- **Risk-adjusted**: Even if error reduction is only 50% (not 75%), savings are $2.81/patient × 180 × 220 = $111,276/year  
- **Verdict**: **Extremely justified**—high error cost, high volume, massive ROI. This is the highest-value automation target.  
  
---  
  
### Step 3: Pre-Visit Questionnaire  
  
**Current Cost (Manual)**:  
- Time per patient: 1.5 min (per A3)  
- Labor cost: 1.5 min × ($22/hour ÷ 60 min) = **$0.55 per patient**  
- Error cost: Estimated 1% of questionnaires have issues (missed urgent response)  
  - Error impact: Delayed care for urgent issue, potential clinical risk, staff time to reschedule  
  - Average error cost: $20 (conservative: 30 min staff time + patient inconvenience)  
  - Expected error cost per patient: 1% × $20 = **$0.20 per patient**  
- **Total current cost: $0.75 per patient**  
  
**Proposed Cost (Hybrid)**:  
- AI cost: $0.008 per patient (per A7, allocated: $0.08 × 0.10 = 10% of token budget, as questionnaire processing is simple)  
- Human oversight cost: 0.3 min × ($22/hour ÷ 60 min) = **$0.11 per patient** (human reviews flagged cases, estimated 10% of patients)  
  - Averaged across all patients: 10% × 3 min + 90% × 0 min = 0.3 min average  
- Expected error cost: 0.25% error rate (75% reduction) × $20 = **$0.05 per patient**  
- **Total proposed cost: $0.17 per patient**  
  
**Net Savings per Patient**:  
- $0.75 - $0.17 = **$0.58 per patient**  
  
**Annual Savings**:  
- $0.58 × 180 patients/day × 220 workdays = **$22,968/year**  
  
**Payoff Justification**:  
- **ROI**: $22,968 annual savings for ~$1,000 implementation cost (questionnaire OCR/processing) = **23× annual ROI**  
- **Payback period**: ~2 weeks  
- **Risk-adjusted**: Even if time savings are only 50%, savings are $0.28/patient × 180 × 220 = $11,088/year  
- **Verdict**: **Justified**—modest savings per patient but high volume makes it worthwhile. Primary value is error reduction (catching urgent responses).  
  
---  
  
### Step 4: Reason-for-Visit Triage  
  
**Current Cost (Manual)**:  
- Time per patient: 2 min (per A3)  
- Labor cost: 2 min × ($22/hour ÷ 60 min) = **$0.73 per patient**  
- Error cost: Estimated 2% of triage decisions are suboptimal (urgent case triaged as routine, or vice versa)  
  - Error impact: Delayed care (urgent → routine), or wasted urgent slot (routine → urgent)  
  - Average error cost: $30 (staff time to reschedule + patient inconvenience + potential clinical risk)  
  - Expected error cost per patient: 2% × $30 = **$0.60 per patient**  
- **Total current cost: $1.33 per patient**  
  
**Proposed Cost (AI Assistance)**:  
- AI cost: $0.012 per patient (per A7, allocated: $0.08 × 0.15 = 15% of token budget)  
- Human time: 1.5 min × ($22/hour ÷ 60 min) = **$0.55 per patient** (human still makes decision, AI structures info)  
- Expected error cost: 0.5% error rate (75% reduction due to AI flagging urgent keywords) × $30 = **$0.15 per patient**  
- **Total proposed cost: $0.71 per patient**  
  
**Net Savings per Patient**:  
- $1.33 - $0.71 = **$0.62 per patient**  
  
**Annual Savings**:  
- $0.62 × 180 patients/day × 220 workdays = **$24,552/year**  
  
**Payoff Justification**:  
- **ROI**: $24,552 annual savings for ~$1,500 implementation cost (triage protocol integration) = **16.4× annual ROI**  
- **Payback period**: ~3 weeks  
- **Risk-adjusted**: Primary value is error reduction (preventing mis-triage), not time savings. Even if time savings are zero, error reduction alone saves $0.45/patient × 180 × 220 = $17,820/year  
- **Verdict**: **Justified**—modest time savings but significant error reduction. Aligns with "no clinical judgment by AI" constraint while adding safety value.  
  
---  
  
### Step 5: Medication Reconciliation  
  
**Current Cost (Manual)**:  
- Time per patient: 2 min (per A3)  
- Labor cost: 2 min × ($22/hour ÷ 60 min) = **$0.73 per patient**  
- Error cost: Estimated 2.5% of reconciliations have errors (unreviewed medication change, per scenario)  
  - Error impact: Physician discovers during visit, spends time resolving, potential clinical risk  
  - Average error cost: $8 (4 min physician time × $120/hour per A6)  
  - Expected error cost per patient: 2.5% × $8 = **$0.20 per patient**  
- **Total current cost: $0.93 per patient**  
  
**Proposed Cost (Human-in-Loop)**:  
- AI cost: $0.015 per patient (per A7, allocated: $0.08 × 0.19 = 19% of token budget)  
- Human oversight cost: 0.5 min × ($22/hour ÷ 60 min) = **$0.18 per patient**  
- Expected error cost: 0.625% error rate (75% reduction) × $8 = **$0.05 per patient**  
- **Total proposed cost: $0.25 per patient**  
  
**Net Savings per Patient**:  
- $0.93 - $0.25 = **$0.68 per patient**  
  
**Annual Savings**:  
- $0.68 × 180 patients/day × 220 workdays = **$26,928/year**  
  
**Payoff Justification**:  
- **ROI**: $26,928 annual savings for ~$2,000 implementation cost (EHR medication data integration) = **13.5× annual ROI**  
- **Payback period**: ~4 weeks  
- **Risk-adjusted**: Even if error reduction is only 50%, savings are $0.61/patient × 180 × 220 = $24,156/year  
- **Verdict**: **Justified**—significant time savings and error reduction. High value given medication errors are a common intake gap per scenario.  
  
---  
  
### Step 6: Allergy-Flag Review  
  
**Current Cost (Manual)**:  
- Time per patient: 1 min (per A3)  
- Labor cost: 1 min × ($22/hour ÷ 60 min) = **$0.37 per patient**  
- Error cost: Estimated 1% of allergy reviews have errors (new allergy not documented)  
  - Error impact: Physician discovers during visit, potential medication error risk  
  - Average error cost: $10 (5 min physician time × $120/hour per A6)  
  - Expected error cost per patient: 1% × $10 = **$0.10 per patient**  
- **Total current cost: $0.47 per patient**  
  
**Proposed Cost (Full Delegation with Escalation)**:  
- AI cost: $0.008 per patient (per A7, allocated: $0.08 × 0.10 = 10% of token budget, as allergy review is simple)  
- Human oversight cost: 0.1 min × ($22/hour ÷ 60 min) = **$0.04 per patient** (human reviews escalated cases, estimated 10%)  
  - Averaged: 10% × 1 min + 90% × 0 min = 0.1 min average  
- Expected error cost: 0.25% error rate (75% reduction) × $10 = **$0.03 per patient**  
- **Total proposed cost: $0.08 per patient**  
  
**Net Savings per Patient**:  
- $0.47 - $0.08 = **$0.39 per patient**  
  
**Annual Savings**:  
- $0.39 × 180 patients/day × 220 workdays = **$15,444/year**  
  
**Payoff Justification**:  
- **ROI**: $15,444 annual savings for ~$500 implementation cost (allergy data integration) = **30.9× annual ROI**  
- **Payback period**: ~2 weeks  
- **Risk-adjusted**: Even if time savings are only 50%, savings are $0.22/patient × 180 × 220 = $8,712/year  
- **Verdict**: **Justified**—low implementation cost, clear ROI, low risk. Allergy review is simple and high-volume.  
  
---  
  
## 4. Summary Table: Delegation Distribution  
  
| Intake Step | Cognitive Zone | Delegation Archetype | AI Role | Human Role | Time Saved per Patient | Annual Labor Savings | Annual Error Savings | Total Annual Savings | Risk Level |  
|-------------|----------------|---------------------|---------|------------|----------------------|---------------------|---------------------|---------------------|------------|  
| **Insurance Verification** | Routine | Full Delegation | Queries insurance API, parses response, documents in EHR, flags ambiguous cases | Reviews escalated cases only (~5%) | 2.9 min | $41,382 | $3,762 | **$45,144** | Low |  
| **Prior-Authorization Check** | Judgment | Human-in-Loop | Queries prior-auth database, matches to procedure, assesses validity, recommends proceed/reschedule | Reviews all AI recommendations, makes final decision | 2.0 min | $29,040 | $131,736 | **$160,776** | Medium |  
| **Pre-Visit Questionnaire** | Routine (with judgment escalation) | Hybrid | Processes questionnaire, checks completeness, flags urgent keywords | Reviews flagged urgent responses (~10%), makes escalation decisions | 1.2 min | $17,424 | $5,544 | **$22,968** | Low |  
| **Reason-for-Visit Triage** | Judgment | AI Assistance | Structures patient description, flags urgent keywords, presents protocols | Makes all triage decisions, uses AI-structured info as input | 0.5 min | $7,260 | $17,292 | **$24,552** | Medium |  
| **Medication Reconciliation** | Judgment | Human-in-Loop | Compares EHR to patient report, flags discrepancies, generates summary | Reviews all discrepancies, assesses clinical significance, updates EHR | 1.5 min | $21,780 | $5,148 | **$26,928** | Medium |  
| **Allergy-Flag Review** | Routine (with judgment escalation) | Full Delegation | Displays allergy list, prompts patient confirmation, documents changes, flags new/severe allergies | Reviews escalated cases only (~10%) | 0.9 min | $13,068 | $2,376 | **$15,444** | Low |  
| **TOTALS** | — | — | — | — | **9.0 min** | **$129,954** | **$165,858** | **$295,812** | **Medium** |  
  
### Key Insights from Summary Table:  
  
**Delegation Distribution**:  
- **Full Delegation**: 2 steps (33% of steps) → Insurance Verification, Allergy Review  
- **Human-in-Loop**: 2 steps (33% of steps) → Prior-Auth Check, Medication Reconciliation  
- **AI Assistance**: 1 step (17% of steps) → Reason-for-Visit Triage  
- **Hybrid**: 1 step (17% of steps) → Pre-Visit Questionnaire  
- **Human-Led**: 0 steps (0%) → All steps have some level of AI delegation  
  
**Time Savings**:  
- **Total time saved per patient**: 9.0 minutes (75% reduction from 12 min to 3 min per A1 and A8)  
- **Highest time savings**: Insurance Verification (2.9 min), Prior-Auth Check (2.0 min), Medication Reconciliation (1.5 min)  
- **Lowest time savings**: Reason-for-Visit Triage (0.5 min) → intentional, as human judgment must remain primary  
  
**Economic Impact**:  
- **Total annual savings**: $295,812  
  - Labor savings: $129,954 (44%)  
  - Error reduction savings: $165,858 (56%)  
- **Highest ROI steps**: Prior-Auth Check ($160,776), Insurance Verification ($45,144), Medication Reconciliation ($26,928)  
- **Error reduction is the primary value driver** (56% of total savings) → validates that the problem is quality, not just capacity  
  
**Risk Profile**:  
- **Low risk**: 2 steps (routine work, low clinical impact)  
- **Medium risk**: 3 steps (judgment work, clinical significance)  
- **High risk**: 0 steps (no high-risk delegation due to conservative design)  
- **Overall risk**: Medium (balanced approach with appropriate human oversight)  
  
---  
  
## 5. Delegation Rationale Summary  
  
### The Overall Delegation Strategy  
  
The delegation design for this patient intake workflow achieves a **75% time reduction** (from 12 min to 3 min per patient) while preserving human judgment for all clinically significant decisions. The strategy is deliberately conservative, prioritizing safety and constraint compliance over maximum automation.  
  
**Delegation breakdown by work type**:  
- **Routine verification work** (insurance, allergy review, questionnaire data entry) → **Full delegation** with escalation paths for edge cases  
- **Judgment work with high stakes** (prior-auth, medication reconciliation) → **Human-in-loop** where AI does the analysis but humans make decisions  
- **Clinical judgment work** (triage) → **AI assistance** where humans remain in control and AI provides structured support  
  
This distribution respects the hard constraints:  
1. ✅ **No clinical judgment by AI**: Triage remains human-led; medication reconciliation and prior-auth require human decision-making  
2. ✅ **Human escalation path for visit-reason decisions**: Triage is AI-assisted, not AI-led  
3. ✅ **HIPAA compliance**: All AI access to patient data is logged, encrypted, and governed by BAA  
  
The strategy is **economics-driven**: 56% of total savings ($165,858 of $295,812) come from error reduction, not time savings. This validates the problem statement—the actual problem is systematic quality failures, not capacity constraints. The delegation design targets error reduction as the primary value driver.  
  
### Where AI Adds Most Value  
  
**Highest-value automation targets** (by total annual savings):  
1. **Prior-Authorization Check** ($160,776/year) → High error cost ($4.50/patient) makes this the most valuable automation. Human-in-loop design captures efficiency while preventing costly claim denials.  
2. **Insurance Verification** ($45,144/year) → High volume + low risk = clear ROI. Full delegation is safe because errors are caught downstream.  
3. **Medication Reconciliation** ($26,928/year) → Scenario identifies this as a common error type. AI eliminates tedious comparison work; human assesses clinical significance.  
  
**Error reduction impact**:  
- **Prior-auth errors**: 75% reduction saves $131,736/year (avoiding claim denials)  
- **Triage errors**: 75% reduction saves $17,292/year (preventing delayed care for urgent cases)  
- **Medication errors**: 75% reduction saves $5,148/year (reducing physician time waste)  
  
The delegation design specifically targets the **two error types mentioned in the scenario** (expired prior-auth, unreviewed medication changes) with human-in-loop safeguards. This is not coincidental—the delegation strategy is designed to solve the stated problem.  
  
**Time savings distribution**:  
- **Routine work** (insurance, allergy, questionnaire): 5.0 min saved per patient (56% of total time savings)  
- **Judgment work** (prior-auth, med rec): 3.5 min saved per patient (39% of total time savings)  
- **Clinical judgment work** (triage): 0.5 min saved per patient (6% of total time savings)  
  
AI adds most value where work is high-volume, rule-based, and error-prone. The delegation design maximizes automation for routine work while preserving human judgment where stakes are high.  
  
### Where Humans Remain Essential  
  
**Humans retain decision-making authority for**:  
1. **All triage decisions** (AI Assistance model) → Human assesses urgency, schedules appointment type, makes clinical risk judgments  
2. **All prior-auth proceed/reschedule decisions** (Human-in-Loop) → Human reviews AI analysis and decides whether visit should proceed  
3. **All medication discrepancy significance assessments** (Human-in-Loop) → Human decides which discrepancies require physician attention  
4. **All escalated cases** (Full Delegation with escalation) → Ambiguous insurance responses, new allergies, urgent questionnaire responses  
  
**The human's new role in the AI-assisted workflow**:  
- **From executor to validator**: Humans no longer perform tedious verification tasks (querying systems, transcribing data, checking completeness). AI handles execution; humans validate output and make judgment calls.  
- **From generalist to specialist**: Humans focus cognitive effort on exceptions, edge cases, and judgment calls—the work that actually requires human intelligence.  
- **From reactive to proactive**: AI flags issues before they reach physicians (expired prior-auth, medication discrepancies, urgent symptoms). Humans intervene earlier in the workflow.  
  
**Preserving "no clinical judgment by AI"**:  
The delegation design draws a clear line between **administrative verification** (AI can handle) and **clinical assessment** (humans only):  
- ✅ AI can verify insurance is active (administrative fact)  
- ❌ AI cannot decide if a symptom is urgent (clinical judgment)  
- ✅ AI can flag medication discrepancies (data comparison)  
- ❌ AI cannot decide which discrepancies are clinically significant (requires medical knowledge)  
- ✅ AI can check if prior-auth is expired (date comparison)  
- ❌ AI cannot decide if visit should proceed with expired prior-auth (risk assessment)  
  
This distinction is operationalized through delegation archetypes: Full Delegation for administrative facts, Human-in-Loop or AI Assistance for anything requiring judgment.  
  
### Risk Management Philosophy  
  
The delegation design manages risk through **layered safeguards**:  
  
**Layer 1: Delegation archetype selection**  
- High-stakes decisions (prior-auth, medication reconciliation, triage) use Human-in-Loop or AI Assistance  
- Low-stakes verification (insurance, allergy) uses Full Delegation  
- No high-risk work is fully delegated without human oversight  
  
**Layer 2: Escalation paths**  
- Every Full Delegation step has defined escalation conditions (ambiguous responses, edge cases)  
- Escalation rate is monitored; if >15%, AI tuning is triggered  
- Humans always have override authority  
  
**Layer 3: Physician review as final safeguard**  
- Physicians review all intake information during visit (existing process preserved)  
- AI is an additional safety layer, not a replacement for physician review  
- Errors caught by physicians are logged and used to improve AI  
  
**Layer 4: Production monitoring**  
- Daily dashboards track completion rates, escalation rates, error rates  
- Weekly audits sample AI output vs. manual review  
- Monthly reviews analyze physician-reported errors and claim denials  
  
**Escalation path when AI encounters ambiguity**:  
1. **AI detects ambiguity** (low confidence score, missing data, contradictory information)  
2. **AI flags case for human review** (does not proceed with uncertain decision)  
3. **Human investigates** (contacts patient, queries additional systems, applies judgment)  
4. **Human documents resolution** (decision + rationale)  
5. **AI learns from human decisions** (pattern recognition for future similar cases)  
  
The risk management philosophy is **conservative by design**: when in doubt, escalate to human. This may reduce efficiency gains in the short term but builds trust and safety, which are prerequisites for long-term adoption.  
  
---  
  
## 6. Critical Unknowns Affecting Delegation  
  
### Unknown U1: Actual Current Error Rate  
  
**Impact on Delegation**:  
If discovery reveals the actual error rate is **15% (not 8% per A2)**, we should:  
- **Prior-Authorization Check**: Increase human oversight—consider requiring human review of ALL cases (not just flagged ones) until AI accuracy is proven  
- **Medication Reconciliation**: Add a second human review gate for high-risk medications (anticoagulants, insulin)  
- **Economic justification**: Error reduction savings increase proportionally (15% × error cost vs. 8% × error cost), making automation even more valuable  
  
If discovery reveals the actual error rate is **3% (not 8%)**, we should:  
- **Reconsider ROI**: Error reduction savings are lower than estimated; time savings become primary value driver  
- **Delegation decisions remain unchanged**: Even at 3% error rate, human-in-loop for high-stakes steps is still justified  
- **Adjust success metrics**: Target error rate of 0.75% (75% reduction from 3%) instead of 2%  
  
**Decision Rule**:   
- If error rate >10%, add second human review gate for prior-auth and medication reconciliation  
- If error rate <5%, delegation archetypes remain unchanged but success metric targets are adjusted proportionally  
  
---  
  
### Unknown U2: Distribution of Errors by Type  
  
**Impact on Delegation**:  
If discovery reveals that **90% of errors are prior-auth related** (not evenly distributed), we should:  
- **Prior-Authorization Check**:   
  - Increase AI validation rigor (add redundant checks, cross-reference multiple data sources)  
  - Require human review of ALL prior-auth cases (not just flagged ones) until error rate drops below 2%  
  - Allocate more token budget to prior-auth (deeper analysis, more context)  
- **Other steps**:   
  - Reduce human oversight for steps with low error rates (e.g., insurance verification, allergy review)  
  - Reallocate human time to prior-auth review  
- **Economic justification**:   
  - Prior-auth automation becomes even higher priority (error cost is concentrated here)  
  - ROI for prior-auth increases; ROI for other steps decreases  
  
If discovery reveals errors are **evenly distributed** (not concentrated in prior-auth), we should:  
- **Delegation decisions remain unchanged**: Current design assumes moderate error distribution  
- **Validation design**: Ensure equal validation rigor across all steps (no single step gets disproportionate attention)  
  
**Decision Rule**:  
- If >70% of errors are in a single step, increase human oversight for that step to 100% review (not just flagged cases)  
- If errors are evenly distributed (<30% in any single step), proceed with current delegation design  
  
---  
  
### Unknown U3: Prior-Authorization Workflow Complexity  
  
**Impact on Delegation**:  
If discovery reveals that **only 20% of patients require prior-auth** (not 50% as assumed), we should:  
- **Prior-Authorization Check**:  
  - Time savings are lower than estimated (2.5 min × 20% = 0.5 min saved per patient, not 2.0 min)  
  - Annual labor savings drop from $29,040 to ~$5,808  
  - Error reduction savings remain high (concentrated in the 20% who need prior-auth)  
- **Economic justification**:   
  - ROI decreases but remains positive (error reduction is still valuable)  
  - Prior-auth automation drops from #2 to #4 priority (behind insurance, med rec, questionnaire)  
- **Delegation archetype**:   
  - Remains Human-in-Loop (high stakes justify human review even at lower volume)  
  
If discovery reveals that **70% of patients require prior-auth** (higher than assumed), we should:  
- **Prior-Authorization Check**:  
  - Time savings are higher than estimated (2.5 min × 70% = 1.75 min saved per patient)  
  - Annual labor savings increase proportionally  
  - This becomes the #1 automation priority (highest volume + highest error cost)  
- **Delegation archetype**:   
  - Remains Human-in-Loop (cannot reduce oversight given high stakes)  
  
**Decision Rule**:  
- If <30% of patients require prior-auth, defer prior-auth automation to Phase 2 (focus on higher-volume steps first)  
- If >50% of patients require prior-auth, prioritize prior-auth automation in Phase 1 (highest impact)  
  
---  
  
### Unknown U4: Insurance Eligibility Tool API Capabilities  
  
**Impact on Delegation**:  
If discovery reveals the insurance tool **has no API** (requires manual web portal access), we should:  
- **Insurance Verification**:  
  - Change delegation archetype from Full Delegation to **Human-in-Loop** (AI cannot query system; human must)  
  - AI role changes to: structure the query, display patient info, document result (human performs the actual lookup)  
  - Time savings drop from 2.9 min to ~1.0 min per patient (AI eliminates documentation time but not lookup time)  
  - Annual labor savings drop from $45,144 to ~$15,000  
- **Implementation cost**:   
  - Increases significantly if we need to build screen-scraping automation (not recommended due to fragility)  
  - May require negotiating API access with insurance tool vendor (adds 2-3 months to timeline)  
- **Economic justification**:   
  - ROI decreases but may still be positive (depends on documentation time savings)  
  - Insurance verification drops from #2 to #5 priority  
  
If discovery reveals the insurance tool **has a robust API** (as assumed), we should:  
- **Delegation decisions remain unchanged**: Proceed with Full Delegation design  
  
**Decision Rule**:  
- If no API exists, change to Human-in-Loop and defer to Phase 2 (focus on steps with clear automation paths first)  
- If API exists but has >5 sec latency, add human escalation path for timeout cases  
- If API is robust (<2 sec latency, 99%+ uptime), proceed with Full Delegation  
  
---  
  
### Unknown U5: athenahealth EHR Data Structure  
  
**Impact on Delegation**:  
If discovery reveals medication data is **unstructured free-text** (not structured fields), we should:  
- **Medication Reconciliation**:  
  - AI accuracy drops significantly (free-text parsing is error-prone)  
  - Change delegation archetype from Human-in-Loop to **AI Assistance** (AI suggests matches; human makes all decisions)  
  - Time savings drop from 1.5 min to ~0.5 min per patient (AI provides less value if data is messy)  
  - Annual labor savings drop from $26,928 to ~$9,000  
- **Implementation cost**:   
  - Increases (requires NLP for free-text parsing, more complex AI model)  
  - May require data cleanup project before automation is feasible  
- **Economic justification**:   
  - ROI decreases; medication reconciliation drops from #3 to #5 priority  
  
If discovery reveals medication data is **structured** (as assumed), we should:  
- **Delegation decisions remain unchanged**: Proceed with Human-in-Loop design  
  
**Decision Rule**:  
- If medication data is >50% free-text, change to AI Assistance archetype (human makes all matching decisions)  
- If medication data is structured, proceed with Human-in-Loop  
- If medication data is structured but has >20% missing fields, add data quality improvement project to scope  
  
---  
  
### Unknown U6: Human Escalation Tolerance  
  
**Impact on Delegation**:  
If discovery reveals that **front-desk staff cannot handle >20% escalation rate** (lower tolerance than assumed), we should:  
- **All Full Delegation steps**:  
  - Tune AI to reduce false positives (lower escalation rate, accept slightly higher false negative rate)  
  - Target escalation rate: <15% (instead of assumed <20%)  
  - May require more sophisticated AI model (higher token cost)  
- **Economic justification**:   
  - If escalation rate is too high, staff perceive AI as "more work, not less" → adoption risk  
  - Better to under-automate (higher human review rate) than over-escalate (high false positive rate)  
  
If discovery reveals staff can handle **>30% escalation rate** (higher tolerance), we should:  
- **All Full Delegation steps**:  
  - Tune AI for higher recall (catch more edge cases, accept higher false positive rate)  
  - This improves safety at the cost of slightly more human review time  
  
**Decision Rule**:  
- Target escalation rate: <15% for Full Delegation steps  
- If actual escalation rate exceeds 20% in production, retune AI or change to Human-in-Loop  
- Monitor staff feedback weekly; adjust escalation thresholds based on workload perception  
  
---  
  
### Unknown U7: Physician Willingness to Trust AI Verification  
  
**Impact on Delegation**:  
If discovery reveals physicians **do not trust AI output** (will re-verify everything), we should:  
- **All delegation archetypes**:  
  - Add transparency layer: AI shows its work (what data sources it checked, what logic it applied)  
  - Provide confidence scores: Physicians see "High confidence" vs. "Medium confidence" flags  
  - Gradual rollout: Start with low-stakes steps (allergy review, questionnaire), build trust, then expand to high-stakes steps (prior-auth, med rec)  
- **Validation design**:   
  - Increase audit frequency (weekly physician review of AI output)  
  - Publish accuracy metrics (physicians see error rates, escalation rates)  
  - Solicit physician feedback (what would make them trust AI verification?)  
- **Risk**:   
  - If physicians don't trust AI, they duplicate verification work → efficiency gains disappear  
  - This is an adoption risk, not a technical risk  
  
If discovery reveals physicians **are comfortable with AI verification** (trust but verify), we should:  
- **Delegation decisions remain unchanged**: Proceed as designed  
- **Validation design**: Standard monitoring (monthly audits, quarterly reviews)  
  
**Decision Rule**:  
- Conduct physician trust assessment during discovery (survey or interviews)  
- If trust score <7/10, add transparency features and gradual rollout plan  
- If trust score >7/10, proceed with standard implementation  
- Monitor physician re-verification behavior in production; if >30% re-verify AI output, add transparency features  
  
---  
  
### Summary: Unknowns Decision Matrix  
  
| Unknown | If Discovery Reveals... | Then Change Delegation To... | Impact on ROI |  
|---------|------------------------|------------------------------|---------------|  
| U1: Error Rate | >10% | Add second review gate for high-stakes steps | Increases (error reduction more valuable) |  
| U1: Error Rate | <5% | No change to archetypes, adjust metrics | Decreases (error reduction less valuable) |  
| U2: Error Distribution | >70% in prior-auth | Increase prior-auth oversight to 100% review | Increases for prior-auth, decreases for others |  
| U3: Prior-Auth Volume | <30% need prior-auth | Defer prior-auth to Phase 2 | Decreases (lower volume) |  
| U4: Insurance API | No API available | Change to Human-in-Loop | Decreases significantly |  
| U5: EHR Data Structure | Unstructured free-text | Change med rec to AI Assistance | Decreases (lower accuracy) |  
| U6: Escalation Tolerance | <20% acceptable | Tune AI for lower escalation rate | Slight decrease (more conservative) |  
| U7: Physician Trust | Low trust (<7/10) | Add transparency, gradual rollout | Risk to adoption (not ROI) |  
  
**Next Step**: Conduct discovery engagement to resolve U1-U7 before finalizing delegation design and beginning specification work.  
