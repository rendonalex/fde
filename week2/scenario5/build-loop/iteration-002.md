# Iteration 002: Phase 3 Delegation Qualification

**Date**: 2026-04-28  
**Focus**: ATX Phase 3 — Delegation Suitability Scoring & Archetype Assignment  
**Status**: ✅ Complete

---

## What Was Built

### Primary Artifact
**File**: `scenario5-delegation-qualification.md` (7,850 words, 426 lines)

### Structure Created

1. **Delegation Suitability Matrix** — 4 JtDs scored across 7 dimensions:
   - Input structure (structured → unstructured)
   - Decision determinism (clear rules → judgment-dependent)
   - Tool coverage (APIs available → inaccessible)
   - Context complexity (explicit state → institutional knowledge)
   - Exception rate (rare → frequent)
   - Latency constraint (batch → real-time)
   - Risk/compliance (reversible → high-consequence)

2. **Detailed JtD Scoring** with evidence links to cognitive map:
   - **JtD-1: Insurance Verification** → 4 High, 3 Medium, 0 Low
   - **JtD-2: PA Chase Timing** → 2 High, 3 Medium, 1 Low, 1 High-consequence
   - **JtD-3: Visit Reason Triage** → 2 High, 2 Medium, 2 Low, 1 Very High risk
   - **JtD-4: Medication Reconciliation** → 3 High, 3 Medium, 0 Low, 1 High risk (backstop)

3. **Archetype Assignment Summary Table**:
   - 2 JtDs → Agent-led + Human Oversight (learning) → Fully Agentic (production)
   - 1 JtD → Agent-led + Human Oversight (perpetual)
   - 1 JtD → Human-led + Agent Support (conservative)

4. **Anti-Pattern Analysis** — Verified none can be solved with static rules/RPA

5. **Critical Dependencies** — 5 assumptions must be validated before finalized design

6. **Recommended Sequencing** — 3-wave implementation plan with timelines and success metrics

---

## Key Findings

### Finding 1: Two Strong Agentic Candidates Identified
**JtD-1 (Insurance Verification)** and **JtD-2 (PA Chase Timing)** both score HIGH on most dimensions and can progress to Fully Agentic after learning phases.

**JtD-1 path to autonomy**:
- Initial: Agent-led + Human Oversight (Dana validates re-verification triggers)
- Production: Fully Agentic (auto-triggers re-verification for >6mo + chronic patients [A3])
- Timeline: 1 month validation → production
- **Quick win**: Clear rule, high volume (180/day), prevents billing failures

**JtD-2 path to autonomy**:
- Initial: Agent-led + Human Oversight (Dana teaches insurer patterns, 3-6 months)
- Production: Fully Agentic with spot-checks (agent handles predictable insurers; Dana reviews unpredictable ones like Aetna)
- Timeline: 2 months build → 3-6 months learning → production
- **Strategic win**: Captures Dana's 11 years of institutional knowledge [A2, A4, A7]; scales to team

**Evidence of value**:
- JtD-1 prevents billing failures (currently 3/quarter, Artefact 5.3)
- JtD-2 prevents visit aborts (currently ~1/month, Artefact 5.2: patient TJ's second abort triggered senior physician complaint)

---

### Finding 2: Clinical Judgment Constraint Creates Hard Boundary for JtD-3
**JtD-3 (Visit Reason Triage)** scored LOW on Decision determinism and Context complexity, VERY HIGH on Risk.

**Why it's constrained**:
- Scenario constraint [A13]: "No clinical judgment by the agent" is non-negotiable
- Dana's definition of clinical vs. administrative triage boundary is unknown (Q13 must resolve this)
- Patient safety risk: Missing urgent symptom → patient harm; Over-escalating → alert fatigue (both dangerous)
- Malpractice insurance constraints unknown [A15] — may require human review of all escalations

**Assigned archetype**: **Human-led + Agent Support** (conservative)
- Agent parses visit reason (NLP), flags keyword-based urgency triggers
- Agent does NOT assess severity or urgency — only surfaces ambiguity
- Dana/physician reviews ALL flagged cases; human makes final call
- Over time, agent learns from physician feedback, but human always decides

**Deferred to Wave 4** (optional): Pursue only after Waves 1-3 validated + [A15] malpractice constraints clarified.

---

### Finding 3: Medication Reconciliation Depends on DoseSpot Scope Validation
**JtD-4 (Medication Reconciliation)** scored MEDIUM on most dimensions, HIGH risk but with human backstop.

**Critical dependency [A6]**: "DoseSpot misses things" (scenario states this), but artefacts provide zero detail.
- What does it miss? Out-of-network pharmacies? OTC meds? Physician samples? Other providers' prescriptions?
- Until [A6] validated via coach (Q14, Q17), agent scope is incomplete

**Assigned archetype**: **Agent-led + Human Oversight** (physician reviews flagged discrepancies)
- Agent compares three sources: athenahealth, DoseSpot, patient questionnaire
- Agent flags discrepancies; does NOT auto-update athenahealth (risk mitigation)
- Physician reviews flagged list before visit (30 sec vs. 6 min manual reconciliation)

**Value**: Physician time savings (~5.5 min/patient × 180 = 16.5 hours/day freed up); front-desk time freed for other tasks

**Wave 3 priority**: High volume, immediate ROI, but requires [A6] elicitation first (1 month delay vs. Wave 1).

---

### Finding 4: All 4 JtDs Pass Anti-Pattern Check (Agents Justified)
None of the 4 JtDs can be solved with static rules, RPA, or simple scripts. All require reasoning, pattern recognition, or NLP.

**JtD-1**: 30% exception rate [A1] requires interpreting Availity error codes in context; re-verification rule [A3] has conditional logic (chronic patient identification)

**JtD-2**: Insurer-specific patterns [A2, A4] are empirical (learned over 11 years), not documented rules. "Humana always 6 days" is observed behavior, not API-provided SLA.

**JtD-3**: Patient language is highly variable ("feeling off" vs. "chest pain"); NLP required. Agent learns from physician feedback to calibrate escalation.

**JtD-4**: Reconciling three sources (two structured, one unstructured) requires interpreting discrepancies. Patient verbal report ("I stopped that") is ambiguous.

**Conclusion**: Agents add value through pattern learning, institutional knowledge capture, NLP interpretation, and adaptive escalation. Not engineering overhead.

---

## Suitability Scoring Summary (7 Dimensions × 4 JtDs)

| JtD | Input Structure | Decision Determinism | Tool Coverage | Context Complexity | Exception Rate | Latency | Risk |
|-----|----------------|---------------------|---------------|-------------------|----------------|---------|------|
| **JtD-1: Insurance Verification** | HIGH | MEDIUM | HIGH | MEDIUM | MEDIUM (30% [A1]) | HIGH (low constraint) | MEDIUM (reversible) |
| **JtD-2: PA Chase Timing** | MEDIUM | **LOW** (patterns [A2, A4]) | MEDIUM | **HIGH** (Dana's knowledge) | MEDIUM (40%) | HIGH (low constraint) | HIGH (visit abort) |
| **JtD-3: Visit Reason Triage** | MEDIUM | **LOW** (judgment [A5]) | HIGH | **HIGH** (clinical boundary [A13]) | **HIGH** (ambiguous language) | MEDIUM | **VERY HIGH** (patient safety) |
| **JtD-4: Medication Reconciliation** | MEDIUM | MEDIUM | HIGH | **HIGH** (DoseSpot gaps [A6]) | MEDIUM | HIGH (low constraint) | HIGH (but backstop) |

**Key insight**: JtD-2 and JtD-3 both score LOW on Decision determinism, but for different reasons:
- **JtD-2**: Patterns are learnable (agent captures institutional knowledge) → Agent-led viable
- **JtD-3**: Judgment is clinical (agent cannot cross boundary) → Human-led required

This demonstrates that LOW Decision determinism does not automatically disqualify agentic delegation — it depends on whether the judgment is capturable (patterns, historical data) vs. irreducibly human (clinical, ethical, relationship-based).

---

## Critical Dependencies Identified (Must Validate Before Finalized Design)

| Dependency | Assumption | Affects | Questions to Resolve | Risk if Not Validated |
|------------|-----------|---------|---------------------|----------------------|
| **1. Dana's Re-Verification Rule** | [A3] Front-desk lacks consistent training on >6mo rule | JtD-1 archetype (Fully Agentic feasibility) | Q6, Q8, Q9 | Agent over-verifies (API cost) or under-verifies (billing failures continue) |
| **2. PA Pattern Stability** | [A2] Dana's chase timing patterns stable over 6-12 months | JtD-2 archetype (Fully Agentic timeline) | Q3, Q5 | Dana's Google Sheet is stale; agent applies outdated timing |
| **3. Clinical Judgment Boundary** | [A13] No clinical judgment by agent | JtD-3 archetype (Human-led vs. Agent-led) | Q10, Q11, Q13 | Agent crosses into clinical territory (malpractice risk) or over-escalates (alert fatigue) |
| **4. DoseSpot Integration Gaps** | [A6] DoseSpot misses medication sources (scope unknown) | JtD-4 scope (what to reconcile) | Q14, Q15, Q17 | Agent misses sources DoseSpot doesn't cover; scope incomplete |
| **5. Malpractice Insurance Constraints** | [A15] Malpractice policy may require human review | All JtDs (especially JtD-3) | Q20 | Agent design violates policy; practice exposed to liability |

**Priority for coach role-play**:
- **Tier 1 (must answer)**: Dependencies 3, 4, 5 (Q13, Q14, Q20)
- **Tier 2 (refine design)**: Dependencies 1, 2 (Q6, Q3)

---

## Recommended Implementation Sequencing (3 Waves)

### Wave 1: Insurance Re-Verification (Quick Win)
**Target**: JtD-1 sub-task — enforce >6mo re-verification rule [A3]  
**Archetype**: Fully Agentic (after 1-month validation)  
**Timeline**: 1 month validation → 2 months build → 1 month pilot → production (4 months total)  
**Success metrics**:
- Zero billing failures from stale verification (currently 3/quarter)
- 30-50 proactive re-verifications/month
- $0 API cost increase (re-verify only when needed)

**Why Wave 1**: Clear rule, high volume (180/day), immediate ROI, low complexity

---

### Wave 2: PA Chase Timing (Strategic Value)
**Target**: JtD-2 — Dana's insurer-specific chase timing patterns [A2, A4, A7]  
**Archetype**: Agent-led + Human Oversight (3-6 months) → Fully Agentic (production)  
**Timeline**: 2 months build → 3-6 months learning → production (8-11 months total)  
**Success metrics**:
- Zero visit aborts from PA timing misses (currently ~1/month)
- Agent learns 15+ insurer-specific patterns
- Dana's time reduced from ~1-2 hours/day to ~15 min spot-checking

**Why Wave 2**: Highest-value unlock (institutional knowledge capture), scalable to team, moderate complexity

---

### Wave 3: Medication Reconciliation (Volume Play)
**Target**: JtD-4 — three-source discrepancy flagging  
**Archetype**: Agent-led + Human Oversight (perpetual; physician reviews flags)  
**Timeline**: 1 month elicitation ([A6] validation) → 2 months build → 1 month pilot → production (4 months total)  
**Success metrics**:
- Physician review time reduced from 6 min to 30 sec per patient
- Zero unreviewed med changes discovered at visit (currently "regular" [A8])
- Front-desk time freed: 15 hours/day across team

**Why Wave 3**: High volume (180/day), immediate physician time savings, depends on [A6] elicitation

---

### Wave 4 (Optional): Visit Reason Triage (Long-Term)
**Target**: JtD-3 — keyword-based urgency flagging  
**Archetype**: Human-led + Agent Support (conservative escalation)  
**Timeline**: Defer until Waves 1-3 validated; reassess based on [A15] malpractice constraints  
**Success metrics** (if pursued):
- Standardized triage across 4-person team
- Zero missed urgent symptoms (maintain safety, improve consistency)
- <5% false positive rate on escalations

**Why Wave 4 (deferred)**: Clinical boundary constraint [A13], malpractice risk [A15], lower immediate ROI

---

## Design Decisions Made

### Decision 1: JtD-2 (PA Chase) is Agent-led Despite LOW Decision Determinism
**Rationale**: Patterns are learnable from historical data (Dana's Google Sheet [A7]) + reinforcement learning (Dana's corrections). LOW determinism does NOT disqualify agentic delegation when judgment is capturable.

**Alternatives considered**:
- Human-led + Automation Support (agent only does PA submission, Dana chases) — loses value of institutional knowledge capture
- Human-only (status quo) — perpetuates single point of failure (Dana), no scaling

**Outcome**: Agent-led + Human Oversight during learning phase (3-6 months); Fully Agentic in production with spot-checks for unpredictable insurers.

---

### Decision 2: JtD-3 (Visit Triage) is Human-led Despite Agent Capability
**Rationale**: Clinical judgment constraint [A13] is hard blocker. Patient safety risk (VERY HIGH) + malpractice exposure [A15] requires conservative design. Agent can parse language and flag keywords, but human must assess urgency.

**Alternatives considered**:
- Agent-led + Human Oversight (agent assesses urgency, Dana spot-checks) — violates "no clinical judgment" constraint
- Fully Agentic (agent triages autonomously) — unacceptable risk (patient harm if urgent symptom missed)

**Outcome**: Human-led + Agent Support (agent flags ambiguity, human always decides). Defer to Wave 4; reassess after [A15] validated.

---

### Decision 3: JtD-4 (Medication Reconciliation) Agent Flags, Physician Reviews
**Rationale**: High risk (drug interactions, allergy conflicts), but physician reviews before prescribing (human backstop). Agent does NOT auto-update athenahealth (risk mitigation).

**Alternatives considered**:
- Fully Agentic (agent auto-updates athenahealth med list) — too risky without multi-month validation
- Human-only (physician does full reconciliation) — loses 5.5 min/patient time savings

**Outcome**: Agent-led + Human Oversight (perpetual). Agent compares three sources, flags discrepancies; physician reviews flagged list (30 sec vs. 6 min).

---

## Assumptions Reinforced (Confidence Increased)

### A3 (Re-verification rule) — Confidence: HIGH → VERY HIGH
**Evidence from Phase 3 analysis**:
- Artefact 5.3 explicitly shows billing failure pattern (>6 months + chronic patient)
- Front-desk note: "this is the third time" → systemic, not one-off human error
- Rule is simple to encode once validated: IF (last_verified > 6 months AND visits_past_year ≥ 3) THEN trigger_re_verification

**Implication**: JtD-1 can proceed to Fully Agentic after 1-month rule validation (Wave 1 timeline confirmed)

---

### A13 (Clinical judgment constraint) — Confidence: HIGH → VERY HIGH
**Evidence from Phase 3 analysis**:
- Scenario states "no clinical judgment by the agent" as hard constraint
- "Clear human escalation path for visit reason" reinforces this
- Risk analysis shows VERY HIGH consequence (patient safety) if boundary crossed

**Implication**: JtD-3 must be Human-led + Agent Support (conservative design); no path to Fully Agentic

---

## Assumptions Requiring Urgent Validation (Confidence Still LOW)

### A6 (DoseSpot gaps) — Confidence: LOW (unchanged)
**Why critical**: JtD-4 scope is undefined without this. Agent can't reconcile what it doesn't know is missing.
**Questions to resolve**: Q14 ("What does DoseSpot miss?"), Q17 ("Does DoseSpot show other-state fills?")
**Next step**: Coach role-play (Tier 1 priority)

### A15 (Malpractice constraints) — Confidence: MEDIUM (unchanged)
**Why critical**: If malpractice policy requires human review of all AI decisions, Fully Agentic is off the table for all JtDs.
**Questions to resolve**: Q20 ("Have you talked to malpractice carrier about AI?")
**Next step**: Coach role-play (Tier 1 priority)

---

## New Insights from Phase 3

### Insight 1: Decision Determinism ≠ Agent Unsuitability
**Discovery**: JtD-2 (PA Chase) scores LOW on Decision determinism, but is still Agent-led candidate because patterns are learnable.

**Lesson**: LOW determinism disqualifies agents only when judgment is irreducibly human (clinical, ethical, relationship-based). If judgment is pattern-based or institutional knowledge, agents can capture it through:
- Historical data ingestion (Dana's Google Sheet)
- Reinforcement learning (Dana's corrections)
- Pattern recognition (insurer-specific behavior)

**Application**: When scoring Decision determinism, distinguish:
- "LOW (judgment-dependent, not learnable)" → likely Human-only or Human-led
- "LOW (pattern-based, learnable from data/feedback)" → candidate for Agent-led

---

### Insight 2: Risk Mitigation Through Human Backstops
**Discovery**: JtD-4 (Medication Reconciliation) scores HIGH risk, but Agent-led is viable because physician reviews before prescribing.

**Lesson**: High-consequence tasks can be delegated to agents if:
- Human backstop exists downstream (physician review before action)
- Agent flags issues, does NOT take irreversible action (no auto-update)
- Failure mode is "missed discrepancy" (caught by backstop), not "wrong update" (irreversible)

**Application**: For high-risk JtDs, design agents to flag/synthesize/recommend, not execute. Human makes final decision or takes final action.

---

### Insight 3: Learning Phase → Production Transition
**Discovery**: JtD-1 and JtD-2 both start as Agent-led + Human Oversight, but timelines differ:
- JtD-1: 1 month learning → Fully Agentic (rule is simple)
- JtD-2: 3-6 months learning → Fully Agentic (patterns are complex)

**Lesson**: Archetype assignment is not static. Use learning phases to:
- Validate assumptions (does re-verification rule hold?)
- Teach patterns (Dana corrects agent's chase timing recommendations)
- Build confidence (observe agent behavior before full autonomy)

**Application**: For LOW determinism tasks, design learning phase where agent recommends, human approves/corrects. Track correction rate; when <5%, transition to Fully Agentic with spot-checks.

---

## What This Iteration Does NOT Answer

1. **Economic feasibility**: No token cost estimate, no TCO model, no ROI calculation for each wave
   - Need: Volume × time saved × hourly cost vs. token consumption + infrastructure

2. **Technical feasibility**: No assessment of athenahealth API limitations, Availity rate limits, DoseSpot API depth
   - Need: API documentation review, sandbox testing

3. **Volume × Value prioritization**: Preliminary sequencing provided, but no formal Phase 4 grid
   - Need: Plot each JtD on Y-axis (frequency) × X-axis (non-determinism) to validate Wave 1-3 order

4. **Organizational readiness**: No assessment of Dana's team's AI literacy, HITL supervision capacity, change management risk
   - Need: Coach role-play signals (Q23: headcount plans, Q22: Dana's career goals)

5. **Compliance details**: HIPAA acknowledged, but no audit logging requirements, patient consent workflow, data retention policy
   - Need: Legal/compliance review

---

## Next Steps (Proceeding to Phase 4)

**Immediate (before Phase 4)**:
1. ✅ Complete Phase 3 delegation qualification (done)
2. ⏳ Coach role-play: Tier 1 questions (Q14, Q20, Q13) to validate [A6], [A15], [A13]
3. ⏳ Update delegation archetypes if [A15] malpractice constraints discovered

**Phase 4 (Candidate Prioritization)**:
4. Build Volume × Value grid (plot 4 JtDs on frequency × non-determinism axes)
5. Score feasibility (6 factors: data availability, system integration, compliance risk, context stability, org readiness, TCO)
6. Validate Wave 1-3 sequencing with feasibility scores
7. Draft preliminary token economics model (cost per patient per JtD)

**After Phase 4**:
8. Create agent architecture design (orchestration, tool interfaces, guardrails)
9. Define success metrics and monitoring strategy for Wave 1 pilot

---

## Update: Lived Process Narrative Added (Iteration 002.1)

**Date**: 2026-04-29  
**Change**: Added missing Phase 2 output requirement and navigation improvements

### What Changed

1. **Added Lived Process Narrative section to cognitive map** (new section 4)
   - Contrasts documented SOPs vs. actual practice
   - Identifies 5 critical gaps where real work diverges from documentation
   - ~2,100 words describing what really happens in Dana's world

2. **Added Table of Contents to cognitive map** (10 sections)
   - Improves navigation for 548-line document
   - Links to all major sections

3. **Added Table of Contents to delegation qualification** (7 sections)
   - Improves navigation for 426-line document
   - Links to JtD scorings, wave sequencing, critical dependencies

### Lived Process Narrative: 5 Critical Gaps Documented

**Gap 1: Dana's Invisible Re-Verification Rules [A3]**
- **Documented**: "Verify insurance via Availity for all scheduled appointments"
- **Lived**: Dana knows verification >6 months old is unreliable, especially for chronic patients. **This rule exists only in her head**. Front-desk doesn't consistently apply it → billing failures (Artefact 5.3).

**Gap 2: Dana's Insurer-Specific Chase Timing Patterns [A2, A4, A7]**
- **Documented**: "Submit PA per insurer requirements; follow up at day 5"
- **Lived**: Stated SLAs are fiction. Dana has learned actual timing over 11 years:
  - Humana: Always exactly 6 days, never 5
  - UnitedHealthcare Choice: 6-7 days
  - Wellpath: Always denies colonoscopy first time, needs prior visit note
  - Tracked in Dana's personal Google Sheet [A7], not athenahealth or SOPs

**Gap 3: Front-Desk's Informal Clinical Triage [A5, A9]**
- **Documented**: "Review pre-visit questionnaire; document visit reason"
- **Lived**: Front-desk makes implicit clinical judgments when parsing patient language ("chest pain" — urgent or routine?). No formal triage protocol [A5]. Training is inconsistent across 4-person rotating team [A9].

**Gap 4: DoseSpot's Unknown Boundaries [A6]**
- **Documented**: "Reconcile medications using DoseSpot at check-in"
- **Lived**: DoseSpot misses things [A6] (scope unknown: out-of-network pharmacies? OTC? samples? other providers?). Front-desk asks generic "any changes?" Patients forget to mention OTC, unreported meds from specialists. Discrepancies discovered by physician during visit.

**Gap 5: Post-Incident Learning Doesn't Scale [A11]**
- **Documented**: (No documented process for incorporating lessons learned)
- **Lived**: When intake miss occurs, physician flags it → Dana investigates → Dana updates her mental model and maybe Google Sheet [A11]. But she doesn't update SOPs, doesn't systematically train front-desk, doesn't build into athenahealth. **Institutional knowledge stays locked in Dana's head**.

### Key Insight from Narrative

**Where the cognitive work lives**: 70% of intake is structured (successful API calls, clean data). **30% is exception handling** [A1] requiring:
- Dana's learned patterns (PA timing, denial workarounds, re-verification rules)
- Front-desk's informal judgment (triage, language interpretation)
- Manual reconciliation of system gaps (DoseSpot misses, patient forgetfulness)

**This is what agents must address**: Not the structured 70% (already handled by APIs), but the **exception-handling 30%** where human judgment bridges system gaps, interprets ambiguity, and applies institutional knowledge that exists nowhere else.

### Why This Matters

**ATX Phase 2 Output requirement** (from atx-assessment.md):
> "**Lived process narrative**: 1-page description of what really happens vs. what the SOP says"

This was missing from Iteration 001. The cognitive map had:
- ✅ Jobs to be Done decomposition
- ✅ Cognitive zones and breakpoints (process topology)
- ✅ Micro-task inventory with dimension scores
- ❌ Lived process narrative (missing until now)

**Value of the narrative**:
- Makes the "documented vs. lived" gap explicit and concrete
- Shows WHY Dana's institutional knowledge is valuable (it fills gaps SOPs don't address)
- Explains WHY front-desk makes mistakes (they don't have Dana's patterns [A11])
- Justifies agent design focus on exception handling, not just structured flows
- Provides specific examples for coach role-play (Q4: "What happens to PA chases when you're on vacation?" → narrative shows PA timing patterns exist only in Dana's head)

### Tables of Contents Added

**Cognitive map TOC** (10 sections):
1. Jobs to be Done (JtDs) Decomposition
2. Micro-Task Inventory with Cognitive Load Scores
3. Cognitive Topology: Zones and Critical Breakpoints
4. Lived Process Narrative: What Really Happens vs. What the SOP Says ← NEW
5. Assumption Register (with Confidence Levels)
6. Delegation Archetype Assignment (Preliminary)
7. Key Cognitive Hotspots
8. Design-Changing Questions for Coach Role-Play
9. Summary: Where Agents Win vs. Where Humans Must Stay
10. Next Steps for FDE (You)

**Delegation qualification TOC** (7 sections):
1. Delegation Suitability Matrix (4 JtDs scored)
2. Delegation Archetype Summary
3. Anti-Pattern Analysis
4. Critical Dependencies
5. Recommended Delegation Sequencing (4 waves)
6. Output Artifacts
7. Next Steps

**Navigation benefit**: Both documents are now 400+ lines. TOCs make it easy to jump to specific sections, especially useful when:
- Coach asks about specific JtD (jump to JtD-2 scoring)
- Need to reference specific assumption (jump to Assumption Register)
- Want to review wave sequencing (jump to Wave 2: PA Chase Timing)

---

**End of Iteration 002 (including 002.1 update)**
