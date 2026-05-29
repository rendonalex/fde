# Discovery Questions — MedFlex Healthcare Staffing

**Stakeholder:** Marcus Reyes, CEO  
**Engagement goal:** 10x business volume without 10x-ing coordinators  
**Focus:** AI automation opportunities in matching, credentialing, and coordination

---

## Broad Funnel (5 Questions)
*Work patterns, time sinks, repetitive vs. novel work, coordination pain points*

**ATX alignment: Volume & Time / Organisational**

**Q1.** Walk me through what a coordinator actually does from 9am to noon on a typical day. Not the job description — what's consuming their attention hour by hour?

> *Listening for:* time distribution across matching vs. compliance vs. coordination; tool-switching; volume signals.

**Q2.** Of the 120 shift decisions your coordinators make each day, what fraction feel genuinely routine versus requiring real thought? What separates the two?

> *Listening for:* estimated cognitive load ratio; early signal on codifiability of matching rules.

**Q3.** When a shift sits unfilled for more than an hour, what's the most common reason? Walk me through the last time that happened.

> *Listening for:* bottleneck category — data gap, availability conflict, credential mismatch, or coordinator bandwidth.

**Q4.** If I watched your coordinators for a day, what work would I see them doing that feels like it shouldn't require a human — things they'd describe as tedious or mechanical?

> *Listening for:* routine-zone tasks ripe for full delegation; frustration with current tooling.

**Q5.** You mentioned two prior AI projects that didn't stick. What were coordinators doing instead of using the tools, and why did that feel like the better option to them?

> *Listening for:* trust barriers, workflow fit, real process vs. assumed process — also critical for adoption risk in any new system.

---

## Narrow Funnel (5 Questions)
*Specific pause points in placement/credentialing, judgment calls in matching, exception handling, cross-system data gathering*

**ATX alignment: Cognitive Nature / Data & Systems**

**Q6.** Pick a shift request from this week that took your coordinator more than two hours to fill. Walk me through every step they took — including the steps that aren't in any manual.

> *Listening for:* lived process vs. documented SOP; hidden judgment calls; data-gathering detours.

**Q7.** When a coordinator is matching a nurse to a facility, where do they actually stop and think? What's the moment where it's not obvious who to call?

> *Listening for:* pause points in matching — where criteria conflict, preference data is stale, or availability is uncertain.

**Q8.** Credential verification — you said it's done manually against state regulatory databases. How does a coordinator know when a credential check is "good enough" to proceed versus when it needs a second look?

> *Listening for:* the judgment layer inside what sounds like a rote check; exception triggers; risk thresholds.

**Q9.** When a hospital submits a shift request, what information is typically missing or ambiguous that forces a coordinator to go back and ask? How often does that happen?

> *Listening for:* input quality problems; coordination round-trips that add latency; async wait patterns.

**Q10.** You have a 7% credential mismatch rate. Walk me through how a mismatch actually gets discovered — at what point in the process, by whom, and what happens next?

> *Listening for:* detection lag; downstream cost of late failure; whether the mismatch source is data, process, or judgment error.

---

## Probe Funnel (5 Questions)
*Codifiability of matching criteria, exception rates, risk/reversibility of placement decisions, latency requirements, human trust in AI-assisted decisions*

**ATX alignment: Risk & Compliance / Cognitive Nature / Organisational**

**Q11.** If you had to write down the rules a coordinator uses to decide which nurse gets a shift — not the official policy, the real criteria they use — how far would you get before you hit "it depends"? What does "it depends" actually mean in those cases?

> *Listening for:* codifiability ceiling; exception rate; whether "it depends" resolves to enumerable sub-rules or genuine ambiguity.

**Q12.** If an AI agent matched a nurse to a shift and flagged it for coordinator review before sending the offer — how long does the coordinator have to act before the opportunity disappears? What's the real time window?

> *Listening for:* latency constraints; whether human-in-the-loop is viable or if speed requirements demand higher automation.

**Q13.** What's the worst thing that happens if a placement is wrong — wrong credential type, wrong specialty, wrong facility? Who bears the consequence, and how quickly is it caught?

> *Listening for:* risk level and reversibility; regulatory exposure; whether mistakes compound or are self-correcting.

**Q14.** For the matching decision specifically — if an agent made 100 calls and a coordinator could review them in a batch, how many would they change? What pattern would drive the changes?

> *Listening for:* expected override rate; whether trust requires near-perfect accuracy or moderate accuracy with easy correction.

**Q15.** Your coordinators have built up pattern recognition over time — they know which nurses are reliable for which facility types, which hospitals are hard to staff, which requests are likely to fall through. How much of that knowledge lives only in people's heads versus somewhere a system could access?

> *Listening for:* tacit knowledge inventory; data infrastructure gaps; whether institutional knowledge can be captured for agent training or must stay human-in-the-loop.

---

## Question-to-ATX Category Mapping

| # | Question Focus | ATX Category | Funnel Stage |
|---|---|---|---|
| 1 | Daily attention distribution | Volume & Time | Broad |
| 2 | Routine vs. judgment ratio | Cognitive Nature | Broad |
| 3 | Bottleneck on unfilled shifts | Organisational | Broad |
| 4 | Mechanical work identification | Volume & Time | Broad |
| 5 | Prior AI failure modes | Organisational / Risk | Broad |
| 6 | Lived process walkthrough | Cognitive Nature | Narrow |
| 7 | Matching pause points | Cognitive Nature | Narrow |
| 8 | Credential verification judgment | Risk & Compliance | Narrow |
| 9 | Input quality / async waits | Data & Systems | Narrow |
| 10 | Mismatch detection lag | Risk & Compliance | Narrow |
| 11 | Matching rule codifiability | Cognitive Nature | Probe |
| 12 | Latency window for review | Risk & Compliance | Probe |
| 13 | Placement error consequences | Risk & Compliance | Probe |
| 14 | Expected AI override rate | Cognitive Nature | Probe |
| 15 | Tacit knowledge inventory | Data & Systems | Probe |
