# Quick Start Guide

Get started with the Code Analysis Agent in 5 minutes!

## Step 1: Installation

```bash
# Navigate to project directory
cd BugAnalysisTool

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure API Key

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Anthropic API key
# Get your key from: https://console.anthropic.com/
```

Edit `.env`:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Step 3: Run Your First Analysis

### Test with Sample Code

The project includes sample buggy code for testing:

```bash
# Analyze the sample buggy code
python src/ui/cli.py --repo-path data/test_repos quick-scan buggy_code.py
```

You should see the agent:
1. Parse the code using AST
2. Run static analysis
3. Detect security vulnerabilities
4. Report issues with severity levels

### Run Demo Script

```bash
# Interactive demo showing all features
python examples/demo_analysis.py
```

This demonstrates:
- Bug detection
- Security scanning
- Tool usage
- Reasoning traces

## Step 4: Analyze Your Own Code

```bash
# Analyze a specific file
python src/ui/cli.py --repo-path /path/to/your/project quick-scan your_file.py

# Analyze entire project
python src/ui/cli.py --repo-path /path/to/your/project analyze

# Security audit
python src/ui/cli.py --repo-path /path/to/your/project security-audit

# Verbose mode (see reasoning steps)
python src/ui/cli.py --repo-path /path/to/your/project --verbose analyze
```

## Step 5: Use Python API

Create `my_analysis.py`:

```python
from src.agent.orchestrator import CodeAnalysisAgent

# Initialize agent
agent = CodeAnalysisAgent(repo_path="/path/to/your/project")

# Run analysis
result = agent.analyze(target="src/module.py")

# Print results
print(result["output"])

# Show reasoning steps
for step, (action, observation) in enumerate(result["intermediate_steps"], 1):
    print(f"\nStep {step}: {action.tool}")
    print(f"Result: {observation[:200]}...")
```

Run it:
```bash
python my_analysis.py
```

## Understanding the Output

The agent provides:

1. **Issue Type**: Bug, Security, Performance, Code Quality
2. **Severity**: Critical, High, Medium, Low
3. **Location**: File path and line numbers
4. **Description**: What's wrong
5. **Impact**: Consequences
6. **Fix**: How to resolve it
7. **Reasoning**: Why it's an issue

Example output:
```
[HIGH] SECURITY: SQL Injection vulnerability
  Location: process_user_input (line 15)
  Description: User input concatenated directly into SQL query
  Impact: Attacker could read/modify database
  Fix: Use parameterized queries
  Reasoning: String formatting with user input allows SQL injection
```

## Available Analysis Types

```bash
# Bug detection only
--type bug_detection

# Security vulnerabilities only
--type security_scan

# Code quality issues
--type code_quality

# Everything (default)
--type comprehensive
```

## Tips for Success

1. **Start small**: Analyze single files before entire projects
2. **Use verbose mode**: See how the agent thinks
3. **Be specific**: Target specific files for faster results
4. **Iterate**: Use findings to guide deeper analysis

## Common Issues

### "ANTHROPIC_API_KEY not found"
- Make sure `.env` file exists
- Check the API key is correctly formatted
- API key should start with `sk-ant-`

### "Repository path does not exist"
- Use absolute paths: `/full/path/to/project`
- Or run from correct directory

### "Tool not installed"
- Some tools (pylint, flake8) need separate installation:
  ```bash
  pip install pylint flake8
  ```

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Check out [examples/demo_analysis.py](examples/demo_analysis.py) for API usage
3. Run tests: `pytest tests/ -v`
4. Explore the [ReAct pattern](https://arxiv.org/abs/2210.03629) to understand the reasoning

## Getting Help

- Check the README for detailed documentation
- Look at example code in `examples/`
- Review test cases in `tests/`

## What's Next?

Now you can:
- ✅ Analyze your own projects
- ✅ Integrate into CI/CD pipelines
- ✅ Customize prompts for your needs
- ✅ Add new analysis tools
- ✅ Build on top of this framework

Happy analyzing! 🚀
