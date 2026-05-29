#!/bin/bash
# Start all 4 services for demo

echo "🚀 Starting AI Claims Processing Demo..."
echo ""

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ERROR: ANTHROPIC_API_KEY not set"
    echo "Run: export ANTHROPIC_API_KEY=your_key_here"
    exit 1
fi

# Start ADR-1 (port 8000)
echo "Starting ADR-1 Intake Agent (port 8000)..."
cd adr1-intake-agent
pip install -q -r requirements.txt
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 &
ADR1_PID=$!
cd ..

# Start ADR-4 (port 8001)
echo "Starting ADR-4 Triage Agent (port 8001)..."
cd adr4-triage-agent
pip install -q -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 &
ADR4_PID=$!
cd ..

# Start Backend (port 3001)
echo "Starting Workflow Backend (port 3001)..."
cd workflow-ui/backend
npm install --silent
node server.js &
BACKEND_PID=$!
cd ../..

# Start Frontend (port 5173)
echo "Starting Workflow Frontend (port 5173)..."
cd workflow-ui/frontend
npm install --silent
npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!
cd ../..

echo ""
echo "✅ All services starting..."
echo ""
echo "📍 Ports:"
echo "   - ADR-1:    http://localhost:8000"
echo "   - ADR-4:    http://localhost:8001"
echo "   - Backend:  http://localhost:3001"
echo "   - Frontend: http://localhost:5173 (THIS IS YOUR DEMO LINK)"
echo ""
echo "🌐 In Codespaces: Make port 5173 PUBLIC, then share that URL"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping services...'; kill $ADR1_PID $ADR4_PID $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
