# AI Claims Processing Workflow Demo

**Dual-path claims processing transformation** for Greenfield Health Systems.

This demo showcases **ADR-1 (Claim Intake)** and **ADR-4 (Clinical Triage)** agents working together to automate claims processing.

🔗 **Live Demo**: [Coming soon after deployment]

---

## 🎯 What This Demo Shows

1. **ADR-1 Intake Agent** - Validates and normalizes claims from multiple formats (EDI, PDF, JSON, email)
2. **ADR-4 Triage Agent** - Routes claims to Fast Path (routine) or Clinical Path (physician review)
3. **Interactive Workflow UI** - Process claims, handle exceptions, and see AI reasoning in real-time

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Mock Claims    │  (EDI, PDF, JSON, email formats)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ADR-1 API     │  Validates & normalizes claims
│  (port 8000)    │  Routes incomplete claims to human review
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ADR-4 API     │  Clinical content triage
│  (port 8001)    │  Codebook-driven classification
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Workflow UI                     │
│  • Fast Path Queue (routine)     │
│  • Clinical Path Queue (review)  │
│  • Human Review Queue (HITL)     │
└──────────────────────────────────┘
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- Node.js 18+
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### 1. Clone & Install

```bash
git clone git@github.com:rendonalex/fde.git
cd fde/capstone

# Install ADR-1 dependencies
cd adr1-intake-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Install ADR-4 dependencies
cd adr4-triage-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Install Workflow UI dependencies
cd workflow-ui/backend
npm install
cd ../frontend
npm install
cd ../..
```

### 2. Set API Key

```bash
# ADR-1
echo "ANTHROPIC_API_KEY=your_key_here" > adr1-intake-agent/.env

# ADR-4
echo "ANTHROPIC_API_KEY=your_key_here" > adr4-triage-agent/.env
```

### 3. Start All Services

**Terminal 1 - ADR-1:**
```bash
cd adr1-intake-agent
source venv/bin/activate
python3 -m uvicorn src.api.app:app --reload --port 8000
```

**Terminal 2 - ADR-4:**
```bash
cd adr4-triage-agent
source venv/bin/activate
python3 -m uvicorn app.main:app --reload --port 8001
```

**Terminal 3 - Workflow Backend:**
```bash
cd workflow-ui/backend
node server.js
```

**Terminal 4 - Workflow Frontend:**
```bash
cd workflow-ui/frontend
npm run dev
```

### 4. Open Browser

Visit: http://localhost:5173

---

## 📖 Demo Scenarios

### Scenario 1: Routine Claim (Fast Path)
1. Select `test-claims/t-CLM-2026-1000001.edi` (EDI claim)
2. Click "Process Selected Claims"
3. ✅ Claim auto-validates → routes to **Fast Path** (routine processing)
4. View reasoning: Why it's routine (no clinical indicators)

### Scenario 2: Clinical Claim (Physician Review)
1. Select `test-claims/t-CLM-2026-9003.json` (chemotherapy)
2. Click "Process Selected Claims"
3. ✅ ADR-4 detects clinical complexity → routes to **Clinical Path**
4. View reasoning: CPT 96413 (chemotherapy) triggers clinical review

### Scenario 3: Human Review (HITL)
1. Select `cms1500-ocr/CLM-2026-1001601.txt` (poor OCR quality)
2. Click "Process Selected Claims"
3. ⚠️ Low confidence fields → routes to **Human Review Queue**
4. Click "Edit" → fix missing fields → "Ready for Triage"
5. ✅ Re-validates → triages to correct queue

---

## 🎓 Key Features

### ADR-1 Capabilities
- ✅ Multi-format ingestion (EDI 837P/I, CMS-1500 PDF, FHIR R4, JSON, email)
- ✅ Per-field confidence scoring
- ✅ Automatic routing to HITL when confidence < 0.85
- ✅ Prior authorization normalization

### ADR-4 Capabilities
- ✅ Codebook-driven clinical classification
- ✅ Chain-of-thought reasoning (viewable in UI)
- ✅ Shadow mode ready (logs decisions without affecting routing)
- ✅ Confidence fallback (<0.70 → routes to Clinical Path for safety)

### Workflow UI
- ✅ Drag-and-drop claim processing
- ✅ Real-time status updates
- ✅ Human review workflow with re-validation
- ✅ Reasoning transparency (see why each decision was made)

---

## 🌐 Deployment (Render.com)

This project is configured for one-click deployment to Render.com.

### Deploy Steps:
1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → "New Blueprint"
3. Connect your GitHub repo
4. Render reads `render.yaml` and deploys all 4 services automatically
5. Add your `ANTHROPIC_API_KEY` in Render dashboard (Environment tab)
6. Services deploy in ~5-10 minutes

**Note:** Free tier services sleep after 15 min inactivity. First request takes ~30-60 sec to wake up.

---

## 📊 Project Structure

```
capstone/
├── adr1-intake-agent/       # ADR-1 API (FastAPI)
│   ├── src/
│   │   ├── api/             # FastAPI routes
│   │   ├── models/          # Pydantic models
│   │   ├── services/        # Agent logic
│   │   └── prompts/         # System prompts
│   └── tests/
├── adr4-triage-agent/       # ADR-4 API (FastAPI)
│   ├── app/
│   │   ├── agent.py         # Classification agent
│   │   ├── models.py        # Data models
│   │   └── main.py          # FastAPI app
│   ├── config/
│   │   └── criteria-codebook.json
│   └── tests/
├── workflow-ui/
│   ├── backend/             # Express.js API
│   │   └── server.js
│   └── frontend/            # React + Vite
│       └── src/
│           └── App.jsx
├── mock-data/               # Test claims (EDI, PDF, JSON, email)
├── demo/                    # IDP preprocessors
├── specs/                   # Detailed specifications
└── render.yaml              # Deployment config
```

---

## 🧪 Testing

### ADR-1 Tests
```bash
cd adr1-intake-agent
source venv/bin/activate
pytest tests/ -v
```

### ADR-4 Tests
```bash
cd adr4-triage-agent
source venv/bin/activate
pytest tests/ -v
```

---

## 📚 Documentation

- **Problem Framing**: `specs/01-problem-framing.md`
- **ADR-1 Spec**: `specs/06a-capability-spec-intake.md`
- **ADR-4 Spec**: `specs/06b-capability-spec-triage.md`
- **Token Economics**: `specs/08-economics.md`

---

## 🔑 Environment Variables

### Required
- `ANTHROPIC_API_KEY` - Claude API key

### Optional (auto-configured in deployment)
- `ADR1_URL` - ADR-1 API endpoint (default: http://localhost:8000)
- `ADR4_URL` - ADR-4 API endpoint (default: http://localhost:8001)
- `PORT` - Service port (Render assigns dynamically)

---

## ⚠️ Known Limitations

- **Free tier sleep**: Services on Render free tier sleep after 15 min inactivity
- **Shadow mode only**: ADR-4 is in shadow mode (doesn't write routing decisions to production CMS)
- **Mock data**: Uses synthetic claims for demo purposes

---

## 👥 Contact

**Alexandra Rendon** - FDE Capstone Project  
GitHub: [@rendonalex](https://github.com/rendonalex)

---

## 📄 License

This is an educational project created for the FDE program.
