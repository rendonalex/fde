# Cognitive Load Map — Scenario 4: Community Content Moderation
## MiniBase Platform

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Scenario Context](#scenario-context)
3. [Lived Process vs. Documented Process](#lived-process-vs-documented-process)
4. [Jobs to be Done (JtD) Decomposition](#jobs-to-be-done-jtd-decomposition)
5. [Cognitive Zones and Breakpoints](#cognitive-zones-and-breakpoints)
6. [Micro-Task Cognitive Load Inventory](#micro-task-cognitive-load-inventory)
7. [Assumptions Register](#assumptions-register)
8. [Key Findings](#key-findings)

---

## Executive Summary

**Platform**: MiniBase — tabletop-miniature hobbyist community platform  
**Stakeholder**: Tomasz "Tom" Włodarczyk, Community Manager  
**Team**: 8 volunteer moderators + 2 paid staff (Tom + Senior Moderator)  
**Daily volume**: ~12,000 posts; ~1,500/day (12.5%) enter moderation queue  
**Daily effort**: ~47 hours across 10-person team (at capacity)  

**Core tension**: False positives are survivable; one viral false negative is existential.

**Primary cognitive bottleneck**: Grey-zone case review (360/day, 5 min/case, 24% of queue) — requires sub-forum contextual norms, prior-incident awareness, sponsor/IP-claim sensitivity, and volunteer-moderator consensus-building.

---

## Scenario Context

### The Platform
- **MiniBase**: UK-based tabletop miniature hobbyist community (~180K active users)
- **Geography**: UK, Western Europe, North America, Japan, Australia
- **Structure**: 14 sub-forums + gallery section
- **Volume**: 12K posts/day
- **Revenue**: £1.4M/yr (premium memberships, gallery commissions, sponsored content)

### The Function
**Hybrid moderation team**:
- 8 volunteer moderators (distributed across US, UK, Germany, Australia, Japan for timezone coverage)
- 2 paid staff: Community Manager (Tom) + Senior Moderator
- Total capacity: ~47 hours/day (team at full capacity) [**Assumption A01, confidence: high**]

### Work Stream Volumes

| Stream | Daily Volume | % of Queue | Handling Time | Daily Effort |
|--------|--------------|------------|---------------|--------------|
| Routine spam / clear violations | 1,080 | 72% | ~30 sec/case | ~9 hrs |
| Grey-zone case review | 360 | 24% | ~5 min/case | ~30 hrs |
| User dispute appeals | 60 | 4% | ~8 min/case | ~8 hrs |
| IP-claim resolution | 3-5/week | <1% | ~30 min/case | Variable |
| **Total queue** | **1,500/day** | **100%** | | **~47 hrs/day** |

[**Assumption A02, confidence: medium** — Daily effort calculation assumes no overlap between streams and that handling times are median, not including coordination overhead.]

---

## Lived Process vs. Documented Process

### Documented Process (Implied)
Global 14-page moderation policy applied uniformly across all sub-forums, with clear violation categories and standardized response protocols.

### Lived Process (Evidence-Based)

**From Artefact 4.2 (Discord thread):**
- **Sub-forum-specific norms override global policy**: "painters sub has the 'no critique without invitation' thing" — not in global policy, but enforced in practice
- **Context-dependent interpretation**: "Thread title is literally 'help me figure out what's wrong' so OP invited it" — invitation is *implied*, requiring moderator judgment
- **Prior-incident awareness shapes decisions**: "That 'no critique without invitation' is painters-sub-specific" and "That was the sponsor incident. Different."
- **Volunteer consensus-building**: "want a second opinion before I close the report"

**From Artefact 4.3 (Tom's Google Sheet):**
- **Individual account patterns tracked manually**: sculptor IP claims, sponsor accounts, high-profile users
- **Escalation rules not in policy**: "Tom personally reviews every IP claim from @sculpturedragon" after 2024 incident
- **Sub-forum carve-outs**: Historical sub has more permissive rules on historically-charged imagery; Japanese painters sub requires soft-warning protocol due to language/cultural interpretation gaps

**Critical finding**: The 14-page global policy is *necessary but insufficient*. Effective moderation requires:
1. Sub-forum norm awareness (not documented centrally)
2. Individual account history (Tom's sheet + institutional memory)
3. Prior incident sensitivity (2024 sponsor incident; sculptor IP-claim patterns)
4. Cultural/linguistic interpretation (Japanese painters sub)
5. Volunteer coordination and consensus (Discord, not Discourse)

[**Assumption A03, confidence: high** — The 14-page policy is the *baseline*, but effective moderation lives in the undocumented layer.]

---

## Jobs to be Done (JtD) Decomposition

### JtD-1: Triage Inbound Content to Queue
**Trigger**: Post submitted OR user flag OR automated detection  
**Actor**: System + sampling by volunteer moderators  
**Goal**: Determine if post requires moderator review  
**Key systems**: Discourse (forum platform), in-house gallery (Rails app)  
**Expected output**: Post bypasses queue (87.5% of posts) OR enters moderation queue (12.5%)  
**Cognitive nature**: Pattern recognition (automated + moderator sampling)  

**Breakpoint**: System heuristics route obvious violations; moderator sampling catches edge cases. [**Assumption A04, confidence: medium** — The ratio of automated-to-sampled routing is unknown.]

---

### JtD-2: Resolve Routine Spam / Clear Violations
**Trigger**: Post enters queue, flagged as routine spam or clear violation  
**Actor**: Volunteer moderator  
**Goal**: Remove obvious spam, off-topic, or miscategorized posts  
**Volume**: ~1,080/day (~72% of queue)  
**Handling time**: ~30 sec/case  
**Key decisions**: Does this match clear violation patterns? (Yes → remove; No → escalate to JtD-3)  
**Key systems**: Discourse moderation interface  
**Expected output**: Post removed + log entry  
**Cognitive nature**: Execution (minimal judgment required)  

**Key observation**: This is the *only* low-cognitive-load stream. The other 28% of the queue (grey-zone + appeals + IP) absorbs 38 of 47 daily moderator hours.

---

### JtD-3: Review Grey-Zone Cases
**Trigger**: Post flagged by users (e.g., 4 reports for "harsh / harassment") OR moderator identifies ambiguity during sampling  
**Actor**: Volunteer moderator (often seeking second opinion via Discord)  
**Goal**: Determine if content violates norms *in context*  
**Volume**: ~360/day (~24% of queue)  
**Handling time**: ~5 min/case  
**Key decisions**:
- Does this violate *global policy* or *sub-forum norms*?
- Was critique *invited* (explicitly or implicitly)?
- Is tone harsh *within community standards* for this sub-forum?
- Does OP's reaction validate the critique (Artefact 4.1: "thanks, that's actually really useful")?
- Does this involve a sponsor, high-profile sculptor, or prior-incident-sensitive account? (Artefact 4.3)
- Is this a cultural/linguistic interpretation issue? (Japanese painters sub)

**Key systems**: Discourse (post content + report queue), Discord (#mod-decisions channel for consensus), Tom's Google Sheet (account patterns), institutional memory (prior incidents)

**Expected output**: 
- No action (close report with reason)
- Warning (soft or formal)
- Post removal
- Escalation to Tom (sponsor/IP-sensitive cases)

**Cognitive nature**: Synthesis + judgment + consensus-building

**Breakpoints**:
1. **Moderator → Discord (peer consultation)**: When moderator is uncertain ("want a second opinion before I close the report")
2. **Moderator → Tom (escalation)**: When case involves sponsor, IP-claim-sensitive account, or potential viral risk
3. **Moderator → No action (logged)**: When consensus is "within sub norms" (Artefact 4.2: "Closing. Logging in Discourse as 'no action — invited critique within sub norms'")

[**Assumption A05, confidence: medium** — ~30-40% of grey-zone cases involve Discord peer consultation; ~5-10% escalate to Tom. These rates are inferred from artefacts but not explicitly stated.]

---

### JtD-4: Resolve User Dispute Appeals
**Trigger**: User appeals prior moderation action (warning, post removal, suspension)  
**Actor**: Volunteer moderator OR Tom (depending on original action severity)  
**Goal**: Review original decision; uphold, reverse, or modify action  
**Volume**: ~60/day (~4% of queue)  
**Handling time**: ~8 min/case  
**Key decisions**:
- Was original decision consistent with policy + sub-forum norms?
- Has user provided new context?
- Is this a repeat offender or first-time appeal?
- Does this require Tom's sign-off? (sponsor-related, high-profile user, potential PR risk)

**Key systems**: Discourse (moderation log), Discord (if original moderator unavailable), Tom's Google Sheet (account history)

**Expected output**: Appeal upheld, reversed, or modified + communication to user  
**Cognitive nature**: Synthesis + judgment + policy consistency  

**Breakpoint**: Moderator reviews appeal; escalates to Tom if original action was Tom-initiated or involves high-risk account.

---

### JtD-5: Resolve IP-Claim Cases
**Trigger**: Sculptor, manufacturer, or rights-holder submits IP claim via email  
**Actor**: Tom (personally reviews every IP claim after 2024 incident) [Artefact 4.3]  
**Goal**: Validate claim; decide on takedown, user notification, or dismissal  
**Volume**: 3-5/week (~0.6/day, <1% of total workload but high cognitive + legal + PR risk)  
**Handling time**: ~30 min/case + escalation to legal if contested  
**Key decisions**:
- Is claimant credible? (Artefact 4.3: @sculpturedragon is "recurring IP claims" → Tom personally reviews; @vintage_kitbasher is "IP claims credibility unclear" → standard escalation)
- Does claim have merit (copyright, trademark, licensing)?
- Is this a retaliatory claim? (Artefact 4.3: "Watch for retaliatory reports")
- Does this require legal review? (contested claims, high-profile sculptor)
- How do we communicate decision to user and claimant?

**Key systems**: Email (IP-claim correspondence), Discourse/gallery (content in question), Tom's Google Sheet (claimant history), legal record-keeping

**Expected output**: Takedown + user notification OR dismissal + claimant notification OR escalation to legal  
**Cognitive nature**: Synthesis + judgment + legal reasoning + stakeholder management  

**Breakpoints**:
1. **Email → Tom (triage)**: Every IP claim routed to Tom first
2. **Tom → Legal (escalation)**: Contested claims, high-stakes cases
3. **Tom → User + Claimant (communication)**: Final decision + justification

[**Assumption A06, confidence: high** — IP claims are *always* Tom-reviewed after 2024 incident, based on explicit statement in Artefact 4.3.]

---

## Cognitive Zones and Breakpoints

### Zone 1: Intent Recognition & Triage
**Activities**: Post flagged by system, user reports, or moderator sampling → initial classification (routine spam vs. grey-zone vs. appeal vs. IP claim)  
**Cognitive load**: Low to Medium (pattern matching for routine; context-gathering for grey-zone)  
**Primary actors**: System + volunteer moderators  
**Key data sources**: Discourse flags, user reports, post content  
**Latency constraint**: Minutes to hours (no real-time requirement)  

**Breakpoint 1.1**: System heuristics route obvious violations → moderator review  
**Breakpoint 1.2**: Moderator uncertain → escalate to JtD-3 (grey-zone review)

---

### Zone 2: Context Synthesis
**Activities**: Gather sub-forum norms, user history, prior-incident awareness, cultural/linguistic context, sponsor/IP sensitivity  
**Cognitive load**: High (requires institutional memory, Tom's Google Sheet, Discord coordination, artefact review)  
**Primary actors**: Volunteer moderators (for sub-forum norms) + Tom (for sponsor/IP patterns)  
**Key data sources**: 14-page policy (baseline), sub-forum-specific norms (undocumented), Tom's Google Sheet (account patterns), Discord #mod-decisions (peer knowledge), institutional memory (2024 sponsor incident, sculptor IP patterns)  
**Latency constraint**: Minutes to hours  

**Breakpoint 2.1**: Moderator lacks context → Discord peer consultation  
**Breakpoint 2.2**: Case involves sponsor/IP-sensitive account → escalate to Tom

---

### Zone 3: Judgment & Decision
**Activities**: Apply norms + context → decide action (no action, warning, removal, escalation)  
**Cognitive load**: High (non-deterministic; requires balancing false-positive vs. false-negative risk)  
**Primary actors**: Volunteer moderators (routine grey-zone) + Tom (sponsor/IP/high-risk cases)  
**Key decision logic**: 
- "False positives are survivable; one viral false negative is existential" [Tom's mandate]
- Sub-forum norms override global policy in practice (Artefact 4.2)
- Prior incidents shape risk tolerance (2024 sponsor incident)
- Cultural/linguistic interpretation (Japanese painters sub soft-warning protocol)

**Breakpoint 3.1**: Moderator decides within sub-forum norm authority  
**Breakpoint 3.2**: Moderator escalates to Tom for sponsor/IP/viral-risk cases  
**Breakpoint 3.3**: Tom escalates IP claims to legal if contested

---

### Zone 4: Action Execution
**Activities**: Post removal, warning issuance, user notification, appeal communication, IP-claim correspondence  
**Cognitive load**: Low to Medium (execution + communication)  
**Primary actors**: Volunteer moderators (routine actions) + Tom (sponsor/IP communications)  
**Key systems**: Discourse (moderation actions), Discord (volunteer coordination), Email (IP claims)  
**Latency constraint**: Hours to days (user expects timely response)  

**Breakpoint 4.1**: Action logged in Discourse (Artefact 4.2: "Logging in Discourse as 'no action — invited critique within sub norms'")  
**Breakpoint 4.2**: Tom personally communicates sponsor/IP decisions (not delegated to volunteers)

---

### Zone 5: Documentation & Learning
**Activities**: Log decision rationale, update Tom's Google Sheet (account patterns), share learnings in Discord, refine sub-forum norms  
**Cognitive load**: Low to Medium (synthesis + knowledge capture)  
**Primary actors**: Volunteer moderators (Discourse logs) + Tom (Google Sheet updates)  
**Key systems**: Discourse (moderation log), Google Sheets (Tom's tracker), Discord (volunteer knowledge-sharing)  
**Latency constraint**: Days to weeks (not urgent)  

**Breakpoint 5.1**: Decision logged → institutional memory updated  
**Breakpoint 5.2**: Pattern identified → Tom's Google Sheet updated (new account flagged, new sub-forum norm documented)

[**Assumption A07, confidence: medium** — Documentation quality varies by moderator; Tom's Google Sheet is *not* systematically updated for every decision, only high-risk patterns.]

---

## Micro-Task Cognitive Load Inventory

### JtD-2: Routine Spam / Clear Violations

| Micro-Task | Cognitive Load | Input Structure | Decision Determinism | Exception Frequency | Turn-Taking | Latency | Risk Sensitivity | Tool Availability |
|------------|----------------|-----------------|---------------------|--------------------|--------------|---------|--------------------|-------------------|
| **Identify obvious spam** | L | H (structured patterns) | H (clear rules) | L (rare edge cases) | L (solo action) | M (hours acceptable) | L (reversible) | H (Discourse API) |
| **Remove spam post** | L | H | H | L | L | M | L | H |
| **Log removal action** | L | H | H | L | L | M | L | H |

**Delegation suitability**: High — deterministic, low-risk, structured inputs, rare exceptions. [**Assumption A08, confidence: high** — This is the easiest stream to automate, but only if "obvious spam" can be reliably detected. Current 30-sec handling time suggests moderators are confident in their classification.]

---

### JtD-3: Grey-Zone Case Review

| Micro-Task | Cognitive Load | Input Structure | Decision Determinism | Exception Frequency | Turn-Taking | Latency | Risk Sensitivity | Tool Availability |
|------------|----------------|-----------------|---------------------|--------------------|--------------|---------|--------------------|-------------------|
| **Read post + user reports** | M | M (semi-structured) | M | M | L | M | M | H (Discourse) |
| **Identify sub-forum context** | H | L (undocumented norms) | L (judgment-dependent) | H (varies by sub) | M (may need Discord) | M | H (norm misapplication = user backlash) | L (norms not in system) |
| **Assess tone vs. community standards** | H | L (unstructured text) | L (cultural/linguistic) | H | M | M | H | M (LLM could assist) |
| **Check if critique was invited** | M | M (thread context) | M (implicit vs. explicit) | M | L | M | M | M (thread analysis) |
| **Cross-check account history** | M | M (Tom's sheet + memory) | M | M | H (Tom's sheet not integrated) | M | H (sponsor/IP risk) | L (manual Google Sheets) |
| **Consult peers if uncertain** | H | L (informal Discord) | L (consensus-building) | H | H (async Discord) | M-L | H (consistency risk) | M (Discord not integrated) |
| **Decide action** | H | L | L (judgment call) | H | M | M | H (false negative = viral risk) | n/a |
| **Log decision + rationale** | M | M | M | M | L | M | M (audit trail) | H (Discourse) |

**Delegation suitability**: Low to Medium — high cognitive load, unstructured inputs, judgment-dependent, frequent exceptions, turn-taking (Discord), high false-negative risk. [**Assumption A09, confidence: high** — This is the core bottleneck. Agent could *support* (synthesize context, flag risks), but human judgment is indispensable.]

---

### JtD-4: User Dispute Appeals

| Micro-Task | Cognitive Load | Input Structure | Decision Determinism | Exception Frequency | Turn-Taking | Latency | Risk Sensitivity | Tool Availability |
|------------|----------------|-----------------|---------------------|--------------------|--------------|---------|--------------------|-------------------|
| **Review original moderation action** | M | M (Discourse log) | M | M | L | M | M | H (Discourse API) |
| **Read user appeal** | M | M (structured appeal) | M | M | L | M | M | H (Discourse/email) |
| **Assess new context** | H | L (unstructured) | L (judgment) | H | M | M | H | M |
| **Check policy consistency** | M | M (14-page policy) | M | M | L | M | H (inconsistency = user trust loss) | M (policy not in system) |
| **Decide appeal outcome** | H | L | L | M | M | M | H | n/a |
| **Communicate decision to user** | M | M | M | L | L | M | H (user-facing) | H (Discourse/email) |

**Delegation suitability**: Low to Medium — similar to JtD-3 (judgment-dependent, unstructured context, high risk). [**Assumption A10, confidence: medium** — Agent could draft appeal responses for review, but final decision must be human.]

---

### JtD-5: IP-Claim Resolution

| Micro-Task | Cognitive Load | Input Structure | Decision Determinism | Exception Frequency | Turn-Taking | Latency | Risk Sensitivity | Tool Availability |
|------------|----------------|-----------------|---------------------|--------------------|--------------|---------|--------------------|-------------------|
| **Triage IP-claim email** | M | M (email + attachment) | M | M | L | M-L (days acceptable) | H (legal + PR risk) | M (email parsing) |
| **Check claimant credibility** | H | L (Tom's memory + sheet) | L | H | M (may need legal) | M-L | H | L (manual sheet) |
| **Assess claim merit** | H | L (copyright/TM law) | L | H | H (legal consultation) | M-L | H (legal liability) | L (legal expertise required) |
| **Decide action** | H | L | L | H | H | M-L | H | n/a |
| **Communicate to user + claimant** | M | M | M | M | L | M-L | H (legal record) | H (email) |
| **Escalate to legal if contested** | M | M | M | M | H | L | H | M |

**Delegation suitability**: Low — high cognitive load, legal reasoning, high risk, turn-taking (legal), low tool availability. [**Assumption A11, confidence: high** — IP claims are *human-only* work. Agent could organize claimant history, but judgment is Tom's alone.]

---

## Assumptions Register

| ID | Assumption | Confidence | Rationale | Coach Question ID |
|----|------------|------------|-----------|-------------------|
| **A01** | Team operates at ~47 hrs/day capacity | High | Calculated from volumes + handling times provided | Q01, Q02 |
| **A02** | Handling times are median; no overlap between streams | Medium | Brief states times per case, but doesn't specify variance or concurrent work | Q01, Q02, Q03 |
| **A03** | 14-page policy is baseline; effective moderation requires undocumented layer | High | Artefacts 4.2 and 4.3 explicitly show sub-forum norms and account patterns not in policy | Q05, Q06, Q09 |
| **A04** | Ratio of automated-to-sampled routing is unknown | Medium | Brief states "user flags, automated detection, or moderator sampling" but no proportions | Q04 |
| **A05** | ~30-40% of grey-zone cases involve Discord peer consultation | Medium | Artefact 4.2 shows consultation, but frequency is inferred | Q07 |
| **A06** | IP claims are *always* Tom-reviewed after 2024 incident | High | Artefact 4.3 explicit: "Tom personally reviews every IP claim from @sculpturedragon" | Q10, Q11 |
| **A07** | Tom's Google Sheet is *not* systematically updated for every decision | Medium | Artefact 4.3 shows account-level patterns, not decision-level logs | Q13 |
| **A08** | Routine spam (72% of queue) is reliably classified in ~30 sec | High | Volume + handling time suggests high moderator confidence | Q03, Q04 |
| **A09** | Grey-zone review is the core bottleneck (30 hrs/day of 47 total) | High | Calculated from volumes + handling times; highest cognitive load | Q02, Q05, Q06 |
| **A10** | Agent could draft appeal responses for review, but final decision must be human | Medium | Inferred from risk profile; not explicitly stated | Q14 |
| **A11** | IP claims are *human-only* work; legal + PR risk too high to delegate | High | Artefact 4.3 + Tom's mandate ("false negatives are existential") | Q10, Q11 |
| **A12** | Sub-forum norms are *not* centrally documented | High | Artefact 4.2: "That 'no critique without invitation' is painters-sub-specific. Thread title is literally 'help me figure out what's wrong' so OP invited it." | Q05, Q06, Q09 |
| **A13** | 2024 sponsor incident is the primary driver of Tom's risk aversion | High | Artefact 4.2: "That was the sponsor incident. Different." Artefact 4.3: "@vortex_minis — THE 2024 SPONSOR — never get this wrong" | Q08, Q11 |
| **A14** | Japanese painters sub requires special handling due to language/cultural interpretation | High | Artefact 4.3: "English-language critiques sometimes read harsher than intended... Aki has flagged this; we're learning" | Q09, Q15 |
| **A15** | Volunteer moderators have authority to close grey-zone cases *without* Tom's approval, unless sponsor/IP-sensitive | Medium | Artefact 4.2 shows moderators closing reports independently; Artefact 4.3 shows Tom's escalation rules | Q07, Q12 |
| **A16** | Moderation queue volume (1,500/day) is stable; no seasonal or growth-driven spikes | Low | Brief states "12.5% of posts (~1,500/day)" but no trend data | Q01, Q16 |
| **A17** | Discourse platform has REST APIs; in-house gallery has "limited API surface" | High | Brief explicit: "Discourse (forum platform, self-hosted on AWS, REST APIs)" and "In-house gallery (Rails app, custom; limited API surface)" | Q17 |
| **A18** | Volunteer moderator retention is stable; no burnout or turnover concerns | Low | Not mentioned in brief or artefacts; critical for long-term viability | Q18 |
| **A19** | Sponsor content moderation errors are higher-risk than user content errors | High | Artefact 4.3: "@vortex_minis — Sponsor account; commercial-content posts — Tom personally reviews; do not auto-flag as commercial-spam — THE 2024 SPONSOR — never get this wrong" | Q08, Q11 |
| **A20** | Tom's Google Sheet is shared only with Senior Moderator, not volunteers | High | Artefact 4.3 explicit: "Shared with the senior moderator only; not in the volunteer Discord." | Q12, Q13 |

---

## Key Findings

### 1. **Grey-zone review is the cognitive bottleneck**
- **30 hrs/day** of the 47-hour total workload (64% of effort)
- **360 cases/day** at **5 min/case**
- Requires sub-forum norms (undocumented), account history (Tom's manual sheet), prior-incident awareness, cultural/linguistic interpretation, and Discord peer consultation
- **Non-deterministic**: "invited critique" is *implied*, not explicit; tone is *contextual*, not absolute

### 2. **Lived process is *not* the documented process**
- 14-page global policy is the *baseline*, but effective moderation lives in:
  - **Sub-forum-specific norms** (not documented centrally)
  - **Account-level patterns** (Tom's Google Sheet, shared only with Senior Moderator)
  - **Prior-incident sensitivity** (2024 sponsor incident shapes risk tolerance)
  - **Volunteer institutional memory** (Discord #mod-decisions, not Discourse)

### 3. **Tom is the single point of failure for high-risk cases**
- Every IP claim routed to Tom after 2024 incident
- Sponsor-related cases Tom-reviewed (not delegated to volunteers)
- High-profile sculptor accounts Tom-reviewed
- Appeals involving Tom's original decisions Tom-reviewed
- [**Assumption A21, confidence: high** — Tom's workload is unknown but growing; potential burnout risk.]

### 4. **False-negative risk dominates decision-making**
- "False positives are survivable; one viral false negative is existential" [Tom's mandate]
- 2024 sponsor incident is *the* reference case ("never get this wrong")
- Escalation rules prioritize *avoiding* false negatives over efficiency (Tom personally reviews every IP claim, every sponsor case)

### 5. **Volunteer coordination is informal and async**
- Discord #mod-decisions is the *actual* decision-making space, not Discourse
- Consensus-building takes time (async, timezone-distributed)
- No formal SLA for peer consultation [**Assumption A22, confidence: medium** — grey-zone decision latency is unknown; could be hours to days depending on volunteer availability]

### 6. **Delegation suitability varies dramatically by stream**

| Stream | Daily Volume | Daily Effort | Delegation Suitability | Rationale |
|--------|--------------|--------------|------------------------|-----------|
| Routine spam / clear violations | 1,080 | 9 hrs | **High** | Deterministic, low-risk, structured |
| Grey-zone case review | 360 | 30 hrs | **Low to Medium** | High cognitive load, judgment-dependent, undocumented norms, false-negative risk |
| User dispute appeals | 60 | 8 hrs | **Low to Medium** | Similar to grey-zone; policy consistency + user trust |
| IP-claim resolution | 3-5/wk | Variable | **Low (Human Only)** | Legal reasoning, PR risk, Tom-exclusive |

**Opportunity**: Routine spam (9 hrs/day) is agent-suitable. Grey-zone (30 hrs/day) is *agent-supported* (context synthesis, risk flagging) but *human-decided*.

### 7. **Tool/data availability is fragmented**
- **Discourse**: REST APIs available (moderation actions, post content, user reports)
- **In-house gallery**: Rails app, "limited API surface" [**Assumption A17**]
- **Tom's Google Sheet**: Manual, not integrated with Discourse or gallery [**Assumption A23, confidence: high** — integrating Tom's sheet into moderation workflow would reduce context-switching]
- **Discord**: Volunteer coordination happens *outside* the moderation platform [**Assumption A24, confidence: high** — Discord is not integrated with Discourse; peer consultation is fully manual]
- **Email**: IP-claim correspondence is *separate* from Discourse/gallery moderation [**Assumption A25, confidence: medium** — IP-claim workflow could be semi-automated if email parsing + Discourse integration is built]

### 8. **Compliance/risk sensitivity is implicit, not codified**
- No formal risk-scoring framework
- No audit trail requirement mentioned [**Assumption A26, confidence: low** — legal/regulatory constraints are unknown; UK platform, user-generated content, potential Online Safety Act implications]
- Tom's Google Sheet is *not* backed up or version-controlled [**Assumption A27, confidence: medium** — Tom's sheet is business-critical but fragile]

---

## Next Steps (for Coach Role-Play)

**Critical questions to elicit**:
1. What is Tom's current workload breakdown? (IP claims, sponsor reviews, appeals, volunteer coordination)
2. What was the 2024 sponsor incident, and what specifically changed afterward?
3. How are sub-forum norms currently maintained and communicated to new volunteer moderators?
4. What is volunteer moderator turnover/burnout rate?
5. What legal/regulatory constraints apply to MiniBase moderation? (UK Online Safety Act, GDPR, libel)
6. What happens when Tom is unavailable? (vacation, illness, timezone gaps)
7. How often do volunteer moderators disagree on grey-zone cases, and how is consensus reached?
8. What is the current IP-claim false-positive rate? (dismissed vs. upheld claims)
9. Are there sub-forum moderators with specialized knowledge? (painters sub norms, historical sub imagery sensitivity)
10. What data/metrics does Tom use to evaluate moderation quality? (appeal rate, user complaints, sponsor feedback)

**See**: `scenario4-discovery-questions.md` for full coach role-play question set.
