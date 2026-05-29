# Problem Statement with Quantified Success Metrics
## Regional Professional Services Firm: New-Hire Onboarding

---

## 1. Problem Statement

### Current State (Quantified)

A regional professional-services firm with 1,200 employees processes 220+ new hires annually through a 3-person HR Ops team. Each onboarding involves approximately 40 discrete tasks distributed across 6 disconnected systems (Workday, ServiceNow, LMS, email, and at least 2 others) over a 2-week period.

**Capacity Analysis:**
- Annual onboarding volume: 220 hires
- Weekly average: 4.2 new hires (220 ÷ 52 weeks)
- Concurrent onboardings in progress: 8.4 hires (4.2 hires/week × 2-week duration)
- Total active tasks at any moment: ~336 tasks (8.4 hires × 40 tasks)
- Tasks per HR Ops team member: 112 concurrent tasks

**The Stated Request:**
"Automate the paperwork so my team doesn't have to touch routine tasks."

**The Actual Problem:**
The HR Ops team is trapped in a **coordination tax** imposed by system fragmentation and inconsistent edge-case handling, not simply "too much paperwork." The team manages 336 concurrent tasks across 6 systems with 15% requiring judgment calls (~50 judgment calls in flight at any time). Previous automation attempts failed because:

1. **System integration gaps** create manual handoffs that automation cannot bridge without middleware
2. **Edge-case variability** (contractor compliance tracks, cross-seniority buddy matching, late I-9 holds) lacks documented decision logic, making automation brittle
3. **No feedback loop** exists to capture when automated decisions fail, preventing iterative improvement

The real problem is not task volume—it's **context switching cost** and **undocumented institutional knowledge** embedded in judgment calls that prevents reliable automation.

### What They Asked For vs. What They Need

| What They Asked For | What They Actually Need |
|---------------------|-------------------------|
| "Automate the paperwork" | Decision-support tooling for the 15% judgment calls + orchestration layer for the 85% routine tasks |
| End-to-end automation | Supervised automation with human-in-the-loop for edge cases |
| Replace manual work | Reduce context-switching and system-hopping overhead |
| AI infrastructure | Integration middleware + decision logic documentation + selective AI augmentation |

### Explicit Constraints

1. **No AI infrastructure** currently exists (no LLM access, no vector databases, no agent frameworks)
2. **6 heterogeneous systems** with unknown API maturity (Workday, ServiceNow, LMS, email, +2 unspecified)
3. **3-person team** cannot absorb implementation overhead without backfilling capacity
4. **220 hires/year** provides limited training data for ML approaches (~18 hires/month)
5. **15% judgment-call rate** means ~33 hires/year hit edge cases requiring human expertise
6. **2-week onboarding window** creates tight SLA for error detection and recovery

---

## 2. Assumptions

### A1: Time per Onboarding Task
**Assumed Value:** 15 minutes average per task (range: 5 min for routine data entry to 45 min for judgment calls)

**Reasoning:** 
- 40 tasks × 15 min = 600 minutes (10 hours) per hire
- 220 hires × 10 hours = 2,200 hours annually
- Distributed across 3 FTEs = 733 hours/person/year
- At ~1,800 billable hours/year per FTE (accounting for PTO, meetings, admin), this represents 41% of team capacity
- Remaining 59% allocated to: onboarding process exceptions (15% of cases), employee relations issues, process improvement, and other HR Ops duties
- Industry benchmark: HR Ops teams in professional services spend 35-50% of time on onboarding during growth phases (SHRM 2022 benchmarks)

### A2: Fully Burdened Cost per HR Ops Team Member
**Assumed Value:** $75,000 annual fully-burdened cost ($36/hour)

**Reasoning:**
- Regional professional services firm suggests mid-tier market (not Big 4, not small local)
- HR Ops roles in this segment: $50-60K base salary
- Fully-burdened multiplier of 1.3-1.5× for benefits, payroll taxes, overhead, systems
- $75K represents conservative mid-point
- Hourly rate: $75,000 ÷ 2,080 hours = $36/hour

### A3: Current Error Rate in Onboarding
**Assumed Value:** 8% of onboardings experience at least one material error (18 hires/year)

**Reasoning:**
- "Something falls through the cracks" suggests errors occur regularly but not constantly
- 6 systems with manual handoffs create multiple failure points
- 15% judgment-call rate provides upper bound (if all judgment calls failed)
- Industry benchmark: Manual multi-system processes typically see 5-12% error rates (Gartner IT Process Automation research)
- 8% represents mid-range estimate: 220 hires × 8% = 17.6 ≈ 18 hires/year

### A4: Cost per Onboarding Error
**Assumed Value:** $450 per error (3 hours remediation time across HR Ops + hiring manager + new hire)

**Reasoning:**
- HR Ops remediation: 1.5 hours @ $36/hour = $54
- Hiring manager time: 1 hour @ $125/hour (mid-level manager rate in professional services) = $125
- New hire disruption: 0.5 hours @ $85/hour (blended rate for new professional services hire) = $43
- System correction overhead, re-processing: 0.5 hours @ $36/hour = $18
- Intangible costs (new hire experience degradation, manager frustration): ~$210 (estimated as 1.5× tangible costs)
- Total: $450 per error
- Annual error cost: 18 errors × $450 = $8,100

### A5: Distribution of Routine vs. Judgment Tasks
**Assumed Value:** 
- 85% of tasks (34 per hire) are routine and deterministic
- 15% of tasks (6 per hire) require judgment or edge-case handling

**Reasoning:**
- Scenario explicitly states "roughly 15% require judgment calls"
- Applied uniformly: 40 tasks × 15% = 6 judgment tasks per hire
- Judgment tasks likely concentrated in: compliance track assignment (1), buddy matching (1), late document handling (2), cross-functional handoffs (2)

### A6: Time Distribution Between Routine and Judgment Tasks
**Assumed Value:**
- Routine tasks: 10 minutes average (34 tasks × 10 min = 340 min = 5.7 hours)
- Judgment tasks: 45 minutes average (6 tasks × 45 min = 270 min = 4.5 hours)
- Total per hire: 10.2 hours (aligns with A1's 10-hour estimate)

**Reasoning:**
- Judgment tasks require: context gathering across systems (15 min), decision-making (15 min), documentation (10 min), stakeholder communication (5 min)
- Routine tasks: data entry (5 min), verification (3 min), system navigation (2 min)
- Weighted average: (34 × 10 + 6 × 45) ÷ 40 = 15.25 minutes (consistent with A1)

### A7: Context-Switching Overhead
**Assumed Value:** 25% time overhead due to system fragmentation (switching between 6 systems)

**Reasoning:**
- Research on task-switching shows 20-40% productivity loss when alternating between disparate systems (Microsoft Research, "The Cost of Interrupted Work")
- 6 systems means average of 6.7 system switches per hire (40 tasks ÷ 6 systems)
- Each context switch: re-authentication, navigation, mental model reload
- 25% overhead means 10 hours of productive work requires 12.5 hours of elapsed time
- Annual overhead: 2,200 hours × 25% = 550 hours wasted on context-switching

### A8: AI Infrastructure Implementation Timeline
**Assumed Value:** 6-9 months to production-ready agentic workflow

**Reasoning:**
- No existing AI infrastructure means building from scratch:
  - Month 1-2: System API discovery and integration architecture
  - Month 2-4: Middleware/orchestration layer development
  - Month 3-5: Decision logic documentation and codification
  - Month 5-7: Agent development and testing
  - Month 7-9: Pilot, iteration, and rollout
- Professional services firm likely has limited engineering resources for internal tools
- Complexity of 6-system integration is primary timeline driver, not AI components

### A9: Token Costs for LLM Operations
**Assumed Value:** $0.15 per hire for LLM inference costs

**Reasoning:**
- 6 judgment calls per hire requiring LLM reasoning
- Each judgment call: ~2,000 input tokens (context) + 500 output tokens (decision + reasoning)
- Total per hire: 15,000 tokens
- Using GPT-4o pricing: $5/1M input tokens, $15/1M output tokens
- Cost per hire: (12,000 × $5 + 3,000 × $15) ÷ 1,000,000 = $0.105 ≈ $0.15 with overhead
- Annual LLM cost: 220 hires × $0.15 = $33

### A10: Automation Success Rate Target
**Assumed Value:** 95% of routine tasks (85% of total) can be reliably automated with orchestration layer

**Reasoning:**
- Routine tasks are deterministic by definition
- 5% failure rate accounts for: API downtime, data quality issues, unexpected system changes
- Judgment tasks remain human-supervised (not fully automated)
- Industry benchmark: RPA/workflow automation achieves 92-98% reliability for rule-based processes (Forrester RPA research)

### A11: HR Ops Team Capacity Reallocation
**Assumed Value:** Time saved from automation will be reallocated to:
- 40% → Handling exceptions and edge cases more thoroughly
- 30% → Process improvement and documentation
- 20% → Strategic HR initiatives (retention, culture, DEI)
- 10% → Headcount reduction or growth absorption

**Reasoning:**
- Professional services firms rarely reduce headcount for efficiency gains; they reallocate to growth
- 220 hires/year suggests ~15-18% annual growth rate (220 ÷ 1,200)
- Growing firms need HR Ops capacity for scaling, not just onboarding
- Assumption enables capacity-based ROI calculation rather than pure cost reduction

---

## 3. Success Metrics

### Metric 1: HR Ops Time per Onboarding
**Description:** Total HR Ops team hours spent per completed onboarding, including routine tasks, judgment calls, and error remediation.

**Current Baseline:** 12.5 hours per hire
- Productive work: 10.2 hours (A1, A6)
- Context-switching overhead: 2.3 hours (A7: 25% of 10.2 hours)
- Error remediation (amortized): 0.07 hours per hire (18 errors × 1.5 HR hours ÷ 220 hires, from A3, A4)
- **Total: 12.5 hours per hire**
- **Annual team capacity consumed: 2,750 hours (12.5 × 220)**

**Target:** 4.5 hours per hire (64% reduction)
- Routine tasks automated: 5.7 hours saved (34 tasks × 10 min, A6)
- Context-switching eliminated for automated tasks: 1.4 hours saved (25% of 5.7 hours)
- Judgment tasks remain: 4.5 hours (6 tasks × 45 min, A6)
- Error remediation reduced by 60%: 0.04 hours (assumes automation reduces error rate from 8% to 3%)
- **Target: 4.5 hours per hire**
- **Annual team capacity consumed: 990 hours (4.5 × 220)**
- **Capacity freed: 1,760 hours/year (64% reduction)**

**Measurement Method:** 
- Time-tracking tags in HR Ops team's task management system (ServiceNow or equivalent)
- Weekly retrospective sampling: 4 random onboardings per week, detailed time logs
- Monthly aggregation and trend analysis

**Dependencies:** A1, A6, A7, A10

**Indicator Type:** Leading indicator (process metric)

---

### Metric 2: Onboarding Error Rate
**Description:** Percentage of onboardings that experience at least one material error requiring remediation (missed tasks, incorrect system provisioning, compliance gaps, mismatched buddy assignments).

**Current Baseline:** 8% (18 hires per year experience errors, A3)

**Target:** 3% (7 hires per year, 62.5% reduction)
- Routine task errors eliminated by automation: ~5% reduction (assumes most errors occur in routine tasks due to manual handoffs)
- Judgment task errors remain but with better documentation: ~3% residual
- **Target: 3% error rate**

**Measurement Method:**
- Error tracking log maintained by HR Ops team
- Error definition: Any task requiring re-work after initial completion, or discovered during 30-day checkpoint
- Monthly audit: HR Ops lead reviews all completed onboardings for errors
- Categorization: Routine task error vs. judgment task error

**Dependencies:** A3, A10

**Indicator Type:** Lagging indicator (outcome metric)

---

### Metric 3: System Context Switches per Onboarding
**Description:** Number of times HR Ops team members must switch between different systems (Workday, ServiceNow, LMS, email, etc.) to complete one onboarding.

**Current Baseline:** 40 context switches per hire
- 40 tasks across 6 systems, assuming each task requires at least one system interaction
- Some tasks require multiple systems (e.g., create Workday record → trigger ServiceNow ticket → verify in email)
- Conservative estimate: 1 switch per task = 40 switches per hire

**Target:** 6 context switches per hire (85% reduction)
- Orchestration layer handles 34 routine tasks automatically
- HR Ops only accesses systems for 6 judgment tasks
- **Target: 6 switches per hire**

**Measurement Method:**
- Browser plugin or screen-tracking software (with employee consent) to log application switches
- Weekly sampling: 2 onboardings per week tracked in detail
- Self-reported logs as backup: HR Ops team logs system switches for 1 week per month

**Dependencies:** A5, A7

**Indicator Type:** Leading indicator (process metric)

---

### Metric 4: Time to First Productive Day
**Description:** Calendar days from hire start date to completion of all onboarding tasks enabling full productivity (IT access provisioned, compliance training assigned, manager handoff complete).

**Current Baseline:** 14 calendar days (2-week onboarding window stated in scenario)
- Assumes tasks are completed sequentially or with limited parallelization due to manual coordination
- Some tasks block others (e.g., IT provisioning must complete before LMS access)

**Target:** 7 calendar days (50% reduction)
- Automation enables parallel task execution (e.g., IT provisioning, benefits enrollment, LMS setup triggered simultaneously)
- Judgment tasks no longer bottlenecked by routine task backlog
- **Target: 7 days to full productivity**

**Measurement Method:**
- Automated tracking via orchestration system: timestamp of hire start date → timestamp of final task completion
- Validated against manager survey: "On what date was [new hire] able to perform their role without onboarding blockers?"
- Monthly reporting with median and 90th percentile values

**Dependencies:** A8, A10

**Indicator Type:** Lagging indicator (outcome metric)

---

### Metric 5: Cost per Onboarding (HR Ops Labor Only)
**Description:** Fully-burdened HR Ops labor cost to complete one onboarding, excluding benefits costs, IT hardware, or other non-labor expenses.

**Current Baseline:** $450 per hire
- 12.5 hours per hire (from Metric 1 baseline) × $36/hour (A2)
- **Baseline: $450 per hire**
- **Annual HR Ops onboarding cost: $99,000 (450 × 220)**

**Target:** $162 per hire (64% reduction)
- 4.5 hours per hire (from Metric 1 target) × $36/hour (A2)
- **Target: $162 per hire**
- **Annual HR Ops onboarding cost: $35,640 (162 × 220)**
- **Annual savings: $63,360**

**Additional Cost Considerations:**
- LLM inference costs: $33/year (A9)
- Orchestration platform costs: ~$15,000/year (estimated SaaS middleware platform like Workato or Zapier Enterprise)
- **Net annual savings: $48,327 ($63,360 - $15,033)**
- **Payback period on implementation: ~9-12 months** (assuming $50-60K implementation cost per A8)

**Measurement Method:**
- Calculated metric derived from Metric 1 (time per onboarding) × hourly rate (A2)
- Monthly financial reporting
- Annual reconciliation against HR Ops team capacity allocation

**Dependencies:** A1, A2, A6, A7, A9

**Indicator Type:** Lagging indicator (outcome metric)

---

## 4. Unknowns

### Critical Unknowns (Must Resolve Before Specification)

#### U1: API Maturity and Integration Feasibility
**What's Missing:** 
- Do all 6 systems expose APIs? Which require screen-scraping or manual workarounds?
- What is the authentication model for each system (OAuth, SAML, API keys)?
- Are there rate limits or usage restrictions that would throttle automation?
- What is the data quality in source systems (completeness, consistency, timeliness)?

**Why Critical:** 
- Determines whether orchestration layer is feasible or requires expensive custom middleware
- Affects implementation timeline (A8) by 3-6 months if APIs don't exist
- May force hybrid automation approach (some systems automated, others remain manual)

**Discovery Questions:**
1. "Can you provide API documentation or developer portal access for Workday, ServiceNow, and your LMS?"
2. "What are the two unspecified systems used in onboarding, and do they have integration capabilities?"
3. "Has IT attempted any system integrations previously? What blockers did they encounter?"
4. "What is your IT team's capacity to support integration work, or would this require external consultants?"

**Risk if Wrong:** 
- High risk: Could invalidate entire automation approach if key systems lack APIs
- May require fallback to RPA (robotic process automation) with higher maintenance costs

---

#### U2: Decision Logic Documentation for Judgment Calls
**What's Missing:**
- What are the specific rules for determining compliance tracks (contractor vs. FTE vs. intern)?
- What defines "seniority norms" for buddy matching? Are there written guidelines?
- What triggers a late I-9 hold, and what's the remediation process?
- Are there other judgment calls beyond the three examples provided?

**Why Critical:**
- Determines whether AI can provide decision support or if logic is purely tacit knowledge
- Affects the 15% judgment-call rate (A5)—may be higher if undocumented edge cases exist
- Influences whether solution is "agentic AI" vs. "decision tree + human approval"

**Discovery Questions:**
1. "Can you walk me through the last 5 onboardings that required judgment calls? What made them edge cases?"
2. "Do you have written policies for compliance track assignment, buddy matching, and document deadline handling?"
3. "How often do two team members make different decisions on similar edge cases?"
4. "What percentage of judgment calls are truly novel vs. recurring patterns you haven't documented?"

**Risk if Wrong:**
- Medium risk: Overestimating automation potential for judgment tasks
- May result in high false-positive rate (AI suggests incorrect decisions) and user distrust

---

#### U3: Current Error Types and Root Causes
**What's Missing:**
- What are the most common errors? (e.g., missed IT provisioning, incorrect compliance training, buddy mismatch)
- Are errors concentrated in specific systems or task types?
- How are errors currently detected? (proactive monitoring vs. new hire complaints vs. 30-day checkpoint)
- What's the time-to-detection for errors? (same day vs. weeks later)

**Why Critical:**
- Determines which tasks to prioritize for automation (highest error-prone tasks first)
- Affects error rate assumptions (A3) and cost per error (A4)
- Influences monitoring and alerting requirements for automated system

**Discovery Questions:**
1. "Can you share error logs or incident reports from the past 6 months of onboardings?"
2. "What's the most painful error you've encountered? What caused it?"
3. "How do you typically discover that something went wrong in an onboarding?"
4. "Have you ever had a compliance issue (e.g., I-9 violation) result from an onboarding error?"

**Risk if Wrong:**
- Medium risk: Automating low-error tasks while leaving high-error tasks manual
- Could result in no improvement to Metric 2 (error rate) despite automation

---

#### U4: Stakeholder Tolerance for Automation Errors
**What's Missing:**
- How do hiring managers react when onboarding errors occur?
- What's the tolerance for "new" types of errors introduced by automation?
- Is there executive sponsorship for an automation initiative, or is this HR Ops-driven?
- What's the firm's risk appetite for compliance-related automation (I-9, background checks)?

**Why Critical:**
- Determines acceptable error rate for automated system (affects target for Metric 2)
- Influences human-in-the-loop requirements (full automation vs. approval workflows)
- Affects change management strategy and rollout approach

**Discovery Questions:**
1. "If an automated system made the same 8% error rate as today, but different types of errors, would that be acceptable?"
2. "Who needs to approve an automation initiative like this? What concerns would they raise?"
3. "Have you had any compliance audits or near-misses related to onboarding in the past 2 years?"
4. "What would make you shut down an automated onboarding system?"

**Risk if Wrong:**
- High risk: Building a system that's technically sound but organizationally rejected
- Could result in "shelfware" if stakeholders don't trust automated decisions

---

### Important Unknowns (Resolve During Implementation)

#### U5: Task Dependency Mapping
**What's Missing:**
- Which of the 40 tasks must be completed sequentially vs. can run in parallel?
- What are the blocking dependencies? (e.g., Workday record must exist before ServiceNow ticket)
- Are there timing constraints? (e.g., benefits enrollment must complete 3 days before start date)

**Why Important:**
- Affects time-to-first-productive-day reduction (Metric 4)
- Influences orchestration logic complexity
- Determines maximum theoretical speedup from parallelization

**Discovery Approach:**
- Process mapping workshop with HR Ops team (4-hour session)
- Observation of 3-5 live onboardings to document actual workflow
- Can be deferred until implementation phase

---

#### U6: Seasonal Hiring Patterns
**What's Missing:**
- Are the 220 hires evenly distributed, or are there hiring surges (e.g., summer interns, post-grad recruiting)?
- What's the peak concurrent onboarding load?
- Does the team scale up during busy periods (temps, overtime)?

**Why Important:**
- Affects capacity calculations and ROI (A1, A11)
- Determines whether automation should handle peak load or average load
- Influences infrastructure sizing (concurrent workflow executions)

**Discovery Approach:**
- Request monthly hiring data for past 2 years
- Interview HR Ops lead about peak periods and how team copes
- Can be resolved during discovery phase

---

#### U7: New Hire Demographics and Edge Case Distribution
**What's Missing:**
- What percentage of hires are: FTEs, contractors, interns, executives, remote vs. on-site?
- How does onboarding vary by role type, seniority, or location?
- Are the 15% judgment calls evenly distributed or concentrated in specific hire types?

**Why Important:**
- Affects judgment call rate (A5) and automation success rate (A10)
- Determines whether single workflow can handle all hire types or needs branching logic
- Influences training data requirements if using ML approaches

**Discovery Approach:**
- Request hire type breakdown from Workday
- Interview HR Ops team about which roles are "easy" vs. "complex" to onboard
- Can be resolved during discovery phase

---

### Safely Deferrable Unknowns

#### U8: Employee Experience Impact
**What's Missing:**
- How do new hires currently perceive onboarding quality?
- What's the correlation between onboarding errors and early turnover?
- Do hiring managers see onboarding delays as a problem?

**Why Deferrable:**
- Not required for technical feasibility or ROI justification
- Can be measured post-implementation as validation
- Qualitative data is less critical than operational metrics for this use case

---

#### U9: Competitive Landscape
**What's Missing:**
- Are peer firms automating onboarding? What tools are they using?
- Is onboarding speed/quality a recruiting differentiator in this market?

**Why Deferrable:**
- Doesn't affect technical solution design
- Internal efficiency gains justify project without competitive pressure
- Can inform messaging and change management but not core requirements

---

## Summary of Risk-Weighted Unknowns

| Unknown | Risk if Wrong | Must Resolve Before |
|---------|---------------|---------------------|
| U1: API Maturity | High | Specification |
| U2: Decision Logic | Medium | Specification |
| U3: Error Types | Medium | Specification |
| U4: Stakeholder Tolerance | High | Specification |
| U5: Task Dependencies | Medium | Implementation |
| U6: Seasonal Patterns | Low | Implementation |
| U7: Hire Demographics | Low | Implementation |
| U8: Employee Experience | Low | Post-launch |
| U9: Competitive Landscape | Low | Post-launch |

**Recommended Discovery Sequence:**
1. **Week 1:** System integration assessment (U1) + stakeholder interviews (U4)
2. **Week 2:** Error analysis (U3) + decision logic documentation (U2)
3. **Week 3:** Process mapping workshop (U5) + data requests (U6, U7)
4. **Week 4:** Synthesis and specification

---

## Appendix: Economic Model

### Current State Annual Costs
- HR Ops labor: $99,000 (220 hires × $450/hire, Metric 5)
- Error remediation: $8,100 (18 errors × $450/error, A3, A4)
- Context-switching productivity loss: $19,800 (550 hours × $36/hour, A7)
- **Total annual cost: $126,900**

### Future State Annual Costs (Post-Automation)
- HR Ops labor: $35,640 (220 hires × $162/hire, Metric 5)
- Error remediation: $3,150 (7 errors × $450/error, Metric 2 target)
- Orchestration platform: $15,000/year (estimated)
- LLM inference: $33/year (A9)
- **Total annual cost: $53,823**

### Net Annual Savings
- **$73,077 per year** ($126,900 - $53,823)
- **Payback period: 8-10 months** (assuming $50-60K implementation cost)
- **3-year NPV: ~$180K** (at 10% discount rate)

### Capacity Freed for Reallocation
- **1,760 hours per year** (64% of current onboarding time, Metric 1)
- **Equivalent to 0.85 FTE** (1,760 ÷ 2,080 hours)
- **Value of reallocation** (A11):
  - 40% → Exception handling: 704 hours (improves quality, reduces escalations)
  - 30% → Process improvement: 528 hours (compounds efficiency gains)
  - 20% → Strategic HR: 352 hours (retention, culture initiatives)
  - 10% → Growth absorption: 176 hours (enables 10% hiring growth without headcount)

---

**Document Prepared By:** AI Forward Deployed Engineer  
**Date:** 2025-01-28  
**Version:** 1.0  
**Status:** Ready for Discovery Validation