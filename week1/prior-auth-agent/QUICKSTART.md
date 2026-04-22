# Quick Start Guide: Prior-Authorization Check Agent

Get the agent running in 5 minutes!

## Prerequisites

- Python 3.10+
- PostgreSQL 14+ (or use SQLite for quick testing)

## Option 1: Quick Start (SQLite)

For quick testing without PostgreSQL:

```bash
# Navigate to project
cd prior-auth-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Use SQLite instead of PostgreSQL
export DATABASE_URL="sqlite:///./test.db"

# Run the application
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs to see the API documentation.

## Option 2: Full Setup (PostgreSQL)

```bash
# 1. Create database
createdb prior_auth_db

# 2. Navigate to project
cd prior-auth-agent

# 3. Run setup script
./run.sh
```

The script will:
- Create virtual environment
- Install dependencies
- Create database tables
- Start the application

## Test the API

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Create Prior-Auth Check (Valid Scenario)

```bash
curl -X POST "http://localhost:8000/api/v1/prior-auth-checks/" \
  -H "Content-Type: application/json" \
  -d '{"appointment_id": "APT-2024-001"}'
```

**Expected Result**: `PROCEED` with `HIGH` confidence

### 3. Create Prior-Auth Check (Expiring Soon)

```bash
curl -X POST "http://localhost:8000/api/v1/prior-auth-checks/" \
  -H "Content-Type: application/json" \
  -d '{"appointment_id": "APT-2024-002"}'
```

**Expected Result**: `ESCALATE` with `MEDIUM` confidence (expires in 2 days)

### 4. Create Prior-Auth Check (No Prior-Auth Required)

```bash
curl -X POST "http://localhost:8000/api/v1/prior-auth-checks/" \
  -H "Content-Type: application/json" \
  -d '{"appointment_id": "APT-2024-003"}'
```

**Expected Result**: `COMPLETED` (office visit doesn't require prior-auth)

### 5. Record Human Decision

```bash
# Get the check_id from the previous response, then:
curl -X POST "http://localhost:8000/api/v1/prior-auth-checks/{check_id}/human-decision" \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "APPROVED",
    "decision_by": "staff-001",
    "notes": "Prior-auth verified, patient can proceed"
  }'
```

## Interactive API Documentation

Visit http://localhost:8000/docs for:
- Interactive API testing
- Request/response schemas
- Complete endpoint documentation
- Try-it-out functionality

## Test Scenarios

The system includes three mock scenarios for testing:

| Appointment ID | Patient | Procedure | Expected Outcome |
|----------------|---------|-----------|------------------|
| APT-2024-001 | PAT-12345 | MRI Brain (70553) | ✅ PROCEED (HIGH) - Valid 45 days |
| APT-2024-002 | PAT-67890 | MRI Spine (72148) | ⚠️ ESCALATE (MEDIUM) - Expires in 2 days |
| APT-2024-003 | PAT-99999 | Office Visit (99214) | ✅ COMPLETED - No prior-auth needed |

## Architecture Overview

```
Request → FastAPI → Decision Engine → 5 Steps → Response
                          ↓
                    Mock Adapters
                    ├─ EHR (athenahealth)
                    ├─ Prior-Auth Database
                    └─ Insurance Requirements
```

## 5-Step Process

Each check executes:

1. **Determine Requirement**: Does this procedure need prior-auth?
2. **Locate Documentation**: Query prior-auth database
3. **Validate Match**: Match CPT codes (exact or fuzzy)
4. **Check Expiration**: Calculate days until expiration
5. **Generate Recommendation**: PROCEED | RESCHEDULE | ESCALATE

## State Machine

```
PENDING → CHECKING → AWAITING_REVIEW → APPROVED → COMPLETED
                   ↘ ESCALATED ↗             ↘ RESCHEDULED ↗
                   ↘ FAILED → COMPLETED
```

## Configuration

Edit `.env` to customize:

```bash
# Business rules
EXPIRATION_WARNING_DAYS=7    # Days before expiration to warn
TRIGGER_WINDOW_HOURS=48     # When to trigger check (hours before appointment)
FUZZY_MATCH_THRESHOLD=0.8   # String similarity threshold (0.0-1.0)
```

## Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
pg_isready

# Create database if missing
createdb prior_auth_db

# Or use SQLite for testing
export DATABASE_URL="sqlite:///./test.db"
```

### Port 8000 Already in Use

```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

1. **Explore API**: Visit http://localhost:8000/docs
2. **Run Tests**: `pytest tests/`
3. **Review Code**: Start with `app/main.py` and `app/services/decision_engine.py`
4. **Read Spec**: See `Claude.md` for complete specification
5. **Customize**: Modify mock data in `app/adapters/` for your scenarios

## Key Files

- `app/main.py` - FastAPI application
- `app/services/decision_engine.py` - 5-step decision logic
- `app/models/prior_auth_check.py` - State machine
- `app/adapters/` - Mock external systems
- `Claude.md` - Complete specification

## Production Deployment

For production use:

1. Replace mock adapters with real API clients
2. Configure OAuth 2.0 authentication
3. Enable HIPAA-compliant infrastructure
4. Set up proper audit logging
5. Configure 7-year retention policy

See `README.md` for complete deployment guide.

## Support

- **Specification**: See `Claude.md`
- **API Docs**: http://localhost:8000/docs
- **Test Examples**: See `tests/` directory

---

**Happy Testing! 🚀**
