# 🐳 Docker Deployment Guide

Complete guide to deploy the Code Analysis Agent using Docker.

## 📋 Prerequisites

- Docker 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose 2.0+ ([Install Compose](https://docs.docker.com/compose/install/))
- Anthropic API Key ([Get one here](https://console.anthropic.com/))

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Vaibhavee89/Multi-Step-Reasoning--Bug-Analysis-Tool.git
cd Multi-Step-Reasoning--Bug-Analysis-Tool
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.docker .env

# Edit and add your API key
nano .env  # or use your preferred editor
```

Add your Anthropic API key:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Start Application
```bash
# Production mode (optimized)
./docker-start.sh prod

# OR Development mode (with hot reload)
./docker-start.sh dev
```

### 4. Access Application
- **Frontend:** http://localhost
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 📦 What's Included

### Services

**Backend (Port 8000)**
- FastAPI server
- WebSocket support
- GitHub integration
- LangChain agent
- Automatic cleanup

**Frontend (Port 80/3000)**
- React application
- Real-time updates
- Beautiful UI
- Responsive design

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         Docker Host                 │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Frontend Container          │  │
│  │  - Nginx (production)        │  │
│  │  - Vite dev server (dev)     │  │
│  │  - Port: 80 or 3000          │  │
│  └────────┬─────────────────────┘  │
│           │                         │
│           │ HTTP/WebSocket          │
│           │                         │
│  ┌────────▼─────────────────────┐  │
│  │  Backend Container           │  │
│  │  - FastAPI                   │  │
│  │  - Uvicorn                   │  │
│  │  - Port: 8000                │  │
│  └────────┬─────────────────────┘  │
│           │                         │
│           │ Network Bridge          │
│           │                         │
│  ┌────────▼─────────────────────┐  │
│  │  Volumes                     │  │
│  │  - backend-cache             │  │
│  │  - temp_repos                │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

## 🎯 Usage Modes

### Production Mode (Recommended for Deployment)

**Features:**
- Optimized builds
- Nginx serving frontend
- Health checks enabled
- Auto-restart on failure
- Persistent volumes

**Start:**
```bash
./docker-start.sh prod

# OR manually:
docker-compose up -d --build
```

**Access:**
- Frontend: http://localhost
- Backend: http://localhost:8000

### Development Mode (For Local Development)

**Features:**
- Hot reload for both services
- Source code mounted as volumes
- Faster iteration
- Development server logs

**Start:**
```bash
./docker-start.sh dev

# OR manually:
docker-compose -f docker-compose.dev.yml up --build
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## 🔧 Docker Commands

### Basic Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up --build -d
```

### Advanced Operations

```bash
# Enter backend container
docker exec -it bug-analysis-backend bash

# Enter frontend container
docker exec -it bug-analysis-frontend sh

# View container status
docker-compose ps

# Check resource usage
docker stats

# Remove all volumes (clean slate)
docker-compose down -v

# Remove all containers and images
docker-compose down --rmi all
```

## 🌐 Environment Variables

### Backend (.env)

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxx

# Optional
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_secret
CLAUDE_MODEL=claude-sonnet-4-5-20250929
MAX_ITERATIONS=15
VERBOSE=true
```

### Frontend (Automatic)

Frontend environment is automatically configured by Docker Compose.

For custom API URL:
```bash
VITE_API_URL=http://localhost:8000
```

## 📊 Health Checks

Both services include health checks:

**Backend:**
- Endpoint: `/api/health`
- Interval: 30s
- Timeout: 10s

**Frontend:**
- Check: HTTP GET /
- Interval: 30s
- Timeout: 10s

View health status:
```bash
docker-compose ps
```

## 🔒 Security Considerations

### Production Deployment

1. **Use HTTPS:**
   ```bash
   # Use Nginx proxy or load balancer
   # Enable SSL certificates (Let's Encrypt)
   ```

2. **Environment Variables:**
   ```bash
   # Never commit .env file
   # Use secrets management in production
   ```

3. **Network Security:**
   ```bash
   # Configure firewall rules
   # Restrict port access
   # Use Docker networks
   ```

4. **Updates:**
   ```bash
   # Regular security updates
   docker-compose pull
   docker-compose up -d
   ```

## 🚀 Deployment Options

### Deploy to Cloud

#### 1. AWS ECS/Fargate

```bash
# Push images to ECR
docker tag bug-analysis-backend:latest xxx.dkr.ecr.region.amazonaws.com/backend
docker push xxx.dkr.ecr.region.amazonaws.com/backend

# Use ECS task definitions
# Configure load balancer
```

#### 2. Google Cloud Run

```bash
# Build and push
docker build -t gcr.io/project-id/backend backend
docker push gcr.io/project-id/backend

# Deploy
gcloud run deploy backend --image gcr.io/project-id/backend
```

#### 3. DigitalOcean App Platform

```bash
# Connect GitHub repository
# Configure from App Platform UI
# Automatic deployments on push
```

#### 4. Railway

```bash
# Connect GitHub repository
# Railway auto-detects Docker Compose
# Set environment variables in UI
```

### Docker Hub

```bash
# Build images
docker-compose build

# Tag images
docker tag bug-analysis-backend username/bug-analysis-backend:latest
docker tag bug-analysis-frontend username/bug-analysis-frontend:latest

# Push to Docker Hub
docker push username/bug-analysis-backend:latest
docker push username/bug-analysis-frontend:latest
```

## 🐛 Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

**Common issues:**
- Missing API key in .env
- Port already in use
- Insufficient disk space

### Backend Connection Issues

**Check backend is running:**
```bash
curl http://localhost:8000/api/health
```

**Restart backend:**
```bash
docker-compose restart backend
```

### Frontend Can't Reach Backend

**Check network:**
```bash
docker network ls
docker network inspect bug-analysis-network
```

**Verify CORS settings in backend/main.py**

### Volume Issues

**Clear volumes:**
```bash
docker-compose down -v
docker volume prune
```

### Build Failures

**Clean build:**
```bash
docker-compose down
docker system prune -a
docker-compose up --build
```

## 📈 Performance Optimization

### Production Optimizations

1. **Multi-stage Builds:**
   - Already implemented in Dockerfiles
   - Smaller image sizes
   - Faster deployments

2. **Caching:**
   - Layer caching enabled
   - npm/pip cache optimization
   - Volume mounts for persistence

3. **Resource Limits:**
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '1.0'
             memory: 1G
   ```

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/docker.yml
name: Docker Build and Push

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build images
        run: docker-compose build

      - name: Push to registry
        run: |
          docker push your-registry/backend
          docker push your-registry/frontend
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## 🎉 Quick Commands Reference

```bash
# Start production
./docker-start.sh prod

# Start development
./docker-start.sh dev

# Stop all services
./docker-start.sh stop

# View logs
./docker-start.sh logs

# Manual commands
docker-compose up -d              # Start
docker-compose down               # Stop
docker-compose logs -f            # Logs
docker-compose ps                 # Status
docker-compose restart            # Restart
docker-compose up --build -d      # Rebuild
```

---

## 🚀 You're Ready to Deploy!

Your dockerized application is ready for:
- ✅ Local development
- ✅ Production deployment
- ✅ Cloud platforms
- ✅ CI/CD pipelines

**Start now:** `./docker-start.sh prod`

**Questions?** Check the troubleshooting section above!
