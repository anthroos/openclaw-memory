#!/usr/bin/env python3
"""Track AI costs and provide budget alerts.

Usage:
    python3 budget_tracker.py --state state.json
    python3 budget_tracker.py --state state.json --alert-at 5.00
    python3 budget_tracker.py --log-usage --model claude-3-sonnet --input-tokens 1000 --output-tokens 500
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Any

# Model pricing (per 1M tokens) as of 2024
MODEL_PRICING = {
    # Claude 3 family
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    "claude-3-opus": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
    "claude-3-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
    # Claude 3.5 family
    "claude-3-5-sonnet-20240620": {"input": 3.00, "output": 15.00},
    "claude-3.5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    # Claude 4 family (using latest pricing)
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-sonnet-4": {"input": 3.00, "output": 15.00},
    "claude-opus-4-5": {"input": 15.00, "output": 75.00},
    "claude-opus-4": {"input": 15.00, "output": 75.00},
    # Anthropic prefix variants
    "anthropic/claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "anthropic/claude-opus-4-5": {"input": 15.00, "output": 75.00},
    # Default fallback
    "default": {"input": 3.00, "output": 15.00},
}


def get_pricing(model: str) -> dict[str, float]:
    """Get pricing for a model."""
    # Try exact match first
    if model in MODEL_PRICING:
        return MODEL_PRICING[model]
    
    # Try without provider prefix
    if "/" in model:
        model_name = model.split("/")[-1]
        if model_name in MODEL_PRICING:
            return MODEL_PRICING[model_name]
    
    # Try partial match
    model_lower = model.lower()
    for key, pricing in MODEL_PRICING.items():
        if key in model_lower or model_lower in key:
            return pricing
    
    return MODEL_PRICING["default"]


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for a single API call."""
    pricing = get_pricing(model)
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


def load_state(state_path: Path) -> dict[str, Any]:
    """Load state from JSON file."""
    if state_path.exists():
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "usage": [],
        "daily_totals": {},
        "created_at": datetime.now().isoformat(),
    }


def save_state(state: dict[str, Any], state_path: Path) -> None:
    """Save state to JSON file."""
    state["last_updated"] = datetime.now().isoformat()
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def log_usage(
    state: dict[str, Any],
    model: str,
    input_tokens: int,
    output_tokens: int,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Log a usage entry and return the entry."""
    cost = calculate_cost(model, input_tokens, output_tokens)
    today = date.today().isoformat()
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "date": today,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": round(cost, 6),
        "session_id": session_id,
    }
    
    state["usage"].append(entry)
    
    # Update daily total
    if today not in state.get("daily_totals", {}):
        state["daily_totals"] = state.get("daily_totals", {})
        state["daily_totals"][today] = {"cost": 0, "input_tokens": 0, "output_tokens": 0, "calls": 0}
    
    state["daily_totals"][today]["cost"] = round(state["daily_totals"][today]["cost"] + cost, 6)
    state["daily_totals"][today]["input_tokens"] += input_tokens
    state["daily_totals"][today]["output_tokens"] += output_tokens
    state["daily_totals"][today]["calls"] += 1
    
    return entry


def get_stats(state: dict[str, Any], session_id: str | None = None) -> dict[str, Any]:
    """Calculate usage statistics."""
    today = date.today().isoformat()
    usage = state.get("usage", [])
    
    # Filter by session if specified
    if session_id:
        usage = [u for u in usage if u.get("session_id") == session_id]
    
    # Today's stats
    today_usage = [u for u in usage if u.get("date") == today]
    today_cost = sum(u.get("cost", 0) for u in today_usage)
    today_input = sum(u.get("input_tokens", 0) for u in today_usage)
    today_output = sum(u.get("output_tokens", 0) for u in today_usage)
    
    # Session stats (last hour)
    now = datetime.now()
    session_usage = [
        u for u in usage
        if datetime.fromisoformat(u["timestamp"]).date() == now.date()
        and (now - datetime.fromisoformat(u["timestamp"])).seconds < 3600
    ]
    session_cost = sum(u.get("cost", 0) for u in session_usage)
    
    # Total stats
    total_cost = sum(u.get("cost", 0) for u in usage)
    
    # Model breakdown
    model_costs: dict[str, float] = {}
    for u in today_usage:
        model = u.get("model", "unknown")
        model_costs[model] = model_costs.get(model, 0) + u.get("cost", 0)
    
    return {
        "session_cost": round(session_cost, 4),
        "daily_cost": round(today_cost, 4),
        "total_cost": round(total_cost, 4),
        "today": {
            "calls": len(today_usage),
            "input_tokens": today_input,
            "output_tokens": today_output,
        },
        "model_breakdown": {k: round(v, 4) for k, v in model_costs.items()},
        "last_updated": state.get("last_updated"),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Track AI costs and budget")
    ap.add_argument("--state", "-s", type=Path, default=Path("state.json"), help="State file path")
    ap.add_argument("--alert-at", type=float, help="Alert if daily cost exceeds this amount")
    ap.add_argument("--session", help="Filter stats by session ID")
    
    # Logging new usage
    ap.add_argument("--log-usage", "-l", action="store_true", help="Log a new usage entry")
    ap.add_argument("--model", "-m", help="Model name for logging")
    ap.add_argument("--input-tokens", type=int, help="Input tokens for logging")
    ap.add_argument("--output-tokens", type=int, help="Output tokens for logging")
    ap.add_argument("--session-id", help="Session ID for logging")
    
    args = ap.parse_args()

    state = load_state(args.state)

    if args.log_usage:
        if not all([args.model, args.input_tokens is not None, args.output_tokens is not None]):
            print(json.dumps({"error": "log-usage requires --model, --input-tokens, and --output-tokens"}))
            sys.exit(1)
        
        entry = log_usage(
            state,
            args.model,
            args.input_tokens,
            args.output_tokens,
            args.session_id,
        )
        save_state(state, args.state)
        print(json.dumps({"logged": entry}, ensure_ascii=False, indent=2))
        return

    # Get and display stats
    stats = get_stats(state, args.session)
    
    # Check alert threshold
    if args.alert_at is not None:
        stats["alert_threshold"] = args.alert_at
        stats["alert"] = stats["daily_cost"] >= args.alert_at
        if stats["alert"]:
            stats["alert_message"] = f"Daily cost ${stats['daily_cost']:.2f} exceeds ${args.alert_at:.2f}"

    print(json.dumps(stats, ensure_ascii=False, indent=2))

    # Exit with code 1 if alert triggered
    if stats.get("alert"):
        sys.exit(1)


if __name__ == "__main__":
    main()
