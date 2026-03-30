#!/bin/bash

# Docker startup script for Code Analysis Agent

echo "╔═══════════════════════════════════════════════╗"
echo "║   Code Analysis Agent - Docker Startup        ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker is installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found"
    echo "Creating .env from template..."
    cp .env.docker .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY"
    echo "   Run: nano .env"
    echo ""
    read -p "Press Enter after you've added your API key..."
fi

# Parse command line arguments
MODE=${1:-prod}

if [ "$MODE" = "dev" ]; then
    echo "Starting in DEVELOPMENT mode..."
    echo "  - Backend with hot reload"
    echo "  - Frontend with Vite dev server"
    echo ""
    docker-compose -f docker-compose.dev.yml up --build
elif [ "$MODE" = "prod" ]; then
    echo "Starting in PRODUCTION mode..."
    echo "  - Optimized builds"
    echo "  - Nginx serving frontend"
    echo ""
    docker-compose up --build -d
    echo ""
    echo "✓ Services started successfully!"
    echo ""
    echo "Access your application:"
    echo "  Frontend: http://localhost"
    echo "  Backend:  http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "View logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "Stop services:"
    echo "  docker-compose down"
elif [ "$MODE" = "stop" ]; then
    echo "Stopping all services..."
    docker-compose down
    docker-compose -f docker-compose.dev.yml down
    echo "✓ All services stopped"
elif [ "$MODE" = "logs" ]; then
    docker-compose logs -f
else
    echo "Usage: ./docker-start.sh [prod|dev|stop|logs]"
    echo ""
    echo "  prod  - Production mode (default)"
    echo "  dev   - Development mode with hot reload"
    echo "  stop  - Stop all services"
    echo "  logs  - View logs"
    exit 1
fi
