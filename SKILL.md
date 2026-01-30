---
name: memory-manager
description: Prevents context overflow. ALWAYS use these shell commands instead of native tools.
metadata: {"clawdbot":{"emoji":"🧠","os":["darwin","linux"],"requires":{"bins":["python3"]},"priority":"critical","autoLoad":true}}
---

# Memory Manager v2.0

## ⚠️ MANDATORY: Use Shell Commands

**NEVER use native `web_fetch` or `read` for external data.**
**ALWAYS run these shell commands instead:**

### Fetch URL
```bash
python3 ~/.clawdbot/skills/memory-manager/scripts/smart_fetch.py --url "URL" --context-percent 0.5
```

### Read File
```bash
python3 ~/.clawdbot/skills/memory-manager/scripts/smart_read.py --file "PATH" --context-percent 0.5
```

### Read Code (signatures only)
```bash
python3 ~/.clawdbot/skills/memory-manager/scripts/smart_read.py --file "PATH" --signatures-only
```

### Get Cached Content
```bash
python3 ~/.clawdbot/skills/memory-manager/scripts/cache_manager.py --get CACHE_ID
python3 ~/.clawdbot/skills/memory-manager/scripts/cache_manager.py --get CACHE_ID --section "keyword"
```

---

## Context Budget

| Context % | --context-percent | Mode |
|-----------|-------------------|------|
| < 40% | 0.3 | Full |
| 40-70% | 0.5 | Normal |
| 70-85% | 0.7 | Minimal |
| > 85% | 0.9 | Finish & /new |

---

## Rules

1. **URL?** → Run `smart_fetch.py` shell command
2. **File?** → Run `smart_read.py` shell command  
3. **API?** → Always pass `limit=5` or less
4. **Context > 70%?** → Finish current task, suggest /new

---

## Quick Copy-Paste

```bash
# Fetch URL
python3 ~/.clawdbot/skills/memory-manager/scripts/smart_fetch.py --url "https://example.com" --context-percent 0.5

# Read file
python3 ~/.clawdbot/skills/memory-manager/scripts/smart_read.py --file "/path/to/file" --context-percent 0.5

# Get from cache
python3 ~/.clawdbot/skills/memory-manager/scripts/cache_manager.py --get abc123 --section "pricing"
```
