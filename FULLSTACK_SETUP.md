# Full-Stack Setup Guide

Complete guide to set up and run the Code Analysis Agent web application.

## Architecture

```
┌─────────────────┐
│  React Frontend │ (Port 3000)
│   TypeScript    │
│   Tailwind CSS  │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│  FastAPI Backend│ (Port 8000)
│   Python 3.9+   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LangChain Agent│
│  Claude (API)   │
│  Analysis Tools │
└─────────────────┘
```

## Prerequisites

- Python 3.9+
- Node.js 18+
- Git
- Anthropic API key
- (Optional) GitHub Personal Access Token for private repos

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

**Configure `.env`:**
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
GITHUB_CLIENT_ID=your_github_oauth_id  # Optional for GitHub OAuth
GITHUB_CLIENT_SECRET=your_secret        # Optional
```

**Start backend:**
```bash
python main.py
```

Backend will run on: http://localhost:8000

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Usually no changes needed for local development
```

**Start frontend:**
```bash
npm run dev
```

Frontend will run on: http://localhost:3000

### 3. Access the Application

Open your browser to: **http://localhost:3000**

## Features

### Public Repository Analysis
1. Enter any public GitHub repository URL
2. Select analysis type (Comprehensive, Bug Detection, Security, etc.)
3. Click "Start Analysis"
4. View real-time progress
5. Get detailed results with reasoning traces

### Private Repository Analysis
1. Check "This is a private repository"
2. Enter your GitHub Personal Access Token
3. Continue with analysis

### Creating GitHub Token

For private repositories:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scope: `repo` (full control of private repositories)
4. Copy the generated token
5. Paste it in the web interface

## API Endpoints

### Backend API (Port 8000)

- `GET /` - Health check
- `GET /api/health` - Detailed health status
- `POST /api/analyze` - Start repository analysis
- `GET /api/analysis/{id}` - Get analysis results
- `POST /api/github/validate` - Validate GitHub repo
- `GET /api/tools` - Get available tools and analysis types
- `WS /ws` - WebSocket for real-time updates

### Example API Usage

```bash
# Validate repository
curl -X POST http://localhost:8000/api/github/validate \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/facebook/react"}'

# Start analysis
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/facebook/react",
    "analysis_type": "comprehensive"
  }'

# Get results
curl http://localhost:8000/api/analysis/20240330_123456
```

## Project Structure

```
BugAnalysisTool/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables
│   └── temp_repos/            # Temporary cloned repos
│
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/
│   │   │   ├── HomePage.tsx   # Landing/input page
│   │   │   └── AnalysisPage.tsx # Results page
│   │   ├── services/
│   │   │   └── api.ts         # API client
│   │   ├── types/             # TypeScript types
│   │   └── App.tsx            # Main app component
│   ├── package.json
│   └── vite.config.ts
│
└── src/                       # Existing agent code
    ├── agent/                 # LangChain agent
    └── tools/                 # Analysis tools
```

## Development

### Backend Development

```bash
cd backend

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/

# Check logs
tail -f logs/app.log
```

### Frontend Development

```bash
cd frontend

# Development mode (hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check
npx tsc --noEmit
```

## Troubleshooting

### Backend Issues

**"ANTHROPIC_API_KEY not found"**
- Make sure `.env` file exists in `backend/`
- Check API key is valid and starts with `sk-ant-`

**"Failed to clone repository"**
- Check repository URL is correct
- For private repos, verify GitHub token has `repo` scope
- Check network connectivity

**"Import Error"**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend Issues

**"Cannot connect to backend"**
- Make sure backend is running on port 8000
- Check proxy configuration in `vite.config.ts`
- Check CORS settings in backend

**"npm install fails"**
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Try using `npm ci` instead

**Build errors**
- Clear cache: `rm -rf node_modules/.vite`
- Rebuild: `npm run build`

## Production Deployment

### Backend (Python/FastAPI)

**Option 1: Docker**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Option 2: Traditional Server**
```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Frontend (React)

**Build:**
```bash
cd frontend
npm run build
# Output in: dist/
```

**Deploy to:**
- Vercel: `vercel --prod`
- Netlify: `netlify deploy --prod --dir=dist`
- AWS S3 + CloudFront
- GitHub Pages

## Environment Variables

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
TEMP_REPOS_PATH=./temp_repos
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
```

## Security Considerations

1. **API Keys**: Never commit `.env` files
2. **GitHub Tokens**: Stored only in memory, not persisted
3. **CORS**: Configure allowed origins in production
4. **Rate Limiting**: Implement rate limits for API
5. **Input Validation**: All inputs validated on backend
6. **Temporary Files**: Automatically cleaned after analysis

## Performance Tips

1. **Caching**: Results cached temporarily
2. **Async Processing**: Analysis runs in background
3. **WebSocket**: Real-time updates without polling
4. **Cleanup**: Temp repositories deleted after analysis

## Support

For issues or questions:
1. Check this guide first
2. Review backend logs
3. Check browser console for frontend errors
4. Verify API health: http://localhost:8000/api/health

## Next Steps

1. Test with public repositories first
2. Try different analysis types
3. Explore reasoning traces
4. Customize analysis prompts
5. Add more tools to the agent

---

**Happy analyzing!** 🚀
