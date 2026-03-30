"""Demo script showing how to use the Code Analysis Agent."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.orchestrator import CodeAnalysisAgent
from rich.console import Console
from rich.panel import Panel

console = Console()


def demo_basic_analysis():
    """Demo: Basic bug detection on sample code."""
    console.print("\n[bold cyan]Demo 1: Basic Bug Detection[/bold cyan]\n")

    # Create agent pointing to the test repository
    repo_path = Path(__file__).parent.parent / "data" / "test_repos"
    agent = CodeAnalysisAgent(repo_path=str(repo_path), verbose=True)

    # Analyze the buggy code file
    console.print("[yellow]Analyzing buggy_code.py for common issues...[/yellow]\n")

    result = agent.analyze(
        target="buggy_code.py",
        analysis_type="bug_detection"
    )

    console.print(Panel(
        result["output"],
        title="Analysis Results",
        border_style="green"
    ))


def demo_security_scan():
    """Demo: Security vulnerability detection."""
    console.print("\n[bold cyan]Demo 2: Security Vulnerability Scan[/bold cyan]\n")

    repo_path = Path(__file__).parent.parent / "data" / "test_repos"
    agent = CodeAnalysisAgent(repo_path=str(repo_path), verbose=True)

    console.print("[yellow]Scanning for security vulnerabilities...[/yellow]\n")

    result = agent.security_audit(target="buggy_code.py")

    console.print(Panel(
        result["output"],
        title="Security Analysis",
        border_style="red"
    ))


def demo_tool_usage():
    """Demo: Direct tool usage."""
    console.print("\n[bold cyan]Demo 3: Direct Tool Usage[/bold cyan]\n")

    repo_path = Path(__file__).parent.parent / "data" / "test_repos"
    agent = CodeAnalysisAgent(repo_path=str(repo_path), verbose=False)

    # Get AST analyzer tool
    ast_tool = agent.get_tool_by_name("ast_analyzer")

    if ast_tool:
        console.print("[yellow]Using AST analyzer directly...[/yellow]\n")

        # Analyze functions
        result = ast_tool._run(
            '{"file_path": "buggy_code.py", "operation": "analyze_functions"}'
        )

        console.print(Panel(result, title="AST Analysis", border_style="blue"))

        # Detect patterns
        console.print("\n[yellow]Detecting anti-patterns...[/yellow]\n")

        result = ast_tool._run(
            '{"file_path": "buggy_code.py", "operation": "detect_patterns"}'
        )

        console.print(Panel(result, title="Pattern Detection", border_style="blue"))


def demo_reasoning_trace():
    """Demo: Show the agent's reasoning process."""
    console.print("\n[bold cyan]Demo 4: Agent Reasoning Trace[/bold cyan]\n")

    repo_path = Path(__file__).parent.parent / "data" / "test_repos"
    agent = CodeAnalysisAgent(repo_path=str(repo_path), verbose=True)

    console.print("[yellow]Analyzing code with full reasoning trace...[/yellow]\n")

    result = agent.analyze(
        target="buggy_code.py",
        analysis_type="comprehensive"
    )

    # Show reasoning steps
    console.print("\n[bold]Reasoning Steps:[/bold]\n")
    for i, (action, observation) in enumerate(result["intermediate_steps"], 1):
        console.print(f"\n[cyan]Step {i}:[/cyan]")
        console.print(f"  Tool: {action.tool}")
        console.print(f"  Input: {action.tool_input}")
        console.print(f"  Result: {str(observation)[:200]}...")


if __name__ == "__main__":
    console.print("""
    ╔═══════════════════════════════════════════════╗
    ║   Code Analysis Agent - Demo Script           ║
    ║   Multi-Step Reasoning with LangChain         ║
    ╚═══════════════════════════════════════════════╝
    """, style="bold cyan")

    try:
        # Run demos
        demo_basic_analysis()

        input("\nPress Enter to continue to security scan demo...")
        demo_security_scan()

        input("\nPress Enter to continue to direct tool usage demo...")
        demo_tool_usage()

        input("\nPress Enter to see reasoning trace demo...")
        demo_reasoning_trace()

        console.print("\n[bold green]✓ All demos completed successfully![/bold green]\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        console.print("[dim]Make sure you have set ANTHROPIC_API_KEY in .env file[/dim]")
