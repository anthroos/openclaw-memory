---
name: memory-manager
description: Prevents context overflow. Use smart_fetch/smart_read instead of native tools.
metadata: {"clawdbot":{"emoji":"🧠","os":["darwin","linux"],"requires":{"bins":["python3"]},"priority":"critical","autoLoad":true}}
---

# Memory Manager v2.0

## 🛠️ Tools

```bash
# Fetch URL (auto-summarizes based on context)
python3 {baseDir}/scripts/smart_fetch.py --url URL --context-percent 0.X

# Read file (auto-summarizes based on context)
python3 {baseDir}/scripts/smart_read.py --file FILE --context-percent 0.X
python3 {baseDir}/scripts/smart_read.py --file FILE --signatures-only

# Get cached full content
python3 {baseDir}/scripts/cache_manager.py --get CACHE_ID
python3 {baseDir}/scripts/cache_manager.py --get CACHE_ID --section "keyword"

# Count tokens
python3 {baseDir}/scripts/token_counter.py --text "text"
```

## 📊 Context Budget

| Context % | Output Budget | Action |
|-----------|---------------|--------|
| < 40% | 10K tokens | Full speed |
| 40-70% | 5K tokens | Continue |
| 70-85% | 2K tokens | Finish task |
| > 85% | 500 tokens | Suggest /new |

## 🔴 Rules

1. **NEVER** use `web_fetch`, `curl`, `cat` for external data → use `smart_fetch` / `smart_read`
2. **ALWAYS** pass `limit` param to API calls: `search(limit=5)`, `get_feed(limit=3)`
3. **CHECK** context every 3 tool calls
4. **AT 70%+**: finish current task, suggest `/new` for more tasks
5. **CACHE**: full content saved automatically, retrieve with `--get ID --section "keyword"`

## ❌ Banned → ✅ Use

```
web_fetch(url)     → smart_fetch.py --url URL
cat file           → smart_read.py --file FILE
search()           → search(limit=5)
get_feed()         → get_feed(limit=3)
```

## Install

```bash
pip install tiktoken
```
