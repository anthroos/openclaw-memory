#!/usr/bin/env python3
"""Compress conversation history by summarizing old messages.

Keeps recent messages verbatim, summarizes older ones using Claude Haiku.

Usage:
    python3 compressor.py --input history.json --output compressed.json
    python3 compressor.py --input history.json --keep-recent 5
    python3 compressor.py --input history.json --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import tiktoken
except ImportError:
    print("Error: tiktoken not installed. Run: pip install tiktoken", file=sys.stderr)
    sys.exit(1)

try:
    import anthropic
except ImportError:
    anthropic = None

ENCODING = tiktoken.get_encoding("cl100k_base")

# Use Haiku for compression (cheapest)
COMPRESSION_MODEL = "claude-3-haiku-20240307"

SUMMARY_PROMPT = """Summarize this conversation segment concisely. Preserve:
- Key decisions made
- Important facts mentioned
- Action items agreed upon
- Names and specific details that might be referenced later

Keep the summary under 500 words. Format as bullet points.

Conversation to summarize:
{conversation}"""


def count_tokens(text: str) -> int:
    """Count tokens in text."""
    return len(ENCODING.encode(text))


def messages_to_text(messages: list[dict]) -> str:
    """Convert messages to readable text."""
    lines = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                block.get("text", "") for block in content if isinstance(block, dict)
            )
        lines.append(f"[{role}]: {content}")
    return "\n\n".join(lines)


def summarize_with_claude(text: str, api_key: str | None = None) -> str:
    """Summarize text using Claude Haiku."""
    if anthropic is None:
        raise RuntimeError("anthropic package not installed")
    
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    
    client = anthropic.Anthropic(api_key=key)
    
    response = client.messages.create(
        model=COMPRESSION_MODEL,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": SUMMARY_PROMPT.format(conversation=text),
            }
        ],
    )
    
    return response.content[0].text


def compress_messages(
    messages: list[dict],
    keep_recent: int = 5,
    batch_size: int = 10,
    api_key: str | None = None,
    dry_run: bool = False,
) -> tuple[list[dict], dict]:
    """Compress messages by summarizing old ones.
    
    Returns:
        Tuple of (compressed_messages, stats)
    """
    if len(messages) <= keep_recent:
        return messages, {"compressed": False, "reason": "Not enough messages to compress"}
    
    # Split messages
    old_messages = messages[:-keep_recent]
    recent_messages = messages[-keep_recent:]
    
    # Count tokens before
    old_text = messages_to_text(old_messages)
    old_tokens = count_tokens(old_text)
    recent_tokens = sum(
        count_tokens(m.get("content", "") if isinstance(m.get("content"), str) else str(m.get("content", "")))
        for m in recent_messages
    )
    
    stats = {
        "original_messages": len(messages),
        "old_messages_count": len(old_messages),
        "recent_messages_count": len(recent_messages),
        "old_tokens": old_tokens,
        "recent_tokens": recent_tokens,
        "total_tokens_before": old_tokens + recent_tokens,
    }
    
    if dry_run:
        stats["dry_run"] = True
        stats["would_compress"] = len(old_messages)
        return messages, stats
    
    # Compress old messages in batches
    summaries = []
    for i in range(0, len(old_messages), batch_size):
        batch = old_messages[i:i + batch_size]
        batch_text = messages_to_text(batch)
        
        if anthropic is not None:
            try:
                summary = summarize_with_claude(batch_text, api_key)
                summaries.append(summary)
            except Exception as e:
                # Fallback: just truncate
                summaries.append(f"[Summary of {len(batch)} messages - compression failed: {e}]")
        else:
            # No API available, create placeholder
            summaries.append(f"[Summary of {len(batch)} messages from conversation history]")
    
    # Create compressed history
    combined_summary = "\n\n---\n\n".join(summaries)
    summary_tokens = count_tokens(combined_summary)
    
    compressed_messages = [
        {
            "role": "system",
            "content": f"[COMPRESSED HISTORY - {datetime.now().isoformat()}]\n\n{combined_summary}",
            "_meta": {
                "compressed": True,
                "original_messages": len(old_messages),
                "compressed_at": datetime.now().isoformat(),
            },
        }
    ] + recent_messages
    
    stats.update({
        "compressed": True,
        "summary_tokens": summary_tokens,
        "total_tokens_after": summary_tokens + recent_tokens,
        "tokens_saved": old_tokens - summary_tokens,
        "compression_ratio": round(summary_tokens / old_tokens, 2) if old_tokens > 0 else 0,
    })
    
    return compressed_messages, stats


def main() -> None:
    ap = argparse.ArgumentParser(description="Compress conversation history")
    ap.add_argument("--input", "-i", type=Path, required=True, help="Input JSON file")
    ap.add_argument("--output", "-o", type=Path, help="Output JSON file (default: overwrite input)")
    ap.add_argument("--keep-recent", "-k", type=int, default=5, help="Number of recent messages to keep verbatim")
    ap.add_argument("--batch-size", "-b", type=int, default=10, help="Messages per compression batch")
    ap.add_argument("--dry-run", "-n", action="store_true", help="Show what would be compressed without doing it")
    ap.add_argument("--api-key", help="Anthropic API key (or use ANTHROPIC_API_KEY env)")
    args = ap.parse_args()

    if not args.input.exists():
        print(json.dumps({"error": f"File not found: {args.input}"}))
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle different formats
    if isinstance(data, list):
        messages = data
        wrapper = None
    elif isinstance(data, dict) and "messages" in data:
        messages = data["messages"]
        wrapper = data
    else:
        print(json.dumps({"error": "Unsupported format. Expected array of messages or {messages: [...]}"}))
        sys.exit(1)

    compressed, stats = compress_messages(
        messages,
        keep_recent=args.keep_recent,
        batch_size=args.batch_size,
        api_key=args.api_key,
        dry_run=args.dry_run,
    )

    # Output stats
    print(json.dumps(stats, ensure_ascii=False, indent=2))

    if not args.dry_run and stats.get("compressed"):
        # Save compressed messages
        output_path = args.output or args.input
        
        if wrapper is not None:
            wrapper["messages"] = compressed
            wrapper["_compression_meta"] = stats
            output_data = wrapper
        else:
            output_data = compressed
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\nSaved to: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
