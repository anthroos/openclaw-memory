#!/usr/bin/env python3
"""Track AI costs and budget."""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, date
from pathlib import Path

PRICING = {"claude-3-opus": {"in": 15, "out": 75}, "claude-3-sonnet": {"in": 3, "out": 15},
           "claude-3-haiku": {"in": 0.25, "out": 1.25}, "default": {"in": 3, "out": 15}}

def get_price(model):
    for k,v in PRICING.items():
        if k in model.lower(): return v
    return PRICING["default"]

def calc_cost(model, inp, out):
    p = get_price(model)
    return (inp/1e6)*p["in"] + (out/1e6)*p["out"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", "-s", type=Path, default=Path("state.json"))
    ap.add_argument("--log-usage", "-l", action="store_true")
    ap.add_argument("--model", "-m")
    ap.add_argument("--input-tokens", type=int)
    ap.add_argument("--output-tokens", type=int)
    ap.add_argument("--alert-at", type=float)
    args = ap.parse_args()

    state = json.loads(args.state.read_text()) if args.state.exists() else {"usage": [], "daily": {}}
    
    if args.log_usage and args.model:
        cost = calc_cost(args.model, args.input_tokens or 0, args.output_tokens or 0)
        entry = {"ts": datetime.now().isoformat(), "date": date.today().isoformat(),
                 "model": args.model, "in": args.input_tokens, "out": args.output_tokens, "cost": round(cost,6)}
        state["usage"].append(entry)
        today = date.today().isoformat()
        state["daily"][today] = state["daily"].get(today, 0) + cost
        args.state.write_text(json.dumps(state, indent=2))
        print(json.dumps({"logged": entry}, indent=2))
        return

    today = date.today().isoformat()
    daily = state["daily"].get(today, 0)
    total = sum(state["daily"].values())
    result = {"daily_cost": round(daily, 4), "total_cost": round(total, 4)}
    if args.alert_at:
        result["alert"] = daily >= args.alert_at
    print(json.dumps(result, indent=2))

if __name__ == "__main__": main()
