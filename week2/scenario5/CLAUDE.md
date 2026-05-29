# CLAUDE.md

This file provides guidance to Claude Code when working with enterprise agent design projects using the ATX Assessment Framework.

---

## Methodology Overview

**Framework**: ATX Assessment Framework - A systematic methodology for converting real business operations into prioritized agentic opportunity maps.

**Core Principle**: Start from **lived work**, not documented processes. Shadow people, review transcripts, walk through real cases—not SOPs.

**Phases**:
1. **Discovery** - Understand points of pain (volume, time, cognitive nature, data/systems, risk)
2. **Cognitive Load Mapping** - Decompose work into Jobs to be Done, cognitive zones, micro-tasks
3. **Delegation Qualification** - Determine how far each task can be safely delegated to agents
4. **Candidate Prioritization** - Volume × Value scoring, TCO analysis, wave sequencing
5. **Agent Mapping** - Design fully specified agent: purpose, scope, activity catalog, autonomy, context, governance

---

## Project Structure Pattern

When working with ATX assessment projects, expect this structure:

```
/project-root/
├── specs/                           # Requirements & design (source of truth)
│   ├── [scenario]-cognitive-map.md              # Phase 2: JtDs, cognitive zones
│   ├── [scenario]-delegation-qualification.md   # Phase 3: Suitability scoring
│   ├── [scenario]-phase4-prioritization.md      # Phase 4: Wave sequencing, TCO
│   ├── [scenario]-agent-mapping-[wave].md       # Agent specifications (per wave)
│   └── cognitive-topology.mermaid.md            # Visual diagrams
│
├── agent-[name]/                    # Wave implementations
│   ├── src/                         # Core logic (deterministic preferred)
│   ├── data/                        # Mock data (realistic, validated)
│   ├── tests/                       # Test suite
│   └── README.md                    # Architecture & next steps
│
├── build-loop/                      # Iteration tracking
│   ├── BUILD-LOOP.md                # Index of all iterations
│   └── iteration-*.md               # Detailed iteration logs
│
└── input-docs/                      # ATX methodology reference
    ├── atx-assessment.md            # Phase 2-4 process
    ├── atx-agent-mapping.md         # 6 deliverables framework
    └── [scenario].md                # Original business case
```

---

## Working Philosophy

### Source of Truth Hierarchy
1. **Specs directory** - All requirements, design decisions, validated assumptions
2. **Build-loop directory** - Iteration history, design rationale, emergent findings
3. **Agent implementation READMEs** - Current status, next steps, architecture
4. **ATX methodology docs** (`input-docs/`) - Framework reference

**If specs are ambiguous**: Ask user, don't invent requirements.

### Assumptions Are Critical
- All assumptions must be tagged with `[A#]` notation and catalogued
- Track confidence levels: VERY HIGH, HIGH, MEDIUM, LOW, UNVALIDATED
- Cross-reference assumptions throughout specs
- Update confidence after coach role-play validation
- Document which assumptions are "design-changing" (affect architecture/wave sequencing)

### Iteration Tracking
**After significant work**, update `build-loop/BUILD-LOOP.md`:
1. Add row to iteration summary table
2. Create `iteration-XXX.md` documenting:
   - What was built
   - Key decisions made
   - What emerged (surprises, pivots, validated/invalidated assumptions)
   - Artifacts generated
3. Update "Last Updated" timestamp

**Format**:
```markdown
| [XXX](iteration-XXX.md) | YYYY-MM-DD | [Focus] | [Artifacts] | ✅ Complete |
```

---

## Phase 2: Cognitive Load Mapping

### Key Deliverables
1. **Jobs to be Done (JtDs)** - Cognitive contracts between actor and outcome
   - Trigger, actor, goal, key decisions, key systems, expected output
   - Flag primary nature: decision-making, execution, synthesis, communication, exception-handling

2. **Cognitive Zones** - Groups of micro-tasks (e.g., intent understanding, data retrieval, diagnosis, decision, action, documentation)
   - Mark **breakpoints** where control shifts: human → system, system → human, rule → judgment
   - Identify **cognitive hotspots** (high-leverage automation opportunities)

3. **Micro-task Inventory** - Scored on 7 dimensions:
   - Cognitive Load (H/M/L)
   - Input Structure (structured/semi-structured/unstructured)
   - Decision Determinism (predictable vs. judgment-dependent)
   - Exception Frequency
   - Turn-Taking Degree
   - Latency Constraint (real-time vs. batch)
   - Compliance/Risk Sensitivity

4. **Lived Process Narrative** - 1-page description contrasting documented SOPs vs. lived practice
   - Critical gaps between "how it should work" and "how it actually works"

5. **Assumption Register** - Catalogue all assumptions with:
   - `[A#]` ID tag
   - Statement
   - Confidence level
   - Design impact (which decisions depend on this assumption)
   - Validation plan

6. **Design-Changing Questions** - Specific questions that target assumptions or unknowns
   - Prioritized by tier (Tier 1: must answer to proceed, Tier 2: refine design, Tier 3: operational context)

---

## Phase 3: Delegation Qualification

### Key Deliverables
1. **Suitability Matrix** - Score each JtD on 7 dimensions:
   - Pattern Recognizability
   - Input Structuredness
   - Decision Determinism
   - Tool/API Access
   - Failure Consequence
   - Exception Frequency
   - Turn-Taking Degree

2. **Delegation Archetypes** - Classify each JtD:
   - **Fully Agentic** - Agent operates autonomously with minimal oversight
   - **Agent-led (learning → production)** - Initial HITL, transition to autonomous
   - **Agent-led (perpetual oversight)** - Agent acts, human monitors/overrides
   - **Human-led (agent-supported)** - Agent assists, human decides

3. **Anti-Pattern Check** - Validate agents are justified (not solvable with static rules/RPA)

4. **Initial Wave Sequencing** - Group JtDs into implementation waves based on:
   - Technical feasibility
   - Stakeholder priority
   - Dependency chain (which builds shared assets for later waves)

---

## Phase 4: Candidate Prioritization

### Key Deliverables
1. **Volume × Value Scoring** - Quantify business impact
   - Volume (1-5): annual frequency × time per case
   - Value (1-5): cost of delay + strategic importance
   - Combined score (1-25)

2. **TCO Analysis** - Three-year economic model per JtD:
   - **Costs**: Development (months × $150K/month), Claude API, tool costs, HITL
   - **Savings**: Displaced labor hours × $75/hr (or role-specific rate)
   - **ROI**: (3-year savings - costs) / costs × 100%

3. **Feasibility Matrix** - Technical readiness (1-5):
   - API availability
   - Data quality
   - Pattern clarity
   - Stakeholder alignment
   - Compliance readiness

4. **Strategic Sequencing** - Finalized wave roadmap:
   - Consider: Quick wins vs. strategic investment
   - Stakeholder priorities (may override pure ROI)
   - Compounding asset reuse (later waves cheaper if early waves build shared components)

5. **Use Case Scoring Templates** - Reusable scoring rubrics for future projects

---

## Phase 5: Agent Mapping (Per Wave)

### The 6 Deliverables Framework
Complete one per agent (or per wave if agents are grouped):

**1. Agent Purpose Document**
```
Agent Name: [descriptive name]
Job to be Done: [cognitive contract - what outcome does this agent produce?]
Business context: [department, process, customer journey step]

Primary objectives: [2-3 measurable outcomes]
KPIs: [Accuracy, Coverage, Throughput, Cost per case, HITL rate]
Failure modes: [What does bad output look like? Consequence? Recovery path?]
Delegation archetype: [archetype + rationale]
Escalation triggers: [Condition → escalate to [role]]
```

**2. Agent Activity Catalog** - Enumerate every micro-task:
| Task | Type | Delegation level | Data required | Tool required | Risk level |
|------|------|-----------------|---------------|---------------|------------|

Task types: Reasoning, Retrieval, Decision, Action, Generation

**3. Autonomy Matrix (Decision Authority Matrix)**
```
AGENT DECIDES ALONE (no HITL required):
  - [list of decisions/actions]

AGENT ACTS, HUMAN NOTIFIED AFTER:
  - [list of decisions/actions]

AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:
  - [list of decisions/actions]

HUMAN TAKES OVER (agent supports):
  - [list of triggers]
```

**4. System and Data Inventory** - Catalogue all systems:
| System | Purpose | Access type | Data/API gaps | Risk level | Reusability |
|--------|---------|-------------|---------------|------------|-------------|

**5. Context Engineering Design**
- **Memory architecture**: What the agent remembers (session, long-term, pattern library, corrections)
- **Retrieval strategy**: When to fetch data (triggers, frequency, scope)
- **Prompt engineering principles**: How to frame instructions for consistency/safety

**6. Compounding Roadmap** - Show how later waves reuse assets:
| Wave | Integration | Reuses from prior waves | Marginal cost reduction |
|------|-------------|------------------------|-------------------------|

Identify **shared assets** built in each wave (e.g., API clients, HITL UI patterns, logging frameworks)

---

## Agent Design Philosophy

### Prefer Deterministic Core Logic
- **When possible**, use deterministic algorithms for core decisions (zero token cost, fully testable, predictable)
- **Use LLMs for**: Ambiguity resolution, unstructured input interpretation, generating human-readable explanations
- **Example**: Chase timing = math (`submission_date + SLA - 1 days`); denial reason interpretation = LLM

### Escalation-First Architecture
- **Check escalation triggers BEFORE attempting automated decision**
- **Escalate when**:
  - Unknown/unpredictable patterns (don't guess)
  - Urgent cases requiring immediate human judgment
  - Anomalies (deviation from learned patterns)
  - High-consequence decisions (defined in autonomy matrix)

### Learning Phase Design
- **Initial**: Human-in-the-loop for all recommendations (3-6 months)
- **Production**: Agent handles predictable cases autonomously, escalates 15-25%
- **Capture corrections**: Log human overrides for pattern reinforcement

---

## Integration Points

### Common Systems in Enterprise Agent Projects
- **EHR/Practice Management** (e.g., athenahealth, Epic) - OAuth 2.0, rate limits, batch query strategy
- **Historical Data Extraction** (e.g., Google Sheets, Excel) - One-time ingestion, pattern extraction
- **External APIs** (e.g., insurance verification APIs) - Error handling, retry logic, circuit breaker
- **HITL Approval UI** - Display pending recommendations, approve/defer/override, feedback capture
- **Activity Logging** - Audit trail, compliance, pattern learning

**When implementing integrations**: Refer to agent mapping Section 4 (System Inventory) for:
- Authentication flows
- Rate limits and batch strategies
- Error handling requirements
- Shared asset reuse opportunities

---

## Testing Philosophy

### Mock Data Must Be Realistic
- Base on validated examples (coach role-play, historical data samples)
- Cover all decision paths (happy path, escalation triggers, edge cases, anomalies)
- **Don't invent**:
  - Business rules not in agent mapping
  - Patterns not validated in specs
  - Edge cases not documented

### What to Test
- **All escalation triggers** (defined in agent purpose document)
- **Decision logic edge cases** (boundary conditions, thresholds)
- **Anomaly detection** (deviation from learned patterns)
- **Pattern update logic** (if agent learns from corrections)
- **Output format** (JSON schema, required fields)

### Test Coverage Expectations
- Unit tests: All core logic functions
- Integration tests: Mock API responses, realistic data flows
- End-to-end tests: Full recommendation generation from sample cases

---

## Coach Role-Play Validation

**Purpose**: Validate assumptions by role-playing as the process owner (e.g., Dana, the office manager)

**Process**:
1. Take all Design-Changing Questions from Phase 2
2. Answer AS the process owner (first-person perspective)
3. Provide specific, concrete answers (not generic)
4. Update Assumption Register with new confidence levels
5. Document major findings that change design decisions

**Findings to Capture**:
- Validated assumptions (upgrade confidence: LOW → MEDIUM → HIGH → VERY HIGH)
- Invalidated assumptions (requires design pivot)
- New patterns/rules discovered
- Stakeholder priority insights (may override economic ranking)

**After coach validation**: Update ALL specs with revised assumptions and cross-check wave sequencing

---

## Wave Sequencing Strategy

### Compounding Approach
- **Each wave reuses prior integrations**, reducing marginal cost
- **Build shared assets early** (API clients, HITL UI patterns, logging)
- **Later waves leverage**: Established patterns, proven architectures, user trust

### Sequencing Factors
1. **Stakeholder priority** (may override pure ROI)
2. **Quick wins** (build momentum, validate methodology)
3. **Strategic investment** (solves highest-pain problem, even if negative short-term ROI)
4. **Technical dependencies** (some waves can't start until others complete)
5. **Learning curve** (initial waves are learning phase; later waves benefit from corrections)

### Typical Timeline
- **Wave 1**: Months 1-8 (includes learning phase, HITL transition)
- **Wave 2**: Months 5-9 (overlaps with Wave 1, reuses integrations)
- **Wave 3**: Months 13-17 (platform mature, marginal cost lower)
- **Wave 4**: Months 19-24 (multi-agent workflows, optimizations)

---

## Commands

### Run Tests (Typical Pattern)
```bash
cd agent-[name]
python3 tests/test_agent.py
```

### Test Single Component (Python REPL)
```python
import sys
sys.path.append('agent-[name]')
from src import [ComponentName]

# Instantiate and test
component = ComponentName()
result = component.method(test_input)
print(result)
```

---

## Critical Constraints

### Validated Assumptions Are Sacred
- **Do not change without user approval**:
  - Escalation logic (defined in autonomy matrix)
  - Business rules (validated through coach role-play)
  - Calculation formulas (if mathematically validated)
  - Thresholds (if empirically derived)

### Guardrails Are Non-Negotiable
- Defined in agent purpose document (Section: Escalation Triggers)
- Defined in autonomy matrix (Section: Human Takes Over)
- **Example guardrails**:
  - Never take action on high-consequence decisions without human approval
  - Always escalate unpredictable patterns (don't guess)
  - Anomaly detection must trigger review (don't auto-update learned patterns)

---

## Common Patterns

### Adding New Business Rules
1. Document in agent mapping (Activity Catalog or Autonomy Matrix)
2. Add test case covering new rule
3. Update pattern library or decision tree
4. Log in `build-loop/BUILD-LOOP.md` (Key Decisions section)

### Adding New Escalation Trigger
1. Update agent purpose document (Escalation Triggers section)
2. Update `ChaseEngine._check_escalation_triggers()` (or equivalent)
3. Add test case
4. Document rationale in iteration log

### Modifying Core Logic
1. Verify change aligns with agent mapping (Activity Catalog, Autonomy Matrix)
2. Update all affected tests
3. Document in iteration log (What Changed, Why, Impact)

---

## Quick Reference

### File Reading Priority (When Starting Work)
1. `specs/[scenario]-agent-mapping-[wave].md` - Agent requirements (read first)
2. `build-loop/BUILD-LOOP.md` - Project history, decisions, open questions
3. `agent-[name]/README.md` - Implementation status, architecture
4. `specs/[scenario]-cognitive-map.md` - Full problem context, assumptions
5. `input-docs/atx-*.md` - Methodology reference (if unclear on process)

### Decision Traceability
- **Major decisions** → `build-loop/BUILD-LOOP.md` (Key Decisions Made section)
- **Iteration details** → `build-loop/iteration-XXX.md` (What Emerged section)
- **Design rationale** → Agent mapping (Rationale fields throughout)
- **Assumption validation** → Coach role-play answers + assumptions update doc

---

## Anti-Patterns to Avoid

❌ **Inventing business rules** not in specs
❌ **Assuming patterns** not validated through coach role-play
❌ **Skipping assumption tagging** (all assumptions must have `[A#]` IDs)
❌ **Over-engineering** (prefer deterministic logic over LLMs when possible)
❌ **Insufficient escalation triggers** (when in doubt, escalate)
❌ **Ignoring lived process narrative** (SOPs ≠ reality)
❌ **Building before mapping** (complete Phase 5 agent mapping before implementation)

---

**Last Updated**: 2026-05-04

**Project Context**: This CLAUDE.md applies to all ATX Assessment Framework projects. For scenario-specific details, refer to the specs directory in your working folder.
