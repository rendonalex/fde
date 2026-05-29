# Assumptions Log — HR Onboarding Coordination

## Volume & Timing Assumptions

**A01** — *190 new-hire setup cases/year distributed evenly throughout year*
- **Confidence**: Medium (60%)
- **Basis**: Brief states "~190/yr" but no seasonality indicated
- **Impact**: Affects staffing model and queue management strategy
- **What would change this**: Hiring spikes tied to fiscal quarters, grad recruiting cycles, consulting seasonal demand

**A02** — *3-hour "effective handling" spread across 2 weeks implies 20-25 touchpoints*
- **Confidence**: Low (40%)
- **Basis**: Calculation from stated duration; artefact 1.2 shows active monitoring
- **Impact**: Critical for understanding cognitive load distribution and delegation boundaries
- **What would change this**: Actual time-log data; task analysis of Priya's tracker updates

**A03** — *Compliance training assignment volume (~220/yr) includes all hire types*
- **Confidence**: High (85%)
- **Basis**: Brief states ~220/yr matches total hires including contractors/secondments
- **Impact**: Flowchart routing logic must handle all edge cases
- **What would change this**: Confirmation whether TEMP-EXT retirements affected volume

**A04** — *Edge-case resolution (30-50/yr) represents 15-25% of total hire volume*
- **Confidence**: Medium (65%)
- **Basis**: Math from stated volumes
- **Impact**: Exception-handling capacity requirement
- **What would change this**: Post-Brexit right-to-work changes; contractor conversion policy shifts

**A05** — *"Unpredictable" 4 hrs/case for edge cases means no advance warning*
- **Confidence**: Medium (60%)
- **Basis**: Brief characterization; no artefact evidence of predictive indicators
- **Impact**: HITL escalation paths must be immediate-response
- **What would change this**: Pattern analysis of historical edge cases; early warning indicators from recruiting

## Tooling & Integration Assumptions

**A06** — *Workday REST APIs are production-ready and documented*
- **Confidence**: High (80%)
- **Basis**: Brief states "REST APIs available"; Workday is modern SaaS
- **Impact**: Core data source reliability for agent
- **What would change this**: API rate limits, data freshness SLAs, authentication complexity

**A07** — *Saba LMS "no API" means data extraction requires workarounds*
- **Confidence**: High (85%)
- **Basis**: Explicit statement in brief
- **Impact**: Training assignment automation requires alternative integration (email parsing, UI automation, manual)
- **What would change this**: Discovery of Saba webhook support, CSV export automation, or replacement LMS consideration

**A08** — *ServiceNow "robust auto-routing" works for standard cases but failed for Tom Reeves*
- **Confidence**: High (90%)
- **Basis**: Artefact 1.1 — "consulting laptop spec changed last quarter and the auto-routing didn't pick it up"
- **Impact**: IT request generation requires spec validation before submission
- **What would change this**: ServiceNow configuration audit; consulting-specific routing rules

**A09** — *Outlook is primary communication channel (not Workday, not SharePoint)*
- **Confidence**: High (85%)
- **Basis**: Brief states "most stakeholder communication" via Outlook; artefact 1.1 is email thread
- **Impact**: Agent notification strategy must integrate with email
- **What would change this**: Microsoft Teams adoption; Workday notification preferences

**A10** — *SharePoint onboarding doc library is read-only for coordinators*
- **Confidence**: Medium (55%)
- **Impact**: Agent cannot update templates or policies directly
- **What would change this**: Coordinator permissions audit; document management workflow

## Stakeholder & Organizational Assumptions

**A11** — *CFO's "look at AI options" request is reactive to consulting division complaints*
- **Confidence**: High (90%)
- **Basis**: Brief explicitly states this; artefact 1.1 confirms consulting director's escalation path to CFO
- **Impact**: Consulting hires are high-visibility test cases; failure = project termination
- **What would change this**: CFO's actual mandate (cost reduction vs speed vs quality)

**A12** — *3-person HR Ops team operates at capacity with current volumes*
- **Confidence**: Medium (70%)
- **Basis**: Implied by CFO pressure and onboarding delays surfacing as complaints
- **Impact**: No slack for manual escalation handling without process change
- **What would change this**: Team utilization data; overtime patterns; backlog size

**A13** — *Priya updates Master Tracker first, then Workday end-of-week*
- **Confidence**: High (95%)
- **Basis**: Artefact 1.2 explicit note
- **Impact**: Excel is system of record in practice; Workday lag creates data staleness
- **What would change this**: Priya's actual workflow observation; data reconciliation frequency

**A14** — *"Workday status" vs "Visible status" implies dual-tracking for stakeholder management*
- **Confidence**: High (90%)
- **Basis**: Artefact 1.2 column structure
- **Impact**: Agent must maintain human-readable status separate from system status
- **What would change this**: Rationale for dual status (reporting up? managing expectations?)

**A15** — *Hidden columns (Notes, Risk flag, Buddy override) contain decision context not in Workday*
- **Confidence**: High (95%)
- **Basis**: Artefact 1.2 shows tacit knowledge in hidden fields
- **Impact**: Critical context for delegation boundaries; agent needs structured access to this
- **What would change this**: Full tracker schema; decision rules for risk flags and overrides

## Process & Policy Assumptions

**A16** — *Buddy assignment follows documented rules except for high-profile hires*
- **Confidence**: High (85%)
- **Basis**: Artefact 1.2 Tom Reeves buddy override
- **Impact**: Agent-led buddy matching requires escalation path for VIP hires
- **What would change this**: Full buddy matching policy; override criteria; who authorizes overrides

**A17** — *Compliance training flowchart v4.2 (Oct 2023) is 18+ months stale*
- **Confidence**: High (90%)
- **Basis**: Artefact 1.3 footnote "TEMP-EXT retired 2024-Q1 — update flowchart sometime"
- **Impact**: Documented process != lived process; agent needs current routing logic
- **What would change this**: Current routing rules from Priya; TEMP-EXT volume and actual routing

**A18** — *Contractor→FTE conversions don't pull compliance history*
- **Confidence**: High (90%)
- **Basis**: Artefact 1.2 Maria Costa note
- **Impact**: Agent must handle data reconciliation for conversion cases
- **What would change this**: Workday data model for conversions; compliance history data location

**A19** — *Returning hires with frozen records require manual IT/Workday triage*
- **Confidence**: High (90%)
- **Basis**: Artefact 1.2 James O'Connor note
- **Impact**: Edge case requiring human escalation; agent can detect but not resolve
- **What would change this**: IT duplicate detection logic; Workday record lifecycle rules

**A20** — *Building access and badge ordering are separate systems from Workday/ServiceNow*
- **Confidence**: Medium (70%)
- **Basis**: Brief mentions these as part of setup but no tooling detail
- **Impact**: Additional integration points required
- **What would change this**: Actual badge/access system identification; API availability

## Risk & Compliance Assumptions

**A21** — *Right-to-work checks (Home Office share-code) are manual and time-sensitive*
- **Confidence**: High (85%)
- **Basis**: Brief lists "late right-to-work checks" as edge case; UK context implies Home Office integration
- **Impact**: Agent cannot make right-to-work decisions; can only track and escalate
- **What would change this**: Home Office Employer Checking Service API integration capability

**A22** — *UK vs Republic of Ireland compliance differences affect ~15% of hires*
- **Confidence**: Medium (60%)
- **Basis**: Brief mentions "small Dublin team"; compliance training differs by country
- **Impact**: Country-specific routing rules required
- **What would change this**: Actual Dublin hire volume; Ireland-specific compliance requirements

**A23** — *No GDPR/data-access constraints explicitly stated in brief*
- **Confidence**: Low (30%)
- **Basis**: Absence in brief; UK firm implies GDPR UK compliance required
- **Impact**: Agent design must assume GDPR constraints on personal data access and retention
- **What would change this**: Aldridge & Sykes data governance policy; legal review of agent data access

## Automation History Assumptions

**A24** — *No prior automation attempts mentioned in brief*
- **Confidence**: Low (40%)
- **Basis**: Absence in brief; discovery question explicitly asks about this
- **Impact**: Unknown risk aversion or lessons learned from prior failures
- **What would change this**: Coach role-play question about automation history

**A25** — *ServiceNow auto-routing issue (Tom Reeves) is symptom of configuration drift*
- **Confidence**: High (80%)
- **Basis**: Artefact 1.1 "consulting laptop spec changed last quarter and the auto-routing didn't pick it up"
- **Impact**: Agent-generated ServiceNow tickets require validation against current specs
- **What would change this**: ServiceNow change management audit; consulting spec update frequency

## Cognitive Load Distribution Assumptions

**A26** — *Priya's hidden tracker columns represent 20-30% of cognitive load*
- **Confidence**: Medium (65%)
- **Basis**: Artefact 1.2 decision context in Notes/Risk flag/Buddy override
- **Impact**: Offloading routine tasks won't address highest-value cognitive work
- **What would change this**: Time study of Priya's actual work; cognitive load hotspot mapping

**A27** — *30-day check-in scheduling (60 min across first 30 days) implies 4-6 touchpoints*
- **Confidence**: Medium (60%)
- **Basis**: Math from stated duration
- **Impact**: Agent scheduling automation must handle multi-stage cadence
- **What would change this**: Actual check-in template; escalation triggers

**A28** — *Chasing compliance training (~45 min/case) is primarily communication overhead*
- **Confidence**: Medium (70%)
- **Basis**: Brief characterization "assignment plus chasing"
- **Impact**: Agent value = reducing follow-up communication
- **What would change this**: Actual time breakdown (assignment vs tracking vs chasing)

## Stakeholder Relationship Assumptions

**A29** — *Mike Tehrani (Consulting Director's PA) escalates directly to CFO*
- **Confidence**: High (90%)
- **Basis**: Artefact 1.1 "The director has emailed the CFO"
- **Impact**: Consulting hires are politically sensitive; agent failures will escalate quickly
- **What would change this**: Consulting division org chart; escalation protocols

**A30** — *"Director's hire from Deloitte" implies external senior hires get special treatment*
- **Confidence**: High (85%)
- **Basis**: Artefact 1.2 note emphasizes this context
- **Impact**: Agent must flag high-profile hires for human oversight
- **What would change this**: VIP hire identification criteria; special handling protocols
