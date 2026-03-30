"""Security trend analyzer using web scraping and RSS feeds."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from langchain.tools import BaseTool
import feedparser
from bs4 import BeautifulSoup

from .utils.http_utils import CacheManager, make_api_call
from .utils.security_utils import extract_cve_from_text, normalize_severity


class TrendAnalyzerTool(BaseTool):
    """Security trend analyzer for tracking emerging threats and vulnerabilities.

    Aggregates security information from:
    - PyPI vulnerability announcements
    - GitHub Security Advisories
    - Security news feeds
    - Recent CVE disclosures
    """

    name: str = "trend_analyzer"
    description: str = """Security trend analyzer for current threats and emerging vulnerabilities.

    Operations:
    - get_security_news: Fetch recent security announcements
    - analyze_trends: Generate security trend report
    - check_emerging_threats: Find zero-day and critical disclosures
    - get_vulnerable_packages: List recently disclosed vulnerable packages

    Input format (JSON string):
    {
        "operation": "get_security_news|analyze_trends|check_emerging_threats|get_vulnerable_packages",
        "days": 7,  // Number of days to look back (default: 7)
        "ecosystem": "all|python|javascript|java|go",  // Ecosystem filter (default: all)
        "severity": "critical|high",  // Minimum severity filter (default: high)
    }

    Use this tool to:
    - Stay informed about recent security disclosures
    - Identify trending vulnerable packages
    - Track emerging attack patterns
    - Monitor critical CVEs in your tech stack
    """

    repo_path: str

    # Security feeds
    FEEDS = {
        "pypi_vulns": "https://pypi.org/rss/vulnerabilities.xml",
        "github_advisories": "https://github.com/advisories?query=type%3Areviewed+ecosystem%3A",
        "cve_recent": "https://cve.mitre.org/data/downloads/allitems-cvrf-year-recent.xml",
    }

    def __init__(self, **kwargs):
        """Initialize trend analyzer."""
        super().__init__(**kwargs)

        # Long TTL cache for trend data (24 hours)
        cache_dir = Path.home() / ".cache" / "bug_analysis_tool" / "trends"
        self.cache_manager = CacheManager(ttl=86400, cache_dir=str(cache_dir))

    def _run(self, tool_input: str) -> str:
        """Run trend analyzer."""
        try:
            params = json.loads(tool_input)
            operation = params.get("operation")

            if operation == "get_security_news":
                return self._get_security_news(params)
            elif operation == "analyze_trends":
                return self._analyze_trends(params)
            elif operation == "check_emerging_threats":
                return self._check_emerging_threats(params)
            elif operation == "get_vulnerable_packages":
                return self._get_vulnerable_packages(params)
            else:
                return json.dumps({
                    "error": f"Unknown operation: {operation}",
                    "available_operations": [
                        "get_security_news",
                        "analyze_trends",
                        "check_emerging_threats",
                        "get_vulnerable_packages"
                    ]
                })

        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON input"})
        except Exception as e:
            return json.dumps({"error": f"Trend analyzer error: {str(e)}"})

    def _get_security_news(self, params: Dict) -> str:
        """Fetch recent security announcements."""
        days = params.get("days", 7)
        ecosystem = params.get("ecosystem", "all").lower()

        news_items = []

        # Fetch PyPI vulnerabilities
        if ecosystem in ["all", "python"]:
            pypi_news = self._fetch_pypi_vulnerabilities(days)
            news_items.extend(pypi_news)

        # Fetch GitHub advisories
        github_news = self._fetch_github_advisories(days, ecosystem)
        news_items.extend(github_news)

        # Sort by date
        news_items.sort(key=lambda x: x.get("date", ""), reverse=True)

        return json.dumps({
            "operation": "security_news",
            "days": days,
            "ecosystem": ecosystem,
            "total_items": len(news_items),
            "items": news_items[:50],  # Limit to 50 most recent
            "last_updated": datetime.utcnow().isoformat()
        }, indent=2)

    def _analyze_trends(self, params: Dict) -> str:
        """Generate security trend report."""
        days = params.get("days", 30)

        # Get all news items
        news_result = self._get_security_news({"days": days, "ecosystem": "all"})
        news_data = json.loads(news_result)
        items = news_data.get("items", [])

        if not items:
            return json.dumps({
                "error": "No security news found",
                "days": days
            })

        # Analyze trends
        severity_distribution = {}
        ecosystem_distribution = {}
        vulnerability_types = {}
        top_packages = {}

        for item in items:
            # Count by severity
            severity = item.get("severity", "UNKNOWN")
            severity_distribution[severity] = severity_distribution.get(severity, 0) + 1

            # Count by ecosystem
            eco = item.get("ecosystem", "unknown")
            ecosystem_distribution[eco] = ecosystem_distribution.get(eco, 0) + 1

            # Count vulnerability types (from CVE/CWE)
            cves = item.get("cves", [])
            for cve in cves:
                vulnerability_types[cve] = vulnerability_types.get(cve, 0) + 1

            # Track affected packages
            package = item.get("package", "unknown")
            top_packages[package] = top_packages.get(package, 0) + 1

        # Get top 10 packages
        top_packages_sorted = sorted(
            top_packages.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Calculate trends
        critical_count = severity_distribution.get("CRITICAL", 0)
        high_count = severity_distribution.get("HIGH", 0)
        total_count = len(items)

        risk_score = (critical_count * 10 + high_count * 5) / max(total_count, 1)

        return json.dumps({
            "operation": "trend_analysis",
            "period_days": days,
            "total_vulnerabilities": total_count,
            "severity_distribution": severity_distribution,
            "ecosystem_distribution": ecosystem_distribution,
            "top_vulnerable_packages": [
                {"package": pkg, "vulnerability_count": count}
                for pkg, count in top_packages_sorted
            ],
            "risk_score": round(risk_score, 2),
            "risk_level": self._calculate_risk_level(risk_score),
            "summary": self._generate_trend_summary(
                total_count, critical_count, high_count, top_packages_sorted
            ),
            "analyzed_at": datetime.utcnow().isoformat()
        }, indent=2)

    def _check_emerging_threats(self, params: Dict) -> str:
        """Find zero-day and critical disclosures."""
        days = params.get("days", 7)
        min_severity = params.get("severity", "high").upper()

        # Get recent news
        news_result = self._get_security_news({"days": days, "ecosystem": "all"})
        news_data = json.loads(news_result)
        items = news_data.get("items", [])

        # Filter for critical/high severity
        emerging_threats = []
        for item in items:
            severity = item.get("severity", "UNKNOWN")

            if min_severity == "CRITICAL" and severity != "CRITICAL":
                continue
            elif min_severity == "HIGH" and severity not in ["CRITICAL", "HIGH"]:
                continue

            # Check if recently published (last N days)
            threat = {
                "title": item.get("title", "Unknown"),
                "severity": severity,
                "package": item.get("package", "unknown"),
                "ecosystem": item.get("ecosystem", "unknown"),
                "cves": item.get("cves", []),
                "date": item.get("date", ""),
                "description": item.get("description", "")[:200],
                "threat_level": "EMERGING" if days <= 7 else "RECENT"
            }

            emerging_threats.append(threat)

        return json.dumps({
            "operation": "emerging_threats",
            "days": days,
            "min_severity": min_severity,
            "total_threats": len(emerging_threats),
            "threats": emerging_threats[:20],  # Top 20 most critical
            "checked_at": datetime.utcnow().isoformat()
        }, indent=2)

    def _get_vulnerable_packages(self, params: Dict) -> str:
        """List recently disclosed vulnerable packages."""
        days = params.get("days", 7)
        ecosystem = params.get("ecosystem", "all")

        # Get security news
        news_result = self._get_security_news({"days": days, "ecosystem": ecosystem})
        news_data = json.loads(news_result)
        items = news_data.get("items", [])

        # Extract unique packages
        packages_dict = {}

        for item in items:
            package = item.get("package", "unknown")
            eco = item.get("ecosystem", "unknown")
            key = f"{eco}:{package}"

            if key not in packages_dict:
                packages_dict[key] = {
                    "package": package,
                    "ecosystem": eco,
                    "vulnerability_count": 0,
                    "max_severity": "LOW",
                    "cves": [],
                    "latest_disclosure": item.get("date", "")
                }

            pkg_data = packages_dict[key]
            pkg_data["vulnerability_count"] += 1
            pkg_data["cves"].extend(item.get("cves", []))

            # Update max severity
            current_severity = item.get("severity", "LOW")
            if self._severity_rank(current_severity) > self._severity_rank(pkg_data["max_severity"]):
                pkg_data["max_severity"] = current_severity

        # Sort by severity and count
        packages_list = sorted(
            packages_dict.values(),
            key=lambda x: (self._severity_rank(x["max_severity"]), x["vulnerability_count"]),
            reverse=True
        )

        return json.dumps({
            "operation": "vulnerable_packages",
            "days": days,
            "ecosystem": ecosystem,
            "total_packages": len(packages_list),
            "packages": packages_list[:50],  # Top 50
            "generated_at": datetime.utcnow().isoformat()
        }, indent=2)

    def _fetch_pypi_vulnerabilities(self, days: int) -> List[Dict]:
        """Fetch PyPI vulnerability RSS feed."""
        cache_key = f"pypi_vulns:{days}"
        cached = self.cache_manager.get(cache_key)

        if cached:
            return cached

        try:
            feed = feedparser.parse(self.FEEDS["pypi_vulns"])
            items = []

            cutoff_date = datetime.utcnow() - timedelta(days=days)

            for entry in feed.entries[:50]:  # Limit to 50 entries
                # Parse date
                published = entry.get("published_parsed")
                if published:
                    pub_date = datetime(*published[:6])
                    if pub_date < cutoff_date:
                        continue
                else:
                    pub_date = datetime.utcnow()

                # Extract CVEs from description
                description = entry.get("summary", "")
                cves = extract_cve_from_text(entry.get("title", "") + " " + description)

                # Extract package name (usually in title)
                title = entry.get("title", "")
                package = title.split()[0] if title else "unknown"

                item = {
                    "title": title,
                    "package": package,
                    "ecosystem": "python",
                    "severity": "HIGH",  # Default for PyPI security advisories
                    "cves": cves,
                    "description": description[:200],
                    "link": entry.get("link", ""),
                    "date": pub_date.isoformat(),
                    "source": "PyPI"
                }

                items.append(item)

            self.cache_manager.set(cache_key, items)
            return items

        except Exception as e:
            return []

    def _fetch_github_advisories(self, days: int, ecosystem: str = "all") -> List[Dict]:
        """Fetch GitHub security advisories."""
        cache_key = f"github_advisories:{days}:{ecosystem}"
        cached = self.cache_manager.get(cache_key)

        if cached:
            return cached

        items = []

        # GitHub advisory API
        ecosystems_map = {
            "python": "pip",
            "javascript": "npm",
            "java": "maven",
            "ruby": "rubygems",
            "rust": "cargo",
            "go": "go",
            "php": "composer",
        }

        query_ecosystems = [ecosystems_map.get(ecosystem)] if ecosystem != "all" else ecosystems_map.values()

        try:
            for eco in query_ecosystems:
                # Use GitHub API (no auth needed for public data)
                url = "https://api.github.com/advisories"
                params = {
                    "ecosystem": eco,
                    "per_page": 20,
                    "sort": "published",
                    "direction": "desc"
                }

                result = make_api_call(
                    url=url,
                    method="GET",
                    params=params,
                    timeout=10,
                    cache_manager=self.cache_manager,
                    cache_key=f"github_api:{eco}"
                )

                if not result:
                    continue

                cutoff_date = datetime.utcnow() - timedelta(days=days)

                for advisory in result:
                    # Parse date
                    published = advisory.get("published_at", "")
                    if published:
                        pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
                        if pub_date < cutoff_date:
                            continue
                    else:
                        continue

                    # Extract package from first affected
                    affected = advisory.get("vulnerabilities", [])
                    package = affected[0].get("package", {}).get("name", "unknown") if affected else "unknown"

                    # Map severity
                    severity = normalize_severity(advisory.get("severity", "MODERATE"))

                    item = {
                        "title": advisory.get("summary", "Unknown"),
                        "package": package,
                        "ecosystem": eco,
                        "severity": severity.value,
                        "cves": [advisory.get("cve_id")] if advisory.get("cve_id") else [],
                        "description": advisory.get("description", "")[:200],
                        "link": advisory.get("html_url", ""),
                        "date": pub_date.isoformat(),
                        "source": "GitHub Advisory"
                    }

                    items.append(item)

            self.cache_manager.set(cache_key, items)
            return items

        except Exception as e:
            return []

    def _severity_rank(self, severity: str) -> int:
        """Get numeric rank for severity."""
        ranks = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
            "INFO": 0,
            "UNKNOWN": 0
        }
        return ranks.get(severity.upper(), 0)

    def _calculate_risk_level(self, risk_score: float) -> str:
        """Calculate risk level from score."""
        if risk_score >= 8:
            return "CRITICAL"
        elif risk_score >= 5:
            return "HIGH"
        elif risk_score >= 3:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_trend_summary(
        self,
        total: int,
        critical: int,
        high: int,
        top_packages: List
    ) -> str:
        """Generate human-readable trend summary."""
        summary_parts = [
            f"Found {total} security vulnerabilities in the analyzed period."
        ]

        if critical > 0:
            summary_parts.append(f"{critical} are CRITICAL severity requiring immediate attention.")

        if high > 0:
            summary_parts.append(f"{high} are HIGH severity.")

        if top_packages:
            top_pkg = top_packages[0][0]
            top_count = top_packages[0][1]
            summary_parts.append(f"Most affected package: {top_pkg} ({top_count} vulnerabilities).")

        return " ".join(summary_parts)
