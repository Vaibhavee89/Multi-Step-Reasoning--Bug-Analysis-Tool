# 🌐 Code Analysis Agent - Web Application

Beautiful web interface for analyzing GitHub repositories with AI-powered multi-step reasoning.

## ✨ Features

### 🔍 **Analyze Any GitHub Repository**
- **Public Repositories**: Just paste the URL and analyze
- **Private Repositories**: Authenticate with your GitHub token
- **Real-time Progress**: Watch the agent think through the analysis
- **Detailed Results**: Get comprehensive bug reports with reasoning traces

### 🎯 **Analysis Types**
- **Comprehensive**: Full analysis covering all aspects
- **Bug Detection**: Find logical errors and runtime bugs
- **Security Scan**: Identify vulnerabilities (SQL injection, XSS, etc.)
- **Code Quality**: Maintainability and best practices

### 🧠 **Multi-Step Reasoning**
- See exactly how the AI agent thinks
- View each tool used and why
- Understand the analysis process
- Export results for documentation

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Anthropic API Key ([Get one here](https://console.anthropic.com/))

### Automated Setup

```bash
# Run the setup script
./setup-fullstack.sh
```

This will:
- ✅ Set up Python backend with FastAPI
- ✅ Set up React frontend with TypeScript
- ✅ Install all dependencies
- ✅ Create configuration files

### Manual Setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```
Backend runs on: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs on: http://localhost:3000

**Open Browser:**
Navigate to: http://localhost:3000

## 📖 User Guide

### Analyzing a Public Repository

1. **Enter Repository URL**
   ```
   https://github.com/owner/repository
   ```

2. **Validate Repository** (optional)
   - Click "Validate" to check if repo exists
   - See repo info: stars, language, description

3. **Select Analysis Type**
   - Comprehensive (recommended)
   - Bug Detection
   - Security Scan
   - Code Quality

4. **Start Analysis**
   - Click "Start Analysis"
   - Watch real-time progress
   - Wait for completion (1-5 minutes)

5. **View Results**
   - Detailed bug reports
   - Severity levels (Critical, High, Medium, Low)
   - Reasoning traces showing how issues were found
   - Suggested fixes

### Analyzing a Private Repository

1. **Get GitHub Token**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scope: `repo` (full access)
   - Copy the generated token

2. **Use Token in App**
   - Check "This is a private repository"
   - Paste your GitHub token
   - Continue with analysis

3. **Security**
   - Token is used only for cloning
   - Not stored permanently
   - Cleared after analysis

## 🎨 Screenshots

### Home Page
- Clean, modern interface
- Easy repository input
- Analysis type selection
- GitHub token support

### Analysis Page
- Real-time progress updates
- WebSocket-powered live feed
- Spinning loader with status
- Progress messages

### Results Page
- Comprehensive bug report
- Severity categorization
- Reasoning trace viewer
- Downloadable JSON report

## 🔧 Configuration

### Backend Environment Variables

**backend/.env:**
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional
GITHUB_CLIENT_ID=your_github_oauth_id
GITHUB_CLIENT_SECRET=your_github_oauth_secret
CLAUDE_MODEL=claude-sonnet-4-5-20250929
MAX_ITERATIONS=15
VERBOSE=true
```

### Frontend Environment Variables

**frontend/.env:**
```bash
VITE_API_URL=http://localhost:8000
```

## 📊 API Reference

### Endpoints

**Health Check**
```bash
GET /api/health
```

**Start Analysis**
```bash
POST /api/analyze
{
  "repo_url": "https://github.com/owner/repo",
  "analysis_type": "comprehensive",
  "github_token": "optional_token"
}
```

**Get Results**
```bash
GET /api/analysis/{analysis_id}
```

**Validate Repository**
```bash
POST /api/github/validate
{
  "repo_url": "https://github.com/owner/repo",
  "github_token": "optional"
}
```

**WebSocket for Progress**
```bash
WS /ws
```

## 🏗️ Architecture

```
┌──────────────────────┐
│   React Frontend     │
│   - TypeScript       │
│   - Tailwind CSS     │
│   - Vite             │
└──────────┬───────────┘
           │ HTTP/WebSocket
           │
┌──────────▼───────────┐
│   FastAPI Backend    │
│   - Python 3.9+      │
│   - Async/Await      │
│   - CORS enabled     │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│   LangChain Agent    │
│   - Claude API       │
│   - ReAct Pattern    │
│   - 4 Analysis Tools │
└──────────────────────┘
```

## 🔍 Tech Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Vite** - Build tool
- **Axios** - HTTP client
- **React Router** - Navigation
- **React Markdown** - Formatted output

### Backend
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **WebSockets** - Real-time updates
- **PyGithub** - GitHub API
- **GitPython** - Repository cloning
- **LangChain** - Agent orchestration
- **Anthropic** - Claude AI

## 🚀 Deployment

### Backend Deployment

**Docker:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
COPY src/ ../src/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Traditional Server:**
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Frontend Deployment

**Build:**
```bash
cd frontend
npm run build
```

**Deploy to:**
- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages
- Any static host

## 🔒 Security

- ✅ API keys stored securely in environment variables
- ✅ GitHub tokens used only in memory
- ✅ CORS configured for allowed origins
- ✅ Input validation on all endpoints
- ✅ Temporary repositories auto-cleaned
- ✅ Rate limiting recommended for production

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Check environment variables
cat backend/.env

# Check logs
python main.py
```

### Frontend Won't Build
```bash
# Clear cache
rm -rf node_modules/.vite
rm -rf node_modules

# Reinstall
npm install
npm run dev
```

### Can't Connect to Backend
- Check backend is running on port 8000
- Check CORS settings in `main.py`
- Verify API URL in frontend `.env`

## 📚 Related Documentation

- [FULLSTACK_SETUP.md](FULLSTACK_SETUP.md) - Complete setup guide
- [README.md](README.md) - Project overview
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Architecture details

## 💡 Tips

1. **Start with small repos** - Test with smaller repositories first
2. **Use comprehensive analysis** - Gets best results
3. **Check reasoning traces** - Learn how the AI thinks
4. **Download reports** - Export as JSON for documentation
5. **Try different repos** - See how it handles various codebases

## 🎯 Example Repositories to Try

**Good starter repos:**
- https://github.com/django/django
- https://github.com/flask/flask
- https://github.com/facebook/react
- https://github.com/tensorflow/tensorflow

**Small test repos:**
- Any of your own projects
- Toy projects for learning
- Code challenge solutions

## 🤝 Contributing

Want to improve the web interface?

**Frontend improvements:**
- Better UI/UX
- Dark mode
- Export to PDF
- Comparison view

**Backend enhancements:**
- Caching layer
- Database for results
- User authentication
- API rate limiting

## 📄 License

MIT License - See main README.md

---

## 🎉 You're Ready!

1. Run `./setup-fullstack.sh`
2. Add your API key
3. Start backend and frontend
4. Open http://localhost:3000
5. Start analyzing!

**Happy analyzing!** 🚀
