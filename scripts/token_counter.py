#!/usr/bin/env python3
"""Count tokens in text or JSON conversation files.

Usage:
    python3 token_counter.py --text "Your message here"
    python3 token_counter.py --file conversation.json
    python3 token_counter.py --file history.json --threshold 0.7
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import tiktoken
except ImportError:
    print("Error: tiktoken not installed. Run: pip install tiktoken", file=sys.stderr)
    sys.exit(1)

# Claude uses cl100k_base encoding (same as GPT-4)
ENCODING = tiktoken.get_encoding("cl100k_base")

# Model context limits
MODEL_LIMITS = {
    "claude-3-opus": 200_000,
    "claude-3-sonnet": 200_000,
    "claude-3-haiku": 200_000,
    "claude-3.5-sonnet": 200_000,
    "claude-sonnet-4": 200_000,
    "claude-opus-4": 200_000,
    "default": 200_000,
}


def count_tokens(text: str) -> int:
    """Count tokens in a string."""
    return len(ENCODING.encode(text))


def count_tokens_in_messages(messages: list[dict]) -> int:
    """Count tokens in a list of messages (OpenAI/Anthropic format)."""
    total = 0
    for msg in messages:
        # Handle different message formats
        if isinstance(msg, dict):
            content = msg.get("content", "")
            if isinstance(content, str):
                total += count_tokens(content)
            elif isinstance(content, list):
                # Anthropic format with content blocks
                for block in content:
                    if isinstance(block, dict) and "text" in block:
                        total += count_tokens(block["text"])
            # Add role overhead (~4 tokens per message)
            total += 4
    return total


def load_and_count_file(file_path: Path) -> int:
    """Load a JSON file and count tokens."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if isinstance(data, list):
        # Array of messages
        return count_tokens_in_messages(data)
    elif isinstance(data, dict):
        if "messages" in data:
            return count_tokens_in_messages(data["messages"])
        elif "content" in data:
            return count_tokens(data["content"])
        else:
            # Count entire JSON as string
            return count_tokens(json.dumps(data))
    elif isinstance(data, str):
        return count_tokens(data)
    else:
        return count_tokens(str(data))


def main() -> None:
    ap = argparse.ArgumentParser(description="Count tokens in text or files")
    ap.add_argument("--text", "-t", help="Text to count tokens in")
    ap.add_argument("--file", "-f", type=Path, help="JSON file to count tokens in")
    ap.add_argument("--model", "-m", default="default", help="Model name for context limit")
    ap.add_argument("--threshold", type=float, help="Exit with code 1 if usage exceeds threshold (0.0-1.0)")
    ap.add_argument("--quiet", "-q", action="store_true", help="Only output JSON, no warnings")
    args = ap.parse_args()

    if not args.text and not args.file:
        # Read from stdin
        text = sys.stdin.read()
        tokens = count_tokens(text)
    elif args.text:
        tokens = count_tokens(args.text)
    elif args.file:
        if not args.file.exists():
            print(json.dumps({"error": f"File not found: {args.file}"}))
            sys.exit(1)
        tokens = load_and_count_file(args.file)
    else:
        tokens = 0

    limit = MODEL_LIMITS.get(args.model, MODEL_LIMITS["default"])
    percent = tokens / limit
    remaining = limit - tokens

    result = {
        "tokens": tokens,
        "limit": limit,
        "percent": round(percent, 4),
        "remaining": remaining,
        "model": args.model,
    }

    # Add warning levels
    if percent >= 0.9:
        result["warning"] = "CRITICAL"
        result["message"] = "Context nearly full! Compress immediately."
    elif percent >= 0.8:
        result["warning"] = "HIGH"
        result["message"] = "Compress now to avoid overflow."
    elif percent >= 0.7:
        result["warning"] = "MEDIUM"
        result["message"] = "Consider compressing soon."
    else:
        result["warning"] = "OK"

    print(json.dumps(result, ensure_ascii=False))

    # Exit with code 1 if threshold exceeded
    if args.threshold is not None and percent > args.threshold:
        if not args.quiet:
            print(f"Threshold {args.threshold} exceeded: {percent:.2%}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
