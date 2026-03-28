#!/usr/bin/env python3
# Vibe coded by Claude
#
# Supervisor/proxy for GameExtractorServer.jar
# Spawns N worker JVMs and load-balances /extract requests across them.
# /detect, /list, /status are forwarded to any available worker.
#
# Usage: python3 supervisor.py [--workers=10] [--port=25499]

import argparse
import http.client
import json
import os
import signal
import subprocess
import sys
import threading
import time
from collections import deque
from http.server import HTTPServer, BaseHTTPRequestHandler

# ── CLI args ──────────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser(description="Game Extractor Supervisor")
parser.add_argument("--workers", type=int, default=10)
parser.add_argument("--port", type=int, default=25499)
args = parser.parse_args()

NUM_WORKERS = args.workers
SUPERVISOR_PORT = args.port

# ── Constants ─────────────────────────────────────────────────────────────────

JAVA_ARGS = [
    "java",
    "-Djava.awt.headless=true",
    "--add-exports", "java.desktop/sun.awt.shell=ALL-UNNAMED",
    "--add-exports", "java.desktop/com.sun.imageio.plugins.bmp=ALL-UNNAMED",
    "--add-exports", "java.desktop/com.sun.imageio.plugins.gif=ALL-UNNAMED",
    "--add-exports", "java.desktop/com.sun.imageio.plugins.png=ALL-UNNAMED",
    "--add-exports", "java.desktop/com.sun.imageio.plugins.wbmp=ALL-UNNAMED",
    "-jar", "GameExtractorServer.jar",
]

STARTING = 0
READY = 1
BUSY = 2
DEAD = 3

EXTRACT_TIMEOUT = 600       # 10 min
STATELESS_TIMEOUT = 30      # 30s
QUEUE_TIMEOUT = 600         # 10 min
STARTUP_TIMEOUT = 120       # 2 min
MAX_RAPID_RESTARTS = 5
RAPID_RESTART_WINDOW = 60

# ── Worker pool ───────────────────────────────────────────────────────────────

class Worker:
    def __init__(self, index, port):
        self.index = index
        self.port = port
        self.state = DEAD
        self.process = None
        self.restart_timestamps = []
        self.lock = threading.Lock()

workers = []
pool_lock = threading.Lock()
extract_queue = deque()
queue_event = threading.Event()
shutdown_flag = threading.Event()
start_time = time.time()


def spawn_worker(worker):
    cmd = JAVA_ARGS + [f"--port={worker.port}"]
    cwd = os.path.dirname(os.path.abspath(__file__))
    proc = subprocess.Popen(
        cmd, cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    worker.process = proc
    worker.state = STARTING

    # Monitor stdout for readiness in a thread
    def monitor_stdout():
        buf = b""
        try:
            for chunk in iter(lambda: proc.stdout.read1(4096) if hasattr(proc.stdout, 'read1') else proc.stdout.read(4096), b""):
                if not chunk:
                    break
                buf += chunk
                if worker.state == STARTING and b"Server listening on port" in buf:
                    worker.state = READY
                    print(f"  Worker {worker.index} ready on port {worker.port}", flush=True)
                    queue_event.set()  # wake queue drainer
                    break
        except Exception:
            pass
        # Keep draining stdout to prevent blocking
        try:
            while proc.poll() is None:
                proc.stdout.read(4096)
        except Exception:
            pass

    def monitor_stderr():
        try:
            while proc.poll() is None:
                line = proc.stderr.readline()
                if not line:
                    break
        except Exception:
            pass

    threading.Thread(target=monitor_stdout, daemon=True).start()
    threading.Thread(target=monitor_stderr, daemon=True).start()

    # Monitor for exit
    def monitor_exit():
        proc.wait()
        worker.state = DEAD
        worker.process = None
        if shutdown_flag.is_set():
            return
        print(f"  Worker {worker.index} exited (code={proc.returncode})", flush=True)

        now = time.time()
        worker.restart_timestamps = [t for t in worker.restart_timestamps if now - t < RAPID_RESTART_WINDOW]
        worker.restart_timestamps.append(now)
        if len(worker.restart_timestamps) >= MAX_RAPID_RESTARTS:
            print(f"  Worker {worker.index} restart-looping, backing off 30s", flush=True)
            time.sleep(30)
            worker.restart_timestamps = []

        if not shutdown_flag.is_set():
            time.sleep(1)
            spawn_worker(worker)

    threading.Thread(target=monitor_exit, daemon=True).start()

    # Startup timeout
    def startup_timeout():
        time.sleep(STARTUP_TIMEOUT)
        if worker.state == STARTING:
            print(f"  Worker {worker.index} startup timeout, killing", flush=True)
            try:
                proc.kill()
            except Exception:
                pass

    threading.Thread(target=startup_timeout, daemon=True).start()


def find_free_worker():
    """Find a READY worker for /extract (exclusive access)."""
    for w in workers:
        if w.state == READY:
            return w
    return None


def find_any_worker():
    """Find any READY or BUSY worker for stateless requests."""
    for w in workers:
        if w.state in (READY, BUSY):
            return w
    return None


# ── Proxying ──────────────────────────────────────────────────────────────────

def proxy_to_worker(worker, method, path, body, timeout=STATELESS_TIMEOUT):
    """Send request to worker, return (status, headers, body). Thread-safe."""
    try:
        conn = http.client.HTTPConnection("127.0.0.1", worker.port, timeout=timeout)
        headers = {"Content-Type": "application/json"} if body else {}
        conn.request(method, path, body=body, headers=headers)
        resp = conn.getresponse()
        resp_body = resp.read()
        resp_headers = dict(resp.getheaders())
        status = resp.status
        conn.close()
        return status, resp_headers, resp_body
    except Exception as e:
        return 502, {"Content-Type": "application/json"}, json.dumps({"error": f"Worker {worker.index}: {e}"}).encode()


# ── Queue drainer thread ─────────────────────────────────────────────────────

def queue_drainer():
    """Background thread that processes queued /extract requests."""
    while not shutdown_flag.is_set():
        queue_event.wait(timeout=1.0)
        queue_event.clear()

        while extract_queue and not shutdown_flag.is_set():
            worker = find_free_worker()
            if not worker:
                break

            entry = extract_queue.popleft()
            result_event, method, path, body = entry["event"], entry["method"], entry["path"], entry["body"]

            if entry.get("aborted"):
                continue

            worker.state = BUSY
            try:
                status, headers, resp_body = proxy_to_worker(worker, method, path, body, timeout=EXTRACT_TIMEOUT)
                entry["result"] = (status, headers, resp_body)
            except Exception as e:
                entry["result"] = (502, {"Content-Type": "application/json"}, json.dumps({"error": str(e)}).encode())
            finally:
                worker.state = READY
                result_event.set()
                queue_event.set()  # check if more queued items can be served


threading.Thread(target=queue_drainer, daemon=True).start()


# ── HTTP handler ──────────────────────────────────────────────────────────────

class SupervisorHandler(BaseHTTPRequestHandler):
    # Suppress default logging
    def log_message(self, format, *a):
        pass

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length > 0 else b""

    def _send_response(self, status, headers, body):
        self.send_response(status)
        for k, v in headers.items():
            if k.lower() not in ("transfer-encoding", "connection"):
                self.send_header(k, v)
        if "Content-Length" not in headers and "content-length" not in headers:
            self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status, obj):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle(self):
        path = self.path.split("?")[0]
        body = self._read_body()

        # Supervisor status
        if path == "/supervisor/status":
            self._send_json(200, {
                "workers": len(workers),
                "ready": sum(1 for w in workers if w.state == READY),
                "busy": sum(1 for w in workers if w.state == BUSY),
                "starting": sum(1 for w in workers if w.state == STARTING),
                "dead": sum(1 for w in workers if w.state == DEAD),
                "queueDepth": len(extract_queue),
                "uptime": int(time.time() - start_time),
            })
            return

        # /extract — route to free worker or queue
        if path == "/extract":
            worker = find_free_worker()
            if worker:
                worker.state = BUSY
                try:
                    status, headers, resp_body = proxy_to_worker(worker, self.command, path, body, timeout=EXTRACT_TIMEOUT)
                    self._send_response(status, headers, resp_body)
                finally:
                    worker.state = READY
                    queue_event.set()
                return

            # All workers busy — queue this request
            entry = {
                "event": threading.Event(),
                "method": self.command,
                "path": path,
                "body": body,
                "result": None,
                "aborted": False,
            }
            extract_queue.append(entry)
            queue_event.set()

            # Wait for result (blocks this handler thread, which is fine — HTTPServer uses threads)
            got_result = entry["event"].wait(timeout=QUEUE_TIMEOUT)
            if not got_result or entry["result"] is None:
                entry["aborted"] = True
                self._send_json(504, {"error": "Queue timeout — all workers busy"})
                return

            status, headers, resp_body = entry["result"]
            self._send_response(status, headers, resp_body)
            return

        # Stateless endpoints: /detect, /list, /status
        worker = find_any_worker()
        if not worker:
            self._send_json(503, {"error": "No workers available"})
            return

        status, headers, resp_body = proxy_to_worker(worker, self.command, path, body, timeout=STATELESS_TIMEOUT)
        self._send_response(status, headers, resp_body)

    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()


class ThreadedHTTPServer(HTTPServer):
    """Handle each request in a new thread."""
    def process_request(self, request, client_address):
        t = threading.Thread(target=self.process_request_thread, args=(request, client_address))
        t.daemon = True
        t.start()

    def process_request_thread(self, request, client_address):
        try:
            self.finish_request(request, client_address)
        except Exception:
            self.handle_error(request, client_address)
        finally:
            self.shutdown_request(request)


# ── Shutdown ──────────────────────────────────────────────────────────────────

def shutdown_handler(signum, frame):
    print("\nShutting down...", flush=True)
    shutdown_flag.set()
    queue_event.set()

    # Reject queued requests
    while extract_queue:
        entry = extract_queue.popleft()
        entry["aborted"] = True
        entry["event"].set()

    # Kill workers
    for w in workers:
        if w.process:
            try:
                w.process.terminate()
            except Exception:
                pass

    time.sleep(2)

    for w in workers:
        if w.process:
            try:
                w.process.kill()
            except Exception:
                pass

    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

# ── Startup ───────────────────────────────────────────────────────────────────

print(f"=== Game Extractor Supervisor ===")
print(f"  Workers: {NUM_WORKERS}")
print(f"  Port: {SUPERVISOR_PORT}")
print(f"  Worker ports: {SUPERVISOR_PORT + 1}-{SUPERVISOR_PORT + NUM_WORKERS}")
print(flush=True)
print("Starting workers...", flush=True)

for i in range(NUM_WORKERS):
    w = Worker(i, SUPERVISOR_PORT + 1 + i)
    workers.append(w)
    spawn_worker(w)

# Wait for all workers to be ready
deadline = time.time() + STARTUP_TIMEOUT
while time.time() < deadline:
    ready = sum(1 for w in workers if w.state == READY)
    if ready == NUM_WORKERS:
        break
    time.sleep(0.5)

ready = sum(1 for w in workers if w.state == READY)
if ready == 0:
    print("Fatal: No workers became ready within timeout", flush=True)
    sys.exit(1)
elif ready < NUM_WORKERS:
    print(f"\nWarning: Only {ready}/{NUM_WORKERS} workers ready, starting anyway...", flush=True)

print(flush=True)

httpd = ThreadedHTTPServer(("", SUPERVISOR_PORT), SupervisorHandler)
print(f"Server listening on port {SUPERVISOR_PORT}")
print(f"  GET  /status")
print(f"  GET  /list")
print(f"  POST /detect  {{\"filePath\": \"...\"}}")
print(f"  POST /extract {{\"inputFilePath\": \"...\", \"outputDirPath\": \"...\", \"codes\": [\"...\"]}}")
print(f"  GET  /supervisor/status", flush=True)

httpd.serve_forever()
