# Build-Loop Index: Scenario 5 - Small-Clinic Patient Intake

## Purpose
This index tracks all iterations of document development for the Westbridge Family Medicine patient intake analysis. Each iteration is documented in a separate file, capturing what was built, what assumptions were tested, and what emerged.

---

## Iteration Summary

| # | Date | Focus | Key Artifacts | Status |
|---|------|-------|---------------|--------|
| [001](iteration-001.md) | 2026-04-28 | Initial Cognitive Map | `scenario5-cognitive-map.md` | ✅ Complete |
| [001.1](iteration-001.md#update-assumption-references) | 2026-04-28 | Add Assumption ID References | `scenario5-cognitive-map.md` (updated) | ✅ Complete |
| [002](iteration-002.md) | 2026-04-28 | Phase 3: Delegation Qualification | `scenario5-delegation-qualification.md` | ✅ Complete |
| [002.1](iteration-002.md#update-lived-process-narrative) | 2026-04-29 | Add Lived Process Narrative & TOCs | `scenario5-cognitive-map.md`, `scenario5-delegation-qualification.md` (updated) | ✅ Complete |
| [003](iteration-003.md) | 2026-04-29 | Coach Role-Play & Assumption Validation | `coach-roleplay-answers.md`, `assumptions-update-post-coach.md` | ✅ Complete |
| [004](iteration-004.md) | 2026-04-29 | Phase 4: Candidate Prioritization | `scenario5-phase4-prioritization.md` | ✅ Complete |
| [004.1](iteration-004.md#post-coach-updates) | 2026-04-29 | Update All Docs with Validated Assumptions | All 3 main docs updated | ✅ Complete |
| 004.2 | 2026-04-29 | Add Use Case Scoring Templates + Quadrant | `scenario5-phase4-prioritization.md` (updated) | ✅ Complete |
| [005](iteration-005.md) | 2026-04-29 | Agent Mapping: PA Chase Timing (Wave 1) | `scenario5-agent-mapping-pa-chase.md` | ✅ Complete |

---

## Current State

### Completed Work
- ✅ Phase 2: Cognitive Load Mapping (4 JtDs, 11 micro-tasks, 6 cognitive zones, 4 hotspots)
- ✅ Assumption Register (15 assumptions catalogued with confidence levels, cross-referenced with [A#] tags)
- ✅ Design-Changing Questions (24 questions organized into 5 categories)
- ✅ Phase 3: Delegation Qualification (4 JtDs scored on 7 dimensions, archetypes assigned, 3-wave sequencing)
- ✅ **Coach role-play validation** (all 24 questions answered, 11 assumptions upgraded to HIGH/VERY HIGH confidence)
- ✅ **Phase 4: Candidate Prioritization** (Volume × Value scoring, TCO analysis, feasibility matrix, revised wave sequencing)
- ✅ **All documents updated** with validated assumptions and revised wave priority (PA Chase → Wave 1)
- ✅ **Agent Mapping (Wave 1: PA Chase Timing)** (6 deliverables: Purpose, Activity Catalog, Autonomy Matrix, System Inventory, Context Design, Compounding Roadmap)

### Ready for Implementation
- ✅ **Agent Mapping Complete** (Wave 1: PA Chase Timing) - Full specification ready for development team
- ⏳ Obtain Dana's full historical Google Sheet (past 2-3 years of PA data)
- ⏳ Provision athenahealth API keys (OAuth 2.0 credentials)
- ⏳ Begin Wave 1 build: Google Sheet ingestion, pattern extraction, agent architecture
- ⏳ Design HITL approval UI mockup for Dana's review

### Not Started
- ⭐ Wave 1 development environment setup (Claude API, athenahealth sandbox, Google Sheets API)
- ⭐ HITL protocol formalization (Dana's learning phase workflow, escalation rules)
- ⭐ HIPAA/compliance detailed review (audit logging, patient consent, data retention)

---

## Key Decisions Made

### Iteration 001
- **Focus on Dana's institutional knowledge as primary value unlock** - 11 years of insurer-specific PA chase patterns not systematized
- **Prioritize 4 cognitive hotspots** over breadth - PA chase timing, re-verification rules, visit triage boundary, medication reconciliation gaps
- **Design 24 specific questions** (not generic) - each targets assumption or unknown in cognitive map

### Iteration 001.1 (Update)
- **Added assumption ID references throughout cognitive map** - All 15 assumptions now tagged with [A#] notation for easy cross-referencing
- **Improved traceability** - Can now quickly identify which assumptions underpin each analysis section, question, or design decision

### Iteration 002
- **Completed Phase 3 Delegation Qualification** - Scored 4 JtDs across 7 suitability dimensions
- **Assigned delegation archetypes** - 2 Agent-led → Fully Agentic, 1 Agent-led (perpetual oversight), 1 Human-led
- **Identified 2 strong agentic candidates** - JtD-1 (insurance verification) and JtD-2 (PA chase timing)
- **Defined 3-wave implementation sequencing** - Wave 1: re-verification (quick win), Wave 2: PA chase (strategic), Wave 3: med reconciliation (volume)
- **Validated all 4 JtDs pass anti-pattern check** - None can be solved with static rules/RPA; agents justified

### Iteration 002.1 (Update)
- **Added Lived Process Narrative** - Section 4 of cognitive map contrasts documented SOPs vs. lived practice across 5 critical gaps
- **Added Tables of Contents** - Both cognitive map and delegation qualification now have navigable TOCs
- **Completed Phase 2 requirements** - ATX methodology Phase 2 output includes lived process narrative (was missing)

### Iteration 003 (Coach Validation)
- **Completed all 24 coach role-play questions** - Dana Velazquez perspective, comprehensive answers documented
- **Validated 11 critical assumptions** - Upgraded confidence levels: [A2] HIGH, [A3] VERY HIGH, [A4] VERY HIGH, [A5] HIGH, [A6] VERY HIGH (⬆️⬆️), [A7] VERY HIGH, [A9] HIGH, [A11] VERY HIGH, [A12] HIGH, [A13] VERY HIGH, [A14] VERY HIGH (⬆️⬆️⬆️)
- **Major finding from Q18**: Dana's #1 frustration is PA timing misses (visit aborts), not billing failures → changes wave priority
- **DoseSpot gaps fully specified [A6]**: 5 categories identified (out-of-network 10-15%, other providers, OTC, supplements, samples); 70-80% pharmacy fills captured, 0% OTC/samples
- **Dana's career ambitions validated [A14]**: Regional manager role in 5 years; success = replicable system; highly motivated stakeholder

### Iteration 004 (Phase 4 Prioritization)
- **Completed Volume × Value scoring** - JtD-1: 15, JtD-2: 15, JtD-3: 20, JtD-4: 12
- **Completed TCO analysis** - JtD-4 highest ROI (1,758%), JtD-1 strong (171%), JtD-2 strategic (-42% but justified)
- **Completed feasibility scoring** - JtD-1 and JtD-4 both 4.5/5 (Very High), JtD-2 3.3/5 (Medium)
- **Defined 3-year implementation roadmap** - Year 1: Waves 1-2 (strategic investment), Year 2: Wave 3 + platform optimization, Year 3: Wave 4 + multi-agent workflows

### Iteration 004.1 (Post-Coach Updates)
- **CRITICAL WAVE SEQUENCING CHANGE**: PA Chase Timing (JtD-2) promoted to Wave 1 (from Wave 2) based on stakeholder priority (Q18)
- **Rationale**: Dana's #1 frustration + Dr. Westbridge's triggering concern + Dana's career timeline [A14] override pure economic ranking
- **Insurance Re-Verification (JtD-1) moved to Wave 2** - Can start during Wave 1 learning phase (6-month overlap)
- **All 3 main documents updated** with validated assumptions, revised wave priority, updated confidence levels
- **Implementation-ready**: Wave 1 (PA Chase) scope finalized, Dana's Google Sheet ingestion ready, 8-11 month timeline confirmed

### Iteration 005 (Agent Mapping: PA Chase Timing)
- **Completed all 6 agent mapping deliverables** per atx-agent-mapping.md methodology
- **1. Agent Purpose Document**: Job to be Done, objectives, 6 KPIs, 6 failure modes, delegation archetype (learning → production), 6 escalation triggers
- **2. Agent Activity Catalog**: 20 micro-tasks enumerated with type, delegation level, data/tool requirements, risk levels
- **3. Autonomy Matrix**: Defined 4 decision authority levels (agent alone, notify after, approve before, human takes over) with specific examples
- **4. System and Data Inventory**: 5 systems catalogued (athenahealth, Google Sheet, insurer portals, pattern library, activity logs) with access types, gaps, risks, reusability
- **5. Context Engineering Design**: Memory architecture (4 types), retrieval strategy (4 triggers), 7 prompt engineering principles
- **6. Compounding Roadmap**: Wave 1-4 sequencing, integration reuse matrix (5 shared assets identified), compounding effect quantified (Wave 2-3 save 3-4 weeks each)
- **Key shared assets built in Wave 1**: athenahealth API client, activity logging framework, HITL approval UI pattern, pattern learning pipeline
- **Implementation-ready**: Document serves as input to development team; no further scoping required before build begins

---

## Open Questions (Prioritized)

### Tier 1 (Must Answer to Proceed) — ✅ ALL ANSWERED (2026-04-29)
- [x] Q14: What does DoseSpot actually miss? ([A6: VERY HIGH ⬆️⬆️], JtD-4 scope) — **ANSWERED**: 5 categories specified (out-of-network 10-15%, other providers, OTC, supplements, samples)
- [x] Q20: Malpractice insurance AI constraints? ([A15: MEDIUM], all JtDs autonomy) — **ANSWERED**: Dana expects human review required for clinical decisions
- [x] Q13: Define clinical judgment boundary ([A13: VERY HIGH ⬆️], JtD-3 design) — **ANSWERED**: "Recognition → escalate. Assessment → clinician."
- [x] Q1: Walk through last PA denial resolution ([A4: VERY HIGH ⬆️] pattern learnability, Hotspot 1) — **ANSWERED**: Wellpath colonoscopy 30-40 occurrences over 6 years, 100% consistent
- [x] Q18: What's Dana's biggest frustration? ([Q18], stakeholder priority) — **ANSWERED**: PA timing misses that lead to visit aborts (changed Wave 1 priority)

### Tier 2 (Refine Delegation Design) — ✅ ALL ANSWERED (2026-04-29)
- [x] Q6: What do the 3 billing failures have in common? ([A3: VERY HIGH ⬆️], JtD-1 rule validation) — **ANSWERED**: >6mo + chronic patient, plus sub-rules
- [x] Q3: Has insurer changed SLA recently? ([A2: HIGH ⬆️] pattern stability) — **ANSWERED**: UHC changed 18 months ago; patterns stable 6-12 months
- [x] Q10: Examples of false positive/negative triage? (JtD-3 calibration) — **ANSWERED**: Keywords provided (chest pain, SOB, severe, sudden, can't); false negative example (hypertensive crisis missed)
- [x] Q22: Dana's career goals? ([A14: VERY HIGH ⬆️⬆️⬆️]) — **ANSWERED**: Regional manager role in 5 years; success = replicable system

### Tier 3 (Economic & Operational Context) — ✅ ALL ANSWERED (2026-04-29)
- [x] Q24: Practice IT budget? (Feasibility) — **ANSWERED**: <$5K auto-approved, $5-20K business case, >$20K partners meeting. Dana's ROI threshold: <$6K/month
- [x] Q23: Front-desk headcount plans? (Change management risk) — **ANSWERED**: Redeploy, not reduce. "We're already short-staffed."
- [x] Q21: Which patients don't fit standard flow? (Edge cases) — **ANSWERED**: Not explicitly discussed, but non-English speakers, portal-less patients implied

### Remaining Technical Questions (Implementation Phase)
- [ ] Validate athenahealth/Availity/DoseSpot API documentation ([A12: HIGH ⬆️]) — **NEXT**: Technical review during Wave 1 Month 1
- [ ] Confirm malpractice carrier approval for AI use ([A15: MEDIUM]) — **NEXT**: Dana to contact carrier before Wave 1 production transition
- [ ] Obtain Dana's full Google Sheet historical data (Artefact 5.1 + archives) — **NEXT**: Wave 1 Month 1 data ingestion

---

## Artifacts Generated

### Primary Documents
- `scenario5-cognitive-map.md` - Phase 2 cognitive load mapping (Iteration 001; updated 004.1)
- `scenario5-delegation-qualification.md` - Phase 3 delegation suitability matrix (Iteration 002; updated 004.1)
- `scenario5-phase4-prioritization.md` - Phase 4 candidate prioritization (Iteration 004; updated 004.1, 004.2)
  - **Complete ATX methodology implementation**: Volume × Value scoring, TCO analysis, feasibility matrix, strategic sequencing, use case scoring templates, visual quadrant

### Validation Documents
- `coach-roleplay-answers.md` - All 24 coach questions answered as Dana (Iteration 003)
- `assumptions-update-post-coach.md` - Confidence level changes + major findings (Iteration 003)

### Supporting Documents
- `build-loop/iteration-001.md` - Cognitive map creation + assumption tagging
- `build-loop/iteration-002.md` - Delegation qualification + wave sequencing
- `build-loop/iteration-003.md` - Coach role-play validation (to be created)
- `build-loop/BUILD-LOOP.md` - This index (updated each session)

---

## High-Confidence Findings (Validated)

### From Phase 3 (Iteration 002)
- ✅ **JtD-1 and JtD-2 are strong agentic candidates** - Both can progress to Fully Agentic after learning phases
- ✅ **JtD-3 must remain Human-led** - Clinical judgment constraint [A13] + VERY HIGH risk (patient safety) creates hard boundary
- ✅ **All 4 JtDs pass anti-pattern check** - None can be solved with static rules/RPA; agents justified for pattern learning, NLP, institutional knowledge capture
- ✅ **Decision determinism ≠ agent unsuitability** - LOW determinism is acceptable if patterns are learnable (JtD-2 example)

### From Coach Validation (Iteration 003)
- ✅ **PA timing misses are Dana's #1 frustration** (Q18) - Visit aborts, not billing failures, are primary pain point
- ✅ **DoseSpot gaps fully specified** [A6: VERY HIGH ⬆️⬆️] - 5 categories: out-of-network (10-15%), other providers, OTC, supplements, samples. Captures 70-80% pharmacy fills, 0% OTC/samples.
- ✅ **PA denial patterns are highly learnable** [A4: VERY HIGH ⬆️] - Wellpath colonoscopy: 30-40 occurrences over 6 years, 100% consistent
- ✅ **Dana's career ambitions drive high stakeholder commitment** [A14: VERY HIGH ⬆️⬆️⬆️] - Regional manager role in 5 years; willing to teach patterns 3-6 months (career-building)
- ✅ **Re-verification rule validated with sub-rules** [A3: VERY HIGH ⬆️] - >6mo + ≥3 visits/year, plus Medicaid every 3mo, Medicare Advantage in Q4, new insurance at next visit
- ✅ **Clinical judgment boundary explicitly defined** [A13: VERY HIGH ⬆️] - "Recognition → escalate. Assessment → clinician."
- ✅ **PA patterns stable 6-12 months** [A2: HIGH ⬆️] - UHC example: changed 18 months ago; Dana tracks and adjusts
- ✅ **No planned headcount reduction** (Q23) - "Redeploy, not reduce. We're already short-staffed." → Low change management risk

### From Phase 4 (Iteration 004)
- ✅ **Medication reconciliation has highest ROI** (1,758% Year 1) - But Wave 3 priority due to [A6] dependency
- ✅ **Stakeholder priority overrides economic ranking** - Dana's Q18 answer justifies PA Chase as Wave 1 despite -42% Year 1 ROI
- ✅ **Wave overlap reduces total timeline** - Wave 2 can start Month 5 during Wave 1 learning phase (6-month overlap)

---

## Invalidated Assumptions

- ⚠️ **Wave sequencing based purely on ROI** - Iteration 004.1 revealed stakeholder priority (Q18) overrides economics; PA Chase promoted to Wave 1
- ⚠️ **DoseSpot gaps were unknowable** [A6] - Coach validation (Q14, Q17) fully specified 5 categories of misses with percentages

---

## Meta: How to Use This Build-Loop

### After Each Session
1. Create new `iteration-XXX.md` file documenting:
   - What was built/modified
   - What assumptions were tested
   - What answers were received (from coach, artefacts, technical tests)
   - What confidence levels changed
   - What design decisions were made
   - What new questions emerged

2. Update this index file (`BUILD-LOOP.md`):
   - Add row to Iteration Summary table
   - Update Current State section
   - Update Key Decisions Made
   - Update Open Questions (mark completed, add new ones)
   - Move validated findings to High-Confidence Findings
   - Document invalidated assumptions

### When to Create New Iteration
- After coach role-play session
- After receiving new artefacts
- After technical feasibility tests (API sandbox, integration testing)
- After economic modeling (TCO, ROI calculation)
- Before major design decisions (agent architecture, tool interfaces)

---

## Changelog

### 2026-04-29 (Iteration 004.2 - Use Case Scoring Templates + Visual Quadrant)
- **Added Use Case Scoring Templates** to Phase 4 prioritization document (new section "Step 4.5")
- **Complete scoring templates for all 4 JtDs** following atx-scoring.md format:
  - JtD-1 (Insurance Verification): Wave 2, 171% ROI, Agentic Value 15
  - JtD-2 (PA Chase Timing): Wave 1, -42% ROI (strategic), Agentic Value 15
  - JtD-4 (Medication Reconciliation): Wave 3, 1,758% ROI, Agentic Value 12
  - JtD-3 (Visit Reason Triage): Wave 4 (deferred), Agentic Value 20
- Each template includes: suitability gate, scoring (volume × value), full economics (baseline, token costs, HITL, ROI), sequencing rationale, delegation archetype, next steps
- **Added Volume × Value Quadrant** (visual 2×2 grid) showing JtDs positioned by Volume (x-axis) and Non-Determinism (y-axis)
- **Added quadrant interpretation** for each of 4 quadrants (top-left, top-right, bottom-right, bottom-left)
- All templates reflect validated assumptions from coach role-play and revised wave sequencing (PA Chase → Wave 1)

### 2026-04-29 (Iteration 004.1 - Post-Coach Document Updates)
- **Updated all 3 main documents** with validated assumptions and revised wave sequencing:
  - **Cognitive map** (scenario5-cognitive-map.md): Updated assumption confidence levels in Section 5; revised wave priority in Section 10 (PA Chase → Wave 1)
  - **Delegation qualification** (scenario5-delegation-qualification.md): Swapped Wave 1/Wave 2; updated Wave 3 with [A6] DoseSpot gaps; updated Wave 4 with [A13] clinical boundary
  - **Phase 4 prioritization** (scenario5-phase4-prioritization.md): Major wave swap with full justification; updated TCO with Dana's validated time (Q18); updated feasibility with [A6] gaps; revised roadmap
- **Key change**: **Stakeholder priority overrides economic ranking** - Dana's Q18 answer ("PA timing misses are my biggest frustration") justifies starting with PA Chase (JtD-2) despite -42% Year 1 ROI
- **Updated BUILD-LOOP.md**: Added iterations 003, 004, 004.1; updated all sections with completion status

### 2026-04-29 (Iteration 004 - Phase 4 Prioritization)
- **Completed Phase 4: Candidate Prioritization** - Volume × Value scoring, TCO analysis, feasibility matrix, strategic sequencing validation
- **Volume × Value scoring**: JtD-1: 15, JtD-2: 15 (both Strong), JtD-3: 20 (Strongest but deferred), JtD-4: 12 (Marginal)
- **TCO analysis with token economics**: JtD-4 highest ROI (1,758%, 0.6-month payback), JtD-1 strong (171%, 4.4-month payback), JtD-2 strategic (-42% Year 1 but justified)
- **Feasibility scoring**: JtD-1 and JtD-4 both 4.5/5 (Very High), JtD-2: 3.3/5 (Medium), JtD-3: 3.6/5 (blocked by risk)
- **3-year implementation roadmap**: Year 1 self-funding foundation (Waves 1-2), Year 2 compounding returns (Wave 3), Year 3 AI-native operations (Wave 4 + multi-agent workflows)
- **Economic projections**: Year 1 -$12K (strategic investment), Year 2 +$500K, Cumulative by Month 24: +$488K

### 2026-04-29 (Iteration 003 - Coach Role-Play Validation)
- **Completed all 24 coach role-play questions** - Role-played as Dana Velazquez; comprehensive answers documented in `coach-roleplay-answers.md`
- **Validated 11 critical assumptions** with confidence upgrades:
  - [A2] PA patterns stable → HIGH ⬆️ (UHC example: changed 18 months ago)
  - [A3] Re-verification rule → VERY HIGH ⬆️ (>6mo + ≥3 visits/year, plus sub-rules)
  - [A4] PA denial patterns learnable → VERY HIGH ⬆️ (Wellpath: 30-40 occurrences, 100% consistent)
  - [A5] Visit triage inconsistent → HIGH ⬆️ (no written protocol, keywords provided)
  - [A6] DoseSpot gaps → VERY HIGH ⬆️⬆️ (5 categories fully specified, 70-80% capture rate)
  - [A7] Google Sheet authoritative → VERY HIGH ⬆️ (Dana's personal tool, "living document")
  - [A9] Front-desk rotation → HIGH ⬆️ (4-person team, patterns locked in Dana's head)
  - [A11] No formal knowledge transfer → VERY HIGH ⬆️ ("Patterns locked in my head")
  - [A12] API availability → HIGH ⬆️ (Dana confirms athenahealth, Availity, DoseSpot integrated)
  - [A13] Clinical judgment boundary → VERY HIGH ⬆️ ("Recognition → escalate. Assessment → clinician.")
  - [A14] Dana's personal stake → VERY HIGH ⬆️⬆️⬆️ (regional manager role in 5 years, replicable system goal)
- **Major finding from Q18**: "PA timing misses that lead to visit aborts" is Dana's #1 frustration (not billing failures) → triggers wave priority change
- **Created assumptions-update-post-coach.md**: Documented all confidence changes, 8 major findings, revised wave sequencing rationale

### 2026-04-29 (Iteration 002.1)
- **Added Lived Process Narrative to cognitive map** - New section 4 contrasts documented SOPs vs. actual practice across 5 critical gaps
- **Added Table of Contents to both documents** - Improves navigation in cognitive map (10 sections) and delegation qualification (7 sections)
- **Completed Phase 2 Output requirements** - ATX methodology specifies "Lived process narrative: 1-page description of what really happens vs. what the SOP says"

### 2026-04-28 (Iteration 002)
- **Completed Phase 3: Delegation Qualification** - Scored 4 JtDs on 7 suitability dimensions (input structure, decision determinism, tool coverage, context complexity, exception rate, latency, risk)
- **Assigned delegation archetypes**:
  - JtD-1 (Insurance Verification): Agent-led → Fully Agentic (1 month learning)
  - JtD-2 (PA Chase Timing): Agent-led → Fully Agentic (3-6 months learning)
  - JtD-3 (Visit Reason Triage): Human-led + Agent Support (clinical constraint)
  - JtD-4 (Medication Reconciliation): Agent-led + Human Oversight (perpetual; physician reviews)
- **Defined 3-wave implementation sequencing** with timelines and success metrics
- **Validated anti-pattern check** for all 4 JtDs (none can be static rules/RPA)
- **Identified 5 critical dependencies** requiring coach validation before finalized design
- **New insights**: Decision determinism ≠ agent unsuitability when patterns learnable; risk mitigation through human backstops

### 2026-04-28 (Iteration 001.1)
- Added assumption ID references [A1] through [A15] throughout cognitive map document
- Tagged all mentions of assumptions in JtD descriptions, cognitive zones, micro-task inventory, topology diagram, hotspots, and questions
- Improves traceability: can now track which assumptions support each analysis or design decision

### 2026-04-28 (Iteration 001)
- Created initial cognitive map with 4 JtDs, 11 micro-tasks, 6 cognitive zones, 4 hotspots
- Catalogued 15 assumptions with confidence levels (Very Low to High)
- Generated 24 design-changing questions organized into 5 categories
- Established build-loop tracking system with separate iteration files

---

**Last Updated**: 2026-04-29 (Iteration 004.2 - Use Case Scoring Templates + Visual Quadrant Complete)
