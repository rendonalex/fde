# System and Data Inventory: ETA Investigation Agent (DE-3)

## Document Purpose

This inventory catalogs all systems, data sources, APIs, and infrastructure required for the ETA Investigation Agent to operate in production. It identifies availability, access requirements, integration effort, gaps, and risks for each dependency.

---

## Table of Contents

1. [System Integration Summary](#system-integration-summary)
2. [Primary Systems](#primary-systems)
3. [Supporting Systems](#supporting-systems)
4. [Data Sources](#data-sources)
5. [External Services](#external-services)
6. [Infrastructure Requirements](#infrastructure-requirements)
7. [Integration Gaps and Risks](#integration-gaps-and-risks)
8. [Data Quality Assessment](#data-quality-assessment)
9. [Security and Compliance](#security-and-compliance)

---

## System Integration Summary

The ETA Investigation Agent requires integration with **4 primary systems**, **2 supporting systems**, **3 data sources**, and **2 external services**.

| System / Service | Purpose | Integration Type | Availability | Build Effort | Risk Level |
|------------------|---------|------------------|--------------|--------------|------------|
| **Salesforce CRM** | Customer records, order details, case management | REST API (read/write) | ✅ Available | Medium (2 weeks) | Low |
| **Driver App** (iOS/Android) | GPS location, delivery status, route sequence | REST API (read-only) | ⚠️ Assumed available [A003] | Medium (2 weeks) | Medium |
| **Dispatch Console** | Route planning (for context only, no writes) | Limited API (read-only) [A004] | ⚠️ Constrained | Low (1 week, read-only) | Low |
| **Historical Timing DB** | Route timing patterns for ETA calculation | PostgreSQL DB | ❌ Build required | High (3 weeks: ETL + schema) | Medium |
| **SMS Gateway** | Customer notifications | REST API | ✅ Available (Twilio/similar) | Low (1 week) | Low |
| **Email Service** | Customer notifications | REST API | ✅ Available (SendGrid/similar) | Low (1 week) | Low |
| **Traffic API** (optional Wave 1) | Real-time traffic conditions | REST API | ✅ Available (Google Maps/HERE) | Low (1 week) | Low |
| **Agent Monitoring** | Token usage, API calls, escalations, audit logs | Custom platform | ❌ Build required | Medium (2 weeks) | Low |

**Total Integration Effort**: 12-14 weeks (parallelizable: CRM + Driver App + SMS/Email can build concurrently)

---

## Primary Systems

### 1. Salesforce CRM

**Purpose**: Central customer and order management system. Agent retrieves order details, customer contact info, SLA terms, and logs case records for audit.

**System Details**:
- **Platform**: Salesforce Service Cloud
- **Version**: Assumed latest (API compatibility confirmed with IT)
- **Deployment**: Cloud (Salesforce-hosted)
- **Authentication**: OAuth 2.0
- **Base URL**: `https://apex-distribution.salesforce.com/services/data/v60.0/` [Ref: A049]

**Data Needed**:
| Data Entity | Fields Required | Usage | Availability |
|-------------|-----------------|-------|--------------|
| **Orders** | `id`, `order_number`, `customer_id`, `delivery_address`, `consignment_value`, `committed_delivery_window` (start/end timestamps), `customer_priority_tier` [A009], `route_id`, `driver_id` | Order lookup by order number; SLA breach detection; customer priority check | ✅ Available (standard Salesforce objects) |
| **Customers** | `id`, `name`, `contact_email`, `contact_sms`, `communication_preference` (email/SMS), `inquiry_history_count` (custom field [A048]) | Customer contact for notifications; inquiry history for escalation pattern detection | ✅ Available (email/SMS in Contact object; inquiry_history_count may need custom field [A050]) |
| **Cases** | `id`, `order_id`, `inquiry_type`, `inquiry_timestamp`, `agent_actions` (JSON), `escalation_flag`, `escalation_reason`, `resolution_notes` | Case creation for audit trail; escalation logging | ✅ Available (standard Case object; custom fields for agent_actions JSON [A051]) |

**Access Type**: **Read/Write**
- **Read**: `GET /sobjects/Order/{id}`, `GET /sobjects/Contact/{id}`, `GET /query?q=SELECT...` (SOQL queries)
- **Write**: `POST /sobjects/Case`, `PATCH /sobjects/Order/{id}` (add notes), `POST /sobjects/Task` (escalation tasks)

**Availability**: ✅ **Available** — Salesforce REST API is production-ready. OAuth 2.0 client credentials flow supported.

**Integration Effort**: **Medium (2 weeks)**
- Week 1: OAuth client setup, SOQL query development, error handling (rate limits, retries)
- Week 2: Custom field creation (inquiry_history_count, agent_actions JSON), testing, staging validation

**Rate Limits**: 
- Salesforce API limits: 100,000 API calls/24 hours for Enterprise Edition [Ref: A052]
- Agent usage: 140 cases/day × 3 API calls (order, contact, case creation) = **420 calls/day** (0.4% of limit, no risk)

**Gaps / Risks**:
- **Customer priority tier field** [A009]: May not exist in Salesforce. If missing, requires:
  - Option 1: Create custom field `Customer_Priority_Tier__c` on Contact object (manual data migration from tacit knowledge)
  - Option 2: Use proxy field (e.g., `Account.AnnualRevenue` threshold: >£500K = high-priority)
  - **Risk**: Medium — Customer priority is critical for SLA breach escalation. If unavailable, all customers treated equally (suboptimal).
  - **Mitigation**: Phase 2 Wave 2 prep formalizes priority system [A009]; use revenue proxy in Wave 1 pilot.

- **Inquiry history count field** [A048]: Used to detect repeat inquiries (escalation signal). If missing, query Case history on demand (higher API cost).
  - **Risk**: Low — Fallback is viable (query Cases where contact_id = X, created_date > 30 days ago).

**Data Quality** (see Data Quality Assessment section): Medium-High (CRM data generally clean; address standardization may vary)

---

### 2. Driver App (iOS/Android)

**Purpose**: Real-time GPS location, delivery status, and route sequence for ETA calculation. Agent queries driver app backend API.

**System Details**:
- **Platform**: In-house iOS/Android app with backend REST API
- **Version**: Current production version (details TBD with IT discovery [A053])
- **Deployment**: On-premise or cloud (TBD)
- **Authentication**: API key (assumed) or OAuth 2.0 (TBD)
- **Base URL**: `https://driver-app.apex-distribution.com/api/v1/` [Ref: A053]

**Data Needed**:
| Data Entity | Fields Required | Usage | Availability |
|-------------|-----------------|-------|--------------|
| **Drivers** | `id`, `current_location` (lat, lon), `last_gps_update_timestamp`, `route_id`, `status` (active, offline, on_break) | GPS location retrieval; GPS freshness validation (>30 min = stale [A045]) | ⚠️ **Assumed available** [A003] — Read-only API assumed to exist. **Validation required**. |
| **Deliveries** | `id`, `order_id`, `status` (out_for_delivery, delivered, failed_attempt, return_to_depot, exception, lost), `delivery_timestamp`, `failure_reason` (if failed), `driver_id` | Delivery status lookup; escalation triggers (lost, exception status) | ⚠️ **Assumed available** [A003] — Delivery events logged in driver app. **Validation required**. |
| **Routes** | `id`, `stops` (array of {stop_id, address, sequence_number, delivery_id}), `route_plan` (stop sequence), `assigned_driver_id` | Route sequence for ETA calculation (driver at stop 4 of 9) | ⚠️ **Assumed available** [A003] — Route plans assigned to drivers. **Validation required**. |

**Access Type**: **Read-Only**
- **Read**: `GET /drivers/{id}/location`, `GET /deliveries/{id}/status`, `GET /routes/{id}/stops`
- **Write**: ❌ Not required for ETA Investigation Agent (driver app is data source, not action target)

**Availability**: ⚠️ **Assumed Available** [Ref: A003] — Driver app has GPS and delivery status data, but **API access not confirmed**. 

**Integration Effort**: **Medium (2 weeks)**
- **Discovery Phase** (3 days): Technical discovery with IT team to confirm:
  - Does driver app backend expose REST API? (If not, requires API wrapper build → +1-2 weeks)
  - What is authentication method? (API key, OAuth, or direct DB query?)
  - What is data freshness? (GPS update frequency: real-time, 5 min intervals, on-event?)
  - Are route stops accessible via API or only in mobile app UI?
- **Integration Phase** (1.5 weeks): API client development, GPS freshness validation logic, error handling (driver offline, GPS unavailable)
- **Testing Phase** (3 days): Validate GPS accuracy, test stale GPS escalation trigger

**Rate Limits**: 
- Unknown (TBD with IT). Estimated agent usage: 140 cases/day × 3 API calls (location, status, route) = **420 calls/day**.
- **Risk**: Low — Volume is modest; caching can reduce (e.g., cache driver location for 5 min if multiple inquiries on same route).

**Gaps / Risks**:
- **API availability unknown** [A003]: If driver app backend does NOT expose API, requires:
  - Option 1: Build API wrapper (2-3 weeks additional effort)
  - Option 2: Direct database query (if permissions granted; requires DB schema discovery)
  - **Risk**: High — Critical blocker for pilot. Without GPS data, agent cannot calculate ETAs.
  - **Mitigation**: Prioritize IT discovery in Week 1 of build sprint. If API unavailable, this becomes Wave 1 build dependency.

- **GPS freshness inconsistency**: Driver app GPS may update on event (delivery scanned) rather than continuous (30 sec intervals). If GPS only updates on delivery events, time between stops could be 15-30 min (appears "stale" but driver is active).
  - **Risk**: Medium — Agent may escalate unnecessarily if GPS appears stale but driver is between stops.
  - **Mitigation**: Tune "stale" threshold based on pilot data (e.g., 45 min instead of 30 min [A045]), or add delivery event timestamp validation (if last event <10 min ago, GPS is implicitly fresh).

**Data Quality** (see Data Quality Assessment section): Medium (GPS accuracy depends on driver phone signal; route plans assumed accurate but need validation)

---

### 3. Dispatch Console (Java Desktop, Citrix)

**Purpose**: Route planning and driver assignment system. Agent uses for **read-only context** (route plans, historical route assignment) but does NOT write (no route modifications).

**System Details**:
- **Platform**: Java desktop application deployed via Citrix
- **Version**: Legacy (exact version TBD)
- **Deployment**: On-premise (Citrix app streaming)
- **Authentication**: LDAP or Active Directory (TBD)
- **API**: **Limited API surface** [Ref: A004] — Read-only API assumed for route plan retrieval; write operations require manual UI interaction.

**Data Needed**:
| Data Entity | Fields Required | Usage | Availability |
|-------------|-----------------|-------|--------------|
| **Route Plans** | `route_id`, `assigned_driver_id`, `stops` (sequence), `planned_start_time`, `planned_completion_time` | Route sequence for ETA calculation (supplement to driver app route data) | ⚠️ **Assumed limited availability** [A004] — May require API wrapper or DB query. |

**Access Type**: **Read-Only** (no writes required for DE-3)
- **Read**: `GET /routes/{id}` or direct DB query (TBD)
- **Write**: ❌ Not required for ETA Investigation Agent

**Availability**: ⚠️ **Constrained** [Ref: A004] — "Limited API surface" suggests read access may be via:
- Option 1: REST API wrapper (if IT team built this for integrations)
- Option 2: Direct database query (if permissions granted)
- Option 3: No API → agent cannot access dispatch console data (fallback: rely on driver app route data only)

**Integration Effort**: **Low (1 week)** — Read-only route plan retrieval
- Assumes API or DB query access available. If not, effort increases to Medium (2 weeks for API wrapper).

**Rate Limits**: Unknown (TBD). Low volume: 140 cases/day × 1 route query = **140 calls/day**.

**Gaps / Risks**:
- **Limited API availability** [A004]: If no API exists, fallback options:
  - Option 1: Driver app provides route plans (preferred, reduces dispatch console dependency)
  - Option 2: Agent operates without route plan context (uses GPS + historical timing only for ETA)
  - **Risk**: Low — Route plan enhances ETA accuracy but is not critical. GPS + historical timing sufficient for 90%+ accuracy [A042].
  - **Mitigation**: Discovery phase validates if dispatch console API needed. If unavailable, proceed with driver app route data.

**Data Quality**: Assumed high (dispatch console is operational system for route planning).

---

### 4. Historical Timing Database

**Purpose**: Stores aggregated route timing patterns (avg stop duration, traffic patterns, day-of-week effects) for ETA calculation engine. This is a **new build** (not an existing Apex system).

**System Details**:
- **Platform**: PostgreSQL database (new build)
- **Deployment**: Cloud (AWS RDS or Azure PostgreSQL)
- **Schema**: Custom design (see Data Sources section)
- **Data Source**: Nightly ETL from driver app delivery logs
- **Authentication**: Database credentials (managed via secrets manager)

**Data Needed**:
| Table | Fields | Usage | Availability |
|-------|--------|-------|--------------|
| **route_timings** | `route_id`, `time_bucket` (morning, afternoon, evening), `day_of_week`, `avg_stop_duration_min`, `stddev_stop_duration`, `sample_size`, `last_updated` | ETA calculation: remaining stops × avg stop duration = estimated time | ❌ **Build required** — ETL from driver app logs |
| **traffic_patterns** (optional Wave 1) | `route_segment` (lat/lon bounding box), `time_bucket`, `day_of_week`, `avg_delay_min`, `stddev_delay` | Traffic buffer for ETA calculation | ❌ **Build required** — ETL from driver app GPS logs or external traffic API |

**Access Type**: **Read-Only** (agent queries historical data; ETL writes)
- **Read**: `SELECT * FROM route_timings WHERE route_id = X AND time_bucket = 'afternoon'`
- **Write**: ❌ Agent does not write; nightly ETL updates historical data

**Availability**: ❌ **Build Required** — No existing historical timing system at Apex.

**Integration Effort**: **High (3 weeks)**
- Week 1: Schema design, ETL pipeline development (extract driver app delivery logs, aggregate timing patterns)
- Week 2: ETL testing, backfill historical data (6-12 months of logs for statistical validity [A054])
- Week 3: Database deployment, API layer for agent queries, caching strategy [A030]

**Rate Limits**: Database query performance (assumed <100ms per query with indexing). Volume: 140 cases/day × 1 query = **140 queries/day** (negligible load).

**Gaps / Risks**:
- **Historical data availability**: Requires driver app to log delivery events with timestamps. If logs incomplete or missing, historical timing patterns may be sparse.
  - **Risk**: Medium — Poor historical data → low ETA accuracy. Agent falls back to generic timing assumptions (15 min/stop default [A055]).
  - **Mitigation**: Validate driver app log completeness in discovery phase. If logs incomplete, use default timing assumptions for pilot, collect 3-6 months of clean data, then retrain ETA engine.

- **Cold start problem**: New routes with no historical data cannot use timing patterns.
  - **Risk**: Low — Affects <5% of cases (new routes are rare). Fallback: use avg timing from similar routes (same depot, similar stop count).
  - **Mitigation**: ETA engine includes fallback logic; confidence score reflects data sparsity.

**Data Quality** (see Data Quality Assessment section): Medium (depends on driver app log completeness and accuracy)

---

## Supporting Systems

### 5. Aurum Billing System (Read-Only Context)

**Purpose**: **Not directly integrated** in Wave 1 ETA Investigation Agent. Mentioned for completeness as legacy billing system described in scenario [Ref: A007]. Future agents (DE-2 Damaged Consignment, billing disputes) will require Aurum integration.

**System Details**:
- **Platform**: On-premise Oracle database (legacy, since 2008)
- **API**: ❌ **No real-time API** — Batch export only (daily 02:00-04:00 GMT to CSV [A007])
- **Export Lag**: T-1 for most data, T-2 for reconciliation [A007]

**Relevance to DE-3**: ❌ **Not required** — ETA Investigation Agent does not access billing data. SLA terms and customer priority retrieved from CRM, not Aurum.

**Future Wave Impact**: Aurum integration required for DE-2 (credit processing) and billing disputes work stream. 24-48h lag is a known constraint [A007].

---

### 6. Workforce Management System (Indirect)

**Purpose**: Driver availability, shift schedules, qualifications. **Not directly accessed** by ETA Investigation Agent. Relevant for future DA-3 (Driver Swap) but that agent is "Human Only" [not prioritized].

**Relevance to DE-3**: ❌ **Not required** — ETA Investigation Agent queries driver location (driver app), not driver schedules.

---

## Data Sources

### 7. Historical Timing Database (Details)

**Schema Design**:

```sql
CREATE TABLE route_timings (
    route_id VARCHAR(50) NOT NULL,
    time_bucket VARCHAR(20) NOT NULL,  -- 'morning' (06:00-12:00), 'afternoon' (12:00-18:00), 'evening' (18:00-22:00)
    day_of_week INT NOT NULL,          -- 1=Monday, 7=Sunday
    avg_stop_duration_min DECIMAL(5,2),
    stddev_stop_duration DECIMAL(5,2),
    sample_size INT,                    -- Number of historical deliveries in this bucket
    last_updated TIMESTAMP,
    PRIMARY KEY (route_id, time_bucket, day_of_week)
);

CREATE INDEX idx_route_lookup ON route_timings(route_id, time_bucket);
```

**ETL Process**:
1. **Extract**: Query driver app DB for delivery logs: `SELECT route_id, stop_sequence, arrival_time, departure_time, delivery_timestamp FROM delivery_events WHERE delivery_date BETWEEN X AND Y`
2. **Transform**: Aggregate by route, time bucket, day of week: `AVG(departure_time - arrival_time) AS avg_stop_duration`
3. **Load**: Upsert into `route_timings` table (nightly job, incremental updates)

**Caching Strategy** [A030]:
- Route timing patterns cached in agent prompt for 24 hours → reused across 140 inquiries/day
- Cache key: `route_id:time_bucket:day_of_week`
- Estimated cache hit rate: 80% (same routes queried multiple times per day)
- Token savings: 400 tokens per cached retrieval × 112 cache hits/day = 44,800 tokens/day saved = **£1.01/day** = **£369/year**

**Data Refresh Frequency**: Nightly (route patterns stable intraday; updates at 02:00 GMT after driver app batch close)

---

### 8. Customer SLA Terms (CRM)

**Data Source**: Salesforce CRM (`Order.Committed_Delivery_Window_Start__c`, `Order.Committed_Delivery_Window_End__c`)

**Usage**: SLA breach detection (if current time > window end → flag/escalate)

**Availability**: ⚠️ **May require custom fields** [A056] — Standard Salesforce Order object may not have delivery window fields. If missing:
- Option 1: Create custom fields (data migration from dispatch console or contracts)
- Option 2: Use default SLA windows by customer tier (high-priority = 2-hour window, standard = 4-hour window)

**Data Quality**: Medium (SLA terms may be in contracts, not digitized in CRM)

---

### 9. Customer Priority Tiers (CRM)

**Data Source**: Salesforce CRM (`Account.Customer_Priority_Tier__c` or proxy field `Account.AnnualRevenue`)

**Usage**: Escalation prioritization (high-priority customers get supervisor escalation for SLA breaches [A009])

**Availability**: ❌ **Likely missing** [A009] — Customer priority is currently tacit knowledge (e.g., "Hayes & Sons always gets Sandra"). Formalization required in Wave 2 prep.

**Fallback for Wave 1**: Use annual revenue proxy (>£500K = high-priority) or hard-code known high-value accounts (Hayes & Sons, Northstar Foods, etc.) [A057].

**Data Quality**: Low (priority system not formalized; manual data entry needed)

---

## External Services

### 10. SMS Gateway (Twilio or Similar)

**Purpose**: Send ETA notifications to customers via SMS

**System Details**:
- **Provider**: Twilio (recommended) or equivalent (Plivo, MessageBird)
- **API**: REST API
- **Authentication**: API key (managed via secrets manager)
- **Base URL**: `https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages`

**Data Needed**:
- Customer phone number (from CRM)
- Message text (drafted by agent)

**Access Type**: **Write-Only** (send SMS, no read required)
- **Write**: `POST /Messages` (send SMS)

**Availability**: ✅ **Available** — Twilio REST API is production-ready

**Integration Effort**: **Low (1 week)** — Twilio SDK integration, phone number validation, error handling (invalid number, SMS delivery failure)

**Cost**:
- Twilio SMS pricing: £0.04 per SMS (UK) [Ref: A058]
- Volume: 140 cases/day × 1 SMS per case = **140 SMS/day** = **£5.60/day** = **£2,044/year**
- Included in agent cost model (£0.05 per case API cost [Ref: TCO calculation])

**Rate Limits**: Twilio default: 200 SMS/second (far exceeds agent needs)

**Gaps / Risks**:
- **Customer phone number missing**: If CRM does not have SMS contact for customer, agent cannot send SMS → falls back to email or escalates to human for phone call.
  - **Risk**: Medium — Affects ~20% of customers (phone number not on file [A059]).
  - **Mitigation**: Agent detects missing phone number → asks customer "To send you ETA updates, please reply with your phone number."

**Data Quality**: Medium (phone numbers in CRM may be outdated or incorrect; validation needed)

---

### 11. Email Service (SendGrid or Similar)

**Purpose**: Send ETA notifications to customers via email

**System Details**:
- **Provider**: SendGrid (recommended) or equivalent (Mailgun, Amazon SES)
- **API**: REST API
- **Authentication**: API key
- **Base URL**: `https://api.sendgrid.com/v3/mail/send`

**Data Needed**:
- Customer email address (from CRM)
- Message HTML (drafted by agent with template)

**Access Type**: **Write-Only** (send email, no read required)
- **Write**: `POST /mail/send`

**Availability**: ✅ **Available** — SendGrid REST API is production-ready

**Integration Effort**: **Low (1 week)** — SendGrid SDK integration, email template design, error handling (bounce, spam filter)

**Cost**:
- SendGrid pricing: £0.001 per email (first 100K emails free [A060])
- Volume: 140 cases/day × 1 email per case = **140 emails/day** = **32,200 emails/year** = **£32/year** (negligible)

**Rate Limits**: SendGrid default: 10,000 emails/second (far exceeds agent needs)

**Gaps / Risks**:
- **Email bounce rate**: Customer email addresses may be outdated or incorrect.
  - **Risk**: Low — Affects ~10% of customers (email invalid [A061]). Agent logs bounce, escalates to human for phone follow-up.

**Data Quality**: Medium-High (email addresses generally more reliable than phone numbers in CRM)

---

### 12. Traffic API (Optional Wave 1, Planned Wave 2)

**Purpose**: Real-time traffic conditions for ETA calculation refinement

**System Details**:
- **Provider**: Google Maps Traffic API (recommended) or HERE Traffic API
- **API**: REST API
- **Authentication**: API key
- **Base URL**: `https://maps.googleapis.com/maps/api/distancematrix/json?departure_time=now&traffic_model=best_guess`

**Data Needed**:
- Driver GPS location (current)
- Customer delivery address
- Current timestamp

**Access Type**: **Read-Only** (query traffic conditions)
- **Read**: `GET /distancematrix` (returns travel time with traffic)

**Availability**: ✅ **Available** — Google Maps Traffic API is production-ready

**Integration Effort**: **Low (1 week)** — Google Maps SDK integration, traffic delay calculation, fallback logic (if API unavailable)

**Cost**:
- Google Maps Traffic API pricing: £0.005 per request [Ref: A062]
- Volume: 140 cases/day × 1 request per case = **140 requests/day** = **£0.70/day** = **£256/year**

**Inclusion Decision**: **Optional Wave 1** (ETA calculation works without traffic API using historical timing patterns). Include if:
- Historical timing data is sparse (cold start, new routes)
- ETA accuracy target >95% requires traffic adjustments
- Budget allows (£256/year is marginal cost)

**Mitigation**: Pilot without traffic API initially. Measure ETA accuracy with historical timing only. Add traffic API in Month 2-3 if accuracy falls below 90%.

---

## Infrastructure Requirements

### 13. Agent Monitoring & Logging Platform

**Purpose**: Token usage tracking, API call logging, escalation dashboard, audit trail

**System Details**:
- **Platform**: Custom build (Python/Node.js backend, PostgreSQL DB, web dashboard)
- **Deployment**: Cloud (AWS/Azure)
- **Authentication**: SSO (Apex corporate login)

**Components**:
| Component | Function | Build Effort |
|-----------|----------|--------------|
| **Token Usage Tracker** | Log input/output tokens per inquiry, calculate cost per case | 3 days |
| **API Call Logger** | Log all API calls (endpoint, latency, error rate) | 2 days |
| **Escalation Dashboard** | Display pending HITL cases, escalation reasons, queue assignment | 1 week |
| **Audit Trail Logger** | Log agent decisions, data sources, reasoning, confidence scores | 3 days |
| **Performance Dashboard** | KPIs: coverage, accuracy, HITL rate, cost per case | 3 days |

**Build Effort**: **Medium (2 weeks)** — Custom build required (no off-the-shelf agent monitoring platform at Apex)

**Reusability**: ✅ **High** — Monitoring platform shared across all Wave 2-3 agents (platform-level asset [Ref: A028])

**Gaps / Risks**:
- **No existing monitoring infrastructure**: Apex must build from scratch.
  - **Risk**: Low — Standard web app build, no technical blockers.
  - **Mitigation**: Build iteratively (MVP in Week 1, expand features in Weeks 2-4 based on pilot feedback).

---

### 14. Agent Runtime Infrastructure

**Purpose**: Claude API access, compute for agent execution, secrets management

**System Details**:
- **Model Provider**: Anthropic Claude API (Claude Sonnet 4.5)
- **Model ID**: `claude-sonnet-4-5-20250929`
- **Deployment**: Cloud (agent backend hosted on AWS/Azure, calls Claude API)
- **Authentication**: Anthropic API key (secrets manager)
- **Cost**: £0.015 per 1K input tokens, £0.075 per 1K output tokens [Ref: TCO calculation]

**Infrastructure Stack**:
- **Agent Backend**: Python (FastAPI) or Node.js (Express), hosted on AWS Lambda or Azure Functions (serverless)
- **Secrets Management**: AWS Secrets Manager or Azure Key Vault (API keys, DB credentials)
- **Queue (for async processing)**: AWS SQS or Azure Service Bus (if async inquiry processing needed)

**Build Effort**: **Low (1 week)** — Standard cloud infrastructure setup

**Gaps / Risks**:
- **Claude API rate limits**: Anthropic tier limits (TBD based on Apex account tier). Estimated usage: 140 cases/day × 2,860 tokens input × 365 days = **146M tokens/year input**.
  - **Risk**: Low — Volume is modest; Anthropic standard tier supports billions of tokens/month.
  - **Mitigation**: Confirm Apex account tier with Anthropic; upgrade if needed.

---

## Integration Gaps and Risks

### Critical Path Blockers (Must Resolve Before Pilot)

1. **Driver App API Availability** [A003]
   - **Gap**: API access not confirmed. If driver app backend does NOT expose API, agent cannot retrieve GPS/delivery status.
   - **Risk**: **HIGH** — Blocks ETA calculation (core agent function)
   - **Mitigation**: 
     - Week 1: IT discovery to confirm API availability
     - If API unavailable: Build API wrapper (add 2-3 weeks) or direct DB query
     - **Decision point Week 1**: Go/No-Go on pilot if API blocked

2. **Historical Timing Data Availability** [A054]
   - **Gap**: Driver app delivery logs may be incomplete or missing timestamps.
   - **Risk**: **MEDIUM** — Poor historical data → low ETA accuracy → high escalation rate
   - **Mitigation**: 
     - Discovery phase: Validate driver app log completeness (sample 1 month of logs)
     - If logs incomplete: Use default timing assumptions (15 min/stop [A055]) for pilot, collect 3-6 months of clean data post-pilot

### Medium Priority Gaps (Address in Build Phase)

3. **Customer Priority Tier Field** [A009]
   - **Gap**: CRM may not have formalized customer priority tier field.
   - **Risk**: **MEDIUM** — Affects SLA breach escalation prioritization
   - **Mitigation**: 
     - Wave 1 pilot: Use annual revenue proxy (>£500K = high-priority) or hard-code known accounts [A057]
     - Wave 2 prep: Formalize priority system (data migration, CRM field creation)

4. **SLA Committed Window Fields** [A056]
   - **Gap**: CRM Order object may not have delivery window start/end fields.
   - **Risk**: **MEDIUM** — Affects SLA breach detection
   - **Mitigation**: 
     - Option 1: Create custom fields in CRM (data migration from dispatch console)
     - Option 2: Use default windows by customer tier (high-priority = 2-hour, standard = 4-hour)

5. **Customer Contact Data Completeness** [A059, A061]
   - **Gap**: ~20% of customers missing phone number, ~10% missing/invalid email.
   - **Risk**: **LOW** — Agent cannot send notification → escalates to human for phone call
   - **Mitigation**: 
     - Agent detects missing contact → requests from customer or escalates
     - Track contact completeness in pilot; launch CRM data cleanup initiative post-pilot

### Low Priority Gaps (Nice-to-Have, Not Blocking)

6. **Traffic API Integration** [A062]
   - **Gap**: Not included in Wave 1 pilot (optional).
   - **Risk**: **LOW** — ETA accuracy may be 90-93% without traffic vs. 95% target [A042]
   - **Mitigation**: Pilot without traffic API; add in Month 2-3 if accuracy below target

---

## Data Quality Assessment

| Data Source | Quality Rating | Issues | Mitigation |
|-------------|----------------|--------|------------|
| **Salesforce CRM Orders** | High | Address standardization may vary (typos, abbreviations) | Address validation API (Google Places) for normalization |
| **Salesforce CRM Contacts** | Medium-High | ~20% missing phone, ~10% invalid email [A059, A061] | Agent requests contact from customer; CRM cleanup initiative |
| **Driver App GPS** | Medium | GPS accuracy depends on phone signal; rural areas may have poor coverage | GPS freshness validation; escalate if stale [A045] |
| **Driver App Delivery Status** | High | Delivery events logged consistently (assumption; validate in discovery) | Status validation against GPS timestamp (if status="delivered", GPS should be at delivery location) |
| **Dispatch Console Route Plans** | High | Route plans operational data, assumed accurate | Validate route sequence matches driver app route (cross-check) |
| **Historical Timing DB** | Medium | Quality depends on driver app log completeness [A054] | ETL data validation; flag routes with <20 historical samples as "low confidence" |
| **Customer SLA Terms** | Low-Medium | SLA windows may be in contracts, not digitized in CRM [A056] | Use default windows by tier; formalize in Wave 2 prep |
| **Customer Priority Tiers** | Low | Priority system not formalized [A009] | Use revenue proxy or hard-code known accounts; formalize in Wave 2 prep |

**Overall Data Quality**: **Medium** — Core operational data (orders, GPS, delivery status) is medium-high quality. Enrichment data (SLA terms, customer priority) is low and requires formalization in Wave 2 prep.

---

## Security and Compliance

### Authentication & Authorization

| System | Auth Method | Agent Permissions | Audit Requirements |
|--------|-------------|-------------------|-------------------|
| **Salesforce CRM** | OAuth 2.0 | Read: Orders, Contacts. Write: Cases, Order Notes | All API calls logged in Salesforce audit trail (90-day retention) |
| **Driver App** | API key (assumed) | Read-only: GPS, delivery status, routes | API call logging in agent monitoring platform |
| **Historical Timing DB** | DB credentials | Read-only: Route timing patterns | Query logging in DB (30-day retention) |
| **SMS Gateway** | API key | Write: Send SMS | Message delivery logs in Twilio (12-month retention) |
| **Email Service** | API key | Write: Send email | Delivery logs in SendGrid (12-month retention) |

**Secrets Management**: All API keys and DB credentials stored in AWS Secrets Manager or Azure Key Vault (encrypted at rest, audited access).

### Data Privacy (GDPR Compliance)

**Personal Data Processed**:
- Customer name, email, phone number (from CRM)
- Delivery address (from CRM orders)
- Inquiry history (from CRM cases)

**GDPR Compliance Measures**:
1. **Lawful Basis**: Legitimate interest (providing delivery services to customer)
2. **Data Minimization**: Agent only retrieves data required for ETA calculation (no unnecessary PII)
3. **Retention**: Agent does not store customer data (queries on demand); audit logs retain inquiry details for 90 days (Salesforce standard), then purged
4. **Customer Rights**: Customers can request ETA inquiry history via Apex customer service (Salesforce case records); data deleted upon request (GDPR Article 17 right to erasure)

**No Special Category Data**: Agent does not process health, biometric, or sensitive personal data.

**Risk**: **LOW** — Standard delivery service data processing, no high-risk GDPR scenarios.

### Compliance with UK AI Regulations

**EU AI Act / UK AI Regulation (Emerging)**:
- **Risk Level**: LOW (ETA calculation is low-risk use case; not high-risk per EU AI Act Annex III)
- **Transparency**: Agent identifies itself as AI ("automated ETA system"), provides escalation to human agent on request
- **Auditability**: All agent decisions logged with reasoning, data sources, confidence scores (audit trail in CRM)
- **Human Oversight**: HITL supervision required for escalations (stale GPS, SLA breach, lost consignment)

**No Prohibited Use Cases**: Agent does not perform biometric identification, social scoring, or manipulative AI.

**Risk**: **LOW** — Agent design complies with emerging UK AI regulations.

---

## Document Control

- **Created**: 2026-05-06
- **Version**: 1.0
- **Agent**: ETA Investigation Agent (DE-3)
- **Owner**: AI FDE Team
- **Related Documents**:
  - `4-agent-purpose-document.md` - Agent purpose, activity catalog, autonomy matrix
  - `assumptions.md` - All assumptions referenced with [Ref: A###]
- **Next Steps**: 
  - IT discovery to validate driver app API availability, historical timing data completeness
  - Build sprint planning (12-14 weeks integration effort)
  - Schema design for historical timing DB and agent monitoring platform
