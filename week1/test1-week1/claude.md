# HR Onboarding Automation Agent

## Project Overview

Agentic solution for a regional professional services firm (1,200 employees, 220 hires/year) to automate new-hire onboarding across Workday, ServiceNow, and email systems. Target: eliminate coordination overhead across 6 disconnected systems, reduce HR Ops time per hire from 2.0 hours to 0.43 hours (79% reduction), and reduce error rate from 8% to 2.5%.

## Current Capability: Phase 1 - Fully Agentic Tasks

**Automation Scope**: Three fully autonomous onboarding tasks that eliminate 0.77 hours per hire without human-in-the-loop:
1. **IT Provisioning** – Read employee data from Workday, map role to IT access template, create ServiceNow ticket, validate completion
2. **Welcome Materials** – Generate personalized welcome email from template (on-site vs. remote variants), send at Day -7 before start date
3. **30-Day Checkpoint Scheduling** – Query calendar availability, find 30-min slot for new hire + manager + HR, send meeting invite

**Success Target**: 95% automation success rate, zero critical errors, IT access ready by Day 0, all tasks completed without human intervention.

**Specification**: See [specs/fully-agentic-tasks](specs/fully-agentic-tasks) for complete capability design (core entities, state machines, validation rules).

## Project Structure

```
test-week1/
├── analysis-docs/
│   ├── delegation-analysis          # Strategy: 3 fully agentic, 3 agent-led, 1 human-led
│   ├── problem-statement           # Quantified business case & success metrics
│   └── scenario-description        # Scenario overview
├── specs/
│   └── fully-agentic-tasks         # Phase 1 capability spec (entities, APIs, workflows)
└── claude.md                       # This file
```

**Key Documents**:
- [delegation-analysis](analysis-docs/delegation-analysis) – Business case, ROI, implementation roadmap
- [fully-agentic-tasks](specs/fully-agentic-tasks) – Technical specification for Phase 1

## Development Guidelines

### Scope & Constraints
- **Phase 1 only**: Automate the 3 fully agentic tasks. Phase 2 & 3 are future.
- **No new infrastructure**: Integrate with existing Workday, ServiceNow, email APIs (assume production-ready per A12).
- **Agent database**: Simple audit/state store for IT provisioning, welcome emails, checkpoint scheduling (not a full system-of-record).
- **Error handling**: Conservative approach – any API error, data validation failure, or edge case triggers escalation to HR Ops queue.

### Critical Assumptions to Validate
- **A13** – 80% of roles have documented IT access templates (audit IT documentation)
- **A17** – Welcome email template covers 95% of scenarios (on-site vs. remote, locations, roles)
- **A12** – APIs available and production-ready (request docs, test authentication)

### Testing & Validation
- Pilot: 10-20 real onboardings before full rollout
- Success metric: 95% of tasks complete without human intervention
- Error tracking: Log all failures with reason; weekly review to refine rules

## Guardrails: What the Agent Should NOT Do

### Universal Guardrails (All Tasks)
- Never modify source systems (Workday read-only, ServiceNow template-only)
- Never bypass validation steps (email RFC 5322, start_date business days, employee status PENDING)
- Never create duplicates (query first, DB unique constraints on employee_id)
- Never modify immutable fields (created_at, employee_id, ticket numbers)
- Never delete audit logs (all actions logged with timestamp, status changes, failure reasons)

### IT Provisioning Guardrails
- **Never provision without an IT template** – Escalate to HR Ops + IT if no template exists for role+department
- **Never provision for non-PENDING employees** – Status check required; only pre-start hires
- **Never bypass template lookup** – Always check registry; never custom-map roles
- **Never mark COMPLETED if ServiceNow status ≠ "Closed Complete"** – Validate in AD before completion
- **Never submit <5 days or >30 days before start_date** – Submission timing critical; outside window = escalate

### Welcome Materials Guardrails
- **Never send to invalid email addresses** – RFC 5322 validation required; escalate if email fails format check
- **Never send executive welcome emails without HR Ops approval** – Detected roles (Partner, Director, VP) require manual review
- **Never resend after initial send** – If delivery fails, alert HR Ops instead of auto-retry (avoid confusion)
- **Never send outside 09:00-17:00 business hours in employee timezone** – Respect timezone, never send nights/weekends
- **Never use unresolved template variables** – If manager name/location not found, use fallback ("your manager", "Contact HR") and log warning

### 30-Day Checkpoint Guardrails
- **Never schedule <24h notice** – Minimum lead time 24h for calendar invites
- **Never reschedule >2 times** – After 2nd decline, escalate to HR Ops; manual coordination required
- **Never schedule outside 28-32 day window** – Window is strict; do not negotiate
- **Never omit any participant** – Must include employee, manager, HR Ops; partial scheduling = failure
- **Never schedule during business hour conflicts** – Check all 3 calendars; no overlaps allowed

---

## When to Ask (Escalate) vs. When to Decide (Proceed Alone)

### Agent Decides Alone (No Escalation)
**Data Validation & Lookup**:
- Validate email format (RFC 5322 regex)
- Map role + department to IT template (exact lookup table match)
- Calculate send/schedule timestamps (arithmetic: start_date ± N days)
- Determine employee timezone from location (lookup table)
- Check for duplicates (query employee_id, confirm no prior onboarding record)

**Routine Decisions**:
- Template selection matches rules exactly (no ambiguity = proceed)
- All required fields present and valid (proceed)
- Submit timing within window (proceed)
- Assign HR Ops via round-robin (proceed)
- Query availability and find slot in window (proceed)

### Agent Decides + Logs Audit Trail
**Actions Requiring Audit Records**:
- Submit ServiceNow ticket (log: template, ticket number, employee_id)
- Send welcome email (log: template version, recipient_email, SMTP message ID)
- Create calendar event (log: event ID, participants, scheduled_date)
- Update status (every status change logged with timestamp, reason, from/to state)
- Retry API call (log: attempt number, error code, response)
- Assign HR Ops (log: assignment method, assigned user_id)
- Cancel task (log: reason, cascade delete if employee deleted)

### Agent Escalates (Human Decides)

**Critical Blocks – Escalate Immediately**:
- **No IT template for role** → Escalate to HR Ops + IT team; decision: create template or block provisioning
- **Email validation fails (invalid RFC 5322)** → Escalate to HR Ops; decision: fix data or block send
- **Employee data incomplete** (missing role, department, manager_id) → Escalate to HR Ops; decision: fill data or skip hire
- **Workday unavailable >5 min** → Escalate to IT Ops; decision: retry or pause agent
- **ServiceNow unavailable >5 min** → Queue requests, escalate to IT Ops at 24h; decision: restore service or manual workaround
- **Email system (SMTP) unavailable >5 min** → Queue emails, escalate to IT Ops at 24h; decision: restore or manual send

**Edge Case Escalations**:
- **Executive role detected** (Partner, Director, VP) → Escalate to HR Ops + Slack; decision: approve, customize, or block
- **No available meeting slot in 28-32 window** → Escalate to HR Ops; decision: schedule outside window, use async survey, or defer
- **Meeting rescheduled twice** (both participants declined) → Escalate to HR Ops; decision: manual intervention or async approach
- **ServiceNow ticket "Closed Incomplete"** → Escalate to IT; decision: investigate error, fix, retry
- **Email bounced (permanent failure)** → Escalate to HR Ops; decision: correct address or manual delivery
- **Start date changes >3 days after submission** → Escalate to HR Ops; decision: update ticket, resend email, or reschedule
- **Submission deadline approaching** (start_date - 1 day, not completed) → Escalate to HR Ops + IT; decision: expedite or flag risk
- **Rescheduled meeting >2 times** → Escalate to HR Ops; decision: abandon checkpoint or manual scheduling

---

## Future Capabilities (Roadmap)

### Phase 2: Agent-Led with Human Oversight (Months 4-6)
Target: Reduce HR Ops time by additional 0.60 hours per hire via agent proposals + human approval

- [ ] **Capability 2.1 – Benefits Enrollment** – Agent applies eligibility rules, detects edge cases (contractors, part-time, state-specific), generates communication for approval
- [ ] **Capability 2.2 – Compliance Training Assignment** – Agent applies training matrix, detects edge cases (contractors with manager titles, dual roles), proposes assignments for approval
- [ ] **Capability 2.3 – Buddy Matching** – Agent queries org chart, filters candidates (same dept, seniority, workload), ranks matches, presents top 3 for selection

### Phase 3: Human-Led with Agent Support (Months 7-9)
Target: Reduce HR Ops time by additional 0.18 hours per hire via agent decision support + draft generation

- [ ] **Capability 3.1 – Manager Handoff** – Agent compiles task completion status, gathers new hire feedback, detects issues, drafts handoff email for HR Ops review & send

---

## Metrics & Success Criteria

| Metric | Current | Target | Phase |
|--------|---------|--------|-------|
| HR Ops time/hire | 2.0 hrs | 0.43 hrs | 1-3 |
| Error rate | 8% | 2.5% | 1-3 |
| Automation success rate | — | 95% | 1 |
| System context switches | 12 | 2.5 | 1-3 |

See [problem-statement](analysis-docs/problem-statement) for detailed metrics and financial impact.
