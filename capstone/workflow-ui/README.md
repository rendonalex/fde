# Claims Processing Workflow UI

Interactive UI for testing ADR-1 (Claim Intake) and ADR-4 (Clinical Triage) agents.

## Architecture

```
Frontend (React + Vite + Tailwind)  →  Backend (Express.js)  →  ADR-1 & ADR-4 APIs
   localhost:5173                        localhost:3001            :8000  :8001
```

## Prerequisites

1. **ADR-1 running** on `http://localhost:8000`
   ```bash
   cd ~/gh/fde/capstone/adr1-intake-agent
   python cli.py serve
   ```

2. **ADR-4 running** on `http://localhost:8001`
   ```bash
   cd ~/gh/fde/capstone/adr4-triage-agent
   uvicorn app.main:app --port 8001
   ```

3. **ANTHROPIC_API_KEY** set in environment for both agents

## Quick Start

### Terminal 1: Start Backend
```bash
cd ~/gh/fde/capstone/workflow-ui/backend
npm start
```

### Terminal 2: Start Frontend
```bash
cd ~/gh/fde/capstone/workflow-ui/frontend
npm run dev
```

Open browser to `http://localhost:5173`

## Workflow

### 1. Select Claims
- Search and multi-select claims from `~/gh/fde/capstone/mock-data/`
- Click "Add to Queue" to add selected claims to processing queue

### 2. Process Claims
- Click "Process Claim(s)" to send claims through ADR-1
- Claims are processed one by one:
  - **AUTO_COMPLETE** → automatically sent to ADR-4 for triage
  - **HUMAN_REQUIRED** → added to HITL queue

### 3. HITL (Human-in-the-Loop) Review
- Claims with low-confidence fields appear in "Human Review Required" section
- Click "Edit" to update low-confidence fields
- Select reviewed claims and click "Ready for Triage" to send to ADR-4

### 4. View Results
- **Physician Review (Clinical Path)**: Claims requiring physician review
- **Routine (Fast Path)**: Administrative claims for automatic adjudication
- Click "Expand" on any claim to see:
  - Reasoning trace from ADR-4
  - Full ADR-4 output JSON

## State Persistence

All queue state is saved to browser localStorage and survives page refresh.

To reset: Open browser console and run:
```javascript
localStorage.clear()
```

## Mock Data

Claims are loaded from `~/gh/fde/capstone/mock-data/` with support for:
- `portal-json/*.json` - Portal submissions
- `fhir-r4-json/*.json` - FHIR R4 claims
- `edi-837p/*.edi` - EDI 837P professional
- `edi-837i/*.edi` - EDI 837I institutional
- `cms1500-ocr/*.txt` - CMS-1500 OCR text
- And more...

## Troubleshooting

### Backend won't start
- Check ADR-1 and ADR-4 are running on ports 8000 and 8001
- Check Python3 is available (`which python3`)

### Claims don't load
- Check backend logs for errors
- Verify `~/gh/fde/capstone/mock-data/` exists

### Processing fails
- Check ANTHROPIC_API_KEY is set for both agents
- Check backend console for detailed error messages
- Check ADR-1 and ADR-4 logs

## API Endpoints

### Backend (port 3001)
- `GET /api/claims` - List all available claims
- `POST /api/process-claim` - Process claim through ADR-1
  ```json
  { "claimPath": "portal-json/CLM-2026-1001201.json" }
  ```
- `POST /api/triage-claim` - Triage claim through ADR-4
  ```json
  { "normalizedClaim": { ... } }
  ```

### ADR-1 (port 8000)
- `POST /api/v1/claims/submit` - Submit extraction result

### ADR-4 (port 8001)
- `POST /api/v1/classify` - Classify normalized claim record
