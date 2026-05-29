# CLAUDE.md

This file configures Claude Code's behavior when building the ETA Investigation Agent (DE-3) for Apex Distribution.

---

## Project Purpose

ETA Investigation Agent: automates customer inquiries about missed delivery windows ("Where is my delivery?"). Retrieves GPS location, calculates revised ETA using route timing patterns, and communicates accurate ETA (±30 min, 95% target) via SMS/email. Handles 140 cases/day with 85-95% autonomous coverage.

**Key Entities**: `CustomerInquiry` (inquiry text, order_number, channel), `Order` (delivery_address, committed_delivery_window, customer_priority_tier, delivery_status), `Driver` (GPS coordinates, last_gps_update_timestamp), `Route` (stops, time_bucket), `ETACalculation` (eta_range_start/end, confidence_score), `Escalation` (reason, assigned_to, context_data).

**For detailed entity definitions, state machines, and validation rules, see `specs/4-agent-purpose-document.md` Section 3 (Activity Catalog) and `specs/5-system-data-inventory.md` (integration specs).**

---

## Repository Structure

```
agent-build/
├── CLAUDE.md              # This file
├── src/
│   ├── agent.py           # Main agent orchestrator
│   ├── eta_calculator.py  # ETA calculation engine
│   ├── integrations/      # CRM, Driver App, SMS/Email clients
│   └── validators.py      # GPS freshness, confidence scoring
├── tests/
└── config/
    └── secrets.json       # API keys (OAuth tokens, Twilio, SendGrid)
```

**Reference documents** (in `../specs/`):
- `4-agent-purpose-document.md` — Agent purpose, micro-tasks, autonomy matrix, context engineering
- `5-system-data-inventory.md` — API endpoints, authentication, rate limits, schemas
- `assumptions.md` — All assumptions (A001-A062) with confidence levels

---

## Scope: What You SHOULD Build

1. **Intent Classification** — NLP classifier to identify "ETA inquiry" vs. "complaint" vs. "other"
2. **Order Number Extraction** — Extract order_number from customer message (regex: `AX-\d{3}-\d{4}`)
3. **GPS Freshness Validator** — Check if `(current_timestamp - driver.last_gps_update_timestamp) > 1800 seconds` (30 min threshold)
4. **ETA Calculation Engine** — Algorithm: `remaining_stops × avg_stop_duration + distance_to_customer_km / 40 kmh + traffic_buffer`
5. **Confidence Scorer** — Base 1.0, deduct 0.10 (GPS warning), 0.20 (historical data <20 samples), 0.15 (route volatility >30%), 0.10 (no traffic API)
6. **SLA Breach Detector** — Compare `current_timestamp` vs. `order.committed_delivery_window_end`
7. **Customer Communication Generator** — Draft empathetic SMS/email with ETA range (20-min window)
8. **Escalation Router** — Route to CUSTOMER_SERVICE, DISPATCH_COORDINATOR, or SUPERVISOR based on trigger
9. **API Clients** — Salesforce CRM (OAuth 2.0), Driver App (API key), Twilio SMS, SendGrid Email, Historical Timing DB (PostgreSQL)
10. **Logging & Monitoring** — Token usage, API call latency, escalation dashboard data

---

## Out of Scope: What You Should NOT Build

- **Never calculate ETA if GPS >30 min stale** (escalate instead, see §Guard Rails)
- **Never modify order delivery_status, driver GPS, or route stops** (read-only access)
- **Never bypass confidence threshold** (<0.70 = escalate, see Assumption A044)
- **Never contact drivers directly** (no calls, no SMS to driver phone)
- **Never issue refunds or credits** (SLA breaches escalate to SUPERVISOR for approval)
- **Never expose internal errors to customer** (e.g., "CRM API timeout" → use "We're investigating your delivery status")

---

## Critical Guard Rails

### GPS Freshness (BLOCKING VALIDATION)
```python
if (current_timestamp - driver.last_gps_update_timestamp).total_seconds() > 1800:
    escalate(reason="GPS_STALE")  # Do NOT calculate ETA
    return None
```

### Confidence Threshold
```python
if eta_calculation.confidence_score < 0.70:
    escalate(reason="LOW_CONFIDENCE")  # Do NOT send ETA to customer
```

### Delivery Status Guard Rails
```python
if order.delivery_status in ["LOST", "EXCEPTION", "RETURN_TO_DEPOT"]:
    escalate(reason="AMBIGUOUS_STATUS")  # Requires human intervention
```

---

## Escalation Triggers

**To CUSTOMER_SERVICE**:
- GPS stale (>30 min): "A Customer Service agent is investigating. Update within 15 minutes."
- Low confidence (<70%): "ETA uncertain due to [reason]. Human review requested."
- Customer requests human: "Connecting you to an agent now. Case ref: [escalation_id]."
- Ambiguous order: "We found 2 orders matching your reference. Please confirm..."

**To DISPATCH_COORDINATOR**:
- Driver unreachable: GPS >1 hour stale, no delivery events (possible driver welfare concern)

**To SUPERVISOR**:
- SLA breach + HIGH_PRIORITY customer: Supervisor approves goodwill action before agent sends message
- Consignment lost: Escalate with full order context for depot search

**For full escalation logic, see `specs/4-agent-purpose-document.md` Section 4 (Autonomy Matrix).**

---

## Integration Constraints

**Salesforce CRM** (`GET /sobjects/Order/{id}`, `POST /sobjects/Case`):
- OAuth 2.0, timeout 5s, retry once
- Rate limit: 100K calls/24h (agent uses 420/day = 0.4%)
- If timeout → escalate with reason "CRM_UNAVAILABLE"

**Driver App** (`GET /drivers/{id}/location`, `GET /deliveries/{id}/status`):
- API key auth, timeout 5s, retry once
- **CRITICAL**: API availability unconfirmed (Assumption A003, A053). Week 1 Go/No-Go validation required.
- If timeout → escalate with reason "GPS_UNAVAILABLE"

**Historical Timing DB** (PostgreSQL):
- Query: `SELECT avg_stop_duration_min FROM route_timings WHERE route_id=? AND time_bucket=?`
- Timeout 1s, fallback: use 15 min/stop default (Assumption A055)
- Cache route timings 24h (prompt caching saves £369/year, see Assumption A030)

**SMS/Email** (Twilio, SendGrid):
- Timeout 10s, retry once
- If fails → mark inquiry FAILED, alert ops (do not spam customer with retries)

**For full endpoint specs, authentication, and fallback logic, see `specs/5-system-data-inventory.md` Sections 2-7.**

---

## Naming Conventions

- **Database tables**: snake_case, plural (`customer_inquiries`, `orders`, `drivers`)
- **API fields**: snake_case (match DB columns: `order_number`, `delivery_status`, `eta_range_start`)
- **Enums**: SCREAMING_SNAKE_CASE (`OUT_FOR_DELIVERY`, `GPS_STALE`, `HIGH_PRIORITY`)
- **Timestamps**: ISO 8601 with timezone (store UTC, display location timezone)

---

## When to Ask vs When to Decide

**Decide alone** (no user prompt):
- Validate order_number format, GPS freshness, confidence threshold
- Classify inquiry_type via NLP
- Calculate ETA using documented algorithm
- Detect SLA breach (timestamp comparison)
- Send SMS/email (if escalation_required = false)
- Log case in CRM

**Ask the user before proceeding**:
- CRM/Driver App API unavailable (all retries failed): "Should I escalate all inquiries or retry in 5 minutes?"
- Ambiguous order reference: "Order number unclear. Did you mean AX-771-3344 or AX-772-3344?"
- Historical timing data sample_size = 0: "No data for route [id]. Use default 15 min/stop (low confidence) or escalate?"

**Never ask**:
- "Should I calculate ETA if GPS is stale?" (NO, always escalate per guard rail)
- "Should I send ETA if confidence <0.70?" (NO, always escalate per guard rail)
- "Should I provide ETA for LOST consignment?" (NO, always escalate per guard rail)

---

## Assumptions & Risks

**Critical assumptions** (see `specs/assumptions.md` for full list):
- [A003, A053] Driver App API available (HIGH RISK, Week 1 validation required)
- [A042] 95% ETA accuracy target (±30 min)
- [A044] 70% confidence threshold for autonomous action
- [A045] 30 min GPS staleness threshold
- [A054] Historical timing data completeness (MEDIUM RISK)

**If assumptions fail, see `specs/7-risk-scenario-analysis.md` for contingency plans** (e.g., if Driver App API unavailable → pivot to DE-4 as Wave 1 pilot).

---

## Document Control

- **Version**: 1.0
- **Created**: 2026-05-06
- **Owner**: AI FDE Team
- **Next Steps**: Week 1 discovery validation (API availability, GPS reliability, data completeness)
