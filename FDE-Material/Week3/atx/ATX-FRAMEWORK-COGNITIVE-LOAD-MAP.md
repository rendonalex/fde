# ATX Framework: Cognitive Load Map<a id='0'></a>

1. [Meta-Frame](#1)
2. [Decision Criteria](#2)
3. [Phase 1 — Discovery](#3)
4. [Phase 2 — Cognitive Load Mapping](#4)
5. [Phase 3 — Delegation Qualification](#5)
6. [Phase 4 — Prioritization and Economics](#6)
7. [Phase 5 — Agent Design](#7)
8. [The Delegation Gradient](#8)

---

## [Meta-Frame](#0)<a id='1'></a>

This map applies ATX's own delegation archetypes and suitability dimensions to the ATX assessment process itself. Every activity in a client engagement — interviewing, scoring, modeling, designing — is itself a cognitive task. Some belong to humans; others can be safely delegated to agents. Getting this wrong in either direction costs you: under-delegating wastes FDE time on mechanical work; over-delegating loses tacit signal that only humans can surface.

The five archetypes used throughout this map:

| Archetype | Short label | When to use |
|-----------|-------------|-------------|
| Human Only | **HO** | Tacit knowledge, ethics, irreversibility, live trust-building |
| Human-led + Automation Support | **HA** | Deterministic sub-tasks can run in background; judgment stays human |
| Human-led + Agent Support | **HAS** | Agent provides synthesis, structure, drafts; human decides and validates |
| Agent-led + Human Oversight | **AHO** | Agent executes; human reviews output or approves edge cases |
| Fully Agentic | **FA** | All suitability dimensions met; human not needed in the loop |

---

## [Decision Criteria](#0)<a id='2'></a>

Before assigning any archetype, answer three questions derived from ATX suitability scoring:

**1. Is the input available without human presence?**
If the input is tacit (in someone's head, read from body language, elicited through relationship) → human must be present. If the input is structured or can be derived from documents, transcripts, or data → agent eligible.

**2. Is the decision deterministic given the inputs?**
If yes (pure calculation, template fill, rule application) → agent executes. If the decision requires judgment, contextual weighting, or reading organizational dynamics → human decides; agent supports.

**3. What is the cost and reversibility of a wrong output?**
Irreversible or high-stakes (stakeholder commitment, compliance sign-off, governance contract) → Human Only or Human-led. Reversible or low-stakes → Agent can lead with oversight.

---

## [Phase 1 — Discovery](#0)<a id='3'></a>

Discovery is the most human-intensive phase. Its inputs are locked inside people's heads, not in documents. Lived work — the pauses, judgment calls, workarounds — surfaces only through presence, rapport, and skilled questioning. Agents cannot run discovery interviews. What agents can do is prepare humans before the call and structure raw outputs immediately after.

| Activity | Archetype | Why | Agent provides |
|----------|-----------|-----|----------------|
| Conduct stakeholder interviews | **HO** | Tacit knowledge extraction. Trust is a prerequisite for honest answers about exception handling and workarounds. Evasion detection and contradiction probing require real-time adaptation and reading tone. | Nothing during interview. |
| Shadow workers in live work environment | **HO** | Physical presence reveals pause points, tool-switching, and informal coordination invisible in any transcript or SOP. No API for embodied observation. | Nothing during observation. |
| Walk through real cases with process owner | **HO** | Lived vs. documented gap only emerges under conversational pressure — "why did you skip that step?" — which requires trust and follow-up. | Post-session: structured case narrative from notes. |
| Detect evasion and contradiction | **HO** | Contradiction signals (SOP answer vs. actual behavior) require real-time pattern recognition across tone, word choice, and prior statements. | Post-call: flag contradictions in transcript analysis. |
| Pre-call domain research | **AHO** | Research from industry standards, regulations, and comparable processes is structured retrieval with no tacit component. Human validates framing fits the client context. | Domain brief: typical processes, regulations, 10 hypothesis questions calibrated to ATX dimensions. |
| Post-call transcript processing | **FA** | Summarizing a transcript into structured categories (pause points, judgment calls, exception signals, volume estimates) is deterministic given the transcript. Decision determinism: high. Exception rate: low. | Structured debrief: core processes, cognitive hotspots, delegation signals, follow-up questions. |
| Draft lived process narrative | **HAS** | Human validates the narrative against memory and lived experience — agent frequently misses the significance of what was said. Draft is fast; validation requires judgment. | First draft from structured debrief. |
| Compile Points of Pain inventory | **HAS** | Structuring raw interview output into a formatted inventory is mostly mechanical. Human validates that pain levels and volume estimates reflect what was actually said. | Formatted inventory table: process, volume, pain level, data/system context. |

---

## [Phase 2 — Cognitive Load Mapping](#0)<a id='4'></a>

Cognitive load mapping begins with human presence (the case walk-through) and transitions quickly to structured analysis where agents become productive. The key breakpoint is after step 1: once you have a real case on paper, the decomposition and scoring work is largely rule-bound and agent-eligible. The human stays in the loop to validate that the map reflects reality — not what the SOP says and not what the agent inferred from incomplete notes.

| Activity | Archetype | Why | Agent provides |
|----------|-----------|-----|----------------|
| Live case walk-through with SME | **HO** | Cognitive hotspots (where the worker pauses, checks, calls someone) are invisible in text. They only surface under real-time conversation with someone who does the work. | Nothing during session. |
| Identify cognitive hotspots in real-time | **HO** | Hotspot detection requires listening for what is not said — the hesitation, the "it depends," the skipped SOP step — while maintaining conversation flow. | Nothing during session. |
| Decompose process into Jobs to be Done | **HAS** | JtD boundaries require judgment: "is this one cognitive contract or two?" Agent drafts decomposition from notes; human validates each JtD is a real unit of delegation with a meaningful outcome. | Draft JtD list with trigger, actor, goal, key decisions, systems, output. |
| Score micro-tasks on 8 ATX dimensions | **AHO** | Scoring (Cognitive Load, Input Structure, Decision Determinism, Exception Frequency, Turn-Taking, Latency, Compliance, Tool Availability) is rule-based once inputs exist. Human reviews borderline H/M/L calls. | Scored micro-task table. Human reviews scores where multiple dimensions conflict. |
| Map Cognitive Zones and Breakpoints | **HAS** | Zone boundaries and breakpoints are judgment calls — where does "data retrieval" end and "diagnosis" begin? Agent drafts topology; human corrects based on what was actually observed. | Draft zone map with proposed breakpoints. |
| Build process topology diagram | **AHO** | Topology generation from scored micro-tasks is structured layout work. Human validates that the topology matches lived reality, not the agent's inference from notes. | Textual topology with zones, breakpoints, handoff labels. |
| Write Cognitive Load Map document | **FA** | Document generation from scored tables and validated topology is fully deterministic. All judgment was exercised in the scoring step. | Complete Cognitive Load Map table and narrative. |

---

## [Phase 3 — Delegation Qualification](#0)<a id='5'></a>

Delegation qualification is the judgment-intensive middle ground. The suitability scoring matrix looks mechanical — score seven dimensions, assign an archetype — but the hard cases require human judgment: a task scoring Low on compliance risk but High on exception frequency sits between Agent-led and Human Only, and which archetype you choose commits the organization to a governance model. The anti-pattern check (is this actually an RPA job?) requires domain experience, not just scoring.

| Activity | Archetype | Why | Agent provides |
|----------|-----------|-----|----------------|
| Score delegation suitability dimensions | **AHO** | Seven dimensions (Input Structure, Decision Determinism, Tool Coverage, Context Complexity, Exception Rate, Latency, Risk/Compliance) are explicit criteria. Agent scores based on Cognitive Load Map data. Human reviews borderline cases. | Suitability score per dimension per task. |
| Assign delegation archetype | **HAS** | Archetype assignment is a commitment. Clear cases (all high or all low) are agent-decidable. Mixed cases — where one low-suitability dimension on risk/compliance can veto four high-suitability dimensions — require human judgment about organizational tolerance and acceptable failure modes. | Proposed archetype with score summary and rationale; human confirms or overrides. |
| Anti-pattern check (RPA vs. agent decision) | **HAS** | Recognizing that a task could be solved with a script or deterministic rule — and that building an agent adds engineering overhead without agentic value — requires domain experience. This is a judgment call about what non-determinism actually exists. | Flag tasks scoring 1–2 on Non-Deterministic Effort; present rule-based alternative. |
| Risk/compliance boundary judgment | **HO** | For tasks at extreme compliance risk (regulated, irreversible, high-consequence), no scoring algorithm substitutes for human accountability. Who is liable if the agent is wrong? That question has no formula. | Compliance context research; relevant regulation summaries. |
| Build Delegation Suitability Matrix | **FA** | Matrix generation from confirmed archetype assignments is mechanical document work. | Formatted matrix: tasks × dimensions × archetype × rationale. |

---

## [Phase 4 — Prioritization and Economics](#0)<a id='6'></a>

This phase is the most agent-friendly in the entire ATX process. The inputs — volume estimates, cost data, suitability scores, wave criteria — are structured. The calculations are deterministic. The only human-essential work is validating assumptions (which came from interviews and carry uncertainty) and making the final sequencing call, which involves organizational politics and budget dynamics no agent can observe.

| Activity | Archetype | Why | Agent provides |
|----------|-----------|-----|----------------|
| Volume × Value grid placement | **FA** | Score multiplication and quadrant assignment are pure arithmetic. Decision determinism: maximum. Input structure: fully structured. | Volume × Value grid with quadrant labels and priority scores. |
| Feasibility scoring (6 factors) | **AHO** | Five factors (data availability, integration feasibility, compliance risk, context stability, TCO viability) can be scored from available data. Organizational readiness requires human judgment — agent cannot assess stakeholder politics or leadership buy-in. | Scored feasibility table; flag organizational readiness for human input. |
| Baseline cost model | **FA** | Time × rate = cost per case; cases/year × cost/case = annual baseline. Pure arithmetic from interview estimates. | Baseline cost table with formula and calculated figures. |
| Token economics model | **FA** | Token consumption per case × token price + tool call cost + infrastructure + HITL cost = agent cost per case. All arithmetic given model selection. | Full cost-per-case breakdown with formula. |
| ROI and payback period calculation | **FA** | Standard financial formulas: Annual saving / Build cost = payback. Year 1 ROI = (saving − build cost) / build cost. | ROI table: Year 1, 3-year, payback period. |
| Financial sensitivity analysis | **FA** | Scenario modeling (conservative/base/optimistic token price × HITL rate permutations) is deterministic scenario math. | Sensitivity table across three scenarios. |
| Validate cost assumptions from interviews | **HAS** | Volume and time estimates came from interviews and carry uncertainty. Human validates whether the numbers reflect reality; agent builds the sensitivity model that shows how much each assumption matters. | Sensitivity flags: which assumptions break the business case if wrong by ±30%. |
| Wave sequencing decision | **HAS** | Strategic sequencing involves organizational dynamics, budget cycles, executive sponsorship, and which use cases build reusable infrastructure for later waves. Agent recommends based on ROI and integration reuse scores; human commits the roadmap. | Draft wave sequence with integration reuse matrix and rationale. |
| Prioritized candidate shortlist | **AHO** | Ranking by agentic value score × feasibility score is mechanical. Human reviews the top candidates for organizational context the score cannot capture. | Ranked shortlist with feasibility annotations and recommended next steps. |

---

## [Phase 5 — Agent Design](#0)<a id='7'></a>

Agent mapping spans a wide delegation range within a single phase. Some artefacts — the Agent Purpose Document — are human-essential because they encode organizational commitment. Others — the System and Data Inventory, the Activity Catalog — are structured document generation from already-validated inputs. The Autonomy Matrix (the decision authority contract) requires human judgment about acceptable risk and organizational tolerance for agent errors.

| Activity | Archetype | Why | Agent provides |
|----------|-----------|-----|----------------|
| Define Job to be Done for agent | **HO** | The JtD is a commitment: it defines what the agent exists to produce. Getting it wrong frames every subsequent design decision incorrectly. Only the human who understands organizational context and stakeholder expectations can commit this definition. | Nothing — this must be human-authored. |
| Write Agent Purpose Document | **HAS** | Document structure and KPI framing follow templates. Human provides the JtD, objectives, and failure modes from organizational knowledge; agent structures the document and drafts KPI targets from the economics model. | Drafted Purpose Document from human inputs + economics data. |
| Build Agent Activity Catalog | **AHO** | Micro-task enumeration from validated JtD decomposition is structured catalog work. Agent assigns task types (Reasoning/Retrieval/Decision/Action/Generation) and proposes delegation levels. Human validates delegation levels — especially for Action and Decision tasks. | Activity Catalog with task types, delegation levels, data requirements, tools, risk levels. |
| Define Autonomy Matrix | **HAS** | The Autonomy Matrix is an operational governance contract. Thresholds (what value triggers HITL? what confidence level triggers escalation?) require human judgment about organizational risk tolerance. Agent drafts the matrix from delegation qualification outputs; human sets the actual thresholds. | Draft Autonomy Matrix with proposed thresholds; human fills in numeric boundaries. |
| System and Data Inventory | **AHO** | Mapping systems, data, access types, and integration gaps is structured inventory work from known information. Human validates gap/risk assessment — especially for legacy or politically sensitive systems. | Inventory table: system, data needed, access type, availability, gap/risk. |
| Context Engineering Design | **HAS** | Memory architecture (in-context, episodic, semantic, procedural) and retrieval strategy require architectural judgment about cost-accuracy trade-offs. Agent drafts based on ATX patterns; architect reviews and approves. | Memory architecture table, retrieval strategy description, prompt engineering principles applied. |
| Compounding Roadmap | **HAS** | Integration reuse matrix is mechanical — track which agent builds which integration and which reuses it. Wave ordering is strategic — that is human. Agent populates the matrix; human validates the ordering. | Integration reuse matrix; draft wave structure with assets built vs. reused per agent. |
| Governance and Autonomy contract sign-off | **HO** | This is an organizational commitment with compliance and liability implications. No agent can make this commitment. Sign-off requires human authority. | Governance documentation for human review. |

---

## [The Delegation Gradient](#0)<a id='8'></a>

The ATX process itself follows the same delegation gradient it prescribes for client work: the most human-intensive activities are at the front (where tacit knowledge lives), and the most agent-eligible activities are in the middle (structured scoring and economics). The end of the process oscillates — document generation is agent-friendly, but governance and commitment are permanently human.

```
Phase             Human-essential              Agent-eligible
─────────────────────────────────────────────────────────────
Discovery         ████████████████████         ████
  (90% human)     Interviews, shadowing,        Pre-call research,
                  contradiction detection       post-call synthesis

Cog. Mapping      ████████████                 ████████████
  (50/50)         Case walk-through,            Dimension scoring,
                  JtD boundary judgment         CLM document

Delegation        ████████                     ████████████████
  (35% human)     Archetype commits,           Suitability matrix,
                  risk/compliance calls        anti-pattern flagging

Economics         ████                         ████████████████████
  (15% human)     Assumption validation,        All calculations,
                  wave sequencing              sensitivity models

Agent Design      ████████                     ████████████████
  (40% human)     JtD definition,              Activity catalog,
                  autonomy thresholds,         system inventory,
                  governance sign-off          compounding roadmap
```

**Three rules derived from this map:**

1. **Never delegate discovery to an agent.** The lived process signal is the entire foundation. An agent-conducted "discovery" produces documented-process answers, which ATX explicitly treats as inferior inputs.

2. **Always delegate economics to an agent.** Manual calculation of token costs, ROI, and sensitivity tables is error-prone and adds no judgment value. An agent is faster and more accurate. Human time belongs in validating the assumptions, not running the formulas.

3. **The Autonomy Matrix is always human-authored.** Agents propose thresholds; humans commit them. The governance contract between an agent and an organization cannot be written by the agent being governed.
