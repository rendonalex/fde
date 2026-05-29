# Assumptions Register: Apex Distribution Customer Operations

This file tracks all assumptions made across the ATX assessment phases. Assumptions A001–A027 were established in Phase 2 (Cognitive Load Map) and Phase 3 (Delegation Suitability Matrix). Assumptions A028–A033 are introduced in Phase 4 (Volume × Value Analysis).

---

## Phase 2–3 Assumptions (A001–A027)

These assumptions are referenced in `specs/1-cognitive-load-map.md` and `specs/2-delegation-suitability-matrix.md`. Reproduced here for completeness.

| ID | Assumption | Confidence | Phase Introduced |
|----|-----------|------------|-----------------|
| A001 | Dispatch adjustment volume breakdown: ~40% DA-1 (Additional Pickup), ~30% DA-2 (Route Diversion), ~15% DA-3 (Driver Swap), ~15% other | Medium | Phase 2 |
| A002 | Senior dispatcher (Sandra/Sarah) expertise is concentrated; driver selection and swap decisions depend on relationship knowledge not in systems | High | Phase 2 |
| A003 | Driver App API provides read-only GPS and delivery status access; write/task-assignment not available | Medium | Phase 2 |
| A004 | Dispatch console (Java/Citrix) has limited/no write API; route updates require manual console entry | High | Phase 2 |
| A005 | Refused delivery disposition decision tree is not formally documented; currently relies on dispatcher discretion | High | Phase 2 |
| A006 | Historical refused delivery classifications are available in CRM or can be extracted for NLP training | Medium | Phase 2 |
| A007 | Aurum billing system processes credits via 24–48h batch export; no real-time API available | High | Phase 2 |
| A008 | Sandra has manual override credit authority that currently bypasses the Aurum audit trail | High | Phase 2 |
| A009 | Customer priority/tier system is tacit knowledge (e.g., "Hayes & Sons always gets Sandra"); not formalised in CRM | High | Phase 2 |
| A010 | ETA calculation relies on dispatcher tacit knowledge of route timing; driver app does not provide predictive ETA | High | Phase 2 |
| A012 | ~25% of cases span multiple workstreams (delivery exception → billing dispute → dispatch adjustment) | Medium | Phase 2 |
| A013 | CRM data quality (customer addresses, delivery instructions) is sufficient for agent validation of pickup requests | Medium | Phase 2 |
| A014 | Drivers prefer voice communication for complex or negotiated interactions; driver app messaging used for simple instructions | Medium | Phase 2 |
| A015 | API schemas (CRM, driver app) are stable enough to build against without frequent breaking changes | Medium | Phase 2 |
| A016 | DA-3 (Driver Swap) volume is ~10–15 cases/day; lower due to infrequency of driver emergencies | Medium | Phase 3 |
| A017 | Damage liability assessment criteria (transit vs. packaging fault) are not formally documented | High | Phase 2 |
| A018 | Fully loaded FTE salary is £35,000/year (includes salary + benefits + management overhead) | Medium | Phase 2 |
| A019 | Route diversion decision rules (what counts as "unacceptable" delay) are not formally documented | High | Phase 3 |
| A020 | ~40% of route diversions have complicating factors (driver unreachable, cascading delays, customer refuses alternate timing) | Medium | Phase 3 |
| A021 | DA-3 (Driver Swap) average handling time is 25–30 minutes due to negotiation and coordination complexity | Medium | Phase 3 |
| A022 | DE-1 (Refused Delivery) volume is ~54 cases/day (30% of 180 daily delivery exceptions) | Medium | Phase 3 |
| A023 | DE-2 (Damaged Consignment) volume is ~36 cases/day (20% of 180 daily delivery exceptions) | Medium | Phase 3 |
| A024 | DE-3 (Missed Window) volume is ~140 cases/day (35% of ~400 daily ETA inquiries require investigation beyond simple lookup) | Medium | Phase 3 |
| A025 | DE-4 (Unattended Address) volume is ~45 cases/day (25% of 180 daily delivery exceptions) | Medium | Phase 3 |
| A026 | Policy conflicts in DE-4 (signature required but customer has safe-place authority on file) occur in ~5% of unattended address cases | Low | Phase 3 |
| A027 | Build cost estimates (greenfield): DE-3 £25K · DE-4 £17K · DA-1 £25K · DE-1 £35K · DA-2 £28K · DE-2 £35K. Actual costs depend on integration complexity and team day rates | Low | Phase 3 |

---

## Phase 4 Assumptions (A028–A033)

Introduced in `specs/volume-×-value-analysis.md` for TCO calculations and sequencing logic.

| ID | Assumption | Confidence | Rationale |
|----|-----------|------------|-----------|
| A028 | Claude Sonnet API pricing: £0.003/1K input tokens, £0.015/1K output tokens (approximate, inclusive of infrastructure markup) | Low | Based on Anthropic published pricing converted to GBP at £1 = $1.27; subject to change. Used for TCO modelling only — validate against actual contract pricing before business case finalisation. |
| A029 | Tool/API call overhead cost: £0.005 per call (infrastructure, API gateway, logging overhead combined) | Low | Blended estimate covering CRM API calls, driver app queries, notification sends. Validate against actual AWS/infrastructure billing during pilot. |
| A030 | 250 working days per year for volume annualisation | High | Standard UK working year (52 weeks × 5 days − bank holidays). Excludes seasonal variation — Apex Distribution may have higher Q4 volumes [validate]. |
| A031 | 1,750 working hours per year (7 hours/day × 250 days), yielding an effective £20/hr fully loaded rate from £35K FTE [A018] | High | Standard assumption. Does not account for part-time or shift-based staffing mix. |
| A032 | Wave 2 candidates inherit ~30% of Wave 1 infrastructure (CRM integration, Driver App client, notification automation, audit logging), reducing marginal build costs by ~30% relative to greenfield estimates [A027] | Medium | Based on component reuse analysis: CRM and Driver App integrations are reused across all six agentic candidates. Actual savings depend on code architecture decisions during Wave 1 build. |
| A033 | Image recognition model for DE-2 (Damaged Consignment) must achieve ≥85% damage severity classification accuracy on a held-out test set before production deployment | Medium | Threshold set based on acceptable false-negative rate (missed damage → customer dissatisfaction) and false-positive rate (over-credited claims → margin erosion). Should be validated with Sandra and finance team before committing to threshold. Minimum ~6 months of labelled damage photo data required for training. |

---

## Assumption Risk Summary

| Risk Level | Assumptions | Mitigation |
|------------|-------------|------------|
| **High impact if wrong** | A004, A005, A007, A009, A010, A017, A019 | Critical path validations — resolve before Wave 1 build begins |
| **Medium impact** | A001, A022–A025, A027, A028–A032 | Validate during pilot; adjust TCO model as actuals emerge |
| **Low impact** | A006, A013–A015, A026, A033 | Monitor; revisit if anomalies detected in pilot data |

---

## Document Control

- **Created**: 2026-05-11
- **Version**: 1.0
- **Owner**: AI FDE Team
- **Related Documents**: All `specs/` phase documents reference assumptions using `[Ref: A###]` notation
