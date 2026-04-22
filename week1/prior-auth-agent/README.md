# Prior-Authorization Check Agent

Automated prior-authorization verification system for medical practices, built per **Claude.md** specification.

## Overview

This agent automates the prior-authorization check process, reducing front-desk staff time from 2.5 minutes to 0.5 minutes per patient while improving accuracy from 97% to 99.25% [per Claude.md assumptions A3, A8, A2, A9].

### Features

- **5-Step Decision Logic**: Implements complete prior-auth verification workflow (Claude.md Section 3)
- **State Machine**: Enforces valid transitions per specification (Claude.md Section 2)
- **Human-in-Loop**: AI recommends, humans decide
- **Confidence Scoring**: HIGH/MEDIUM/LOW with detailed rationale
- **Mock Adapters**: External system mocks for development
- **Fuzzy Matching**: Levenshtein distance algorithm [per Claude.md A40]
- **Complete Audit Trail**: All decisions and state changes logged

## Architecture

```
prior-auth-agent/
├── app/
│   ├── models/          # SQLAlchemy ORM models
│   │   ├── prior_auth_check.py    # PriorAuthCheck with state machine
│   │   ├── prior_auth_record.py   # PriorAuthRecord entity
│   │   └── appointment.py         # Appointment entity
│   ├── routes/          # FastAPI endpoints
│   │   └── prior_auth_check.py    # API routes
│   ├── services/        # Business logic
│   │   ├── decision_engine.py     # 5-step decision process
│   │   └── fuzzy_matcher.py       # String matching algorithm
│   ├── adapters/        # External system mocks
│   │   ├── athenahealth.py        # EHR adapter
│   │   ├── prior_auth_db.py       # Prior-auth database adapter
│   │   └── insurance_requirements.py  # Insurance rules adapter
│   ├── schemas/         # Pydantic schemas
│   ├── database.py      # Database configuration
│   └── main.py          # FastAPI application
├── tests/               # Test suite
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- pip or conda

### Installation

1. **Clone and navigate to project**:
   ```bash
   cd prior-auth-agent
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Create database**:
   ```bash
   createdb prior_auth_db
   ```

6. **Run application**:
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Access API documentation**:
   - Open browser to http://localhost:8000/docs
   - Interactive Swagger UI with all endpoints

## Usage Examples

### 1. Create Prior-Auth Check

```bash
curl -X POST "http://localhost:8000/api/v1/prior-auth-checks/" \
  -H "Content-Type: application/json" \
  -d '{"appointment_id": "APT-2024-001"}'
```

**Response**:
```json
{
  "check_id": "PAC-1713792000-PAT-12345-APT-2024-001",
  "status": "AWAITING_HUMAN_REVIEW",
  "prior_auth_status": "VALID",
  "ai_recommendation": "PROCEED",
  "confidence_score": "HIGH",
  "confidence_rationale": "Prior-auth valid until 2024-06-15, 45 days after appointment",
  ...
}
```

### 2. Get Check Status

```bash
curl "http://localhost:8000/api/v1/prior-auth-checks/PAC-1713792000-PAT-12345-APT-2024-001"
```

### 3. Record Human Decision

```bash
curl -X POST "http://localhost:8000/api/v1/prior-auth-checks/PAC-1713792000-PAT-12345-APT-2024-001/human-decision" \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "APPROVED",
    "decision_by": "staff-001",
    "notes": "Prior-auth verified, patient can proceed"
  }'
```

### 4. List All Checks

```bash
curl "http://localhost:8000/api/v1/prior-auth-checks/?limit=10"
```

### 5. Get Check by Appointment

```bash
curl "http://localhost:8000/api/v1/prior-auth-checks/appointments/APT-2024-001/check"
```

## Test Scenarios

The mock adapters provide three test scenarios:

### Scenario 1: Valid Prior-Auth (HIGH Confidence)
- **Appointment**: APT-2024-001
- **Patient**: PAT-12345
- **Procedure**: MRI Brain with Contrast (CPT 70553)
- **Expected Result**: PROCEED with HIGH confidence
- **Reason**: Prior-auth valid, expires 45 days after appointment

### Scenario 2: Expiring Soon (MEDIUM Confidence)
- **Appointment**: APT-2024-002
- **Patient**: PAT-67890
- **Procedure**: MRI Lumbar Spine (CPT 72148)
- **Expected Result**: ESCALATE with MEDIUM confidence
- **Reason**: Prior-auth expires in 2 days (within 7-day warning threshold)

### Scenario 3: Missing Prior-Auth (HIGH Confidence)
- **Appointment**: APT-2024-003
- **Patient**: PAT-99999
- **Procedure**: Office Visit (CPT 99214)
- **Expected Result**: COMPLETED (no prior-auth required)
- **Reason**: Office visits don't require prior-authorization

## API Endpoints

### POST /api/v1/prior-auth-checks/
Create new prior-auth check for an appointment. Triggers 5-step analysis.

### GET /api/v1/prior-auth-checks/{check_id}
Get check status and recommendation by check ID.

### GET /api/v1/prior-auth-checks/
List checks with optional filters (status, patient_id).

### POST /api/v1/prior-auth-checks/{check_id}/human-decision
Record human decision (APPROVED | RESCHEDULED | ESCALATED | OVERRIDDEN).

### GET /api/v1/prior-auth-checks/appointments/{appointment_id}/check
Get check for specific appointment.

### GET /health
Health check endpoint.

## Decision Logic (5 Steps)

Per **Claude.md Section 3**, the agent executes:

1. **Determine Requirement**: Check if procedure needs prior-auth [insurance rules]
2. **Locate Documentation**: Query prior-auth database [patient + policy + date]
3. **Validate Match**: Match CPT codes (exact or fuzzy) [Levenshtein distance]
4. **Check Expiration**: Calculate days until expiration [7-day warning threshold]
5. **Generate Recommendation**: Synthesize PROCEED | RESCHEDULE | ESCALATE

## State Machine

Per **Claude.md Section 2**, valid transitions:

```
PENDING_CHECK → CHECKING
CHECKING → AWAITING_HUMAN_REVIEW | ESCALATED | FAILED
AWAITING_HUMAN_REVIEW → APPROVED | RESCHEDULED | ESCALATED
ESCALATED → AWAITING_HUMAN_REVIEW | COMPLETED
APPROVED → COMPLETED
RESCHEDULED → COMPLETED
FAILED → COMPLETED
```

Terminal states: **COMPLETED**, **FAILED**

## Confidence Scoring

- **HIGH**: Exact CPT match, valid expiration (>7 days), complete data
- **MEDIUM**: Fuzzy match OR expiring soon (≤7 days)
- **LOW**: Missing data, ambiguous match, multiple conflicts

## Mock Adapters

External systems use mock data for development:

- **AthenaHealthAdapter**: Mock EHR API (OAuth 2.0 in production)
- **PriorAuthDBAdapter**: Mock prior-auth database (PostgreSQL/API in production)
- **InsuranceRequirementsAdapter**: Hardcoded rules [per Claude.md A38a]

## Configuration

Environment variables (`.env`):

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/prior_auth_db
EXPIRATION_WARNING_DAYS=7          # Per Claude.md A44
TRIGGER_WINDOW_HOURS=48           # Per Claude.md A11
FUZZY_MATCH_THRESHOLD=0.8         # Per Claude.md A40
```

## Development

### Run Tests
```bash
pytest tests/
```

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head
```

### Code Style
```bash
black app/
flake8 app/
mypy app/
```

## Production Deployment

1. Replace mock adapters with real API clients
2. Configure OAuth 2.0 for athenahealth
3. Set up HIPAA-compliant infrastructure [Claude.md A22]
4. Enable audit logging to separate database [Claude.md A23]
5. Configure 7-year retention [Claude.md A16]

## Specification Reference

This implementation follows:
- **Claude.md**: Main specification (Sections 1-5, 11)
- **specs/api-specifications.md**: API contracts and algorithms
- **specs/requirements.md**: Functional/non-functional requirements
- **specs/integration-guide.md**: Integration points
- **Assumptions A1-A52**: Design decisions and constraints

## Performance Targets

Per **Claude.md**:
- Response time: <10 seconds end-to-end
- Throughput: 90 checks/day (scalable)
- Accuracy: ≥95% for HIGH confidence
- Escalation rate: <20%
- Availability: 99% uptime

## Support

For questions about the specification, refer to:
- Claude.md (main spec)
- delegation-analysis.md (delegation strategy)
- problem-statement.md (success metrics)

## License

Internal use only. Refer to project documentation for terms.
