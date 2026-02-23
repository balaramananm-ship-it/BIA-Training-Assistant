#!/bin/bash

# AI Training Assistant - Backend Startup Script

echo "🚀 AI Training Assistant Backend Starter"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv backend/venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source backend/venv/bin/activate

# Install requirements
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "========================================"
echo "✓ Setup Complete!"
echo "========================================"
echo ""

# Check Ollama
echo "🔍 Checking Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Ollama is running at localhost:11434"
else
    echo "⚠️  Ollama is not accessible at localhost:11434"
    echo "   Make sure to start Ollama with: ollama serve"
    echo ""
fi

echo ""
echo "========================================"
echo "🚀 Starting Backend Server..."
echo "========================================"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""

# Start backend
cd backend
uvicorn api:app --reload --host 0.0.0.0 --port 8000
