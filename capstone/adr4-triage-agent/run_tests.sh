#!/bin/bash
# Run ADR-4 test suite

set -e

echo "Running ADR-4 Clinical Content Triage Agent Tests"
echo "=================================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run tests
echo ""
echo "Running unit tests..."
pytest tests/test_agent.py -v

echo ""
echo "Running API tests..."
pytest tests/test_api.py -v

echo ""
echo "Running validation scenarios..."
pytest tests/test_scenarios.py -v

echo ""
echo "All tests complete!"
