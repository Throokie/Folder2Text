#!/bin/bash
# CodeBundle Pro - Development Environment Setup

set -e

echo "🚀 Setting up CodeBundle Pro development environment..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "📋 Python version: $PYTHON_VERSION"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies (if requirements.txt exists)
if [ -f "requirements.txt" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Run tests
echo "🧪 Running tests..."
python3 test_codebundle.py

echo ""
echo "✅ Development environment ready!"
echo ""
echo "Usage:"
echo "  python run_codebundle.py           # Interactive mode"
echo "  python run_codebundle.py bundle .  # Bundle current directory"
echo "  python run_codebundle.py --help    # Show help"
