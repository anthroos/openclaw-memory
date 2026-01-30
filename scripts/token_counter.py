#!/usr/bin/env python3
"""Count tokens in text or JSON conversation files."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

try:
    import tiktoken
    ENCODING = tiktoken.get_encoding("cl100k_base")
    def count_tokens(text: str) -> int: return len(ENCODING.encode(text))
except ImportError:
    def count_tokens(text: str) -> int: return len(text) // 4

MODEL_LIMITS = {"default": 200_000}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", "-t")
    ap.add_argument("--file", "-f", type=Path)
    ap.add_argument("--threshold", type=float)
    ap.add_argument("--quiet", "-q", action="store_true")
    args = ap.parse_args()

    if args.text:
        tokens = count_tokens(args.text)
    elif args.file and args.file.exists():
        data = json.loads(args.file.read_text())
        if isinstance(data, list):
            tokens = sum(count_tokens(m.get("content", "")) + 4 for m in data if isinstance(m, dict))
        else:
            tokens = count_tokens(json.dumps(data))
    else:
        tokens = count_tokens(sys.stdin.read()) if not sys.stdin.isatty() else 0

    limit = MODEL_LIMITS["default"]
    percent = tokens / limit
    warning = "CRITICAL" if percent >= 0.9 else "HIGH" if percent >= 0.8 else "MEDIUM" if percent >= 0.7 else "OK"
    
    print(json.dumps({"tokens": tokens, "limit": limit, "percent": round(percent, 4), "remaining": limit - tokens, "warning": warning}))
    
    if args.threshold and percent > args.threshold:
        if not args.quiet: print(f"Threshold {args.threshold} exceeded: {percent:.2%}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__": main()
