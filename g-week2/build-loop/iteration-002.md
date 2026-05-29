# Build Loop - Iteration 002

## Date
2026-05-06

## Goal
Complete Phase 3: Delegation Qualification for all 7 JtDs identified in cognitive load map.

## Approach
1. Score each JtD on 7 delegation suitability dimensions (High/Medium/Low)
2. Assign delegation archetype based on suitability profile
3. Develop implementation recommendations and sequencing logic
4. Update assumptions register with 12 new assumptions (A016-A027)

---

## Deliverables Completed

### 1. Delegation Suitability Matrix (`specs/2-delegation-suitability-matrix.md`)
- ✅ Detailed analysis of all 7 JtDs across 7 dimensions
- ✅ Delegation archetype assignments with rationale:
  - **Fully Agentic**: 1 JtD (DE-3: Missed Window Investigation)
  - **Agent-led + Human Oversight**: 2 JtDs (DE-4: Unattended Address, DA-1: Additional Pickup)
  - **Human-led + Agent Support**: 3 JtDs (DA-2: Route Diversion, DE-1: Refused Delivery, DE-2: Damaged Consignment)
  - **Human Only**: 1 JtD (DA-3: Driver Swap)
- ✅ Summary matrix table with scores and automation potential
- ✅ Implementation sequencing recommendations (3 phases)
- ✅ Business case calculations by archetype
- ✅ Executive summary with key findings and constraints

### 2. Assumptions Register Update (`specs/assumptions.md`)
- ✅ Added 12 new assumptions (A016-A027) discovered during delegation analysis
- ✅ Categories: Volume distributions (A016, A020-A026), Process rules (A017, A019), Cost estimates (A018, A027)
- ✅ Updated confidence level summary: 27 total assumptions (6 High, 14 Medium, 7 Low)

---

## Key Findings from Phase 3

### Prime Candidate Identified: DE-3 (Missed Window Investigation)
- **Only Fully Agentic candidate** across all 7 JtDs
- **Highest volume**: 140 cases/day (estimated from 400 ETA inquiries × 35% requiring investigation)
- **Highest automation potential**: 85-95% cases handled autonomously
- **Lowest risk**: Wrong ETA is easily corrected, no financial/safety impact
- **Conservative business case**: £61K/year savings from this JtD alone
- **Recommendation**: Phase 1 pilot focus

### Near-Autonomous Candidates: DE-4 & DA-1
- **Agent-led + Human Oversight**: 70-85% autonomous with lightweight approval
- **Combined volume**: 81 cases/day
- **Combined savings**: £48K/year
- **Constraint**: DA-1 requires dispatch console API access [A004] or human execution workaround
- **Recommendation**: Phase 1 expansion after DE-3 proves successful

### Agent-Assisted Candidates: DA-2, DE-1, DE-2
- **Human-led + Agent Support**: 40-60% cognitive load reduction
- **Combined volume**: 117 cases/day
- **Combined savings**: £35-44K/year
- **Critical dependencies**:
  - Refused delivery decision rules formalization [A005]
  - Damage liability criteria codification [A017]
  - Route diversion decision rules [A019]
  - Customer priority system implementation [A009]
- **Recommendation**: Phase 2 after decision rules are formalized

### Human-Only Holdout: DA-3 (Driver Swap)
- **Low suitability**: 3+ dimensions at LOW (decision determinism, context complexity, risk/compliance)
- **Low volume**: 10-15 cases/day [A016]
- **High complexity**: Relationship-heavy, negotiation-dependent, regulatory compliance
- **Correct resource allocation**: Senior dispatcher expertise is appropriate tool
- **Agent role**: 10-20% administrative support only (data retrieval, logging)
- **Recommendation**: Not a priority for automation investment

### Cumulative Business Case (Phase 1: Tiers 1-2)
- **Volume**: 221 cases/day (DE-3 + DE-4 + DA-1)
- **Time saved**: 25 hours/day = 3.1 FTE equivalent
- **Annual labor cost saved**: £109K/year [A018]
- **Agent infrastructure cost**: £30-40K/year (estimated) [A027]
- **Net benefit Year 1**: £65-75K conservative, scaling to £144K if Phase 2 deployed

---

## Critical Constraints Identified

### API Access Blockers
1. **A004 - Dispatch Console API**: Required for DA-1, DA-2 autonomous execution
   - **Workaround**: Agent recommends, human executes manually in Citrix console
   - **Impact**: Limits DA-1 to Agent-led + Oversight instead of Fully Agentic
   - **Action**: Technical discovery on API availability; consider building API wrapper or alternative route management service

2. **A007 - Aurum Billing Lag**: 24-48h batch exports, no real-time API
   - **Impact**: DE-2 credit processing delayed, cannot validate billing state in real-time
   - **Workaround**: Agent queues credit requests, tracks to completion
   - **Action**: Negotiate with Aurum vendor for API access or implement real-time workflow outside Aurum with batch reconciliation

### Decision Rule Formalization Gaps
1. **A005 - Refused Delivery Disposition Logic**: Currently relies on dispatcher discretion
   - **Impact**: DE-1 limited to Human-led + Agent Support (recommendations only)
   - **Action**: Shadow Sandra/dispatchers on 20+ cases, codify decision tree, validate with COO Sarah

2. **A017 - Damage Liability Assessment Criteria**: No formal criteria, judgment-based
   - **Impact**: DE-2 limited to Agent Support, cannot determine liability autonomously
   - **Action**: Interview Sandra/supervisor, review 30-50 historical damage cases, formalize liability decision tree

3. **A019 - Route Diversion Decision Rules**: Implicit rules based on customer priority, delay tolerance
   - **Impact**: DA-2 limited to Agent Support
   - **Action**: Shadow coordinators on 20+ diversion cases, interview Sarah, codify rules with thresholds

### Knowledge Formalization Needs
1. **A009 - Customer Tier/Priority System**: Currently tacit (Hayes & Sons pattern visible in data)
   - **Impact**: All customer-facing JtDs have degraded recommendation quality
   - **Action**: Analyze customer master data, interview Sandra on account management, implement formal tier system in CRM

2. **A002 - Dispatcher Knowledge Concentration**: Senior dispatchers hold critical expertise
   - **Impact**: DA-3 unsuitable for delegation, risk if senior staff leave
   - **Action**: Record decision patterns from Sandra/seniors to build training dataset for agent (and for onboarding new staff)

---

## Implementation Sequencing Logic

### Phase 1 Pilot (Months 1-3): Prove Value with Lowest Risk
**Scope**: DE-3 only (Missed Window Investigation)
- **Why**: Fully Agentic, highest volume, lowest risk, clear success criteria
- **Build**: CRM integration, driver app GPS API, ETA estimator, SMS/email automation
- **Risk mitigation**: 2-week shadow mode (agent generates ETA, human validates before sending)
- **Success criteria**: 85%+ autonomous, <5% error rate, 90%+ customer satisfaction

### Phase 1 Expansion (Months 4-6): Scale to Near-Autonomous
**Scope**: Add DE-4 (Unattended Address) + DA-1 (Additional Pickup)
- **Why**: Agent-led + Oversight, combined volume 81 cases/day, lightweight human approval
- **Build**: Safe place authority rules, pickup feasibility calculator, approval dashboard
- **Dependency**: Validate dispatch console API [A004], implement human-in-loop workaround if unavailable
- **Success criteria**: 75%+ autonomous with one-click approval

### Phase 2 (Months 7-12): Agent-Assisted for Complex Judgment
**Scope**: Add DA-2 (Route Diversion) + DE-1 (Refused Delivery) + DE-2 (Damaged Consignment)
- **Why**: High cognitive load reduction (40-60%), high combined volume (117 cases/day)
- **Build**: NLP classification, decision tree implementations, image recognition (DE-2), recommendation UI
- **Critical path dependencies**: Formalize decision rules [A005, A017, A019], implement customer priority system [A009]
- **Success criteria**: 40-60% handling time reduction, 90%+ human acceptance of recommendations

### Phase 3 (Month 13+): Continuous Improvement
**Scope**: Elevate Agent Support to Agent-led where decision rules prove robust; expand to other work streams
- **Platform compounding**: Reuse CRM integration, NLP, recommendation engine across billing disputes, ETA inquiries, etc.

---

## Validation Priorities Before Phase 1 Kickoff

### Critical Path (Must Validate Before Build)
1. **A004**: Dispatch console API capabilities - technical discovery session with IT
2. **A003**: Driver app API read access - confirm GPS, delivery status, messaging endpoints
3. **A024**: Missed window investigation volume - analyze 2-week ETA inquiry logs to validate 35% investigation rate
4. **A018**: Labor cost validation - confirm £35K average salary with Sarah/HR

### High Priority (Validate During Pilot)
1. **A010**: ETA estimator requirements - analyze GPS data quality, historical route timing patterns
2. **A009**: Customer priority system - map existing tiers in customer master, interview Sandra
3. **A005**: Refused delivery decision patterns - begin shadowing Sandra on refused delivery cases

### Medium Priority (Validate During Phase 2 Planning)
1. **A017**: Damage liability assessment - collect historical damage cases for pattern analysis
2. **A019**: Route diversion rules - shadow dispatch coordinators on diversion cases
3. **A027**: Agent infrastructure cost - obtain Claude API pricing, SMS gateway quotes

---

## Archetype Distribution Insights

### Why Only One Fully Agentic?
- **DE-3** is diagnostic (data retrieval + calculation), not dispositional (judgment call)
- All other JtDs have judgment components (refusal reasoning, damage liability, driver negotiation)
- Agent excels at structured data lookup and rule-based reasoning, not complex human judgment
- **Key insight**: Highest ROI comes from automating high-volume, low-judgment tasks first

### Why No "Human-led + Automation Support"?
- This archetype is for RPA-style static rules (form-filling, data entry)
- None of our JtDs fit this pattern—all require non-deterministic reasoning (NLP, recommendation scoring, exception detection)
- Low-determinism tasks need agent reasoning (Agent Support), not just automation
- **Anti-pattern avoided**: Not building "RPA disguised as agents"

### Why Human Only for Driver Swaps?
- 3+ critical dimensions at LOW: decision determinism, context complexity, risk/compliance
- Relationship-dependent, negotiation-heavy, regulatory compliance (driver hours, safety)
- Low volume (10-15 cases/day) doesn't justify forcing automation
- **Correct resource allocation**: Senior expertise is the right tool for high-stakes, low-volume work

---

## Build Quality Notes

### Strengths
- Comprehensive 7-dimension scoring across all JtDs with detailed rationale
- Clear archetype assignments grounded in suitability profiles
- Implementation sequencing tied to risk, volume, and dependencies
- Business case calculations by archetype and phase
- 12 new assumptions explicitly tracked with confidence levels
- Anti-pattern awareness (no "RPA as agents")

### Areas for Refinement
- **Volume assumptions** (A016, A020-A026) have medium confidence—validate with actual data
- **Decision rule formalization** (A005, A017, A019) is critical path for Phase 2—start elicitation early
- **Image recognition** for DE-2 (damage assessment) may require 3-6 months model training
- **Customer priority system** (A009) appears across multiple JtDs—high-leverage formalization target

---

## Next Phase

**Phase 4: Candidate Prioritization**
- Create Volume × Value grid (Y-axis: volume, X-axis: non-deterministic decision effort)
- Feasibility scoring across 6 factors (data availability, system integration, compliance, context stability, org readiness, TCO)
- Wave sequencing with funding logic (Phase 1 ROI funds Phase 2 expansion)
- Final prioritized candidate shortlist with implementation roadmap

---

## Document Control
- **Created**: 2026-05-06
- **Phase**: Phase 3 Delegation Qualification
- **Related Documents**:
  - `specs/1-cognitive-load-map.md` - Input JtDs and micro-tasks
  - `specs/2-delegation-suitability-matrix.md` - Main deliverable
  - `specs/assumptions.md` - Updated with A016-A027
  - `build-loop/iteration-001.md` - Phase 2 (Cognitive Load Mapping)
