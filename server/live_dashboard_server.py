"""Unprivileged loopback HTTP server for the live strategy dashboard."""

from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path("/opt/strategy-dashboard/site")
DATA_URL = "/afml-study/results/_server_live/"
LIVE_FILES = {
    f"{prefix}_{suffix}"
    for prefix in ("week33", "week42")
    for suffix in ("status.json", "state.json", "equity_history.csv")
}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        if urlsplit(self.path).path.startswith(DATA_URL) or self.path == "/api/health":
            self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/api/health":
            payload = json.dumps({"ok": True, "read_only": True}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if path.startswith(DATA_URL) and path.removeprefix(DATA_URL) not in LIVE_FILES | {"week33_candles.json"}:
            self.send_error(404)
            return
        super().do_GET()

    def do_POST(self) -> None:
        self.send_error(405)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
