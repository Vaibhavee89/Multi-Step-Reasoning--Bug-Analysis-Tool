"""AST (Abstract Syntax Tree) analyzer tool for code parsing and analysis."""

import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
from langchain.tools import BaseTool
from pydantic import Field


class ASTAnalyzerTool(BaseTool):
    """Tool for analyzing Python code using AST parsing."""

    name: str = "ast_analyzer"
    description: str = """Analyzes Python code using Abstract Syntax Tree (AST) parsing.

    Use this tool to:
    - Parse Python files and extract structure
    - Find function and class definitions
    - Identify variable usage and assignments
    - Detect code patterns and anti-patterns
    - Analyze control flow

    Input should be a JSON string with:
    {
        "file_path": "path/to/file.py",
        "operation": "analyze_functions" | "find_variables" | "detect_patterns" | "analyze_imports"
    }
    """

    repo_path: Path = Field(default=None)

    def __init__(self, repo_path: str):
        super().__init__()
        self.repo_path = Path(repo_path)

    def _run(self, query: str) -> str:
        """Execute AST analysis."""
        import json

        try:
            params = json.loads(query)
            file_path = self.repo_path / params["file_path"]
            operation = params.get("operation", "analyze_functions")

            if not file_path.exists():
                return f"Error: File {file_path} not found"

            with open(file_path, 'r') as f:
                code = f.read()

            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                return f"Syntax Error in {file_path}: {e}"

            if operation == "analyze_functions":
                return self._analyze_functions(tree, file_path)
            elif operation == "find_variables":
                return self._find_variables(tree, file_path)
            elif operation == "detect_patterns":
                return self._detect_patterns(tree, file_path)
            elif operation == "analyze_imports":
                return self._analyze_imports(tree, file_path)
            else:
                return f"Unknown operation: {operation}"

        except json.JSONDecodeError:
            return "Error: Invalid JSON input"
        except Exception as e:
            return f"Error during AST analysis: {str(e)}"

    def _analyze_functions(self, tree: ast.AST, file_path: Path) -> str:
        """Analyze functions in the code."""
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "line": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": [d.id if isinstance(d, ast.Name) else "complex_decorator"
                                  for d in node.decorator_list],
                    "returns": ast.unparse(node.returns) if node.returns else None,
                    "docstring": ast.get_docstring(node),
                    "complexity": self._calculate_complexity(node)
                }

                # Check for common issues
                issues = []
                if len(node.args.args) > 5:
                    issues.append("Too many parameters (>5)")
                if func_info["complexity"] > 10:
                    issues.append(f"High complexity: {func_info['complexity']}")
                if not func_info["docstring"]:
                    issues.append("Missing docstring")

                func_info["issues"] = issues
                functions.append(func_info)

        result = f"Found {len(functions)} functions in {file_path.name}:\n\n"
        for func in functions:
            result += f"Function: {func['name']} (line {func['line']})\n"
            result += f"  Args: {func['args']}\n"
            result += f"  Complexity: {func['complexity']}\n"
            if func['issues']:
                result += f"  Issues: {', '.join(func['issues'])}\n"
            result += "\n"

        return result

    def _find_variables(self, tree: ast.AST, file_path: Path) -> str:
        """Find variable assignments and usage."""
        assignments = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assignments.append({
                            "variable": target.id,
                            "line": node.lineno,
                            "value_type": type(node.value).__name__
                        })

        result = f"Found {len(assignments)} variable assignments:\n\n"
        for assign in assignments[:20]:  # Limit output
            result += f"Line {assign['line']}: {assign['variable']} = <{assign['value_type']}>\n"

        return result

    def _detect_patterns(self, tree: ast.AST, file_path: Path) -> str:
        """Detect common code patterns and anti-patterns."""
        patterns = []

        for node in ast.walk(tree):
            # Detect bare except clauses
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    patterns.append({
                        "type": "ANTI-PATTERN",
                        "pattern": "Bare except clause",
                        "line": node.lineno,
                        "severity": "HIGH",
                        "description": "Catches all exceptions including system exits"
                    })

            # Detect mutable default arguments
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        patterns.append({
                            "type": "BUG",
                            "pattern": "Mutable default argument",
                            "line": node.lineno,
                            "severity": "MEDIUM",
                            "description": f"Function '{node.name}' has mutable default argument"
                        })

            # Detect unused variables (simple check)
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.startswith('_') and target.id != '_':
                        patterns.append({
                            "type": "CODE_SMELL",
                            "pattern": "Potentially unused variable",
                            "line": node.lineno,
                            "severity": "LOW",
                            "description": f"Variable '{target.id}' may be unused"
                        })

        if not patterns:
            return "No common anti-patterns detected."

        result = f"Detected {len(patterns)} potential issues:\n\n"
        for p in patterns:
            result += f"[{p['severity']}] {p['type']}: {p['pattern']}\n"
            result += f"  Line {p['line']}: {p['description']}\n\n"

        return result

    def _analyze_imports(self, tree: ast.AST, file_path: Path) -> str:
        """Analyze import statements."""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "type": "import",
                        "module": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append({
                        "type": "from_import",
                        "module": node.module,
                        "name": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno
                    })

        result = f"Found {len(imports)} imports:\n\n"
        for imp in imports:
            if imp["type"] == "import":
                result += f"Line {imp['line']}: import {imp['module']}\n"
            else:
                result += f"Line {imp['line']}: from {imp['module']} import {imp['name']}\n"

        return result

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    async def _arun(self, query: str) -> str:
        """Async version."""
        return self._run(query)
