# OpenClaw Memory Manager v2.0

**Smart Tool Proxy for AI agents. Prevents "context overflow" by auto-summarizing large inputs.**

## The Problem

AI agents have a context limit (~200K tokens). One `web_fetch` can return 50K tokens. Three fetches = crash.

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTEXT WINDOW (200K)                    │
├─────────────────────────────────────────────────────────────┤
│ System prompt    │████░░░░░░░░░░░░░░░░░░░░░░░░░░│  5K      │
│ Conversation     │████████░░░░░░░░░░░░░░░░░░░░░░│  20K     │
│ web_fetch #1     │████████████████░░░░░░░░░░░░░░│ +50K 💥  │
│ web_fetch #2     │████████████████████████░░░░░░│ +40K 💥  │
│ web_fetch #3     │████████████████████████████░░│ +35K 💥  │
│ Next response    │██████████████████████████████│ OVERFLOW │
└─────────────────────────────────────────────────────────────┘
                              ↓
              "Context overflow: prompt too large"
                        SESSION DEAD
```

**What happens:**
1. Agent calls `web_fetch` → gets 50K tokens
2. All content goes into context window
3. After 3 requests → overflow, session dead
4. Work lost

---

## The Solution

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTEXT WINDOW (200K)                    │
├─────────────────────────────────────────────────────────────┤
│ System prompt    │████░░░░░░░░░░░░░░░░░░░░░░░░░░│  5K      │
│ Conversation     │████████░░░░░░░░░░░░░░░░░░░░░░│  20K     │
│ smart_fetch #1   │████████▓░░░░░░░░░░░░░░░░░░░░░│ +3K ✅   │
│ smart_fetch #2   │████████▓▓░░░░░░░░░░░░░░░░░░░░│ +2K ✅   │
│ smart_fetch #3   │████████▓▓▓░░░░░░░░░░░░░░░░░░░│ +2K ✅   │
│ ... #10          │████████▓▓▓▓▓▓░░░░░░░░░░░░░░░░│ +15K ✅  │
│ Still working!   │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ 55% free │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    LOCAL CACHE                              │
├─────────────────────────────────────────────────────────────┤
│ abc123.txt │ Full content from fetch #1 (50K)              │
│ def456.txt │ Full content from fetch #2 (40K)              │
│ ghi789.txt │ Full content from fetch #3 (35K)              │
│            │ → Access: cache --get ID --section "keyword"   │
└─────────────────────────────────────────────────────────────┘
```

**What happens now:**
1. `smart_fetch` gets page (50K)
2. Auto-summarizes to 2-3K (key info)
3. Full content → local cache
4. Only summary goes to context
5. Need details? → `cache --get ID --section "pricing"`

---

## How It Works

```
User: "Find info about company X"
              │
              ▼
┌─────────────────────────────────┐
│ smart_fetch("company-x.com")   │
│                                 │
│ 1. Fetch page → 50K tokens     │
│ 2. Check context: 30%          │
│ 3. Budget at 30% = 10K         │
│ 4. Content > budget?           │
│    YES → summarize to 3K       │
│         + save full to cache   │
│ 5. Return: summary + cache_id  │
└─────────────────────────────────┘
              │
              ▼
Agent receives:
- Summary (3K) → into context
- cache_id: "abc123" → if details needed

Context: 30% → 32% (instead of 30% → 55%!)
```

---

## Comparison

| Metric | Without | With Memory Manager |
|--------|---------|---------------------|
| Requests before overflow | 3 | 10-20+ |
| Tokens per fetch | 50K | 2-5K |
| Full data | Lost | Cached |
| Autonomy | Low | High |

---

## Quick Start

### Install

```bash
pip install tiktoken
```

### Use smart_fetch instead of web_fetch

```bash
# Auto-summarizes based on current context usage
python3 scripts/smart_fetch.py --url "https://example.com" --context-percent 0.3
```

### Use smart_read instead of cat/read

```bash
# For code files - extract signatures only
python3 scripts/smart_read.py --file app.py --signatures-only

# For any file - auto-summarize
python3 scripts/smart_read.py --file docs.md --context-percent 0.5
```

### Retrieve full content from cache

```bash
# Get specific section
python3 scripts/cache_manager.py --get abc123 --section "pricing"

# Get everything
python3 scripts/cache_manager.py --get abc123
```

### Count tokens

```bash
python3 scripts/token_counter.py --text "Your message here"
# {"tokens": 5, "percent": 0.0, "warning": "OK"}
```

---

## Context Budget

| Context % | Output Budget | Agent Action |
|-----------|---------------|--------------|
| < 40% | 10K tokens | Full speed |
| 40-70% | 5K tokens | Continue |
| 70-85% | 2K tokens | Finish current task |
| > 85% | 500 tokens | Suggest /new session |

---

## Rules for Agents

1. **NEVER** use `web_fetch`, `curl`, `cat` → use `smart_fetch` / `smart_read`
2. **ALWAYS** pass `limit` to API calls: `search(limit=5)`
3. **CHECK** context every 3 tool calls
4. **AT 70%+**: finish current task, suggest `/new`
5. **CACHE**: retrieve details with `--section "keyword"`

---

## As a Clawdbot/Moltbot Skill

```bash
cp -r . ~/.clawdbot/skills/memory-manager/
```

Or add to config:

```json
{
  "skills": {
    "load": {
      "extraDirs": ["/path/to/openclaw-memory"]
    }
  }
}
```

---

## Value

**For users:**
- Agent works longer without crash
- No constant `/new` needed
- Complex tasks complete successfully

**For agents:**
- More operations per session
- Full data access via cache
- Automatic budget control

**One sentence:**
> Instead of 3 requests and crash — 10+ requests and keep working.

---

## License

MIT License

## Author

Created for the Moltbot/Clawdbot ecosystem.
