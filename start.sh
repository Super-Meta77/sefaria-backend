#!/bin/bash

# Sefaria Advanced Backend - Quick Start Script

echo "🚀 Starting Sefaria Advanced Backend..."
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
pip install -r requirements.txt

# Start the server
echo ""
echo "✅ Starting FastAPI server..."
echo "📖 Swagger docs will be available at: http://localhost:8000/docs"
echo "📄 ReDoc will be available at: http://localhost:8000/redoc"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

