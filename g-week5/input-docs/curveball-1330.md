# Curveball — 13:30 CET

**Final Exam, Gate 5b. Time: 13:30 CET.**
**Action required:** revise your design before the build phase begins at 14:00.

---

## What just happened

At 09:42 ET this morning, the **U.S. Food and Drug Administration** posted **Final Guidance for Industry: Artificial Intelligence and Machine Learning in Postmarketing Safety Reporting (May 2026)** at the FDA Center for Drug Evaluation and Research. The guidance is effective immediately and applies to all FDA-regulated marketing-authorisation holders using AI-assisted intake, triage, classification, or reportability-decision-support in postmarketing pharmacovigilance.

You are forwarded the guidance during a 13:30 video call with Dr. Maeve Carmichael (CMO), Carolina Núñez-Reyes (VP Regulatory), and Greta Schäffer (Chief Compliance Officer). Greta has already read it. Maeve: *"Tell us how the design changes."*

## FDA Final Guidance — operative excerpts

> **Scope.** This guidance addresses use of AI/ML systems in postmarketing pharmacovigilance intake and reportability decision-support for adverse event reports received under 21 CFR 314.80 and equivalent regulations. AI-assisted use includes intake routing, structured-information extraction, seriousness classification recommendation, expectedness signal generation, and reportability recommendation. Investigational New Drug pharmacovigilance is addressed in a separate guidance.
>
> **Requirement 1 — Per-case audit record.** For each AI-assisted determination contributing to a postmarketing safety report, the marketing-authorisation holder must maintain a machine-readable audit record sufficient to reconstruct the AI's contribution. The record must include: model identity and version; source documents consulted; extracted facts surfaced; classifications recommended (seriousness, expectedness); reportability recommendation generated; the human safety physician's accept/modify/override action with rationale; timestamped chain of custody. Retention: 10 years post-disposition.
>
> **Requirement 2 — Human review of all serious AE classifications.** Any AE that the AI system classifies as serious per ICH E2A criteria must receive human safety physician review and signature before the seriousness classification is final. The AI may recommend; a qualified medical reviewer must adjudicate. This requirement is not satisfied by reviewer "rubber stamp" — the audit record must capture substantive review.
>
> **Requirement 3 — Signal-detection escalation.** When the AI system identifies that an incoming AE matches a pattern with three or more cases of the same MedDRA Preferred Term and same suspect product in a rolling 90-day window, the system must escalate the case for safety physician signal-detection review within 5 business days of the third case. This complements but does not replace periodic aggregate review obligations.
>
> **Requirement 4 — Expectedness determination boundary.** AI-assisted expectedness signals may inform but may not substitute for the marketing-authorisation holder's determination of expectedness against the Reference Safety Information. Final expectedness determination remains the safety physician's responsibility. AI-assisted recommendations of "unexpected" must include the specific RSI section consulted and the specific span in the case from which the unexpectedness is inferred.
>
> **Requirement 5 — 15-day clock attribution.** When AI-assisted intake first receives an AE meeting expedited reporting criteria, the 15-day FDA reporting clock is attributed to the timestamp of AI receipt, regardless of when the human safety physician opens the case. Architectural design must ensure that AI receipt timestamps are preserved as the clock-start, not human-open timestamps.

## What Maeve, Carolina, and Greta want from you in 30 minutes

1. **Does this kill the project?** Maeve needs a one-sentence answer at 14:00.
2. **What changes in the architecture?** Which capabilities change scope, what gets added, what becomes load-bearing.
3. **What changes in the signal-detection path?** Requirement 3 introduces a 3-cases-in-90-days escalation that must run as the system processes each new case.
4. **What changes in the audit-record infrastructure?** Requirement 1's 10-year retention and Requirement 2's substantive-review-not-rubber-stamp affect the data model.
5. **What changes in the economics?** Audit retention + human-review SLA on every serious classification + signal-detection escalation capacity are real line items.
6. **What changes in the build you're about to start at 14:00?** If anything in your prototype needs to demonstrate Requirements 1, 2, 5 specifically, name it now and bake it in.

## Constraints

- **Compliance is non-negotiable.** A design that ignores Requirements 1, 2, or 5 fails the gate (per the participant rules file automatic-fail list — *"missed a mandatory compliance or regulatory requirement from the curveball"*).
- **Final honest version.** Per `final-exam-rules.md`, the design is graded against its final honest version — original + curveball adaptation + any build-phase amendments. Naming a gap you discovered beats hiding it.
- **Time-pressure framing.** You have 30 minutes (13:30–14:00) to revise the delegation design + spec amendments (Deliverable #9). The build phase begins at 14:00 — your D#10 prototype should reflect the architecture you'd actually build.

## Submit

By **14:00 CET**, submit `D#9 — Revised delegation design + spec amendments` to the exam submission folder. Continue to the build phase at 14:00.

---

*Sealed curveball — Final Exam, Gate 5b. Released 13:30 CET, Virtual Friday Week 5. Do not distribute.*
