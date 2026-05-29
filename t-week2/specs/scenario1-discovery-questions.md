# Discovery Questions — HR Onboarding Coordination
**For Coach Role-Play with Priya Aggarwal, HR Ops Lead**

## Purpose
These questions target design-changing information not in the brief. Each question aims to surface:
- Lived practice vs documented process gaps
- Prior automation lessons
- Hidden constraints or failure modes
- Stakeholder priorities and political dynamics
- System behaviors and edge-case patterns

---

## 1. Automation History & Lessons Learned

**Q1**: What automation or process improvement projects has Aldridge & Sykes tried in HR Ops (or adjacent functions) in the past 3 years, and what happened to them?
- **Design impact**: Reveals risk aversion patterns, vendor relationships, prior failures to avoid
- **Follow-up**: If failed: Why? Technical? Adoption? Political? If succeeded: What made it work?

**Q2**: The brief mentions ServiceNow has "robust auto-routing" but Tom Reeves's laptop ticket failed because "the consulting laptop spec changed last quarter and the auto-routing didn't pick it up." How often do specs or routing rules drift, and who is responsible for keeping them current?
- **Design impact**: Determines if agent needs active spec validation or if this was one-off
- **Closes**: A25 (configuration drift pattern vs one-time miss)

---

## 2. Excel Tracker vs Workday: System of Record Reality

**Q3**: Artefact 1.2 shows you update the Excel tracker first and refresh Workday end-of-week. Walk me through why — what does Excel let you do that Workday doesn't?
- **Design impact**: Reveals whether Excel is workaround or preferred interface; informs agent integration strategy
- **Closes**: A13 (rationale for dual tracking)

**Q4**: The tracker has hidden columns (Notes, Risk flag, Buddy override). What triggers you to populate those fields, and who else sees them?
- **Design impact**: Defines agent's access requirements and HITL escalation triggers
- **Closes**: A15 (decision context structure and visibility)

**Q5**: If an agent were monitoring onboarding progress and updating tracker status automatically, what would you need to see or control before you'd trust it?
- **Design impact**: Shapes agent oversight UI, approval workflows, and confidence thresholds
- **Reveals**: Priya's personal stake and risk tolerance

---

## 3. VIP Hire Detection & Special Handling

**Q6**: Tom Reeves is flagged as "Director's hire from Deloitte; sensitive about onboarding speed." How do you know a hire is VIP before problems surface? Is there a formal flag from recruiting, or do you infer it?
- **Design impact**: Determines agent's VIP detection logic (structured flag vs heuristic)
- **Closes**: A30 (VIP identification criteria)

**Q7**: Tom's buddy assignment shows "Paired with Sarah J (peer level), not Anna (rule says senior pair)." What criteria determine when you override the standard buddy rule?
- **Design impact**: Defines human-only vs agent-flagged override decisions
- **Closes**: A16 (override decision logic)

**Q8**: Mike Tehrani (Consulting Director's PA) escalated directly to the CFO after 5 days. Is this escalation path typical for consulting hires, or was Tom's case exceptional?
- **Design impact**: Reveals whether consulting division is always high-touch or if this was one-off political dynamic
- **Closes**: A11, A29 (political sensitivity and escalation patterns)

---

## 4. Compliance Training: Flowchart Staleness & Lived Routing

**Q9**: The compliance flowchart (v4.2, Oct 2023) has a pencilled note saying "TEMP-EXT retired 2024-Q1 — update flowchart sometime." What actually happens when a TEMP-EXT hire comes through now?
- **Design impact**: Reveals current routing logic and whether documented rules are trustworthy
- **Closes**: A17 (stale documentation impact)

**Q10**: Maria Costa (contractor→FTE) shows "FTE conversion record didn't pull contractor compliance history." How often does this happen, and what's the manual fix?
- **Design impact**: Determines if agent needs data reconciliation logic for conversions
- **Closes**: A18 (contractor→FTE data handling)

**Q11**: For UK vs Ireland hires, the brief mentions compliance differences. What specifically differs, and have you ever had a case where the wrong country's compliance path was assigned?
- **Design impact**: Reveals error frequency and consequence severity for country routing
- **Closes**: A22 (UK/Ireland compliance impact)

---

## 5. Edge Cases: Detection Patterns & Resolution Ownership

**Q12**: The brief lists edge cases: late right-to-work checks, expired visas, frozen records (James O'Connor example), contractor→FTE conversions. Are there early warning signs for any of these, or do they only surface when you're setting up the hire?
- **Design impact**: Determines if agent can detect edge cases proactively vs reactively
- **Closes**: A05 (predictability of edge cases)

**Q13**: James O'Connor's record shows "Was contractor 2022; old record frozen, IT thinks duplicate." Who resolved this — you, IT, or someone else — and how long did it take?
- **Design impact**: Maps edge-case resolution ownership and expected resolution time
- **Closes**: A19 (frozen record resolution process)

**Q14**: Right-to-work checks are listed as edge cases. Are these always manual (Home Office share-code lookup), or is there any system integration?
- **Design impact**: Determines if agent can automate checks or only flag for human action
- **Closes**: A21 (right-to-work verification process)

---

## 6. Stakeholder Communication & Status Translation

**Q15**: The tracker shows "Workday status" vs "Visible status" (e.g., Workday="Active" but Visible="Pending IT — laptop"). Who sees the Visible status, and how do you decide what to show?
- **Design impact**: Defines agent's role in status translation and stakeholder communication
- **Closes**: A14 (dual status rationale and audience)

**Q16**: Tom Reeves's email thread escalated over 5 days. At what point did you know this was going to be a problem, and what would have prevented it?
- **Design impact**: Reveals whether earlier detection/escalation logic would have helped
- **Informs**: Agent monitoring frequency and escalation thresholds

---

## 7. Saba LMS & Compliance Chasing

**Q17**: Saba LMS has no API. Walk me through how you actually assign a training pack and check completion status today. What takes the most time?
- **Design impact**: Determines workaround feasibility (UI automation, email parsing, manual handoff)
- **Closes**: A07 (Saba integration options)

**Q18**: The brief says "assignment plus chasing" takes ~45 min/case. Break that down — how much is assignment vs how much is chasing, and what would reduce the chasing time?
- **Design impact**: Quantifies agent's value proposition for chasing automation
- **Closes**: A28 (chasing overhead breakdown)

---

## 8. CFO Mandate & Project Success Criteria

**Q19**: The CFO asked you to "look at AI options" after consulting division complaints. What does success look like for this project in the CFO's eyes — faster onboarding, fewer complaints, cost savings, or something else?
- **Design impact**: Defines primary success metric and stakeholder priorities
- **Closes**: A11 (CFO's actual mandate)

**Q20**: If an AI agent were handling routine monitoring and chasing, but you still had to intervene for VIP cases and edge cases, would that feel like a win, or does the CFO expect more?
- **Design impact**: Calibrates agent autonomy level to stakeholder expectations
- **Reveals**: Whether partial automation is acceptable or full automation is expected

---

## Question Design Principles Applied

1. **Specific over generic**: "Walk me through Tom Reeves's laptop ticket failure" not "Tell me about your challenges"
2. **Lived practice over documentation**: "What actually happens when TEMP-EXT comes through" not "What does the flowchart say"
3. **Prior incidents as evidence**: "What automation projects have you tried" not "Would you be open to automation"
4. **Edge cases as design constraints**: "How do you know a hire is VIP before problems surface" not "Do you handle VIPs differently"
5. **Time/frequency quantification**: "How often do specs drift" not "Is spec drift a problem"
6. **Escalation thresholds**: "At what point did you know Tom's case was escalating" not "How do you handle escalations"
7. **System workarounds**: "Walk me through how you assign training in Saba" not "Is Saba hard to use"
8. **Stakeholder politics**: "What does the CFO expect from this project" not "Is the CFO supportive"
9. **Failure mode specificity**: "Have you ever assigned the wrong compliance path" not "Are there compliance risks"
10. **Decision rationale**: "What triggers a buddy override" not "Do you follow the buddy policy"
