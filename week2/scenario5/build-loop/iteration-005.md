# Iteration 005: Agent Mapping — PA Chase Timing Agent (Wave 1)

**Date**: 2026-04-29  
**Focus**: Complete ATX Agent Mapping deliverables for Wave 1 (PA Chase Timing & Denial Management Agent)  
**Status**: ✅ Complete

---

## What Was Built

### Primary Artifact
**File**: `specs/scenario5-agent-mapping-pa-chase.md`

**Content**: Complete agent mapping specification following atx-agent-mapping.md methodology, including all 6 required deliverables:

1. **Agent Purpose Document**
   - Agent Name: PA Chase Timing & Denial Management Agent
   - Job to be Done: Ensure PA approvals arrive before scheduled procedures by determining optimal chase timing based on insurer-specific patterns
   - Business Context: Clinical Operations, 25 PAs/day, Dana's 11-year institutional knowledge capture
   - Primary Objectives: Zero visit aborts, systematize institutional knowledge, proactive chase timing, reduce Dana's overhead
   - KPIs: 6 metrics defined (accuracy 90%, coverage 80%, throughput 50+ PAs/day, cost $0.31/case, HITL 20%, 100% PA approval on time)
   - Failure Modes: 6 scenarios identified (chase too early/late, wrong pattern, denial misinterpreted, SLA changed, redundant chase)
   - Delegation Archetype: Agent-led + HITL (learning phase, months 1-6) → Fully Agentic (production, month 7+)
   - Escalation Triggers: 6 conditions specified (Aetna, denials, anomalies, urgent cases, new insurers, API errors)

2. **Agent Activity Catalog**
   - 20 micro-tasks enumerated
   - Each task specified: Type (Reasoning/Retrieval/Decision/Action/Generation), Delegation Level, Data Required, Tool Required, Risk Level, Notes
   - Examples: Ingest Google Sheet, poll athenahealth, calculate chase date, recommend chase, detect approval, match denial patterns, flag urgent cases, update pattern library, generate weekly summary

3. **Autonomy Matrix (Decision Authority Matrix)**
   - 4 authority levels defined:
     - **Agent Decides Alone**: Data retrieval, monitoring, pattern learning, production chase recommendations (predictable insurers)
     - **Agent Acts, Human Notified After**: Learning phase chase recommendations, risk flags
     - **Agent Proposes, Human Approves Before Action**: Learning phase timing, denial resubmission, pattern library updates
     - **Human Takes Over**: Unpredictable insurers (Aetna), high-stakes/urgent cases, new insurers, system failures, clinical judgment required
   - Explicit examples provided for each level

4. **System and Data Inventory**
   - 5 systems catalogued:
     1. **athenahealth EHR**: PA data (read/write), REST API, gaps/risks identified, shared with Wave 2-3
     2. **Dana's Google Sheet**: Historical PA patterns (read, one-time ingest), Google Sheets API, not shared
     3. **Insurer Portals**: Real-time PA status (manual, no APIs), fragmented, workaround via athenahealth updates
     4. **Agent Pattern Library**: Learned SLAs and denial patterns (read/write), internal DB, potential future sharing
     5. **Agent Activity Log**: Audit trail (write), append-only, shared across all agents
   - Integration notes: athenahealth OAuth 2.0, rate limits, batch queries, shared Wave 2 reuse
   - Reusability flagged for each system

5. **Context Engineering Design**
   - **Memory Architecture** (4 types):
     - In-context: Current PA case details (per session)
     - Episodic: Dana's corrections during learning phase (vector DB, 6 months)
     - Semantic: Insurer-specific patterns (structured DB, versioned, long-term)
     - Procedural: Agent instructions, escalation rules, guardrails (system prompt, static)
   - **Retrieval Strategy**: 4 trigger types specified (new PA, chase date reached, denial detected, Dana correction)
   - **Retrieval Targets**: Pattern library (top-1 exact match), episodic corrections (top-5 semantic), denial patterns (top-3 semantic)
   - **Quality Evaluation**: Pattern accuracy (RMSE per insurer), denial match rate (target 70%), correction learning rate (target <10/insurer)
   - **Cost Management**: In-memory cache, batch daily queries, vector search only during learning phase
   - **7 Prompt Engineering Principles**: Role first, explicit scope, few-shot examples, guardrails, structured output (JSON), chain of thought, token discipline

6. **Compounding Roadmap**
   - **Wave 1** (Months 1-8): PA Chase Timing — builds 4 shared assets:
     1. athenahealth API Client (OAuth, error handling, retry logic) → reused Wave 2-3
     2. Agent Activity Logging Framework → reused Wave 2-4
     3. HITL Approval UI Pattern → reused Wave 2-4
     4. Pattern Learning Pipeline (concept) → reused Wave 2
   - **Wave 2** (Months 5-9): Insurance Re-Verification — reuses 4 Wave 1 assets, builds Availity API client
   - **Wave 3** (Months 13-17): Medication Reconciliation — reuses all Wave 1-2 platform assets, builds DoseSpot integration
   - **Wave 4** (Month 18+, deferred): Visit Reason Triage — reuses all platform assets, adds clinical NLP
   - **Integration Reuse Matrix**: 5 shared assets × 4 waves = shows compounding effect
   - **Compounding Effect Quantified**: Wave 1 = 2 months build, Wave 2-3 save 3-4 weeks each by reusing shared assets

---

## Key Decisions

### 1. Learning Phase Design (Months 1-6)
- **Decision**: Agent operates in supervised learning mode where Dana approves/corrects every chase recommendation
- **Rationale**: Dana's 11-year institutional knowledge (A2, A4, A7) cannot be fully extracted from Google Sheet alone; requires active teaching phase
- **Implementation**: 
  - Agent ingests Google Sheet (historical patterns)
  - Agent recommends chase timing based on submission date + insurer + learned pattern
  - Dana reviews every recommendation in HITL UI (approve/defer/override)
  - Agent logs corrections to episodic memory, updates semantic patterns when corrections are consistent (3+ in same direction)
- **Success Criteria**: Agent achieves <10 corrections per insurer, 90% accuracy within ±1 day of optimal timing
- **Timeline**: 3-6 months (agent learns 15+ insurer patterns from Dana's feedback)

### 2. Production Transition Criteria
- **Decision**: Agent transitions to Fully Agentic for predictable insurers only; continues HITL for unpredictable insurers (Aetna)
- **Rationale**: Q5 validated that Aetna has no stable pattern ("sometimes fast, sometimes slow"); forcing autonomous operation would increase failure rate
- **Implementation**:
  - **Autonomous**: Humana, UHC, BCBS, Medicare, Wellpath (stable patterns, 80% of volume)
  - **Escalate to Dana**: Aetna (unpredictable, ~20% of volume)
  - Dana spot-checks 20% of autonomous cases (~5 PAs/day = 15 min/day)
- **Success Criteria**: 0 visit aborts in production phase, Dana's time reduced from 1.5-2 hours/day to 15 min/day

### 3. Escalation Strategy for Denials
- **Decision**: Agent matches denials to historical patterns and suggests resubmission workarounds, but Dana always approves before resubmission
- **Rationale**: Denial resolution requires clinical judgment (e.g., "medical necessity not demonstrated" requires physician input); agent cannot make this decision alone
- **Implementation**:
  - Agent detects PA status=denied
  - Agent retrieves denial reason from athenahealth
  - Agent queries pattern library: "Wellpath colonoscopy denial" → match "attach prior visit note"
  - Agent proposes: "Suggest resubmission with [Document X] based on [Insurer] pattern [Y]"
  - Dana reviews: validates clinical documentation available, approves/modifies, executes resubmission
  - Agent logs outcome for future pattern refinement (reinforcement learning)
- **Target**: 70% denial match rate (remaining 30% are novel denials requiring Dana's judgment)

### 4. Shared Asset Prioritization
- **Decision**: Wave 1 build focuses on creating robust, reusable platform components (athenahealth client, logging, HITL UI), not just agent-specific logic
- **Rationale**: Compounding strategy — every shared asset reduces marginal cost of Wave 2-4 agents
- **Quantified Benefit**: 
  - Wave 1 build time: 2 months (no shared assets exist yet)
  - Wave 2 build time: 2 months (saves ~3 weeks by reusing athenahealth client, HITL UI, logging)
  - Wave 3 build time: 2 months (saves ~4 weeks by reusing athenahealth + HITL + logging)
  - Total time saved: 7 weeks across Wave 2-3 (1.75 months)
- **Trade-off**: Wave 1 build includes extra engineering effort to make components reusable (e.g., generic athenahealth API wrapper, not PA-specific code)

### 5. Anomaly Detection as Pattern Update Signal
- **Decision**: Agent automatically detects when insurer behavior deviates >2 days from learned pattern and flags to Dana for validation
- **Rationale**: Insurers occasionally change SLA policies (A2 validated: UHC changed 18 months ago); agent must adapt to remain accurate
- **Implementation**:
  - Agent compares predicted approval date vs. actual approval date
  - If deviation >2 days → flag to Dana: "Humana approved in 5 days (predicted 6); possible SLA change"
  - Dana validates: "Yes, Humana changed policy last month" OR "No, this was exception (holiday delay)"
  - If validated, agent proposes pattern update: "Change Humana SLA from 6 days to 5 days"
  - Dana approves → agent applies to future recommendations
- **Benefit**: Agent patterns stay current without manual Dana updates to Google Sheet; self-correcting system

### 6. Integration with Wave 2 Timing
- **Decision**: Wave 2 (Insurance Re-Verification) can start Month 5, overlapping with Wave 1 learning phase (Months 3-8)
- **Rationale**: Wave 2 does not depend on Wave 1 completion; athenahealth API client can be built in parallel and shared retroactively
- **Implementation**:
  - Month 5: Wave 2 build starts (athenahealth + Availity integration)
  - Month 6-7: Wave 1 still in learning phase; Wave 2 continues independently
  - Month 8: Wave 1 enters production; Wave 2 enters validation
  - Month 9: Both agents in production
- **Benefit**: Accelerates overall timeline (Waves 1-2 complete in 9 months vs. 12 months sequential)

---

## What Emerged

### 1. Google Sheet as One-Time Ingest, Not Live Sync
- **Finding**: Dana's Google Sheet is updated ad-hoc (A7: "living document"); not suitable for real-time agent queries
- **Implication**: Agent ingests historical snapshot during build (past 2-3 years of PA data), extracts patterns, then relies on Dana's corrections during learning phase for future pattern updates
- **Design Change**: Agent does NOT continuously sync with Google Sheet; episodic memory (Dana's corrections) becomes primary training signal after initial ingest
- **Trade-off**: Agent won't automatically pick up Dana's manual sheet updates; but learning phase captures Dana's knowledge more accurately than sheet parsing alone

### 2. Insurer Portals Are Irrelevant (Deferred)
- **Finding**: Most insurer portals lack APIs; web-only, inconsistent UX, would require brittle web scraping
- **Implication**: Agent relies on athenahealth PA status field (manually updated by Dana/front-desk after checking portals)
- **Design Decision**: No insurer portal integration in Wave 1; defer to future enhancement if specific insurers provide partner APIs
- **Trade-off**: Agent doesn't reduce Dana's manual portal checking (she still checks, updates athenahealth); but agent automates timing calculation and escalation logic

### 3. Denial Resolution Requires Clinical Context
- **Finding**: Many denial reasons require physician input (e.g., "medical necessity not demonstrated" → need additional clinical justification)
- **Implication**: Agent cannot fully automate denial resolution; must escalate to Dana, who coordinates with physician
- **Design Decision**: Agent proposes resubmission workarounds based on historical patterns, but Dana always approves before action
- **Boundary**: Agent can match denial patterns (Wellpath colonoscopy → prior visit note), but cannot assess clinical documentation adequacy or compose clinical justifications

### 4. Aetna as Permanent Escalation Case
- **Finding**: Q5 validated Aetna has no stable timing pattern ("sometimes fast, sometimes slow"); agent cannot learn reliable SLA
- **Implication**: Agent will never achieve Fully Agentic status for Aetna PAs (20% of volume); perpetual HITL required
- **Design Decision**: Agent explicitly escalates all Aetna cases to Dana with note: "No stable pattern available; recommend manual timing decision"
- **Success Redefined**: Production coverage = 80% (predictable insurers only), not 100%; Dana's time reduced but not eliminated

### 5. Pattern Learning Pipeline as Reusable Concept
- **Finding**: Wave 1's approach (ingest historical data → extract patterns → learn from corrections → update patterns) applies to Wave 2 (insurance re-verification rules)
- **Implication**: Pattern learning pipeline is a reusable platform component, not just PA-specific
- **Compounding Opportunity**: Wave 2 can reuse conceptual framework (reinforcement learning from Dana's corrections) even though domain differs (re-verification rules vs. PA timing)
- **Wave 2 Application**: Agent learns Dana's re-verification sub-rules (Medicaid every 3mo, Medicare Advantage in Q4, new insurance at next visit) through corrections during validation phase

### 6. HITL UI Pattern as Unified Cross-Agent Experience
- **Finding**: Dana will interact with multiple agents (PA Chase Wave 1, Insurance Wave 2, Med Recon Wave 3); each needs approval workflow
- **Implication**: HITL approval UI should be unified (consistent UX, single dashboard), not per-agent custom UI
- **Design Decision**: Wave 1 builds generic HITL UI pattern:
  - Pending recommendations list (filterable by agent, date, patient)
  - Approve/defer/override actions
  - Feedback capture (corrections logged for all agents)
  - Approval audit trail (who approved what, when)
- **Compounding Benefit**: Wave 2-4 agents integrate into same UI; Dana learns once, uses everywhere; reduces training overhead for future waves

---

## Artifacts Generated

### Primary Deliverable
- **`specs/scenario5-agent-mapping-pa-chase.md`** (11,500 words)
  - Section 1: Agent Purpose Document (2,800 words)
  - Section 2: Agent Activity Catalog (1,800 words)
  - Section 3: Autonomy Matrix (1,500 words)
  - Section 4: System and Data Inventory (1,200 words)
  - Section 5: Context Engineering Design (2,400 words)
  - Section 6: Compounding Roadmap (1,800 words)

### Supporting Updates
- **`build-loop/BUILD-LOOP.md`** (updated)
  - Added Iteration 005 to summary table
  - Updated "Completed Work" section with agent mapping deliverables
  - Updated "Ready for Implementation" section with Wave 1 next steps
  - Added "Iteration 005" key decisions section
- **`build-loop/iteration-005.md`** (this file)
  - Documents iteration process, decisions, emergent findings

---

## Open Questions (None)

All design-changing questions were answered in Iteration 003 (coach role-play validation). Agent mapping leverages validated assumptions (A2, A4, A7, A14 all VERY HIGH confidence).

---

## Next Steps

### Immediate (Ready for Development Team)
1. ✅ **Agent mapping complete** — Document serves as input to development; no further scoping required
2. ⏳ **Obtain Dana's full historical Google Sheet** (past 2-3 years of PA data, not just Artefact 5.1 sample)
3. ⏳ **Provision athenahealth API keys** (OAuth 2.0 credentials; practice-level access; Dana to request from athenahealth support)
4. ⏳ **Technical validation**: Test athenahealth REST API (PA submission/status endpoints, rate limits, auth flow)
5. ⏳ **Design HITL approval UI mockup** (for Dana's review and feedback before build)

### Wave 1 Build Phase (Months 1-2)
1. Google Sheet ingestion pipeline (parse historical data, extract insurer patterns)
2. Pattern extraction algorithm (group by insurer, calculate median approval time, identify denial patterns)
3. athenahealth API client (OAuth 2.0, rate limiting, error handling, retry logic)
4. Agent core logic (calculate chase date, compare to current date, generate recommendations)
5. Pattern library database (structured storage: insurer → SLA + confidence + last updated)
6. Activity logging framework (structured logs, append-only, audit trail)
7. HITL approval UI (Dana's dashboard, approve/defer/override, feedback capture)

### Wave 1 Learning Phase (Months 3-8)
1. Deploy agent to Dana's workflow (daily PA chase recommendations)
2. Dana reviews 100% of recommendations (approve/correct)
3. Agent logs corrections to episodic memory
4. Agent updates semantic patterns when corrections are consistent (3+ in same direction)
5. Weekly accuracy review (predicted vs. actual approval dates per insurer)
6. Monthly pattern library audits (Dana validates current SLAs, flags insurer policy changes)

### Wave 1 Production Transition (Month 9+)
1. Agent operates autonomously for predictable insurers (Humana, UHC, BCBS, Medicare, Wellpath)
2. Agent escalates Aetna + denials + anomalies to Dana
3. Dana spot-checks 20% of autonomous cases (5 PAs/day = 15 min/day)
4. Continuous anomaly detection (flag SLA changes, pattern drift)
5. Quarterly pattern library reviews (Dana validates agent remains accurate)

### Wave 2 Preparation (Month 5+)
1. Begin Wave 2 build (Insurance Re-Verification) — overlaps with Wave 1 learning phase
2. Reuse athenahealth API client from Wave 1
3. Reuse HITL approval UI pattern from Wave 1
4. Reuse activity logging framework from Wave 1

---

## Success Metrics (Tracked Post-Implementation)

| Metric | Baseline (Current) | Target (Production) | Measurement Cadence |
|--------|-------------------|---------------------|---------------------|
| Visit aborts from PA timing misses | 1-3 per quarter | 0 per quarter | Monthly |
| Dana's daily PA chase time | 1.5-2 hours/day | 15 min/day (spot-checking) | Weekly |
| PA chase timing accuracy | Unknown (Dana's tacit timing) | 90% within ±1 day of optimal | Per PA (calculated post-approval) |
| Agent autonomy rate | 0% (Dana handles all) | 80% (predictable insurers only) | Monthly |
| Agent cost per case | $3.30 (Dana's fully loaded time) | $0.31 (token + tool + HITL) | Monthly |
| Insurer patterns learned | 0 systematized (locked in Dana's head) | 15+ patterns documented | End of learning phase (Month 8) |
| Dana's career goal progress | Institutional knowledge locked in her head | Replicable system ready for regional rollout | End of Wave 1 (Month 8) |

---

## Status: ✅ Complete

**Date Completed**: 2026-04-29  
**Implementation-Ready**: Yes — Full agent mapping specification delivered per atx-agent-mapping.md requirements  
**Blockers**: None — All design-changing questions answered in Iteration 003  
**Next Iteration**: Wave 1 Build begins (obtain Google Sheet, provision athenahealth API keys, start development)

---

**End of Iteration 005**
