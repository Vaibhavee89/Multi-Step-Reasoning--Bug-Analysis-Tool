"""Git integration tools for analyzing repository history."""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta
from langchain.tools import BaseTool
from pydantic import Field


class GitAnalyzerTool(BaseTool):
    """Tool for analyzing git repository history."""

    name: str = "git_analyzer"
    description: str = """Analyzes git repository history to find patterns and insights.

    Use this tool to:
    - Find frequently changed files (bug-prone areas)
    - Analyze commit history for specific files
    - Identify who last modified code sections
    - Track when bugs were introduced

    Input should be a JSON string with:
    {
        "operation": "frequent_changes" | "file_history" | "recent_commits" | "blame",
        "file_path": "path/to/file.py" (for file-specific operations),
        "days": 90 (for time-based queries)
    }
    """

    repo_path: Path = Field(default=None)

    def __init__(self, repo_path: str):
        super().__init__()
        self.repo_path = Path(repo_path)

    def _run(self, query: str) -> str:
        """Execute git analysis."""
        try:
            import git
        except ImportError:
            return "GitPython not installed. Run: pip install GitPython"

        try:
            params = json.loads(query)
            operation = params.get("operation", "frequent_changes")

            # Check if it's a git repository
            try:
                repo = git.Repo(self.repo_path)
            except git.InvalidGitRepositoryError:
                return f"Error: {self.repo_path} is not a git repository"

            if operation == "frequent_changes":
                days = params.get("days", 90)
                return self._find_frequent_changes(repo, days)
            elif operation == "file_history":
                file_path = params.get("file_path")
                if not file_path:
                    return "Error: file_path required for file_history operation"
                return self._analyze_file_history(repo, file_path)
            elif operation == "recent_commits":
                days = params.get("days", 30)
                return self._get_recent_commits(repo, days)
            elif operation == "blame":
                file_path = params.get("file_path")
                if not file_path:
                    return "Error: file_path required for blame operation"
                return self._get_blame_info(repo, file_path)
            else:
                return f"Unknown operation: {operation}"

        except json.JSONDecodeError:
            return "Error: Invalid JSON input"
        except Exception as e:
            return f"Error during git analysis: {str(e)}"

    def _find_frequent_changes(self, repo, days: int) -> str:
        """Find files that change frequently (potential bug hotspots)."""
        since_date = datetime.now() - timedelta(days=days)
        file_changes = {}

        for commit in repo.iter_commits(since=since_date):
            for item in commit.stats.files:
                file_changes[item] = file_changes.get(item, 0) + 1

        # Sort by frequency
        sorted_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)

        output = [f"Most frequently changed files (last {days} days):\n"]
        for file_path, count in sorted_files[:15]:
            output.append(f"  {count:3d} changes: {file_path}")

        output.append(
            f"\nNote: Frequently changed files may indicate:"
            f"\n  - Active development areas"
            f"\n  - Bug-prone code requiring frequent fixes"
            f"\n  - Code that needs refactoring"
        )

        return "\n".join(output)

    def _analyze_file_history(self, repo, file_path: str) -> str:
        """Analyze commit history for a specific file."""
        full_path = self.repo_path / file_path

        if not full_path.exists():
            return f"Error: File {file_path} not found"

        try:
            commits = list(repo.iter_commits(paths=file_path, max_count=20))
        except Exception as e:
            return f"Error getting file history: {str(e)}"

        if not commits:
            return f"No commit history found for {file_path}"

        output = [f"Recent commit history for {file_path}:\n"]

        for commit in commits:
            date = datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d')
            message = commit.message.split('\n')[0][:60]
            output.append(f"  {date} - {commit.author.name}: {message}")

        output.append(f"\nTotal commits: {len(commits)}")
        output.append(f"First commit: {datetime.fromtimestamp(commits[-1].committed_date).strftime('%Y-%m-%d')}")
        output.append(f"Last commit: {datetime.fromtimestamp(commits[0].committed_date).strftime('%Y-%m-%d')}")

        return "\n".join(output)

    def _get_recent_commits(self, repo, days: int) -> str:
        """Get recent commits to understand current development."""
        since_date = datetime.now() - timedelta(days=days)
        commits = list(repo.iter_commits(since=since_date, max_count=20))

        if not commits:
            return f"No commits found in the last {days} days"

        output = [f"Recent commits (last {days} days):\n"]

        for commit in commits:
            date = datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M')
            message = commit.message.split('\n')[0][:70]
            files_changed = len(commit.stats.files)
            output.append(f"  {date} - {commit.author.name}")
            output.append(f"    {message}")
            output.append(f"    Files changed: {files_changed}\n")

        return "\n".join(output)

    def _get_blame_info(self, repo, file_path: str) -> str:
        """Get blame information for a file."""
        full_path = self.repo_path / file_path

        if not full_path.exists():
            return f"Error: File {file_path} not found"

        try:
            blame = repo.blame('HEAD', file_path)
        except Exception as e:
            return f"Error getting blame info: {str(e)}"

        # Aggregate by author
        author_lines = {}
        for commit, lines in blame:
            author = commit.author.name
            author_lines[author] = author_lines.get(author, 0) + len(lines)

        total_lines = sum(author_lines.values())

        output = [f"Code authorship for {file_path}:\n"]
        sorted_authors = sorted(author_lines.items(), key=lambda x: x[1], reverse=True)

        for author, lines in sorted_authors:
            percentage = (lines / total_lines) * 100
            output.append(f"  {author}: {lines} lines ({percentage:.1f}%)")

        return "\n".join(output)

    async def _arun(self, query: str) -> str:
        """Async version."""
        return self._run(query)
