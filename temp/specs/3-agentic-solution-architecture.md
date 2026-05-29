# Phase 3 — Delegation Qualification & Agentic Solution Architecture
## Apex Distribution Customer Operations

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Input Documents and Scope](#2-input-documents-and-scope)
3. [Phase 3 Methodology](#3-phase-3-methodology)
4. [Suitability Scoring Framework](#4-suitability-scoring-framework)
5. [Delegation Suitability Matrix](#5-delegation-suitability-matrix)
   - 5.1 [Delivery Exceptions](#51-delivery-exceptions)
   - 5.2 [Dispatch Adjustments](#52-dispatch-adjustments)
6. [Archetype Assignments: Rationale and Trade-off Analysis](#6-archetype-assignments-rationale-and-trade-off-analysis)
   - 6.1 [Agent-led + Human Oversight](#61-agent-led--human-oversight)
   - 6.2 [Human-led + Agent Support](#62-human-led--agent-support)
   - 6.3 [Human Only](#63-human-only)
7. [Proposed Agentic Solution Architecture](#7-proposed-agentic-solution-architecture)
   - 7.1 [Wave 1: Foundation Agents](#71-wave-1-foundation-agents-months-14)
   - 7.2 [Wave 2: Expanding Coverage](#72-wave-2-expanding-coverage-months-59)
   - 7.3 [Wave 3: Multi-Agent Orchestration](#73-wave-3-multi-agent-orchestration-months-1018)
8. [Assumptions Register (Phase 3 Additions)](#8-assumptions-register-phase-3-additions)
9. [Open Questions and Next Steps](#9-open-questions-and-next-steps)

---

## 1. Executive Summary

This document delivers Phase 3 — Delegation Qualification for Apex Distribution's Customer Operations agentic transformation. It applies the ATX suitability framework to the seven Jobs to be Done identified in the Phase 2 Cognitive Load Map, scores each across seven dimensions, assigns a delegation archetype, and proposes an implementation architecture in three waves.

**Key findings:**

- **Two JtDs are strong Wave 1 candidates for Agent-led + Human Oversight**: DE-3 (Missed Delivery Window) and DE-4 (Unattended Address Exception). Combined with the ETA Inquiry work stream (~400/day), this represents the highest-volume, best-API-coverage opportunity in the entire function.

- **Three JtDs are assigned Human-led + Agent Support**: DE-1 (Refused Delivery), DA-1 (Additional Pickup), DA-2 (Route Diversion). Each has a clear upgrade path: DE-1 is blocked by uncodified disposition rules [A005]; DA-1 and DA-2 are blocked by dispatch console write access [A004]. Both are solvable with targeted investment.

- **DE-2 (Damaged Consignment) is Human-led + Agent Support** with the deepest judgment requirement in the exception work stream. Core liability and credit decisions approach Human Only until the insurance protocol is completed and credit thresholds are formalized [A008].

- **DA-3 (Driver Swap) is Human Only** for its core sub-tasks. 6 of 7 suitability dimensions score Low, including risk/compliance and decision determinism. Agent support is retained for intake and documentation only.

- **The critical path to higher autonomy** runs through three dependencies: (1) codifying Sandra's disposition rules [A005, A018]; (2) formalizing customer tier data in CRM [A009]; (3) dispatch console API wrapper [A004, A022].

- **Billing Disputes** (~60/day, 28 min avg) is excluded from this phase; Aurum constraints make delegation infeasible without infrastructure investment [A007, A021].

**Estimated delegatable volume at Wave 1**: 450–600 daily interactions automated or substantially assisted, assuming ETA inquiries are in scope. Without ETA inquiries, Wave 1 covers 25–35% of exception case load. Agent cost per case target: <£0.15 vs. ~£3.50–£7.00 current loaded cost per case [A001].

**Architecture recommendation**: Build two foundational agents (ETA Status Agent, Unattended Address Agent) in Wave 1 to establish shared CRM read + driver app read/write integration assets that compound into all subsequent agents.

---

## 2. Input Documents and Scope

**Source documents:**

- `specs/cognitive-load-map.md` — Phase 2 output: 7 JtDs, 34 micro-tasks, 7 cognitive breakpoints, lived process narrative
- `input-docs/atx/atx-assessment.md` — Phase 3 methodology reference
- `input-docs/atx/atx-concepts.md` — Delegation archetypes and cognitive work definitions
- `input-docs/atx/atx-agent-mapping.md` — Agent mapping framework (Phase 4 input)
- `input-docs/scenario.md` — Apex Distribution scenario and five artefacts

**Work streams in scope:**

| Work Stream | Volume | Avg Handle Time | In Phase 3 Scope |
|-------------|--------|-----------------|------------------|
| Delivery Exceptions | ~180/day | 12 min | Yes |
| ETA Inquiries | ~400/day | 4 min | Yes (assessed with DE-3) |
| Dispatch Adjustments | ~90/day | 18 min | Yes |
| Billing Disputes | ~60/day | 28 min | No [A021] |

---

## 3. Phase 3 Methodology

Per `atx-assessment.md`, Phase 3 scores each candidate JtD on seven suitability dimensions and assigns a delegation archetype. This document extends that methodology with:

- **Sub-task differentiation**: where micro-tasks within a JtD warrant materially different archetypes, they are called out explicitly
- **Trade-off analysis**: each archetype assignment is compared against the next tier up and down
- **Architecture roadmap**: archetype assignments are translated into agent designs and wave sequencing

---

## 4. Suitability Scoring Framework

### Dimension Definitions

| Dimension | H — High Suitability | L — Low Suitability |
|-----------|----------------------|----------------------|
| **Input Structure** | Structured, machine-readable | Unstructured, ambiguous, requires interpretation |
| **Decision Determinism** | Clear rules, predictable outputs | Judgment-dependent, contextual, implicit |
| **Tool Coverage** | APIs available or buildable | Systems inaccessible, black-box, or manual |
| **Context Complexity** | State can be made explicit | Requires institutional knowledge or relationship history |
| **Exception Rate** | Rare, predictable exceptions | Frequent, unpredictable edge cases |
| **Latency Constraint** | Batch or async acceptable | Real-time, sub-second response required |
| **Risk / Compliance** | Reversible, low consequence | Irreversible, regulated, high-consequence |

### Archetype Thresholds

| Archetype | Suitability Profile |
|-----------|---------------------|
| **Human Only** | ≥3 dimensions at L, especially Risk/Compliance and Decision Determinism |
| **Human-led + Automation Support** | Fully deterministic sub-tasks automatable; no reasoning required |
| **Human-led + Agent Support** | Mixed H/M/L; judgment-heavy dimensions remain L |
| **Agent-led + Human Oversight** | ≤1 dimension at L; HITL required for high-stakes outputs [A016] |
| **Fully Agentic** | All dimensions M or H; volume justifies full delegation |

**Anti-pattern check**: if a task is fully deterministic, use RPA or static rules — not an agent. Agents are for non-determinism.

---

## 5. Delegation Suitability Matrix

Scores use **H** (high suitability for delegation), **M** (medium), **L** (low). The *Score* column counts L-rated dimensions; the archetype threshold is: ≥3L → Human-led or below; ≤1L → Agent-led candidate.

### 5.1 Delivery Exceptions

#### Summary

| JtD | Input Struct | Decision Det | Tool Coverage | Context Complexity | Exception Rate | Latency | Risk / Compliance | L-count | Archetype |
|-----|-------------|--------------|---------------|-------------------|----------------|---------|-------------------|---------|-----------|
| DE-1 Refused Delivery | M | **L** [A005] | M [A003, A004, A007] | **L** [A005, A009] | **L** | **L** | M | 4 | Human-led + Agent Support |
| DE-2 Damaged Consignment | **L** | **L** [A008] | M [A007] | **L** [A008] | **L** | M | **L** [A008] | 5 | Human-led + Agent Support |
| DE-3 Missed Delivery Window | **H** | M [A010] | M [A003, A010] | M [A010] | M | **L** | M [A009] | 1 | Agent-led + Human Oversight |
| DE-4 Unattended Address | **H** | M | **H** [A003] | M | M | **L** | M | 1 | Agent-led + Human Oversight |

---

#### DE-1: Resolve Refused Delivery — Detailed Scoring

| Dimension | Score | Evidence and References |
|-----------|-------|------------------------|
| Input Structure | M | Driver report arrives via voicemail or app message; refusal narrative requires interpretation (Artefact 1: Mark's call about the Stein-Allen pallet) |
| Decision Determinism | **L** | Disposition rules (return / hold / re-attempt) are not codified; Sandra and dispatchers apply tacit judgment [A005]; SOP references retired tooling (Artefact 4) |
| Tool Coverage | M | CRM REST API (H); driver app read-only (M) [A003]; dispatch console limited (L) [A004]; Aurum batch-only (L) [A007] — averaged M |
| Context Complexity | **L** | Requires customer account tier [A009], driver route state, refusal reason interpretation, and informal disposition norms not in any system [A005] |
| Exception Rate | **L** | Conflicting driver/customer accounts are common (Artefact 1); high-value escalations irregular; edge cases frequent |
| Latency Constraint | **L** | Driver is parked, waiting for instruction; 6+ downstream drops at risk (Artefact 1) |
| Risk / Compliance | M | Financial impact (return cost, potential credit); reversible with further action; £500 escalation threshold exists but is only partial logic |

**Score: 4L, 3M → Human-led + Agent Support**

**Delegatable sub-tasks** (Agent-led + Human Oversight within the JtD):
- DE-1.1: Parse and structure driver report from app message
- DE-1.3: Retrieve customer account and delivery history — CRM API
- DE-1.4: Apply high-value escalation threshold (>£500 rule) — deterministic
- DE-1.7: Communicate disposition instruction to driver — template via app
- DE-1.8: Create and log case in CRM — structured form entry

**Human-led sub-tasks:**
- DE-1.2: Classify refusal reason — interpretation of conflicting narratives [A005]
- DE-1.6: Decide disposition — judgment-dependent on route context, customer relationship, driver capacity [A005]
- DE-1.9: Customer follow-up when upset — relationship-sensitive [A009]
- DE-1.10: Billing adjustment coordination — Aurum constraint [A007]

---

#### DE-2: Handle Damaged Consignment Report — Detailed Scoring

| Dimension | Score | Evidence and References |
|-----------|-------|------------------------|
| Input Structure | **L** | Damage assessment requires photo interpretation plus unstructured driver/customer narrative; quality of photos varies |
| Decision Determinism | **L** | Transit vs. packaging liability requires judgment [A008]; SOP section 4.3 is explicitly incomplete ("TBD pending review of insurance protocol" — Artefact 4) |
| Tool Coverage | M | CRM (H); Aurum batch-only (L) [A007]; dispatch console limited for return logistics (L) [A004]; driver app photo upload (M) |
| Context Complexity | **L** | Liability norms are informal; recurring damage pattern recognition requires aggregated history not surfaced in CRM [A008] |
| Exception Rate | **L** | Frequent ambiguity in transit vs. packaging liability; insurance threshold cases irregular |
| Latency Constraint | M | Customer communication is time-sensitive; credit processing via Aurum is inherently batch [A007] |
| Risk / Compliance | **L** | Financial liability, insurance threshold, audit trail required; Sandra's unlogged £170 credit illustrates current audit gap (Artefact 2) [A008] |

**Score: 5L, 2M → Human-led + Agent Support**

**Delegatable sub-tasks:**
- DE-2.1: Receive damage report, extract structured fields — CRM API
- DE-2.3: Retrieve consignment and sender details — CRM / dispatch system
- DE-2.5: Query recurring damage patterns for sender or route — CRM analytics [A006]
- DE-2.7: Draft customer resolution communication — template with agent-authored message

**Human-led sub-tasks (approaching Human Only):**
- DE-2.2: Assess damage severity and liability — visual judgment + narrative interpretation [A008]
- DE-2.4: Determine credit amount — policy exists but is judgment-heavy; supervisor approval for high amounts [A008]
- DE-2.6: Initiate credit in Aurum — manual ticket process [A007]

---

#### DE-3: Investigate Missed Delivery Window — Detailed Scoring

| Dimension | Score | Evidence and References |
|-----------|-------|------------------------|
| Input Structure | **H** | Customer inquiry is highly predictable ("Where is order #AX-771-3344?" — Artefact 3); structured order reference available |
| Decision Determinism | M | Status lookup is deterministic; ETA estimation requires tacit route timing knowledge [A010] |
| Tool Coverage | M | CRM REST API (H); driver app read-only (M) [A003, A010]; dispatch console not required for status inquiry |
| Context Complexity | M | Route timing partially tacit [A010]; majority of relevant data is API-accessible |
| Exception Rate | M | Root cause diagnosis has a judgment element; most cases resolve via status lookup |
| Latency Constraint | **L** | Customer expects near-real-time response (Artefact 3: SMS exchange completed in 11 minutes) |
| Risk / Compliance | M | SLA breach risk for high-value customers [A009]; reputational; reversible |

**Score: 1L, 5M, 1H → Agent-led + Human Oversight**

**Note on Latency L**: The L score reflects that the task cannot be batched — not that an agent cannot respond quickly. An agent querying CRM + driver app in parallel responds in 2–3 seconds, which is faster than the current 5–10 minute human process. The latency constraint is satisfied by the archetype, not blocked by it.

**Escalation triggers for human oversight:**
- SLA breach confirmed (missed window = contract breach) [A009]
- Consignment appears lost (GPS stale, driver offline)
- Agent ETA confidence below threshold [A017]
- Customer escalation request

---

#### DE-4: Manage Unattended Address Exception — Detailed Scoring

| Dimension | Score | Evidence and References |
|-----------|-------|------------------------|
| Input Structure | **H** | Driver app report is structured; CRM safe place / neighbour authority fields are structured |
| Decision Determinism | M | Rules exist (safe place authority on file, signature requirement for high-value); edge cases require judgment |
| Tool Coverage | **H** | CRM REST API (H); driver app messaging API (H) [A003]; dispatch console not required for primary path |
| Context Complexity | M | Customer preferences largely in CRM; high-value rules codifiable; some edge cases tacit |
| Exception Rate | M | Missing safe place authority (data gap [A013]); time-sensitive consignments (M frequency) |
| Latency Constraint | **L** | Driver is at the address, waiting for instruction in real-time |
| Risk / Compliance | M | Theft / loss liability for unattended delivery; reversible (depot pickup option exists) |

**Score: 1L, 4M, 2H → Agent-led + Human Oversight**

Same latency note as DE-3 applies: agent satisfies real-time constraint.

**Escalation triggers for human oversight:**
- High-value consignment requiring signature but no customer contact reachable
- Missing safe place authority and re-delivery not same-day feasible
- Customer requests explicit policy exception

---

### 5.2 Dispatch Adjustments

#### Summary

| JtD | Input Struct | Decision Det | Tool Coverage | Context Complexity | Exception Rate | Latency | Risk / Compliance | L-count | Archetype |
|-----|-------------|--------------|---------------|-------------------|----------------|---------|-------------------|---------|-----------|
| DA-1 Additional Pickup | M | M | M [A003, A004] | M [A002] | M | **L** | M | 1 | Human-led + Agent Support |
| DA-2 Route Diversion | M | M [A009] | **L** [A004] | M [A009] | M | **L** | M | 2 | Human-led + Agent Support |
| DA-3 Driver Swap | M | **L** [A002] | **L** [A002, A004, A014] | **L** [A002, A014] | **L** | **L** | **L** [A002] | 6 | Human Only (core) |

---

#### DA-1: Process Additional Pickup Request — Detailed Scoring

| Dimension | Score | Evidence and References |
|-----------|-------|------------------------|
| Input Structure | M | Customer request via phone or email; semi-structured; validation fields (location, time, weight) are obtainable |
| Decision Determinism | M | Route feasibility and vehicle capacity are calculable; driver selection has a judgment component [A002] |
| Tool Coverage | M | CRM (H); driver app capacity / GPS read (M) [A003]; dispatch console write for route update (L) [A004]; route optimization engine unconfirmed [A004] |
| Context Complexity | M | Route state is largely explicit; driver capability and willingness are partially tacit [A002] |
| Exception Rate | M | ~15% of cases require customer callback (DA-1.1); driver refusal is possible [A002] |
| Latency Constraint | **L** | Real-time; coordinator must act before driver departs current stop |
| Risk / Compliance | M | Reversible; downstream SLA impact; driver hours compliance [A002] |

**Score: 1L, 6M → Human-led + Agent Support**

**Binding constraint**: Dispatch console write limitation [A004] means the agent cannot autonomously execute the route update (DA-1.6). Agent handles feasibility analysis, driver candidate ranking, ETA impact calculation, and customer notification drafting; human confirms the driver and executes the route update.

**Path to Agent-led + Human Oversight**: Resolve dispatch console API [A004, A022] and codify driver selection criteria [A002].

---

#### DA-2: Execute Route Diversion — Detailed Scoring

| Dimension | Score | Evidence and References |
|-----------|-------|------------------------|
| Input Structure | M | Diversion request is semi-structured; arrives via customer call or driver message |
| Decision Determinism | M | Downstream delivery impact is calculable; customer delay tolerance is informally tiered [A009] |
| Tool Coverage | **L** | Dispatch console is the primary execution system and has limited write API [A004]; route update requires manual Citrix entry |
| Context Complexity | M | Route data is available; customer priority levels are informally known [A009] |
| Exception Rate | M | Diversion may create unacceptable downstream delays; customer may refuse alternate timing |
| Latency Constraint | **L** | Time-critical; driver must be re-routed while in transit |
| Risk / Compliance | M | SLA breach risk; customer relationship impact [A009]; reversible |

**Score: 2L, 5M → Human-led + Agent Support**

**Binding constraint**: Same as DA-1 — dispatch console write access [A004]. Agent calculates route impact, drafts customer ETA updates, flags priority account implications [A009]; human executes the route change in the console.

---

#### DA-3: Manage Driver Swap — Detailed Scoring

| Dimension | Score | Evidence and References |
|-----------|-------|------------------------|
| Input Structure | M | Initial report (illness, breakdown) is semi-structured; subsequent data structured |
| Decision Determinism | **L** | Driver selection requires judgment on qualifications, fatigue, location, and willingness [A002]; overtime authorization requires cost / SLA tradeoff |
| Tool Coverage | **L** | Workforce management system write API unconfirmed [A002]; dispatch console limited [A004]; driver contact relies on phone calls [A014] |
| Context Complexity | **L** | Driver capability, willingness, and relationship knowledge are informal [A002, A014]; contractor and union rules implicit |
| Exception Rate | **L** | Limited driver pool; drivers may refuse short-notice swap (DA-3.4 is the highest-friction sub-task); vehicle handoff location constraints |
| Latency Constraint | **L** | Time-critical; multiple deliveries at risk; driver cannot wait indefinitely |
| Risk / Compliance | **L** | Driver welfare, hours compliance, cargo security, and handoff safety [A002] |

**Score: 6L, 1M → Human Only (core negotiation and decision sub-tasks)**

**Agent Support scope retained (2 sub-tasks):**
- DA-3.1: Structure driver unavailability report — extract route number, location, reason, affected deliveries
- DA-3.7: Document incident and log shift adjustments — CRM / incident system write after human resolves the swap

**Human Only sub-tasks:**
- DA-3.2: Identify replacement driver — judgment on qualifications, location, availability [A002]
- DA-3.3: Determine handoff location — safety, convenience, cargo security judgment [A002]
- DA-3.4: Negotiate with drivers — relationship-dependent, persuasion, union rules [A014]
- DA-3.5: Authorize overtime / contractor call-out — cost vs. SLA vs. budget judgment [A002]

---

## 6. Archetype Assignments: Rationale and Trade-off Analysis

### 6.1 Agent-led + Human Oversight

#### DE-3: Investigate Missed Delivery Window

**Rationale**: The standard case is a lookup-and-respond workflow: query CRM for order, query driver app for GPS / status, estimate ETA, respond to customer. The agent satisfies the real-time latency constraint (API query + generation < 3 seconds vs. current 5–10 minute human process). Tacit route timing knowledge [A010] is partially capturable through GPS history pattern analysis and improves with volume.

**Why not Fully Agentic?**
- ETA estimation accuracy [A020] is unvalidated; tacit dispatcher knowledge [A010] introduces structural variance that is not yet encoded
- SLA breach cases require human judgment and accountability [A009]
- Lost consignment investigations require cross-system diagnosis beyond a status lookup

**Why not Human-led + Agent Support?**
- Volume (~400 ETA inquiries + DE-3 share of 180 exceptions/day) makes human-led economically indefensible
- Current 5–10 minute response time is already causing customer dissatisfaction (Artefact 3: customer calls out the 4-hour ETA window)
- ≥80% of cases are pure lookup with no judgment content; human review at this rate is overhead without value addition

**Risk of assigned archetype**: Agent ETA estimates below accuracy threshold [A020] erode customer trust over time. **Mitigation**: agent communicates confidence explicitly ("based on last GPS position, estimated delivery 14:00–15:00") and escalates when confidence is below threshold [A017].

---

#### DE-4: Manage Unattended Address Exception

**Rationale**: The decision tree is the most structured of all exception sub-types: check safe place authority (CRM lookup) → verify consignment eligibility (value + signature rules) → apply policy → instruct driver via app. Both primary data sources (CRM, driver app) have confirmed API access [A003]. Execution path is end-to-end agent-feasible.

**Why not Fully Agentic?**
- Safe place authority field in CRM has known data gaps [A013]; missing data creates uncertain cases requiring human judgment
- High-value consignment edge cases require human accountability for theft / loss risk
- Policy exceptions (customer demands unattended delivery despite mandatory signature) require human escalation

**Why not Human-led + Agent Support?**
- Cases with populated safe place authority and eligible consignments have zero judgment requirement — full automation is appropriate
- Good tool coverage (CRM + driver app messaging API) makes the complete execution path feasible without human involvement
- Driver is at the address waiting; human response latency introduces real operational cost (delayed driver, knock-on route delays)

**Risk of assigned archetype**: Incorrect unattended delivery decision causes theft or loss. **Mitigation**: hard rule — no autonomous unattended delivery above value threshold; explicit escalation for all high-value items [A016].

---

### 6.2 Human-led + Agent Support

#### DE-1: Resolve Refused Delivery

**Rationale**: The disposition decision (return / hold / re-attempt) is the cognitive core of this JtD and cannot be safely delegated without first codifying Sandra's implicit rules [A005, A018]. Until those rules are formalized and validated against historical cases [A006], human judgment is irreplaceable at DE-1.6. The surrounding sub-tasks (case creation, threshold detection, driver notification) are automatable today.

**Why not Agent-led + Human Oversight?**
- Decision rules are not codified [A005]; an agent acting on incomplete or incorrect rules creates wrong dispositions (abandoned drivers, unwanted returns, lost consignments)
- Conflicting accounts (driver vs. warehouse manager, Artefact 1) require interpretive judgment that current agent capability cannot reliably resolve
- The £500 threshold rule is only a partial trigger; full escalation logic is tacit [A005, A009]

**Path to upgrade (target: Wave 2)**: Conduct Sandra decision rule elicitation [A018]; formalize disposition decision tree; validate on 50+ historical cases [A006]. Target Agent-led + Human Oversight within 6 months of Wave 2 launch.

**Estimated value at current archetype**: ~40% reduction in average handling time (DE-1.3, DE-1.4, DE-1.7, DE-1.8 automated = ~5 of 12 min eliminated).

---

#### DA-1: Process Additional Pickup Request

**Rationale**: The agent handles all cognitive preparation — feasibility analysis, driver candidate ranking by capacity and proximity, ETA impact calculation, and customer notification drafting. The human confirms the driver selection and executes the route update in the dispatch console. The binding constraint is purely technical [A004], not cognitive.

**Why not Agent-led + Human Oversight?**
- Dispatch console has no confirmed write API [A004]; route update execution requires Citrix manual entry — the agent physically cannot complete the workflow
- Driver selection has implicit capability and relationship factors [A002] that are not yet encoded

**Path to upgrade (target: Wave 3)**: Build dispatch console API wrapper [A022]; codify driver selection scoring criteria [A002].

---

#### DA-2: Execute Route Diversion

**Rationale**: Same primary constraint as DA-1 — dispatch console write access [A004]. The additional dimension is that customer delay tolerance is informally tiered by account [A009], adding a judgment layer to which customers receive proactive personal communication vs. standard automated notification.

**Path to upgrade**: Same as DA-1 plus customer tier formalization in CRM [A009].

---

#### DE-2: Handle Damaged Consignment Report

**Rationale**: Liability assessment (transit vs. packaging) and credit determination are the highest-judgment tasks in the entire analysis. The SOP section covering damage handling is explicitly incomplete (Artefact 4). The audit trail for credits is broken (Artefact 2, Artefact 2 internal note) [A008]. This JtD requires **process repair before agent delegation** — the current state is not a delegation ceiling problem; it is a process integrity problem.

**Path to upgrade**: (1) Complete insurance protocol documentation; (2) formalize credit approval thresholds and build CRM audit trail [A008]; (3) re-assess liability classification for a confidence-scored agent recommendation (not autonomous decision). Timeline: Wave 2 at earliest.

---

### 6.3 Human Only

#### DA-3: Manage Driver Swap (core sub-tasks)

**Rationale**: 6 of 7 suitability dimensions score L. The critical-path tasks — driver selection, handoff location, negotiation, overtime authorization — are judgment-dense, relationship-dependent, safety-sensitive, and time-critical simultaneously. DA-3.4 (driver negotiation) involves union considerations, driver welfare, and real-time persuasion that cannot be delegated without safety and compliance risk. No plausible roadmap exists to move the core decision tasks above Human Only within a 12-month horizon.

**Why not Human-led + Agent Support for more sub-tasks?**
- Workforce management system write API is unconfirmed [A002]; the agent cannot reliably surface or update driver availability
- Phone-based driver communication [A014] makes agent-mediated messaging ineffective for negotiation contexts
- Safety and compliance stakes (driver hours, cargo security at handoff) require unambiguous human accountability

**Agent Support scope retained**: DA-3.1 (structured intake) and DA-3.7 (post-resolution documentation) are included in the Orchestration Layer at Wave 3.

---

## 7. Proposed Agentic Solution Architecture

### 7.1 Wave 1: Foundation Agents (Months 1–4)

**Target archetype**: Agent-led + Human Oversight  
**Prerequisite**: CRM API access confirmed; driver app API scope confirmed [A003]; Wave 1 agent platform selected [A019]

#### Agent 1 — ETA Status Agent

| Field | Value |
|-------|-------|
| **Scope** | ETA Inquiries (~400/day) + DE-3 standard cases (~60% of DE-3 volume) |
| **Primary JtDs** | DE-3 (Missed Delivery Window), ETA Inquiry work stream |
| **Archetype** | Agent-led + Human Oversight; HITL ceiling ≤30% [A016] |
| **Integrations built** | CRM REST API (read); Driver App API (read); SMS / email channel |
| **Escalation triggers** | SLA breach detected [A009]; GPS stale / consignment lost; agent confidence < 0.75 [A017]; customer explicit escalation request |
| **Compounding value** | CRM read + driver app read integration reused by all subsequent agents |

#### Agent 2 — Unattended Address Agent

| Field | Value |
|-------|-------|
| **Scope** | DE-4 (~30% of exception volume, ~55 cases/day) |
| **Primary JtDs** | DE-4 (Unattended Address Exception) |
| **Archetype** | Agent-led + Human Oversight; HITL ceiling ≤20% [A016] |
| **Integrations built** | Driver app messaging API (write) — new capability; CRM safe place / delivery instructions query |
| **Escalation triggers** | High-value item + no signature authority; no safe place data + customer unreachable; driver capacity insufficient for same-day re-attempt |
| **Compounding value** | Driver app messaging write integration reused by Wave 2 (DE-1 driver notification) and Wave 3 (DA-1 driver instructions) |

**Wave 1 estimated impact**: 450–600 daily interactions automated or substantially assisted. Agent cost per case target: <£0.15 vs. ~£3.50–£7.00 current loaded cost [A001]. Shared integration assets (CRM read, driver app read + write) are the primary platform investment; marginal cost of each subsequent agent is significantly lower.

---

### 7.2 Wave 2: Expanding Coverage (Months 5–9)

**Prerequisite**: Decision rule elicitation complete [A018]; customer tier data formalized in CRM [A009]; credit audit trail established [A008]

#### Agent 3 — Refused Delivery Triage Agent

| Field | Value |
|-------|-------|
| **Scope** | DE-1 — initially Human-led + Agent Support; target Agent-led + Human Oversight post rule-formalization [A005] |
| **Primary JtDs** | DE-1 (Refused Delivery Resolution) |
| **Integrations reused** | CRM read (Agent 1), driver app messaging write (Agent 2) |
| **New integrations** | CRM case write; billing queue handoff (structured output to human for Aurum action) |
| **Prerequisite** | Sandra disposition rules codified in validated decision tree [A005, A018] |

#### Agent 4 — Damage Report Support Agent

| Field | Value |
|-------|-------|
| **Scope** | DE-2 — Human-led + Agent Support (liability assessment and credit determination remain human) |
| **Primary JtDs** | DE-2 (Damaged Consignment Report) |
| **Integrations reused** | CRM read + write (Agents 1, 3), driver app photo retrieval (Agent 1) |
| **New integrations** | Recurring damage pattern analytics query [A006]; photo structured extraction |
| **Prerequisite** | Credit approval threshold formalized; CRM audit trail for credits established [A008] |

---

### 7.3 Wave 3: Multi-Agent Orchestration (Months 10–18)

**Prerequisite**: Dispatch console API wrapper built [A022]; customer tier data fully formalized [A009]

#### Agent 5 — Dispatch Coordination Agent

| Field | Value |
|-------|-------|
| **Scope** | DA-1 + DA-2 (Additional Pickup + Route Diversion) — Human-led + Agent Support → Agent-led + Human Oversight |
| **Primary JtDs** | DA-1, DA-2 |
| **Integrations reused** | CRM (Agents 1–4), driver app messaging (Agent 2) |
| **New integrations** | Dispatch console API wrapper [A022]; route optimization engine [A004] |
| **Human role retained** | Final route update confirmation until full dispatch console write API is validated |

#### Orchestration Layer

- Connects DE agents → billing queue → dispatch coordination for cross-stream cases (~25% of volume) [A012]
- Maintains shared case context across work streams (handoff state, open billing disputes, prior exceptions)
- Triggers downstream workflows automatically (refused delivery → credit queue initiation [A007])
- Surfaces cross-stream history to human agents ("this customer has 3 open disputes this quarter")
- DA-3 Agent Support: structured intake (DA-3.1) and post-resolution documentation (DA-3.7) included here

**DA-3 remains Human Only** for core sub-tasks through all waves. The orchestration layer provides agent-assisted intake and documentation without changing the archetype for decisions.

### Integration Reuse Matrix

| Integration / Asset | Agent 1 (ETA) | Agent 2 (Unattended) | Agent 3 (Refused Del.) | Agent 4 (Damage) | Agent 5 (Dispatch) | Orchestration |
|--------------------|:---:|:---:|:---:|:---:|:---:|:---:|
| CRM read API | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| Driver app read API | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| Driver app messaging (write) | — | ✓ Build | ✓ Reuse | — | ✓ Reuse | ✓ Reuse |
| CRM case write | — | — | ✓ Build | ✓ Reuse | — | ✓ Reuse |
| Dispatch console API | — | — | — | — | ✓ Build [A022] | ✓ Reuse |
| Billing queue handoff | — | — | ✓ Build | ✓ Reuse | — | ✓ Reuse |
| Photo extraction | — | — | — | ✓ Build | — | — |
| Cross-stream state store | — | — | — | — | — | ✓ Build |

---

## 8. Assumptions Register (Phase 3 Additions)

Assumptions A001–A015 are carried forward from `specs/cognitive-load-map.md`. New assumptions introduced in this phase:

| ID | Assumption | Confidence | Impact if Wrong | Validation Path |
|----|-----------|------------|-----------------|-----------------|
| A016 | HITL escalation rate ceiling: ≤30% of cases requiring human review is operationally acceptable for Agent-led + Human Oversight at current staffing (35 FTEs); ≤20% for high-volume routine JtDs (DE-4) | Medium | Team cannot absorb escalation volume above ceiling; Wave 1 scope must shrink or headcount must be restructured | Measure in Wave 1 pilot and confirm with COO |
| A017 | Agent confidence threshold: a score below 0.75 on ETA estimates and disposition recommendations triggers mandatory human escalation; threshold to be tuned during Wave 1 | Medium | Too low → excessive HITL undermines value; too high → unacceptable error rate reaching customers | A/B test threshold calibration in Wave 1 |
| A018 | Decision rule elicitation: Sandra and ≥2 senior dispatchers are available for a structured 2-week shadowing exercise (20+ cases per work stream) before Wave 2 deployment; elicitation output is sufficient to codify a validated disposition decision tree for DE-1 | Medium | DE-1 remains Human-led + Agent Support indefinitely; Wave 2 Refused Delivery Agent cannot be built as designed | Requires COO (Sarah Whitmore) sponsorship to secure time |
| A019 | Wave 1 sequencing: ETA Status Agent and Unattended Address Agent are selected as initial pilots because they have the best combination of API availability, structured decision profiles, and highest volume-to-judgment ratio; this order creates shared integration assets (CRM read, driver app messaging) that compound into all subsequent agents | High | Alternative sequencing is viable; compounding benefit is reduced but not eliminated | Architecture review with engineering at Month 1 |
| A020 | ETA prediction SLA: agent ETA estimates must fall within ±45 minutes of actual delivery in ≥80% of cases to be acceptable for autonomous customer response without accuracy caveat; below this threshold, agent must state confidence level explicitly or escalate | Medium | Customer trust degradation if accuracy falls below threshold; may require mandatory human review of all ETA estimates until model improves | Measure GPS-to-arrival accuracy in first week of pilot against ±45 min benchmark |
| A021 | Billing Disputes work stream (~60/day, 28 min avg) is excluded from this Phase 3 analysis; Aurum constraints [A007] make meaningful agent delegation infeasible without (a) a real-time Aurum API or (b) a parallel credit workflow outside Aurum with batch reconciliation; the work stream will be re-assessed when the Aurum roadmap is clarified | High | If Aurum API is available sooner, Billing Disputes becomes the highest-value target by handling time and should be re-inserted into Phase 3 immediately | Monitor Aurum vendor roadmap quarterly; escalate to COO if API is announced |
| A022 | Dispatch console API: a REST / HTTP middleware wrapper around the Citrix-deployed Java console is technically feasible but requires vendor engagement and is estimated at 4–6 weeks development for read + write endpoints; without this, DA-1 and DA-2 remain Human-led + Agent Support permanently | Low–Medium | If not feasible, Dispatch Coordination Agent (Wave 3) cannot be built as designed; dispatch automation ceiling is Human-led + Agent Support | Technical spike with dispatch console vendor in Month 1; escalate to CTO |

---

## 9. Open Questions and Next Steps

### Critical Path Items (block Wave 1 start)

| Item | Owner | Target |
|------|-------|--------|
| Confirm driver app API write capabilities for messaging [A003] | Engineering | Month 1 |
| Validate CRM safe place authority field completion rate [A013] | Customer Ops data lead | Month 1 |
| Select agent platform — enterprise-owned orchestration vs. Salesforce Einstein [A019] | CTO + COO | Month 1 |
| Technical spike: dispatch console API feasibility [A004, A022] | CTO / console vendor | Month 1 |

### Wave 1 Measurement Plan

| Metric | Target | Source |
|--------|--------|--------|
| ETA accuracy: agent estimate within ±45 min | ≥80% of cases [A020] | GPS vs. actual delivery log |
| HITL escalation rate: DE-3 + ETA | ≤30% [A016] | Agent escalation log |
| HITL escalation rate: DE-4 | ≤20% [A016] | Agent escalation log |
| Agent confidence threshold calibration | 0.75 baseline [A017] | Confidence score distribution |
| Cases handled without human intervention | Target ≥70% | Agent activity log |

### Wave 2 Prerequisites (begin in Month 2)

| Item | Owner | Target |
|------|-------|--------|
| Sandra decision rule elicitation: identify session coordinator and design protocol [A018] | FDE / COO sponsorship | Month 3 |
| Customer tier formalization: map top 50 accounts in CRM [A009] | Customer Ops + Sales | Month 3 |
| Credit audit trail: design CRM workflow to replace manual override [A008] | Customer Ops + Finance | Month 3 |
| Insurance protocol: complete SOP section 4.3 (Artefact 4 gap) | Customer Ops + Legal | Month 3 |

### Assumptions Requiring Validation Before Architecture is Final

The following open assumptions, if resolved differently than expected, would materially change the archetype assignments or wave sequencing:

- **A004 / A022**: Dispatch console write API — determines whether DA-1 and DA-2 can ever reach Agent-led + Human Oversight
- **A005 / A018**: Disposition rule codification — determines DE-1 archetype ceiling
- **A007**: Aurum API roadmap — determines whether Billing Disputes enters scope
- **A009**: Customer tier formalization — affects DE-1, DA-2 escalation logic
- **A003**: Driver app write access scope — affects all agent-to-driver communication paths

---

## Document Control

| Field | Value |
|-------|-------|
| **Phase** | 3 — Delegation Qualification |
| **Created** | 2026-05-11 |
| **Version** | 1.0 |
| **Owner** | AI FDE Team |
| **Input document** | `specs/cognitive-load-map.md` (Phase 2) |
| **Next phase** | Phase 4 — Candidate Prioritisation |
| **Related** | `specs/assumptions.md`, `input-docs/atx/atx-assessment.md`, `input-docs/atx/atx-agent-mapping.md` |
