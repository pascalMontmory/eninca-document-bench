"""Loopback-only browser UI; no remote API, uploads, telemetry or CDN assets."""
import argparse
import fcntl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import threading
import traceback
from urllib.parse import parse_qs, urlsplit
import webbrowser

from .app import Conflict, Demo

STATIC = Path(__file__).parent / "static"


def handler_for(app, token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # Do not log queries or document content.

        def reply(self, status, data, content_type="application/json; charset=utf-8", download=False):
            payload = json.dumps(data, ensure_ascii=False, allow_nan=False).encode() if isinstance(data, dict) else data
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; "
                             "img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            if download:
                self.send_header("Content-Disposition", 'attachment; filename="eninca-decisions.csv"')
            self.end_headers()
            try:
                self.wfile.write(payload)
            except (BrokenPipeError, ConnectionResetError):
                pass  # A closed/reloaded tab is not an application failure.

        def allowed_host(self):
            host = f"127.0.0.1:{self.server.server_port}"
            return self.headers.get("Host") == host and self.headers.get("Origin", "http://" + host) == "http://" + host

        def do_GET(self):
            if not self.allowed_host():
                return self.reply(403, {"error": "local_origin_required"})
            url = urlsplit(self.path)
            assets = {"/": ("index.html", "text/html; charset=utf-8"),
                      "/icon.svg": ("icon.svg", "image/svg+xml"),
                      "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                      "/style.css": ("style.css", "text/css; charset=utf-8")}
            if url.path in assets:
                filename, mime = assets[url.path]
                return self.reply(200, (STATIC / filename).read_bytes(), mime)
            if url.path == "/api/status":
                return self.reply(200, dict(app.status(), token=token))
            if not app.status()["ready"]:
                return self.reply(503, {"error": "not_ready"})
            try:
                if url.path == "/api/state":
                    return self.reply(200, app.snapshot())
                if url.path == "/api/document":
                    return self.reply(200, app.document(parse_qs(url.query)["id"][0]))
                if url.path == "/api/export.csv":
                    return self.reply(200, app.export_csv(), "text/csv; charset=utf-8", download=True)
            except (KeyError, ValueError):
                return self.reply(404, {"error": "not_found"})
            return self.reply(404, {"error": "not_found"})

        def do_POST(self):
            if not self.allowed_host() or self.headers.get("X-Demo-Token") != token:
                return self.reply(403, {"error": "local_origin_required"})
            if not app.status()["ready"]:
                return self.reply(503, {"error": "not_ready"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 16384 or self.headers.get("Content-Type") != "application/json":
                    raise ValueError("invalid_request")
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError("invalid_request")
                if self.path == "/api/search":
                    return self.reply(200, app.search(data.get("query")))
                if self.path == "/api/review":
                    if set(data) != {"document_id", "label", "revision"}:
                        raise ValueError("invalid_request")
                    return self.reply(200, app.review(data["document_id"], data["label"], data["revision"]))
                return self.reply(404, {"error": "not_found"})
            except Conflict:
                return self.reply(409, {"error": "stale_review"})
            except (ValueError, TypeError, UnicodeError):
                return self.reply(400, {"error": "invalid_request_or_query"})
            except Exception:
                traceback.print_exc()
                return self.reply(500, {"error": "server_error"})

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--state-dir", default="runs/browser-demo")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("Invalid port")
    state = Path(args.state_dir)
    state.mkdir(parents=True, exist_ok=True)
    # macOS and Linux: one process owns an index/review directory at a time.
    with (state / "server.lock").open("a") as lockfile:
        try:
            fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.exit(1, "Demo already running for this state directory / Démonstration déjà ouverte.\n")
        app = Demo(args.model_dir, state)
        try:
            server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_for(app, secrets.token_urlsafe(32)))
        except OSError as exc:
            parser.exit(1, f"Local port unavailable; try --port 8766. {exc}\n")
        url = f"http://127.0.0.1:{server.server_port}"
        print(f"\nENINCA CONSULTING · Documents\n{url}\nCtrl+C : arrêter / stop\n", flush=True)

        def prepare():
            try:
                app.prepare()
            except Exception:
                traceback.print_exc()
                with app.status_lock:
                    app.error = True

        threading.Thread(target=prepare, daemon=True).start()
        if args.open:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped / Arrêté", flush=True)
        finally:
            server.server_close()


if __name__ == "__main__":
    main()
