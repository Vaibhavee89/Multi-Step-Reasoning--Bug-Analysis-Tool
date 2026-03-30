#!/bin/bash

# Installation script for Code Analysis & Debugging Agent

echo "╔═══════════════════════════════════════════════╗"
echo "║   Code Analysis Agent - Installation         ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if Python >= 3.9
required_version="3.9"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.9 or higher is required"
    exit 1
fi

echo "✓ Python version OK"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY"
    echo "   Get your API key from: https://console.anthropic.com/"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

# Create data directories
echo "Creating data directories..."
mkdir -p data/cache
mkdir -p data/vector_store

echo "✓ Data directories created"
echo ""

# Run tests
echo "Running tests..."
pytest tests/ -v --tb=short

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   Installation Complete!                      ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your ANTHROPIC_API_KEY"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run the demo: python examples/demo_analysis.py"
echo "4. Or analyze code: python src/ui/cli.py --help"
echo ""
echo "Documentation:"
echo "- README.md: Full documentation"
echo "- QUICKSTART.md: Quick start guide"
echo "- PROJECT_OVERVIEW.md: Project details"
echo ""
echo "Happy analyzing! 🚀"
