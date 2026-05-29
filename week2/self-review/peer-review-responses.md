# Peer Review Response — Cognitive Load Map Questions

**Date**: 2026-05-05  
**Reviewer Questions Source**: peer-review.md  
**Response Author**: Alexandra Rendon

---

## JtD-1: Verify Insurance Eligibility for Scheduled Visit

### Q1: "Why medium cognitive zone for an API call?" (Data retrieval zone)

**Answer**: The "Data retrieval" zone is scored MEDIUM (not LOW) because it involves **two systems with different schemas** that must be coordinated:

1. **athenahealth query**: Pull patient ID, insurance info, appointment type, last verification date (structured, but multi-field)
2. **Availity API call**: Send structured query with insurance details, wait for response

**Why MEDIUM cognitive load**:
- Front-desk must **map athenahealth insurance format to Availity query format** (insurer names vary: "UnitedHealthcare Choice PPO" in athenahealth vs. "UHC" in Availity)
- Must **select correct verification type** based on appointment type (e.g., pre-procedure vs. routine visit)
- **Error handling**: If Availity times out or returns ambiguous response, front-desk must decide whether to retry or escalate

**Supporting evidence**: Cognitive map Micro-Task Inventory (Section 2) scores "Query Availity for insurance eligibility" as Input Structure = HIGH (structured API) but Turn-Taking = MEDIUM (API call requires coordination between systems).

---

### Q2: "Diagnosis is not part of insurance eligibility verification, is it? Should this line here?"

**Answer**: **Yes, "Diagnosis" belongs here** — but the term is cognitive mapping terminology, not clinical diagnosis.

**Cognitive Zone Definition** (from atx-concepts.md):
- **Diagnosis (cognitive)** = interpreting inputs, identifying patterns, determining what type of situation this is

**In JtD-1 context**: When Availity verification **fails** (30% of cases [A1]), front-desk must **diagnose why it failed**:
- Is it an expired policy? (error code: "coverage inactive")
- Is it a misspelled patient name? (error code: "member not found")
- Is it Medicaid managed care complexity? (error code: "requires manual verification")
- Is it a stale verification >6 months old? (requires checking last verification date in athenahealth)

**This is pattern recognition** (HIGH cognitive load) because:
- Availity error codes are semi-structured (not always clear)
- Front-desk must **interpret error in context of patient history** (e.g., "member not found" for a chronic patient who's been verified 10 times → likely system error, not actually uninsured)

**Supporting evidence**: Artefact 5.3 shows patient TJ received a $340 surprise bill because verification was stale (>6 months). Front-desk didn't **diagnose** that re-verification was needed.

---

### Q3: "What's the point of re-query? Is there a case for this?"

**Answer**: **Yes, re-query is a valid decision path** for specific Availity failure scenarios.

**Re-query cases**:

1. **Timeout/System Error**: Availity API times out or returns "system unavailable" → retry after 5 minutes
2. **Name/DOB Mismatch**: Availity returns "member not found" → front-desk checks if patient name spelling differs in athenahealth vs. insurance card → re-query with corrected spelling
3. **Effective Date Edge Case**: Patient's new insurance just started (e.g., started 1st of month, verification attempted on 2nd) → Availity says "coverage not found" → re-query with different effective date parameter
4. **Medicaid Managed Care Plan Selection**: Patient has Medicaid but multiple managed care plan options (Wellpath vs. AmeriHealth) → initial query uses wrong plan → re-query with correct plan code

**Supporting evidence**: Cognitive map Section 1 states "30% fail auto-verify [A1], requiring interpretation of Availity response codes, patient history, prior verification dates". Some of these 30% are solvable via re-query with corrected parameters (not all require Dana escalation).

---

### Q4: "Was this for insurance eligibility verification via Availity? I think it was about the authorization status via athenahealth (JtD-2)."

**Answer**: **You're partially correct** — there's a distinction, but re-verification timing applies to **both**.

**Clarification**:
- **JtD-1 (Insurance Verification)**: Dana's >6 month re-verification rule [A3] applies to **eligibility status** (is patient currently insured?) checked via Availity
- **JtD-2 (Prior Authorization)**: PA submission/chase timing applies to **procedure-specific authorization** (is this specific procedure approved?) tracked in athenahealth + Dana's Google Sheet

**Why the >6 month rule is in JtD-1**:
- Artefact 5.3 explicitly shows **billing failure** from stale **insurance verification** (patient TJ's eligibility was last verified 6+ months ago, system pulled outdated self-pay record from 2022)
- This is **not about PA status** — it's about foundational insurance eligibility
- Dana's note in Artefact 5.3: "Patient verification refresh window > 6 months caused billing miss... Need to discuss." → This is eligibility re-verification, not PA chase

**Post-coach validation** (A3: VERY HIGH confidence): ">6mo + chronic patient (≥3 visits/year); plus sub-rules for Medicaid (every 3mo), Medicare Advantage (Q4), new insurance (next visit)"

**Supporting evidence**: Coach validation confirmed this rule exists for **eligibility verification** (JtD-1), not just PA chase (JtD-2).

---

## JtD-2: Determine Prior Authorization Status and Chase Pending PAs

### Q5: "'5-7 days' seems vague. How do we choose the exact trigger time?"

**Answer**: **"5-7 days" is intentionally vague in the trigger description** because the exact timing is **insurer-specific and learned** — this is the core problem JtD-2 solves.

**Why vague**:
- **Documented SLA**: Most insurers state "5 business days" in their PA requirements
- **Lived SLA (Dana's patterns [A2])**: Actual approval timing varies by insurer:
  - Humana: Always 6 days, never 5
  - UnitedHealthcare Choice: 6-7 days
  - BCBS PPO: 3 days
  - Medicare: 4-5 days
  - Wellpath: 7 days (and always denies colonoscopy first time)
  - Aetna: Unpredictable (sometimes 3, sometimes 7)

**Exact trigger time determination**:
- Dana submits PA 5-7 days before procedure (as soon as procedure is scheduled)
- Dana then **calculates chase date** using her learned insurer-specific pattern (not the stated 5-day SLA)
- Example: PA submitted 04/01 for Humana → Dana's Google Sheet shows "target chase 04/07" (submission date + 6 days, not 5)

**This is the agent's value proposition**: Replace Dana's manual timing calculation (locked in her head + Google Sheet [A7]) with agent that learns insurer patterns and recommends optimal chase date.

**Supporting evidence**: Artefact 5.1 (Dana's Google Sheet) shows 5 PAs with varying actual approval times, Dana's handwritten notes: "Humana always exactly 6 days; never 5", "UHC Choice is always 6 days, sometimes 7", "Aetna fast this month, unusual"

---

### Q6: "Why is Dana the primary actor here? Shouldn't front-desk do this work?"

**Answer**: **Dana is primary actor because PA chase requires institutional knowledge and judgment** that front-desk doesn't have.

**Why Dana, not front-desk**:

1. **Insurer-specific timing patterns [A2]** are locked in Dana's head (11 years of learning):
   - Front-desk doesn't know "Humana always 6 days, not 5"
   - Front-desk doesn't know "Wellpath always denies colonoscopy first time"

2. **Dana's Google Sheet [A7]** is her personal tracking tool:
   - Coach validation (Q4): "If you were on vacation for two weeks, what would happen to PA chases? Would front-desk handle them, or would they wait for you?" → Answer: Front-desk waits for Dana or guesses (knowledge not transferred)

3. **PA denials require clinical judgment**:
   - When Wellpath denies colonoscopy, Dana knows to attach "prior visit note" from August (not documented in Availity or athenahealth)
   - When insurer requests "medical necessity documentation", Dana coordinates with physician to get clinical justification

4. **Front-desk does structured submission**:
   - Front-desk can fill out PA forms in athenahealth (structured data entry)
   - But **chase timing decision** and **denial workarounds** are Dana's domain

**Supporting evidence**: 
- Cognitive map Section 4 "Lived Process Narrative" Gap 2: "Dana's Insurer-Specific Chase Timing Patterns [A2, A4, A7]" — "Dana checks her Google Sheet daily, calculates chase timing based on learned patterns... When Dana is out sick or on vacation, PA chases either wait or front-desk guesses"
- Coach validation [A11: VERY HIGH]: "Patterns locked in my head; front-desk doesn't know insurer-specific timing"

---

### Q7: "Where did insurer portals (varying) come from? Were they mentioned in the scenario?"

**Answer**: **Insurer portals are implicit in real-world PA workflows** but not explicitly mentioned in Scenario 5 brief. This is **inferred from lived work reality**.

**Why insurer portals exist**:
- After Dana submits PA via athenahealth, insurers process it in **their own systems** (not athenahealth)
- To check PA status, Dana must either:
  1. **Phone the insurer** (unstructured, 5-10 min hold time)
  2. **Log into insurer's web portal** (UnitedHealthcare has provider portal, Aetna has provider website, etc.)
  3. **Wait for athenahealth status update** (delayed; insurers don't push real-time updates to athenahealth)

**Evidence for insurer portals**:
- Artefact 5.1 shows Dana tracking "Status" column manually (Pending, Approved, Denied)
- Dana's notes: "UHC Choice is always 6 days, sometimes 7" → She's checking UHC's portal or calling them to get this timing data
- Cognitive map Section 4: "Real work: Dana checks her Google Sheet daily, calculates chase timing..., phones insurers at the right time" → "Phones insurers" implies she's not getting real-time status from athenahealth alone

**Why "varying"**: Each insurer has different portal/phone workflow (no standardization across healthcare industry)

**System inventory note** (Agent Mapping Section 4): "Insurer Portals: No standard API across insurers; agent relies on athenahealth as source of truth (assumes Dana/front-desk updates status after portal checks)" — pragmatic workaround since portals lack APIs

---

### Q8: "Why does it have very high cognitive zone? Isn't it simple to just query the approvals in advance based on the insurer rules?"

**Answer**: **VERY HIGH cognitive load because insurer rules are *learned patterns*, not documented rules** — and patterns change over time.

**Why not simple**:

1. **No documented rules exist**:
   - Insurers state "5 business days" SLA, but lived reality is Humana=6d, UHC=7d, Aetna=unpredictable
   - Denial patterns (Wellpath colonoscopy→attach prior visit note) are **not in insurer PA forms** — Dana discovered through trial-and-error

2. **Patterns are empirical, not rule-based**:
   - Artefact 5.1 shows Dana has observed "Humana always exactly 6 days; never 5" over 11 years [A2]
   - Coach validation (Q2): "How many times did Wellpath colonoscopy denial happen before you realized it was consistent?" → Answer: 30-40 occurrences over 6 years, 100% consistent pattern [A4: VERY HIGH]

3. **Patterns require temporal reasoning**:
   - "Humana SLA is 6 days" is not in any system → Dana must calculate: submission date + 6 days = chase date
   - Coach validation (Q3): "Has an insurer ever changed their PA SLA in last 2 years?" → Answer: Yes, UHC changed 18 months ago; Dana tracks and adjusts [A2: HIGH]

4. **Context-dependent judgment**:
   - If PA is submitted <3 days before procedure (urgent), normal chase timing doesn't apply → escalate immediately
   - If Aetna (unpredictable), can't rely on pattern → Dana uses clinical judgment

**This is institutional knowledge capture** — the highest-value unlock of the agent. Dana's 11 years of pattern learning is locked in her head + Google Sheet [A7, A11]. Agent learns from her corrections during 3-6 month learning phase.

**Supporting evidence**: Phase 4 Prioritization scores JtD-2 as Non-Determinism=5 (highest score) because "Chase timing requires synthesis of: submission date + insurer + stated SLA + Dana's learned actual SLA"

---

### Q9: "Where did Insurer portal come from?" (Breakpoint: System → Human)

**Answer**: Same as Q7 — **inferred from real-world PA workflows**. See Q7 response above.

**Additional context for this breakpoint**:
- **"Insurer portal doesn't update; requires phone call"** = When Dana checks insurer portal and status still shows "Pending" (no update), she must phone the insurer to get verbal status
- This is **System → Human breakpoint** because automated system (portal) fails to provide needed information → human must use unstructured communication (phone call) to get answer

---

### Q10: "Does a physician provide the additional documentation? Aren't the previous procedures stored in athenahealth, so front-desk can do that?"

**Answer**: **Physician must provide *clinical justification*, not just procedural records** — front-desk cannot make clinical statements.

**Why physician is required**:

1. **PA denials often request "medical necessity documentation"**:
   - Insurer: "Why is this colonoscopy medically necessary for this patient?"
   - Dana cannot answer this (not a clinician)
   - Front-desk cannot answer this (no clinical training)
   - **Physician must write**: "Patient has family history of colon cancer + rectal bleeding symptoms; colonoscopy medically indicated per [clinical guideline]"

2. **Previous procedure records ≠ clinical justification**:
   - athenahealth stores *what procedures were done* (e.g., "Colonoscopy performed 08/15/2023")
   - But insurer denial asks *why new procedure is needed* (clinical rationale)
   - Example (Artefact 5.1): "Wellpath always denies colonoscopy first time — needs prior visit note"
     - "Prior visit note" = physician's clinical note from August visit explaining symptoms + diagnosis
     - Front-desk can attach the note to resubmission, but cannot *write* clinical justification

3. **Clinical judgment required for edge cases**:
   - If insurer denies due to "not meeting frequency guidelines" (e.g., patient had colonoscopy 2 years ago, insurer says "too soon, guidelines say every 5 years"), physician must decide:
     - Is there clinical exception? (patient's symptoms warrant earlier screening)
     - Should we appeal with clinical justification?
     - Should we delay procedure until guideline-compliant?

**Dana's role**: Coordinate between insurer (what documentation they need) and physician (get clinical note/justification) → Dana compiles resubmission package

**Supporting evidence**: Cognitive map Breakpoint "Dana → Physician: Denial requires additional clinical documentation" + Autonomy Matrix (Agent Mapping Section 3): "Clinical Judgment Required: Denial reason requires physician input (e.g., 'medical necessity not demonstrated') → Escalate to Dana → Dana coordinates with physician"

---

### Q11: "I think 'in her head' shouldn't be here. Dana does not do the prior authorization status check - front-desk does that using Dana's Google Sheet."

**Answer**: **"In her head" is correct** — front-desk does **not** use Dana's Google Sheet patterns for chase timing decisions.

**Clarification**:

1. **What front-desk does**: Submits PA forms in athenahealth (structured data entry)

2. **What Dana does**:
   - Maintains Google Sheet with submission dates, insurers, target chase dates, notes
   - **Calculates chase timing** using insurer-specific patterns (Humana=6d, UHC=7d) **in her head**
   - Phones insurers at optimal time based on calculated timing
   - Updates Google Sheet with outcomes

3. **Front-desk does NOT use Google Sheet for decisions**:
   - Coach validation (Q4): "If you were on vacation, would front-desk handle PA chases?" → "Front-desk waits or guesses"
   - Coach validation [A9: HIGH]: "4-person team rotates between 2 locations; training doesn't stick; patterns locked in Dana's head"
   - **Google Sheet is Dana's personal tool**, shared with front-desk for visibility, but front-desk doesn't execute chase timing logic from it

4. **"In her head" specifically refers to**:
   - Pattern knowledge: "Humana always 6 days, not 5" (not written in athenahealth or SOP [A11])
   - Denial workarounds: "Wellpath colonoscopy needs prior visit note" (not documented)
   - When patterns change: "Aetna fast this month, unusual" (Dana adapts in real-time)

**Supporting evidence**: 
- Cognitive map Section 4 Gap 2: "Dana's patterns aren't documented in athenahealth or practice SOPs [A11]. When Dana is on vacation, PA chases wait or front-desk guesses."
- Assumption [A11: VERY HIGH]: "Dana has no formal system for surfacing learned patterns to front-desk team beyond Google Sheet. Patterns locked in my head; front-desk doesn't know insurer-specific timing."

---

## Section 6: Delegation Archetype Assignment (Preliminary)

### Q12: "Why is this not automatic (rule-based)? Availity has some documented API with failure codes - why is Dana involved here?"

**Task**: Interpret Availity failure codes  
**Archetype**: Agent-led + Human Oversight

**Answer**: **Availity failure codes are semi-structured and require contextual interpretation** — not simple error code → action mapping.

**Why not rule-based**:

1. **Error codes are ambiguous**:
   - "Member not found" could mean:
     - Patient is actually uninsured
     - Patient name misspelled in athenahealth vs. insurance card
     - Patient's insurance changed recently (not updated in athenahealth)
     - Availity system error (rare, but happens)
   - **Context required**: Front-desk must check patient history (chronic patient who's been verified 10 times? → likely system error, not uninsured)

2. **Medicaid managed care complexity [A1]**:
   - Medicaid patients often enrolled in managed care plans (Wellpath, AmeriHealth, etc.)
   - Availity error: "Plan not found" → Front-desk must determine which managed care plan patient is enrolled in
   - **This is HIGH exception rate** (30% of verifications fail [A1]), disproportionately Medicaid

3. **Dana's role: Validation during learning phase**:
   - Agent learns error code patterns from historical data (30% failures)
   - During learning phase (1 month), Dana reviews agent's interpretation: "Agent says 'member not found' → escalate to patient for insurance card verification — correct?"
   - Dana corrects when agent misinterprets (e.g., "No, that patient just got new Medicaid card last week, try re-query with new plan code")
   - After 1 month, agent handles predictable error codes autonomously; escalates Medicaid managed care to Dana

**Why "Agent-led + Human Oversight" not "Fully Agentic"**: Initial validation phase ensures agent learns correct patterns. Production phase: agent handles most automatically, escalates Medicaid edge cases.

**Supporting evidence**: Micro-Task Inventory (Section 2) scores "Interpret Availity failure codes" as Input Structure = MEDIUM (semi-structured error codes + patient context), Decision Determinism = MEDIUM (pattern-based), Exception Frequency = HIGH (30% fail rate)

---

### Q13: "Why is this not automatic (rule-based)?" (Determine re-verification timing)

**Task**: Determine re-verification timing  
**Archetype**: Agent-led + Human Oversight

**Answer**: **Re-verification rule has edge cases and sub-rules** that require validation before full automation.

**Base rule [A3]**: >6 months + chronic patient (≥3 visits/year) → re-verify

**Sub-rules** (post-coach validation [A3: VERY HIGH]):
- Medicaid: Re-verify every 3 months (eligibility changes frequently)
- Medicare Advantage: Re-verify in Q4 (annual enrollment period)
- New insurance: Re-verify at next visit (even if <6 months)

**Why not immediately rule-based**:

1. **"Chronic patient" definition needs validation**:
   - ≥3 visits/year is Dana's heuristic, but what about edge cases?
   - Patient with 2 visits/year but high-risk conditions (diabetes, heart disease) → should they be treated as chronic?
   - Dana validates: "Yes, ≥3 visits/year is the cutoff; high-risk conditions don't change the rule"

2. **Sub-rule edge cases**:
   - Medicaid 3-month rule: Does it apply to all Medicaid, or only managed care?
   - Medicare Advantage Q4 rule: Does it apply if patient just enrolled mid-year?
   - Dana validates these during 1-month pilot

3. **Agent-led + Dana approval initially**:
   - Agent flags: "Patient last verified 7 months ago, ≥3 visits/year → recommend re-verification"
   - Dana reviews: "Correct" or "No, patient switched to Medicare Advantage last month, already re-verified"
   - After 1 month, agent handles autonomously (rule fully encoded)

**Transition to Fully Agentic**: After rule validation (1 month), becomes fully automated. Dana spot-checks 5% of re-verification triggers.

**Supporting evidence**: Delegation Matrix (Phase 3) notes: "Tacit rule can be encoded (>6mo for chronic patients), but needs Dana to validate rule completeness" — validation phase ensures no edge cases missed.

---

### Q14: "Why is this not automatic (rule-based)?" (Determine when to chase PA)

**Task**: Determine when to chase PA  
**Archetype**: Agent-led + Human Oversight

**Answer**: **Insurer-specific patterns are learned empirically over 3-6 months, not encoded as rules upfront** — this is machine learning, not rule-based automation.

**Why not rule-based**:

1. **No documented rules exist**:
   - Insurers don't publish "We approve PAs in exactly 6 days"
   - Dana discovered "Humana always 6 days" through 11 years of observation [A2]
   - **Agent must learn patterns from historical data** (Dana's Google Sheet) + corrections during learning phase

2. **Patterns change over time**:
   - Coach validation (Q3): "UHC changed SLA 18 months ago; Dana adjusted"
   - Agent must **detect anomalies** (approval arrives 2+ days earlier/later than predicted) → flag to Dana for pattern update
   - This is **not static rules** — it's adaptive pattern learning

3. **Learning phase (3-6 months)**:
   - Month 1-6: Dana approves 100% of chase recommendations; agent learns from corrections
   - Example: Agent says "Chase Humana on day 5", Dana corrects "No, wait until day 6" → Agent updates Humana pattern
   - After 6 months, agent has learned 15+ insurer patterns → Production phase: autonomous for predictable insurers, escalates Aetna (unpredictable)

4. **Why not "Fully Agentic" immediately**: Can't encode rules we don't have. Dana's institutional knowledge [A2, A4] exists as tacit patterns, not documented rules. Agent must learn through reinforcement.

**Transition to Fully Agentic (Month 7+)**: Agent handles Humana, UHC, BCBS, Medicare, Wellpath autonomously. Dana spot-checks 20% of cases + reviews Aetna (unpredictable insurer).

**Supporting evidence**: 
- Phase 4 Prioritization: JtD-2 Non-Determinism=5 (highest) because patterns are learned, not rule-based
- Agent Mapping Delegation Archetype: "Learning Phase (Months 1-6): Agent-led + Human Oversight → Production Phase (Month 7+): Fully Agentic for Predictable Insurers"

---

### Q15: "IMO, for Wellpath we should have a rule to always submit these extra documents instead of extending the approval time with resubmissions."

**Task**: Interpret PA denial & resubmit  
**Suggestion**: Preemptively attach prior visit note for Wellpath colonoscopy PAs

**Answer**: **Excellent suggestion — this is exactly the agent's value proposition.** You've identified the optimization Dana has already implemented.

**Current state** (Dana's workaround):
- Artefact 5.1 footer note: "Wellpath colonoscopy denial pattern — they want the prior visit note attached, **never says so on the form**. **Standing rule: include with submission, save the resubmit cycle.**"
- Dana **already preemptively attaches** prior visit note to Wellpath colonoscopy PAs (she learned this pattern after 30-40 denial cycles [A4])

**Why it's not universally applied**:
1. **Pattern is in Dana's head** [A11], not in athenahealth workflow or front-desk training
2. **Front-desk doesn't know** to attach prior visit note when submitting Wellpath colonoscopy PA
3. **If Dana is out**, front-desk submits without note → gets denied → waits for Dana to return for resubmission

**Agent design incorporates this**:
- Agent learns: "Wellpath + colonoscopy → preemptively attach prior visit note from most recent GI visit"
- Agent flags to Dana at **submission time** (not after denial): "Attaching prior visit note per Wellpath pattern"
- This **prevents denial cycle** (1-2 week delay eliminated)

**Why archetype is "Human-led + Agent Support" not "Fully Agentic"**:
- Dana must **approve which clinical document to attach** (agent suggests "prior visit note from 08/15", Dana confirms it's the correct note)
- Some denial reasons are **novel** (not in agent's pattern library) → Dana must use judgment

**Implementation note**: Agent Mapping Activity Catalog (Section 2) includes task "Suggest resubmission workaround" with note: "Example: 'Wellpath colonoscopy denial' → match pattern 'attach prior visit note'" — this is **proactive suggestion at submission**, not reactive after denial (when pattern is known).

**Supporting evidence**: Coach validation [A4: VERY HIGH]: "Wellpath colonoscopy 30-40 occurrences over 6 years, 100% consistent. Standing rule in my head." Agent systematizes this standing rule.

---

## Summary of Key Themes

### 1. **Why "Agent-led + Human Oversight" vs. "Fully Agentic"**
- **Learning phase design**: Agent learns patterns from historical data + Dana's corrections (3-6 months)
- **Production phase**: Agent handles predictable cases autonomously; Dana spot-checks + handles edge cases
- **Rationale**: Dana's institutional knowledge [A2, A4, A7] is tacit (not documented) → agent must learn through reinforcement, not encode rules upfront

### 2. **Why cognitive load scores are HIGH for "simple" tasks**
- **Context dependency**: Tasks require interpreting semi-structured data in context of patient history, insurer patterns, clinical constraints
- **Institutional knowledge**: Dana's 11 years of pattern learning (not documented anywhere [A11]) is precisely what makes these tasks HIGH cognitive load for front-desk (they don't have the knowledge)
- **Exception rate**: 30% of verifications fail [A1], requiring judgment → not simple API calls

### 3. **Inferred real-world elements** (insurer portals, phone calls)
- Healthcare PA workflows inherently involve **multiple systems** (athenahealth, insurer portals, phone calls) even if not explicitly stated in scenario brief
- **Lived work vs. Documented work**: Scenario brief is simplified; cognitive map captures real-world complexity through assumption validation + coach role-play

### 4. **Dana vs. Front-desk responsibility**
- **Front-desk**: Structured data entry (submit PA forms, query Availity)
- **Dana**: Judgment, pattern recognition, clinical coordination (chase timing, denial workarounds, physician documentation requests)
- **Knowledge concentration risk** [A11]: Patterns locked in Dana's head → agent systematizes for front-desk access

---

**Response Complete**: 2026-05-05  
**All 15 peer review questions answered with supporting evidence from cognitive map, coach validation, and agent design decisions.**
