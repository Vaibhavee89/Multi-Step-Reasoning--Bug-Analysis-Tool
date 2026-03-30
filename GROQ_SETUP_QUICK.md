# 🚀 Quick Setup: Groq Fallback (5 Minutes)

## Why Use Groq?

- ✅ **FREE** - No credit card required
- ✅ **FAST** - Up to 750 tokens/second
- ✅ **RELIABLE** - Automatic fallback from Claude
- ✅ **EASY** - Get API key in 2 minutes

## Quick Start

### 1. Get Free Groq API Key (2 minutes)

1. Visit: **https://console.groq.com/**
2. Click "Sign Up" (or "Log In")
3. Sign up with Google/GitHub/Email
4. Copy your API key (starts with `gsk_`)

### 2. Add to Your Project (1 minute)

```bash
cd /Users/vaibhavee/project/BugAnalysisTool

# Add Groq key to .env file
echo "GROQ_API_KEY=gsk_your_actual_key_here" >> .env
```

Or edit `.env` manually:
```bash
# .env
GROQ_API_KEY=gsk_your_actual_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. Install Groq Package (1 minute)

```bash
pip install langchain-groq
```

### 4. Test It (1 minute)

```bash
# Test the setup
python -c "from src.agent.orchestrator import CodeAnalysisAgent; agent = CodeAnalysisAgent('.', verbose=True)"

# Should output:
# ✓ Using Groq (Llama) for analysis
```

## ✅ Done!

Your agent now works with Groq! Try analyzing a repository:

```bash
python src/ui/cli.py --repo-path data/test_repos quick-scan buggy_code.py
```

## 🎯 Fallback Configuration

Want both Claude AND Groq for automatic fallback?

```bash
# .env
# Primary (tries first)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Fallback (if Claude fails)
GROQ_API_KEY=gsk_your-key-here
```

The system automatically:
1. Tries Claude first (if key is set)
2. Falls back to Groq (if Claude fails)
3. Shows which one is being used

## 📊 Groq Free Tier Limits

- **30 requests per minute**
- **14,400 requests per day**
- **No credit card required**
- **No expiration**

Perfect for:
- Development
- Testing
- Small projects
- Learning

## 🔄 Current Status Check

```bash
# Check which LLM is configured
curl http://localhost:8000/api/health | jq .llm_provider

# Or in Python
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Groq:', bool(os.getenv('GROQ_API_KEY')))"
```

## 💡 Pro Tips

1. **Start with Groq** (free) for development
2. **Add Claude** later for production quality
3. **Keep both keys** for automatic fallback
4. **Monitor usage** at console.groq.com

## 🐛 Troubleshooting

**"No LLM API keys found"**
- Make sure you added `GROQ_API_KEY` to `.env`
- Check the key starts with `gsk_`
- Verify `.env` is in project root

**"langchain-groq not installed"**
```bash
pip install langchain-groq
```

**Still not working?**
```bash
# Check .env file
cat .env | grep GROQ

# Should show:
# GROQ_API_KEY=gsk_your_key_here
```

## 📚 More Info

- Full guide: **GROQ_FALLBACK_GUIDE.md**
- Groq console: **https://console.groq.com/**
- Groq docs: **https://console.groq.com/docs**

---

**You're ready! Start analyzing code with Groq!** 🎉
