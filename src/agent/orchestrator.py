"""Main agent orchestrator using LangChain and Claude."""

import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool
from langchain.prompts import PromptTemplate

from .prompts import SYSTEM_PROMPT, REACT_PROMPT_TEMPLATE
from ..tools.ast_analyzer import ASTAnalyzerTool
from ..tools.static_analyzer import StaticAnalyzerTool
from ..tools.code_search import CodeSearchTool
from ..tools.git_tools import GitAnalyzerTool


class CodeAnalysisAgent:
    """Main code analysis agent using LangChain ReAct pattern."""

    def __init__(self, repo_path: str, model: str = None, verbose: bool = True):
        """Initialize the code analysis agent.

        Args:
            repo_path: Path to the code repository to analyze
            model: Claude model to use (default: from env or claude-sonnet-4-5)
            verbose: Whether to show reasoning steps
        """
        load_dotenv()

        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

        # Initialize Claude LLM
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        model_name = model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")

        self.llm = ChatAnthropic(
            model=model_name,
            anthropic_api_key=api_key,
            temperature=0,
            max_tokens=4096
        )

        # Initialize tools
        self.tools = self._initialize_tools()

        # Create ReAct agent
        self.agent = self._create_agent()

        # Create agent executor
        max_iterations = int(os.getenv("MAX_ITERATIONS", "15"))
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=verbose,
            max_iterations=max_iterations,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

    def _initialize_tools(self) -> List[Tool]:
        """Initialize all analysis tools."""
        repo_path_str = str(self.repo_path)

        # Create tool instances
        ast_tool = ASTAnalyzerTool(repo_path=repo_path_str)
        static_tool = StaticAnalyzerTool(repo_path=repo_path_str)
        search_tool = CodeSearchTool(repo_path=repo_path_str)
        git_tool = GitAnalyzerTool(repo_path=repo_path_str)

        return [ast_tool, static_tool, search_tool, git_tool]

    def _create_agent(self):
        """Create the ReAct agent with custom prompt."""
        # Create the prompt template
        prompt = PromptTemplate(
            template=SYSTEM_PROMPT + "\n\n" + REACT_PROMPT_TEMPLATE,
            input_variables=["repo_path", "target", "analysis_type", "agent_scratchpad"],
            partial_variables={
                "tools": "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools]),
                "tool_names": ", ".join([tool.name for tool in self.tools])
            }
        )

        # Create ReAct agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        return agent

    def analyze(
        self,
        target: str = ".",
        analysis_type: str = "comprehensive"
    ) -> dict:
        """Run code analysis on the target.

        Args:
            target: File or directory to analyze (relative to repo_path)
            analysis_type: Type of analysis to perform
                - bug_detection: Find bugs and logical errors
                - security_scan: Security vulnerability scan
                - code_quality: Code quality and maintainability
                - comprehensive: All of the above

        Returns:
            dict with 'output' and 'intermediate_steps'
        """
        # Prepare input for agent
        agent_input = {
            "repo_path": str(self.repo_path),
            "target": target,
            "analysis_type": analysis_type,
            "agent_scratchpad": ""
        }

        # Run the agent
        result = self.agent_executor.invoke(agent_input)

        return {
            "output": result["output"],
            "intermediate_steps": result.get("intermediate_steps", []),
            "analysis_type": analysis_type,
            "target": target
        }

    def quick_scan(self, file_path: str) -> dict:
        """Quick scan of a single file for common issues.

        Args:
            file_path: Path to file relative to repo_path

        Returns:
            Analysis results
        """
        return self.analyze(target=file_path, analysis_type="bug_detection")

    def security_audit(self, target: str = ".") -> dict:
        """Run security-focused analysis.

        Args:
            target: File or directory to analyze

        Returns:
            Security analysis results
        """
        return self.analyze(target=target, analysis_type="security_scan")

    def get_tool_by_name(self, tool_name: str) -> Optional[Tool]:
        """Get a specific tool by name."""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None

    def list_tools(self) -> List[str]:
        """List all available tools."""
        return [tool.name for tool in self.tools]


def create_agent(repo_path: str, **kwargs) -> CodeAnalysisAgent:
    """Factory function to create a CodeAnalysisAgent.

    Args:
        repo_path: Path to repository
        **kwargs: Additional arguments for CodeAnalysisAgent

    Returns:
        Configured CodeAnalysisAgent instance
    """
    return CodeAnalysisAgent(repo_path=repo_path, **kwargs)
