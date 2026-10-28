#!/usr/bin/env python3
# Vibe coded by Codex
# Vibe coded by Claude
# Supervisor/proxy for GameExtractorServer.jar. Plugin requests reserve one JVM.

import argparse
import http.client
import json
import math
import os
import signal
import subprocess
import sys
import threading
import time
from collections import deque
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

parser = argparse.ArgumentParser(description="Game Extractor Supervisor")
parser.add_argument("--workers", type=int, default=10)
parser.add_argument("--port", type=int, default=25499)
parser.add_argument("--detect-timeout", type=float, default=30, help="seconds per detection")
parser.add_argument("--extract-timeout", type=float, default=600, help="seconds per extraction")
parser.add_argument("--queue-timeout", type=float, default=600, help="seconds waiting for a worker")
args = parser.parse_args()
if args.workers < 1 or not 0 < args.port < 65536 - args.workers:
    parser.error("workers must be positive and the port range must fit within 1..65535")
if not all(math.isfinite(t) and t > 0 for t in (args.detect_timeout, args.extract_timeout, args.queue_timeout)):
    parser.error("timeouts must be positive")

NUM_WORKERS = args.workers
SUPERVISOR_PORT = args.port
JAVA_ARGS = [
    "java", "-Djava.awt.headless=true",
    "--add-exports", "java.desktop/sun.awt.shell=ALL-UNNAMED",
    "--add-exports", "java.desktop/com.sun.imageio.plugins.bmp=ALL-UNNAMED",
    "--add-exports", "java.desktop/com.sun.imageio.plugins.gif=ALL-UNNAMED",
    "--add-exports", "java.desktop/com.sun.imageio.plugins.png=ALL-UNNAMED",
    "--add-exports", "java.desktop/com.sun.imageio.plugins.wbmp=ALL-UNNAMED",
    "-jar", "GameExtractorServer.jar",
]
STARTING, READY, BUSY, DEAD = range(4)
STATE_NAMES = ("starting", "ready", "busy", "dead")
STARTUP_TIMEOUT = 120
STATELESS_TIMEOUT = 30
MAX_RAPID_RESTARTS = 5
RAPID_RESTART_WINDOW = 60


class Worker:
    def __init__(self, index):
        self.index = index
        self.port = SUPERVISOR_PORT + 1 + index
        self.state = DEAD
        self.process = None
        self.restart_timestamps = []
        self.lease = None
        self.current_request = None
        self.started = None
        self.requests = 0
        self.completed = 0
        self.last_error = None


workers = [Worker(i) for i in range(NUM_WORKERS)]
pool = threading.Condition(threading.RLock())
request_queue = deque()
next_worker = 0
shutdown_flag = threading.Event()
start_time = time.monotonic()


def spawn_worker(worker):
    with pool:
        if shutdown_flag.is_set():
            return
        proc = subprocess.Popen(JAVA_ARGS + [f"--port={worker.port}"],
                                cwd=os.path.dirname(os.path.realpath(__file__)),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        worker.process = proc
        worker.state = STARTING

    def monitor_stdout():
        buf = b""
        for chunk in iter(lambda: proc.stdout.read1(4096), b""):
            with pool:
                if worker.process is not proc or worker.state != STARTING:
                    continue
                buf = (buf + chunk)[-8192:]
                if b"Server listening on port" in buf:
                    worker.state = READY
                    print(f"  Worker {worker.index} ready on port {worker.port}", flush=True)
                    pool.notify_all()

    def monitor_stderr():
        for line in proc.stderr:
            # Retain timeout diagnostics without forwarding expected plugin errors.
            if b"Worker retiring" in line:
                print(f"  Worker {worker.index}: {line.decode(errors='replace').strip()}", flush=True)

    def monitor_exit():
        proc.wait()
        with pool:
            if worker.process is not proc:
                return
            worker.state = DEAD
            worker.process = None
            worker.lease = None
            worker.current_request = None
            worker.started = None
            pool.notify_all()
        if shutdown_flag.is_set():
            return
        print(f"  Worker {worker.index} exited (code={proc.returncode})", flush=True)
        now = time.monotonic()
        worker.restart_timestamps = [t for t in worker.restart_timestamps if now - t < RAPID_RESTART_WINDOW]
        worker.restart_timestamps.append(now)
        delay = 1
        if len(worker.restart_timestamps) >= MAX_RAPID_RESTARTS:
            print(f"  Worker {worker.index} restart-looping, backing off 30s", flush=True)
            delay = 30
            worker.restart_timestamps = []
        if not shutdown_flag.wait(delay):
            spawn_worker(worker)

    def startup_timeout():
        if shutdown_flag.wait(STARTUP_TIMEOUT):
            return
        with pool:
            if worker.process is proc and worker.state == STARTING:
                worker.state = DEAD
                print(f"  Worker {worker.index} startup timeout, killing", flush=True)
                proc.kill()
                pool.notify_all()

    for target in (monitor_stdout, monitor_stderr, monitor_exit, startup_timeout):
        threading.Thread(target=target, daemon=True).start()


def reserve_worker(path):
    """FIFO admission; selection and reservation occur under the same lock."""
    global next_worker
    ticket = object()
    deadline = time.monotonic() + args.queue_timeout
    with pool:
        request_queue.append(ticket)
        try:
            while not shutdown_flag.is_set():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return None
                if request_queue[0] is ticket:
                    for offset in range(len(workers)):
                        index = (next_worker + offset) % len(workers)
                        worker = workers[index]
                        if worker.state == READY:
                            worker.state = BUSY
                            worker.lease = ticket
                            worker.current_request = path
                            worker.started = time.monotonic()
                            worker.requests += 1
                            next_worker = (index + 1) % len(workers)
                            return worker, worker.process, ticket
                pool.wait(remaining)
            return None
        finally:
            request_queue.remove(ticket)
            pool.notify_all()


def release_worker(worker, proc, lease):
    with pool:
        # A callback from an exited process must never release its replacement.
        if worker.process is proc and worker.lease is lease and worker.state == BUSY:
            worker.state = READY
            worker.lease = None
            worker.current_request = None
            worker.started = None
            worker.completed += 1
            pool.notify_all()


def retire_worker(worker, proc, lease, reason):
    with pool:
        if worker.process is not proc or worker.lease is not lease or worker.state != BUSY:
            return False
        worker.state = DEAD
        worker.lease = None
        worker.last_error = reason
        print(f"  Worker {worker.index} retiring: {reason}", flush=True)
        # Socket closure/interruption cannot stop an uncooperative Java plugin.
        # Do not reuse this process, even if its HTTP connection has gone away.
        if proc.poll() is None:
            proc.kill()
        pool.notify_all()
        return True


def error_response(status, message):
    return status, {"Content-Type": "application/json"}, json.dumps({"error": message}).encode()


def proxy_to_worker(worker, method, path, body, timeout, reservation=None):
    conn = http.client.HTTPConnection("127.0.0.1", worker.port, timeout=timeout)
    timed_out = threading.Event()
    timer = None
    if reservation:
        proc, lease = reservation

        def deadline():
            with pool:
                if retire_worker(worker, proc, lease, f"{path} deadline exceeded"):
                    timed_out.set()

        timer = threading.Timer(timeout, deadline)
        timer.daemon = True
        timer.start()
    try:
        conn.request(method, path, body=body, headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        result = resp.status, dict(resp.getheaders()), resp.read()
        if reservation:
            if resp.status == 504:
                retire_worker(worker, proc, lease, "Java plugin deadline exceeded")
            else:
                release_worker(worker, proc, lease)
        if timed_out.is_set():
            return error_response(504, f"Worker {worker.index} timeout; worker restarted")
        return result
    except Exception as exc:
        is_timeout = isinstance(exc, TimeoutError) or timed_out.is_set()
        if reservation:
            retire_worker(worker, proc, lease, f"{path}: {exc}")
        return error_response(504 if is_timeout else 502, f"Worker {worker.index}: {exc}")
    finally:
        if timer:
            timer.cancel()
        conn.close()


def status_snapshot():
    with pool:
        now = time.monotonic()
        return {
            "workers": len(workers),
            **{name: sum(w.state == state for w in workers) for state, name in enumerate(STATE_NAMES)},
            "queueDepth": len(request_queue),
            "uptime": int(now - start_time),
            "workerDetails": [{"index": w.index, "port": w.port,
                               "pid": w.process.pid if w.process else None,
                               "state": STATE_NAMES[w.state], "requests": w.requests,
                               "completed": w.completed, "currentRequest": w.current_request,
                               "busySeconds": round(now - w.started, 3) if w.started else 0,
                               "lastError": w.last_error} for w in workers],
        }


class SupervisorHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_response(self, status, headers, body):
        self.send_response(status)
        for key, value in headers.items():
            if key.lower() not in ("transfer-encoding", "connection", "content-length"):
                self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle(self):
        path = self.path.split("?")[0]
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if path == "/supervisor/status":
            self._send_response(200, {"Content-Type": "application/json"}, json.dumps(status_snapshot()).encode())
            return
        # Include unknown routes in the exclusive lane. Only known metadata/health
        # routes can bypass it; /detect is plugin work, not a stateless read.
        if path not in ("/status", "/list"):
            reservation = reserve_worker(path)
            if not reservation:
                self._send_response(*error_response(503 if shutdown_flag.is_set() else 504,
                                                    "No worker before queue deadline"))
                return
            worker, proc, lease = reservation
            timeout = args.extract_timeout if path == "/extract" else args.detect_timeout
            result = proxy_to_worker(worker, self.command, self.path, body, timeout, (proc, lease))
        else:
            with pool:
                worker = next((w for w in workers if w.state == READY), None)
                worker = worker or next((w for w in workers if w.state == BUSY), None)
            if not worker:
                self._send_response(*error_response(503, "No workers available"))
                return
            result = proxy_to_worker(worker, self.command, self.path, body, STATELESS_TIMEOUT)
        self._send_response(*result)

    def do_GET(self):
        try:
            self._handle()
        except (BrokenPipeError, ConnectionResetError):
            pass

    do_POST = do_GET


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def shutdown_handler(signum, frame):
    print("\nShutting down...", flush=True)
    shutdown_flag.set()
    with pool:
        pool.notify_all()
        processes = [w.process for w in workers if w.process]
    for proc in processes:
        if proc.poll() is None:
            proc.terminate()
    deadline = time.monotonic() + 2
    for proc in processes:
        try:
            proc.wait(timeout=max(0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            proc.kill()
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)
print(f"=== Game Extractor Supervisor ===\n  Workers: {NUM_WORKERS}\n  Port: {SUPERVISOR_PORT}", flush=True)
for worker in workers:
    spawn_worker(worker)
with pool:
    pool.wait_for(lambda: all(w.state == READY for w in workers), timeout=STARTUP_TIMEOUT)
    if not any(w.state == READY for w in workers):
        print("Fatal: No workers became ready within timeout", flush=True)
        shutdown_handler(None, None)
httpd = ThreadedHTTPServer(("", SUPERVISOR_PORT), SupervisorHandler)
print(f"Server listening on port {SUPERVISOR_PORT}", flush=True)
httpd.serve_forever()
