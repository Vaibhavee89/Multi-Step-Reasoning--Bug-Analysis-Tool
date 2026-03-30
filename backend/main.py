"""FastAPI backend for Code Analysis Agent Web Interface."""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import tempfile
import asyncio

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv
import git
from github import Github, GithubException

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.agent.orchestrator import CodeAnalysisAgent

load_dotenv()

app = FastAPI(
    title="Code Analysis Agent API",
    description="Multi-step reasoning agent for code analysis",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary storage for repositories
TEMP_REPOS_PATH = Path(os.getenv("TEMP_REPOS_PATH", "./temp_repos"))
TEMP_REPOS_PATH.mkdir(exist_ok=True)

# Active WebSocket connections
active_connections: List[WebSocket] = []


# Pydantic models
class RepoAnalysisRequest(BaseModel):
    repo_url: str
    analysis_type: str = "comprehensive"
    github_token: Optional[str] = None


class GitHubAuthRequest(BaseModel):
    code: str


class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    repo_url: str
    message: str


class AnalysisResult(BaseModel):
    analysis_id: str
    status: str
    repo_url: str
    output: str
    reasoning_steps: List[dict]
    timestamp: str


# Helper functions
def extract_repo_info(repo_url: str) -> tuple:
    """Extract owner and repo name from GitHub URL."""
    # Handle various GitHub URL formats
    url = repo_url.strip().rstrip('/')

    if url.startswith('http'):
        # https://github.com/owner/repo or https://github.com/owner/repo.git
        parts = url.split('github.com/')[-1].split('/')
    else:
        # owner/repo format
        parts = url.split('/')

    if len(parts) >= 2:
        owner = parts[0]
        repo = parts[1].replace('.git', '')
        return owner, repo

    raise ValueError("Invalid GitHub repository URL")


async def send_progress_update(message: str, analysis_id: str):
    """Send progress update to all connected WebSocket clients."""
    for connection in active_connections:
        try:
            await connection.send_json({
                "type": "progress",
                "analysis_id": analysis_id,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
        except:
            pass


def clone_repository(repo_url: str, github_token: Optional[str] = None) -> Path:
    """Clone a GitHub repository to temporary location."""
    analysis_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    repo_path = TEMP_REPOS_PATH / analysis_id

    try:
        # Add token to URL if provided for private repos
        if github_token and repo_url.startswith('https://github.com'):
            clone_url = repo_url.replace('https://', f'https://{github_token}@')
        else:
            clone_url = repo_url

        git.Repo.clone_from(clone_url, repo_path)
        return repo_path, analysis_id

    except git.GitCommandError as e:
        raise HTTPException(status_code=400, detail=f"Failed to clone repository: {str(e)}")


async def run_analysis(repo_path: Path, analysis_type: str, analysis_id: str) -> dict:
    """Run the code analysis agent on the repository."""
    try:
        await send_progress_update("Initializing analysis agent...", analysis_id)

        # Create agent
        agent = CodeAnalysisAgent(
            repo_path=str(repo_path),
            verbose=True
        )

        await send_progress_update("Starting code analysis...", analysis_id)

        # Run analysis
        result = agent.analyze(
            target=".",
            analysis_type=analysis_type
        )

        await send_progress_update("Analysis complete!", analysis_id)

        # Format reasoning steps
        reasoning_steps = []
        for i, (action, observation) in enumerate(result.get("intermediate_steps", []), 1):
            reasoning_steps.append({
                "step": i,
                "tool": action.tool,
                "input": str(action.tool_input),
                "output": str(observation)[:500] + ("..." if len(str(observation)) > 500 else "")
            })

        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "output": result["output"],
            "reasoning_steps": reasoning_steps,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        await send_progress_update(f"Error: {str(e)}", analysis_id)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Code Analysis Agent API",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "api_key_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
        "github_oauth_configured": bool(os.getenv("GITHUB_CLIENT_ID")),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_repository(request: RepoAnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze a GitHub repository."""

    # Validate inputs
    if not request.repo_url:
        raise HTTPException(status_code=400, detail="Repository URL is required")

    # Validate API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise HTTPException(status_code=500, detail="Anthropic API key not configured")

    try:
        # Clone repository
        repo_path, analysis_id = clone_repository(request.repo_url, request.github_token)

        # Start analysis in background
        background_tasks.add_task(
            run_analysis_task,
            repo_path,
            request.analysis_type,
            analysis_id
        )

        return AnalysisResponse(
            analysis_id=analysis_id,
            status="started",
            repo_url=request.repo_url,
            message="Analysis started successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def run_analysis_task(repo_path: Path, analysis_type: str, analysis_id: str):
    """Background task to run analysis."""
    try:
        result = await run_analysis(repo_path, analysis_type, analysis_id)

        # Store result (in production, use a database)
        result_file = TEMP_REPOS_PATH / f"{analysis_id}_result.json"
        import json
        with open(result_file, 'w') as f:
            json.dump(result, f)

    except Exception as e:
        print(f"Analysis error: {e}")

    finally:
        # Cleanup repository after analysis
        if repo_path.exists():
            shutil.rmtree(repo_path, ignore_errors=True)


@app.get("/api/analysis/{analysis_id}", response_model=AnalysisResult)
async def get_analysis_result(analysis_id: str):
    """Get analysis results by ID."""
    result_file = TEMP_REPOS_PATH / f"{analysis_id}_result.json"

    if not result_file.exists():
        raise HTTPException(status_code=404, detail="Analysis not found or still in progress")

    import json
    with open(result_file, 'r') as f:
        result = json.load(f)

    return AnalysisResult(**result, repo_url="")


@app.post("/api/github/validate")
async def validate_github_repo(request: RepoAnalysisRequest):
    """Validate if a GitHub repository exists and is accessible."""
    try:
        owner, repo = extract_repo_info(request.repo_url)

        # Initialize GitHub client
        if request.github_token:
            g = Github(request.github_token)
        else:
            g = Github()

        # Try to access the repository
        repository = g.get_repo(f"{owner}/{repo}")

        return {
            "valid": True,
            "name": repository.full_name,
            "description": repository.description,
            "language": repository.language,
            "stars": repository.stargazers_count,
            "is_private": repository.private
        }

    except GithubException as e:
        raise HTTPException(status_code=404, detail="Repository not found or not accessible")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time progress updates."""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)


@app.get("/api/tools")
async def get_available_tools():
    """Get list of available analysis tools."""
    return {
        "tools": [
            {
                "name": "ast_analyzer",
                "description": "AST parsing and code structure analysis"
            },
            {
                "name": "static_analyzer",
                "description": "Static analysis with pylint and flake8"
            },
            {
                "name": "code_search",
                "description": "Semantic code search and pattern detection"
            },
            {
                "name": "git_analyzer",
                "description": "Git history and commit analysis"
            }
        ],
        "analysis_types": [
            {
                "type": "bug_detection",
                "description": "Find logical errors and runtime bugs"
            },
            {
                "type": "security_scan",
                "description": "Identify security vulnerabilities"
            },
            {
                "type": "code_quality",
                "description": "Analyze code quality and maintainability"
            },
            {
                "type": "comprehensive",
                "description": "Complete analysis covering all aspects"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
