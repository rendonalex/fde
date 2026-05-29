# Build Loop - Iteration 003

## Date
2026-05-06

## Goal
Complete Phase 4: Candidate Prioritization using Volume × Value scoring, TCO assessment, feasibility analysis, and strategic sequencing.

## Approach
1. Apply suitability gating to validate agent-suitable candidates
2. Score each JtD on Volume (1-5) and Non-Determinism (1-5) to calculate Agentic Value Score
3. Create Volume × Value quadrant diagram
4. Perform detailed TCO assessment (baseline costs, agent costs, ROI calculations)
5. Build feasibility scoring matrix across 6 factors
6. Validate strategic sequencing with self-financing wave structure
7. Generate prioritized candidate shortlist with implementation logic

---

## Deliverables Completed

### 1. Volume × Value Analysis (`specs/3-volume-x-value-analysis.md`)
- ✅ **Step 1: Suitability Gating**: All 7 JtDs evaluated, 6 pass for agent consideration, 1 conditional fail (DA-3: Human Only)
- ✅ **Step 2: Volume × Value Scoring**: 
  - Volume scores (1-5) based on cases/day frequency
  - Non-Determinism scores (1-5) based on reasoning complexity
  - Agentic Value Scores (1-25 scale) calculated
  - Volume × Value quadrant diagram created in Mermaid format
- ✅ **Step 3: Total Cost of Ownership**: 
  - Baseline human costs for all 7 JtDs (£308K total annual)
  - Agent cost model (token costs, API calls, HITL, infrastructure)
  - Detailed ROI calculations by JtD with payback periods
- ✅ **Step 4: Feasibility Scoring Matrix**: 6 factors scored 1-5 for each JtD
- ✅ **Step 5: Strategic Sequencing**: 3-wave structure with funding logic and decision points
- ✅ **Prioritized Candidate Shortlist**: Ranked by feasibility and ROI with wave assignments
- ✅ **Implementation Sequencing Logic**: Self-financing model, decision points, platform compounding thesis

### 2. Assumptions Register Update (`specs/assumptions.md`)
- ✅ Added 14 new assumptions (A028-A041) discovered during prioritization
- ✅ Categories: Platform compounding, TCO estimates, sequencing decisions, strategic pivots
- ✅ Updated confidence level summary: 41 total assumptions (9 High, 20 Medium, 6 Low)

---

## Key Findings from Phase 4

### Clear Wave 1 Winners

**Rank #1: DE-3 (Missed Window Investigation)**
- Volume: 5 (140 cases/day), Non-Det: 2, Value Score: 10
- **Annual Saving: £53K, Payback: 7 months, Year 1 ROI: 77%**
- Fully Agentic (85-95% autonomous), lowest risk
- Feasibility: 4.8/5 (highest across all dimensions)
- **Strategic value**: Builds CRM API, GPS API, ETA engine (all reused in Waves 2-3)

**Rank #2: DE-4 (Unattended Address)**
- Volume: 4 (45 cases/day), Non-Det: 2, Value Score: 8
- **Annual Saving: £16K, Payback: 11 months, Year 1 ROI: 9%**
- Agent-led + Oversight (75-85% autonomous)
- Feasibility: 4.3/5
- **Strategic value**: Safe place rules, re-delivery scheduling

**Rank #3: DA-1 (Additional Pickup)** - *Conditional*
- Volume: 4 (36 cases/day), Non-Det: 3, Value Score: 12
- **Annual Saving: £14K, Payback: 18 months, Year 1 ROI: -32%**
- Agent-led + Oversight (70-80% autonomous with HITL execution workaround)
- Feasibility: 3.5/5
- **Constraint**: Dispatch console API [A004] limits to 70% automation
- **Decision point**: Include if 9-month blended payback acceptable, exclude if 7-month critical [A033, A037]

**Wave 1 Combined** (all 3):
- Annual saving: £83K
- Build cost: £65K
- Blended payback: **9 months**
- Year 1 net: £18K

**Wave 1 Alternative** (DE-3 + DE-4 only):
- Annual saving: £69K
- Build cost: £45K
- Blended payback: **7 months** (faster)
- Year 1 net: £24K

### Major Strategic Pivot: Wave 2 Becomes Preparation Phase

**Original Plan**: Deploy DE-1, DE-2, DA-2 in Wave 2  
**Issue Identified**: All three have **negative net economics** (agent costs exceed savings)
- DE-1: -£5K/year (HITL 50%)
- DE-2: -£3K/year (HITL 60%)
- DA-2: -£2K/year (HITL 60%)

**Root Cause**: High HITL rates (50-60%) driven by undocumented decision rules [A005, A017, A019]

**Revised Strategy**: **Wave 2 = Preparation Phase** (Months 7-18)
- Formalize decision rules [A005, A017, A019]
- Implement customer priority system [A009]
- Train image recognition model (6-12 months for DE-2)
- Resolve dispatch console API [A004]
- **Investment**: £40-50K (funded by Wave 1 Year 2 savings £83K)

**Wave 3 Conditional Deploy** (Months 19-24):
- If preparation reduces HITL to 30-40% → marginal positive economics (£7K/year combined)
- If HITL remains high → **pivot to other work streams** (ETA inquiries full automation, billing disputes) with better ROI [A040, A041]

### Platform Compounding Validated

**Wave 1 Platform Assets** (built once, reused forever):
- CRM API integration, GPS/driver app integration, ETA calculation engine, notification automation, oversight dashboard
- **Marginal cost reduction**: Wave 2-3 agents cost 40-50% less due to asset reuse [A028]

**3-Year ROI Scenarios**:
1. **All Waves Deploy**: £67.5K net benefit, 35% ROI (modest) [A029]
2. **Pivot to Other Work Streams**: £344K net benefit, 237% ROI (significantly higher) [A040]

**Strategic Recommendation**: Deploy Wave 1, assess Wave 2 prep at Month 12, **pivot to high-ROI work streams if Wave 3 economics remain marginal** [A041]

### Not Prioritized: DA-3 (Driver Swap)

- Volume: 2 (12 cases/day), Non-Det: 5, Value Score: 10
- Annual saving: £2-3K (insufficient to justify build)
- **Human Only archetype**: 3+ LOW scores (decision determinism, context complexity, risk/compliance)
- Feasibility: 2.2/5 (poorest across all JtDs)
- **Correct resource allocation**: Senior dispatcher expertise is appropriate for high-stakes, low-volume, relationship-heavy work

---

## Volume × Value Quadrant Insights

**Positioning by Quadrant**:

**Top-Right (High Volume, High Reasoning) - PRIMARY AGENTIC TARGETS**:
- DE-1 (Refused Delivery): Value 16
- DE-2 (Damaged Consignment): Value 20
- **Issue**: High reasoning means high HITL rates → negative economics in current state
- **Resolution**: Wave 2 prep to formalize rules, reduce HITL

**Top-Left (High Volume, Low Reasoning) - NORMALLY RULES/RPA**:
- DE-3 (Missed Window): Value 10
- DE-4 (Unattended Address): Value 8
- **Why agents, not RPA?**: Require NLP (input parsing), dynamic ETA calculation, exception handling
- **Result**: Highest ROI despite "low reasoning" scores

**Mid-Right (Medium Volume, High Reasoning)**:
- DA-2 (Route Diversion): Value 12
- DA-1 (Additional Pickup): Value 12
- Solid candidates if inheriting Wave 1 assets

**Bottom-Right (Low Volume, High Reasoning) - SELECT USE CASES**:
- DA-3 (Driver Swap): Value 10
- **Correct decision**: Human Only despite high reasoning, due to low volume + high risk

**Key Learning**: **Agentic Value Score alone is insufficient for prioritization**. Must combine with:
- Delegation archetype (Fully Agentic > Agent-led > Agent Support)
- Absolute volume (drives absolute ROI)
- Risk profile (enables deployment speed)

---

## TCO Assessment Key Findings

### Baseline Human Costs
- Total across 7 JtDs: £308K/year (350 cases/day)
- Excluding DA-3 (not automating): £283K/year (338 cases/day)

### Agent Cost Drivers
1. **Token costs**: £0.025-£0.098 per case (varies by complexity)
   - DE-3: £0.045/case (caching reduces to £0.025 [A030])
   - DE-2: £0.098/case (vision tokens for damage photos)
2. **API call costs**: £0.15-£0.30 per case (3-6 API calls)
3. **HITL costs**: £0.32-£2.28 per case (10-60% HITL rates)
   - Fully Agentic (DE-3): 10% HITL = £0.32/case
   - Agent Support (DE-2): 60% HITL = £2.28/case
4. **Infrastructure**: £25-35K/year (supervision, monitoring, platform)

**Cost Insight**: **HITL rate is dominant cost factor** for Agent Support archetypes. Reducing HITL from 60% → 40% turns negative ROI → positive ROI [A035].

### ROI Rankings (Wave 1 Candidates Only)
1. DE-3: 77% Year 1 ROI, 431% 3-year ROI (champion)
2. DE-4: 9% Year 1 ROI, 225% 3-year ROI (solid)
3. DA-1: -32% Year 1 ROI, 104% 3-year ROI (breakeven Month 18, acceptable if blended with DE-3/DE-4)

---

## Feasibility Scoring Key Findings

**Feasibility Rankings (Average Score /5)**:
1. DE-3: 4.8/5 (excellent across all dimensions)
2. DE-4: 4.3/5 (strong, minor supervision setup)
3. DA-1: 3.5/5 (moderate, API constraint manageable)
4. DE-1: 3.3/5 (moderate, rule formalization needed)
5. DA-2: 3.0/5 (moderate, multiple dependencies)
6. DE-2: 2.8/5 (challenging, image recognition + criteria)
7. DA-3: 2.2/5 (poor, not prioritized)

**Feasibility Constraints by Factor**:
- **System Integration (LOW scores)**: DA-1, DA-2 (dispatch console API [A004])
- **Context Stability (LOW scores)**: DE-1, DA-2, DE-2 (decision rules need formalization [A005, A017, A019])
- **TCO Viability (LOW scores)**: DE-1, DE-2, DA-2, DA-3 (negative economics in current state)

**Constraint Resolution**: Wave 2 preparation phase addresses context stability and TCO viability for Wave 3 candidates.

---

## Strategic Sequencing Validation

### Self-Financing Model Validated ✓
- **Wave 1 saves £83K/year** (or £69K without DA-1)
- **Wave 1 build costs £65K** (or £45K without DA-1)
- **Year 1 net cash: £18K** (or £24K without DA-1) → positive cash flow
- **Year 2 full savings: £83K** → funds Wave 2 prep (£40-50K) with £33-43K surplus [A038]

### Decision Points Defined
1. **Month 3**: DE-3 pilot Go/No-Go (85%+ autonomous? <5% error?)
2. **Month 5**: Include DA-1? (API blocker resolved? Prefer 7-month vs. 9-month payback?) [A033, A037]
3. **Month 12**: Wave 3 Go/No-Go (rules formalized? Economics validated? Or pivot to other work streams?) [A040]
4. **Month 18**: Wave 3 vs. Pivot (positive ROI confirmed? Or expand platform to ETA/billing?)

### Platform Compounding Thesis Confirmed
- Wave 1 assets (CRM, GPS, ETA, NLP) reduce Wave 2-3 marginal cost by 40-50% [A028]
- Platform value maximized by reusing across **high-ROI work streams**, not completing all original JtDs [A041]
- Alternative pivot (ETA inquiries 400/day, billing disputes 60/day) may deliver 237% 3-year ROI vs. 35% if all original JtDs deployed [A040]

---

## Prioritized Candidate Shortlist

### Tier 1: Wave 1 Deploy (Months 1-6)
1. **DE-3: Missed Window Investigation** - Fully Agentic, £53K/year, 7-month payback, 4.8/5 feasibility
2. **DE-4: Unattended Address** - Agent-led + Oversight, £16K/year, 11-month payback, 4.3/5 feasibility
3. **DA-1: Additional Pickup** (Conditional) - Agent-led + Oversight, £14K/year, 18-month payback, 3.5/5 feasibility

**Wave 1 Recommendation**: Deploy DE-3 (pilot) + DE-4 (expansion). Include DA-1 if 9-month blended payback acceptable; exclude if 7-month critical [A033].

### Tier 2: Wave 2 Preparation (Months 7-18)
**No deployments**. Focus on decision rule formalization [A005, A017, A019], customer priority system [A009], dispatch console API resolution [A004], image recognition training, Wave 1 performance monitoring.

**Investment**: £40-50K (funded by Wave 1 Year 2 savings)

### Tier 3: Wave 3 Deploy (Months 19-24, Conditional)
4. **DE-1: Refused Delivery** - Human-led + Agent Support, £4K/year (post-prep), 3.3/5 feasibility
5. **DE-2: Damaged Consignment** - Human-led + Agent Support, £1K/year (post-prep), 2.8/5 feasibility
6. **DA-2: Route Diversion** - Human-led + Agent Support, £2K/year (post-prep), 3.0/5 feasibility

**Wave 3 Recommendation**: **Conditional proceed** only if Wave 2 prep validates positive economics. **Alternative**: Pivot to ETA inquiries / billing disputes with better ROI [A040, A041].

### Not Prioritized
7. **DA-3: Driver Swap** - Human Only, £2-3K/year, 2.2/5 feasibility, not economically viable

---

## Implementation Sequencing Logic

### Funding Flow (Self-Financing)
- **Wave 1 Year 1**: £83K savings - £65K build = **£18K net** (or £24K without DA-1)
- **Wave 1 Year 2**: £83K full-year savings (or £69K without DA-1)
- **Wave 2 Prep**: £40-50K investment funded from Year 2 savings, leaving £33-43K surplus [A038]
- **Wave 3** (if deployed): £7K/year marginal savings, but strategic value in cognitive load reduction [A039]

### Critical Path Dependencies
**Wave 1 → Wave 2 Prep**:
- Wave 1 must achieve target ROI to fund Wave 2 prep
- CRM + GPS integrations built in Wave 1 are prerequisites for Wave 2-3

**Wave 2 Prep → Wave 3**:
- Decision rules formalized [A005, A017, A019] → reduces HITL rates 50-60% → 30-40%
- HITL reduction → negative economics → marginal positive economics [A035]
- Without Wave 2 prep, Wave 3 is not viable [A036]

**Wave 3 vs. Pivot Decision**:
- If Wave 3 economics remain marginal (£7K/year) → pivot to other work streams (ETA 400/day, billing 60/day) for 237% 3-year ROI [A040]
- Platform reusability principle: maximize ROI by deploying to highest-value work streams [A041]

---

## Build Quality Notes

### Strengths
- Comprehensive 5-step scoring methodology applied (suitability gating, volume × value, TCO, feasibility, sequencing)
- Detailed TCO analysis with per-case cost breakdown and ROI calculations
- Major strategic insight: Wave 2 pivot from deploy → preparation phase due to negative economics
- Clear decision points with go/no-go criteria at each wave
- Platform compounding thesis validated with alternative scenario analysis (237% vs. 35% ROI)
- 14 new assumptions explicitly tracked (A028-A041)

### Critical Findings
1. **Agentic Value Score ≠ ROI Priority**: DE-3 scores only 10 (tied 5th) but is #1 due to Fully Agentic archetype + highest volume
2. **HITL rate is dominant cost factor**: 50-60% HITL makes agent costs exceed savings for "Human-led + Agent Support" archetypes [A034]
3. **Wave 2 prep is critical**: Without decision rule formalization, Wave 3 candidates have negative ROI [A036]
4. **Platform pivot strategy**: Better to reuse Wave 1 assets on high-ROI work streams than to force low-ROI JtDs [A041]

### Areas for Refinement / Validation
- **Token cost assumptions** (A030): Validate caching opportunity in DE-3 pilot; measure actual token usage
- **HITL rate reduction** (A035): Mock test with formalized rules to validate 50% → 30% reduction is achievable
- **Alternative work stream economics** (A040): Preliminary analysis on ETA inquiries (400/day) and billing disputes (60/day) ROI
- **Dispatch console API** (A004): Technical discovery on API access or workaround viability for DA-1, DA-2
- **DA-1 inclusion decision** (A033): Stakeholder preference on 7-month vs. 9-month payback

---

## Next Phase

**Agent Mapping (for Wave 1 Candidates)**:
- Detailed agent design for DE-3, DE-4, (DA-1 if included)
- Tool definitions, prompt templates, workflow diagrams
- HITL escalation logic, error handling, audit trails
- Testing and validation strategy
- Build sprint planning

---

## Document Control
- **Created**: 2026-05-06
- **Phase**: Phase 4 Candidate Prioritization
- **Related Documents**:
  - `specs/1-cognitive-load-map.md` - Source JtDs
  - `specs/2-delegation-suitability-matrix.md` - Archetype assignments
  - `specs/3-volume-x-value-analysis.md` - Main deliverable
  - `specs/assumptions.md` - Updated with A028-A041
  - `build-loop/iteration-001.md` - Phase 2 (Cognitive Load Mapping)
  - `build-loop/iteration-002.md` - Phase 3 (Delegation Qualification)
