# Discovery Questions — Scenario 4: Community Content Moderation
## Coach Role-Play Questions for Tom Włodarczyk

---

## Purpose

These questions target **design-changing** information — insights that would materially alter delegation boundaries, agent architecture, tool integration priorities, or risk-mitigation strategies. They are structured to elicit **lived practice**, **prior automation history**, **system edge cases**, and **stakeholder priorities**.

Each question maps to one or more assumptions in the Cognitive Load Map. Generic questions avoided.

---

## Category 1: Tom's Workload & Escalation Patterns

### Q01: Tom's Personal Workload Breakdown
**Question**: "Walk me through your last full working day. What percentage of your time went to: (a) IP-claim triage, (b) sponsor-related post reviews, (c) appeal escalations from volunteers, (d) volunteer coordination, (e) policy/norm updates, (f) other?"

**Why this matters**: Tom is the single point of failure for high-risk decisions. If his workload is unsustainable or growing faster than queue volume, delegation strategy must prioritize *reducing Tom's load* over optimizing volunteer efficiency.

**Assumption closure**: A21 (Tom's workload unknown; burnout risk)

---

### Q02: Escalation Volume & Latency
**Question**: "How many grey-zone cases escalate to you per day, on average? What's your typical response time when a volunteer pings you in Discord or flags something in Discourse? Are there cases where you're the bottleneck?"

**Why this matters**: If Tom is swamped with escalations, agent priority should be *pre-filtering* cases that don't need his review (e.g., "this looks like painters-sub norm, not sponsor-risk"). If Tom responds quickly, escalation latency isn't the problem — volunteer decision confidence is.

**Assumption closure**: A05 (unknown escalation frequency), A22 (unknown decision latency)

---

### Q03: Routine Spam Handling Time Variance
**Question**: "The brief says routine spam takes ~30 seconds per case. Is that consistent, or do some 'obvious spam' cases take longer because they're borderline? What percentage of the 1,080 daily 'routine' cases actually require more than 1 minute?"

**Why this matters**: If "routine spam" is only truly routine for 80% of cases, the remaining 20% (~216/day) may be mis-categorized grey-zone cases, inflating both streams. This changes volume assumptions and agent design (need better triage, not just spam removal).

**Assumption closure**: A02 (handling time variance), A08 (spam classification confidence)

---

## Category 2: The 2024 Sponsor Incident & Risk Tolerance

### Q04: What Happened in the 2024 Sponsor Incident?
**Question**: "The artefacts mention 'THE 2024 SPONSOR' incident multiple times. What specifically happened with @vortex_minis? What was the consequence (user backlash, revenue loss, founder intervention)? What changed in your moderation approach afterward?"

**Why this matters**: This incident defines Tom's risk tolerance. If the consequence was revenue loss (sponsor threatened to pull funding), agent design must prioritize *sponsor-content protection* over efficiency. If it was a false-positive (sponsor wrongly flagged as spam), agent must be tuned for *high recall* on sponsor accounts. The design changes depending on the failure mode.

**Assumption closure**: A13 (2024 incident is primary driver of risk aversion), A19 (sponsor errors are higher-risk than user errors)

---

### Q05: Are There Other High-Risk Accounts Beyond Sponsors?
**Question**: "Your Google Sheet lists @sculpturedragon (recurring IP claims) and @vortex_minis (sponsor). Are there other account types or users that get the same 'Tom personally reviews' treatment? How many total accounts are on your 'high-risk' list?"

**Why this matters**: If Tom has a dozen high-risk accounts, agent can hard-code escalation rules. If he has *hundreds*, we need a pattern-detection system (e.g., "high-profile sculptor = >10K followers + >5 IP claims in 12 months"). The design changes from rule-based to heuristic.

**Assumption closure**: A06 (IP claims always Tom-reviewed), A20 (Google Sheet shared only with Senior Moderator)

---

## Category 3: Sub-Forum Norms & Undocumented Knowledge

### Q06: How Are Sub-Forum Norms Created & Maintained?
**Question**: "The Discord thread mentions 'painters sub has the no critique without invitation thing' — but it's not in the global policy. How did that norm emerge? Who decides when a new sub-forum norm is adopted? How do new volunteer moderators learn these norms?"

**Why this matters**: If sub-forum norms are emergent (volunteer consensus over time), agent can't rely on a static rulebook — it needs to *learn* norms from moderation logs. If norms are top-down (Tom or sub-forum lead decides), agent needs a structured norm repository. The design changes from ML-based to rule-based.

**Assumption closure**: A03 (undocumented norms layer), A12 (sub-forum norms not centrally documented)

---

### Q07: How Often Do Volunteers Disagree on Grey-Zone Cases?
**Question**: "When two volunteers disagree in Discord on a grey-zone case, what happens? Do you tie-break? Does the majority rule? Are there cases where disagreement signals 'this needs Tom' vs. 'we'll pick the safer call'?"

**Why this matters**: If disagreement is rare (<5% of grey-zone cases), volunteers are well-calibrated — agent design can trust volunteer consensus. If disagreement is common (>20%), agent needs to *surface* disagreement early (e.g., "this post has high norm-ambiguity score; suggest Discord check before action"). The design changes from post-decision logging to pre-decision flagging.

**Assumption closure**: A05 (peer consultation frequency), A15 (volunteer authority boundaries), A22 (decision latency)

---

### Q08: Which Sub-Forums Are the Hardest to Moderate?
**Question**: "If I asked each volunteer 'which sub-forum gives you the most grey-zone headaches?', what would they say? Is it painters (critique norms), historical (controversial imagery), Japanese painters (language/cultural), or something else?"

**Why this matters**: Agent effort should focus on the *highest cognitive-load sub-forums*, not uniform across all 14. If painters sub is 50% of grey-zone cases, agent should prioritize painters-norm context synthesis. If Japanese painters is only 5% but has the highest risk of cultural misinterpretation, agent needs specialized handling there.

**Assumption closure**: A14 (Japanese painters sub special handling), Q09 (sub-forum-specific delegation strategy)

---

## Category 4: Automation History & Prior Attempts

### Q09: What Automation Has MiniBase Tried Before?
**Question**: "Has MiniBase tried any automated moderation tools before — keyword filters, sentiment analysis, third-party moderation APIs? If yes, what happened? If no, why not?"

**Why this matters**: If prior automation failed (e.g., keyword filter flagged legitimate critique as harassment), Tom will be skeptical of agent-based moderation — we need to address that specific failure mode. If no prior attempts, we have a blank slate but also no organizational learning. The design changes from "fix what broke last time" to "start with trust-building pilot."

**Assumption closure**: (No direct assumption, but shapes stakeholder buy-in strategy)

---

## Category 5: IP-Claim Resolution Workflow

### Q10: What Percentage of IP Claims Are Upheld vs. Dismissed?
**Question**: "Of the 3-5 IP claims you review each week, roughly how many result in: (a) takedown (claim upheld), (b) dismissal (claim rejected), (c) escalation to legal (contested)? Are there serial claimants who submit frivolous claims?"

**Why this matters**: If 80% of claims are frivolous (@vintage_kitbasher pattern), agent can *pre-triage* low-credibility claims, saving Tom time. If 80% are upheld, Tom's review is finding real issues — agent should focus on *organizing evidence* (claimant history, prior takedowns, similar claims), not pre-filtering. The design changes from triage to synthesis.

**Assumption closure**: A06 (IP claims always Tom-reviewed), A11 (IP claims are human-only work)

---

### Q11: What Triggers Legal Escalation on an IP Claim?
**Question**: "When you escalate an IP claim to legal, what are you looking for? Is it 'claim is contested and high-value' or 'claim involves trademark law and I'm not qualified' or 'claimant is litigious and we need coverage'?"

**Why this matters**: If escalation criteria are codifiable (e.g., "claim value >£5K OR claimant has prior litigation history"), agent can *prepare legal escalation packages* automatically (gather evidence, draft summary, flag risk factors). If criteria are intuitive ("I know it when I see it"), agent can't pre-filter — but it can still organize case materials to speed Tom's review.

**Assumption closure**: A11 (IP claims are human-only work; legal reasoning required)

---

## Category 6: Volunteer Moderator Dynamics

### Q12: How Do You Share Your Google Sheet Knowledge with Volunteers?
**Question**: "Your Google Sheet is shared only with the Senior Moderator. When a volunteer moderator reviews a post from @sculpturedragon (recurring IP claims), do they know that history? Or do they ping you in Discord and you fill them in?"

**Why this matters**: If volunteers lack context, they're flying blind — agent should surface account history *to volunteers* during review (e.g., "This user has 3 prior IP claims; Tom reviews all their posts"). If Tom intentionally shields volunteers from sensitive account data (privacy, volunteer trust), agent needs role-based access controls. The design changes from shared-context to tiered-access.

**Assumption closure**: A20 (Google Sheet shared only with Senior Moderator), A07 (sheet not systematically updated)

---

### Q13: How Do You Update Your Google Sheet? Is It Ad Hoc or Systematic?
**Question**: "When you add a new account to your 'high-risk' tracker (like @sculpturedragon or @vortex_minis), what triggers that? Is it 'I noticed a pattern after 3 incidents' or 'founder told me to watch this account' or something else? Do you ever remove accounts from the tracker?"

**Why this matters**: If updates are ad hoc, Tom's sheet is a **fragile single point of failure** — agent needs to *replicate* this pattern-detection (e.g., "user has 3 IP claims in 30 days → auto-flag for Tom's review"). If updates are systematic, agent can codify the rules. The design changes from reactive flagging to proactive pattern-detection.

**Assumption closure**: A07 (sheet not systematically updated), A23 (integrating sheet would reduce context-switching)

---

### Q14: What's Volunteer Moderator Turnover Like?
**Question**: "How long do volunteer moderators typically stay active? Are you constantly onboarding new volunteers, or is the team stable? What causes volunteers to leave (burnout, life changes, community drama)?"

**Why this matters**: If turnover is high (>30% per year), agent should prioritize *onboarding support* (e.g., "here's what painters-sub norms look like in practice; here are 10 example grey-zone cases with rationale"). If turnover is low, agent should optimize *experienced moderator efficiency* (context synthesis, not training wheels). The design changes from education to acceleration.

**Assumption closure**: A18 (volunteer retention unknown)

---

## Category 7: Volume, Growth & Seasonal Patterns

### Q15: Is the 1,500/day Queue Volume Stable or Growing?
**Question**: "The brief says ~1,500 posts/day enter the moderation queue (12.5% of 12K daily posts). Is that consistent year-round, or are there spikes (conventions, new game releases, holiday seasons)? Has it grown over the past year as the platform grows?"

**Why this matters**: If volume is stable, agent design can optimize for *current throughput*. If volume is growing 20% YoY, agent design must *scale ahead of demand* (e.g., "fully automate routine spam now, because it'll be 1,300 cases/day next year"). If there are seasonal spikes (2x volume during convention season), agent needs *burst capacity* planning. The design changes from static to adaptive.

**Assumption closure**: A16 (queue volume stability unknown)

---

### Q16: Are There Time-of-Day or Day-of-Week Patterns in Grey-Zone Cases?
**Question**: "Do grey-zone cases bunch up at certain times — evenings when more users are online, weekends when volunteers are slower to respond, or timezone gaps between your US and Japan moderators?"

**Why this matters**: If grey-zone cases spike at night (UK time) when volunteer coverage is thin, agent should prioritize *async context synthesis* (prepare case summaries overnight so morning moderators can decide quickly). If cases are evenly distributed, agent design can assume real-time review. The design changes from batch-prep to real-time assist.

**Assumption closure**: A22 (decision latency unknown; timezone dynamics unclear)

---

## Category 8: Tool Integration & Data Access

### Q17: What Does "Limited API Surface" Mean for the In-House Gallery?
**Question**: "The brief says your Rails gallery app has 'limited API surface.' What can you *not* do via API that would help moderation? Is it read-only access, or are writes also blocked? Can you add API endpoints, or is the codebase unmaintained?"

**Why this matters**: If gallery API is read-only, agent can *retrieve* gallery posts for review but can't *act* (remove, flag). If no API exists, agent design must work around it (Discourse-only for now; gallery later). If API can be extended, that's a platform investment decision. The design changes from workaround to roadmap.

**Assumption closure**: A17 (Discourse has APIs; gallery API limited), A25 (IP-claim workflow could be semi-automated with email parsing)

---

### Q18: How Is IP-Claim Email Currently Parsed?
**Question**: "When a sculptor sends an IP claim via email, do you manually copy-paste the claim details into Discourse or your Google Sheet? Or is there a standard email template claimants use? How much time do you spend just organizing IP-claim correspondence?"

**Why this matters**: If IP-claim emails are structured (standard template), agent can *auto-parse* and populate a case record (claimant name, claimed work, user accused, evidence links). If emails are free-form, agent needs NLP extraction. If Tom is spending 10 min/case just organizing emails, that's low-hanging automation fruit. The design changes from judgment-support to admin-reduction.

**Assumption closure**: A25 (email parsing for IP claims)

---

## Category 9: Compliance, Risk & Audit

### Q19: What Legal or Regulatory Constraints Apply to MiniBase Moderation?
**Question**: "Does MiniBase have legal obligations under the UK Online Safety Act, GDPR, or other regulations? Do you keep moderation decision audit trails for legal reasons, or just operational reasons? Has MiniBase ever faced a legal challenge from a user whose content was removed?"

**Why this matters**: If Online Safety Act applies (likely, given UK incorporation + user-generated content), agent design must include *auditability* (every decision logged with rationale, human-in-loop for high-risk removals). If no formal compliance requirement, agent can prioritize speed over audit trails. The design changes from compliance-first to efficiency-first.

**Assumption closure**: A26 (legal/regulatory constraints unknown)

---

### Q20: What Metrics Does Tom Use to Evaluate Moderation Quality?
**Question**: "How do you know if moderation is working well? Do you track appeal rate, user complaints, sponsor feedback, volunteer moderator consistency, or something else? What would 'success' look like for an AI-assisted moderation system?"

**Why this matters**: If Tom tracks appeal rate (currently ~4% of queue = 60/day), agent success = *reduce appeals without increasing false negatives*. If Tom tracks volunteer consistency (inter-moderator agreement), agent success = *surface norm conflicts early*. If Tom tracks sponsor satisfaction, agent success = *zero sponsor false positives*. The design optimizes for Tom's actual success metric, not a generic "reduce handling time."

**Assumption closure**: (No direct assumption, but defines agent success criteria)

---

## Summary: Question-to-Assumption Mapping

| Question | Primary Assumptions Targeted |
|----------|------------------------------|
| Q01 | A21 (Tom's workload/burnout) |
| Q02 | A05 (escalation frequency), A22 (latency) |
| Q03 | A02 (handling time variance), A08 (spam confidence) |
| Q04 | A13 (2024 incident), A19 (sponsor risk) |
| Q05 | A06 (IP always Tom), A20 (Google Sheet access) |
| Q06 | A03 (undocumented norms), A12 (sub-forum norms) |
| Q07 | A05 (peer consultation), A15 (volunteer authority), A22 (latency) |
| Q08 | A14 (Japanese painters), sub-forum delegation strategy |
| Q09 | Prior automation history (stakeholder buy-in) |
| Q10 | A06 (IP always Tom), A11 (IP human-only) |
| Q11 | A11 (legal reasoning required) |
| Q12 | A20 (Google Sheet access), A07 (sheet updates) |
| Q13 | A07 (sheet updates), A23 (sheet integration) |
| Q14 | A18 (volunteer retention) |
| Q15 | A16 (volume stability) |
| Q16 | A22 (decision latency; timezone dynamics) |
| Q17 | A17 (API availability), A25 (email parsing) |
| Q18 | A25 (IP-claim email workflow) |
| Q19 | A26 (compliance constraints) |
| Q20 | Agent success criteria (design optimization target) |

---

## Usage Notes

- Bring **3-5 questions per coach interaction** (office hours, mid-week checkpoint, squad sessions)
- Prioritize questions that **materially change your design** (not just fill in details)
- After each answer, **update assumptions** in the Cognitive Load Map with confidence level adjustments
- If coach answer is "I don't know" or "that's not how we think about it," that's valuable data — it signals where operational reality diverges from engineering assumptions
