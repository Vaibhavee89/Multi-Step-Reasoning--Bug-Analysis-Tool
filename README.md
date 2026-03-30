# Code Analysis & Debugging Agent

A sophisticated multi-step reasoning agent for code analysis and bug detection, powered by **LangChain** and **Claude (Anthropic)**.

## 🎯 Features

- **Multi-Step Reasoning**: Uses ReAct (Reasoning + Acting) pattern for systematic code analysis
- **AST Parsing**: Deep code structure analysis using Abstract Syntax Trees
- **Static Analysis**: Integration with pylint, flake8, and other linters
- **Security Scanning**: Detects SQL injection, XSS, and other vulnerabilities
- **Git Integration**: Analyzes commit history to find bug-prone areas
- **Semantic Code Search**: Find patterns and definitions across your codebase
- **Reasoning Traces**: See exactly how the agent thinks through problems

## 🏗️ Architecture

```
User Query → LangChain Agent → Tool Selection → Multi-Step Analysis →
Reasoning Loop → Validation → Final Report
```

The agent uses a ReAct pattern:
1. **Thought**: Reasons about what to do next
2. **Action**: Selects and uses appropriate tools
3. **Observation**: Interprets results
4. **Repeat**: Continues until complete analysis

## 📦 Installation

### Prerequisites

- Python 3.9+
- Anthropic API key for Claude

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
cd BugAnalysisTool
pip install -r requirements.txt
```

3. Create `.env` file from example:
```bash
cp .env.example .env
```

4. Add your Anthropic API key to `.env`:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## 🚀 Quick Start

### Command Line Interface

```bash
# Analyze entire repository
python src/ui/cli.py --repo-path /path/to/repo analyze

# Quick scan a single file
python src/ui/cli.py --repo-path /path/to/repo quick-scan buggy_file.py

# Security audit
python src/ui/cli.py --repo-path /path/to/repo security-audit

# List available tools
python src/ui/cli.py --repo-path /path/to/repo list-tools

# Verbose mode (show reasoning steps)
python src/ui/cli.py --repo-path /path/to/repo --verbose analyze
```

### Python API

```python
from src.agent.orchestrator import CodeAnalysisAgent

# Initialize agent
agent = CodeAnalysisAgent(repo_path="/path/to/repo")

# Run comprehensive analysis
result = agent.analyze(
    target="src/module.py",
    analysis_type="comprehensive"
)

print(result["output"])

# Quick scan for bugs
result = agent.quick_scan("buggy_file.py")

# Security audit
result = agent.security_audit(target=".")
```

### Run Demo

```bash
python examples/demo_analysis.py
```

This will analyze the sample buggy code and demonstrate:
- Bug detection
- Security vulnerability scanning
- Direct tool usage
- Reasoning trace visualization

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| **ast_analyzer** | Parse Python code using AST, find functions, classes, detect anti-patterns |
| **static_analyzer** | Run pylint/flake8 for code quality and style issues |
| **code_search** | Semantic search for patterns, definitions, and usage |
| **git_analyzer** | Analyze commit history, find bug hotspots, track changes |

## 📊 Analysis Types

- `bug_detection`: Find logical errors and runtime bugs
- `security_scan`: Identify security vulnerabilities
- `code_quality`: Analyze maintainability and code smells
- `comprehensive`: All of the above (default)

## 🎓 How It Works

### ReAct Pattern Example

```
Thought: I need to understand the structure of this file
Action: ast_analyzer
Action Input: {"file_path": "module.py", "operation": "analyze_functions"}
Observation: Found 15 functions, 3 have high complexity...

Thought: High complexity functions may have bugs, let me check
Action: static_analyzer
Action Input: {"file_path": "module.py", "analyzer": "pylint"}
Observation: Found error in complex_function at line 45...

Thought: Let me search for where this function is called
Action: code_search
Action Input: {"query": "complex_function", "search_type": "usage"}
Observation: Function called in 8 locations...

Thought: I have enough information to provide recommendations
Final Answer: [Comprehensive bug report with fixes]
```

## 📁 Project Structure

```
BugAnalysisTool/
├── src/
│   ├── agent/
│   │   ├── orchestrator.py      # Main agent with ReAct pattern
│   │   └── prompts.py           # System prompts
│   ├── tools/
│   │   ├── ast_analyzer.py      # AST parsing
│   │   ├── static_analyzer.py   # Linting integration
│   │   ├── code_search.py       # Pattern search
│   │   └── git_tools.py         # Git analysis
│   └── ui/
│       └── cli.py               # Command-line interface
├── data/
│   └── test_repos/
│       └── buggy_code.py        # Sample buggy code
├── examples/
│   └── demo_analysis.py         # Demo script
├── tests/
│   └── test_agent.py            # Test suite
├── requirements.txt
└── README.md
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

Test with sample buggy code:

```bash
python src/ui/cli.py --repo-path data/test_repos quick-scan buggy_code.py
```

## 🎯 Use Cases

### 1. Code Review Automation
Automatically review pull requests for bugs and security issues

### 2. Legacy Code Analysis
Understand and improve old codebases with systematic analysis

### 3. Security Audits
Find SQL injection, XSS, and other vulnerabilities

### 4. Refactoring Guidance
Identify code smells and get refactoring suggestions

### 5. Learning Tool
See how AI reasons through code analysis problems

## 🔧 Configuration

Edit `.env` to customize:

```bash
# Model selection
CLAUDE_MODEL=claude-sonnet-4-5-20250929  # or claude-opus-4-6

# Agent behavior
MAX_ITERATIONS=15
VERBOSE=true

# Caching
ENABLE_CACHE=true
CACHE_PATH=./data/cache
```

## 📈 Performance Tips

1. **Start with single files**: Use `quick-scan` for faster results
2. **Specify analysis type**: Use `bug_detection` instead of `comprehensive` if you only need bug checks
3. **Cache results**: Enable caching for repeated analyses
4. **Use Sonnet**: Claude Sonnet is faster and cheaper than Opus for most tasks

## 🚧 Roadmap

- [ ] Support for JavaScript, Java, TypeScript
- [ ] Vector database for code embeddings
- [ ] Web dashboard with Streamlit
- [ ] Integration with GitHub Actions
- [ ] Performance profiling tools
- [ ] Automated fix generation
- [ ] Learning from past analyses

## 🤝 Contributing

This is a portfolio/learning project. Feel free to:
- Add new analysis tools
- Improve prompts and reasoning
- Add support for more languages
- Enhance the CLI interface

## 📝 License

MIT License - feel free to use for learning and portfolio purposes

## 🙏 Acknowledgments

- **LangChain**: Agent framework
- **Anthropic**: Claude AI models
- **Rich**: Beautiful terminal output

## 📧 Contact

Created as part of a multi-step reasoning portfolio project.

---

## 🎓 Learning Resources

Want to learn more about:
- **ReAct Pattern**: [Paper](https://arxiv.org/abs/2210.03629)
- **LangChain Agents**: [Docs](https://python.langchain.com/docs/modules/agents/)
- **Claude API**: [Documentation](https://docs.anthropic.com/)
- **AST in Python**: [Official Docs](https://docs.python.org/3/library/ast.html)

## 🐛 Known Issues

- Large repositories may take time to analyze
- Some git operations require valid git repository
- Static analysis tools (pylint, flake8) must be installed separately

## 💡 Tips for Best Results

1. **Be specific**: Target specific files or directories for faster analysis
2. **Use verbose mode**: Learn how the agent reasons by seeing all steps
3. **Start simple**: Try sample buggy code before analyzing your own projects
4. **Iterate**: Use the agent's findings to guide deeper analysis

---

**Built with ❤️ using LangChain and Claude**
