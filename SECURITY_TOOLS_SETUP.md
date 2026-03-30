# Multi-Language Security Vulnerability Tracking Setup

## Overview

Your Bug Analysis Tool now has comprehensive security vulnerability tracking across **all major tech stacks**, not just Python. The system uses universal security scanners and internet-enabled vulnerability databases.

## New Capabilities

### 🌐 Multi-Language Support
- **30+ Programming Languages**: Python, JavaScript, TypeScript, Java, Kotlin, Go, Rust, Ruby, PHP, C, C++, C#, and more
- **All Major Ecosystems**: PyPI, npm, Maven, Gradle, Go modules, Cargo, RubyGems, Composer, NuGet
- **Universal Scanners**: Semgrep (code patterns) + Trivy (dependencies)

### 🔒 Three New Security Tools

#### 1. **SecurityScannerTool** (Local Analysis)
- **Semgrep**: Multi-language static analysis for security vulnerabilities
  - SQL injection, XSS, command injection, hardcoded secrets
  - Works with 30+ languages out of the box
- **Trivy**: Universal dependency scanner
  - Scans all dependency files across all ecosystems
  - Container and filesystem scanning
- **Operations**: `scan_code`, `scan_dependencies`, `full_scan`, `check_tool_status`

#### 2. **VulnerabilityTrackerTool** (Internet-Enabled)
- **OSV.dev API**: Free, no API key required
  - Real-time CVE lookups across all ecosystems
  - Python, JavaScript, Java, Go, Rust, Ruby, PHP, .NET support
- **NVD API**: National Vulnerability Database
  - Detailed CVE information with CVSS scores
  - Optional API key for higher rate limits
- **Operations**: `check_package`, `check_cve`, `check_dependencies`, `search_vulnerabilities`, `batch_check`

#### 3. **TrendAnalyzerTool** (Internet-Enabled)
- **Security Trend Analysis**: Track emerging threats and recent disclosures
- **Multiple Sources**: PyPI RSS, GitHub Security Advisories, security feeds
- **Operations**: `get_security_news`, `analyze_trends`, `check_emerging_threats`, `get_vulnerable_packages`

## Installation

### Step 1: Install Python Dependencies

```bash
cd /Users/vaibhavee/project/BugAnalysisTool
pip install -r requirements.txt
```

New dependencies added:
- `requests==2.31.0` - HTTP client
- `beautifulsoup4==4.12.3` - Web scraping
- `lxml==5.1.0` - XML parsing
- `feedparser==6.0.11` - RSS feed parsing
- `cachetools==5.3.2` - Caching

### Step 2: Install Semgrep (Multi-Language Security Scanner)

```bash
# Using pip (recommended)
pip install semgrep

# Or using Homebrew (macOS)
brew install semgrep

# Verify installation
semgrep --version
```

### Step 3: Install Trivy (Universal Dependency Scanner)

```bash
# macOS
brew install trivy

# Linux
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy

# Verify installation
trivy --version
```

### Step 4: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and configure:
nano .env
```

**Required Configuration:**
```bash
# Your LLM API key (Claude or Groq)
ANTHROPIC_API_KEY=your_api_key_here

# Enable internet tools
ENABLE_INTERNET_TOOLS=true
```

**Optional but Recommended:**
```bash
# Get free NVD API key: https://nvd.nist.gov/developers/request-an-api-key
# Increases rate limit from 5 to 50 requests per 30 seconds
NVD_API_KEY=your_nvd_api_key_here

# Cache settings (default values shown)
VULNERABILITY_CACHE_TTL=3600  # 1 hour cache
MAX_API_RETRIES=3
```

### Step 5: Verify Installation

Run this verification script:

```bash
python - << 'EOF'
import sys
sys.path.insert(0, '/Users/vaibhavee/project/BugAnalysisTool')

from src.tools.security_scanner import SecurityScannerTool
import json

# Check if tools are installed
tool = SecurityScannerTool(repo_path='.')
result = tool._run('{"operation": "check_tool_status"}')
status = json.loads(result)

print("=== Security Tools Status ===")
print(f"Semgrep: {'✓ Installed' if status['semgrep']['installed'] else '✗ Not installed'}")
print(f"Trivy: {'✓ Installed' if status['trivy']['installed'] else '✗ Not installed'}")
print(f"Overall: {'✓ Ready' if status['ready'] else '✗ Install missing tools'}")

if not status['ready']:
    print("\nInstallation commands:")
    print(f"  Semgrep: {status['semgrep']['install_command']}")
    print(f"  Trivy: {status['trivy']['install_command']}")
EOF
```

## Usage Examples

### Example 1: Scan Python Code for Security Issues

```python
from src.agent.orchestrator import CodeAnalysisAgent

# Initialize agent
agent = CodeAnalysisAgent(
    repo_path="/path/to/your/project",
    verbose=True
)

# Run security audit
result = agent.security_audit(target=".")

print(result["output"])
```

### Example 2: Check Package Vulnerabilities (Any Ecosystem)

```python
from src.tools.vulnerability_tracker import VulnerabilityTrackerTool
import json

tool = VulnerabilityTrackerTool(repo_path=".")

# Check Python package
result = tool._run(json.dumps({
    "operation": "check_package",
    "package": "requests",
    "version": "2.0.0",
    "ecosystem": "PyPI"
}))

print(json.loads(result))

# Check JavaScript package
result = tool._run(json.dumps({
    "operation": "check_package",
    "package": "axios",
    "version": "0.18.0",
    "ecosystem": "npm"
}))

print(json.loads(result))
```

### Example 3: Scan All Dependencies in a Project

```python
from src.tools.security_scanner import SecurityScannerTool
import json

tool = SecurityScannerTool(repo_path="/path/to/project")

# Full scan (code + dependencies)
result = tool._run(json.dumps({
    "operation": "full_scan",
    "path": ".",
    "severity": "medium"
}))

data = json.loads(result)
print(f"Found {data['combined_statistics']['total']} vulnerabilities")
print(f"Critical: {data['combined_statistics']['by_severity'].get('CRITICAL', 0)}")
print(f"High: {data['combined_statistics']['by_severity'].get('HIGH', 0)}")
```

### Example 4: Track Security Trends

```python
from src.tools.trend_analyzer import TrendAnalyzerTool
import json

tool = TrendAnalyzerTool(repo_path=".")

# Get recent security news
result = tool._run(json.dumps({
    "operation": "analyze_trends",
    "days": 7,
    "ecosystem": "all"
}))

data = json.loads(result)
print(f"Total vulnerabilities last 7 days: {data['total_vulnerabilities']}")
print(f"Risk level: {data['risk_level']}")
print(f"Summary: {data['summary']}")
```

### Example 5: CLI Usage

```bash
# Navigate to project directory
cd /Users/vaibhavee/project/BugAnalysisTool

# Run security audit via CLI
python src/ui/cli.py \
  --repo-path /path/to/your/project \
  security-audit \
  --verbose

# The agent will automatically:
# 1. Detect languages and ecosystems in your project
# 2. Run Semgrep for code security analysis
# 3. Run Trivy for dependency vulnerabilities
# 4. Query OSV.dev/NVD for real-time CVE data
# 5. Analyze security trends
# 6. Generate comprehensive report
```

## Supported Ecosystems

| Language | Ecosystem | Dependency Files | Semgrep | Trivy | OSV.dev |
|----------|-----------|------------------|---------|-------|---------|
| Python | PyPI | requirements.txt, setup.py, pyproject.toml, Pipfile | ✓ | ✓ | ✓ |
| JavaScript | npm | package.json, package-lock.json, yarn.lock | ✓ | ✓ | ✓ |
| TypeScript | npm | package.json, package-lock.json | ✓ | ✓ | ✓ |
| Java | Maven | pom.xml | ✓ | ✓ | ✓ |
| Java | Gradle | build.gradle, gradle.lockfile | ✓ | ✓ | ✓ |
| Go | Go modules | go.mod, go.sum | ✓ | ✓ | ✓ |
| Rust | Cargo | Cargo.toml, Cargo.lock | ✓ | ✓ | ✓ |
| Ruby | RubyGems | Gemfile, Gemfile.lock | ✓ | ✓ | ✓ |
| PHP | Composer | composer.json, composer.lock | ✓ | ✓ | ✓ |
| C# | NuGet | *.csproj, packages.config | ✓ | ✓ | ✓ |
| C/C++ | - | Auto-detect from source | ✓ | ✓ | - |

Plus 20+ more languages supported by Semgrep!

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  CodeAnalysisAgent                       │
│                   (LangChain ReAct)                      │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Existing     │  │ Security     │  │ Internet     │
│ Tools        │  │ Scanner      │  │ Tools        │
├──────────────┤  ├──────────────┤  ├──────────────┤
│ • AST        │  │ • Semgrep    │  │ • OSV.dev    │
│ • Static     │  │ • Trivy      │  │ • NVD        │
│ • Search     │  │              │  │ • Trends     │
│ • Git        │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
      │                 │                 │
      └─────────────────┴─────────────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
        ┌───▼────┐            ┌────▼─────┐
        │ Local  │            │ Internet │
        │ Files  │            │ APIs     │
        └────────┘            └──────────┘
```

## Privacy & Security

### What Gets Sent to External APIs?
- ✓ **Package names and versions only** (e.g., "requests==2.0.0")
- ✓ **CVE identifiers** (e.g., "CVE-2023-12345")
- ✗ **NO source code** is ever sent to external services
- ✗ **NO file contents** are uploaded

### Caching
- All API responses are cached locally (default: 1 hour)
- Cache location: `~/.cache/bug_analysis_tool/`
- Reduces API calls and improves performance

### Rate Limiting
- OSV.dev: No rate limit (reasonable use)
- NVD without key: 5 requests per 30 seconds
- NVD with key: 50 requests per 30 seconds
- Built-in rate limiter prevents bans

## Troubleshooting

### Semgrep Not Found
```bash
# Make sure Semgrep is in PATH
which semgrep

# If not found, reinstall
pip install --upgrade semgrep
```

### Trivy Not Found
```bash
# Check installation
trivy --version

# macOS reinstall
brew reinstall trivy

# Linux reinstall - see https://aquasecurity.github.io/trivy/
```

### API Rate Limit Errors
- Get free NVD API key: https://nvd.nist.gov/developers/request-an-api-key
- Add to `.env`: `NVD_API_KEY=your_key`
- Increase cache TTL: `VULNERABILITY_CACHE_TTL=7200`

### Internet Tools Not Loading
```bash
# Check environment variable
echo $ENABLE_INTERNET_TOOLS

# Should be "true" - if not, update .env:
ENABLE_INTERNET_TOOLS=true
```

## Performance Tips

1. **Enable Caching**: Set `CACHE_VULNERABILITIES=true` (default)
2. **Increase Cache TTL**: Vulnerability data doesn't change frequently
   ```bash
   VULNERABILITY_CACHE_TTL=7200  # 2 hours
   ```
3. **Use NVD API Key**: 10x rate limit increase
4. **Run Scans in Parallel**: Tools are independent and can run concurrently
5. **Filter by Severity**: Focus on critical/high severity issues first

## Next Steps

1. ✓ Install dependencies: `pip install -r requirements.txt`
2. ✓ Install Semgrep: `pip install semgrep`
3. ✓ Install Trivy: `brew install trivy`
4. ✓ Configure `.env` file
5. ✓ Verify installation with test script
6. ✓ Run your first security audit!

## Support

- **Semgrep Docs**: https://semgrep.dev/docs/
- **Trivy Docs**: https://aquasecurity.github.io/trivy/
- **OSV.dev API**: https://osv.dev/docs/
- **NVD API**: https://nvd.nist.gov/developers

---

**🎉 Your Bug Analysis Tool now supports comprehensive security analysis across ALL major tech stacks!**
