"""Code search tool for finding patterns and definitions."""

import re
from pathlib import Path
from typing import List, Dict
from langchain.tools import BaseTool
from pydantic import Field


class CodeSearchTool(BaseTool):
    """Tool for searching code patterns and definitions."""

    name: str = "code_search"
    description: str = """Search for code patterns, function definitions, and usage.

    Use this tool to:
    - Find function or class definitions
    - Search for variable usage
    - Locate specific code patterns
    - Find function call sites

    Input should be a JSON string with:
    {
        "query": "search term or pattern",
        "search_type": "function_def" | "class_def" | "usage" | "pattern",
        "file_pattern": "*.py" (optional)
    }
    """

    repo_path: Path = Field(default=None)

    def __init__(self, repo_path: str):
        super().__init__()
        self.repo_path = Path(repo_path)

    def _run(self, query: str) -> str:
        """Execute code search."""
        import json

        try:
            params = json.loads(query)
            search_query = params["query"]
            search_type = params.get("search_type", "pattern")
            file_pattern = params.get("file_pattern", "*.py")

            results = []

            if search_type == "function_def":
                results = self._search_function_definitions(search_query, file_pattern)
            elif search_type == "class_def":
                results = self._search_class_definitions(search_query, file_pattern)
            elif search_type == "usage":
                results = self._search_usage(search_query, file_pattern)
            else:
                results = self._search_pattern(search_query, file_pattern)

            return self._format_results(results, search_query)

        except json.JSONDecodeError:
            return "Error: Invalid JSON input"
        except Exception as e:
            return f"Error during code search: {str(e)}"

    def _search_function_definitions(self, func_name: str, pattern: str) -> List[Dict]:
        """Search for function definitions."""
        results = []
        regex = re.compile(rf'^\s*def\s+{re.escape(func_name)}\s*\(')

        for file_path in self.repo_path.rglob(pattern):
            if file_path.is_file():
                try:
                    with open(file_path, 'r') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append({
                                    "file": str(file_path.relative_to(self.repo_path)),
                                    "line": line_num,
                                    "content": line.strip(),
                                    "type": "function_definition"
                                })
                except Exception:
                    continue

        return results

    def _search_class_definitions(self, class_name: str, pattern: str) -> List[Dict]:
        """Search for class definitions."""
        results = []
        regex = re.compile(rf'^\s*class\s+{re.escape(class_name)}\s*[\(:]')

        for file_path in self.repo_path.rglob(pattern):
            if file_path.is_file():
                try:
                    with open(file_path, 'r') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append({
                                    "file": str(file_path.relative_to(self.repo_path)),
                                    "line": line_num,
                                    "content": line.strip(),
                                    "type": "class_definition"
                                })
                except Exception:
                    continue

        return results

    def _search_usage(self, identifier: str, pattern: str) -> List[Dict]:
        """Search for variable/function usage."""
        results = []
        regex = re.compile(rf'\b{re.escape(identifier)}\b')

        for file_path in self.repo_path.rglob(pattern):
            if file_path.is_file():
                try:
                    with open(file_path, 'r') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append({
                                    "file": str(file_path.relative_to(self.repo_path)),
                                    "line": line_num,
                                    "content": line.strip(),
                                    "type": "usage"
                                })
                                if len(results) >= 50:  # Limit results
                                    return results
                except Exception:
                    continue

        return results

    def _search_pattern(self, pattern_str: str, file_pattern: str) -> List[Dict]:
        """Search for a general pattern."""
        results = []

        try:
            regex = re.compile(pattern_str)
        except re.error:
            # If not a valid regex, search as literal string
            regex = re.compile(re.escape(pattern_str))

        for file_path in self.repo_path.rglob(file_pattern):
            if file_path.is_file():
                try:
                    with open(file_path, 'r') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append({
                                    "file": str(file_path.relative_to(self.repo_path)),
                                    "line": line_num,
                                    "content": line.strip(),
                                    "type": "pattern_match"
                                })
                                if len(results) >= 50:
                                    return results
                except Exception:
                    continue

        return results

    def _format_results(self, results: List[Dict], query: str) -> str:
        """Format search results."""
        if not results:
            return f"No results found for: {query}"

        output = [f"Found {len(results)} results for '{query}':\n"]

        # Group by file
        by_file = {}
        for result in results:
            file_name = result["file"]
            by_file.setdefault(file_name, []).append(result)

        for file_name, matches in list(by_file.items())[:10]:  # Limit to 10 files
            output.append(f"\n{file_name}:")
            for match in matches[:5]:  # Limit to 5 matches per file
                output.append(f"  Line {match['line']}: {match['content']}")

        if len(results) > 50:
            output.append(f"\n... and {len(results) - 50} more results")

        return "\n".join(output)

    async def _arun(self, query: str) -> str:
        """Async version."""
        return self._run(query)
