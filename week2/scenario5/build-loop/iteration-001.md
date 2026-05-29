# Iteration 001: Initial Cognitive Map

**Date**: 2026-04-28  
**Focus**: Phase 2 Cognitive Load Mapping  
**Status**: ✅ Complete

---

## What Was Built

### Primary Artifact
**File**: `scenario5-cognitive-map.md` (9,461 words, 548 lines)

### Structure Created

1. **Jobs to be Done Decomposition** (4 JtDs)
   - JtD-1: Verify insurance eligibility for scheduled visit
   - JtD-2: Determine prior authorization status and chase pending PAs
   - JtD-3: Triage patient visit reason and flag clinical urgency
   - JtD-4: Reconcile medications and flag allergy alerts

   Each JtD includes:
   - Trigger, Actor, Goal, Key decisions, Key systems, Expected output
   - Cognitive nature classification
   - 4-6 cognitive zones (intent understanding → documentation)
   - 2-4 critical breakpoints (rule→judgment, system→human, frontline→Dana)
   - Lived vs. documented work gap analysis

2. **Micro-Task Inventory** (11 tasks scored across 8 dimensions)
   - Cognitive Load, Input Structure, Decision Determinism, Exception Frequency
   - Turn-Taking Degree, Latency Constraint, Compliance/Risk, Tool/API Availability
   - Scoring: H/M/L/VH (High/Medium/Low/Very High)

3. **Cognitive Topology Diagram** (6 zones with breakpoints)
   - Zone 1: Patient scheduling (pre-intake)
   - Zone 2: Insurance verification → 30% exceptions
   - Zone 3: Prior authorization management → Dana's institutional knowledge
   - Zone 4: Visit reason triage → clinical boundary enforcement
   - Zone 5: Medication reconciliation → DoseSpot integration gaps
   - Zone 6: Post-visit documentation & feedback

4. **Assumption Register** (15 assumptions with confidence levels)
   - 1 Very Low confidence (A14: Dana's personal stake)
   - 5 Low confidence (A6, A8, A10, A12, A14)
   - 8 Medium confidence
   - 2 High confidence (A3, A13)
   - 0 Very High confidence (nothing validated yet)

5. **Preliminary Delegation Archetypes** (11 micro-tasks assigned)
   - 3 Fully Agentic candidates
   - 4 Agent-led + Human Oversight candidates
   - 2 Human-led + Agent Support candidates
   - 1 Human-led + Automation Support candidate
   - 1 Human Only (initially) candidate

6. **4 Cognitive Hotspots** (deep analysis sections)
   - Hotspot 1: Dana's Institutional Knowledge (PA chase timing & denial patterns)
   - Hotspot 2: Insurance Re-Verification Rule Gap
   - Hotspot 3: Visit Reason Triage (clinical boundary enforcement)
   - Hotspot 4: Medication Reconciliation (DoseSpot integration gaps)

7. **24 Design-Changing Questions** (organized into 5 categories)
   - Category A: Prior Authorization Chase Logic (5 questions)
   - Category B: Insurance Re-Verification Rules (4 questions)
   - Category C: Visit Reason Triage (4 questions)
   - Category D: Medication Reconciliation (4 questions)
   - Category E: Stakeholder Priorities & Constraints (7 questions)

8. **Summary Analysis**
   - Strong agent candidates (5 areas)
   - Human-must-stay zones (3 areas)
   - Hybrid zones (2 areas)
   - Next steps for FDE (3 phases)

---

## Key Insights Discovered

### Insight 1: Dana as Single Point of Failure
**Evidence**: 
- Artefact 5.1 (PA chase list) shows insurer-specific timing patterns: "Humana always exactly 6 days, never 5"
- Artefact 5.1 footer: "Wellpath colonoscopy denial pattern — they want the prior visit note attached, never says so on the form"
- These patterns exist nowhere except Dana's Google Sheet + her tacit knowledge

**Implications**:
- Knowledge transfer problem: New hires can't access Dana's 11 years of learning
- Business continuity risk: "If Dana were on vacation for 2 weeks, what happens to PA chases?" (Q4)
- **Highest-leverage automation target**: Systematizing Dana's institutional knowledge scales immediately to entire front-desk team

**Confidence**: HIGH (directly supported by artefacts)

---

### Insight 2: Lived Work ≠ Documented Work
**Evidence**:
- Artefact 5.3: Patient billing failure from stale insurance verification (>6 months)
- Front-desk note: "Patient verification refresh window > 6 months caused billing miss. We don't refresh for chronic patients on stable insurance — Dana said this is the third time."
- Implies Dana has a tacit rule: "Re-verify if >6 months for chronic patients"
- This rule is NOT in documented intake SOP (inference: no one mentioned formal documentation)

**Implications**:
- Agent built from SOPs will reproduce front-desk mistakes, not prevent them
- Need to elicit Dana's tacit rules explicitly (Q6, Q8, Q9)
- Re-verification rule is simple enough to encode as fully agentic once validated

**Confidence**: MEDIUM-HIGH (artefact shows pattern; unclear if it's actually documented somewhere we haven't seen)

---

### Insight 3: PA Chase Timing ≠ Stated SLA
**Evidence**:
- Artefact 5.1: "Standard SLA" column shows 5 days for most insurers
- Artefact 5.1: "My target chase" column shows Dana's actual timing: 6-7 days for some insurers
- Artefact 5.1 notes: "UHC Choice is always 6 days, sometimes 7" / "Humana always exactly 6 days; never 5"

**Implications**:
- Stated SLAs are fiction; Dana has learned real response times through repeated observation
- This is **pattern-based learning over 11 years** — highly valuable to capture
- Agent can learn these patterns from historical Google Sheet data + Dana's corrections
- **Critical question**: Do these patterns stay stable over 6-12 months, or do insurers change frequently? (Q3)

**Confidence**: HIGH (artefact explicitly documents gap between stated vs. lived SLA)

---

### Insight 4: Visit Abort = Operational Failure Mode
**Evidence**:
- Artefact 5.2: Dr. Westbridge's note about patient TJ
- "PA for the MRI was still pending at visit time — see athenahealth ticker. Front desk did not flag this at check-in."
- "Visit aborted at exam-room check; rescheduled for 04.11 once PA confirmed."
- Patient quote: "this is the second time this has happened to me"

**Implications**:
- PA status miss at check-in → wasted physician time, patient frustration, scheduling inefficiency
- Root cause: PA pending beyond expected approval time, but no one chased or flagged it
- **Agent value**: Proactive PA status check 2-3 days before visit → flag for Dana to chase → prevent visit abort
- This failure mode directly motivated senior physician to ask Dana to "look at this AI thing"

**Confidence**: HIGH (artefact shows concrete operational failure with patient impact)

---

### Insight 5: Front-Desk Cognitive Load is Uneven
**Evidence**:
- JtD-1 (insurance verification): 70% structured, 30% exceptions requiring pattern recognition
- JtD-2 (PA chase): Almost entirely Dana's domain; front-desk only does structured submission
- JtD-3 (visit triage): Front-desk does initial review, but clinical boundary is fuzzy (informal training)
- JtD-4 (medication reconciliation): Front-desk does initial reconciliation, but "DoseSpot misses things" (unexplained)

**Implications**:
- Front-desk work is mostly execution (LOW-MEDIUM cognitive load), with exception spikes (HIGH load)
- Exceptions get escalated to Dana, creating bottleneck
- **Agent opportunity**: Absorb exception-pattern recognition (Availity failure codes, PA chase timing) → reduce Dana escalations
- **Agent risk**: Visit triage boundary is fuzzy → agent might make implicit clinical judgments (violates constraint)

**Confidence**: MEDIUM (inferred from artefacts; no direct shadowing data)

---

## Assumptions Catalogued

### Very Low Confidence (1)
- **A14**: Dana's personal stake is career growth (not workflow reduction for front-desk)
  - **Why it matters**: Affects stakeholder alignment — if Dana wants regional role, needs scalable solution; if she wants cost-cutting, different design
  - **How to test**: Q22 (What's your 5-year career plan?)

### Low Confidence (5)
- **A6**: DoseSpot misses medication sources: other providers, OTC, supplements, patient non-adherence
  - **Why it matters**: Determines agent scope for medication reconciliation
  - **How to test**: Q14 (What does DoseSpot actually miss?)

- **A8**: Intake miss rate is ~3-5 per month (physician discovers missed PA, unreviewed med change)
  - **Why it matters**: Justifies automation urgency and ROI
  - **How to test**: Q18 (What's your biggest frustration?) + ask for frequency

- **A10**: PA volume (~25/day) is unevenly distributed by insurer (Medicaid managed care, UnitedHealthcare dominate)
  - **Why it matters**: If PA volume is evenly distributed, insurer-specific pattern learning is less valuable
  - **How to test**: Request one week of Dana's Google Sheet updates

- **A12**: athenahealth REST APIs support all required operations (insurance verification, PA submission/status, visit reason, med reconciliation)
  - **Why it matters**: If APIs are limited, tool integration cost is much higher
  - **How to test**: athenahealth API documentation review + sandbox testing

- **A15**: Malpractice insurance policy constrains AI usage (e.g., requires human review of all clinical flags)
  - **Why it matters**: Determines agent autonomy boundaries
  - **How to test**: Q20 (Have you talked to malpractice carrier about AI?)

### Medium Confidence (7)
- **A1**: 30% of insurance verifications fail auto-verify
- **A2**: Dana's PA chase timing patterns are stable over 6-12 months
- **A4**: PA denials follow learnable insurer-specific patterns
- **A5**: Visit reason triage by front-desk is inconsistent (relies on informal training)
- **A7**: Dana's Google Sheet is authoritative source for PA chase logic (not insurer portals)
- **A9**: Front-desk team rotates between locations, creating knowledge fragmentation
- **A11**: Dana has no formal system for surfacing learned patterns to front-desk (beyond Google Sheet)

### High Confidence (2)
- **A3**: Front-desk lacks consistent training on re-verification rules (>6 months for chronic patients)
  - Directly supported by Artefact 5.3 ("third time" this billing failure happened)
  
- **A13**: HIPAA constraint limits agent access to full clinical record (administrative vs. clinical data boundary)
  - Scenario explicitly states "no clinical judgment" and "HIPAA compliance non-negotiable"

---

## Design Decisions Made

### Decision 1: Focus on Dana's Institutional Knowledge as Primary Value Unlock
**Rationale**: 
- 11 years of insurer-specific patterns not systematized anywhere
- Single point of failure (business continuity risk)
- Direct line to operational failure mode (visit aborts from PA timing misses)
- Scalable to front-desk team immediately upon capture

**Alternatives considered**:
- Focus on front-desk execution work (insurance verification, med reconciliation) — these are higher volume but lower cognitive load, less differentiated value
- Focus on physician-facing features (clinical decision support) — violates "no clinical judgment" constraint

**Outcome**: Hotspot 1 (PA chase timing & denial patterns) prioritized as primary agent design target

---

### Decision 2: Design 24 Specific Questions (Not Generic "Walk Through Your Day")
**Rationale**: 
- ATX-assessment.md guidance: "Precise questions about lived practice, prior automation history, system edge cases, and stakeholder priorities will earn substantive responses"
- Generic questions get generic answers → can't validate assumptions or refine cognitive map
- Each question targets a specific assumption (e.g., Q3 tests A2: pattern stability; Q14 tests A6: DoseSpot gaps)

**Alternatives considered**:
- Open-ended interview ("Tell me about your work") — risks missing critical details, allows Dana to focus on what she thinks is important (not what's actually highest-value)
- Shadowing Dana for a day — more authentic but time-intensive, and we'd still need targeted questions to understand tacit reasoning

**Outcome**: 24 questions organized into 5 categories, tiered by priority (Tier 1 = must answer to proceed)

---

### Decision 3: Preliminary Delegation Archetypes Assigned (But Not Finalized)
**Rationale**:
- Phase 2 (Cognitive Load Mapping) reveals cognitive nature of work
- Phase 3 (Delegation Qualification) requires validated assumptions + suitability scoring matrix
- Premature to finalize archetypes without coach validation of key unknowns (A6, A8, A14, A15)

**Outcome**: 
- 11 micro-tasks assigned to preliminary archetypes (e.g., "PA chase timing" → Agent-led + Human Oversight)
- Archetypes may change after coach role-play (e.g., if Q20 reveals strict malpractice constraints, "Fully Agentic" candidates may downgrade to "Agent-led + Human Oversight")

---

## Questions Generated (Prioritized)

### Tier 1: Must Answer to Proceed (4 questions)
These questions address highest-uncertainty assumptions or reveal true stakeholder priorities:

- **Q14**: "You mentioned DoseSpot misses things. What are the most common medication sources that DoseSpot doesn't capture? Other providers' prescriptions, OTC meds, supplements, something else?"
  - **Targets**: Assumption A6 (LOW confidence), Hotspot 4
  - **Why critical**: Medication reconciliation scope is undefined without this

- **Q1**: "Walk me through the last PA denial you handled. What was the insurer, what reason did they give, and what did you do to resolve it? How did you know to do that?"
  - **Targets**: Assumption A4 (MEDIUM confidence), Hotspot 1
  - **Why critical**: Tests whether Dana's denial response patterns are truly learnable or ad-hoc

- **Q18**: "What's your biggest frustration with the current intake process? If you could wave a magic wand and fix one thing, what would it be?"
  - **Targets**: Stakeholder priority (unknown)
  - **Why critical**: Reveals Dana's actual priority (may not be PA chases; could be front-desk errors, patient complaints, physician complaints)

- **Q22**: "What's your role in 5 years? Are you planning to stay as Practice Manager, or move into a different role? What would success in this AI project mean for your career?"
  - **Targets**: Assumption A14 (VERY LOW confidence)
  - **Why critical**: Affects stakeholder alignment — if Dana's grooming for regional role, she wants scalable solution; if she's staying, she wants operational relief

### Tier 2: Refine Delegation Design (3 questions)
These questions calibrate agent behavior and boundaries:

- **Q6**: "The patient billing issue in October (TJ, $340 self-pay bill) — you said that's the third time this has happened. What do those three cases have in common? Same patient type, same insurer, same time gap?"
  - **Targets**: Assumption A3 (HIGH confidence, but need pattern details), Hotspot 2
  - **Why important**: If all three are >6 months + chronic patients, re-verification rule is clear; if unrelated, harder to prevent

- **Q10**: "Can you give me an example of a visit reason that the front desk flagged as urgent, but turned out to be routine? And vice versa — something they marked routine that should have been escalated?"
  - **Targets**: Hotspot 3 (clinical boundary calibration)
  - **Why important**: Determines agent sensitivity (favor false positives or false negatives?)

- **Q20**: "Have you talked to your malpractice insurance carrier about using AI for intake? Do they have any requirements like 'a human must review every AI decision' or anything like that?"
  - **Targets**: Assumption A15 (MEDIUM confidence), autonomy boundaries
  - **Why important**: If malpractice requires human review, "Fully Agentic" is off the table

### Tier 3: Economic & Operational Context (3 questions)
These questions inform feasibility and change management:

- **Q24**: "What's the practice's budget for new software or technology? Is there an annual IT spend, or would this need special approval?"
  - **Targets**: Economic feasibility
  - **Why important**: If budget is $0, need low-cost solution (token economics < $2,700/month for 180 patients/day)

- **Q23**: "If this AI project works, what happens to the front-desk team? Are you expecting to reduce headcount, or redeploy them to other tasks?"
  - **Targets**: Change management risk
  - **Why important**: If Dana says "we'll let someone go," expect front-desk resistance

- **Q21**: "Which patient populations don't fit the standard intake flow? For example, non-English speakers, patients without portal access, patients who always call instead of filling out forms?"
  - **Targets**: Edge case handling
  - **Why important**: If 20% of patients are "special cases," agent needs explicit handling (phone transcription, multilingual)

---

## New Unknowns Discovered

### Unknown 1: DoseSpot Integration Scope (CRITICAL)
- Scenario states "DoseSpot misses things in real practice"
- Artefacts provide zero detail about what it misses
- **Impact**: Can't design medication reconciliation agent without knowing what gaps to fill
- **Next step**: Q14 in Tier 1 questions

### Unknown 2: Intake Miss Frequency
- Scenario states physicians "regularly discover" intake misses
- Artefact 5.2 shows one example (patient TJ's visit abort)
- Scenario brief mentions "three intake misses in the last quarter (all expired prior auths)"
- **Impact**: If miss rate is 3/quarter, less urgency; if 3/month, much higher ROI
- **Next step**: Q18 + ask for frequency explicitly

### Unknown 3: Dana's Career Trajectory
- Scenario prompt says "What's Dana's personal stake in this — what is she planning for beyond this project?"
- No artefacts address this
- **Impact**: If Dana wants regional role, she'll advocate for scalable solution (good for agent design); if she's protecting her turf, may resist knowledge transfer
- **Next step**: Q22 in Tier 1 questions

### Unknown 4: Malpractice Insurance Constraints
- Scenario mentions this as elicitation target
- No artefacts address it
- **Impact**: Could force all agents to "Agent-led + Human Oversight" (no full autonomy)
- **Next step**: Q20 in Tier 2 questions

---

## Artefacts Requested (Not Yet Received)

1. **Screenshot of athenahealth PA status screen**
   - Why: Understand what data is actually visible to front-desk vs. what Dana infers from phone calls
   - Impact: If athenahealth shows "pending since [date]", agent can calculate expected approval time; if it only shows "pending" (binary), agent needs to rely on submission date + Dana's patterns

2. **Sample Availity API error response**
   - Why: Understand structure of the 30% verification failures (error codes, response format)
   - Impact: Determines whether "Interpret Availity failure codes" can be rule-based or requires pattern learning

3. **One week of Dana's Google Sheet updates (PA chase list)**
   - Why: Measure PA chase frequency, pattern consistency, insurer distribution
   - Impact: Validates Assumption A2 (pattern stability) and A10 (insurer distribution)

4. **Front-desk training manual (if it exists)**
   - Why: See what's documented vs. what's tacit
   - Impact: If re-verification rule is documented but ignored, it's a training problem; if it's not documented, it's a knowledge transfer problem

---

## Next Steps (Defined)

### Immediate (Before Next Coach Session)
1. ✅ Create build-loop tracking system (this file)
2. ⏳ Prepare Tier 1 questions (Q14, Q1, Q18, Q22) for role-play with coach
3. ⏳ Request 4 additional artefacts listed above

### After Coach Session (Iteration 2)
4. Update assumption confidence levels based on coach responses
5. Refine cognitive map sections (especially Hotspot 4 - medication reconciliation)
6. Revise delegation archetypes if new constraints discovered (e.g., malpractice requires human review)

### After Assumptions Validated (Iteration 3)
7. Build formal Delegation Qualification Matrix (Phase 3: 11 micro-tasks × 7 suitability dimensions)
8. Prioritize use cases using Volume × Value grid (Phase 4)
9. Draft preliminary token economics model

### Technical Feasibility (Iteration 4)
10. Review athenahealth API documentation (verify Assumption A12)
11. Test Availity API sandbox (if available) to understand error codes
12. Prototype PA chase timing logic using historical Google Sheet data

---

## Rationale: Why This Approach?

### Why Start with Cognitive Mapping (Not Agent Architecture)?
**Problem**: Most AI projects start with solution ("let's build an agent to do X") before understanding the cognitive work
**Risk**: Agent built from SOPs will miss the lived work (e.g., Dana's tacit re-verification rule, insurer-specific PA timing patterns)
**ATX approach**: Phase 2 (Cognitive Load Mapping) forces explicit enumeration of:
- Where humans make judgments (breakpoints)
- What knowledge is tacit vs. codified (zones)
- Which decisions are pattern-learnable vs. irreducibly human (delegation archetypes)

**Evidence from scenario**:
- Artefact 5.3: Billing failure from missed re-verification rule (not in SOPs)
- Artefact 5.1: PA chase timing patterns in Dana's Google Sheet (not in athenahealth)
- Artefact 5.2: Visit abort from PA status miss at check-in (process exists, but execution failed)

### Why 4 Cognitive Hotspots (Not Comprehensive Coverage)?
**Problem**: Attempting to solve every intake problem at once → scope creep, no clear value demonstration
**ATX approach**: Identify disproportionate value or risk concentrations
**Hotspots chosen**:
1. **Dana's institutional knowledge** (PA chase) → highest leverage unlock, directly prevents visit aborts
2. **Re-verification rule gap** → clear rule, clear failure mode, clear ROI (prevents billing failures)
3. **Visit triage boundary** → highest risk (clinical judgment constraint), needs careful calibration
4. **Medication reconciliation** → unknown gaps (DoseSpot misses), requires elicitation before design

### Why 24 Specific Questions (Not Open-Ended Interview)?
**ATX-assessment.md guidance**: "Precise questions about lived practice, prior automation history, system edge cases, and stakeholder priorities will earn substantive responses. Generic questions will get generic answers."

**Example of generic vs. specific**:
- ❌ Generic: "Walk me through your typical day" → Dana will describe ideal state, not exception handling
- ✅ Specific: "Your Google Sheet shows 'Wellpath always denies colonoscopy first time — needs prior visit note.' How did you discover that pattern? How many times did it happen before you realized it was consistent?" → Forces Dana to reveal pattern stability, sample size, confidence level

**Each question targets a specific assumption** (e.g., Q3 tests A2: pattern stability; Q14 tests A6: DoseSpot gaps)

---

## What This Iteration Does NOT Answer

1. **Economic feasibility**: No token cost estimate, no TCO model, no ROI calculation
2. **Technical feasibility**: No assessment of athenahealth API limitations, Availity rate limits
3. **Formal delegation boundaries**: Preliminary archetypes assigned, but no Phase 3 suitability matrix
4. **Organizational readiness**: No assessment of Dana's team's AI literacy, HITL supervision capacity
5. **HIPAA/compliance details**: Constraint acknowledged but not detailed (audit logging, patient consent)

**Why defer these?**
- Economic model requires volume data (Q18 will reveal Dana's priority → helps scope initial use case)
- Technical feasibility requires API access (can't test without athenahealth sandbox credentials)
- Formal delegation requires validated assumptions (premature to score suitability when A6, A14, A15 are LOW/VERY LOW confidence)

---

## Confidence Assessment: What Can We Trust?

### High Confidence (Can Proceed with Design)
- ✅ Dana's Google Sheet contains insurer-specific PA chase patterns (Artefact 5.1 explicit)
- ✅ PA timing misses cause visit aborts (Artefact 5.2 explicit: patient TJ's visit aborted)
- ✅ Re-verification rule gap causes billing failures (Artefact 5.3 explicit: "third time")
- ✅ Front-desk team rotates between two locations (scenario states this)
- ✅ athenahealth is modern SaaS with REST APIs (scenario states this)

### Medium Confidence (Validate Before Finalizing Design)
- ⚠️ Dana's PA chase patterns are stable over 6-12 months (need Q3 to test)
- ⚠️ 30% of insurance verifications fail auto-verify (stated in scenario, aligns with typical Availity rates)
- ⚠️ PA denials follow learnable patterns (Artefact 5.1 suggests this, but need Q1 to validate)
- ⚠️ Front-desk triage is inconsistent due to informal training (inferred from "clear escalation path" constraint)

### Low Confidence (Must Elicit Before Design)
- ❌ DoseSpot integration gaps (scenario mentions "misses things" with zero detail)
- ❌ Intake miss frequency (stated as "regularly" with one example; need Q18)
- ❌ PA volume distribution by insurer (inferred from 3/5 samples in Artefact 5.1)
- ❌ athenahealth API capabilities (assumed from "modern SaaS"; need documentation review)

### Very Low Confidence (Pure Speculation Until Validated)
- ❌ Dana's career trajectory and personal stake (no artefacts address this; need Q22)

---

## Update: Assumption ID References Added (Iteration 001.1)

**Date**: 2026-04-28 (same day as initial creation)  
**Change**: Added assumption ID references throughout cognitive map for traceability

### What Changed
- Added [A1] through [A15] tags to all assumption mentions in `scenario5-cognitive-map.md`
- Tagged in sections: JtD descriptions, cognitive zones, breakpoints, micro-task inventory, topology diagram, hotspots, and questions

### Specific Locations Tagged
1. **JtD-1 (Insurance Verification)**:
   - [A1]: 30% auto-verify failure rate
   - [A3]: Tacit re-verification rule (>6 months for chronic patients)

2. **JtD-2 (Prior Authorization Management)**:
   - [A2]: Dana's insurer-specific chase timing patterns
   - [A4]: Learnable PA denial patterns (e.g., "Wellpath always denies colonoscopy first time")
   - [A7]: Dana's Google Sheet as authoritative source
   - [A10]: PA volume distribution (~25/day)
   - [A11]: No formal system for surfacing Dana's learned patterns

3. **JtD-3 (Visit Reason Triage)**:
   - [A5]: Informal triage training (inconsistent across team)
   - [A9]: Front-desk rotation between locations
   - [A13]: HIPAA constraint limiting clinical judgment

4. **JtD-4 (Medication Reconciliation)**:
   - [A6]: DoseSpot integration gaps (what it misses is unknown)
   - [A8]: Intake miss frequency (physicians discover med changes at visit)

5. **Micro-Task Inventory**: Added assumption tags to all 11 micro-tasks
6. **Cognitive Topology**: Tagged breakpoints and zones with relevant assumptions
7. **Hotspot Sections**: Linked each hotspot analysis to supporting assumptions
8. **Design-Changing Questions**: Tagged each question with the assumption(s) it tests

### Why This Matters
- **Traceability**: Can now quickly identify which assumptions underpin each analysis section
- **Validation tracking**: When coach answers questions, can immediately find all places where that assumption is referenced
- **Design consistency**: Ensures design decisions reference specific, traceable assumptions rather than vague inferences
- **Communication**: Makes assumption dependencies explicit for stakeholders

### Example Usage
When coach answers Q14 ("What does DoseSpot actually miss?"), can search for [A6] to find:
- JtD-4 description (medication reconciliation scope)
- Micro-task "Identify med list discrepancies" (reconciliation logic)
- Cognitive topology Zone 5 (DoseSpot integration gaps)
- Hotspot 4 analysis (critical elicitation needed)
- Questions Q14, Q17 (both test DoseSpot scope)

This allows updating all related sections simultaneously when assumption confidence changes.

---

**End of Iteration 001**
