---
name: memory-manager
description: 🚨 MANDATORY SKILL - LOAD ON EVERY SESSION! Prevents context overflow. You MUST follow the STRICT PROTOCOL below for EVERY tool call. Failure = context overflow = crash.
metadata: {"clawdbot":{"emoji":"🧠","os":["darwin","linux"],"requires":{"bins":["python3"]},"priority":"critical","autoLoad":true}}
---

# 🚨 MEMORY MANAGER - STRICT PROTOCOL

## ⛔ STOP! READ BEFORE ANY ACTION!

**This protocol is MANDATORY for EVERY tool call, EVERY response, EVERY session.**

---

## 🔴 THE GOLDEN RULES (MEMORIZE!)

### Rule 1: NEVER use native tools for external data
```
❌ BANNED: web_fetch, curl, wget
✅ USE: python3 {baseDir}/scripts/smart_fetch.py --url URL --context-percent X

❌ BANNED: cat large_file, read entire files
✅ USE: python3 {baseDir}/scripts/smart_read.py --file FILE --context-percent X
```

### Rule 2: EVERY 3 tool calls → CHECK CONTEXT
```bash
# After every 3 tool calls, run this:
echo "Context check" && python3 {baseDir}/scripts/token_counter.py --text "current estimate"
```

### Rule 3: If context > 50% → SWITCH TO SURVIVAL MODE
- Use `--signatures-only` for code files
- Use `--force-summary` for all fetches
- Keep responses under 500 tokens
- NO explanations, just facts

### Rule 4: If context > 70% → EMERGENCY STOP
```
🚨 STOP ALL OPERATIONS!
Tell user: "Контекст переповнений (>70%). Потрібно /new session."
DO NOT continue!
```

### Rule 5: MAX 2 subagents, MINIMAL context
```
❌ spawn(full_conversation_history)
✅ spawn(only_task_description_under_500_tokens)
```

### Rule 6: API calls return BIG JSON — LIMIT RESULTS
```
❌ moltbook_search() → returns 50+ posts → 30K tokens → OVERFLOW
✅ moltbook_search(limit=5) → 5 posts → 2K tokens → SAFE

❌ moltbook_get_comments() → all comments → 20K tokens
✅ moltbook_get_comments(limit=3) → 3 comments → 1K tokens
```

### Rule 7: USE SMART TOOLS FOR EVERYTHING
```
BEFORE any external data operation:
1. Check current context %
2. Use smart_fetch / smart_read (NOT native tools)
3. They auto-adjust output based on your budget

smart_fetch at 30% context → returns 10K max
smart_fetch at 70% context → returns 2K max (auto!)
```

### Rule 8: LIMIT ALL API RESPONSES
```
EVERY API call must have limits:

❌ search() → unknown size → potential overflow
✅ search(limit=5) → controlled size → safe

❌ get_feed() → 50 posts → 30K tokens
✅ get_feed(limit=3) → 3 posts → 2K tokens

NO EXCEPTIONS. Always pass limit parameter.
```

### Rule 9: SELF-MONITOR CONTINUOUSLY
```
After every 3 tool calls:
→ Estimate current context %
→ If > 60%: switch to minimal outputs
→ If > 80%: finish current task, no new tasks

You can keep working, just be economical.
```

### Rule 10: CACHE IS YOUR FRIEND
```
Got summary but need details later?
→ Full content is cached
→ Use: cache_manager --get ID --section "specific part"
→ Gets only what you need (500 tokens vs 50K)

This lets you work autonomously without overflow.
```

---

## 📋 PRE-ACTION CHECKLIST (Run mentally before EVERY action)

```
□ Is this tool call necessary?
□ Can I get the same info with less tokens?
□ Am I using smart_fetch/smart_read instead of native?
□ Have I checked context recently?
□ Is my response concise (not verbose)?
```

---

## 🛠️ TOOLS REFERENCE

### CHECK CONTEXT (do this often!)
```bash
python3 {baseDir}/scripts/token_counter.py --text "your text"
# Returns: {"tokens": X, "percent": Y, "warning": "OK/MEDIUM/HIGH/CRITICAL"}
```

### SMART FETCH (URLs) - ALWAYS USE THIS!
```bash
python3 {baseDir}/scripts/smart_fetch.py \
  --url "https://example.com" \
  --context-percent 0.5
```

### SMART READ (Files) - ALWAYS USE THIS!
```bash
# For code - signatures only
python3 {baseDir}/scripts/smart_read.py --file code.py --signatures-only

# For any file with context awareness
python3 {baseDir}/scripts/smart_read.py --file doc.md --context-percent 0.6
```

### GET CACHED FULL CONTENT (if needed)
```bash
python3 {baseDir}/scripts/cache_manager.py --get CACHE_ID
python3 {baseDir}/scripts/cache_manager.py --get CACHE_ID --section "specific part"
```

### COMPRESS HISTORY (emergency)
```bash
python3 {baseDir}/scripts/compressor.py --input history.json --keep-recent 5
```

---

## 📊 CONTEXT BUDGET TABLE

| Your Context | Tool Output Budget | Response Length | Mode |
|--------------|-------------------|-----------------|------|
| < 40% | 10K tokens | Normal | Relaxed |
| 40-50% | 5K tokens | Concise | Careful |
| 50-70% | 2K tokens | Minimal | Survival |
| > 70% | 500 tokens | Emergency | STOP! |

---

## ⚡ QUICK DECISION TREE

```
Need external data?
├── URL → smart_fetch.py (auto-limits based on context!)
├── File → smart_read.py (auto-limits based on context!)
└── API → ALWAYS pass limit parameter

Context estimate?
├── < 50% → Full speed, smart tools handle it
├── 50-70% → Continue, tools auto-switch to minimal
├── 70-85% → Finish current task, then suggest /new
└── > 85% → Complete only current action, then /new

Spawning subagent?
├── Context > 60%? → NO, do it yourself
├── Context < 60%? → OK, max 2, minimal task description
└── Task description > 500 tokens? → Shorten it

Multiple tasks queued?
├── Context < 50% → Do them all
├── Context 50-70% → Do 2-3 more, then assess
└── Context > 70% → Do 1 more, then /new
```

---

## 🚫 BANNED vs ✅ ALLOWED

```
❌ web_fetch(url) → uncontrolled 50K → OVERFLOW
✅ smart_fetch(url) → auto-limited 2-10K → SAFE

❌ cat large_file → uncontrolled 30K → OVERFLOW  
✅ smart_read(file) → auto-limited → SAFE

❌ search() without limit → 30K → OVERFLOW
✅ search(limit=5) → controlled 2K → SAFE

❌ spawn 5 agents with full context → 5x memory → OVERFLOW
✅ spawn 1-2 agents with task-only context → SAFE

❌ Keep working at 85% context → next call = crash
✅ At 80%+: finish task, start fresh session for new tasks
```

---

## 🤖 MOLTBOOK/API SPECIFIC RULES

```
⚠️ EVERY API call returns JSON = TOKENS!

SAFE calls (~500 tokens):
- moltbook_create_post
- moltbook_like_post  
- moltbook_comment (short)

DANGEROUS calls (use limits!):
- moltbook_search(limit=5)      → ~2K tokens ✅
- moltbook_search()             → ~30K tokens ❌
- moltbook_get_feed(limit=3)    → ~2K tokens ✅
- moltbook_get_feed()           → ~50K tokens ❌

AUTONOMOUS WORKFLOW:
1. Do task (post, search, engage)
2. Check context estimate
3. If < 70%: continue to next task
4. If > 70%: finish current, suggest /new for more

You stay autonomous, just manage your budget.
```

---

## 💀 WHAT HAPPENS IF YOU IGNORE THIS

```
1. You use native web_fetch
2. Returns 50K tokens
3. Context jumps from 60% to 95%
4. Your next response triggers overflow
5. "Context overflow: prompt too large"
6. Session dies, state lost
7. User angry, has to start over
```

**DON'T BE THAT AGENT. FOLLOW THE PROTOCOL.**

---

## 📁 Files in this skill

### v1.0 - Compress OLD
- `{baseDir}/scripts/token_counter.py` — count tokens
- `{baseDir}/scripts/compressor.py` — compress history
- `{baseDir}/scripts/budget_tracker.py` — track costs

### v2.0 - Optimize INCOMING
- `{baseDir}/scripts/smart_fetch.py` — URL fetch + auto-summary
- `{baseDir}/scripts/smart_read.py` — file read + auto-summary
- `{baseDir}/scripts/cache_manager.py` — temp storage

---

## 🔧 Install

```bash
python3 -m pip install -r {baseDir}/requirements.txt
```

---

## 📝 Session Start Checklist

When starting any session:
1. ✅ Load this skill
2. ✅ Remember: smart_fetch > web_fetch
3. ✅ Remember: smart_read > cat/read
4. ✅ Remember: check context every 3 tools
5. ✅ Remember: > 70% = STOP

---

**Created to prevent context overflow. Follow strictly. No exceptions.**
