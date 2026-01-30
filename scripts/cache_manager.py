#!/usr/bin/env python3
"""Cache manager for storing full tool outputs temporarily."""
from __future__ import annotations
import argparse, hashlib, json, sys, time
from datetime import datetime, timedelta
from pathlib import Path

CACHE_DIR = Path(__file__).parent.parent / "cache"
INDEX_FILE = CACHE_DIR / "index.json"
DEFAULT_TTL = 2

def load_index():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        with open(INDEX_FILE, "w") as f: json.dump({}, f)
    try:
        return json.loads(INDEX_FILE.read_text())
    except: return {}

def save_index(index):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps(index, indent=2))

def store(content, source="unknown", ttl_hours=DEFAULT_TTL):
    cache_id = hashlib.sha256((content + str(time.time())).encode()).hexdigest()[:12]
    cache_file = CACHE_DIR / f"{cache_id}.txt"
    cache_file.write_text(content)
    expires = datetime.now() + timedelta(hours=ttl_hours)
    index = load_index()
    index[cache_id] = {"file": str(cache_file), "source": source, "created": datetime.now().isoformat(), 
                       "expires": expires.isoformat(), "size_bytes": len(content), "tokens_estimated": len(content)//4}
    save_index(index)
    return {"cache_id": cache_id, "expires": expires.isoformat(), "tokens_estimated": len(content)//4,
            "retrieve_cmd": f"python3 {__file__} --get {cache_id}"}

def get(cache_id, section=None):
    index = load_index()
    if cache_id not in index: return {"error": f"Not found: {cache_id}", "found": False}
    entry = index[cache_id]
    cache_file = Path(entry["file"])
    if not cache_file.exists(): return {"error": "File missing", "found": False}
    if datetime.now() > datetime.fromisoformat(entry["expires"]): return {"error": "Expired", "found": False}
    content = cache_file.read_text()
    if section:
        pos = content.lower().find(section.lower())
        if pos == -1: return {"error": f"Section '{section}' not found", "found": False}
        start, end = max(0, pos-500), min(len(content), pos+len(section)+500)
        return {"content": content[start:end], "found": True, "excerpt": True}
    return {"content": content, "found": True, "tokens_estimated": len(content)//4}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", action="store_true")
    ap.add_argument("--get", metavar="ID")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--cleanup", action="store_true")
    ap.add_argument("--content", "-c")
    ap.add_argument("--file", "-f", type=Path)
    ap.add_argument("--source", "-s", default="unknown")
    ap.add_argument("--section")
    args = ap.parse_args()

    if args.store:
        content = args.file.read_text() if args.file else args.content or sys.stdin.read()
        print(json.dumps(store(content, args.source), indent=2))
    elif args.get:
        print(json.dumps(get(args.get, args.section), indent=2))
    elif args.list:
        index = load_index()
        items = [{"cache_id": k, **{x: v[x] for x in ["source","created","expires"]}} for k,v in index.items()]
        print(json.dumps({"count": len(items), "items": items}, indent=2))
    elif args.stats:
        index = load_index()
        total = sum(e.get("size_bytes",0) for e in index.values())
        print(json.dumps({"entries": len(index), "total_bytes": total, "total_mb": round(total/1024/1024,2)}, indent=2))
    elif args.cleanup:
        index = load_index()
        now = datetime.now()
        kept = {k:v for k,v in index.items() if datetime.fromisoformat(v["expires"]) > now}
        removed = len(index) - len(kept)
        save_index(kept)
        print(json.dumps({"removed": removed, "remaining": len(kept)}, indent=2))

if __name__ == "__main__": main()
