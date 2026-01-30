#!/usr/bin/env python3
"""Smart URL fetcher with context-aware summarization."""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
from urllib.request import urlopen, Request

sys.path.insert(0, str(Path(__file__).parent))
from cache_manager import store as cache_store

try:
    import tiktoken
    ENCODING = tiktoken.get_encoding("cl100k_base")
    def count_tokens(text): return len(ENCODING.encode(text))
except: 
    def count_tokens(text): return len(text)//4

def get_budget(ctx):
    if ctx < 0.4: return 10000
    if ctx < 0.6: return 5000
    if ctx < 0.8: return 2000
    return 500

def fetch_url(url, max_chars=100000):
    try:
        req = Request(url, headers={"User-Agent": "SmartFetch/1.0"})
        with urlopen(req, timeout=30) as r:
            content = r.read().decode("utf-8", errors="replace")[:max_chars]
            return content, {"url": url, "status": r.status}
    except Exception as e:
        return str(e), {"url": url, "error": True}

def summarize(content, max_tokens=2000):
    lines = content.split('\n')
    key = [l.strip() for l in lines if l.strip().startswith(('#','-','*','1.')) or (10 < len(l.strip()) < 200)]
    return '\n'.join(key[:50]) if key else content[:max_tokens*4]

def smart_fetch(url, context_percent=0.5, force_summary=False, force_full=False):
    content, meta = fetch_url(url)
    if meta.get("error"): return {"error": content, "metadata": meta}
    
    tokens = count_tokens(content)
    budget = get_budget(context_percent)
    needs_summary = force_summary or (not force_full and tokens > budget)
    
    result = {"url": url, "fetched_tokens": tokens, "context_percent": context_percent, "output_budget": budget}
    
    if needs_summary:
        cache = cache_store(content, source=url)
        summary = summarize(content, min(budget, 2000))
        result.update({"mode": "summary", "content": summary, "summary_tokens": count_tokens(summary),
                       "savings_percent": round((1-count_tokens(summary)/tokens)*100,1),
                       "cache_id": cache["cache_id"], "get_full_cmd": cache["retrieve_cmd"]})
    else:
        result.update({"mode": "full", "content": content, "content_tokens": tokens})
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", "-u", required=True)
    ap.add_argument("--context-percent", "-c", type=float, default=0.5)
    ap.add_argument("--force-summary", "-s", action="store_true")
    ap.add_argument("--force-full", "-f", action="store_true")
    ap.add_argument("--quiet", "-q", action="store_true")
    args = ap.parse_args()
    result = smart_fetch(args.url, args.context_percent, args.force_summary, args.force_full)
    print(result.get("content","") if args.quiet else json.dumps(result, indent=2))

if __name__ == "__main__": main()
