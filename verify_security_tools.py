#!/usr/bin/env python3
"""Verification script for security tools installation."""

import sys
import json
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if required Python packages are installed."""
    print("=" * 60)
    print("CHECKING PYTHON DEPENDENCIES")
    print("=" * 60)

    required_packages = [
        "requests",
        "beautifulsoup4",
        "lxml",
        "feedparser",
        "cachetools",
        "langchain",
        "anthropic"
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("\n✓ All Python dependencies installed")
    return True

def check_security_tools():
    """Check if Semgrep and Trivy are installed."""
    print("\n" + "=" * 60)
    print("CHECKING SECURITY SCANNERS")
    print("=" * 60)

    try:
        from src.tools.security_scanner import SecurityScannerTool

        tool = SecurityScannerTool(repo_path=str(project_root))
        result = tool._run('{"operation": "check_tool_status"}')
        status = json.loads(result)

        print(f"\nSemgrep:")
        if status['semgrep']['installed']:
            print(f"  ✓ Installed at: {status['semgrep']['path']}")
        else:
            print(f"  ✗ Not installed")
            print(f"  Install: {status['semgrep']['install_command']}")

        print(f"\nTrivy:")
        if status['trivy']['installed']:
            print(f"  ✓ Installed at: {status['trivy']['path']}")
        else:
            print(f"  ✗ Not installed")
            print(f"  Install: {status['trivy']['install_command']}")

        if status['ready']:
            print("\n✓ All security scanners ready")
            return True
        else:
            print("\n⚠️  Some security scanners missing")
            return False

    except Exception as e:
        print(f"✗ Error checking tools: {e}")
        return False

def check_internet_tools():
    """Check if internet-enabled tools work."""
    print("\n" + "=" * 60)
    print("CHECKING INTERNET CONNECTIVITY")
    print("=" * 60)

    try:
        from src.tools.vulnerability_tracker import VulnerabilityTrackerTool

        tool = VulnerabilityTrackerTool(repo_path=str(project_root))

        # Try a simple OSV query
        print("\nTesting OSV.dev connectivity...")
        result = tool._run(json.dumps({
            "operation": "check_package",
            "package": "requests",
            "version": "2.0.0",
            "ecosystem": "PyPI"
        }))

        data = json.loads(result)

        if "error" in data:
            print(f"✗ OSV.dev query failed: {data['error']}")
            return False
        else:
            vuln_count = len(data.get("vulnerabilities", []))
            print(f"✓ OSV.dev working (found {vuln_count} known vulnerabilities for requests 2.0.0)")
            return True

    except Exception as e:
        print(f"✗ Error testing internet tools: {e}")
        return False

def check_agent_integration():
    """Check if agent properly loads all tools."""
    print("\n" + "=" * 60)
    print("CHECKING AGENT INTEGRATION")
    print("=" * 60)

    try:
        from src.agent.orchestrator import CodeAnalysisAgent

        # Check if agent initializes
        print("\nInitializing agent...")
        agent = CodeAnalysisAgent(repo_path=str(project_root), verbose=False)

        tools = agent.list_tools()
        print(f"\nLoaded {len(tools)} tools:")
        for tool_name in tools:
            print(f"  • {tool_name}")

        expected_tools = [
            "ast_analyzer",
            "static_analyzer",
            "code_search",
            "git_analyzer",
            "security_scanner",
            "vulnerability_tracker"
        ]

        # Check if trend_analyzer is loaded (optional based on ENABLE_INTERNET_TOOLS)
        if "trend_analyzer" in tools:
            expected_tools.append("trend_analyzer")
            print("\n✓ Internet tools enabled (trend_analyzer loaded)")
        else:
            print("\n⚠️  Internet tools disabled (set ENABLE_INTERNET_TOOLS=true in .env)")

        missing_tools = [t for t in expected_tools if t not in tools]
        if missing_tools:
            print(f"\n✗ Missing tools: {', '.join(missing_tools)}")
            return False

        print("\n✓ Agent integration successful")
        return True

    except Exception as e:
        print(f"✗ Error checking agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("BUG ANALYSIS TOOL - SECURITY FEATURES VERIFICATION")
    print("=" * 60)

    results = {
        "dependencies": check_dependencies(),
        "security_tools": check_security_tools(),
        "internet": check_internet_tools(),
        "agent": check_agent_integration()
    }

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check.replace('_', ' ').title()}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 All checks passed! Your security tools are ready.")
        print("\nNext steps:")
        print("  1. Run a security scan: python src/ui/cli.py --repo-path . security-audit")
        print("  2. Read the setup guide: SECURITY_TOOLS_SETUP.md")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please review the errors above.")
        print("\nSetup guide: SECURITY_TOOLS_SETUP.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())
