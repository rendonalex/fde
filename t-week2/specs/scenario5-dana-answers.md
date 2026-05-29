# Dana's Answers to Discovery Questions
## Role-Play: Dana Velazquez, Practice Manager, Westbridge Family Medicine

---

## Critical Priority Questions

### Q1: PA Chase Process for UnitedHealthcare Choice

**Dana's Answer**:
"Okay, so for UHC Choice specifically - I submit the PA through their portal, I always get a confirmation number. Their stated SLA is 5 business days. But here's what I've learned after doing this for years: they NEVER respond on day 5. If you call on day 5, they'll say 'still processing, call back tomorrow.' So I don't even bother anymore. I wait until day 6, then I check the portal first thing in the morning. If it's still showing 'pending' on day 6, I call. Nine times out of ten, when I call on day 6, they approve it right there on the phone - like they just needed the nudge. 

The logic is: Don't chase before day 6 (waste of time). Always chase on day 6 (they're ready by then). If it's denied on day 6, escalate to the physician immediately because we need to either appeal or reschedule the patient.

For other payers: Aetna is usually 3 days now - they've gotten faster this year. Humana Medicare Advantage is exactly 6 days, like clockwork. Wellpath Medicaid is 7-10 days and they deny the first time for colonoscopies unless you attach the prior visit note even though the form doesn't ask for it."

**Implication**: **Rules are articulable and encodable**. Dana has explicit payer-specific timing logic.

---

### Q2: Other Payer-Specific Workarounds

**Dana's Answer**:
"Oh yes, Wellpath isn't the only one. Let me think... 

- **Aetna specialty referrals**: You have to include the referral letter from the PCP, not just the order. The form has a field for 'supporting documentation' but it doesn't say 'required' - but if you don't include it, they deny it.
- **Humana imaging**: For MRIs and CT scans, they want the diagnostic code AND the clinical rationale in plain English. If you just put the ICD code, they send it back asking for 'medical necessity narrative.'
- **BCBS PPO cardiac procedures**: They require a copy of the most recent EKG or stress test result, even if it's 6 months old. This isn't on the form either.
- **Medicaid managed care (any MCO) for DME**: Durable medical equipment always requires a face-to-face visit note within the last 6 months. Always. No exceptions.

So yeah, there's probably 7-8 of these that I've learned over time. I keep notes in my Google Sheet, but it's not like a formal document or anything."

**Implication**: **7-8 payer-specific workarounds exist**. High-value tribal knowledge to encode. Agent PA submission ROI increases significantly.

---

### Q3: PA Status Check at Check-In

**Dana's Answer**:
"Honestly? There's no formal step in the check-in workflow where staff check PA status. The front desk checks insurance, collects copay, updates demographics, but PA status isn't on the checklist. I think the assumption is that if the visit is on the schedule, the PA must be cleared - otherwise why would we schedule it?

But that assumption breaks when the PA submission is close to the visit date, or when payers are slow. Like with TJ's MRI - we submitted the PA 10 days before the visit, which should've been plenty of time, but UHC took 8 days instead of their usual 6, and nobody thought to check the day before the visit.

I've been thinking we need to add a PA status check to the check-in workflow, but it would add time and the front desk is already slammed. If I had a system that automatically flagged 'PA pending' when the patient checks in, that would be perfect."

**Implication**: **Step is missing from workflow**. High-value agent intervention = day-of-visit PA status alert at check-in.

---

### Q4: Visit-Reason Triage Protocols

**Dana's Answer**:
"We don't have anything written down. It's basically common sense plus asking me or the nurse if they're not sure. The front desk knows the obvious ones - chest pain, difficulty breathing, severe bleeding, anything with 'sudden' in front of it like sudden vision loss - those get escalated to me or the on-duty physician immediately. 

But what about 'some chest discomfort' or 'feeling dizzy for a few days'? That's where it gets gray. Sometimes the front desk will just put it in the visit reason field and the physician sees it when the patient walks in. Sometimes they'll ask me, and I'll ask a few follow-up questions - 'Is it constant or intermittent?' 'Any shortness of breath?' - and then decide if it needs immediate attention.

I've been meaning to write down a list of red-flag symptoms and what to ask, but I haven't had time. And honestly, even if I wrote it down, there's always going to be edge cases where you need clinical judgment."

**Implication**: **No documented protocols**. Informal red-flag list exists in Dana's head. Agent can formalize protocols, but requires collaboration with Dana + physicians to define criteria.

---

### Q5: Prior Under-Triage Incident

**Dana's Answer**:
"Yes, actually. About 8 months ago, a patient in his 60s came in for what he described as 'indigestion.' He'd scheduled it as a routine follow-up. The front desk didn't flag it because 'indigestion' doesn't sound urgent. Turns out he was having a heart attack - silent MI. The physician caught it during the visit, called 911, patient went to the ER and survived, but it was close.

After that, the senior physician told me we need to be more careful about chest symptoms of any kind, even if the patient downplays it. But we never formalized anything - it's just something I remind the front desk about occasionally. That's why I'm nervous about AI doing triage - what if it misses something like that?"

**Implication**: **Prior incident exists (8 months ago, heart attack)**. Dana's risk tolerance is shaped by this near-miss. Agent design must over-escalate for safety (bias toward false positives, not false negatives).

---

### Q6: Insurance Verification Staleness

**Dana's Answer**:
"athenahealth doesn't have an automatic alert for stale verifications. There's a 'last verified' date field, but you have to remember to look at it. Our unofficial policy is to re-verify every 6 months for commercial insurance and every visit for Medicaid because their eligibility changes so much.

But it's manual - staff have to remember to check that date field. When we're busy, especially Monday mornings or flu season, they skip it. That's how we ended up billing three patients as self-pay when they had active coverage. All three were chronic patients who come in quarterly, so staff assumed their insurance was still good.

If there was a system that automatically flagged 'verification older than 6 months' when we're scheduling or checking in, that would solve it."

**Implication**: **athenahealth has NO automatic staleness alert**. High-value agent feature = automatic stale-verification detection and re-verify trigger.

---

### Q7: Availity 30% Failure Rate Breakdown

**Dana's Answer**:
"I'd say it's about 60% patient eligibility issues and 40% system issues. 

Patient issues: Coverage lapsed (they didn't pay premium), they changed plans and didn't tell us, they gave us the wrong insurance card (sometimes family members' cards get mixed up), or it's a new plan that just started and Availity hasn't synced yet.

System issues: Availity times out occasionally (maybe 5-10% of cases), some small regional payers aren't in Availity's system so we have to call directly, and sometimes the payer ID we have on file doesn't match what Availity expects (especially Medicaid MCOs - the plan names are all over the place).

The frustrating ones are the system issues because we know the patient has coverage, but Availity can't find it, so we waste 15 minutes on the phone with the payer."

**Implication**: **60% patient eligibility (not fixable by agent), 40% system failures (agent can retry, improve config)**. Agent should focus on: (1) retry logic for timeouts, (2) fuzzy matching for payer ID mismatches, (3) patient communication for eligibility issues.

---

## High Priority Questions

### Q8: DoseSpot Medication Reconciliation Complexity

**Dana's Answer**:
"It's several things. First, DoseSpot doesn't pull from every pharmacy - small independent pharmacies, especially in lower-income areas, aren't always in their network. Our self-pay and Medicaid patients often use those pharmacies because they're cheaper or closer.

Second, patients on assistance programs - manufacturer discount cards, samples from specialists, free clinic medications - those don't show up in DoseSpot at all because they're not submitted as pharmacy claims.

Third, mail-order. A lot of our patients use mail-order for maintenance meds (diabetes, blood pressure) and local pharmacy for acute stuff (antibiotics, pain meds). DoseSpot pulls from both, but sometimes the mail-order sync is delayed by weeks.

And finally, OTC stuff - vitamins, supplements, aspirin - patients don't think of those as 'medications' so they don't mention them unless you specifically ask."

**Implication**: **DoseSpot gaps confirmed**: (1) small pharmacies, (2) assistance programs, (3) mail-order delays, (4) OTC/supplements not tracked. Agent interview script should prompt for all four categories.

---

### Q9: Med List Update Process

**Dana's Answer**:
"Front desk documents the change in the 'visit notes' section or in the medication reconciliation comments field, but they don't actually change the med list itself. That's the physician's job during the visit - they review what the patient said, make the clinical decision about whether it's safe, and then update the med list.

Why? Because sometimes a patient will say 'I stopped taking my blood pressure med' but they shouldn't have stopped without talking to the doctor first. Or they'll say 'my cardiologist started me on a new med' but the med name they give is wrong or the dosage is unclear. We can't update the med list based on patient verbal report alone - it needs physician confirmation.

So front desk flags it, physician confirms and updates during the visit."

**Implication**: **Staff only flag, never update**. Agent must follow same boundary: document reported changes in comments/flags, but NOT update athenahealth med list. Physician updates during visit.

---

### Q10: Why Google Sheets Instead of athenahealth PA Module

**Dana's Answer**:
"athenahealth's PA tracking is... basic. It shows me when a PA was submitted, the payer, and the status (pending/approved/denied). But it doesn't have:

1. **My target chase date** - I can't set a custom chase date per payer. It just shows 'submitted 5 days ago' but that doesn't tell me when to actually chase.
2. **Payer-specific notes** - I can't document 'UHC always takes 6 days' or 'Wellpath requires prior visit note' in a structured way.
3. **Visit linkage** - It doesn't show me which patient visit is blocked by this PA. I have to cross-reference manually.
4. **Quick view** - I can't see all my pending PAs in one list sorted by chase date. I have to click through patient records individually.

My Google Sheet has all of that. One row per PA, columns for submission date, payer, my chase date, status, visit date, and notes. I can sort by chase date and see 'these 5 PAs need attention today.'"

**Implication**: **athenahealth PA module is inadequate**. Missing: custom chase dates, payer notes, visit linkage, list view. Agent must build full PA chase management (not just integrate with athenahealth).

---

### Q11: athenahealth PA API Accessibility

**Dana's Answer**:
"I honestly don't know. I've never tried to pull PA data via API - I just use the UI. Our IT person would know, but I think athenahealth has APIs for most things. The question is whether our specific athenahealth subscription includes API access, because I know some features are add-ons that cost extra."

**Implication**: **Uncertain - requires technical validation**. Likely athenahealth APIs exist, but subscription tier and API coverage for PA module need verification. Assumption: Proceed assuming API access is feasible but requires IT validation before Wave 1 kickoff.

---

### Q12: HIPAA/Malpractice Constraints on AI

**Dana's Answer**:
"I haven't checked yet - the senior physician just asked me to 'look at AI' last week. But I know we'd need to run it by our HIPAA compliance consultant and probably our malpractice insurance carrier.

What I'm worried about: If the AI makes a mistake - like it doesn't flag a patient with chest pain, or it updates a med list incorrectly - who's liable? Is it us, or the AI vendor? Our malpractice insurance is very specific about 'standard of care' and I don't know if 'AI-assisted triage' counts as standard of care yet.

And for HIPAA, I know any vendor that touches patient data needs a BAA. We have BAAs with athenahealth, Availity, and DoseSpot already. Would the AI need its own BAA, or does it run 'inside' athenahealth somehow?"

**Implication**: **Not yet checked - requires immediate validation**. Malpractice liability and BAA requirements are Wave 1 blockers. Must resolve before design proceeds. Agent design should assume: (1) BAA required, (2) audit trails mandatory, (3) human accountability for all agent outputs (agent assists, human decides).

---

### Q13: BAA Requirements for AI Agent

**Dana's Answer**:
"Yeah, like I said, we have BAAs with athenahealth, Availity, and DoseSpot. If the AI agent is a separate system that accesses patient data, it would definitely need its own BAA.

If the AI could somehow run 'inside' athenahealth - like as an add-on module or something - maybe it would be covered under our existing athenahealth BAA? I don't know if that's technically possible.

The BAA process with athenahealth took about 2 months - legal review, negotiations, back-and-forth. If we need a new BAA for the AI, we'd need to factor that into the timeline."

**Implication**: **New BAA likely required unless agent runs as athenahealth add-on**. Timeline: 2-3 months for BAA execution. Wave 1 schedule must account for this lead time (can do design/development in parallel with BAA process, but cannot go live until BAA signed).

---

### Q14: Prior Automation History

**Dana's Answer**:
"We tried to automate appointment reminders about 3 years ago - SMS and email reminders sent automatically 48 hours before the visit. That worked great, actually. Reduced no-shows by maybe 20%.

We also tried a patient portal push about 2 years ago - encouraged patients to check in online before their visit, upload insurance cards, fill out forms. That had mixed results - younger patients love it, older patients hate it. We're at maybe 65-70% adoption now.

The failure was when we tried to implement a script for the front desk - a flowchart for how to handle different types of calls. It was too rigid. The front desk hated it because real calls don't follow a script - patients ask weird questions, have unusual situations. After a month they just stopped using it and went back to their own judgment.

What I learned: Automation works when it handles the predictable stuff (reminders, forms). It fails when it tries to replace human judgment. So if you're thinking about AI, don't try to automate the judgment part - automate the data lookup, the checklist, the reminder. But let the human make the final call."

**Implication**: **Prior rigid automation failed**. Dana's mental model: "Automation works for predictable tasks, fails when it replaces judgment." Agent design must emphasize: Agent provides information/recommendations, human makes decisions. Avoid positioning agent as "AI decides for you."

---

## Medium Priority Questions

### Q15: Front-Desk Onboarding Time

**Dana's Answer**:
"Full onboarding is about 3-4 months before someone is fully independent. The first month is basics - how to use athenahealth, check patients in, verify insurance. That's learnable in a few weeks with good training.

The hard part is months 2-4: learning all the edge cases. PA timing, payer-specific quirks, Medicaid MCO verification, which physicians prefer what, when to escalate vs. handle it yourself. That's the stuff I have in my head but isn't written down anywhere.

New staff constantly ask me questions for the first 3-4 months: 'Dana, this PA is at 5 days, do I chase now?' 'Dana, this patient's insurance card says Wellpath but Availity can't find it, what do I do?' Eventually they learn the patterns, but it takes time.

If we could document all that stuff - or better yet, have a system that just tells them the answer - onboarding would be way faster. Probably cut it down to 6-8 weeks instead of 3-4 months."

**Implication**: **Onboarding is 3-4 months; hardest part is tribal knowledge**. Agent that encodes Dana's knowledge could reduce onboarding from 16 weeks → 6-8 weeks (50% reduction). High ROI for PA chase, insurance verification edge cases, payer-specific workarounds.

---

### Q16: Patient Volume Split Across Locations

**Dana's Answer**:
"It's roughly 60-40. The main office gets about 105-110 patients per day, the second location gets about 70-75 per day. Main office is bigger, has more physicians, and is in a more populated area.

Sometimes if one location is short-staffed, I'll have someone work remotely or cover the other location. So the system definitely needs to be accessible from both sites, not locked to one location's desktop."

**Implication**: **Volume split: 60% main (110/day), 40% second location (70/day)**. Agent must be cloud-based (accessible from both locations). Cross-site staff rotation is common.

---

### Q17: Patient Portal Adoption Rate

**Dana's Answer**:
"I'd say about 65-70% complete the pre-visit questionnaire online. The other 30-35% either don't have portal accounts or just prefer paper.

The non-portal group is mostly older patients (65+), some non-English speakers, and a few people who just don't like technology. We've tried to push portal adoption, but you can only push so hard - some people are never going to use it.

So we'll always have a paper workflow for at least 25-30% of patients."

**Implication**: **Portal adoption: 65-70% (not 70% as assumed in A08)**. Paper workflow for 30-35% is permanent. Agent must support dual workflow indefinitely (not just temporary). Deprioritize "increase portal adoption" - focus on making paper workflow efficient.

---

### Q18: Dana's Personal Stake in AI Project

**Dana's Answer**:
"Honestly? I'm excited but also nervous. Excited because I'm drowning in work - the PA chase, the billing errors, the constant questions from front desk. If AI can take some of that off my plate, I can focus on the bigger-picture stuff - improving workflows, working with physicians on quality metrics, maybe even strategic planning.

But I'm also nervous because this is my expertise, you know? If AI can do what I do, does that make me less valuable? Am I automating myself out of a job?

What success means to me: The AI handles the routine, predictable stuff - checking PA status, flagging stale verifications, prompting for DoseSpot gaps - and I handle the complex cases, the physician escalations, the process improvements. I become more of a strategic ops person, less of a firefighter.

But if this doesn't work, or if it creates more problems than it solves, I'm the one who's going to get blamed. So I need to be involved in the design and testing - I can't just hand over my Google Sheet and hope for the best."

**Implication**: **Dana is excited but nervous (bus factor concern)**. Positioning must be: "Agent scales your expertise, frees you for strategic work" (NOT "Agent replaces you"). Dana must be involved in design (encode her rules, validate agent behavior). Change management is critical.

---

### Q19: Most Exhausting Task

**Dana's Answer**:
"PA chase, hands down. It's not just the time - it's the mental load. I have to remember which PAs are coming up, which payers to chase when, checking portals every morning, making phone calls, and then when something goes wrong and a patient shows up without PA clearance, I'm the one who has to apologize, reschedule, deal with the angry patient.

And it's the only thing I can't delegate. Front desk doesn't have the experience to know when to chase, which payer needs a phone call vs. just portal check, what to say when you call. So it's all on me.

If AI could handle PA chase - monitor status, tell me when to act, maybe even automatically check portals and alert me only when there's a problem - that would be life-changing."

**Implication**: **PA chase is Dana's highest pain point** (mental load + non-delegatable + patient-facing consequences). JtD 2.3 (PA chase) confirmed as Wave 1 strategic priority. Agent value: reduce Dana's daily monitoring burden, alert only when action needed.

---

### Q20: Senior Physician's Priorities

**Dana's Answer**:
"He's worried about all three, but especially patient satisfaction and compliance risk. 

The PA miss with TJ - that's the second time it's happened to that patient. TJ complained to the physician, the physician complained to me. If it happens again, we might lose TJ as a patient. And if TJ leaves a bad review online, that hurts our reputation.

The billing errors - those are embarrassing. When a patient gets a surprise bill for a visit that should've been covered, and then we have to refund them and refile... it makes us look disorganized. And it's a compliance issue if we're billing incorrectly.

Staff workload is important too - he knows we're stretched thin - but I think his main driver is 'let's not mess up in front of patients.' He wants reliable, consistent intake. If AI can prevent those embarrassing mistakes, he'll support it."

**Implication**: **Priority: Patient experience (prevent visit cancellations, billing errors) > Compliance risk > Staff efficiency**. Agent design should prioritize: (1) PA status alerts (prevent cancellations), (2) Stale verification detection (prevent billing errors), (3) Error-proofing intake (reduce patient-facing mistakes). ROI narrative should emphasize "prevent patient dissatisfaction" not just "reduce staff time."

---

## Summary: Key Design Implications

### High-Confidence Conclusions
1. **Q1**: Dana's PA chase rules are encodable → Agent-led PA chase is feasible
2. **Q2**: 7-8 payer-specific workarounds exist → High ROI for agent PA submission
3. **Q3**: PA status check is missing from check-in → High-value agent intervention
4. **Q5**: Prior under-triage incident (heart attack) → Agent must over-escalate for safety
5. **Q6**: athenahealth has no staleness alert → High-value agent feature
6. **Q10**: athenahealth PA module is inadequate → Agent must build parallel PA system
7. **Q14**: Prior rigid automation failed → Position agent as assistant, not replacement
8. **Q19**: PA chase is Dana's highest pain point → Confirms Wave 1 strategic priority

### Critical Validations Required
1. **Q12**: HIPAA/malpractice constraints (Wave 1 blocker - must resolve immediately)
2. **Q13**: BAA requirements (2-3 month timeline - start BAA process in parallel with design)
3. **Q11**: athenahealth PA API access (technical validation before Wave 1 kickoff)

### Design Adjustments
1. **Q4 + Q5**: No triage protocols exist + prior heart attack incident → Agent must formalize red-flag list with Dana + physicians (Wave 1 planning phase, deploy in Wave 2)
2. **Q7**: 60% patient eligibility, 40% system failures → Agent focus: retry logic + fuzzy matching (not patient behavior change)
3. **Q9**: Staff only flag med changes, never update → Agent documents in comments, flags for physician (does NOT update med list)
4. **Q15**: Onboarding 3-4 months, tribal knowledge is bottleneck → Agent ROI includes 50% onboarding time reduction
5. **Q17**: Portal adoption 65-70% (not 70%) → Paper workflow is permanent (30-35%), not temporary
6. **Q18**: Dana is nervous about job security → Change management: position as "scaling expertise," involve Dana in design
7. **Q20**: Physician prioritizes patient experience > efficiency → ROI narrative emphasizes preventing patient-facing failures
