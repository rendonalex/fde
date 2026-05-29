# Discovery Questions: Scenario 5 — Small-Clinic Patient Intake
## Westbridge Family Medicine

**Status**: ✅ **ALL 20 QUESTIONS ANSWERED** (see `scenario5-dana-answers.md` for complete responses)

**Purpose**: Design-changing questions for coach role-play sessions. These questions close critical assumptions and surface lived-practice details that would materially alter agent design, delegation boundaries, or implementation approach.

**Question Selection Criteria**:
- Answers would change design decisions (not just add context)
- Focus on lived practice vs. documented SOP
- Probe prior automation history and failure modes
- Surface system edge cases and workarounds
- Clarify stakeholder priorities and constraints

**Organized by priority**: Critical (answer before design), High (answer before scoping), Medium (answer before build).

---

## Critical Priority: Must Answer Before Design

### Prior Authorization Workflow

**Q1**: Can you walk me through your PA chase process for one specific payer — say, UnitedHealthcare Choice? What specific steps do you take, when do you chase, and what information tells you it's time to escalate vs. wait another day?

**Why this matters**: A05, A06. Dana's Google Sheets chase list encodes payer-specific behavioral patterns. If Dana can articulate the logic ("UHC is always 6 days, so I don't chase before day 6, but I always chase on day 6 because they'll never respond on day 5"), that logic is encodable as agent rules. If the logic is pure intuition ("I just know when to chase"), it's harder to automate. This determines whether PA chase can be agent-led or must remain human-led with agent support.

**What would change the design**:
- If Dana's rules are articulable → agent can encode payer-specific chase timing and automate status checks
- If Dana's rules are intuitive/tacit → agent can only remind Dana to check, not execute chases autonomously

---

**Q2**: When you submit a PA to Wellpath for colonoscopy, you include the prior visit note even though the form doesn't ask for it. How did you learn that workaround? Are there other payer-specific workarounds like this that aren't documented anywhere?

**Why this matters**: A05. Artefact 5.1 footnote documents Wellpath pattern. If there are 5–10 other payer-specific workarounds, those represent high-value tribal knowledge to encode. If Wellpath is the only one, automation priority is lower.

**What would change the design**:
- If many workarounds exist → high ROI from encoding them into agent PA submission logic
- If Wellpath is an isolated case → lower priority; focus agent effort elsewhere

---

**Q3**: In Artefact 5.2, patient TJ arrived for a visit and the PA for the MRI was still pending. The physician's note says front desk didn't flag this at check-in. Walk me through your current check-in workflow — is there a step where staff are supposed to check PA status, or is that step missing?

**Why this matters**: A07. If PA status check is missing from the workflow, agent can add it (high-value intervention). If the step exists but staff skip it because it's cumbersome, agent can make it faster/easier (medium-value intervention). If the step exists and is usually followed but this was a one-off miss, agent value is lower.

**What would change the design**:
- If step is missing → agent provides day-of-visit PA status alert at check-in (high priority)
- If step exists but is skipped → agent makes check faster (auto-lookup from athenahealth or payer portal)
- If this was an isolated miss → lower priority; focus agent effort elsewhere

---

### Visit-Reason Triage & Clinical Escalation

**Q4**: When a patient writes "chest discomfort" on their intake form, what happens next? Who decides whether that's urgent (escalate to physician immediately) vs. routine (wait for scheduled visit time)? Is there a written list of red-flag symptoms, or do staff just know?

**Why this matters**: A09, A10. Hard constraint #2 requires "clear human escalation path" for visit reasons. If front-desk staff have documented triage protocols, agent can apply them consistently. If protocols are informal, agent design must include very conservative escalation threshold (over-escalate to be safe) or require human review of every ambiguous case (less automation value).

**What would change the design**:
- If documented protocols exist → agent applies them, escalates per rules
- If protocols are informal → agent must escalate conservatively (may create physician alert fatigue)
- If no protocols exist → agent can help formalize them before deployment

---

**Q5**: Have you ever had a case where a patient's self-reported visit reason at intake turned out to be much more urgent than it seemed, and front desk didn't catch it? What happened?

**Why this matters**: Identifies lived failure mode that would inform agent escalation design. If there's a known incident where under-triage caused patient harm or near-miss, that shapes risk tolerance (agent must over-escalate to prevent recurrence). If no incidents, risk tolerance may be higher.

**What would change the design**:
- If prior incident exists → agent design prioritizes safety (over-escalate)
- If no prior incidents → agent can be tuned for balance (not just safety-first)

---

### Insurance Verification Edge Cases

**Q6**: Artefact 5.3 shows a patient who was billed as self-pay because their insurance verification was 10 months old, even though they had continuous Aetna coverage. The note says "this is the third time." What causes verifications to go stale — is it that staff forget to re-verify, or is there no system reminder?

**Why this matters**: A02. If athenahealth has a built-in staleness alert that staff aren't using, solution is training/process change (not agent). If athenahealth doesn't have the feature, agent can provide it (high value).

**What would change the design**:
- If athenahealth has the alert → agent value is lower (process issue, not tool gap)
- If athenahealth doesn't have the alert → agent auto-triggers re-verification (high-value feature)

---

**Q7**: Of the 30% of insurance verifications that fail auto-verify via Availity, how many are because of Availity API issues (timeout, payer not in system) vs. actual patient eligibility problems (coverage lapsed, wrong plan)?

**Why this matters**: A01. If system failures dominate, agent can retry API calls, improve payer configuration, or use fallback eligibility sources. If patient failures dominate, agent needs to prompt patients for updated insurance info before visit.

**What would change the design**:
- If API/system failures dominate → agent focuses on API reliability (retries, fallbacks)
- If patient failures dominate → agent focuses on patient communication (portal reminders, pre-visit insurance updates)

---

## High Priority: Must Answer Before Scoping

### Medication Reconciliation & DoseSpot Gaps

**Q8**: You mentioned that medication reconciliation is "especially complex for self-pay or Medicaid managed-care patients." What specifically makes it complex? Is it that DoseSpot doesn't pull from their pharmacies, or that they use multiple pharmacies, or something else?

**Why this matters**: A11. If DoseSpot has coverage gaps (small pharmacies, assistance programs), agent can prompt patients for those specific sources during intake interview. If complexity is that patients can't remember their meds, agent interview structure won't help much.

**What would change the design**:
- If DoseSpot gaps are the issue → agent prompts for OTC, samples, mail-order, assistance programs
- If patient memory is the issue → agent can't add much value (still human-led)

---

**Q9**: When a patient says they stopped taking a medication or started a new one from a specialist, what do front-desk staff do? Do they update the med list in athenahealth immediately, or just flag it for the physician to review during the visit?

**Why this matters**: A12. Determines agent's delegation boundary. If staff update immediately (with physician confirmation later), agent can do the same. If staff only flag (never update), agent must follow same rule.

**What would change the design**:
- If staff update immediately → agent can update med list + flag for physician review
- If staff only flag → agent documents change but doesn't update med list (physician-only action)

---

### System Integration & Tool Gaps

**Q10**: You maintain a PA chase list in Google Sheets instead of using athenahealth's PA tracking module. What's missing in athenahealth that made you build your own system?

**Why this matters**: A06. If athenahealth's PA module is missing critical features (custom chase timing, payer-specific notes), agent needs to replace Google Sheets with a shared system (not just integrate with athenahealth). If athenahealth's module is fine but Dana prefers her own setup, integration approach is different.

**What would change the design**:
- If athenahealth lacks features → agent builds full PA chase management (parallel system or athenahealth add-on)
- If athenahealth is adequate but not used → agent integrates with athenahealth, surfaces PA data more accessibly

---

**Q11**: Can you access PA submission status, notes, and approval/denial results from athenahealth via an API, or is that information only visible in the athenahealth user interface?

**Why this matters**: A15. Determines whether agent can pull PA data from athenahealth programmatically or needs manual data entry (like Dana's Google Sheets).

**What would change the design**:
- If PA data is API-accessible → agent integrates directly with athenahealth
- If PA data is UI-only → agent operates as parallel system (requires manual input or screen scraping)

---

### HIPAA, Compliance, and Risk Constraints

**Q12**: Have you checked with your malpractice insurance carrier or HIPAA compliance advisor about using AI for patient intake tasks? Are there specific constraints or requirements they've mentioned — like human-in-the-loop for certain decisions, or audit trail requirements?

**Why this matters**: A17. Hard constraint #3 is "HIPAA and state medical-records compliance is non-negotiable." If malpractice insurance requires human review of all agent outputs (not just escalations), that fundamentally changes agent design (agent becomes recommendation engine, not execution engine).

**What would change the design**:
- If malpractice requires human review of all agent actions → agent is human-led + agent support (not agent-led)
- If HIPAA requires specific audit trails → agent design must include detailed logging
- If no specific constraints → agent has more autonomy (within hard constraints)

---

**Q13**: For athenahealth and Availity, do you have Business Associate Agreements (BAAs) in place? If we add an AI agent that accesses patient data, would that require a new BAA or additional compliance review?

**Why this matters**: Determines procurement timeline and compliance overhead. If new BAA required, implementation timeline extends by 3–6 months (legal review, vendor negotiation).

**What would change the design**:
- If new BAA required → implementation roadmap must account for legal/compliance lead time
- If no new BAA required (agent runs within existing athenahealth/Availity infrastructure) → faster deployment

---

### Prior Automation History

**Q14**: Have you tried any automation or process-improvement projects at Westbridge before (for intake or other workflows)? What worked, what didn't, and what did you learn?

**Why this matters**: Identifies past failures that stakeholder will compare new agent to. If prior automation attempt failed because it was too rigid or didn't handle exceptions, agent design must explicitly address flexibility. If no prior attempts, stakeholder may have unrealistic expectations (positive or negative).

**What would change the design**:
- If prior automation failed due to rigidity → agent design emphasizes graceful exception handling
- If prior automation failed due to staff resistance → change management becomes priority (not just technical design)
- If no prior attempts → need to set realistic expectations about agent capabilities and limitations

---

## Medium Priority: Refine During Build

### Operational Context

**Q15**: How long does it take a new front-desk hire to get fully up to speed on all intake tasks, especially the non-obvious stuff like PA chase timing and Medicaid MCO verification? What's the hardest part for new staff to learn?

**Why this matters**: A18. Quantifies ROI from encoding tribal knowledge. If onboarding takes 6 months and PA chase is the hardest part, automating PA chase has high value (reduces onboarding time + reduces dependency on Dana). If onboarding is 4 weeks and PA is easy, agent value is lower.

**What would change the design**:
- If onboarding is long and PA is hard → high priority to encode Dana's PA rules into agent
- If onboarding is short → agent ROI comes from volume reduction, not knowledge transfer

---

**Q16**: How do the ~180 daily patients split across your two locations? Is one site consistently busier, or does volume vary day-to-day?

**Why this matters**: A19. If volume distribution is uneven, agent deployment may need to be location-specific (or staff may need to use agent remotely when covering the busier site). If volume is evenly split, simpler deployment.

**What would change the design**:
- If uneven split → agent must be accessible remotely (cloud-based, not site-specific desktop install)
- If even split → site-specific deployment is fine

---

**Q17**: What percentage of your patients complete the pre-visit questionnaire via the patient portal vs. filling out paper forms at check-in?

**Why this matters**: A08. Determines whether agent should prioritize portal-based intake (if adoption is high) or front-desk-assisted intake (if adoption is low). If 30%+ still use paper, agent must support dual workflows.

**What would change the design**:
- If portal adoption is >80% → agent can focus on portal-based automation
- If portal adoption is <70% → agent must support front-desk data entry from paper forms

---

### Stakeholder Motivation & Change Management

**Q18**: The senior physician asked you to "look at this AI thing." What does success on this project mean for you personally? Is this something you're excited about, or is it something you're being asked to do?

**Why this matters**: A20. If Dana is personally invested (sees this as career-advancing or workload-reducing), she'll be a strong internal champion. If she's skeptical or sees AI as a threat, change management becomes critical. Understanding motivation shapes how to position the agent (as Dana's assistant vs. Dana's replacement).

**What would change the design**:
- If Dana is excited → agent can be positioned as "scaling Dana's expertise"
- If Dana is skeptical → agent must be positioned carefully (augmentation, not replacement)

---

**Q19**: If an AI agent could take one task completely off your plate, which would it be? What's the most exhausting or frustrating part of intake right now?

**Why this matters**: Identifies highest-value use case from Dana's perspective (not just from volume × value analysis). If Dana says "PA chase is exhausting," that validates A05/A06. If she says something unexpected ("dealing with angry patients whose visits get canceled because of PA delays"), that's a different problem to solve.

**What would change the design**:
- Validates or redirects use-case prioritization based on stakeholder pain points

---

**Q20**: After the three recent PA misses (Artefact 5.2) and the insurance verification billing errors (Artefact 5.3), is the senior physician worried about specific things — like compliance risk, patient satisfaction, or staff workload? What's driving his interest in AI right now?

**Why this matters**: Clarifies whether stakeholder priority is risk reduction (prevent failures), efficiency (reduce staff time), or patient experience (reduce visit cancellations). This shapes which agent capabilities to prioritize.

**What would change the design**:
- If priority is risk reduction → agent focuses on PA status alerts and verification staleness checks (safety features)
- If priority is efficiency → agent focuses on automating high-volume routine tasks (time savings)
- If priority is patient experience → agent focuses on reducing visit cancellations and billing errors (outcome quality)

---

## Summary: Question Sequencing for Coach Role-Play

**Office hours / first interaction** (answer 5–6 critical questions):
- Q1 (PA chase process walkthrough)
- Q3 (PA status check at check-in — why was it missed?)
- Q4 (visit-reason triage protocols)
- Q6 (insurance verification staleness — system issue or process issue?)
- Q12 (HIPAA/malpractice constraints on AI)

**Mid-week checkpoint** (answer 4–5 high-priority questions):
- Q2 (other payer-specific workarounds beyond Wellpath?)
- Q7 (30% manual verification: API failures vs. patient eligibility?)
- Q10 (why Google Sheets instead of athenahealth PA module?)
- Q14 (prior automation history at Westbridge)
- Q18 (Dana's personal stake in this project)

**Final refinement / ad-hoc interactions** (answer remaining medium-priority questions as needed):
- Q8 (DoseSpot gaps for self-pay/Medicaid patients)
- Q15 (front-desk onboarding time and pain points)
- Q19 (Dana's most exhausting task)
- Q20 (physician's priorities: risk, efficiency, or patient experience?)

**Defer to implementation phase** (if time is short):
- Q5 (prior under-triage incidents)
- Q9 (med list update: immediate vs. flag-only)
- Q11 (athenahealth PA API accessibility)
- Q13 (BAA requirements for AI agent)
- Q16 (volume split across locations)
- Q17 (portal adoption rate)
