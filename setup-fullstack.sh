#!/bin/bash

# Full-Stack Setup Script for Code Analysis Agent

echo "╔═══════════════════════════════════════════════╗"
echo "║   Code Analysis Agent - Full-Stack Setup      ║"
echo "║   Backend (FastAPI) + Frontend (React)        ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

required_version="3.9"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.9 or higher is required"
    exit 1
fi
echo "✓ Python version OK"
echo ""

# Check Node.js version
echo "Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js 18+ from: https://nodejs.org/"
    exit 1
fi

node_version=$(node --version | cut -d'v' -f2)
echo "Found Node.js v$node_version"
echo "✓ Node.js installed"
echo ""

# ============================================
# Backend Setup
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Setting up Backend (FastAPI)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt --quiet

echo "✓ Backend dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating backend .env file..."
    cp .env.example .env
    echo "✓ Backend .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit backend/.env and add your ANTHROPIC_API_KEY"
    echo ""
else
    echo "✓ Backend .env file already exists"
    echo ""
fi

# Create temp directories
mkdir -p temp_repos
echo "✓ Created temporary directories"
echo ""

cd ..

# ============================================
# Frontend Setup
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Setting up Frontend (React)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd frontend

# Install frontend dependencies
echo "Installing frontend dependencies (this may take a minute)..."
npm install --silent

echo "✓ Frontend dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating frontend .env file..."
    cp .env.example .env
    echo "✓ Frontend .env file created"
    echo ""
else
    echo "✓ Frontend .env file already exists"
    echo ""
fi

cd ..

# ============================================
# Completion
# ============================================
echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   Setup Complete! ✓                           ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your API key:"
echo "   Edit backend/.env and add your ANTHROPIC_API_KEY"
echo "   Get your key from: https://console.anthropic.com/"
echo ""
echo "2. Start the backend server:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python main.py"
echo "   (Backend will run on http://localhost:8000)"
echo ""
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo "   (Frontend will run on http://localhost:3000)"
echo ""
echo "4. Open your browser:"
echo "   http://localhost:3000"
echo ""
echo "Documentation:"
echo "- FULLSTACK_SETUP.md: Complete setup guide"
echo "- README.md: Project overview"
echo ""
echo "Happy analyzing! 🚀"
