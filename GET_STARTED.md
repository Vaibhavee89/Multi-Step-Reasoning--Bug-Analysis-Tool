# 🚀 Get Started with Your Code Analysis Agent

## What Was Built

A complete **Code Analysis & Debugging Agent** using:
- ✅ LangChain for agent orchestration
- ✅ Claude (Anthropic) for advanced reasoning
- ✅ Multi-step reasoning with ReAct pattern
- ✅ 4 specialized analysis tools
- ✅ CLI and Python API interfaces
- ✅ Sample buggy code for testing
- ✅ Comprehensive documentation

## Quick Start (5 Minutes)

### Option 1: Automated Installation

```bash
cd /Users/vaibhavee/project/BugAnalysisTool
./install.sh
```

This will:
- Create virtual environment
- Install all dependencies
- Set up configuration
- Run tests

### Option 2: Manual Installation

```bash
cd /Users/vaibhavee/project/BugAnalysisTool

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Get Your API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy it to your `.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Test It Out

### 1. Run the Demo

```bash
python examples/demo_analysis.py
```

This interactive demo shows:
- Bug detection
- Security scanning
- Tool usage
- Reasoning traces

### 2. Analyze Sample Code

```bash
# Quick scan
python src/ui/cli.py --repo-path data/test_repos quick-scan buggy_code.py

# With reasoning trace
python src/ui/cli.py --repo-path data/test_repos --verbose quick-scan buggy_code.py

# Security audit
python src/ui/cli.py --repo-path data/test_repos security-audit
```

### 3. Try the Jupyter Notebook

```bash
jupyter notebook examples/example_analysis.ipynb
```

## What Each Component Does

### 🧠 Agent (`src/agent/`)
- **orchestrator.py**: Main ReAct agent with LangChain
- **prompts.py**: System prompts for reasoning

### 🔧 Tools (`src/tools/`)
- **ast_analyzer.py**: Parse code structure, find anti-patterns
- **static_analyzer.py**: Run pylint/flake8
- **code_search.py**: Search for patterns and definitions
- **git_tools.py**: Analyze repository history

### 💻 Interfaces (`src/ui/`)
- **cli.py**: Command-line interface

### 📚 Examples
- **demo_analysis.py**: Interactive demo script
- **example_analysis.ipynb**: Jupyter notebook tutorial

### 🧪 Tests
- **test_agent.py**: Test suite

### 📝 Documentation
- **README.md**: Complete documentation
- **QUICKSTART.md**: Quick start guide
- **PROJECT_OVERVIEW.md**: Portfolio overview
- **GET_STARTED.md**: This file

## Example Usage

### Python API

```python
from src.agent.orchestrator import CodeAnalysisAgent

# Initialize
agent = CodeAnalysisAgent(repo_path="/path/to/your/project")

# Analyze for bugs
result = agent.analyze(target="myfile.py", analysis_type="bug_detection")
print(result["output"])

# Security audit
security = agent.security_audit(target=".")
print(security["output"])

# See reasoning steps
for step, (action, obs) in enumerate(result["intermediate_steps"]):
    print(f"Step {step}: Used {action.tool}")
```

### Command Line

```bash
# Help
python src/ui/cli.py --help

# Analyze entire repository
python src/ui/cli.py --repo-path /path/to/repo analyze

# Specific file
python src/ui/cli.py --repo-path /path/to/repo quick-scan file.py

# Different analysis types
python src/ui/cli.py --repo-path /path/to/repo analyze --type bug_detection
python src/ui/cli.py --repo-path /path/to/repo analyze --type security_scan
python src/ui/cli.py --repo-path /path/to/repo analyze --type code_quality

# Verbose mode (see reasoning)
python src/ui/cli.py --repo-path /path/to/repo --verbose analyze
```

## Understanding the Output

The agent provides:

```
[SEVERITY] TYPE: Issue description
  Location: file.py:line_number
  Description: What's wrong
  Impact: What could go wrong
  Fix: How to resolve it
  Reasoning: Why this is an issue
```

Example:
```
[HIGH] SECURITY: SQL Injection vulnerability
  Location: process_user_input (line 15)
  Description: User input concatenated directly into SQL query
  Impact: Attacker could read/modify database
  Fix: Use parameterized queries with cursor.execute(query, params)
  Reasoning: String formatting with user input allows SQL injection attacks
```

## Project Structure

```
BugAnalysisTool/
├── src/
│   ├── agent/           # Main agent logic
│   ├── tools/           # Analysis tools
│   ├── ui/              # User interfaces
│   ├── memory/          # Caching (future)
│   ├── parsers/         # Language parsers
│   └── reasoning/       # Reasoning patterns
├── data/
│   └── test_repos/      # Sample code
├── examples/            # Demos and tutorials
├── tests/               # Test suite
├── README.md            # Full documentation
├── QUICKSTART.md        # Quick start guide
├── PROJECT_OVERVIEW.md  # Portfolio overview
└── requirements.txt     # Dependencies
```

## Next Steps

### For Learning
1. ✅ Read PROJECT_OVERVIEW.md to understand architecture
2. ✅ Run demo_analysis.py to see it in action
3. ✅ Check out the Jupyter notebook for interactive tutorial
4. ✅ Read the code with comments

### For Development
1. ✅ Analyze your own code projects
2. ✅ Customize prompts in `src/agent/prompts.py`
3. ✅ Add new tools in `src/tools/`
4. ✅ Extend for other languages

### For Portfolio
1. ✅ Run demos and capture screenshots/videos
2. ✅ Analyze real projects and show results
3. ✅ Present the reasoning traces
4. ✅ Discuss architecture decisions

## Common Commands Reference

```bash
# Installation
./install.sh

# Activate environment
source venv/bin/activate

# Run demo
python examples/demo_analysis.py

# Run tests
pytest tests/ -v

# Analyze code
python src/ui/cli.py --repo-path /path analyze

# Quick scan
python src/ui/cli.py --repo-path /path quick-scan file.py

# Security audit
python src/ui/cli.py --repo-path /path security-audit

# List tools
python src/ui/cli.py --repo-path /path list-tools

# Verbose mode
python src/ui/cli.py --repo-path /path --verbose analyze
```

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Make sure `.env` file exists
- Check API key is correct
- API key should start with `sk-ant-`

### "Repository path does not exist"
- Use absolute paths
- Check the path is correct
- Make sure directory exists

### "Tool not installed"
- Run: `pip install pylint flake8`
- Or: `pip install -r requirements.txt`

### Import errors
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

## Resources

### Documentation
- README.md - Complete guide
- QUICKSTART.md - 5-minute start
- PROJECT_OVERVIEW.md - Portfolio details

### Code Examples
- examples/demo_analysis.py - Python demo
- examples/example_analysis.ipynb - Jupyter tutorial
- data/test_repos/buggy_code.py - Sample code

### Research Papers
- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [LangChain Docs](https://python.langchain.com/docs/modules/agents/)
- [Claude API Docs](https://docs.anthropic.com/)

## Need Help?

1. Check the README.md for detailed documentation
2. Look at examples/ for usage patterns
3. Review test cases in tests/
4. Check the code comments for implementation details

## What Makes This Special

✨ **Multi-Step Reasoning**: Not just running linters - actually thinks through problems

✨ **Tool Orchestration**: Autonomously selects and combines multiple tools

✨ **Transparent Reasoning**: Shows exactly how it analyzes code

✨ **Production Ready**: Clean architecture, tested, documented

✨ **Portfolio Worthy**: Demonstrates advanced AI/ML concepts

## Ready to Use!

Everything is set up and ready to go. Just:

1. Add your API key to `.env`
2. Run the demo: `python examples/demo_analysis.py`
3. Analyze your code!

**Happy analyzing!** 🎉🚀
