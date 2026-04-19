#!/usr/bin/env python3
"""
Run on the VM:  python3 server.py
Then open in your browser:  http://localhost:9876
"""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "start_obstacles_custom.sh")
INDEX_PATH = os.path.join(SCRIPT_DIR, "index.html")
PORT = 9876


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"  {self.address_string()} {format % args}")

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            try:
                with open(INDEX_PATH, "rb") as f:
                    html = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)
            except OSError as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"Failed to load index: {e}".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/save":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                script = data.get("script", "")
                os.makedirs(SCRIPT_DIR, exist_ok=True)
                with open(SCRIPT_PATH, "w") as f:
                    f.write(script)
                os.chmod(SCRIPT_PATH, 0o755)
                print(f"  ✓ Wrote {SCRIPT_PATH}")
                resp = json.dumps({"ok": True}).encode()
            except Exception as e:
                print(f"  ✗ Error writing script: {e}")
                resp = json.dumps({"ok": False, "error": str(e)}).encode()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(resp))
            self.end_headers()
            self.wfile.write(resp)
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"ROB450 obstacle server running.")
    print(f"  Open in your browser: http://localhost:{PORT}")
    print(f"  Scripts saved to: {SCRIPT_PATH}")
    print(f"  Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")