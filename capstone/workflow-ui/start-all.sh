#!/bin/bash

echo "=========================================="
echo "Claims Workflow UI - Startup Script"
echo "=========================================="
echo ""

# Check if ADR-1 is running
echo "Checking ADR-1 (port 8000)..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✓ ADR-1 is running"
else
    echo "✗ ADR-1 is NOT running"
    echo "  Start it with: cd ~/gh/fde/capstone/adr1-intake-agent && python cli.py serve"
    exit 1
fi

# Check if ADR-4 is running
echo "Checking ADR-4 (port 8001)..."
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✓ ADR-4 is running"
else
    echo "✗ ADR-4 is NOT running"
    echo "  Start it with: cd ~/gh/fde/capstone/adr4-triage-agent && uvicorn app.main:app --port 8001"
    exit 1
fi

echo ""
echo "All agents are running!"
echo ""
echo "Starting backend and frontend..."
echo ""

# Start backend in background
cd "$(dirname "$0")/backend"
npm start &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Start frontend
cd "$(dirname "$0")/frontend"
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
