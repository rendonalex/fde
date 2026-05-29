# Iteration 004: Phase 4 Candidate Prioritization + Post-Coach Document Updates

**Date**: 2026-04-29  
**Session Type**: Phase 4 Analysis + Document Consolidation  
**Status**: ✅ Complete

---

## Overview

This iteration completed the ATX Assessment methodology through Phase 4 (Candidate Prioritization), then updated all three main documents with validated assumptions from the coach role-play (Iteration 003). The critical output: **wave sequencing changed** based on stakeholder priority revealed in Q18.

---

## What Was Built

### Phase 4: Candidate Prioritization (`scenario5-phase4-prioritization.md`)

**Document structure** (8 sections):
1. Step 1: Suitability Gating (Validation)
2. Step 2: Volume × Value Scoring
3. Step 3: Total Cost of Ownership (TCO) Assessment
4. Step 4: Feasibility Scoring Matrix
5. Step 5: Strategic Sequencing Validation
6. Step 6: Prioritized Candidate Shortlist
7. Step 7: Implementation Roadmap (3-year plan)
8. Step 8: Assumption Dependencies & Update Protocol

**Key outputs**:
- **Volume × Value scores**: JtD-1: 15, JtD-2: 15, JtD-3: 20 (deferred), JtD-4: 12
- **TCO analysis with token economics**:
  - JtD-1 (Insurance): $108,264/year savings, $40K build, 171% Year 1 ROI, 4.4-month payback
  - JtD-2 (PA Chase): $20,897/year savings, $36K build, -42% Year 1 ROI, 20.6-month payback (strategic)
  - JtD-4 (Med Recon): $557,464/year savings, $30K build, 1,758% Year 1 ROI, 0.6-month payback
- **Feasibility scores**: JtD-1: 4.5/5, JtD-2: 3.3/5, JtD-4: 4.5/5, JtD-3: 3.6/5 (risk-blocked)
- **Original wave sequencing** (pre-coach validation):
  - Wave 1: Insurance Re-Verification (self-funding, 171% ROI)
  - Wave 2: PA Chase Timing (strategic value, -42% ROI)
  - Wave 3: Medication Reconciliation (highest ROI, 1,758%)

---

## What Was Discovered

### Major Finding: Stakeholder Priority Overrides Economic Ranking

**Source**: Coach validation Q18 answer (from Iteration 003)

**Dana's quote**: "That's easy: **the PA timing misses that lead to visit aborts**. When a patient shows up for a procedure or an imaging scan, expecting to get it done, and then we tell them, 'Sorry, the prior auth is still pending, we have to reschedule' — that's the worst. If I could fix one thing, it would be proactive PA chase timing that never misses a deadline."

**Impact**:
- Dana's #1 frustration is PA timing misses (visit aborts), NOT billing failures from insurance re-verification misses
- This was Dr. Westbridge's triggering concern (Artefact 5.2: patient TJ's second visit abort)
- **Economic ranking said**: Insurance (Wave 1, 171% ROI) → PA Chase (Wave 2, -42% ROI) → Med Recon (Wave 3, 1,758% ROI)
- **Stakeholder priority says**: PA Chase must be Wave 1 (Dana's #1) → Insurance Wave 2 (still valuable) → Med Recon Wave 3 (highest ROI)

**Justification for wave swap**:
1. **Stakeholder alignment**: Starting with Dana's #1 priority builds trust, momentum, buy-in
2. **Business driver**: Dr. Westbridge asked Dana to address AI specifically because of PA timing misses (not billing failures)
3. **Institutional knowledge urgency**: Dana wants regional manager role in 5 years [A14: VERY HIGH ⬆️⬆️⬆️] → must capture her 11-year patterns [A2, A4, A7] before she moves
4. **Organizational readiness**: Dana willing to teach patterns 3-6 months (career-building: "success = replicable system for other practices")
5. **Timeline optimization**: Wave 2 (Insurance) can start Month 5 during Wave 1 learning phase → 6-month overlap, no delay

**Decision**: **Swap Wave 1 and Wave 2** based on validated stakeholder priority.

---

## Iteration 004.1: Post-Coach Document Updates

After completing Phase 4, realized all three main documents needed updates to reflect validated assumptions and revised wave sequencing. Created "iteration 004.1" as a sub-iteration to consolidate updates.

### Documents Updated

#### 1. `scenario5-cognitive-map.md`

**Section 5: Assumption Register**
- Updated all 15 assumptions with post-coach confidence levels
- Added ⬆️ indicators for 11 upgraded assumptions:
  - [A2] MEDIUM → HIGH (PA patterns stable 6-12 months)
  - [A3] HIGH → VERY HIGH (re-verification rule validated with sub-rules)
  - [A4] MEDIUM→HIGH → VERY HIGH (PA denial patterns 100% consistent)
  - [A5] MEDIUM → HIGH (visit triage inconsistency confirmed)
  - [A6] LOW→MEDIUM → VERY HIGH ⬆️⬆️ (DoseSpot gaps fully specified: 5 categories)
  - [A7] HIGH → VERY HIGH (Google Sheet confirmed as authoritative)
  - [A8] LOW → MEDIUM (3 billing failures in Q4 confirmed)
  - [A9] MEDIUM → HIGH (front-desk rotation creates knowledge fragmentation)
  - [A11] MEDIUM→HIGH → VERY HIGH (no formal knowledge transfer system)
  - [A12] MEDIUM → HIGH (APIs confirmed by Dana, needs technical validation)
  - [A13] HIGH → VERY HIGH (clinical boundary explicitly defined)
  - [A14] VERY LOW → VERY HIGH ⬆️⬆️⬆️ (Dana's regional manager ambitions clarified)

**Section 10: Next Steps**
- **Completely rewritten** to reflect revised wave sequencing
- Added "CRITICAL FINDING from Q18" callout
- **Wave 1 changed to PA Chase Timing** (Dana's #1 priority)
- **Wave 2 changed to Insurance Re-Verification** (can overlap with Wave 1)
- Added immediate next steps for Wave 1 implementation (ingest Google Sheet, extract patterns, build agent)

#### 2. `scenario5-delegation-qualification.md`

**Wave Sequencing Section (Revised)**
- **Wave 1 title changed**: "High Suitability, Clear Rules (Quick Wins)" → "High Value, Institutional Knowledge Capture (Strategic Priority)"
- **Wave 1 target changed**: JtD-1 (Insurance) → JtD-2 (PA Chase Timing)
- Added "POST-COACH UPDATE (2026-04-29)" banner at top of sequencing section
- **Rationale for Wave 1**: Dana's #1 priority (Q18), institutional knowledge urgency [A14], prevents visit aborts, validated PA time 1-2 hours/day [Q18]
- **Wave 2 title changed**: "High Value, Institutional Knowledge Capture (Strategic)" → "High Suitability, Clear Rules (Self-Funding)"
- **Wave 2 target changed**: JtD-2 (PA Chase) → JtD-1 (Insurance)
- **Wave 2 rationale**: Can start Month 5 during Wave 1 learning phase (6-month overlap), builds reusable athenahealth + Availity integrations for Wave 3
- **Wave 3 updated**: [A6] DoseSpot gaps now fully specified (5 categories), agent prompts finalized, build time +1 week
- **Wave 4 updated**: [A13] clinical boundary validated ("Recognition → escalate"), [A15] malpractice expects human review

**Output Artifacts Section**
- Updated sequencing summary: "Wave 1: PA chase, Wave 2: re-verification, Wave 3: med reconciliation"
- Updated next steps: All critical assumptions now validated, ready for Wave 1 implementation

#### 3. `scenario5-phase4-prioritization.md`

**Step 3: TCO Assessment - JtD-2 (PA Chase Timing)**
- Updated "Baseline Cost (Human)" section:
  - Changed "**[NEEDS COACH VALIDATION - Q18]**" to "**Validated time** (Q18)"
  - Added Dana's quote confirming 1-2 hours/day on PA chase work
  - Marked [A2: HIGH ⬆️] and [A4: VERY HIGH ⬆️] throughout

**Step 5: Strategic Sequencing Validation**
- Added "POST-COACH UPDATE (2026-04-29)" banner at top
- **Completely revised sequencing criteria table**:
  - Added new criterion: "Stakeholder priority" (VERY HIGH weight) at top
  - JtD-2 (PA Chase) scores ✅ on stakeholder priority (Dana's #1)
  - JtD-1 (Insurance) scores ⚠️ (back-office)
- **Rewrote "Wave 1 Validation" section**:
  - Changed from "JtD-1 (Insurance Re-Verification)" to "REVISED Wave 1: JtD-2 (PA Chase Timing) — **Dana's #1 Priority**"
  - Added extensive justification with 5 bullet points (stakeholder alignment, business driver, institutional knowledge urgency, organizational readiness, timeline optimization)
  - Included Dana's full Q18 quote
  - Timeline: 8-11 months (2 months build + 3-6 months learning)
- **Rewrote "Wave 2 Validation" section**:
  - Changed from "JtD-2 (PA Chase Timing)" to "REVISED Wave 2: JtD-1 (Insurance Re-Verification) — **Self-Funding**"
  - Added justification for moving to Wave 2 (stakeholder priority drives sequencing, but economics remain strong)
  - Noted Wave 2 can start Month 5 during Wave 1 learning phase
- **Updated "Wave 3 Validation" section**:
  - Added [A6: VERY HIGH ⬆️⬆️] DoseSpot gaps fully specified
  - Listed all 5 categories of misses with Dana's estimates (70-80% pharmacy fills, 0% OTC/samples)
  - Updated agent prompt design with explicit prompts for missing sources
  - Build time +1 week (from 3 to 4 weeks)

**Wave Structure Summary Table**
- **Completely revised** to reflect new sequencing:
  - Row 1: Wave 1 = PA Chase Timing (8-11 months, $36K, -42% ROI, 20.6mo payback)
  - Row 2: Wave 2 = Insurance Re-Verification (4 months, $40K, 171% ROI, 4.4mo payback, can start Month 5)
  - Row 3: Wave 3 = Medication Reconciliation (4 months, $30K, 1,758% ROI, 0.6mo payback, starts Month 13)
- Updated rationale column with validated assumptions and confidence indicators
- Added note: "Key change (post-coach): **Stakeholder priority overrides economic ranking**"

**Prioritized Candidate Shortlist**
- Added "POST-COACH UPDATE" banner
- **Re-ranked table** with JtD-2 (PA Chase) as Rank #1 (stakeholder priority)
- Updated "Recommended Wave" column: JtD-2 → Wave 1 ⬆️, JtD-1 → Wave 2 ⬇️
- Rewrote "Final Sequencing Recommendation" section with revised waves

**Implementation Roadmap**
- **Year 1 section completely rewritten**:
  - "Self-Funding Foundation (Waves 1-2)" → "Stakeholder Priority + Self-Funding (Waves 1-2)"
  - Added "POST-COACH UPDATE" note at top
  - **Months 1-11: Wave 1 — PA Chase Timing** (was Insurance)
  - **Months 5-8: Wave 2 — Insurance Re-Verification** (overlaps with Wave 1 learning phase)
  - Updated economics: Year 1 net = -$12K (Wave 1 strategic investment -$26K + Wave 2 partial $14K)
- **Year 2 section updated**:
  - Wave 3 starts Month 13 (was Month 16)
  - Removed reference to "[A6] validation" (already validated)
  - Updated cumulative economics: +$488K by end of Month 24

**Assumption Dependencies Table**
- **Completely revised** to show validation status:
  - Changed headers from "Coach Questions" to "Validated Answer" and "Impact on Design"
  - Marked 9 assumptions as "✅ VALIDATED" with validation details
  - [A12] marked as "⚠️ INFERRED (HIGH ⬆️)" (needs technical validation)
  - Each row now shows what was learned from coach and how it impacts design

**Update Protocol Section**
- Renamed "Update Protocol (Post-Coach Session)" to "Update Protocol — POST-COACH COMPLETION (2026-04-29)"
- Added "✅ Coach validation completed" banner
- Listed all 5 update categories as "✅ completed" with specific changes documented
- Added reference to iteration-003.md for tracking

**Next Steps Section**
- Renamed "Before Wave 1 Build" to "Pre-Implementation (Completed)"
- Marked steps 1-4 as ✅ complete
- Renamed "Wave 1 Build (if proceeding)" to "Wave 1 Build (PA Chase Timing) — Ready to Proceed"
- Updated steps 5-13 to reflect PA Chase implementation (not Insurance)
- Added explicit Google Sheet pattern extraction step

#### 4. `build-loop/BUILD-LOOP.md`

**Iteration Summary Table**
- Added row for iteration 003 (Coach Role-Play & Assumption Validation)
- Added row for iteration 004 (Phase 4: Candidate Prioritization)
- Added row for iteration 004.1 (Update All Docs with Validated Assumptions)

**Current State Section**
- Moved assumption validation and Phase 4 from "In Progress" to "Completed Work"
- Updated "Ready for Implementation" with Wave 1 specifics (PA Chase Timing)

**Key Decisions Made**
- Added subsection "Iteration 003 (Coach Validation)" with 5 bullet points
- Added subsection "Iteration 004 (Phase 4 Prioritization)" with 4 bullet points
- Added subsection "Iteration 004.1 (Post-Coach Updates)" with 4 bullet points highlighting wave swap

**Open Questions**
- Marked all Tier 1, Tier 2, and Tier 3 questions as "[x] ANSWERED" with validation details
- Added new section "Remaining Technical Questions (Implementation Phase)" for next steps

**High-Confidence Findings**
- Added subsection "From Coach Validation (Iteration 003)" with 8 validated findings
- Added subsection "From Phase 4 (Iteration 004)" with 3 validated findings

**Invalidated Assumptions**
- Added 2 invalidated assumptions (wave sequencing based on ROI, DoseSpot gaps unknowable)

**Artifacts Generated**
- Added validation documents (coach-roleplay-answers.md, assumptions-update-post-coach.md)
- Added iteration-003.md reference (to be created)

**Changelog**
- Added detailed entry for "2026-04-29 (Iteration 004.1)" with document updates summary
- Added detailed entry for "2026-04-29 (Iteration 004)" with Phase 4 outputs
- Added detailed entry for "2026-04-29 (Iteration 003)" with coach validation summary

---

## Assumptions Tested & Results

### Previously Unvalidated (now validated in Iteration 003, applied in 004.1):

| Assumption | Pre-Coach | Post-Coach | Impact on Phase 4 |
|-----------|-----------|------------|-------------------|
| **[A2]** PA pattern stability | MEDIUM | HIGH ⬆️ | JtD-2 feasibility "Context stability" validated at 3/5; learning phase 3-6 months confirmed |
| **[A3]** Re-verification rule | HIGH | VERY HIGH ⬆️ | JtD-1 scope finalized; rule is deterministic with sub-rules (Medicaid every 3mo, Medicare Advantage Q4, new insurance at next visit) |
| **[A6]** DoseSpot gaps | LOW→MEDIUM | VERY HIGH ⬆️⬆️ | JtD-4 scope finalized; agent prompts defined for 5 categories of misses; build time +1 week |
| **[A14]** Dana's personal stake | VERY LOW | VERY HIGH ⬆️⬆️⬆️ | Validates Dana's willingness to teach patterns 3-6 months (career-building); organizational readiness HIGH |
| **[Q18]** Dana's top frustration | Unknown | PA timing misses (visit aborts) | **WAVE SEQUENCING CHANGED**: PA Chase promoted to Wave 1 despite -42% Year 1 ROI; stakeholder priority overrides economics |

### Result: **Major design change**
- Original sequencing (pre-coach): Insurance (Wave 1) → PA Chase (Wave 2) → Med Recon (Wave 3)
- **Revised sequencing (post-coach)**: PA Chase (Wave 1) → Insurance (Wave 2) → Med Recon (Wave 3)

---

## Key Decisions Made

### Decision 1: Phase 4 Methodology

**What**: Use atx-scoring.md 5-step methodology for candidate prioritization
- Step 1: Suitability gating (pass/fail on input structure, decision determinism, tool coverage, risk)
- Step 2: Volume × Value scoring (execution frequency 1-5 × non-deterministic decision effort 1-5)
- Step 3: TCO assessment (baseline cost vs. agent cost, ROI, payback)
- Step 4: Feasibility scoring (6 factors: data availability, system integration, compliance, stability, org readiness, TCO viability)
- Step 5: Strategic sequencing (compounding thesis, integration reusability, self-financing)

**Why**: Provides quantitative backing for wave sequencing, validates Phase 3 qualitative decisions

**Result**: All 4 JtDs pass suitability gate; economic ranking differs from stakeholder priority

---

### Decision 2: Token Economics Model

**What**: Estimate token consumption per use case, calculate annual cost, compare to human baseline

**Model parameters**:
- Input tokens: $3/million (Claude 3.5 Sonnet)
- Output tokens: $15/million
- Tool calls: $0.001/call (estimated)
- Infrastructure: $0.001/case (hosted platform)

**Example (JtD-1 Insurance Verification)**:
- Input: ~1,200 tokens (patient ID, insurance info, visit history)
- Output: ~300 tokens (verification status, re-verification recommendation)
- Total: 1,500 tokens/case × $0.0081 = **$0.0081/case**
- Annual: 65,700 cases × $0.0081 = **$861/year** (vs. $110,460 human baseline)

**Why**: Validates that token economics are negligible compared to human labor cost (0.8% of baseline for JtD-1)

**Result**: All JtDs have positive ROI on token economics alone; build cost is primary investment

---

### Decision 3: Swap Wave 1 and Wave 2 Based on Stakeholder Priority

**What**: Promote PA Chase Timing (JtD-2) to Wave 1, move Insurance Re-Verification (JtD-1) to Wave 2

**Original rationale for Insurance as Wave 1**:
- Self-funding (171% Year 1 ROI, 4.4-month payback)
- Builds reusable athenahealth + Availity integrations for Wave 3
- No critical unknowns → can start immediately

**Counter-argument from coach validation (Q18)**:
- Dana explicitly said PA timing misses are her #1 frustration: "If I could fix one thing, it would be proactive PA chase timing that never misses a deadline"
- Dr. Westbridge's triggering concern was PA timing miss (Artefact 5.2: patient TJ's visit abort), not billing failures
- Dana's career timeline [A14: VERY HIGH ⬆️⬆️⬆️] creates urgency to capture her 11-year institutional knowledge before she moves to regional role

**Decision**: **Stakeholder priority overrides economic ranking**
- Wave 1: PA Chase Timing (Dana's #1, institutional knowledge capture, prevents visit aborts)
- Wave 2: Insurance Re-Verification (can start Month 5 during Wave 1 learning phase, still self-funding)
- Net timeline impact: Zero (Wave 2 overlaps with Wave 1 learning phase)
- Net economic impact Year 1: -$12K (strategic investment in Wave 1 -$26K + Wave 2 partial +$14K)

**Why**: 
1. Starting with Dana's #1 priority builds trust, momentum, stakeholder buy-in
2. Aligns with business driver (Dr. Westbridge's request to address AI)
3. Captures institutional knowledge before Dana's career transition
4. No timeline penalty (overlap during Wave 1 learning phase)

**Result**: All three documents updated with revised wave sequencing; BUILD-LOOP.md updated to reflect decision rationale

---

### Decision 4: Document Consolidation Strategy (Iteration 004.1)

**What**: Update all three main documents with validated assumptions and revised wave sequencing in a single consolidation pass

**Why**:
- Phase 4 completed with provisional wave sequencing (pre-coach validation)
- Iteration 003 coach validation revealed major finding (Q18: PA timing is Dana's #1)
- Documents were inconsistent: cognitive map had original waves, delegation had original waves, Phase 4 had both original and provisional revised
- Risk: User or future reader would see conflicting information across documents

**Approach**: Create sub-iteration 004.1 to consolidate all updates
1. Start with cognitive map (foundational assumptions)
2. Update delegation qualification (wave sequencing rationale)
3. Update Phase 4 prioritization (detailed economic/feasibility justification)
4. Update BUILD-LOOP.md (track all changes)

**Result**: All documents now consistent; assumptions validated throughout; wave sequencing justified with multi-layered rationale (stakeholder, economic, timeline, strategic)

---

## What Emerged

### Insight 1: Stakeholder Priority Can Override Economic Ranking

**What we learned**: Dana's Q18 answer ("PA timing misses are my biggest frustration") revealed that the economic ranking (Insurance 171% ROI first, PA Chase -42% ROI second) didn't align with stakeholder priority.

**Why this matters**: 
- Traditional prioritization would say: Start with highest ROI (Insurance 171%, then Med Recon 1,758%, then PA Chase -42%)
- But stakeholder-driven prioritization says: Start with what the champion cares about most (PA Chase), then self-funding (Insurance), then highest ROI (Med Recon)
- **ATX scoring methodology doesn't explicitly weight stakeholder priority** in Step 5 (Strategic Sequencing) — we added it as a criterion

**Design implication**: When stakeholder priority and economic ranking conflict, **consider stakeholder priority as a gate** (not just a scoring factor). If stakeholder is highly motivated [A14: VERY HIGH] and willing to champion the project, starting with their #1 priority can be more valuable than starting with highest ROI.

**Generalization**: For future projects, add "Stakeholder priority" as an explicit criterion in Step 5 (Strategic Sequencing) with VERY HIGH weight when:
1. Stakeholder is highly motivated and has clear champion role
2. Stakeholder priority is well-defined (not vague "make things better")
3. Starting with stakeholder priority doesn't block other waves (e.g., Wave 2 can overlap, reusable integrations not dependent on Wave 1)

---

### Insight 2: Wave Overlap Enables Aggressive Timelines

**What we learned**: Wave 2 (Insurance Re-Verification) can start Month 5 during Wave 1 (PA Chase) learning phase (Months 4-9), creating 6-month overlap.

**Why this matters**:
- Traditional waterfall sequencing would say: Wave 1 complete (Month 11) → Wave 2 start (Month 12) → Wave 2 complete (Month 15)
- Overlapped sequencing says: Wave 1 build complete (Month 3) → Wave 1 learning (Months 4-9) → Wave 2 starts during learning (Month 5) → Wave 2 complete (Month 8) → Wave 1 production (Month 10)
- **Net timeline savings**: 3 months (Wave 2 completes Month 8 instead of Month 15)

**Design implication**: When a wave has a long learning phase (3-6 months for PA Chase), subsequent waves can start during learning if:
1. Waves are independent (no shared integrations or dependencies)
2. Dana's time is available for both (Wave 1 learning is ~50 min/day, Wave 2 validation is ~1 hour total in Month 7)
3. Build teams are separate or sequential (Wave 1 build complete Month 3 → Wave 2 build starts Month 5)

**Generalization**: For multi-wave projects, identify learning phases as opportunities for parallelization. Don't wait for full production transition if the next wave is independent.

---

### Insight 3: Institutional Knowledge Capture Has Time Pressure

**What we learned**: Dana wants regional manager role in 5 years [A14: VERY HIGH ⬆️⬆️⬆️], which creates urgency to capture her 11-year PA chase patterns [A2, A4, A7] before she transitions.

**Why this matters**:
- If we wait 12-18 months to start Wave 1 (PA Chase), Dana may already be transitioning to new role
- Her replacement won't have the 11-year institutional knowledge → patterns lost
- **Institutional knowledge has shelf life** tied to employee tenure and career progression

**Design implication**: When institutional knowledge is concentrated in one person [A11: VERY HIGH]:
1. Assess stakeholder's career timeline (not just current role)
2. Prioritize knowledge capture before stakeholder transitions
3. Use learning phase as knowledge transfer mechanism (agent learns from human's corrections)
4. **Institutional knowledge capture can justify negative Year 1 ROI** if knowledge is at risk of being lost

**Generalization**: For projects with single-point-of-knowledge risk, add "knowledge preservation urgency" as a strategic sequencing criterion. If stakeholder is planning career transition within project timeline, prioritize knowledge capture early.

---

### Insight 4: Validated Assumptions Change Feasibility Scores

**What we learned**: [A6] DoseSpot gaps went from LOW→MEDIUM confidence (unknown scope) to VERY HIGH ⬆️⬆️ (5 categories fully specified with percentages). This increased JtD-4 feasibility "Data readiness" from ⚠️ to ✅.

**Why this matters**:
- Phase 4 feasibility scoring depends on assumption confidence
- LOW confidence assumptions create feasibility risk → lower scores
- Validating assumptions through coach role-play **de-risks the project** → higher feasibility, faster implementation decision

**Design implication**: When an assumption has LOW confidence and affects feasibility, **validate it before finalizing wave sequencing**. Don't proceed to build if critical unknowns remain.

**Generalization**: Use coach role-play or stakeholder interviews to validate assumptions BEFORE Phase 4 prioritization, not after. Phase 4 scores should reflect validated (or invalidated) assumptions, not speculation.

---

## Status at End of Iteration 004.1

### ✅ Complete
- Phase 4: Candidate Prioritization (Volume × Value, TCO, Feasibility, Strategic Sequencing)
- All 3 main documents updated with validated assumptions and revised wave sequencing
- BUILD-LOOP.md updated with iterations 003, 004, 004.1
- Implementation-ready documentation for Wave 1 (PA Chase Timing)

### 📋 Artifacts
- `scenario5-phase4-prioritization.md` (126 pages, 8 sections)
- `scenario5-cognitive-map.md` (updated Section 5 assumptions, Section 10 next steps)
- `scenario5-delegation-qualification.md` (updated wave sequencing, all 4 waves revised)
- `build-loop/BUILD-LOOP.md` (updated with 3 new iterations, 11 high-confidence findings)

### ⏳ Next Steps
1. **Wave 1 implementation** (PA Chase Timing):
   - Ingest Dana's Google Sheet (Artefact 5.1 + full historical data)
   - Extract insurer-specific patterns (Humana 6d, UHC 7d, Wellpath denial workaround, etc.)
   - Validate athenahealth/Availity API documentation [A12: HIGH ⬆️]
   - Build agent architecture (chase timing logic, escalation rules, HITL protocols)
   - Development environment setup (Claude API, athenahealth sandbox, Google Sheets API)
   - Dana learning phase (3-6 months): Dana approves all chase recommendations, agent learns from corrections
   - Production transition: Agent handles predictable insurers autonomously, Dana spot-checks Aetna

2. **Wave 2 preparation** (can start Month 5 during Wave 1 learning):
   - Insurance Re-Verification build (re-verification logic [A3: VERY HIGH ⬆️], chronic patient detection)
   - athenahealth + Availity integration (reusable in Wave 3)

3. **Governance/compliance** (parallel to Waves 1-2):
   - Malpractice carrier approval ([A15: MEDIUM] - Dana to contact before Wave 1 production)
   - HIPAA compliance review (audit logging, patient consent, data retention)
   - HITL protocol formalization (Dana's learning phase workflow, escalation rules)

---

## Decisions for Next Session

### Technical Validation Needed
- [ ] Validate athenahealth API documentation ([A12: HIGH ⬆️]) - rate limits, authentication, PA submission/status endpoints
- [ ] Validate Availity API documentation - eligibility verification, error codes, response structure
- [ ] Validate Google Sheets API - read historical data, extract insurer patterns
- [ ] Confirm DoseSpot API integration with athenahealth - medication reconciliation endpoints

### Organizational Validation Needed
- [ ] Dana to contact malpractice carrier for AI approval ([A15: MEDIUM]) - required before Wave 1 production
- [ ] Obtain Dana's full Google Sheet historical data (not just Artefact 5.1 sample)
- [ ] Confirm Dana's availability for 3-6 month learning phase (daily ~50 min PA review)
- [ ] Confirm front-desk availability for Wave 2 validation (1 month pilot, re-verification spot-checks)

---

**End of Iteration 004 + 004.1**
