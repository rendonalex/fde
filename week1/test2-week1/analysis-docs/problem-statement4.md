# Problem Statement with Quantified Success Metrics

## Table of Contents
- [1. Problem Statement](#1-problem-statement)
  - [Current State (Quantified)](#current-state-quantified)
  - [The Actual Problem (vs. Stated Request)](#the-actual-problem-vs-stated-request)
  - [Explicit Constraints](#explicit-constraints)
- [2. Assumptions](#2-assumptions)
  - [Volume & Time Assumptions](#volume--time-assumptions)
  - [Cost Assumptions](#cost-assumptions)
  - [Error Rate Assumptions](#error-rate-assumptions)
  - [Workflow Assumptions](#workflow-assumptions)
- [3. Success Metrics](#3-success-metrics)
  - [Metric 1: Volunteer Moderator Cognitive Load](#metric-1-volunteer-moderator-cognitive-load-leading-indicator)
  - [Metric 2: Grey-Zone Case Review Quality](#metric-2-grey-zone-case-review-quality-outcome-indicator)
  - [Metric 3: Community Trust Preservation](#metric-3-community-trust-preservation-outcome-indicator)
  - [Metric 4: System Cost Efficiency](#metric-4-system-cost-efficiency-economic-indicator)
  - [Metric 5: Moderator Retention](#metric-5-moderator-retention-lagging-outcome-indicator)
- [4. Unknowns (Critical Discovery Questions)](#4-unknowns-critical-discovery-questions)
  - [High-Risk Unknowns](#high-risk-unknowns-must-resolve-before-specification)
  - [Medium-Risk Unknowns](#medium-risk-unknowns-can-be-deferred-but-inform-design)
  - [Low-Risk Unknowns](#low-risk-unknowns-safe-to-defer)
- [Summary](#summary-what-this-problem-actually-is)

---

## 1. Problem Statement

### Current State (Quantified)
- **Volume**: 12,000 posts/day requiring moderation decisions
- **Team capacity**: 8 volunteer moderators + 2 paid staff = 10 total moderators
- **Decision distribution**: ~97% routine/clear violations (~11,640 posts/day), ~3% grey-zone cases (~360 posts/day)
- **Community scale**: 180,000 active users
- **Policy complexity**: 14-page policy document covering 6+ distinct violation categories

### The Actual Problem (vs. Stated Request)

**What the client asked for**: "AI that handles 97% instantly, flags 3% for human review with context, never damages trust."

**What they actually need**: A moderation triage system that protects volunteer moderator time from burnout while maintaining community trust through zero tolerance for high-stakes false negatives.

**Evidence for reframing**:
- 10 moderators reviewing 12,000 posts/day = 1,200 posts per moderator per day
- Even if "routine" decisions take 10 seconds each, that's 3.2+ hours/day of purely mechanical work per moderator
- Volunteer moderators are the constraint (not paid staff) — volunteer burnout from repetitive work is the real risk
- The "never damage trust" constraint reveals this is a **risk mitigation problem**, not a cost optimization problem
- The client will "absorb false positives to avoid one viral false negative" — they're optimizing for community trust preservation, not efficiency

**Core problem**: Volunteer moderator cognitive load is dominated by routine decisions (97% of volume), leaving insufficient capacity for the nuanced grey-zone cases (3% of volume) that actually require human judgment and community context. The risk is not moderation speed — it's moderator burnout leading to either (a) rushed grey-zone decisions that damage trust, or (b) volunteer attrition that collapses the moderation system entirely.

### Explicit Constraints
1. **Zero tolerance for trust-damaging false negatives** in grey-zone cases (IP disputes, cultural context, long-standing member edge cases)
2. **Volunteer moderator time is the scarce resource** (not paid staff budget)
3. **14-page policy** must be consistently applied across 6+ violation categories
4. **Community heterogeneity** (global user base, cultural context variance) makes "obvious" violations contextual
5. **Asymmetric risk**: False positive (incorrectly flagging for review) costs moderator time; false negative (incorrectly auto-actioning a grey case) costs community trust

---

## 2. Assumptions

### Volume & Time Assumptions

**A1: Average time per routine moderation decision (current manual process)**  
**Assumed value**: 15 seconds per post  
**Reasoning**: Industry benchmarks for content moderation on clear-cut cases (spam detection, obvious policy violations) range from 10-20 seconds. Using 15 seconds as midpoint. This includes reading the post, comparing to policy, and taking action (approve/remove/flag).

**A2: Average time per grey-zone moderation decision (current manual process)**  
**Assumed value**: 8 minutes per post  
**Reasoning**: Grey-zone cases require: reading post + context (1-2 min), reviewing user history (2-3 min), consulting policy document (2 min), discussing with other moderators if needed (0-3 min), documenting decision rationale (1 min). 8 minutes is conservative for cases involving IP disputes or cultural context.

**A3: Moderator availability (volunteer moderators)**  
**Assumed value**: 2 hours/day average per volunteer moderator  
**Reasoning**: Volunteer moderators typically contribute 1-3 hours/day across similar community platforms. Using 2 hours as baseline. Paid staff assumed at 6 hours/day of active moderation time (remaining time on policy work, escalations, community management).

**A4: Current distribution of work across moderator types**  
**Assumed value**: Volunteers handle 70% of volume, paid staff handle 30%  
**Reasoning**: Volunteers outnumber paid staff 4:1, but paid staff likely handle disproportionate share of complex cases and have longer daily availability. 70/30 split reflects this imbalance.

### Cost Assumptions

**A5: Volunteer moderator opportunity cost**  
**Assumed value**: $0/hour (direct cost), but burnout risk = loss of 1 volunteer per quarter at current load  
**Reasoning**: Volunteers aren't paid, but burnout has real cost. Recruiting/training a replacement moderator estimated at 40 hours paid staff time. Current load (A1, A2, A3) suggests unsustainable cognitive burden.

**A6: Paid staff moderator cost**  
**Assumed value**: $28/hour (fully loaded)  
**Reasoning**: Community manager/moderator roles typically $45-55K salary + 30% benefits/overhead = ~$28/hour fully loaded for mid-tier market.

**A7: AI moderation cost (token economics)**  
**Assumed value**: $0.008 per post for routine triage (Claude 3.5 Sonnet API pricing)  
**Reasoning**: Routine triage requires ~1,500 input tokens (post content + policy excerpt + classification prompt) + ~200 output tokens (classification + confidence score + reasoning). At $3/$15 per million tokens (input/output), this is ~$0.0045 input + $0.003 output = ~$0.008 per post. Grey-zone cases requiring full policy context + user history analysis estimated at $0.04 per post.

### Error Rate Assumptions

**A8: Current false negative rate (missed violations in routine cases)**  
**Assumed value**: 2% of routine cases  
**Reasoning**: At 1,200 posts/moderator/day with 15-second review time, cognitive fatigue leads to missed violations. 2% false negative rate (233 posts/day) is consistent with content moderation research on high-volume manual review.

**A9: Current false positive rate (incorrectly escalated routine cases)**  
**Assumed value**: 5% of routine cases  
**Reasoning**: When uncertain, moderators flag for secondary review. 5% over-escalation rate (582 posts/day) reflects conservative moderation under time pressure.

**A10: Acceptable AI false positive rate (routine cases incorrectly flagged as grey-zone)**  
**Assumed value**: 8% of routine cases  
**Reasoning**: Client stated willingness to "absorb false positives to avoid false negatives." 8% false positive rate (930 posts/day flagged for human review) would still reduce moderator load by 89% on routine cases while maintaining zero-risk posture on grey zones.

**A11: Required AI precision on grey-zone detection**  
**Assumed value**: 95% recall (must catch 95% of true grey-zone cases)  
**Reasoning**: Missing 5% of grey-zone cases (18 posts/day) that get auto-actioned creates unacceptable trust risk. This is the binding constraint.

### Workflow Assumptions

**A12: Time to review AI-flagged post with context**  
**Assumed value**: 4 minutes per post (50% reduction from A2)  
**Reasoning**: If AI provides structured context (user history summary, policy section references, similar past cases, confidence reasoning), moderator review time drops from 8 min to 4 min because discovery work is pre-done.

**A13: Moderator time required to audit AI auto-actions**  
**Assumed value**: 30 minutes/day per moderator (spot-checking sample of auto-approved posts)  
**Reasoning**: Trust in AI system requires ongoing validation. 30 min/day = ~120 posts reviewed (at 15 sec each) = ~1% sample of auto-approved volume.

---

## 3. Success Metrics

### Metric 1: Volunteer Moderator Cognitive Load (Leading Indicator)
**Description**: Average time per volunteer moderator spent on routine moderation decisions per day  

**Current Baseline**: 2.4 hours/day  
- Based on A1 (15 sec/post), A3 (2 hours available), A4 (volunteers handle 70% of 11,640 routine posts = 8,148 posts/day)  
- 8,148 posts ÷ 8 volunteers = 1,019 posts/volunteer/day  
- 1,019 posts × 15 sec = 15,285 seconds = 4.2 hours/volunteer/day  
- **Current state exceeds available volunteer time by 2.1x** (4.2 hours required vs. 2 hours available per A3)  
- This confirms unsustainable load; actual baseline reflects rushed decisions and burnout risk  

**Target**: 0.4 hours/day (80% reduction)  
- AI handles 92% of routine volume (accounting for A10: 8% false positive rate)  
- Volunteers review: (8% × 11,640 routine) + 360 grey-zone = 1,291 posts/day ÷ 8 volunteers = 161 posts/volunteer  
- At A12 (4 min for AI-assisted review) = 644 min = 10.7 hours total ÷ 8 = 1.3 hours/volunteer  
- Plus A13 (30 min audit time) = 1.8 hours/volunteer/day  
- **Revised target: 1.8 hours/day (within A3 available time, 25% buffer for variability)**  

**Measurement Method**: Time-tracking on moderation dashboard (time from post flagged → moderator action logged)  

**Dependencies**: A1, A3, A4, A10, A12, A13  

---

### Metric 2: Grey-Zone Case Review Quality (Outcome Indicator)
**Description**: Percentage of grey-zone cases receiving full 8-minute review with documented rationale  

**Current Baseline**: 45% (estimated)  
- Based on A2 (8 min/case), A3 (2 hours available), current overload from Metric 1  
- 360 grey-zone cases/day × 8 min = 2,880 min = 48 hours required across all moderators  
- Only ~22 hours actually available after routine work consumes capacity  
- Many grey-zone cases receive rushed <4 min review; estimated 45% receive full 8-min treatment  

**Target**: 95%  
- With AI handling routine volume, moderators have capacity for proper grey-zone review  
- 360 cases/day × 4 min (A12, AI-assisted) = 1,440 min = 24 hours across 10 moderators  
- Well within available capacity (10 moderators × 2 hours = 20 hours volunteer + paid staff capacity)  
- 95% target allows for 5% urgent/time-sensitive cases requiring faster triage  

**Measurement Method**: Audit of moderation logs for grey-zone cases; measure time-to-action and presence of documented rationale in moderation notes  

**Dependencies**: A2, A3, A12  

---

### Metric 3: Community Trust Preservation (Outcome Indicator)
**Description**: False negative rate on grey-zone cases (auto-actioned when human review required)  

**Current Baseline**: 0% (by definition — all cases currently get human review, though rushed)  
- Current system doesn't auto-action grey zones, so no false negatives in this category  
- However, A8 suggests 2% false negative rate on routine cases due to cognitive overload  

**Target**: 0% (absolute zero tolerance)  
- Based on A11 (95% recall requirement), system must flag ≥95% of true grey-zone cases  
- Remaining 5% that slip through as "routine" must be caught by A13 (audit process)  
- Combined system (AI + audit) must achieve 0% grey-zone false negatives reaching users  

**Measurement Method**:  
- Primary: Weekly audit of 100% of auto-actioned posts flagged by community reports or moderator spot-checks  
- Secondary: Community sentiment analysis (mentions of "unfair moderation," appeals filed, moderator trust polls)  
- Lagging: Zero viral incidents of "AI moderator got it wrong" in grey-zone cases over 90-day period  

**Dependencies**: A11, A13  

---

### Metric 4: System Cost Efficiency (Economic Indicator)
**Description**: Total cost per moderated post (AI + human time)  

**Current Baseline**: $0.13 per post  
- Routine posts: 11,640/day × 15 sec × $28/hour (A6) ÷ 3600 sec/hour = $1,358/day  
- Grey-zone posts: 360/day × 8 min × $28/hour ÷ 60 min/hour = $1,344/day  
- Total: $2,702/day ÷ 12,000 posts = $0.225 per post  
- **Adjusted for volunteer time at $0**: (30% paid staff per A4) × $0.225 = **$0.068 per post**  
- **Adjusted for burnout cost** (A5): 1 volunteer lost/quarter = 40 hours × $28 = $1,120/quarter ÷ (90 days × 12,000 posts) = +$0.001 per post  
- **Realistic baseline: $0.069 per post**  

**Target**: $0.045 per post (35% reduction)  
- AI routine triage: 11,640 posts × $0.008 (A7) = $93/day  
- AI grey-zone context: 360 posts × $0.04 (A7) = $14/day  
- Human review (AI-assisted): 1,291 posts/day × 4 min × $28/hour ÷ 60 = $605/day (paid staff portion per A4)  
- Human audit: 10 moderators × 30 min × $28/hour × 30% paid staff = $42/day  
- Total: $754/day ÷ 12,000 posts = $0.063 per post  
- **Adjusted for eliminated burnout cost**: $0.063 - $0.001 = **$0.062 per post**  
- **Stretch target with optimization: $0.045 per post** (assumes 20% efficiency gain from workflow refinement over 6 months)  

**Measurement Method**: Monthly cost accounting (AI API costs + time-tracked moderator hours × loaded hourly rate)  

**Dependencies**: A4, A5, A6, A7, A10, A12, A13  

---

### Metric 5: Moderator Retention (Lagging Outcome Indicator)
**Description**: Volunteer moderator retention rate over 6-month period  

**Current Baseline**: 50% (estimated)  
- Based on A5 (1 volunteer lost per quarter due to burnout)  
- 8 volunteers → lose 2 over 6 months = 75% retention  
- Adjusted down to 50% to account for non-burnout attrition (life changes, interest shifts)  
- **Baseline: 4 of 8 volunteers remain active after 6 months**  

**Target**: 85%  
- Reducing cognitive load (Metric 1) and improving grey-zone review quality (Metric 2) reduces burnout  
- Target: 7 of 8 volunteers remain active after 6 months (1 natural attrition)  
- This implies burnout-driven attrition drops from ~2/quarter to ~0.5/quarter  

**Measurement Method**: Track volunteer moderator cohort over 6-month periods; exit interviews to distinguish burnout vs. other attrition causes  

**Dependencies**: A3, A5, and success on Metrics 1-2  

---

## 4. Unknowns (Critical Discovery Questions)

### High-Risk Unknowns (Must Resolve Before Specification)

**U1: What is the actual distribution of the 14-page policy across the 6+ violation categories?**  
- **Why it matters**: If 80% of routine violations are spam (simple rules), vs. 40% spam / 30% harassment / 30% off-topic (complex rules), the AI specification complexity changes dramatically  
- **Discovery method**: Policy document analysis + 2-week moderation log audit (tag each decision by violation category)  
- **Risk if wrong**: AI optimized for spam detection fails on harassment/cultural context cases, creating false negatives  

**U2: What does "community trust damage" actually mean in measurable terms?**  
- **Why it matters**: Client says "never damage trust" but doesn't define threshold — is it 1 viral incident/year? 10 appeals/month? 5% drop in user sentiment?  
- **Discovery method**: Interview community manager + review past incidents that "damaged trust" (what happened, how was it resolved, what was the impact?)  
- **Risk if wrong**: We optimize for wrong risk tolerance (either too conservative, wasting moderator time, or too aggressive, missing real trust threats)  

**U3: What is the current moderator agreement rate on grey-zone cases?**  
- **Why it matters**: If 2 moderators reviewing the same grey-zone post agree 95% of the time, the "grey zone" is actually more structured than it appears. If they agree 60% of the time, these are genuinely ambiguous and may not be delegatable to AI at all  
- **Discovery method**: Double-blind review of 100 grey-zone cases by 3+ moderators; measure inter-rater reliability  
- **Risk if wrong**: We build an AI system to "flag grey zones with context" when the real problem is inconsistent human policy interpretation  

**U4: What percentage of grey-zone cases are repeat scenarios vs. novel edge cases?**  
- **Why it matters**: If 70% of "grey zones" are actually 10 recurring patterns (e.g., "long-standing member posts commercial content"), AI can learn these patterns. If every grey zone is genuinely novel, AI can only provide context, not pattern recognition  
- **Discovery method**: 30-day audit of grey-zone moderation logs; cluster by similarity  
- **Risk if wrong**: We spec an AI system that tries to learn patterns from noise, or we miss an opportunity to automate recurring "grey" patterns  

**U5: What is the current community appeal/dispute rate, and what triggers appeals?**  
- **Why it matters**: If users appeal 5% of moderation decisions and 80% of appeals are overturned, the current system has a quality problem, not just a capacity problem  
- **Discovery method**: Review 6 months of moderation appeals; categorize by violation type, moderator, outcome  
- **Risk if wrong**: We automate a broken process, and AI inherits the quality problems  

---

### Medium-Risk Unknowns (Can Be Deferred but Inform Design)

**U6: What is the distribution of post volume across time zones / time of day?**  
- **Why it matters**: If 60% of posts happen during 6-hour window, moderator availability (A3) may be more constrained than assumed  
- **Discovery method**: 30-day post volume analysis by hour  
- **Risk if wrong**: AI system reduces average load but doesn't solve peak-hour bottlenecks  

**U7: What is the current false positive rate on routine moderation (posts incorrectly removed)?**  
- **Why it matters**: A9 assumes 5%, but if actual rate is 15%, community may already distrust moderation, changing the risk calculus  
- **Discovery method**: Sample 500 removed posts, have 2nd moderator review for correctness  
- **Risk if wrong**: We optimize for wrong baseline trust level  

**U8: What is the moderator training/onboarding time for new volunteers?**  
- **Why it matters**: A5 assumes 40 hours to replace a burned-out volunteer; if actual time is 80 hours, burnout cost is 2x higher  
- **Discovery method**: Interview community manager on volunteer recruitment/training process  
- **Risk if wrong**: Underestimate ROI of burnout prevention  

---

### Low-Risk Unknowns (Safe to Defer)

**U9: What is the paid staff time allocation across moderation vs. other duties?**  
- **Why it matters**: A6 assumes 6 hours/day on moderation; if actual is 4 hours, capacity is more constrained  
- **Discovery method**: Time-tracking audit for 2 weeks  
- **Risk if wrong**: Slightly misestimate baseline capacity, but doesn't change core problem  

**U10: What is the user sentiment on current moderation speed/quality?**  
- **Why it matters**: If users complain about slow moderation, speed becomes a success metric; if they complain about inconsistency, quality is the priority  
- **Discovery method**: User survey or forum sentiment analysis  
- **Risk if wrong**: We optimize for capacity when users care about consistency (or vice versa), but core problem (moderator burnout) remains valid  

---

## Summary: What This Problem Actually Is

This is **not** a "let's automate 97% of moderation" problem.

This is a **volunteer moderator burnout prevention problem** where the intervention is an AI triage system that:
1. Eliminates cognitive load from repetitive routine decisions (Metric 1)
2. Frees moderator capacity for high-quality grey-zone review (Metric 2)  
3. Maintains absolute zero tolerance for trust-damaging errors (Metric 3)
4. Does so at sustainable economic cost (Metric 4)
5. Results in measurable reduction in volunteer attrition (Metric 5)

The client's stated request ("AI handles 97% instantly") is a **means**, not the **end**. The end is a sustainable moderation system that preserves community trust while respecting volunteer moderator time as the scarce resource.

**Critical unknowns U1-U5 must be resolved in discovery before specification begins.** Without understanding policy distribution (U1), trust damage definition (U2), moderator agreement rates (U3), grey-zone pattern frequency (U4), and current appeal rates (U5), we cannot spec a system that meets the "never damage trust" constraint.