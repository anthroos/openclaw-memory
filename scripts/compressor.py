#!/usr/bin/env python3
"""Compress conversation history by summarizing old messages."""
from __future__ import annotations
import argparse, json, os, sys
from datetime import datetime
from pathlib import Path

try:
    import tiktoken
    ENCODING = tiktoken.get_encoding("cl100k_base")
    def count_tokens(text): return len(ENCODING.encode(text))
except:
    def count_tokens(text): return len(text)//4

def messages_to_text(msgs):
    return '\n\n'.join(f"[{m.get('role','?')}]: {m.get('content','')}" for m in msgs)

def compress_messages(messages, keep_recent=5, dry_run=False):
    if len(messages) <= keep_recent:
        return messages, {"compressed": False, "reason": "Not enough messages"}
    
    old, recent = messages[:-keep_recent], messages[-keep_recent:]
    old_tokens = count_tokens(messages_to_text(old))
    recent_tokens = count_tokens(messages_to_text(recent))
    
    stats = {"original": len(messages), "old": len(old), "recent": len(recent),
             "old_tokens": old_tokens, "recent_tokens": recent_tokens}
    
    if dry_run:
        stats["dry_run"] = True
        return messages, stats
    
    summary = f"[Summary of {len(old)} messages]"  # Simplified - would use API in production
    compressed = [{"role": "system", "content": f"[COMPRESSED {datetime.now().isoformat()}]\n{summary}",
                   "_meta": {"compressed": True, "original_count": len(old)}}] + recent
    
    stats.update({"compressed": True, "summary_tokens": count_tokens(summary),
                  "saved": old_tokens - count_tokens(summary)})
    return compressed, stats

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", type=Path, required=True)
    ap.add_argument("--output", "-o", type=Path)
    ap.add_argument("--keep-recent", "-k", type=int, default=5)
    ap.add_argument("--dry-run", "-n", action="store_true")
    args = ap.parse_args()

    data = json.loads(args.input.read_text())
    messages = data if isinstance(data, list) else data.get("messages", [])
    
    compressed, stats = compress_messages(messages, args.keep_recent, args.dry_run)
    print(json.dumps(stats, indent=2))
    
    if not args.dry_run and stats.get("compressed"):
        out = args.output or args.input
        out.write_text(json.dumps(compressed if isinstance(data,list) else {**data,"messages":compressed}, indent=2))

if __name__ == "__main__": main()
