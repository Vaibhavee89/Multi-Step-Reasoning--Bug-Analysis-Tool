"""Tests for the Code Analysis Agent."""

import pytest
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.orchestrator import CodeAnalysisAgent
from src.tools.ast_analyzer import ASTAnalyzerTool


class TestCodeAnalysisAgent:
    """Test suite for CodeAnalysisAgent."""

    @pytest.fixture
    def test_repo_path(self):
        """Fixture providing path to test repository."""
        return Path(__file__).parent.parent / "data" / "test_repos"

    @pytest.fixture
    def agent(self, test_repo_path):
        """Fixture providing a configured agent."""
        return CodeAnalysisAgent(
            repo_path=str(test_repo_path),
            verbose=False
        )

    def test_agent_initialization(self, test_repo_path):
        """Test agent can be initialized."""
        agent = CodeAnalysisAgent(repo_path=str(test_repo_path))
        assert agent is not None
        assert len(agent.tools) > 0

    def test_list_tools(self, agent):
        """Test listing available tools."""
        tools = agent.list_tools()
        assert "ast_analyzer" in tools
        assert "static_analyzer" in tools
        assert "code_search" in tools
        assert "git_analyzer" in tools

    def test_get_tool_by_name(self, agent):
        """Test getting specific tool."""
        ast_tool = agent.get_tool_by_name("ast_analyzer")
        assert ast_tool is not None
        assert ast_tool.name == "ast_analyzer"

    def test_invalid_repo_path(self):
        """Test error handling for invalid repo path."""
        with pytest.raises(ValueError):
            CodeAnalysisAgent(repo_path="/nonexistent/path")


class TestASTAnalyzer:
    """Test suite for AST Analyzer tool."""

    @pytest.fixture
    def ast_tool(self):
        """Fixture providing AST analyzer."""
        test_repo = Path(__file__).parent.parent / "data" / "test_repos"
        return ASTAnalyzerTool(repo_path=str(test_repo))

    def test_analyze_functions(self, ast_tool):
        """Test function analysis."""
        result = ast_tool._run(
            '{"file_path": "buggy_code.py", "operation": "analyze_functions"}'
        )
        assert "divide_numbers" in result
        assert "process_user_input" in result
        assert "Too many parameters" in result  # Should detect complex_calculation

    def test_detect_patterns(self, ast_tool):
        """Test anti-pattern detection."""
        result = ast_tool._run(
            '{"file_path": "buggy_code.py", "operation": "detect_patterns"}'
        )
        assert "Bare except clause" in result
        assert "Mutable default argument" in result

    def test_analyze_imports(self, ast_tool):
        """Test import analysis."""
        result = ast_tool._run(
            '{"file_path": "buggy_code.py", "operation": "analyze_imports"}'
        )
        assert "sqlite3" in result
        assert "json" in result

    def test_invalid_file(self, ast_tool):
        """Test error handling for invalid file."""
        result = ast_tool._run(
            '{"file_path": "nonexistent.py", "operation": "analyze_functions"}'
        )
        assert "not found" in result.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
