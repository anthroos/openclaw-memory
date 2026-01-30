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

### Rule 7: ONE TASK AT A TIME
```
❌ "Create post, then search, then engage 3 bots, then check reactions"
   = 6+ tool calls = OVERFLOW

✅ "Create post" → STOP → wait for user
✅ "Search for 3 bots" → STOP → wait for user  
✅ "Engage 1 bot" → STOP → wait for user
```

### Rule 8: NO CHAIN REACTIONS
```
❌ Tool call → see result → "let me also..." → another tool → "and also..."
   This KILLS context!

✅ Tool call → DONE. Report to user. Wait.
```

### Rule 9: YOUR ESTIMATES ARE WRONG
```
Your "49% context" is probably actually 80%+
Tool outputs are BIGGER than you think
When in doubt: STOP EARLIER, not later
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
├── URL → smart_fetch.py (NOT web_fetch!)
├── File → smart_read.py (NOT cat/read!)
└── API → smart_fetch.py with API URL

Context feeling heavy?
├── < 50% → Continue carefully
├── 50-70% → Switch to survival mode
└── > 70% → STOP, tell user to /new

Spawning subagent?
├── Context > 50%? → NO, don't spawn
├── Task description > 500 tokens? → Shorten it
└── More than 2 agents? → NO, max 2
```

---

## 🚫 BANNED PATTERNS

```
❌ "Let me fetch this URL..." → web_fetch → 50K tokens → OVERFLOW
❌ "I'll read the entire file..." → cat → 30K tokens → OVERFLOW
❌ "Here's a detailed explanation..." → 5K response → OVERFLOW
❌ "Spawning 5 expert agents..." → 5x context → OVERFLOW
❌ "Let me also engage these 3 bots..." → chain reaction → OVERFLOW
❌ "Checking reactions on my post..." → unnecessary call → OVERFLOW

✅ "Using smart_fetch..." → 2K summary → SAFE
✅ "Reading signatures only..." → 500 tokens → SAFE
✅ "Short answer: X" → 200 tokens → SAFE
✅ "Spawning 1 focused agent..." → minimal context → SAFE
✅ "Done. One post created." → STOP → SAFE
```

---

## 🤖 MOLTBOOK/API SPECIFIC RULES

```
⚠️ EVERY API call returns JSON = TOKENS!

moltbook_create_post    → ~500 tokens (OK)
moltbook_search         → ~5K-30K tokens (DANGER!)
moltbook_get_feed       → ~10K-50K tokens (DANGER!)
moltbook_get_comments   → ~2K-20K tokens (DANGER!)

ALWAYS use limit parameter:
- search(limit=5) not search()
- get_feed(limit=3) not get_feed()
- get_comments(limit=3) not get_comments()

RESIST THE URGE to:
- "Check how my post is doing" → unnecessary
- "Engage multiple bots at once" → do ONE
- "Search for more content" → you have enough
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
