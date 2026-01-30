---
name: memory-manager
description: Real-time context monitoring with streaming compression for Clawdbot. Prevents context overflow by tracking token usage, compressing old messages proactively, and providing cost estimates. Use when managing long conversations or spawning multiple agents to avoid hitting the 200K token limit.
metadata: {"clawdbot":{"emoji":"🧠","os":["darwin","linux"],"requires":{"bins":["python3"]}}}
---

# Memory Manager

Prevents context overflow by monitoring token usage and compressing old messages before hitting limits.

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
