"""Multi-language security scanner using Semgrep and Trivy."""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from langchain.tools import BaseTool

from .utils.security_utils import (
    parse_semgrep_severity,
    parse_trivy_severity,
    format_vulnerability_output,
    aggregate_vulnerabilities,
    extract_cve_from_text
)


class SecurityScannerTool(BaseTool):
    """Multi-language security scanner using universal tools (Semgrep + Trivy).

    Supports 30+ programming languages including:
    - Python, JavaScript/TypeScript, Java, Go, Rust, Ruby, PHP, C/C++
    - Scans for security vulnerabilities, code patterns, and dependency issues
    - Works across all major dependency ecosystems
    """

    name: str = "security_scanner"
    description: str = """Multi-language security scanner for code and dependencies.

    Operations:
    - scan_code: Run Semgrep on code files (supports 30+ languages)
    - scan_dependencies: Run Trivy on dependencies (all ecosystems)
    - full_scan: Run both Semgrep and Trivy
    - check_tool_status: Check if security tools are installed

    Input format (JSON string):
    {
        "operation": "scan_code|scan_dependencies|full_scan|check_tool_status",
        "path": "path/to/scan",  // Optional, defaults to repo root
        "language": "python|javascript|java|go|rust|auto",  // Optional for scan_code
        "severity": "critical|high|medium|low",  // Optional minimum severity filter
    }

    Supports ecosystems: Python (PyPI), JavaScript (npm/yarn), Java (Maven/Gradle),
    Go (go.mod), Rust (Cargo), Ruby (Bundler), PHP (Composer), .NET (NuGet), C/C++
    """

    repo_path: str

    def _run(self, tool_input: str) -> str:
        """Run security scanner."""
        try:
            params = json.loads(tool_input)
            operation = params.get("operation")

            if operation == "check_tool_status":
                return self._check_tool_status()
            elif operation == "scan_code":
                return self._scan_code(params)
            elif operation == "scan_dependencies":
                return self._scan_dependencies(params)
            elif operation == "full_scan":
                return self._full_scan(params)
            else:
                return json.dumps({
                    "error": f"Unknown operation: {operation}",
                    "available_operations": [
                        "check_tool_status",
                        "scan_code",
                        "scan_dependencies",
                        "full_scan"
                    ]
                })

        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON input"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def _check_tool_status(self) -> str:
        """Check if security tools are installed."""
        status = {}

        # Check Semgrep
        semgrep_path = shutil.which("semgrep")
        status["semgrep"] = {
            "installed": semgrep_path is not None,
            "path": semgrep_path,
            "install_command": "pip install semgrep"
        }

        # Check Trivy
        trivy_path = shutil.which("trivy")
        status["trivy"] = {
            "installed": trivy_path is not None,
            "path": trivy_path,
            "install_command": "brew install trivy (macOS) or see https://aquasecurity.github.io/trivy/"
        }

        # Overall status
        all_installed = status["semgrep"]["installed"] and status["trivy"]["installed"]
        status["ready"] = all_installed

        if not all_installed:
            status["message"] = "Some security tools are missing. Install them for full functionality."

        return json.dumps(status, indent=2)

    def _scan_code(self, params: Dict) -> str:
        """Scan code with Semgrep.

        Args:
            params: Parameters including path, language, severity

        Returns:
            JSON string with scan results
        """
        # Check if Semgrep is installed
        if not shutil.which("semgrep"):
            return json.dumps({
                "error": "Semgrep not installed",
                "install_command": "pip install semgrep",
                "documentation": "https://semgrep.dev/docs/getting-started/"
            })

        scan_path = params.get("path", ".")
        language = params.get("language", "auto")
        min_severity = params.get("severity", "low").upper()

        # Build full path
        full_path = Path(self.repo_path) / scan_path
        if not full_path.exists():
            return json.dumps({"error": f"Path does not exist: {scan_path}"})

        try:
            # Run Semgrep with security rules
            cmd = [
                "semgrep",
                "--config=auto",  # Use Semgrep Registry rules
                "--json",
                "--severity", min_severity,
                str(full_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=self.repo_path
            )

            # Parse Semgrep output
            if result.returncode != 0 and not result.stdout:
                return json.dumps({
                    "error": "Semgrep scan failed",
                    "stderr": result.stderr[:1000]
                })

            semgrep_output = json.loads(result.stdout)
            vulnerabilities = self._parse_semgrep_output(semgrep_output)

            # Generate summary
            stats = aggregate_vulnerabilities(vulnerabilities)

            return json.dumps({
                "tool": "Semgrep",
                "scan_type": "code_analysis",
                "path": scan_path,
                "language": language,
                "vulnerabilities": vulnerabilities,
                "statistics": stats,
                "scan_info": {
                    "rules_matched": len(vulnerabilities),
                    "files_scanned": len(set(v.get("file_path") for v in vulnerabilities))
                }
            }, indent=2)

        except subprocess.TimeoutExpired:
            return json.dumps({"error": "Semgrep scan timed out (>5 minutes)"})
        except Exception as e:
            return json.dumps({"error": f"Semgrep scan error: {str(e)}"})

    def _parse_semgrep_output(self, semgrep_data: Dict) -> List[Dict]:
        """Parse Semgrep JSON output into standardized format."""
        vulnerabilities = []

        for result in semgrep_data.get("results", []):
            # Extract CVE/CWE from message or metadata
            message = result.get("extra", {}).get("message", "")
            cves = extract_cve_from_text(message)

            # Get CWE from metadata
            cwe_ids = result.get("extra", {}).get("metadata", {}).get("cwe", [])
            cwe_id = cwe_ids[0] if cwe_ids else None

            vuln = format_vulnerability_output(
                vuln_id=result.get("check_id", "unknown"),
                severity=parse_semgrep_severity(
                    result.get("extra", {}).get("severity", "INFO")
                ),
                title=result.get("check_id", "").split(".")[-1].replace("-", " ").title(),
                description=message,
                file_path=result.get("path", ""),
                line_number=result.get("start", {}).get("line"),
                cwe_id=cwe_id,
                cve_id=cves[0] if cves else None,
                references=[
                    result.get("extra", {}).get("metadata", {}).get("source", "")
                ]
            )

            vulnerabilities.append(vuln)

        return vulnerabilities

    def _scan_dependencies(self, params: Dict) -> str:
        """Scan dependencies with Trivy.

        Args:
            params: Parameters including path

        Returns:
            JSON string with scan results
        """
        # Check if Trivy is installed
        if not shutil.which("trivy"):
            return json.dumps({
                "error": "Trivy not installed",
                "install_command": "brew install trivy (macOS)",
                "documentation": "https://aquasecurity.github.io/trivy/"
            })

        scan_path = params.get("path", ".")
        min_severity = params.get("severity", "LOW").upper()

        # Build full path
        full_path = Path(self.repo_path) / scan_path
        if not full_path.exists():
            full_path = Path(self.repo_path)

        try:
            # Run Trivy filesystem scan
            cmd = [
                "trivy",
                "fs",
                "--format", "json",
                "--severity", f"{min_severity},MEDIUM,HIGH,CRITICAL",
                "--scanners", "vuln",
                str(full_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.repo_path
            )

            if result.returncode != 0 and not result.stdout:
                return json.dumps({
                    "error": "Trivy scan failed",
                    "stderr": result.stderr[:1000]
                })

            trivy_output = json.loads(result.stdout)
            vulnerabilities = self._parse_trivy_output(trivy_output)

            # Generate summary
            stats = aggregate_vulnerabilities(vulnerabilities)

            # Detect ecosystems
            ecosystems = self._detect_ecosystems(full_path)

            return json.dumps({
                "tool": "Trivy",
                "scan_type": "dependency_analysis",
                "path": scan_path,
                "ecosystems_detected": ecosystems,
                "vulnerabilities": vulnerabilities,
                "statistics": stats,
                "scan_info": {
                    "packages_scanned": len(set(v.get("title") for v in vulnerabilities)),
                    "unique_cves": len(stats.get("unique_cves", []))
                }
            }, indent=2)

        except subprocess.TimeoutExpired:
            return json.dumps({"error": "Trivy scan timed out (>5 minutes)"})
        except Exception as e:
            return json.dumps({"error": f"Trivy scan error: {str(e)}"})

    def _parse_trivy_output(self, trivy_data: Dict) -> List[Dict]:
        """Parse Trivy JSON output into standardized format."""
        vulnerabilities = []

        for result in trivy_data.get("Results", []):
            target = result.get("Target", "")

            for vuln_data in result.get("Vulnerabilities", []):
                vuln = format_vulnerability_output(
                    vuln_id=vuln_data.get("VulnerabilityID", "unknown"),
                    severity=parse_trivy_severity(vuln_data.get("Severity", "UNKNOWN")),
                    title=f"{vuln_data.get('PkgName', 'unknown')} - {vuln_data.get('VulnerabilityID', '')}",
                    description=vuln_data.get("Title", vuln_data.get("Description", ""))[:500],
                    file_path=target,
                    cve_id=vuln_data.get("VulnerabilityID") if vuln_data.get("VulnerabilityID", "").startswith("CVE") else None,
                    cvss_score=self._extract_cvss_score(vuln_data),
                    recommendation=f"Update {vuln_data.get('PkgName')} to version {vuln_data.get('FixedVersion', 'latest')}",
                    references=vuln_data.get("References", [])[:3]
                )

                vulnerabilities.append(vuln)

        return vulnerabilities

    def _extract_cvss_score(self, vuln_data: Dict) -> Optional[float]:
        """Extract CVSS score from Trivy vulnerability data."""
        cvss = vuln_data.get("CVSS", {})

        # Try different CVSS versions
        for version in ["nvd", "redhat", "ghsa"]:
            if version in cvss and "V3Score" in cvss[version]:
                return cvss[version]["V3Score"]

        return None

    def _detect_ecosystems(self, path: Path) -> List[str]:
        """Detect dependency ecosystems in the path."""
        ecosystems = []

        ecosystem_files = {
            "Python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
            "JavaScript": ["package.json", "yarn.lock", "package-lock.json"],
            "Java": ["pom.xml", "build.gradle", "gradle.lockfile"],
            "Go": ["go.mod", "go.sum"],
            "Rust": ["Cargo.toml", "Cargo.lock"],
            "Ruby": ["Gemfile", "Gemfile.lock"],
            "PHP": ["composer.json", "composer.lock"],
            ".NET": ["packages.config", "packages.lock.json"]
        }

        for ecosystem, files in ecosystem_files.items():
            for file_name in files:
                if (path / file_name).exists() or list(path.rglob(file_name)):
                    ecosystems.append(ecosystem)
                    break

        return ecosystems

    def _full_scan(self, params: Dict) -> str:
        """Run both code and dependency scans."""
        results = {
            "scan_type": "full_security_scan",
            "code_scan": None,
            "dependency_scan": None,
            "combined_statistics": None
        }

        # Run code scan
        code_result = self._scan_code(params)
        try:
            results["code_scan"] = json.loads(code_result)
        except:
            results["code_scan"] = {"error": "Code scan failed"}

        # Run dependency scan
        dep_result = self._scan_dependencies(params)
        try:
            results["dependency_scan"] = json.loads(dep_result)
        except:
            results["dependency_scan"] = {"error": "Dependency scan failed"}

        # Combine statistics
        code_vulns = results["code_scan"].get("vulnerabilities", []) if isinstance(results["code_scan"], dict) else []
        dep_vulns = results["dependency_scan"].get("vulnerabilities", []) if isinstance(results["dependency_scan"], dict) else []

        all_vulns = code_vulns + dep_vulns
        results["combined_statistics"] = aggregate_vulnerabilities(all_vulns)

        return json.dumps(results, indent=2)
