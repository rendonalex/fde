# Assumptions Register — Westbridge Family Medicine Patient Intake

All inferences made during Phase 2 Cognitive Load Mapping and Phase 3 Delegation Qualification that are not directly stated in the scenario artefacts. Referenced throughout documents as [Axxx].

---

## Assumption Log

| ID | Assumption | Confidence | Source / Basis | Referenced In |
|----|-----------|:----------:|----------------|---------------|
| A001 | ~30% of insurance verifications (~54/day) fail auto-verify and require ~5 minutes of manual handling | HIGH | Stated in scenario workstream summary | 1.5, 1.6; WS1 JtD |
| A002 | ~25 PA cases/day is a combined total across both locations | HIGH | Stated in scenario workstream summary | WS2 JtD |
| A003 | Front-desk staff are responsible for PA chasing; no dedicated authorization coordinator exists | MEDIUM | Implied by 4-person front-desk team scope and Dana's described role; not explicitly stated | WS2 JtD |
| A004 | The >6-month insurance verification staleness issue is a systemic policy gap, not an isolated event | HIGH | Artefact 5.3: front-desk note reads "Dana said this is the third time. Need to discuss." | 1.2; WS1 JtD; Lived Narrative |
| A005 | DoseSpot misses OTC medications, hospital-discharge samples, and out-of-network specialist prescriptions | MEDIUM | Implied by discovery question "where does DoseSpot's medication reconciliation miss things in real practice?" — gap confirmed as real; extent and frequency unknown | 4.5; WS4 JtD; Lived Narrative |
| A006 | Approximately 20% of patients lack portal accounts and complete intake via paper forms | LOW | Tooling sketch references paper forms but states no percentage; 20% is a common US primary-care industry baseline | 3.1; WS3 JtD |
| A007 | Cross-site rotation occurs at least weekly and creates consistent knowledge gaps for the covering staff member | MEDIUM | Stated in staffing description ("cross-site rotation when one location is short-staffed"); frequency and impact on error rates are inferred | Lived Narrative |
| A008 | Dana personally holds the PA chase decision-making knowledge; front-desk staff execute actions based on her direction rather than applying insurer knowledge independently | HIGH | Artefact 5.1: PA chase list is in Dana's Google Sheet, annotated in her hand; discovery question confirms "how does Dana actually chase them" | 2.4; WS2 JtD; Lived Narrative |
| A009 | Hard constraint "no clinical judgment by the agent" applies specifically to visit-reason triage classification and any urgency scoring | HIGH | Stated as hard constraint in scenario; triage classification is the most apparent clinical judgment activity in WS3 | 3.4; 3.5; WS3 JtD |
| A010 | The three missed prior auths reported in the last quarter are discovered misses; actual miss rate is likely higher due to unreported or undetected cases | MEDIUM | Physician note (Artefact 5.2) documents one incident; scenario states "three intake misses" — these are likely the ones that surfaced to physician attention, not a complete count | WS2 JtD; Exec Summary |
| A011 | Insurer-specific SLA deviation and denial pattern knowledge (e.g., Wellpath colonoscopy always denied on first submission, UHC Choice actual SLA 6–7 days, Humana exactly 6 days) is entirely undocumented institutional knowledge held primarily by Dana | HIGH | Artefact 5.1: footnote in Dana's hand reveals this knowledge; it does not appear in any structured system or documented workflow | 2.4; 2.6; WS2 JtD; Lived Narrative |
| A012 | Checking PA status at day-of check-in is not a current required or enforced step in the check-in workflow | HIGH | Artefact 5.2: physician note states "front desk did not flag this at check-in" — the tone implies an expectation existed but was not enforced; no documented check-in PA gate is described | 2.8; WS2 JtD; Lived Narrative; Topology Diagram |
| A013 | athenahealth REST API provides programmatic access to PA status, patient records, appointment schedule, and medication lists; Availity provides eligibility via REST | HIGH | Stated in tooling sketch ("REST APIs"); standard capability for both platforms | WS1, WS2, WS3, WS4 JtDs |
| A014 | Current 4-FTE staffing is at or near cognitive capacity for ~180 patients/day given the multi-workstream per-patient load | MEDIUM | Rough calculation: 13–15 min non-PA cognitive time per patient + PA overhead for ~25 cases; with 2 FTEs per site handling 90 patients, per-person load is near ceiling | Exec Summary; Lived Narrative |
| A015 | HIPAA and state medical-records compliance constraints governing AI tool usage at the practice have not been fully specified; a legal review is required before any AI system processes PHI | HIGH | Stated as hard constraint ("HIPAA and state medical-records compliance is non-negotiable") but specific state, BAA requirements, and malpractice insurer stance are not described | Applies to all four workstreams |
| A016 | Dana's Google Sheet PA chase list is the operational source of truth for PA tracking; athenahealth's PA workflow contains submission records but not Dana's insurer behavioral annotations | HIGH | Artefact 5.1 is the Google Sheet. The discovery question implies it is Dana's primary tracking tool. athenahealth records submission dates and status codes, not the tacit chase logic | 2.8; WS2 JtD; Lived Narrative |
| A017 | PA submission is done through athenahealth's native PA workflow and/or insurer portals and fax; no standalone PA management system is in use | MEDIUM | Tooling sketch lists only athenahealth, Availity, DoseSpot, Google Sheets, and phone/paper — no PA-specific tool is mentioned | 2.3; WS2 JtD |
| A018 | Visit-reason triage classification relies significantly on Dana's RN background; staff without clinical training apply more conservative (routine) classifications by default | MEDIUM | Dana is described as RN-trained; discovery question about "patient populations that don't fit the standard intake flow" implies edge cases exist; default behavior of non-RN staff is inferred from the scenario context | 3.4; WS3 JtD; Lived Narrative |
| A019 | Dana's insurer-specific PA behavior patterns (SLA deviations, first-submission denial rules) can be codified into a structured knowledge base through a facilitated elicitation session; 8–12 insurer patterns are sufficient to cover the majority of PA volume, based on the 5-insurer sample visible in Artefact 5.1 | MEDIUM | Artefact 5.1 shows 4 distinct insurer patterns in a single week's data; implies a finite, enumerable set. Codification feasibility assumes Dana's cooperation and a structured interview process | 2.4; 2.6; 03-agentic-solution-architecture.md |
| A020 | Athenahealth's API supports authenticated write operations (documentation tasks 1.7, 3.6, 4.7) and real-time worklist notifications (check-in gate task 2.8) under an executed HIPAA Business Associate Agreement; BAA is required before any agent writes PHI to the EHR | HIGH | athenahealth is documented as a modern SaaS platform with REST APIs [A013]; write and notification capabilities are standard for the platform. BAA requirement follows from hard constraint 3 (HIPAA) and A015 | 1.7; 2.8; 3.6; 4.7; 03-agentic-solution-architecture.md |
| A021 | Portal-based PA submission pathways (via Availity or direct insurer portal APIs) support structured machine-readable responses for at least the top 3 insurers by volume at Westbridge (likely Aetna, UHC, BCBS based on Artefact 5.1); fax remains the fallback for remaining insurers [A017] | MEDIUM | Availity provides eligibility APIs [A013] and also offers PA transaction support; specific insurer portal API coverage at Westbridge is unconfirmed and requires validation with Dana | 2.3; 03-agentic-solution-architecture.md |
| A022 | Fully loaded front-desk staff hourly cost = $40/hour, inclusive of salary, benefits, and management overhead | MEDIUM | US healthcare administrative salary baseline for a mid-Atlantic suburban family practice; Westbridge-specific confirmation needed to refine TCO calculations | volume-×-value-analysis.md |
| A023 | Annual operating days = 250 days/year, representing a standard US work-year adjusted for holiday closures and coverage gaps at a family practice | MEDIUM | Standard US business year assumption; minor variation expected; does not materially change payback period calculations | volume-×-value-analysis.md |
| A024 | Average cost of a visit cancellation caused by a missed or unresolved prior authorization = $250, including physician time, appointment-slot opportunity cost, and patient management overhead | LOW | Industry baseline for primary-care visit disruption cost; actual figure depends on Westbridge's scheduling density and patient mix | WS2 TCO; volume-×-value-analysis.md |

---

## Confidence Level Definitions

| Level | Meaning |
|:-----:|---------|
| HIGH | Directly supported by scenario text or artefact content; low probability of being materially wrong |
| MEDIUM | Consistent with artefacts but requires inference or fills a stated gap; should be verified with Dana |
| LOW | Industry baseline or analogical reasoning; likely directionally correct but Westbridge-specific confirmation needed |

---

## Open Questions: Assumptions to Validate

The following assumptions have the most material impact on Phase 3 (Delegation Qualification) and Phase 4 (Candidate Prioritisation) and should be validated in the next discovery session with Dana. A019–A021 are Phase 3 additions; A022–A024 are Phase 4 additions (TCO calculation inputs — lower validation urgency).

| Priority | ID | Question |
|:--------:|----|----------|
| 1 | A012 | Is there any existing check-in PA gate, even an informal one? Or is the physician consistently the only catch? |
| 2 | A011 | What is the complete set of insurer-specific patterns Dana applies? Can she enumerate them, and are any documented anywhere? |
| 3 | A005 | What does DoseSpot concretely miss, and how often? Is there an informal workaround in place today? |
| 4 | A015 | What specific HIPAA Business Associate Agreement (BAA) terms govern third-party AI tools at Westbridge? Does the malpractice insurer have AI restrictions? |
| 5 | A006 | What percentage of patients are non-portal? Does paper intake create a parallel error pattern? |
| 6 | A007 | How frequent is cross-site rotation, and is any knowledge transfer mechanism in place for covering staff? |
| 7 | A019 | Can Dana enumerate the full set of insurer-specific PA patterns, and is she willing to participate in a structured knowledge-capture session? |
| 8 | A020 | Has Westbridge executed or can it execute a BAA covering API write access to athenahealth by a third-party AI system? |
| 9 | A021 | Which of the top insurers by PA volume at Westbridge support structured portal API submission via Availity? |
