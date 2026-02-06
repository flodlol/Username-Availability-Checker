#!/bin/bash

# Handle Scout - Easy Run Script
# Just double-click this file or run: ./run.sh

echo "🔎 Starting Handle Scout..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo ""
    echo "Please install Python first:"
    echo "  - Mac: brew install python3"
    echo "  - Windows: https://python.org/downloads"
    echo "  - Linux: sudo apt install python3 python3-pip"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Create virtual environment if needed
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo ""
fi

source .venv/bin/activate

# Install dependencies if needed
if ! python -c "import colorama" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    python -m pip install -r requirements.txt
    echo ""
fi

echo "✅ Starting terminal app"
echo "   Press Ctrl+C to stop"
echo ""

python cli.py
