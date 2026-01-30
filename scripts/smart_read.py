#!/usr/bin/env python3
"""Smart file reader with context-aware summarization."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

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

def extract_python_signatures(content):
    result = []
    for line in content.split('\n'):
        s = line.lstrip()
        if s.startswith(('import ','from ','class ','def ','async def ')):
            result.append(line)
    return '\n'.join(result)

def extract_js_signatures(content):
    result = []
    for line in content.split('\n'):
        s = line.strip()
        if s.startswith(('import ','export ','function ','async function ','class ','const ')) and ('=>' in s or '{' in s or 'class ' in s):
            result.append(line)
    return '\n'.join(result)

def smart_read(file_path, context_percent=0.5, signatures_only=False, force_summary=False, force_full=False):
    path = Path(file_path)
    if not path.exists(): return {"error": f"Not found: {file_path}"}
    
    content = path.read_text(errors="replace")
    tokens = count_tokens(content)
    budget = get_budget(context_percent)
    
    result = {"file": str(path.absolute()), "file_tokens": tokens, "file_lines": content.count('\n')+1,
              "context_percent": context_percent, "output_budget": budget}
    
    if signatures_only:
        ext = path.suffix.lower()
        sigs = extract_python_signatures(content) if ext in ['.py'] else extract_js_signatures(content) if ext in ['.js','.ts'] else f"[Not supported for {ext}]"
        sig_tokens = count_tokens(sigs)
        if sig_tokens < tokens * 0.5:
            cache = cache_store(content, source=str(path))
            result.update({"mode": "signatures", "content": sigs, "content_tokens": sig_tokens,
                          "cache_id": cache["cache_id"], "get_full_cmd": cache["retrieve_cmd"]})
        else:
            result.update({"mode": "signatures", "content": sigs, "content_tokens": sig_tokens})
        return result
    
    needs_summary = force_summary or (not force_full and tokens > budget)
    
    if needs_summary:
        cache = cache_store(content, source=str(path))
        lines = content.split('\n')
        summary = '\n'.join(lines[:50]) + (f"\n\n... [{len(lines)-50} more lines] ..." if len(lines)>50 else "")
        result.update({"mode": "summary", "content": summary, "summary_tokens": count_tokens(summary),
                       "savings_percent": round((1-count_tokens(summary)/tokens)*100,1),
                       "cache_id": cache["cache_id"], "get_full_cmd": cache["retrieve_cmd"]})
    else:
        result.update({"mode": "full", "content": content, "content_tokens": tokens})
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", "-f", required=True)
    ap.add_argument("--context-percent", "-c", type=float, default=0.5)
    ap.add_argument("--signatures-only", "-s", action="store_true")
    ap.add_argument("--force-summary", action="store_true")
    ap.add_argument("--force-full", action="store_true")
    ap.add_argument("--quiet", "-q", action="store_true")
    args = ap.parse_args()
    result = smart_read(args.file, args.context_percent, args.signatures_only, args.force_summary, args.force_full)
    print(result.get("content","") if args.quiet else json.dumps(result, indent=2))

if __name__ == "__main__": main()
