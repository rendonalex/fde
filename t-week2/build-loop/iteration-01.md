# Build Loop Iteration 01 — Scenario 4 Cognitive Map & Discovery Questions
**Date**: 2026-04-30  
**Iteration**: Initial creation  
**Status**: Complete

---

## Objective

Create comprehensive cognitive load map and discovery questions for Scenario 4 (Community Content Moderation — MiniBase platform) following ATX methodology.

---

## Inputs Used

1. **enriched_scenarios.md** — Scenario 4 full context:
   - Platform: MiniBase (180K users, 12K posts/day, £1.4M/yr revenue)
   - Team: 8 volunteer moderators + 2 paid staff (Tom + Senior Moderator)
   - Work streams: Routine spam (72%), grey-zone review (24%), appeals (4%), IP claims (<1%)
   - Stakeholder: Tom Włodarczyk (Community Manager, Warsaw)
   - Mandate: "False positives are survivable; one viral false negative is existential"
   - 3 artefacts:
     - 4.1: Grey-zone post with user reports + OP reaction
     - 4.2: Discord thread (volunteer mod consensus-building)
     - 4.3: Tom's Google Sheet (account patterns, sub-forum norms)

2. **atx-assessment.md** — Phase 2: Cognitive Load Mapping guidance:
   - Step 1: Map lived process (not SOP)
   - Step 2: Decompose into Jobs to be Done (JtD)
   - Step 3: Map Cognitive Zones and Breakpoints
   - Step 4: Build micro-task inventory with 8 dimensions

3. **atx-concepts.md** — Key concepts:
   - Cognitive work vs. processes (Section: Cognitive work vs. processes)
   - Lived work vs. documented work (undocumented norms, institutional memory)
   - Jobs to be Done as cognitive contracts (purpose, context, outcomes)
   - Cognitive Zones and Breakpoints (control handoffs, probabilistic vs. deterministic)

---

## Outputs Created

### 1. **scenario4-cognitive-map.md** (15,200 words)
**Location**: `/Users/Alexandra_Rendon/gh/fde/t-week2/specs/`

**Structure**:
- Table of contents
- Executive summary (platform context, team, volumes, core tension)
- Scenario context (platform, function, work stream volumes table)
- **Lived vs. documented process** (critical finding: 14-page policy is baseline; effective moderation lives in undocumented layer)
- **5 Jobs to be Done** (JtD-1 to JtD-5):
  - JtD-1: Triage inbound content to queue
  - JtD-2: Resolve routine spam / clear violations (1,080/day, 9 hrs)
  - JtD-3: Review grey-zone cases (360/day, 30 hrs — **core bottleneck**)
  - JtD-4: Resolve user dispute appeals (60/day, 8 hrs)
  - JtD-5: Resolve IP-claim cases (3-5/wk, high risk)
- **5 Cognitive Zones**:
  - Zone 1: Intent recognition & triage
  - Zone 2: Context synthesis (undocumented norms, Tom's sheet, Discord, prior incidents)
  - Zone 3: Judgment & decision (false-negative risk dominates)
  - Zone 4: Action execution
  - Zone 5: Documentation & learning
- **Micro-task cognitive load inventory** (8-dimension scoring for JtD-2, JtD-3, JtD-4, JtD-5)
- **Assumptions register** (27 assumptions, A01-A27, with confidence levels)
- **8 key findings**:
  1. Grey-zone review is cognitive bottleneck (30 hrs/47 total)
  2. Lived process ≠ documented process (sub-forum norms, account patterns, prior incidents)
  3. Tom is single point of failure for high-risk cases
  4. False-negative risk dominates decision-making (2024 sponsor incident)
  5. Volunteer coordination is informal/async (Discord, not Discourse)
  6. Delegation suitability varies dramatically by stream (routine spam = high; grey-zone = low-medium; IP = human-only)
  7. Tool/data availability is fragmented (Discourse APIs available; gallery limited; Tom's sheet manual; Discord not integrated)
  8. Compliance/risk sensitivity is implicit, not codified

### 2. **scenario4-discovery-questions.md** (6,400 words)
**Location**: `/Users/Alexandra_Rendon/gh/fde/t-week2/specs/`

**Structure**:
- Purpose statement (design-changing questions, not generic)
- **20 questions in 9 categories**:
  - Cat 1: Tom's workload & escalation patterns (Q01-Q03)
  - Cat 2: 2024 sponsor incident & risk tolerance (Q04-Q05)
  - Cat 3: Sub-forum norms & undocumented knowledge (Q06-Q08)
  - Cat 4: Automation history & prior attempts (Q09)
  - Cat 5: IP-claim resolution workflow (Q10-Q11)
  - Cat 6: Volunteer moderator dynamics (Q12-Q14)
  - Cat 7: Volume, growth & seasonal patterns (Q15-Q16)
  - Cat 8: Tool integration & data access (Q17-Q18)
  - Cat 9: Compliance, risk & audit (Q19-Q20)
- **Question-to-assumption mapping table** (which assumptions each question targets)
- Usage notes for coach interactions

---

## Key Design Decisions

### 1. Assumption Discipline
**Every inference marked as assumption** with explicit confidence levels (high/medium/low):
- **High confidence** (14 assumptions): Directly supported by artefacts or brief
  - Example: A06 "IP claims always Tom-reviewed" ← Artefact 4.3 explicit
- **Medium confidence** (9 assumptions): Inferred from artefacts but not explicit
  - Example: A05 "~30-40% of grey-zone cases involve Discord consultation" ← Artefact 4.2 shows pattern but no frequency data
- **Low confidence** (4 assumptions): Not mentioned in brief/artefacts; critical gaps
  - Example: A18 "Volunteer retention stable" ← No data; high risk if wrong

### 2. Lived Process Emphasis
**Artefacts drive the analysis**, not the brief alone:
- Artefact 4.2 (Discord thread) proves: sub-forum norms override global policy, peer consultation is informal/async, prior incidents shape decisions
- Artefact 4.3 (Tom's Google Sheet) proves: account-level patterns tracked manually, escalation rules not in policy, sub-forum carve-outs exist
- Artefact 4.1 (grey-zone post) proves: "invited critique" is implicit (thread title = invitation), OP reaction validates harsh tone

### 3. Grey-Zone Review as Core Bottleneck
**30 hours/day of 47 total** (64% of effort) spent on grey-zone cases:
- High cognitive load (undocumented norms, cultural interpretation, prior-incident sensitivity)
- Non-deterministic (tone is contextual, invitation is implied)
- Turn-taking (Discord peer consultation)
- High false-negative risk (2024 sponsor incident as reference case)

**Implication**: Agent design must prioritize grey-zone *support* (context synthesis, risk flagging) over grey-zone *replacement*. Routine spam (9 hrs/day) is easier to automate but lower ROI.

### 4. Tom as Single Point of Failure
**Tom personally reviews**:
- Every IP claim (after 2024 incident)
- Every sponsor-related post (@vortex_minis)
- Every high-profile sculptor post (@sculpturedragon)
- Appeals involving his original decisions

**Unknown**: Tom's current workload breakdown (Q01), burnout risk (A21)

**Implication**: Agent design should *reduce Tom's load* by pre-filtering cases that don't need his review (e.g., "low-credibility IP claim from @vintage_kitbasher" vs. "high-credibility claim from @sculpturedragon").

### 5. Discovery Questions Target Design-Changing Information
**Not generic** ("walk me through your typical day"):
- Q04: "What specifically happened with @vortex_minis?" → If consequence was revenue loss (sponsor threatened to pull funding), agent must prioritize sponsor-content protection. If false-positive (sponsor wrongly flagged), agent must tune for high recall.
- Q07: "How often do volunteers disagree?" → If rare (<5%), agent can trust volunteer consensus. If common (>20%), agent needs to surface disagreement early.
- Q13: "How do you update your Google Sheet?" → If ad hoc, agent needs to replicate pattern-detection. If systematic, agent can codify rules.

---

## Quality Checks

### ✅ Completeness
- [x] Table of contents (8 sections)
- [x] Scenario context (platform, team, volumes)
- [x] Lived vs. documented process (evidence-based, artefact citations)
- [x] Jobs to be Done decomposition (5 JtDs with triggers, actors, decisions, outputs)
- [x] Cognitive Zones & Breakpoints (5 zones, control handoffs mapped)
- [x] Micro-task inventory (8-dimension scoring for 4 JtDs)
- [x] Assumptions register (27 assumptions, confidence levels, rationale, coach question mapping)
- [x] Key findings (8 findings, delegation suitability by stream)

### ✅ Conciseness
- Cognitive map: 15,200 words (comprehensive but structured with headings, tables, bullets)
- Discovery questions: 6,400 words (20 questions, each with rationale and assumption mapping)
- Total: 21,600 words (within scope for Gate 2 deliverable depth)

### ✅ Assumption Discipline
- 27 assumptions explicitly marked (A01-A27)
- Confidence levels assigned (high/medium/low)
- Rationale provided for each confidence level
- Coach question IDs mapped to assumptions (Q01-Q20)

### ✅ Artefact Grounding
- Artefact 4.1 cited: 2 times (grey-zone post, OP reaction)
- Artefact 4.2 cited: 6 times (Discord consensus, sub-forum norms, prior incidents)
- Artefact 4.3 cited: 8 times (Tom's Google Sheet, account patterns, escalation rules)
- Total artefact citations: 16 (demonstrates evidence-based analysis)

### ✅ Discovery Question Quality
- 20 questions (within max limit)
- 9 categories (workload, risk, norms, automation history, IP, volunteers, volume, tools, compliance)
- Each question includes:
  - Specific prompt (not generic)
  - "Why this matters" (design-changing rationale)
  - Assumption closure mapping
- Question-to-assumption table included

---

## Output Data Summary

### Cognitive Map Outputs

**Work Stream Volumes** (from brief):
| Stream | Daily Volume | Daily Effort | Handling Time |
|--------|--------------|--------------|---------------|
| Routine spam | 1,080 | 9 hrs | ~30 sec/case |
| Grey-zone review | 360 | 30 hrs | ~5 min/case |
| User appeals | 60 | 8 hrs | ~8 min/case |
| IP claims | 0.6 (avg) | Variable | ~30 min/case |
| **Total** | **~1,501/day** | **~47 hrs/day** | |

**Delegation Suitability** (from micro-task analysis):
| Stream | Suitability | Rationale |
|--------|-------------|-----------|
| Routine spam | **High** | Deterministic, low-risk, structured |
| Grey-zone review | **Low-Medium** | High cognitive load, judgment-dependent, undocumented norms, false-negative risk |
| User appeals | **Low-Medium** | Similar to grey-zone; policy consistency + user trust |
| IP claims | **Low (Human Only)** | Legal reasoning, PR risk, Tom-exclusive |

**Cognitive Zones** (5 zones identified):
1. Intent recognition & triage (low-medium load)
2. Context synthesis (high load — undocumented norms, Tom's sheet, Discord, prior incidents)
3. Judgment & decision (high load — false-negative risk dominates)
4. Action execution (low-medium load)
5. Documentation & learning (low-medium load)

**Breakpoints** (8 key handoffs):
- System → moderator (triage)
- Moderator → Discord (peer consultation)
- Moderator → Tom (sponsor/IP escalation)
- Tom → legal (contested IP claims)
- Moderator → no action (logged)
- Tom → user/claimant (IP communication)
- Decision → institutional memory (learning)
- Pattern → Tom's Google Sheet (account flagging)

**Assumptions** (27 total, confidence breakdown):
- High confidence: 14 (52%)
- Medium confidence: 9 (33%)
- Low confidence: 4 (15%)

### Discovery Questions Outputs

**20 questions in 9 categories**:
1. Tom's workload (Q01-Q03)
2. 2024 sponsor incident (Q04-Q05)
3. Sub-forum norms (Q06-Q08)
4. Automation history (Q09)
5. IP-claim workflow (Q10-Q11)
6. Volunteer dynamics (Q12-Q14)
7. Volume/growth (Q15-Q16)
8. Tool integration (Q17-Q18)
9. Compliance/risk (Q19-Q20)

**Assumption coverage**:
- Questions target 22 of 27 assumptions (81% coverage)
- 5 assumptions not directly targeted by questions (A01, A04, A08, A09, A27) — these are either calculable from brief data or secondary findings

---

## Iteration Reflections

### What Went Well
1. **Artefact-driven analysis**: Every claim about lived process grounded in artefact evidence
2. **Assumption discipline**: 27 assumptions explicitly marked with confidence levels
3. **Grey-zone bottleneck identification**: Clear quantification (30 hrs/47 total) and cognitive-load decomposition
4. **Discovery questions target design-changing info**: Not generic; each question has explicit "why this matters" rationale
5. **Lived vs. documented gap surfaced**: 14-page policy is baseline; effective moderation lives in undocumented layer (sub-forum norms, Tom's sheet, prior incidents, Discord consensus)

### Challenges
1. **Volume assumptions**: Brief states handling times (30 sec, 5 min, 8 min) but unclear if median/mean/mode — flagged as assumption A02
2. **Tom's workload unknown**: Critical gap (A21) — Tom is single point of failure, but his actual workload breakdown not stated
3. **Volunteer turnover unknown**: Critical gap (A18) — high turnover changes agent design (onboarding support vs. efficiency)
4. **2024 sponsor incident details missing**: Artefacts reference it 3 times ("THE 2024 SPONSOR — never get this wrong") but no details — Q04 targets this
5. **Compliance constraints unknown**: UK platform, user-generated content, potential Online Safety Act implications — A26, Q19

### Next Steps (If Continuing Iteration)
1. **Coach role-play Q01-Q05** (priority: Tom's workload, 2024 incident, escalation volume)
2. **Update assumptions** based on coach answers (revise confidence levels)
3. **Refine delegation suitability** if coach answers change volume/risk/norm assumptions
4. **Draft Delegation Suitability Matrix** (Week 2 Gate 2 deliverable #2) using updated cognitive map
5. **Draft Volume × Value Analysis** (Week 2 Gate 2 deliverable #3) with coach-validated volumes

---

## Files Created

1. `/Users/Alexandra_Rendon/gh/fde/t-week2/specs/scenario4-cognitive-map.md` (15,200 words)
2. `/Users/Alexandra_Rendon/gh/fde/t-week2/specs/scenario4-discovery-questions.md` (6,400 words)
3. `/Users/Alexandra_Rendon/gh/fde/t-week2/build-loop/iteration-01.md` (this file)

---

## Compliance with Instructions

### ✅ Used Guidance from Reference Files
- **atx-assessment.md Phase 2** followed:
  - Step 1: Mapped lived process (Artefacts 4.1, 4.2, 4.3)
  - Step 2: Decomposed into 5 JtDs
  - Step 3: Mapped 5 Cognitive Zones + Breakpoints
  - Step 4: Built micro-task inventory (8-dimension scoring)
- **atx-concepts.md** sections applied:
  - Cognitive work vs. processes (Section: Cognitive work vs. processes)
  - Lived work vs. documented work (undocumented norms layer)
  - Jobs to be Done as cognitive contracts (JtD structure)
  - Cognitive Zones and Breakpoints (control handoffs)

### ✅ Assumption Discipline
- Every inference marked as assumption (A01-A27)
- Confidence levels explicit (high/medium/low)
- Rationale provided
- Coach question mapping included

### ✅ Discovery Questions (Max 20)
- 20 questions created (within limit)
- Design-changing focus (not generic)
- Precise, lived-practice oriented
- Separate md file created

### ✅ Table of Contents
- Cognitive map: 8-section TOC included
- Discovery questions: Category-based structure (9 categories)

### ✅ Build Loop Folder
- Created: `/Users/Alexandra_Rendon/gh/fde/t-week2/build-loop/`
- Iteration-01.md documents creation process

### ✅ Output Data Included
- Work stream volumes table
- Delegation suitability table
- Cognitive zones list
- Breakpoints list
- Assumptions register (27 entries)
- Question-to-assumption mapping table

### ✅ Specs Folder
- Files created in `/Users/Alexandra_Rendon/gh/fde/t-week2/specs/`

---

## Status: Complete ✅
