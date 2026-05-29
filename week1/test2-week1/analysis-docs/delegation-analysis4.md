# Delegation Analysis

# Executive Summary: Delegation Distribution Analysis

## Overview

This delegation architecture addresses volunteer moderator burnout in a 180K-user tabletop-miniature community platform processing 12,000 posts/day. The analysis distributes moderation work across four delegation models, achieving **63% reduction in moderator cognitive load (68.3 hours/day saved)** while maintaining zero tolerance for trust-damaging errors in grey-zone cases.

---

## Delegation Distribution

### Fully Agentic: 48.5% of Volume, 22.2 Hours/Day Saved

**Work delegated**: Spam detection (3,880 posts/day), post miscategorization correction (1,940 posts/day), and user context gathering (360 cases/day)

**Rationale**: These are low-stakes, pattern-based tasks where false positives are recoverable through user appeals. Per **A10** (8% acceptable false positive rate), we tolerate AI incorrectly flagging legitimate posts to achieve high-volume automation. Spam detection uses 85% confidence threshold (**A14**), and miscategorization uses 80% threshold (**A16**) for auto-action.

**Time impact**: 
- Current: 16.2 hrs (spam) + 8.1 hrs (miscategorization) = 24.3 hrs/day
- With AI: 2.1 hrs/day (audit only, per **A13**: 30 min/moderator/day)
- **Saved: 22.2 hrs/day**

**Cost**: $47/day in AI API costs (per **A7**: $0.008/post for routine triage)

**Risk**: Low. False positives caught through mandatory audit (**A13**) and user appeal paths. Does not trigger "never damage trust" constraint as these are routine decisions, not grey-zone judgments.

---

### Agent-Led with Human Oversight: 51.5% of Volume, 51.6 Hours/Day Saved

**Work delegated**: Clear rule violation detection (5,820 posts/day) and grey-zone identification across four types: harsh critique, established member commercial posts, IP claims, and cultural context evaluation (360 posts/day total)

**Rationale**: This is the critical boundary between automation and human judgment. For clear violations, AI auto-actions posts with >90% confidence (**A15**) but flags 70-90% confidence cases for human review. For grey-zones, AI identifies potential cases and gathers context but never makes moderation decisions. Per **A11** (95% recall requirement), the system must catch 95% of true grey-zone cases to prevent auto-actioning posts that require human judgment.

**Time impact**:
- Current: 24.3 hrs (clear violations) + 48 hrs (grey-zone review) = 72.3 hrs/day
- With AI: 8.7 hrs (human review of flagged violations) + 12 hrs (grey-zone decisions with AI-prepared context, per **A12**: 4 min/case vs. 8 min/case per **A2**)
- **Saved: 51.6 hrs/day**

**Cost**: $61/day in AI API costs (per **A7**: higher token usage for policy matching and context gathering)

**Risk**: Medium-High. The 5% grey-zone miss rate (**A11**) represents 18 posts/day that could be incorrectly auto-actioned, creating trust damage. Mitigated through user appeal triggers and weekly recall validation audits.

**Critical dependency**: Success depends on resolving **U3** (moderator agreement rate on grey-zones). If moderators themselves disagree >30% of the time on what constitutes "clear" violations, this delegation model must shift toward more human oversight.

---

### Human-Led with AI Assistance: 3% of Volume, 24 Hours/Day Saved

**Work delegated**: Final moderation decisions on all 360 grey-zone cases/day

**Rationale**: This is the irreducible human judgment core. AI provides structured context briefs (user history, similar past cases, relevant policy sections, confidence reasoning), reducing moderator discovery time from 8 minutes to 4 minutes per case (**A12**). However, humans make all final decisions on:
- Whether harsh critique crosses into harassment
- Whether established member commercial posts violate self-promotion limits
- Whether IP claims are legitimate or spurious
- Whether cultural references are offensive in community context

**Time impact**:
- Current: 48 hrs/day at 8 min/case (**A2**)
- With AI: 24 hrs/day at 4 min/case (**A12**)
- **Saved: 24 hrs/day**

**Cost**: $0 incremental (covered in Agent-Led grey-zone identification costs)

**Risk**: High stakes but human-controlled. Risk shifts from "AI makes wrong decision" to "AI provides misleading context, human makes wrong decision based on incomplete information." Mitigated through moderator feedback loops and mandatory documentation of decision rationale.

**Critical dependency**: Time savings depend on **A12** assumption (AI-prepared context reduces review time by 50%). If **U4** (pattern frequency in grey-zones) reveals most cases are novel rather than recurring, AI context may be less useful and actual time savings could be 30% instead of 50%.

---

### Human-Led Only: 10% of Volume, -5 Hours/Day (New Oversight Work)

**Work delegated**: Audit of AI auto-actions (1,200 posts/day sampled from ~5,820 auto-actioned posts)

**Rationale**: Per **A13** (30 min/moderator/day audit time), this is mandatory oversight to maintain trust in the AI system. Each moderator spot-checks ~120 auto-actioned posts/day at 15 seconds/post (**A1**). This is new work created by AI delegation, not work saved.

**Time impact**:
- Current: 0 hrs/day (no AI to audit)
- With AI: 5 hrs/day (10 moderators × 30 min)
- **Cost: -5 hrs/day (new work)**

**Purpose**: 
1. Quality assurance (catch AI errors before they become patterns)
2. Calibration (provide feedback to adjust AI confidence thresholds)
3. Trust maintenance (demonstrate human oversight to community)

**Risk**: Medium. If audit sample (1% of auto-actioned volume) misses systematic AI errors, trust damage could accumulate undetected. Mitigated through user appeal clustering detection (if 5+ appeals mention same issue in 24 hours, triggers immediate investigation).

---

## Net Impact Summary

| Metric | Current State | With AI Delegation | Change |
|--------|---------------|-------------------|--------|
| **Total moderator time** | 108.6 hrs/day | 40.3 hrs/day | -63% |
| **Time per moderator** | 10.9 hrs/day | 4.0 hrs/day | -63% |
| **Volunteer moderator time** | Unsustainable (exceeds **A3**: 2 hrs/day available by 5.4x) | 2.8 hrs/day average | Within capacity |
| **Grey-zone review quality** | 45% receive full 8-min review (estimated) | 95% receive full 4-min review | +111% quality |
| **AI operational cost** | $0 | $108/day ($39,420/year) | New cost |
| **Human time cost saved** | - | $573/day × 30% paid staff (**A4**) = $209K/year | Net savings ~$170K/year |
| **Volunteer burnout rate** | 1 volunteer lost/quarter (**A5**) | Target: 0.5/quarter (85% retention) | -50% attrition |

---

## Key Assumptions Driving Delegation Decisions

**Time assumptions**:
- **A1**: 15 sec/routine decision (current manual process)
- **A2**: 8 min/grey-zone decision (current manual process)
- **A12**: 4 min/grey-zone decision (with AI-prepared context)
- **A13**: 30 min/moderator/day for AI audit

**Risk tolerance assumptions**:
- **A10**: 8% false positive rate acceptable on routine cases
- **A11**: 95% recall required on grey-zone identification (5% miss rate maximum)

**Economic assumptions**:
- **A7**: $0.008/post for AI routine triage, $0.04/post for grey-zone context
- **A6**: $28/hr fully-loaded cost for paid staff moderators

**Workflow assumptions**:
- **A4**: Volunteers handle 70% of volume, paid staff 30%
- **A3**: Volunteer moderators available 2 hrs/day average

**Distribution assumptions** (new):
- **A14**: Routine work splits 33% spam / 50% clear violations / 17% miscategorization
- **A15**: 90% confidence threshold for auto-action on clear violations
- **A16**: 80% confidence threshold for auto-recategorization
- **A17**: Grey-zones split 33% harsh critique / 25% commercial / 17% IP / 25% cultural

---

## Critical Unknowns That Could Invalidate Delegation Models

**U3 (moderator agreement rate)**: If moderators disagree >30% of the time on "clear" violations, the Agent-Led model for Work Type 2 (clear violations) must shift to Human-Led with AI Assistance. This would reduce time savings from 15.6 hrs/day to ~8 hrs/day on that work type.

**U4 (grey-zone pattern frequency)**: If 70%+ of grey-zones are recurring patterns (not novel cases), AI could eventually learn to auto-action recurring patterns with human spot-check after 6 months of training data. This would unlock additional 10-15% time savings. Conversely, if all grey-zones are genuinely novel, **A12** (50% time reduction) may be optimistic.

**U2 (trust damage definition)**: Client states "never damage trust" but doesn't quantify threshold. If actual tolerance is stricter than **A11** (95% recall), grey-zone identification must become more conservative (lower confidence threshold), increasing false positives and reducing time savings.

**U1 (policy distribution)**: If spam represents <20% of routine volume (vs. 33% per **A14**), ROI on spam automation drops. If clear violations represent >60% (vs. 50% per **A14**), dependency on **U3** (moderator agreement) becomes even more critical.

---

## Recommendation

Implement this delegation architecture in phases:

**Phase 1 (Weeks 1-4)**: Deploy Fully Agentic work (spam, miscategorization) to validate **A10** (false positive tolerance) and **A13** (audit process). Low-risk, high-ROI (22.2 hrs/day saved).

**Phase 2 (Weeks 5-8)**: Deploy Agent-Led grey-zone identification and Human-Led with AI Assistance for grey-zone decisions. This unlocks the critical 51.6 hrs/day savings on grey-zone work. Requires resolving **U3** (moderator agreement) and **U4** (pattern frequency) through discovery first.

**Phase 3 (Weeks 9-12)**: Deploy Agent-Led clear violation detection only after validating **U3** (moderator agreement >70%) and calibrating **A15** (confidence threshold) based on Phase 1-2 data.

**Success criteria**: Achieve 60%+ moderator time reduction while maintaining zero grey-zone false negatives (per **A11**) and <5% appeal rate on auto-actioned posts.

---

# Delegation Analysis: Content Moderation System Architecture

## 1. Delegation Architecture

### Work Type 1: Obvious Spam Detection and Removal

**Current State**:  
- Volume: ~3,880/day (estimated 33% of routine volume, per A14 below)
- Performed by: All 10 moderators (volunteers + paid staff)
- Time per post: 15 seconds (per A1)
- Total time: 16.2 hours/day across all moderators

**Delegation Model**: Fully Agentic

**Rationale**:  
Spam detection is the highest-confidence automation candidate. Characteristics include:
- Clear, objective patterns (link farms, repeated text, promotional language)
- Low cultural context dependency
- High volume justifies AI investment
- False positives (legitimate post flagged as spam) are recoverable through user appeals
- False negatives (missed spam) have low trust-damage risk compared to grey-zone errors

Per A10, we accept 8% false positive rate on routine cases. For spam specifically, false positives mean legitimate posts incorrectly removed—but these trigger user reports and can be quickly restored. The "never damage trust" constraint (from problem statement) applies primarily to grey-zone cases where context and judgment matter, not to spam where patterns are mechanical.

**Handoff Design**:  
- **AI Action**: Classify post as spam/not-spam using pattern matching (known spam domains, excessive links, promotional keyword density, new account + commercial content pattern)
- **Confidence threshold**: Posts with >85% spam confidence → auto-remove (per A14)
- **Escalation trigger**: Posts with 60-85% spam confidence → flag for human review with reasoning
- **Context passed to human**: Spam classification features (link count, keyword matches, account age, posting frequency)
- **No human involvement**: Posts <60% spam confidence pass through as legitimate

**Risk Mitigation**:  
- **Audit mechanism** (per A13): Moderators spot-check 30 min/day = ~120 auto-removed posts reviewed
- **User appeal path**: Removed posts trigger automated notification with appeal link
- **Pattern monitoring**: Daily dashboard of spam removal volume, false positive rate from appeals
- **Escape valve**: If appeals spike >5/day on spam removals, system auto-escalates to human review mode

**Dependencies**: A1 (time per decision), A7 (AI cost), A10 (acceptable false positive rate), A13 (audit time), A14 (spam volume distribution), U1 (policy distribution—if spam is <20% of routine volume, ROI changes)

---

### Work Type 2: Clear Rule Violation Detection and Removal

**Current State**:  
- Volume: ~5,820/day (estimated 50% of routine volume, per A14 below)
- Performed by: All 10 moderators
- Time per post: 15 seconds (per A1)
- Total time: 24.3 hours/day across all moderators

**Delegation Model**: Agent-Led with Human Oversight

**Rationale**:  
"Clear rule violations" from the 14-page policy (harassment, doxxing, off-topic content per scenario) are more complex than spam but still pattern-based. However:
- Harassment detection requires context (is "your painting sucks" critique or harassment?)
- Doxxing has zero-tolerance requirement (false negative = legal/safety risk)
- Off-topic classification depends on forum section context

This is the critical boundary case. Per A11 (95% recall on grey-zones), we cannot afford to auto-action posts that might be grey-zone harassment or cultural context issues. The delegation model reflects asymmetric risk: we accept AI flagging legitimate posts for review (false positive) but cannot accept AI missing a true violation that should have been caught (false negative in grey-zone territory).

**However**, U3 (moderator agreement rate) creates uncertainty: if moderators themselves disagree 40% of the time on what constitutes "clear" harassment, AI cannot be expected to perform better. This work type may need to shift toward "Human-Led with AI Assistance" after discovery.

**Handoff Design**:  
- **AI Action**: Classify post against policy categories (harassment, doxxing, off-topic)
- **High-confidence violations** (>90% confidence, per A15): Auto-remove with notification
  - Examples: Posts containing personal addresses (doxxing), racial slurs (harassment), spam links in technical forums (off-topic)
- **Medium-confidence violations** (70-90% confidence): Flag for human review with policy section reference and reasoning
  - Examples: Heated critique language, ambiguous personal information, borderline off-topic discussions
- **Low-confidence** (<70%): Pass through, but log for pattern analysis
- **Context passed to human**: Policy section matched, confidence score, similar past cases, user history summary

**Risk Mitigation**:  
- **Mandatory human review** for all doxxing classifications (zero false negative tolerance)
- **Audit mechanism**: 30 min/day spot-check of auto-removed posts (per A13)
- **Escalation path**: Any user appeal of auto-removal triggers immediate human review
- **Confidence calibration**: Weekly review of AI confidence scores vs. human agreement rates; recalibrate thresholds if divergence >10%

**Dependencies**: A1, A7, A10, A11 (recall requirement), A13, A15 (confidence thresholds), U1 (policy distribution—critical), U3 (moderator agreement—if low, this model fails), U5 (appeal rate—if high, indicates AI miscalibration)

---

### Work Type 3: Post Categorization Correction (Miscategorised Posts)

**Current State**:  
- Volume: ~1,940/day (estimated 17% of routine volume, per A14 below)
- Performed by: All 10 moderators
- Time per post: 15 seconds (per A1)
- Total time: 8.1 hours/day across all moderators

**Delegation Model**: Fully Agentic

**Rationale**:  
Miscategorisation (user posts painting showcase in technical discussion forum) is low-stakes, high-volume work. Characteristics:
- Objective classification based on content type (image gallery vs. text discussion vs. tutorial)
- Low trust-damage risk (miscategorised post is still visible, just in wrong section)
- High automation ROI (8.1 hours/day saved)
- False positives (post moved to wrong category) are easily corrected by users or moderators

This is the clearest full-delegation candidate after spam. The "never damage trust" constraint doesn't apply—users care about posts being removed or flagged for violations, not about whether their painting is in "Showcase" vs. "WIP Gallery."

**Handoff Design**:  
- **AI Action**: Analyze post content (text, images, tags) and recommend category
- **Auto-recategorize**: Posts with >80% confidence in correct category (per A16)
- **Notify user**: "Your post has been moved to [Category] for better visibility"
- **No escalation**: Even if AI miscategorizes, users can manually recategorize or moderators catch in routine browsing
- **Context passed**: None required (fully automated)

**Risk Mitigation**:  
- **User self-correction**: Users can recategorize their own posts
- **Moderator visibility**: Recategorization log visible in moderation dashboard
- **Pattern monitoring**: If recategorization rate >15% of posts/day, indicates forum structure problem (not AI problem)

**Dependencies**: A1, A7, A14 (volume distribution), A16 (confidence threshold for auto-recategorization)

---

### Work Type 4-7: Grey-Zone Identification (Composite Analysis)

These four grey-zone types (harsh critique, established member commercial posts, IP claims, cultural context) share a common delegation pattern, so I analyze them together before separating final decisions.

**Current State**:  
- Volume: 360/day total across all four types
- Performed by: All 10 moderators
- Time per post: 8 minutes (per A2) for full review
- Total time: 48 hours/day across all moderators (current unsustainable state)

**Delegation Model**: Agent-Led with Human Oversight (for identification + context gathering)

**Rationale**:  
The AI's role here is NOT to make moderation decisions but to:
1. **Identify** posts that might be grey-zone (vs. clearly routine)
2. **Gather context** that humans need for decisions
3. **Present structured information** to reduce human discovery time from 8 min to 4 min (per A12)

Per A11, we need 95% recall—the AI must catch 95% of true grey-zone cases. This is the binding constraint. We accept false positives (flagging routine posts as grey-zone) to ensure we never auto-action a post that needed human judgment.

**Breakdown by Grey-Zone Type**:

#### 4a. Harsh Critique Detection
- **Estimated volume**: 120/day (33% of grey-zone, per A17)
- **AI identification signals**: Negative sentiment language + technical terminology (suggests critique not harassment), user history of constructive feedback, thread context (ongoing discussion vs. drive-by comment)
- **Context gathered**: User's past critique history, recipient's response pattern, community norms for this forum section
- **Escalation trigger**: Any post with negative sentiment + ambiguous intent flags for human review
- **Human decision**: Is this harsh but constructive critique, or harassment?

#### 4b. Established Member Commercial Posts
- **Estimated volume**: 90/day (25% of grey-zone, per A17)
- **AI identification signals**: Commercial keywords (selling, commission, shop link) + account age >1 year + positive community standing
- **Context gathered**: User's post history (ratio of community contribution vs. commercial posts), past moderator decisions on this user's commercial content, community self-promotion policy limits
- **Escalation trigger**: Any commercial content from established members flags for human review
- **Human decision**: Has this user exceeded self-promotion limits? Is this spam or legitimate community commerce?

#### 4c. IP Claims Assessment
- **Estimated volume**: 60/day (17% of grey-zone, per A17)
- **AI identification signals**: Keywords (stolen, copied, my design, copyright, original sculptor), image similarity analysis if applicable
- **Context gathered**: Claimant's history of IP claims, accused user's posting history, timestamps of original vs. alleged copy, community IP dispute resolution history
- **Escalation trigger**: Any IP claim language flags for human review (zero auto-action tolerance)
- **Human decision**: Is this a legitimate IP dispute requiring investigation, or a spurious claim?

#### 4d. Cultural Context Evaluation
- **Estimated volume**: 90/day (25% of grey-zone, per A17)
- **AI identification signals**: Cultural/religious references, regional slang, historical references, symbols/imagery with multiple cultural meanings
- **Context gathered**: User's location/language, forum section context (historical miniatures vs. fantasy), similar past cases and resolutions, community cultural sensitivity guidelines
- **Escalation trigger**: Any cultural reference that could be interpreted multiple ways flags for human review
- **Human decision**: Is this offensive in context, or culturally appropriate for this community section?

**Handoff Design (All Grey-Zone Types)**:  
- **AI Action**: Identify potential grey-zone post + gather context
- **Output to human**: Structured brief with:
  - Post content + thread context
  - Grey-zone type classification (harsh critique / commercial / IP / cultural)
  - Relevant user history summary (3-5 key data points)
  - Similar past cases (2-3 examples with outcomes)
  - Relevant policy sections (specific page references from 14-page document)
  - AI confidence score (for transparency, not decision-making)
- **Human Action**: Review brief (4 min per A12), make final decision, document rationale
- **No auto-action**: AI never removes or sanctions grey-zone posts

**Risk Mitigation**:  
- **Recall validation** (per A11): Weekly audit of 100 random routine posts to check for missed grey-zones (target: <5% miss rate)
- **Precision monitoring**: Track false positive rate (routine posts flagged as grey-zone); acceptable up to 15% per A10 tolerance
- **Human feedback loop**: Moderators mark AI briefs as "helpful" or "missing key context"; feed back to improve context gathering
- **Escalation safety net**: Any post that receives user report after AI classified as routine triggers immediate human review

**Dependencies**: A2 (current grey-zone time), A11 (95% recall requirement), A12 (AI-assisted review time), A17 (grey-zone distribution), U2 (trust damage definition—critical for calibrating recall threshold), U3 (moderator agreement—if low, even human decisions are inconsistent), U4 (pattern frequency—if 70% of grey-zones are recurring patterns, AI can learn; if all novel, AI only provides context)

---

### Work Type 8: Grey-Zone Case Review and Final Decision

**Current State**:  
- Volume: 360/day
- Performed by: All 10 moderators (with bias toward paid staff for complex cases per A4)
- Time per post: 8 minutes current (per A2), 4 minutes with AI assistance (per A12)
- Total time: 48 hours/day current, 24 hours/day with AI assistance

**Delegation Model**: Human-Led with AI Assistance

**Rationale**:  
This is the irreducible human judgment core. The AI has identified the grey-zone and gathered context (Work Types 4-7), but the final decision requires:
- **Community trust judgment**: Will this decision be seen as fair by the community?
- **Policy interpretation**: Does this specific case fall under harassment or critique?
- **Risk assessment**: What are the consequences of action vs. inaction?
- **Precedent setting**: How does this decision affect future similar cases?

Per the problem statement, this is where moderator time must be protected and focused. The AI's contribution is reducing discovery time (8 min → 4 min per A12) by pre-gathering context, not making the decision.

**Handoff Design**:  
- **Input from AI**: Structured brief from Work Types 4-7
- **Human process**: 
  1. Review AI brief (1 min)
  2. Verify context accuracy (1 min)
  3. Apply policy judgment (1.5 min)
  4. Make decision (approve/remove/warn/escalate) (0.5 min)
  5. Document rationale in moderation log (mandatory for grey-zones)
- **Output**: Moderation decision + documented reasoning
- **No AI involvement in decision**: AI does not recommend actions, only provides information

**Risk Mitigation**:  
- **Mandatory documentation**: All grey-zone decisions require written rationale (feeds into U4 pattern analysis)
- **Peer review option**: Moderators can flag cases for second opinion before action
- **Appeal transparency**: Grey-zone decisions include explanation visible to affected user
- **Quality monitoring**: Track appeal rate on grey-zone decisions (target: <5% per month)

**Dependencies**: A2, A12, U2 (trust damage definition), U3 (moderator agreement—if low, need calibration sessions), U4 (pattern frequency—informs whether AI can eventually learn grey-zone patterns)

---

### Work Type 9: User History/Context Gathering

**Current State**:  
- Volume: 360/day (one per grey-zone case, embedded in 8-min review time per A2)
- Performed by: Moderators during case review
- Time per case: ~2-3 minutes of the 8-minute review (per A2 breakdown)
- Total time: 12-18 hours/day (embedded in grey-zone review)

**Delegation Model**: Fully Agentic (as input to Work Types 4-7)

**Rationale**:  
Context gathering is pure information retrieval:
- User's post history (last 30 days)
- Past moderation actions on this user
- Community standing (account age, positive interactions, reputation score if available)
- Relevant past cases involving this user

This is mechanical work that AI can do faster and more consistently than humans. It's already embedded in the AI brief structure for Work Types 4-7.

**Handoff Design**:  
- **AI Action**: Query user database, moderation log, post history
- **Output**: Structured summary in grey-zone brief (Work Types 4-7)
- **No human involvement**: Fully automated as part of grey-zone identification workflow

**Risk Mitigation**:  
- **Data accuracy validation**: Moderators can click through to raw data if AI summary seems incorrect
- **Privacy constraints**: AI only accesses data already available to moderators (no new privacy concerns)

**Dependencies**: A2 (time breakdown), A12 (AI-assisted time reduction assumes this context is pre-gathered)

---

### Work Type 10: Audit/Validation of AI Decisions

**Current State**:  
- Volume: N/A (new work created by AI delegation)
- Performed by: N/A
- Time: N/A

**Delegation Model**: Human-Led Only

**Rationale**:  
Per A13, moderators must spend 30 min/day auditing AI auto-actions to maintain trust in the system. This is irreducible human oversight work. The audit serves two purposes:
1. **Quality assurance**: Catch AI errors before they become patterns
2. **Calibration**: Provide feedback to adjust AI confidence thresholds

**Handoff Design**:  
- **Human process**: 
  - Each moderator reviews ~120 AI auto-actioned posts/day (30 min at 15 sec/post per A1)
  - Sample includes spam removals, clear violations, and recategorizations
  - Flag any errors for immediate correction + pattern analysis
- **Output**: Error log fed back to AI system for threshold recalibration
- **No AI involvement**: This is human validation of AI work

**Risk Mitigation**:  
- **Mandatory daily audit**: Non-negotiable 30 min/moderator/day
- **Error escalation**: If audit finds >3 errors/day/moderator, trigger full system review
- **Feedback loop**: Weekly calibration meeting to adjust AI confidence thresholds based on audit findings

**Dependencies**: A13 (audit time), A1 (time per post review)

---

## 2. New Assumptions

**A14: Distribution of routine work across categories**  
**Assumed value**: Spam 33% (3,880/day), Clear violations 50% (5,820/day), Miscategorization 17% (1,940/day)  
**Reasoning**: Based on typical community moderation patterns. Spam is constant background noise. Clear violations (harassment, off-topic) dominate routine work. Miscategorization is lower volume but persistent. Total = 11,640/day per scenario.  
**Dependencies**: Work Types 1, 2, 3 volume calculations rely on this distribution. If U1 (policy distribution discovery) reveals different breakdown, delegation ROI changes but models remain valid.

**A15: Confidence threshold for auto-action on clear violations**  
**Assumed value**: >90% confidence for auto-removal, 70-90% for human review, <70% pass-through  
**Reasoning**: Higher threshold than spam (85% per A14) because violations involve user sanctions, not just content removal. Must balance A10 (8% acceptable false positive rate) with A11 (95% recall on grey-zones). 90% threshold leaves room for 10% of "clear violations" to be flagged for human review, protecting against grey-zone false negatives.  
**Dependencies**: Work Type 2 delegation model. If U3 (moderator agreement) shows low consistency, this threshold must increase to 95%+ to maintain trust.

**A16: Confidence threshold for auto-recategorization**  
**Assumed value**: >80% confidence  
**Reasoning**: Lower stakes than violations (no user sanctions), so lower threshold acceptable. 20% false positive rate (post moved to wrong category) is tolerable because users can self-correct and there's no trust damage.  
**Dependencies**: Work Type 3 delegation model.

**A17: Distribution of grey-zone work across four types**  
**Assumed value**: Harsh critique 33% (120/day), Established member commercial 25% (90/day), IP claims 17% (60/day), Cultural context 25% (90/day)  
**Reasoning**: Harsh critique is most common grey-zone (subjective language interpretation). Commercial posts and cultural context are tied for second (both involve community norms). IP claims are rarest (require specific triggering event). Total = 360/day per scenario.  
**Dependencies**: Work Types 4-7 volume calculations. If U4 (pattern frequency) reveals one type dominates, may enable more targeted AI training.

---

## 3. Cross-References to Existing Assumptions

### Dependency Mapping Table

| Work Type | Existing Assumptions | New Assumptions | Critical Unknowns |
|-----------|---------------------|-----------------|-------------------|
| 1. Spam detection | A1, A7, A10, A13 | A14 | U1 (if spam <20% of volume, ROI drops) |
| 2. Clear violations | A1, A7, A10, A11, A13 | A14, A15 | U1 (policy distribution), U3 (moderator agreement), U5 (appeal rate) |
| 3. Miscategorization | A1, A7 | A14, A16 | U1 (if miscategorization >25% of volume, higher ROI) |
| 4-7. Grey-zone identification | A2, A11, A12 | A17 | U2 (trust damage definition), U3 (moderator agreement), U4 (pattern frequency) |
| 8. Grey-zone decisions | A2, A12 | A17 | U2, U3, U4 (all critical for human decision quality) |
| 9. Context gathering | A2, A12 | None | None (mechanical work) |
| 10. Audit | A1, A13 | None | None (mandatory oversight) |

### Risk Analysis: If Assumptions Prove Wrong

**If A10 (8% acceptable false positive rate) is too high**:
- Impact: Work Types 1, 2, 3 must shift from "Fully Agentic" or "Agent-Led" to "Agent-Led with Human Oversight"
- Mitigation: Increase confidence thresholds (A15, A16) to 95%+, reducing auto-action volume
- Cost: Moderator time savings drop from 80% to ~60%

**If A11 (95% recall requirement) proves insufficient**:
- Impact: Work Types 4-7 must flag even more posts for human review (false positive rate rises above 15%)
- Mitigation: Lower confidence threshold for grey-zone identification to 50% (from current 60-70% implied)
- Cost: Moderators review more false positives, but zero grey-zone false negatives maintained

**If A12 (4-min AI-assisted review) is optimistic**:
- Impact: Time savings on grey-zone review are less than projected (24 hours/day vs. 18 hours/day)
- Mitigation: Improve AI brief quality (more concise summaries, better policy references)
- Cost: ROI drops but core delegation model remains valid

**If U3 (moderator agreement rate) is <70%**:
- Impact: Work Type 2 (clear violations) cannot be auto-actioned—even humans disagree on what's "clear"
- Mitigation: Shift Work Type 2 to "Human-Led with AI Assistance" (AI flags, humans always decide)
- Cost: Moderator time savings drop significantly (~40% reduction instead of 80%)

**If U4 (grey-zone patterns) shows 70%+ are recurring**:
- Impact: Work Types 4-7 can eventually shift toward "Agent-Led" for recurring patterns (e.g., "established member commercial post" becomes learnable)
- Opportunity: After 6 months of pattern data, AI can auto-action recurring grey-zones with human spot-check
- Gain: Additional 10-15% moderator time savings

---

## 4. Summary Table

| Work Type | Current Daily Volume | Current Time Cost | Delegation Model | AI Time Cost | Human Time Cost | Time Saved | Risk Level |
|-----------|---------------------|-------------------|------------------|--------------|-----------------|------------|------------|
| 1. Spam detection | 3,880 | 16.2 hrs | Fully Agentic | $31/day | 1.6 hrs (audit) | 14.6 hrs | Low |
| 2. Clear violations | 5,820 | 24.3 hrs | Agent-Led w/ Oversight | $47/day | 8.7 hrs (review) | 15.6 hrs | Medium |
| 3. Miscategorization | 1,940 | 8.1 hrs | Fully Agentic | $16/day | 0.5 hrs (audit) | 7.6 hrs | Low |
| 4-7. Grey-zone ID + context | 360 | 12 hrs (embedded) | Agent-Led w/ Oversight | $14/day | 0 hrs (feeds into #8) | 12 hrs | High |
| 8. Grey-zone decisions | 360 | 48 hrs | Human-Led w/ AI Assist | $0 (covered in #4-7) | 24 hrs | 24 hrs | High |
| 9. Context gathering | 360 | 12 hrs (embedded) | Fully Agentic | $0 (covered in #4-7) | 0 hrs | 12 hrs | Low |
| 10. Audit of AI actions | ~1,200 sampled | 0 hrs (new) | Human-Led Only | $0 | 5 hrs | -5 hrs (new work) | Medium |
| **TOTALS** | **12,000** | **108.6 hrs/day** | **Mixed** | **$108/day** | **40.3 hrs/day** | **68.3 hrs (63%)** | **-** |

### Summary Breakdown

**Total work volume**: 12,000 posts/day

**Fully Agentic**: 
- Volume: 5,820 posts/day (48.5%)
- Time saved: 22.2 hours/day
- Work types: Spam detection, Miscategorization, Context gathering

**Agent-Led with Human Oversight**:
- Volume: 6,180 posts/day (51.5% - includes all grey-zones flagged + clear violations needing review)
- Time saved: 51.6 hours/day (from reducing review time + eliminating discovery work)
- Work types: Clear violations, Grey-zone identification

**Human-Led with AI Assistance**:
- Volume: 360 posts/day (3%)
- Time saved: 24 hours/day (8 min → 4 min per case per A12)
- Work types: Grey-zone final decisions

**Human-Led Only**:
- Volume: ~1,200 posts/day (10% - audit sample)
- Time saved: -5 hours/day (new oversight work)
- Work types: Audit of AI auto-actions

**Net moderator time reduction**: 68.3 hours/day (63% reduction from 108.6 hrs to 40.3 hrs)

**Per-moderator impact**:
- Current: 10.9 hours/moderator/day (unsustainable - exceeds A3 available time by 5.4x)
- With AI: 4.0 hours/moderator/day (within A3 available time of 2 hrs volunteer + paid staff capacity)
- Volunteers specifically: 2.8 hours/day average (within A3 tolerance with buffer)

**Economic impact**:
- AI cost: $108/day = $39,420/year
- Human time saved: 68.3 hrs/day × $28/hr (A6) × 30% paid staff (A4) = $573/day = $209,000/year
- Net savings: ~$170,000/year (not counting volunteer burnout prevention per A5)

---

## 5. Handoff Failure Modes

### Handoff 1: AI Auto-Action (Spam/Miscategorization) → User Experience

**What could go wrong**: AI removes legitimate post as spam, or miscategorizes post to wrong forum section

**Probability**: Medium  
- Per A10, we accept 8% false positive rate = ~930 posts/day incorrectly flagged
- Of these, ~465 are spam false positives (legitimate posts removed)
- Per A14, spam = 3,880/day, so 465/3,880 = 12% false positive rate on spam specifically

**Impact**: Low-Medium  
- Miscategorization: Low impact (user can self-correct, no sanctions)
- Spam removal: Medium impact (user frustration, but appeal path exists)
- Does not trigger "never damage trust" constraint (routine work, not grey-zone judgment)

**Detection method**:  
- User appeals (automated notification on removal)
- Moderator audit (30 min/day per A13 catches ~120 posts = ~1% sample)
- Pattern monitoring (if appeals spike >5/day, triggers alert)

**Mitigation**:  
- **Immediate**: Moderator audit catches errors within 24 hours
- **Systemic**: Weekly calibration of confidence thresholds based on appeal rate
- **User-facing**: Clear appeal path with <4 hour response time
- **Escape valve**: If false positive rate exceeds 10% for 3 consecutive days, system auto-switches to "Agent-Led with Oversight" mode (all AI actions require human confirmation)

---

### Handoff 2: AI Grey-Zone Identification → Human Review Queue

**What could go wrong**: AI misses true grey-zone case (false negative), allowing auto-action on post that needed human judgment

**Probability**: Low (by design)  
- Per A11, system designed for 95% recall = 5% miss rate = 18 posts/day
- These 18 posts get treated as "routine" and may be auto-actioned
- This is the highest-risk failure mode for "never damage trust" constraint

**Impact**: High  
- If missed grey-zone is harsh critique → auto-removed as harassment → community backlash ("AI doesn't understand context")
- If missed grey-zone is established member commercial → auto-removed as spam → trusted member alienated
- If missed grey-zone is cultural reference → auto-removed as offensive → cultural insensitivity accusation
- Single viral incident can damage community trust permanently

**Detection method**:  
- **Primary**: User appeals on auto-actioned posts (any appeal of routine auto-action triggers human review)
- **Secondary**: Community reports (users can flag "moderator got this wrong")
- **Tertiary**: Moderator audit (A13) specifically samples auto-actioned posts for missed grey-zones
- **Lagging**: Weekly audit of 100 random "routine" posts to validate recall rate

**Mitigation**:  
- **Design**: Conservative grey-zone identification (accept 15% false positive rate per A10 to ensure 95% recall per A11)
- **Safety net**: Any post that receives user appeal OR community report within 24 hours of auto-action triggers immediate human review + reversal if appropriate
- **Monitoring**: Daily dashboard of grey-zone miss rate (target: <5% per A11)
- **Escalation**: If weekly audit reveals >5% miss rate, immediately lower confidence threshold for grey-zone flagging (increases false positives but protects recall)
- **Recovery**: Transparent communication when AI error is caught ("We got this wrong, here's why, here's what we're doing about it")

---

### Handoff 3: AI Context Brief → Human Grey-Zone Decision

**What could go wrong**: AI provides incomplete or misleading context, causing moderator to make wrong decision

**Probability**: Medium  
- AI context gathering (Work Type 9) is mechanical, but interpretation can be wrong
- Example: AI summarizes user history as "5 commercial posts in 30 days" but misses that 4 were in designated commerce forum (allowed) and only 1 was in discussion forum (violation)
- Moderator trusts AI brief without verifying, makes wrong decision

**Impact**: Medium-High  
- Wrong decision on grey-zone case = potential trust damage (per problem statement)
- However, moderator is still making final decision (not AI), so accountability remains human
- If pattern emerges (AI briefs consistently misleading), moderators lose trust in AI system and revert to manual context gathering (eliminating A12 time savings)

**Detection method**:  
- Moderator feedback on AI briefs ("helpful" vs. "missing key context" rating)
- Appeal rate on grey-zone decisions (if >5%/month, suggests poor decision quality)
- Moderator time tracking (if grey-zone review time creeps back toward 8 min from 4 min per A12, suggests AI briefs aren't useful)

**Mitigation**:  
- **Design**: AI brief includes links to raw data (moderator can verify if suspicious)
- **Training**: Moderators trained to spot-check AI context, especially for high-stakes cases (IP claims, doxxing)
- **Feedback loop**: Weekly review of "unhelpful" brief ratings to improve AI context gathering
- **Transparency**: AI brief includes confidence score on context accuracy (e.g., "User history: 5 commercial posts [high confidence], community standing: positive [medium confidence]")
- **Escalation**: If >20% of briefs rated "unhelpful" in a week, trigger review of AI context gathering logic

---

### Handoff 4: Human Grey-Zone Decision → AI Learning (Future State)

**What could go wrong**: AI learns from inconsistent human decisions, perpetuating or amplifying moderator biases

**Probability**: Medium (depends on U3 - moderator agreement rate)  
- If U3 reveals <70% moderator agreement on grey-zones, AI trained on this data will learn inconsistency
- Example: Moderator A allows harsh critique, Moderator B removes it → AI learns conflicting patterns
- Over time, AI recommendations become unreliable, moderators stop trusting system

**Impact**: Medium  
- Doesn't create immediate trust damage (humans still make final decisions)
- But undermines long-term goal of AI learning recurring grey-zone patterns (per U4)
- If AI can't learn patterns, system remains stuck at "AI provides context only" (no further automation possible)

**Detection method**:  
- Inter-rater reliability analysis (per U3 discovery)
- Pattern analysis of moderator decisions (per U4 discovery)
- AI confidence scores on pattern matching (if confidence stays low after 6 months of training, suggests inconsistent training data)

**Mitigation**:  
- **Prerequisite**: Resolve U3 (moderator agreement) before attempting AI learning on grey-zones
- **Calibration**: Monthly moderator calibration sessions (review 10 grey-zone cases together, discuss reasoning, align on policy interpretation)
- **Documentation**: Mandatory decision rationale for all grey-zones (creates structured training data)
- **Selective learning**: AI only learns from cases where 2+ moderators agree (filters out inconsistent decisions)
- **Human oversight**: Any AI pattern recommendation requires human validation before deployment

---

### Handoff 5: AI Auto-Action → Audit Process

**What could go wrong**: Audit sample is too small or non-representative, missing systematic AI errors

**Probability**: Medium  
- Per A13, 30 min/day = ~120 posts reviewed = ~1% of auto-actioned volume
- If AI has systematic bias (e.g., incorrectly flags all posts with certain keywords), 1% sample may miss it
- Example: AI incorrectly removes all posts mentioning "Warhammer" (trademark concern), but audit sample doesn't catch this pattern for 2 weeks

**Impact**: Medium  
- Systematic errors affect more users than random errors
- Longer time to detection = more trust damage
- However, user appeals should catch systematic errors faster than audit (users affected by same error will appeal in clusters)

**Detection method**:  
- **Primary**: User appeal clustering (if 5+ appeals mention same issue in 24 hours, triggers alert)
- **Secondary**: Audit sample stratification (ensure sample covers all violation types, not just most common)
- **Tertiary**: Monthly full audit of 1,000 random auto-actions (10x daily sample)

**Mitigation**:  
- **Design**: Audit sample is stratified by violation type (not purely random)
- **Alert system**: Automated detection of appeal clusters (3+ appeals on same keyword/pattern in 24 hours triggers immediate investigation)
- **Escalation**: If audit finds systematic error, immediate halt of AI auto-action in that category until fixed
- **Transparency**: Public changelog of AI errors caught and fixed (builds community trust in oversight process)

---

## Conclusion: Delegation Architecture Summary

This delegation architecture reflects the core insight from the problem statement: **the goal is not to automate 97% of moderation, but to eliminate 63% of moderator cognitive load (68.3 hours/day) while maintaining zero tolerance for trust-damaging errors in grey-zone cases.**

The architecture achieves this through:

1. **Fully Agentic** work (48.5% of volume): Low-stakes, high-volume, pattern-based tasks (spam, miscategorization) where false positives are tolerable and recoverable

2. **Agent-Led with Human Oversight** (51.5% of volume): Medium-stakes work (clear violations) and high-stakes identification (grey-zones) where AI provides structure but humans retain decision authority

3. **Human-Led with AI Assistance** (3% of volume): Irreducible human judgment (grey-zone decisions) where AI reduces discovery time but never makes the call

4. **Human-Led Only** (10% of volume): Mandatory oversight (audit) that maintains system trust and calibration

The critical dependencies are:
- **U3 (moderator agreement)**: If low, Work Type 2 must shift to more human oversight
- **U4 (pattern frequency)**: If high, future opportunity to automate recurring grey-zones
- **A11 (95% recall)**: Non-negotiable for grey-zone identification to prevent trust damage
- **A12 (4-min review)**: Key to achieving 63% time savings while maintaining quality

The architecture is designed to fail safely: when uncertain, escalate to humans. The asymmetric risk tolerance ("absorb false positives to avoid false negatives") is embedded in every delegation decision.


