# 🚀 Groq Fallback Feature Guide

## Overview

Your Code Analysis Agent now supports **automatic LLM fallback** - if Claude API is unavailable or fails, the system automatically switches to Groq!

## 🎯 Benefits

### Reliability
- ✅ **Zero downtime** - Automatic fallback if primary LLM fails
- ✅ **No manual intervention** - Seamless switching
- ✅ **Transparent operation** - Know which LLM is being used

### Cost Savings
- ✅ **Groq free tier** - 30 requests/minute free
- ✅ **Fast inference** - Up to 750 tokens/second
- ✅ **No credit card required** - Get started immediately

### Flexibility
- ✅ **Multiple model options** - Choose Claude or Groq
- ✅ **Easy configuration** - Just add API keys
- ✅ **Works everywhere** - CLI, Web App, Docker

## 🔑 Getting API Keys

### Option 1: Claude (Primary - Best Quality)

1. Go to https://console.anthropic.com/
2. Sign up / Log in
3. Navigate to API Keys
4. Create new key
5. Copy and save it

**Pricing:** Pay-as-you-go
- Claude Sonnet: $3/M input tokens, $15/M output tokens
- Claude Haiku: $0.25/M input tokens, $1.25/M output tokens

### Option 2: Groq (Fallback - Free & Fast)

1. Go to https://console.groq.com/
2. Sign up (free, no credit card)
3. Get API key immediately
4. Copy and save it

**Pricing:** FREE
- 30 requests/minute (free tier)
- 14,400 requests/day
- Fast inference (750 tokens/s)

**Available Models:**
- `llama-3.3-70b-versatile` (Default - Recommended)
- `llama-3.1-70b-versatile`
- `mixtral-8x7b-32768`
- `gemma2-9b-it`

## ⚙️ Configuration

### Setup (Choose One or Both)

**Option A: Claude Only**
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-your-key-here
CLAUDE_MODEL=claude-sonnet-4-5-20250929
```

**Option B: Groq Only**
```bash
# .env
GROQ_API_KEY=gsk_your-key-here
GROQ_MODEL=llama-3.3-70b-versatile
```

**Option C: Both (Recommended - with Fallback)**
```bash
# .env
# Primary: Claude
ANTHROPIC_API_KEY=sk-ant-your-key-here
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# Fallback: Groq (free)
GROQ_API_KEY=gsk_your-key-here
GROQ_MODEL=llama-3.3-70b-versatile
```

## 🔄 How Fallback Works

### Automatic Priority System

```
1. Try Claude (if ANTHROPIC_API_KEY is set)
   ├─ Success → Use Claude
   └─ Fail → Try Groq

2. Try Groq (if GROQ_API_KEY is set)
   ├─ Success → Use Groq
   └─ Fail → Error

3. No keys configured → Error with instructions
```

### Example Scenarios

**Scenario 1: Claude Available**
```
✓ Using Claude (Anthropic) for analysis
Analyzing repository...
```

**Scenario 2: Claude Fails, Groq Available**
```
⚠️  Claude API failed: Rate limit exceeded
Falling back to Groq...
✓ Using Groq (Llama) for analysis
Analyzing repository...
```

**Scenario 3: Only Groq Configured**
```
✓ Using Groq (Llama) for analysis
Analyzing repository...
```

## 🖥️ Usage

### CLI Usage

```bash
# With both keys configured
python src/ui/cli.py --repo-path /path/to/repo analyze

# Output shows which LLM is used:
# ✓ Using Claude (Anthropic) for analysis
# or
# ✓ Using Groq (Llama) for analysis
```

### Python API Usage

```python
from src.agent.orchestrator import CodeAnalysisAgent

# Initialize agent (automatic LLM selection)
agent = CodeAnalysisAgent(repo_path="/path/to/repo", verbose=True)
# Output: ✓ Using Claude (Anthropic) for analysis

# Run analysis
result = agent.analyze(target=".", analysis_type="comprehensive")

# Check which LLM was used
print(f"Analysis performed using: {result['llm_provider']}")
```

### Web Application Usage

The web interface automatically shows which LLM is being used:

```bash
# Start backend
cd backend && python main.py

# Check health endpoint
curl http://localhost:8000/api/health

# Response includes:
{
  "status": "healthy",
  "llm_provider": "Claude (Anthropic)",  # or "Groq (Free Tier Available)"
  "anthropic_configured": true,
  "groq_configured": true,
  "timestamp": "2024-03-30T..."
}
```

## 📊 Comparison: Claude vs Groq

| Feature | Claude (Anthropic) | Groq |
|---------|-------------------|------|
| **Quality** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very Good |
| **Speed** | ⭐⭐⭐⭐ Fast | ⭐⭐⭐⭐⭐ Ultra Fast (750 tok/s) |
| **Cost** | 💰💰💰 Pay-per-use | 💰 FREE (30 req/min) |
| **Context** | 200K tokens | 32K tokens |
| **Reliability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Best For** | Complex analysis, Production | Development, Testing, Budget |

## 🎯 Recommended Setup

### For Development
```bash
# Use Groq for free development
GROQ_API_KEY=gsk_your-key-here
GROQ_MODEL=llama-3.3-70b-versatile
```

### For Production
```bash
# Use Claude with Groq fallback
ANTHROPIC_API_KEY=sk-ant-your-key-here
GROQ_API_KEY=gsk_your-key-here
```

### For Cost-Conscious Users
```bash
# Use Groq only (free tier)
GROQ_API_KEY=gsk_your-key-here
GROQ_MODEL=llama-3.3-70b-versatile
```

## 🔧 Installation

### Install Groq Support

```bash
# Update requirements
pip install langchain-groq

# Or install from requirements.txt
pip install -r requirements.txt
```

### Docker Setup

Groq support is included in Docker images. Just add your key:

```bash
# .env
GROQ_API_KEY=gsk_your-key-here

# Start with Docker
docker-compose up -d
```

## 🐛 Troubleshooting

### "No LLM API keys found"

**Solution:** Add at least one API key to `.env`:
```bash
# Option 1: Claude
ANTHROPIC_API_KEY=sk-ant-your-key

# Option 2: Groq
GROQ_API_KEY=gsk_your-key
```

### "langchain-groq not installed"

**Solution:** Install Groq package:
```bash
pip install langchain-groq
```

### Fallback Not Working

**Check:**
1. Both API keys are set in `.env`
2. Keys are valid (not placeholder text)
3. No typos in key values
4. `.env` file is in correct location

**Verify setup:**
```bash
# Test configuration
python -c "from src.agent.orchestrator import CodeAnalysisAgent; agent = CodeAnalysisAgent('.')"
```

### Rate Limits

**Claude Rate Limits:**
- Varies by tier (starter, build, scale)
- Check console.anthropic.com for limits

**Groq Rate Limits (Free Tier):**
- 30 requests per minute
- 14,400 requests per day
- Automatic rate limit handling

## 📈 Monitoring

### Check Current LLM Provider

**CLI:**
```bash
# Verbose mode shows provider
python src/ui/cli.py --verbose --repo-path . analyze
# Output: ✓ Using Claude (Anthropic) for analysis
```

**API:**
```bash
curl http://localhost:8000/api/health | jq .llm_provider
# Output: "Claude (Anthropic)" or "Groq (Free Tier Available)"
```

**Python:**
```python
result = agent.analyze(...)
print(result['llm_provider'])
```

## 🎓 Best Practices

### 1. Use Both Keys
```bash
# Recommended for production
ANTHROPIC_API_KEY=sk-ant-xxx  # Primary
GROQ_API_KEY=gsk_xxx          # Fallback
```

### 2. Monitor Usage
- Check which LLM is being used
- Monitor API costs
- Watch rate limits

### 3. Test Fallback
```bash
# Test with invalid Claude key
ANTHROPIC_API_KEY=invalid
GROQ_API_KEY=gsk_valid_key

# Should automatically use Groq
```

### 4. Choose Right Model
```bash
# For complex analysis
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# For speed and cost savings
GROQ_MODEL=llama-3.3-70b-versatile
```

## 🚀 Quick Start

### Minimal Setup (Free)

```bash
# 1. Get free Groq API key
# Visit: https://console.groq.com/

# 2. Add to .env
echo "GROQ_API_KEY=gsk_your_key_here" >> .env

# 3. Install package
pip install langchain-groq

# 4. Run analysis
python src/ui/cli.py --repo-path . analyze
```

### Full Setup (with Fallback)

```bash
# 1. Get both API keys
# Claude: https://console.anthropic.com/
# Groq: https://console.groq.com/

# 2. Configure both
cat >> .env << EOF
ANTHROPIC_API_KEY=sk-ant-your_key_here
GROQ_API_KEY=gsk_your_key_here
EOF

# 3. Install packages
pip install langchain-anthropic langchain-groq

# 4. Test
python -c "from src.agent.orchestrator import CodeAnalysisAgent; print('✓ Setup complete!')"
```

## 📚 Additional Resources

### Documentation
- [Groq Documentation](https://console.groq.com/docs)
- [Claude API Docs](https://docs.anthropic.com/)
- [LangChain Groq](https://python.langchain.com/docs/integrations/chat/groq/)

### Getting Keys
- **Groq (Free):** https://console.groq.com/
- **Claude:** https://console.anthropic.com/

### Model Information
- [Groq Models](https://console.groq.com/docs/models)
- [Claude Models](https://docs.anthropic.com/en/docs/models-overview)

## 💡 Tips

1. **Start with Groq** - Free tier is perfect for development
2. **Upgrade to Claude** - When you need best quality
3. **Use Both** - For production reliability
4. **Monitor Costs** - Track your API usage
5. **Test Fallback** - Verify it works before production

## ✅ Checklist

Before deploying:
- [ ] At least one API key configured
- [ ] Keys tested and working
- [ ] Fallback tested (if using both)
- [ ] Rate limits understood
- [ ] Monitoring setup
- [ ] Documentation reviewed

---

## 🎉 You're Ready!

Your Code Analysis Agent now has robust LLM fallback support. Enjoy reliable, cost-effective code analysis!

**Questions?** Check the main README.md or open an issue on GitHub.
