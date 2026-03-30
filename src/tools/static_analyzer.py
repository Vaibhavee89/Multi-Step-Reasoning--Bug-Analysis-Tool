"""Static analysis tool using pylint, mypy, and other linters."""

import subprocess
import json
from pathlib import Path
from typing import Dict, List
from langchain.tools import BaseTool
from pydantic import Field


class StaticAnalyzerTool(BaseTool):
    """Tool for running static analysis on code."""

    name: str = "static_analyzer"
    description: str = """Runs static analysis tools (pylint, flake8) on Python code.

    Use this tool to:
    - Find syntax errors and style violations
    - Detect potential bugs through static analysis
    - Check code quality metrics
    - Identify unused imports and variables

    Input should be a JSON string with:
    {
        "file_path": "path/to/file.py",
        "analyzer": "pylint" | "flake8" | "both"
    }
    """

    repo_path: Path = Field(default=None)

    def __init__(self, repo_path: str):
        super().__init__()
        self.repo_path = Path(repo_path)

    def _run(self, query: str) -> str:
        """Execute static analysis."""
        try:
            params = json.loads(query)
            file_path = self.repo_path / params["file_path"]
            analyzer = params.get("analyzer", "both")

            if not file_path.exists():
                return f"Error: File {file_path} not found"

            results = []

            if analyzer in ["pylint", "both"]:
                pylint_result = self._run_pylint(file_path)
                results.append(f"=== Pylint Analysis ===\n{pylint_result}")

            if analyzer in ["flake8", "both"]:
                flake8_result = self._run_flake8(file_path)
                results.append(f"=== Flake8 Analysis ===\n{flake8_result}")

            return "\n\n".join(results)

        except json.JSONDecodeError:
            return "Error: Invalid JSON input"
        except Exception as e:
            return f"Error during static analysis: {str(e)}"

    def _run_pylint(self, file_path: Path) -> str:
        """Run pylint on the file."""
        try:
            result = subprocess.run(
                ["pylint", "--output-format=json", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.stdout:
                try:
                    issues = json.loads(result.stdout)
                    return self._format_pylint_output(issues)
                except json.JSONDecodeError:
                    return result.stdout

            return "No issues found by pylint"

        except subprocess.TimeoutExpired:
            return "Pylint analysis timed out"
        except FileNotFoundError:
            return "Pylint not installed. Run: pip install pylint"
        except Exception as e:
            return f"Pylint error: {str(e)}"

    def _run_flake8(self, file_path: Path) -> str:
        """Run flake8 on the file."""
        try:
            result = subprocess.run(
                ["flake8", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.stdout:
                return self._format_flake8_output(result.stdout)

            return "No issues found by flake8"

        except subprocess.TimeoutExpired:
            return "Flake8 analysis timed out"
        except FileNotFoundError:
            return "Flake8 not installed. Run: pip install flake8"
        except Exception as e:
            return f"Flake8 error: {str(e)}"

    def _format_pylint_output(self, issues: List[Dict]) -> str:
        """Format pylint JSON output."""
        if not issues:
            return "No issues found"

        # Group by severity
        by_severity = {"error": [], "warning": [], "convention": [], "refactor": []}

        for issue in issues:
            severity = issue.get("type", "warning")
            by_severity.setdefault(severity, []).append(issue)

        output = []
        for severity in ["error", "warning", "refactor", "convention"]:
            items = by_severity.get(severity, [])
            if items:
                output.append(f"\n{severity.upper()}S ({len(items)}):")
                for item in items[:10]:  # Limit to 10 per severity
                    output.append(
                        f"  Line {item['line']}: [{item['message-id']}] {item['message']}"
                    )

        return "\n".join(output)

    def _format_flake8_output(self, output: str) -> str:
        """Format flake8 output."""
        lines = output.strip().split('\n')
        if not lines or lines == ['']:
            return "No issues found"

        formatted = [f"Found {len(lines)} issues:\n"]
        for line in lines[:20]:  # Limit output
            formatted.append(f"  {line}")

        return "\n".join(formatted)

    async def _arun(self, query: str) -> str:
        """Async version."""
        return self._run(query)
