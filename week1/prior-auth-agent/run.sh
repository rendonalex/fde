#!/bin/bash
# Quick start script for Prior-Authorization Check Agent

set -e

echo "🏥 Prior-Authorization Check Agent"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please configure .env with your database credentials"
fi

# Run database migrations (create tables)
echo "🗄️  Setting up database..."
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine); print('✅ Database tables created')"

# Start the application
echo ""
echo "🚀 Starting application..."
echo "📖 API docs will be available at: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
