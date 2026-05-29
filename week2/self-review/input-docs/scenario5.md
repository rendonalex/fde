  
## Scenario 5 — Small-Clinic Patient Intake - Original brief  
  
> A 6-physician family medicine practice (2 locations, ~180 patients per day) runs its patient intake through a 4-person front-desk team. The intake process for each visit spans: insurance verification, prior-authorisation check for scheduled procedures, pre-visit questionnaire, reason-for-visit triage (routine / urgent / same-day), medication reconciliation, and allergy-flag review. Physicians regularly discover at the visit that something was missed in intake — most commonly an expired prior auth or an unreviewed medication change.  
>  
> The practice manager wants to offload the administrative load to an agentic workflow but has three hard constraints: (1) no clinical judgment by the agent, (2) any contact with the stated visit reason must preserve a clear human escalation path, (3) HIPAA and state medical-records compliance is non-negotiable. They use athenahealth for EHR and a separate tool for insurance eligibility. They have no AI infrastructure today.  
>  
  
---

## Scenario 5 (enriched) — Small-Clinic Patient Intake

### The practice

**Westbridge Family Medicine** — 6-physician family medicine practice (US, mid-Atlantic suburb). Two locations 12 miles apart. ~180 patients/day across both sites: routine visits, chronic-disease management, urgent same-day appointments, pre-procedure screenings.

### The function

4-person front-desk intake team supporting both locations (typically 2 at each site, with cross-site rotation when one location is short-staffed). **Dana Velazquez**, RN-trained Practice Manager, oversees the function.

### The four work streams (per visit)

- **Insurance verification** (~180/day; ~3 min/case automated + ~5 min/case for the ~30% that fail auto-verify). Especially complex for self-pay or Medicaid managed-care patients.
- **Prior-authorisation check** (~25/day; ~12 min/case). For scheduled procedures, imaging, specialty referrals.
- **Pre-visit questionnaire & visit-reason triage** (~180/day; ~4 min/case). Routine vs urgent vs same-day classification.
- **Medication reconciliation & allergy-flag review** (~180/day; ~6 min/case). Pharmacy history review, allergy alerts, change flagging.

### Tooling sketch

- **athenahealth** (EHR, modern SaaS, REST APIs)
- **Availity** (insurance eligibility, separate REST-API tool)
- **DoseSpot** (pharmacy / medication reconciliation, integrated with athenahealth)
- **Phone + paper intake forms** (for patients without portal accounts)
- **Google Sheets** (Dana's PA chase list and flagged-patient tracker)

### Stakeholder

**Dana Velazquez**, Practice Manager, RN by background, 11 years at Westbridge. The senior physician has discovered three intake misses in the last quarter (all expired prior auths) and has asked her to "look at this AI thing the medical society keeps emailing about."

### Hard constraints (preserved from the original brief)

1. No clinical judgment by the agent.
2. Any contact with the stated visit reason must preserve a clear human escalation path.
3. HIPAA and state medical-records compliance is non-negotiable.

### What you're expected to elicit through the week

Bring questions to your coach (role-playing Dana) about:

- What happens when prior authorisations fail, and how does Dana actually chase them?
- Where does DoseSpot's medication reconciliation miss things in real practice?
- Which patient populations don't fit the standard intake flow, and how is the team accommodating them today?
- What HIPAA / malpractice insurance constraints govern AI usage at the practice?
- What's Dana's personal stake in this — what is she planning for beyond this project?

### Sample artefacts

#### Artefact 5.1 — Dana's PA chase list

*Selected rows from Dana's "PA chase list" Google Sheet. Shared with the front desk only.*

| Patient | Procedure | Insurer | Submitted | Standard SLA | My target chase | Status | Notes |
|---|---|---|---|---|---|---|---|
| MR (DOB 1962-03-14) | Cardiac stress test | Aetna | 18.10 | 5 days | Chase 23.10 | Approved 22.10 | Aetna fast this month, unusual |
| TJ (DOB 1989-07-22) | MRI right knee | UnitedHealthcare Choice | 16.10 | 5 days | Chase 22.10 | Pending | UHC Choice is always 6 days, sometimes 7; visit on 28.10 |
| RB (DOB 1955-11-02) | Colonoscopy | Medicaid Managed Care (Wellpath) | 11.10 | 5 days | Chase day 7 (18.10) | Denied — needs prior visit doc | Wellpath always denies first time on this — resubmit with the August visit note |
| KS (DOB 1976-04-09) | Specialty referral (rheum) | BCBS PPO | 14.10 | 3 days | Chase 19.10 | Approved 16.10 | Standard |
| DP (DOB 1944-12-01) | Cardiac echo | Medicare Advantage (Humana) | 19.10 | 5 days | Chase 26.10 | Pending | Humana always exactly 6 days; never 5 |

*[Footer note in Dana's hand: "Wellpath colonoscopy denial pattern — they want the prior visit note attached, never says so on the form. Standing rule: include with submission, save the resubmit cycle."]*

#### Artefact 5.2 — Physician portal note

*Note attached to patient TJ's chart by Dr. Westbridge after the visit on 28.10.*

> "Visit reason was MRI follow-up for right knee. Patient arrived expecting results review. PA for the MRI was still pending at visit time — see athenahealth ticker. Front desk did not flag this at check-in.
>
> Visit aborted at exam-room check; rescheduled for 04.11 once PA confirmed. Patient frustrated — 'this is the second time this has happened to me.' Please review with Dana.
>
> JW"

#### Artefact 5.3 — Patient phone call about a bill

*Phone call notes captured by front-desk staff (paraphrased; full call ~7 minutes).*

> Patient called about a bill received 22.10 for visit on 12.08 — $340 listed as 'self-pay portion, insurance not on file at date of service.'
>
> Patient (TJ): "I've been on Aetna for three years and I gave you my card every time. Why is this insurance-not-on-file?"
>
> Looked into athenahealth. Patient was actually verified as Aetna at the August visit, but the verification is dated 22.05 (last verified) and somehow when the claim was submitted, the system pulled the older record showing self-pay from 2022.
>
> Resolved: refiled the claim with the Aetna info; refund pending. Took 12 minutes including hold time with billing.
>
> *Front-desk note added to chart: "Patient verification refresh window > 6 months caused billing miss. We don't refresh for chronic patients on stable insurance — Dana said this is the third time. Need to discuss."*

---
