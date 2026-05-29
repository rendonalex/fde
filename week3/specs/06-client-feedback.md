# CEO Pushback Response — MedFlex Agentic Transformation

**To:** Marcus Reyes, CEO  
**From:** Alexandra Rendon, FDE  
**Re:** Your three items before Monday

---

## Executive Summary

  1. Timeline — Feature 5 is cut, ML ranker deferred, parallel dev reduces the critical path to 6 weeks. Named floor case if data quality fails.                                                 
  2. Ops dependency — Reframes week 1 as executable with a data export from Marcus directly; pins the Head of Operations need to week 3 (not week 1), with specific asks and explicit scope      
  consequences if access doesn't come through.                                                                                                                                                   
  3. A5 falsifiable check — Two-step win rate + speed-correlation analysis from the same ServiceNow export, with a decision table that tells Marcus exactly what number to give his CFO depending
   on what the data shows.  

## Item 1 — 6-week board demo: what gets cut

You're right that the plan as written doesn't land anything runnable in 6 weeks. Here's the honest version.

The original timeline had Features 1–3 largely sequential: parser (2–3 weeks) → ranker (3–4 weeks) → review interface (2–3 weeks). That math runs to 8–10 weeks before you have anything in coordinators' hands. Three changes compress it to 6.

**What changes:**

1. **Ranker scope is cut to rule-based only.** The architecture document already selected this option (Trade-off T4), but the 3–4 week estimate assumed future ML capability. A deterministic rule-based ranker — credential match, availability filter, proximity, hospital preference lookup — can be built in 1–2 weeks because there are no training data dependencies. The ML upgrade moves to Phase 2.

2. **Ranker and parser development overlap.** Parser work starts week 1 from your data export. Ranker data model design starts simultaneously week 1 once I see the nurse profile schema. They converge at integration in week 4–5. This is only possible if I get the data I describe under Item 2 below.

3. **Feature 5 (Shift Confirmation Notifier) is out of the 6-week window.** No M4 no-show reduction at board demo. That's the explicit cut. It also depends on infrastructure access we haven't confirmed (U4), so it was already the highest-risk feature for the 8-week plan.

**Revised 6-week delivery:**

| Weeks | Work |
|---|---|
| 1–2 | Data audit from your export; parser spec + prompt dev; nurse DB schema review; ranker data model |
| 2–4 | Parser build + 200-record validation (A10 check); rule-based ranker build in parallel |
| 4–5 | Parser → ranker integration; coordinator review interface (basic: ranked shortlist + approve/edit/escalate) |
| 5–6 | UAT with 1–2 coordinators; production rollout; win/loss tracking instrumented live |

What walks into your boardroom at week 6: a system running on real inbound shift requests, showing coordinators a ranked shortlist instead of a blank search field, with timestamps on every stage of the pipeline. You can demonstrate fill-time improvement on live requests, not a prototype.

If the data audit in week 1 shows the nurse database is too unstructured to build the ranker in time, I will tell you by end of week 2 — and the week 6 deliverable becomes the parser live on real requests. That's the floor case: something real, not five half-built features. I'd rather make that call in week 2 than surprise you the week before your board meeting.

**What stays out of 6-week scope regardless:** Feature 5 (Confirmation Notifier), ML ranker upgrade, hospital-facing portal, compliance automation, nurse mobile app. None of these are at risk of scope creep — they are named and locked out.

---

## Item 2 — Week 1 without the Head of Operations

The risk register wording was too loose. "Formally downscope if she's not available by week 2" implies the engagement blocks on her. It shouldn't. Here's what week 1 looks like with only what you can give me directly.

**What I need from you, not her:**

1. A ServiceNow data export: 200–300 historical shift request records (raw text as received; sanitized if needed for HIPAA). I don't need access to the live system yet — a flat file works.
2. A one-page description or screenshot of a nurse profile showing which fields are structured (specialty code, credential expiry date, location) and which are free text. You said the data is "pretty much raw format" but you've seen the profiles — a screenshot or field list is enough to start the ranker data model.
3. The name of whoever administers ServiceNow at MedFlex (technical contact, not the Head of Operations). I need API documentation and read-access credentials — an admin grants that, not the ops lead.

**What I produce in week 1 from that:**

- Parse 200 real shift records with the LLM; measure per-field extraction accuracy (this is the A10 validation Marcus's CFO will ask about)
- Identify the top failure modes in the parser (ambiguous specialty shorthand, missing credential codes, non-standard date formats) and tune the system prompt
- Draft the ranker data model and scoring spec against the nurse profile structure you show me
- Deliver a written assessment: is the data tractable in 6 weeks or does it require remediation work that changes the scope?

**What requires the Head of Operations — and when:**

She matters for three specific things that aren't week 1 blockers: (1) ServiceNow API credentials for read/write access to the live database (needed by week 2–3 to build the ranker against real nurse profiles, not a static snapshot), (2) a coordinator shadow session to validate the review interface design before UAT (needed by week 4), and (3) confirmation of how the nurse notification system works (needed only if Feature 5 returns to scope).

I'm not asking you to pull her off the matching floor in week 1. I'm asking for 30 minutes with her in week 2 to get API access set up, and one afternoon with a coordinator in week 4 for the UAT session. If neither of those is possible, I will specify accordingly — and the week 6 deliverable scope will be adjusted to reflect what I could build against a static data snapshot rather than a live system.

R3 in the risk register is rewritten: if I don't have live system API access by end of week 3 (not week 1 as originally written), the week 6 deliverable scopes to the parser and a ranker prototype tested against a static nurse database snapshot — not live on real matches. That is an explicit reduction I would name to you, not quietly absorb.

---

## Item 3 — A5 falsifiable check before you spend the full budget

You're right that your CFO should not be asked to accept $1.5M as a target when both supporting assumptions are Low confidence. Here is a specific, two-step check executable in the first two weeks of having real ServiceNow data.

**The check:**

**Step 1 — Win rate calculation (Week 1, 1–2 hours of analysis).**

Pull the last 3 months of ServiceNow records. Count: (a) total inbound shift requests logged, (b) total shifts filled by MedFlex, (c) total requests that closed without a MedFlex placement. The ratio (b)/(a) is your baseline win rate.

If your current win rate is 65–75%, A5 is roughly right — MedFlex is losing 25–35% of inbound requests, and speed is a plausible primary cause. If win rate is above 90%, A5 is wrong by a factor of 3 and the $1.5M M3 target needs to be replaced before I spend further budget on building for that outcome.

*Precondition:* This only works if ServiceNow currently logs all inbound requests, including those you don't fill. If you only log filled shifts, the historical data can't answer this. In that case, skip to Step 2 and add a "request not filled" log field starting week 1 to generate forward-looking data.

**Step 2 — Speed correlation (Week 2, if historical data supports it).**

For filled shifts in the same 3-month window, plot time-to-fill against request volume per hour (queue depth as a proxy for fill time). If fill rate drops materially during high-queue periods (say, requests received during coordinator transitions or early mornings when queue depth spikes), the competitive loss is speed-sensitive — that validates A6's mechanism (faster response recovers wins).

If fill rate is flat across queue depths, the competitive loss is not primarily a speed problem. It may be a match quality, pricing, or nurse supply problem — none of which this system fixes, and the revenue case changes entirely.

**Decision gate by end of week 2:**

| Win rate result | What it means for M3 | Action |
|---|---|---|
| Win rate ≤75% | A5 plausible; $1.5M target stands | Proceed with full engagement scope |
| Win rate 75–90% | A5 overstated; M3 likely $500K–$900K | Revise M3 target before CFO sees it; proceed with adjusted ROI framing |
| Win rate >90% | A5 wrong; speed recovery is not the revenue story | Replace M3 with throughput-scaling metric; reframe business case to volume × $300 × growth path |

I will not run this check and sit on a bad result. If the data kills A5, I tell you before you walk into the board meeting with a $1.5M number your CFO will dismantle. The point of a falsifiable assumption is to act on what it shows.

**What I need from you to run this check:** The same ServiceNow data export requested in Item 2. This analysis runs on that same file.

---

## What I'm not doing

I'm not proposing a phased roadmap as a way to avoid answering you. Each item above names something concrete: a cut (Feature 5 out, ML deferred), a deliverable redefinition (week 6 scope with a named floor case), and a specific two-week check with decision gates.

If any of these three answers changes your view of the engagement economics, I'd rather know before Monday than after.

— Alexandra
