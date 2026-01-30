#!/usr/bin/env python3
"""Dashboard server for memory monitoring.

Serves the dashboard HTML and provides API endpoints for metrics.

Usage:
    python3 dashboard_server.py --port 8765
    python3 dashboard_server.py --port 8765 --state state.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from aiohttp import web
except ImportError:
    print("Error: aiohttp not installed. Run: pip install aiohttp", file=sys.stderr)
    sys.exit(1)

# Global state
STATE: dict[str, Any] = {
    "context": {
        "tokens": 0,
        "limit": 200000,
        "percent": 0,
        "warning": "OK",
    },
    "cost": {
        "session": 0,
        "daily": 0,
        "alert": False,
    },
    "compression": {
        "last_compressed": None,
        "compressions_today": 0,
        "tokens_saved": 0,
    },
    "agents": {
        "active": 0,
        "queued": 0,
        "completed_today": 0,
    },
    "last_updated": datetime.now().isoformat(),
}

STATE_FILE: Path | None = None
DASHBOARD_DIR: Path = Path(__file__).parent.parent / "dashboard"


def load_state_file() -> None:
    """Load state from file if configured."""
    global STATE
    if STATE_FILE and STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Merge cost data if present
            if "daily_totals" in data:
                today = datetime.now().strftime("%Y-%m-%d")
                today_data = data["daily_totals"].get(today, {})
                STATE["cost"]["daily"] = today_data.get("cost", 0)
            
            # Get recent usage for session cost
            usage = data.get("usage", [])
            now = datetime.now()
            session_usage = [
                u for u in usage
                if (now - datetime.fromisoformat(u.get("timestamp", now.isoformat()))).seconds < 3600
            ]
            STATE["cost"]["session"] = sum(u.get("cost", 0) for u in session_usage)
            
        except Exception as e:
            print(f"Warning: Could not load state file: {e}", file=sys.stderr)


async def handle_index(request: web.Request) -> web.Response:
    """Serve the dashboard HTML."""
    html_path = DASHBOARD_DIR / "index.html"
    if html_path.exists():
        return web.FileResponse(html_path)
    
    # Fallback inline HTML
    return web.Response(
        text="""<!DOCTYPE html>
<html>
<head><title>Memory Manager Dashboard</title></head>
<body>
<h1>Dashboard not found</h1>
<p>Create dashboard/index.html in the skill folder.</p>
</body>
</html>""",
        content_type="text/html",
    )


async def handle_api_state(request: web.Request) -> web.Response:
    """Return current state as JSON."""
    load_state_file()
    STATE["last_updated"] = datetime.now().isoformat()
    return web.json_response(STATE)


async def handle_api_update(request: web.Request) -> web.Response:
    """Update state with new data."""
    try:
        data = await request.json()
        
        # Update context metrics
        if "context" in data:
            STATE["context"].update(data["context"])
            tokens = STATE["context"].get("tokens", 0)
            limit = STATE["context"].get("limit", 200000)
            percent = tokens / limit if limit > 0 else 0
            STATE["context"]["percent"] = round(percent, 4)
            
            # Set warning level
            if percent >= 0.9:
                STATE["context"]["warning"] = "CRITICAL"
            elif percent >= 0.8:
                STATE["context"]["warning"] = "HIGH"
            elif percent >= 0.7:
                STATE["context"]["warning"] = "MEDIUM"
            else:
                STATE["context"]["warning"] = "OK"
        
        if "cost" in data:
            STATE["cost"].update(data["cost"])
        
        if "compression" in data:
            STATE["compression"].update(data["compression"])
        
        if "agents" in data:
            STATE["agents"].update(data["agents"])
        
        STATE["last_updated"] = datetime.now().isoformat()
        
        return web.json_response({"status": "ok", "state": STATE})
    
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)


async def handle_api_trigger_compression(request: web.Request) -> web.Response:
    """Trigger compression (placeholder - actual compression done by compressor.py)."""
    STATE["compression"]["last_compressed"] = datetime.now().isoformat()
    STATE["compression"]["compressions_today"] = STATE["compression"].get("compressions_today", 0) + 1
    return web.json_response({"status": "compression_triggered", "state": STATE})


def create_app() -> web.Application:
    """Create the aiohttp application."""
    app = web.Application()
    
    # Routes
    app.router.add_get("/", handle_index)
    app.router.add_get("/api/state", handle_api_state)
    app.router.add_post("/api/update", handle_api_update)
    app.router.add_post("/api/compress", handle_api_trigger_compression)
    
    # Static files from dashboard folder
    if DASHBOARD_DIR.exists():
        app.router.add_static("/static", DASHBOARD_DIR)
    
    return app


def main() -> None:
    ap = argparse.ArgumentParser(description="Memory Manager Dashboard Server")
    ap.add_argument("--port", "-p", type=int, default=8765, help="Port to listen on")
    ap.add_argument("--host", "-H", default="127.0.0.1", help="Host to bind to")
    ap.add_argument("--state", "-s", type=Path, help="State file to monitor")
    args = ap.parse_args()

    global STATE_FILE
    STATE_FILE = args.state

    print(f"Starting Memory Manager Dashboard on http://{args.host}:{args.port}", file=sys.stderr)
    print(f"State file: {args.state or 'not configured'}", file=sys.stderr)
    
    app = create_app()
    web.run_app(app, host=args.host, port=args.port, print=None)


if __name__ == "__main__":
    main()
