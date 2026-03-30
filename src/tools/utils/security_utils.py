"""Security utilities for vulnerability analysis."""

import re
from typing import Optional, Dict, List
from enum import Enum


class Severity(str, Enum):
    """Standardized severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"
    UNKNOWN = "UNKNOWN"


# CWE category mapping
CWE_CATEGORIES = {
    # Injection
    "CWE-78": "Command Injection",
    "CWE-79": "Cross-Site Scripting (XSS)",
    "CWE-89": "SQL Injection",
    "CWE-94": "Code Injection",
    "CWE-95": "Eval Injection",
    "CWE-917": "Expression Language Injection",

    # Broken Authentication
    "CWE-287": "Authentication Bypass",
    "CWE-798": "Hardcoded Credentials",
    "CWE-259": "Hardcoded Password",
    "CWE-321": "Hardcoded Cryptographic Key",
    "CWE-522": "Insufficiently Protected Credentials",

    # Sensitive Data Exposure
    "CWE-200": "Information Disclosure",
    "CWE-327": "Broken Cryptography",
    "CWE-330": "Insufficient Randomness",
    "CWE-326": "Inadequate Encryption Strength",

    # XXE
    "CWE-611": "XML External Entity (XXE)",

    # Broken Access Control
    "CWE-22": "Path Traversal",
    "CWE-352": "CSRF",
    "CWE-434": "Unrestricted File Upload",
    "CWE-502": "Deserialization of Untrusted Data",

    # Security Misconfiguration
    "CWE-16": "Configuration",
    "CWE-209": "Information Exposure Through Error",
    "CWE-532": "Information Exposure Through Log Files",

    # Insecure Deserialization
    "CWE-502": "Deserialization",

    # Using Components with Known Vulnerabilities
    "CWE-1035": "Outdated Components",

    # Insufficient Logging
    "CWE-778": "Insufficient Logging",

    # Denial of Service
    "CWE-400": "Resource Exhaustion",
    "CWE-770": "Allocation Without Limits",

    # Buffer Overflow
    "CWE-120": "Buffer Overflow",
    "CWE-119": "Buffer Errors",

    # Race Conditions
    "CWE-362": "Race Condition",
}


def normalize_severity(severity: str) -> Severity:
    """Normalize severity from various formats.

    Args:
        severity: Severity string (e.g., "high", "CRITICAL", "error")

    Returns:
        Standardized Severity enum
    """
    if not severity:
        return Severity.UNKNOWN

    severity_upper = str(severity).upper().strip()

    # Direct match
    if severity_upper in ["CRITICAL", "CRIT"]:
        return Severity.CRITICAL
    elif severity_upper in ["HIGH", "ERROR", "E"]:
        return Severity.HIGH
    elif severity_upper in ["MEDIUM", "MED", "WARNING", "WARN", "W"]:
        return Severity.MEDIUM
    elif severity_upper in ["LOW", "INFO", "I", "NOTE"]:
        return Severity.LOW
    elif severity_upper in ["INFORMATIONAL", "NEGLIGIBLE"]:
        return Severity.INFO

    # CVSS score mapping
    try:
        score = float(severity)
        if score >= 9.0:
            return Severity.CRITICAL
        elif score >= 7.0:
            return Severity.HIGH
        elif score >= 4.0:
            return Severity.MEDIUM
        elif score > 0:
            return Severity.LOW
        else:
            return Severity.INFO
    except (ValueError, TypeError):
        pass

    return Severity.UNKNOWN


def extract_cve_from_text(text: str) -> List[str]:
    """Extract CVE IDs from text.

    Args:
        text: Text to search

    Returns:
        List of CVE IDs found
    """
    if not text:
        return []

    # CVE pattern: CVE-YYYY-NNNN+ (4+ digits)
    pattern = r'CVE-\d{4}-\d{4,}'
    cves = re.findall(pattern, text, re.IGNORECASE)

    # Normalize to uppercase and deduplicate
    return list(set(cve.upper() for cve in cves))


def calculate_cvss_score(
    attack_vector: str = "NETWORK",
    attack_complexity: str = "LOW",
    privileges_required: str = "NONE",
    user_interaction: str = "NONE",
    scope: str = "UNCHANGED",
    confidentiality: str = "HIGH",
    integrity: str = "HIGH",
    availability: str = "HIGH"
) -> float:
    """Calculate CVSS 3.1 base score.

    Args:
        attack_vector: NETWORK, ADJACENT, LOCAL, PHYSICAL
        attack_complexity: LOW, HIGH
        privileges_required: NONE, LOW, HIGH
        user_interaction: NONE, REQUIRED
        scope: UNCHANGED, CHANGED
        confidentiality: NONE, LOW, HIGH
        integrity: NONE, LOW, HIGH
        availability: NONE, LOW, HIGH

    Returns:
        CVSS score (0.0-10.0)
    """
    # Simplified CVSS calculation (not exact but reasonable approximation)
    score = 0.0

    # Attack Vector (0-4 points)
    av_scores = {"NETWORK": 3.9, "ADJACENT": 2.8, "LOCAL": 1.8, "PHYSICAL": 0.6}
    score += av_scores.get(attack_vector.upper(), 2.0)

    # Attack Complexity (0-2 points)
    if attack_complexity.upper() == "LOW":
        score += 1.5
    else:
        score += 0.8

    # Privileges Required (0-2 points)
    pr_scores = {"NONE": 2.0, "LOW": 1.2, "HIGH": 0.5}
    score += pr_scores.get(privileges_required.upper(), 1.0)

    # User Interaction (0-1 point)
    if user_interaction.upper() == "NONE":
        score += 0.8

    # Impact (0-3 points for each CIA)
    impact_scores = {"HIGH": 0.9, "LOW": 0.3, "NONE": 0.0}
    score += impact_scores.get(confidentiality.upper(), 0.5)
    score += impact_scores.get(integrity.upper(), 0.5)
    score += impact_scores.get(availability.upper(), 0.5)

    # Normalize to 0-10 range
    score = min(10.0, score)

    return round(score, 1)


def map_cwe_to_category(cwe_id: str) -> str:
    """Map CWE ID to category.

    Args:
        cwe_id: CWE identifier (e.g., "CWE-78" or "78")

    Returns:
        Category description
    """
    if not cwe_id:
        return "Unknown"

    # Normalize CWE format
    if not cwe_id.startswith("CWE-"):
        cwe_id = f"CWE-{cwe_id}"

    return CWE_CATEGORIES.get(cwe_id, "Other")


def parse_semgrep_severity(semgrep_severity: str) -> Severity:
    """Parse Semgrep-specific severity format.

    Args:
        semgrep_severity: Semgrep severity (ERROR, WARNING, INFO)

    Returns:
        Standardized Severity
    """
    mapping = {
        "ERROR": Severity.HIGH,
        "WARNING": Severity.MEDIUM,
        "INFO": Severity.LOW,
    }
    return mapping.get(semgrep_severity.upper(), Severity.UNKNOWN)


def parse_trivy_severity(trivy_severity: str) -> Severity:
    """Parse Trivy-specific severity format.

    Args:
        trivy_severity: Trivy severity

    Returns:
        Standardized Severity
    """
    return normalize_severity(trivy_severity)


def format_vulnerability_output(
    vuln_id: str,
    severity: Severity,
    title: str,
    description: str,
    file_path: Optional[str] = None,
    line_number: Optional[int] = None,
    cwe_id: Optional[str] = None,
    cve_id: Optional[str] = None,
    cvss_score: Optional[float] = None,
    recommendation: Optional[str] = None,
    references: Optional[List[str]] = None
) -> Dict:
    """Format vulnerability finding into standardized structure.

    Returns:
        Standardized vulnerability dict
    """
    result = {
        "vulnerability_id": vuln_id,
        "severity": severity.value,
        "title": title,
        "description": description,
    }

    if file_path:
        result["file_path"] = file_path
    if line_number:
        result["line_number"] = line_number
    if cwe_id:
        result["cwe_id"] = cwe_id
        result["cwe_category"] = map_cwe_to_category(cwe_id)
    if cve_id:
        result["cve_id"] = cve_id
    if cvss_score:
        result["cvss_score"] = cvss_score
    if recommendation:
        result["recommendation"] = recommendation
    if references:
        result["references"] = references

    return result


def aggregate_vulnerabilities(vulnerabilities: List[Dict]) -> Dict:
    """Aggregate vulnerability statistics.

    Args:
        vulnerabilities: List of vulnerability dicts

    Returns:
        Statistics summary
    """
    if not vulnerabilities:
        return {
            "total": 0,
            "by_severity": {},
            "by_category": {},
            "unique_cves": [],
            "unique_cwes": []
        }

    severity_counts = {}
    category_counts = {}
    cves = set()
    cwes = set()

    for vuln in vulnerabilities:
        # Count by severity
        severity = vuln.get("severity", "UNKNOWN")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Count by category
        category = vuln.get("cwe_category", "Other")
        category_counts[category] = category_counts.get(category, 0) + 1

        # Collect CVEs and CWEs
        if "cve_id" in vuln:
            cves.add(vuln["cve_id"])
        if "cwe_id" in vuln:
            cwes.add(vuln["cwe_id"])

    return {
        "total": len(vulnerabilities),
        "by_severity": severity_counts,
        "by_category": category_counts,
        "unique_cves": sorted(list(cves)),
        "unique_cwes": sorted(list(cwes))
    }
