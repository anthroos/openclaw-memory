---
name: memory-manager
description: CRITICAL - Load this skill BEFORE spawning subagents or when context feels heavy. Prevents context overflow by tracking token usage and compressing old messages. If you see 'Context overflow' errors - you MUST use this skill immediately.
metadata: {"clawdbot":{"emoji":"🧠","os":["darwin","linux"],"requires":{"bins":["python3"]},"priority":"high","autoLoad":true}}
---

# Memory Manager

**⚠️ CRITICAL: Use this skill BEFORE spawning any subagents!**

Prevents context overflow by monitoring token usage and compressing old messages before hitting limits.

## MANDATORY RULES (READ FIRST!)

1. **BEFORE spawning subagents**: Check context size first!
2. **If context > 70%**: Do NOT spawn agents. Compress first.
3. **If you see "Context overflow"**: STOP. Start new session or compress.
4. **Maximum subagents**: Spawn max 2 at a time, never more!
5. **Subagent context**: Pass ONLY the task description, NOT full history!

## Quick Check (Run This First!)

```bash
# Check if safe to spawn agents
python3 {baseDir}/scripts/token_counter.py --text "$(cat current_context.txt)" --threshold 0.6
```

If exit code = 1 → **DO NOT SPAWN AGENTS!** Compress first.

## Problem Solved

- Context window fills up unexpectedly → crash
- No visibility into token usage or costs  
- Spawned agents inherit full context → instant overflow

## Files

- `{baseDir}/scripts/token_counter.py` — count tokens in text
- `{baseDir}/scripts/compressor.py` — summarize old messages
- `{baseDir}/scripts/budget_tracker.py` — track costs + alerts
- `{baseDir}/scripts/dashboard_server.py` — serve monitoring dashboard
- `{baseDir}/dashboard/index.html` — visual dashboard

## Install dependencies

```bash
python3 -m pip install -r {baseDir}/requirements.txt
```

## Usage

### Count tokens in text

```bash
python3 {baseDir}/scripts/token_counter.py --text "Your message here"
python3 {baseDir}/scripts/token_counter.py --file conversation.json
```

Output:
```json
{"tokens": 1234, "limit": 200000, "percent": 0.6, "remaining": 198766}
```

### Check if compression needed

```bash
python3 {baseDir}/scripts/token_counter.py --file history.json --threshold 0.7
```

Returns exit code 1 if above threshold (needs compression).

### Compress conversation history

```bash
python3 {baseDir}/scripts/compressor.py --input history.json --output compressed.json
python3 {baseDir}/scripts/compressor.py --input history.json --keep-recent 5
```

Keeps last N messages verbatim, summarizes older messages.

### Track costs

```bash
python3 {baseDir}/scripts/budget_tracker.py --state state.json
python3 {baseDir}/scripts/budget_tracker.py --state state.json --alert-at 5.00
```

Output:
```json
{"session_cost": 2.45, "daily_cost": 12.30, "alert": false, "breakdown": {...}}
```

### Launch dashboard

```bash
python3 {baseDir}/scripts/dashboard_server.py --port 8765 --state state.json
```

Open http://localhost:8765 to view real-time metrics.

## Recommended workflow

Before spawning agents:

```bash
# 1. Check current usage
python3 {baseDir}/scripts/token_counter.py --file history.json --threshold 0.7

# 2. If above threshold, compress first
python3 {baseDir}/scripts/compressor.py --input history.json --output history.json --keep-recent 5

# 3. Now safe to spawn agents with smaller context
```

## Compression thresholds

- **70%** (140K tokens): Warning, consider compressing
- **80%** (160K tokens): Compress now
- **90%** (180K tokens): Critical, immediate compression

## Model pricing (for cost tracking)

| Model | Input (per 1M) | Output (per 1M) |
|-------|----------------|-----------------|
| claude-3-opus | $15.00 | $75.00 |
| claude-3-sonnet | $3.00 | $15.00 |
| claude-3-haiku | $0.25 | $1.25 |
| claude-3.5-sonnet | $3.00 | $15.00 |

## Notes

- Token counting uses `tiktoken` with `cl100k_base` encoding (Claude-compatible)
- Compression uses Claude Haiku (cheapest) for summarization
- State persisted in JSON files for recovery
- Dashboard polls every 2 seconds for real-time updates
