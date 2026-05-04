# PA Chase Timing Agent - Prototype

**Wave 1 Implementation** for Westbridge Family Medicine  
**Based on**: `specs/scenario5-agent-mapping-pa-chase.md`

---

## Overview

This prototype implements the core reasoning engine for the PA Chase Timing & Denial Management Agent. It demonstrates:

- **Chase timing calculation** based on insurer-specific learned patterns
- **Escalation decision logic** implementing the 4-level autonomy matrix
- **Anomaly detection** for insurer SLA changes
- **Denial pattern matching** with resubmission workarounds
- **Dana correction learning** for pattern refinement

---

## What's Built

### Core Modules

1. **`src/models.py`** - Data models
   - `PriorAuthorization`: PA case representation
   - `ChaseRecommendation`: Agent output format
   - `InsurerPattern`: Learned SLA patterns (Humana=6d, UHC=7d, etc.)
   - `DenialPattern`: Denial workaround patterns (Wellpath colonoscopy, etc.)
   - Supporting enums and dataclasses

2. **`src/pattern_library.py`** - Pattern storage and retrieval
   - Seeded with Dana's insurer patterns from Artefact 5.1
   - 6 insurers: Humana, UHC, BCBS PPO, Medicare, Wellpath, Aetna
   - 1 denial pattern: Wellpath colonoscopy (attach prior visit note)
   - Pattern update methods (for learning phase)
   - Predictable vs. unpredictable insurer classification

3. **`src/chase_engine.py`** - Core reasoning engine
   - `generate_recommendation()`: Main entry point (implements decision tree)
   - Escalation trigger checks (Aetna, urgent cases, denials, unknown insurers)
   - Chase timing calculation (submission date + SLA - 1 day)
   - Anomaly detection (>2 day deviation from predicted approval)
   - Dana correction processing (reinforcement learning signal)

4. **`data/mock_pa_data.py`** - Mock PA generator
   - 8 sample PA cases covering all recommendation types
   - Based on Artefact 5.1 examples from Dana's Google Sheet

5. **`tests/test_agent.py`** - Test suite
   - Pattern library tests
   - Chase recommendation tests (all 8 sample PAs)
   - Anomaly detection tests
   - Dana correction learning tests
   - JSON output format tests

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PA Chase Timing Agent                     │
└─────────────────────────────────────────────────────────────┘

Input: PriorAuthorization (from athenahealth API)
   ↓
┌─────────────────────────────────────────────────────────────┐
│  ChaseEngine.generate_recommendation()                       │
│                                                              │
│  Step 1: Check Escalation Triggers                          │
│    → Unpredictable insurer (Aetna)?                         │
│    → Urgent (<3 days before procedure)?                     │
│    → Denied (needs resubmission)?                           │
│    → Unknown insurer (not in library)?                      │
│                                                              │
│  Step 2: Retrieve Insurer Pattern                           │
│    → PatternLibrary.get_pattern(insurer)                    │
│    → Returns: SLA days, confidence, variance, notes         │
│                                                              │
│  Step 3: Calculate Chase Timing                             │
│    → Chase date = submission + (SLA - 1) days               │
│    → Predicted approval = submission + SLA days             │
│    → Guardrail: Never chase before day 3                    │
│                                                              │
│  Step 4: Generate Recommendation                            │
│    → If current_date < chase_date: WAIT                     │
│    → If current_date >= chase_date: RECOMMEND_CHASE         │
│    → If escalation triggered: ESCALATE_TO_DANA / URGENT     │
└─────────────────────────────────────────────────────────────┘
   ↓
Output: ChaseRecommendation (JSON)
   {
     "action": "recommend_chase",
     "pa_id": "PA-2026-001",
     "recommended_chase_date": "2026-04-30",
     "rationale": "Humana pattern: approves in 6 days...",
     "confidence": "high"
   }
```

---

## Running the Tests

```bash
cd /Users/Alexandra_Rendon/gh/fde/week2/agent-pa-chase
python tests/test_agent.py
```

**Expected Output:**
- Test 1: Pattern library retrieval (6 insurers loaded)
- Test 2: Chase recommendations for 8 sample PAs
  - PA-2026-001 (Humana): RECOMMEND_CHASE (6 days elapsed)
  - PA-2026-002 (UHC): WAIT (needs 2 more days)
  - PA-2026-003 (Wellpath): ESCALATE_TO_DANA (denied, match workaround)
  - PA-2026-004 (Aetna): ESCALATE_TO_DANA (unpredictable insurer)
  - PA-2026-005 (BCBS): RECOMMEND_CHASE (3 days elapsed)
  - PA-2026-006 (Medicare): WAIT (needs 1 more day)
  - PA-2026-007 (Humana): URGENT_FLAG (procedure in 2 days)
  - PA-2026-008 (Cigna): ESCALATE_TO_DANA (unknown insurer)
- Test 3: Anomaly detection (Humana approved 4 days late → flag)
- Test 4: Dana correction logging
- Test 5: JSON output format (matches agent mapping spec)

---

## What's NOT Built (Next Steps)

### 1. External Integrations (Requires Clarification)
- [ ] **athenahealth API client** (need OAuth credentials)
- [ ] **Google Sheets API** (need Dana's sheet access)
- [ ] **Claude API integration** (for LLM-enhanced reasoning; optional)

### 2. Persistence Layer (Requires Decision)
- [ ] **Pattern library storage** (JSON file, SQLite, PostgreSQL?)
- [ ] **Episodic memory** (Dana's corrections) → Vector DB (ChromaDB, Pinecone?)
- [ ] **Activity logs** (structured logging to database or log file?)

### 3. HITL Approval Interface (Requires Scope Decision)
- [ ] **Dana's dashboard** (web app: Flask/FastAPI? CLI? Or manual testing?)
- [ ] Approval workflow (approve/defer/override buttons)
- [ ] Feedback capture (Dana's corrections logged to episodic memory)
- [ ] Weekly summary reports

### 4. Production Features (Future Waves)
- [ ] Real-time athenahealth polling (batch daily queries)
- [ ] Email/SMS notifications to Dana for escalations
- [ ] Pattern update approval workflow (Dana reviews proposed changes)
- [ ] Multi-user support (front-desk team access in Wave 2+)

---

## Key Design Decisions

1. **In-memory pattern library** (prototype)
   - Production: Migrate to database with versioning
   - Rollback capability if pattern update degrades accuracy

2. **Deterministic logic** (no LLM for core reasoning)
   - Chase date calculation is pure math (submission + SLA - 1)
   - Escalation triggers are rule-based (explicit if/then logic)
   - LLM optional for: denial reason interpretation, natural language rationale generation
   - **Rationale**: Predictable, testable, no token cost for core logic

3. **Learning phase = HITL for all recommendations**
   - `ChaseEngine.learning_phase = True` (default)
   - When `False`: Agent autonomously handles predictable insurers, escalates only Aetna + denials + anomalies
   - **Transition criteria**: Dana's corrections <10 per insurer, accuracy >90%

4. **Anomaly detection threshold = 2 days**
   - Flags insurer SLA changes (e.g., Humana suddenly approves in 5 days instead of 6)
   - Requires Dana validation before pattern update applied
   - Prevents agent from auto-updating patterns without human review

5. **Guardrail: Never chase before day 3**
   - Even if insurer pattern suggests earlier chase (e.g., BCBS 3-day SLA)
   - Insurers don't process PAs instantly; chasing day 1-2 is premature
   - Overridable in urgent cases (procedure <3 days away)

---

## Example Recommendation

**Input PA:**
- Patient: John Smith
- Insurer: Humana
- Procedure: Colonoscopy (scheduled 2026-05-03)
- Submitted: 2026-04-23
- Status: Pending
- Current date: 2026-04-29 (6 days after submission)

**Agent Recommendation:**
```json
{
  "action": "recommend_chase",
  "pa_id": "PA-2026-001",
  "patient_name": "John Smith",
  "insurer": "Humana",
  "procedure": "Colonoscopy",
  "submission_date": "2026-04-23",
  "procedure_date": "2026-05-03",
  "recommended_chase_date": "2026-04-29",
  "rationale": "Chase recommended today. Humana pattern: approves in 6 days (±0.2 days, 50 cases). Predicted approval: 2026-04-29.",
  "confidence": "high",
  "predicted_approval_date": "2026-04-29"
}
```

**Dana's Action:**
- Reviews recommendation in HITL dashboard
- Approves → Dana places call to Humana
- If approved on 2026-04-29 → Agent accuracy confirmed (6 days as predicted)
- If approved on 2026-05-01 → Agent detects anomaly (2 days late), flags for Dana review

---

## Success Metrics (Trackable with Current Build)

- ✅ **Pattern accuracy**: Compare predicted approval date vs. actual (RMSE per insurer)
- ✅ **Escalation rate**: % PAs escalated to Dana (target: 20% in production)
- ✅ **Anomaly detection rate**: % approvals deviating >2 days from predicted
- ✅ **Denial pattern match rate**: % denials matched to known workarounds (target: 70%)
- ⏳ **Chase timing accuracy**: 90% within ±1 day of optimal (requires production data)
- ⏳ **Dana's time savings**: 1.5-2 hours/day → 15 min/day (requires production deployment)
- ⏳ **Visit abort prevention**: 0 aborts from PA timing misses (requires production deployment)

---

## Status: Core Logic Complete ✅

**Built**: 5 Python modules, 8 sample PAs, comprehensive test suite  
**Runnable**: Yes (mock data, no external dependencies)  
**Ready for**: Integration planning, UI mockup, production database design  
**Blockers**: None for core logic; need clarifications for integrations (see "What's NOT Built")

---

**Questions? See agent mapping:** `specs/scenario5-agent-mapping-pa-chase.md`
