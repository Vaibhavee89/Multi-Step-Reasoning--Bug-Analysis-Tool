"""Command-line interface for the Code Analysis Agent."""

import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.markdown import Markdown

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agent.orchestrator import CodeAnalysisAgent


console = Console()


def print_header():
    """Print welcome header."""
    header = """
    ╔═══════════════════════════════════════════════╗
    ║   Code Analysis & Debugging Agent             ║
    ║   Powered by LangChain + Claude               ║
    ╚═══════════════════════════════════════════════╝
    """
    console.print(header, style="bold cyan")


def print_analysis_result(result: dict):
    """Print analysis results in a formatted way."""
    console.print("\n" + "="*60, style="bold")
    console.print("ANALYSIS RESULTS", style="bold green")
    console.print("="*60 + "\n", style="bold")

    # Print main output
    console.print(Panel(
        result["output"],
        title=f"Analysis: {result['analysis_type']}",
        border_style="green"
    ))

    # Print reasoning steps if verbose
    if result.get("intermediate_steps"):
        console.print("\n" + "─"*60, style="dim")
        console.print("REASONING TRACE", style="bold yellow")
        console.print("─"*60 + "\n", style="dim")

        for i, (action, observation) in enumerate(result["intermediate_steps"], 1):
            # Print action (tool call)
            console.print(f"\n[bold cyan]Step {i}: {action.tool}[/bold cyan]")
            console.print(f"[dim]Input: {action.tool_input}[/dim]")

            # Print observation (result)
            console.print(f"[yellow]Observation:[/yellow]")
            console.print(Panel(
                str(observation)[:500] + ("..." if len(str(observation)) > 500 else ""),
                border_style="yellow"
            ))


def analyze_command(args):
    """Handle analyze command."""
    console.print(f"\n[cyan]Initializing agent for repository:[/cyan] {args.repo_path}")

    try:
        agent = CodeAnalysisAgent(
            repo_path=args.repo_path,
            verbose=args.verbose
        )

        console.print(f"[cyan]Starting analysis...[/cyan]\n")

        result = agent.analyze(
            target=args.target,
            analysis_type=args.type
        )

        print_analysis_result(result)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return 1

    return 0


def quick_scan_command(args):
    """Handle quick-scan command."""
    console.print(f"\n[cyan]Quick scanning:[/cyan] {args.file}")

    try:
        agent = CodeAnalysisAgent(
            repo_path=args.repo_path,
            verbose=args.verbose
        )

        result = agent.quick_scan(args.file)

        print_analysis_result(result)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return 1

    return 0


def security_audit_command(args):
    """Handle security-audit command."""
    console.print(f"\n[cyan]Running security audit on:[/cyan] {args.target}")

    try:
        agent = CodeAnalysisAgent(
            repo_path=args.repo_path,
            verbose=args.verbose
        )

        result = agent.security_audit(args.target)

        print_analysis_result(result)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return 1

    return 0


def list_tools_command(args):
    """Handle list-tools command."""
    try:
        agent = CodeAnalysisAgent(repo_path=args.repo_path, verbose=False)

        table = Table(title="Available Analysis Tools")
        table.add_column("Tool Name", style="cyan")
        table.add_column("Description", style="green")

        for tool in agent.tools:
            table.add_row(tool.name, tool.description.split('\n')[0])

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return 1

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Code Analysis & Debugging Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--repo-path",
        type=str,
        default=".",
        help="Path to the code repository (default: current directory)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed reasoning steps"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze code for bugs and issues"
    )
    analyze_parser.add_argument(
        "--target",
        type=str,
        default=".",
        help="File or directory to analyze (default: entire repo)"
    )
    analyze_parser.add_argument(
        "--type",
        type=str,
        choices=["bug_detection", "security_scan", "code_quality", "comprehensive"],
        default="comprehensive",
        help="Type of analysis to perform"
    )

    # Quick scan command
    quick_parser = subparsers.add_parser(
        "quick-scan",
        help="Quick scan of a single file"
    )
    quick_parser.add_argument(
        "file",
        type=str,
        help="File to scan"
    )

    # Security audit command
    security_parser = subparsers.add_parser(
        "security-audit",
        help="Run security-focused analysis"
    )
    security_parser.add_argument(
        "--target",
        type=str,
        default=".",
        help="File or directory to audit"
    )

    # List tools command
    subparsers.add_parser(
        "list-tools",
        help="List available analysis tools"
    )

    args = parser.parse_args()

    # Print header
    print_header()

    # Execute command
    if not args.command:
        parser.print_help()
        return 0

    if args.command == "analyze":
        return analyze_command(args)
    elif args.command == "quick-scan":
        return quick_scan_command(args)
    elif args.command == "security-audit":
        return security_audit_command(args)
    elif args.command == "list-tools":
        return list_tools_command(args)


if __name__ == "__main__":
    sys.exit(main())
