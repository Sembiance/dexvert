#!/usr/bin/env python3
# Vibe coded by Codex
"""
Fast Binwalk signature detection service.

Run the director with:

    python binwalkServer.py --workers=15

Or specify the director port:

    python binwalkServer.py --workers=15 --port=9090

The director exposes POST /detect and dispatches each request to one of the
single-threaded worker HTTP servers. Each worker preloads Binwalk magic
signatures and plugins once, then handles one detection request at a time.
"""

import argparse
import json
import multiprocessing
import os
import queue
import signal
import sys
import time
import traceback
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer


# Keep portable bundles clean when copied to shared or read-only-ish locations.
sys.dont_write_bytecode = True

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BINWALK_SRC = os.path.join(ROOT_DIR, "binwalk", "src")
if BINWALK_SRC not in sys.path:
    sys.path.insert(0, BINWALK_SRC)


DEFAULT_LENGTH = 512
DEFAULT_PEEK = 8 * 1024
JSON_CONTENT_TYPE = "application/json; charset=utf-8"


class JsonHandler(BaseHTTPRequestHandler):
    server_version = "BinwalkDetect/1.0"

    def log_message(self, fmt, *args):
        if getattr(self.server, "quiet", False):
            return
        super().log_message(fmt, *args)

    def log_request(self, code="-", size="-"):
        if self.command == "POST" and self.path == "/detect" and str(code) == "200":
            return
        super().log_request(code, size)

    def read_json(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise ValueError("Invalid Content-Length")

        if content_length <= 0:
            raise ValueError("Missing JSON request body")

        data = self.rfile.read(content_length)
        try:
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON: %s" % exc)

    def send_json(self, status, payload):
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", JSON_CONTENT_TYPE)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(data)

    def not_found(self):
        self.send_json(404, {"error": "Not found"})

    def send_text(self, status, text):
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(data)


class DetectorConfig:
    def __init__(self, length):
        self.length = length
        self.offset = 0
        self.swap_size = 0
        self.block = 0
        self.base = 0
        self.verbose = False

    def open_file(self, fname, length=None, offset=None, swap=None, block=None, peek=None):
        import binwalk.core.common

        if length is None:
            length = self.length
        if offset is None:
            offset = self.offset
        if swap is None:
            swap = self.swap_size

        return binwalk.core.common.BlockFile(
            fname,
            length=length,
            offset=offset,
            swap=swap,
            block=block,
            peek=peek,
        )


class DetectorExtractor:
    enabled = False
    pending = []

    def add_rule(self, *args, **kwargs):
        return None

    def match(self, *args, **kwargs):
        return False

    def callback(self, *args, **kwargs):
        return None

    def reset(self):
        self.pending = []


class DetectorModule:
    name = "Signature"

    def __init__(self, length):
        self.config = DetectorConfig(length)
        self.extractor = DetectorExtractor()


class BinwalkDetector:
    def __init__(self, length=DEFAULT_LENGTH):
        import binwalk.core.magic
        import binwalk.core.plugin
        import binwalk.core.settings

        self.length = length
        self.module = DetectorModule(length)
        self.magic = binwalk.core.magic.Magic()

        settings = binwalk.core.settings.Settings()
        self.magic_files = settings.user.magic + settings.system.magic
        for magic_file in self.magic_files:
            self.magic.load(magic_file)

        self.plugins = binwalk.core.plugin.Plugins(self.module)
        self.plugins.load_plugins()

    def detect_file(self, file_path):
        self._validate_file_path(file_path)

        fp = self.module.config.open_file(file_path, length=self.length)
        try:
            return self._scan_file(fp)
        finally:
            fp.close()

    def _validate_file_path(self, file_path):
        if not isinstance(file_path, str) or not file_path:
            raise ValueError("filePath must be a non-empty string")
        if os.path.isdir(file_path):
            raise ValueError("filePath points to a directory")
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

    def _scan_file(self, fp):
        matches = []
        one_of_many = None
        self.magic.reset()
        self.module.extractor.reset()

        self.plugins.pre_scan_callbacks(self.module)
        self.plugins.load_file_callbacks(fp)
        self.plugins.new_file_callbacks(fp)

        while True:
            data, dlen = fp.read_block()
            if dlen < 1:
                break

            current_block_offset = 0
            block_start = fp.tell() - dlen

            for result in self.magic.scan(data, dlen):
                if result.offset < current_block_offset:
                    continue

                relative_offset = result.offset + result.adjust
                result.offset = block_start + relative_offset
                result.file = fp
                result.module = "Signature"

                self._validate_result(result)
                one_of_many = self._apply_one_of_many(result, one_of_many)
                self.plugins.scan_callbacks(result)

                if result.valid and result.display:
                    matches.append(self._serialize_result(result))

                if result.end is True:
                    result.jump = fp.size

                if result.valid and result.jump > 0:
                    absolute_jump_offset = result.offset + result.jump
                    current_block_offset = relative_offset + result.jump
                    if absolute_jump_offset >= fp.tell():
                        fp.seek(absolute_jump_offset)
                        break

        self.plugins.post_scan_callbacks(self.module)
        return matches

    def _validate_result(self, result):
        if not result.description:
            result.valid = False

        if result.valid:
            if result.size and (result.size + result.offset) > result.file.size:
                result.valid = False
            if result.jump and (result.jump + result.offset) > result.file.size:
                result.valid = False
            if hasattr(result, "location") and (result.location != result.offset):
                result.valid = False

    def _apply_one_of_many(self, result, one_of_many):
        if result.valid:
            if result.id == one_of_many:
                result.display = False
            elif result.many:
                one_of_many = result.id
            else:
                one_of_many = None
        return one_of_many

    def _serialize_result(self, result):
        return {
            "offset": result.offset,
            "hexadecimal": "0x%X" % result.offset,
            "description": result.description,
        }


class WorkerHandler(JsonHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {
                "ok": True,
                "role": "worker",
                "pid": os.getpid(),
                "signatures": len(self.server.detector.magic.signatures),
            })
        else:
            self.not_found()

    def do_POST(self):
        if self.path != "/detect":
            self.not_found()
            return

        try:
            payload = self.read_json()
            matches = self.server.detector.detect_file(payload.get("filePath"))
            self.send_json(200, {"matches": matches})
        except FileNotFoundError as exc:
            self.send_json(404, {"error": "File not found", "filePath": str(exc)})
        except ValueError as exc:
            self.send_json(400, {"error": str(exc)})
        except Exception as exc:
            self.send_json(500, {
                "error": str(exc),
                "traceback": traceback.format_exc(),
            })


class DirectorHandler(JsonHandler):
    def do_GET(self):
        if self.path == "/status":
            self.send_text(200, "a-ok")
        elif self.path == "/health":
            self.send_json(200, {
                "ok": True,
                "role": "director",
                "workers": len(self.server.worker_urls),
                "availableWorkers": self.server.worker_queue.qsize(),
            })
        else:
            self.not_found()

    def do_POST(self):
        if self.path != "/detect":
            self.not_found()
            return

        try:
            payload = self.read_json()
        except ValueError as exc:
            self.send_json(400, {"error": str(exc)})
            return

        worker_url = self.server.worker_queue.get()
        should_requeue = True
        try:
            status, response = post_json(worker_url + "/detect", payload, self.server.worker_timeout)
            self.send_json(status, response)
        except urllib.error.HTTPError as exc:
            status, response = read_http_error(exc)
            self.send_json(status, response)
        except Exception as exc:
            should_requeue = False
            self.send_json(502, {
                "error": "Worker request failed",
                "worker": worker_url,
                "detail": str(exc),
            })
        finally:
            if should_requeue:
                self.server.worker_queue.put(worker_url)


def post_json(url, payload, timeout):
    data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": JSON_CONTENT_TYPE},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
        return response.status, json.loads(body.decode("utf-8"))


def read_http_error(exc):
    body = exc.read()
    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        payload = {"error": body.decode("utf-8", "replace")}
    return exc.code, payload


def start_worker(worker_id, host, port, length, ready_queue, quiet):
    try:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        detector = BinwalkDetector(length=length)
        server = HTTPServer((host, port), WorkerHandler)
        server.detector = detector
        server.quiet = quiet
        ready_queue.put({
            "id": worker_id,
            "host": host,
            "port": server.server_address[1],
            "pid": os.getpid(),
            "signatures": len(detector.magic.signatures),
        })
        server.serve_forever(poll_interval=0.25)
    except Exception as exc:
        ready_queue.put({
            "id": worker_id,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        })
        raise


def spawn_workers(args):
    ready_queue = multiprocessing.Queue()
    processes = []
    worker_urls = []

    for worker_id in range(args.workers):
        port = args.worker_port_start + worker_id if args.worker_port_start else 0
        process = multiprocessing.Process(
            target=start_worker,
            args=(worker_id, args.worker_host, port, args.length, ready_queue, args.quiet),
            daemon=False,
        )
        process.start()
        processes.append(process)

    deadline = time.monotonic() + args.worker_start_timeout
    ready_by_id = {}
    while len(ready_by_id) < args.workers:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError("Timed out waiting for workers to start")
        try:
            info = ready_queue.get(timeout=remaining)
        except queue.Empty:
            raise RuntimeError("Timed out waiting for workers to start")

        if "error" in info:
            raise RuntimeError("Worker %s failed to start: %s\n%s" % (
                info.get("id"),
                info.get("error"),
                info.get("traceback", ""),
            ))
        ready_by_id[info["id"]] = info

    for worker_id in sorted(ready_by_id):
        info = ready_by_id[worker_id]
        worker_urls.append("http://%s:%d" % (info["host"], info["port"]))
        if not args.quiet:
            print(
                "worker %d ready on %s:%d pid=%s signatures=%s" % (
                    worker_id,
                    info["host"],
                    info["port"],
                    info["pid"],
                    info["signatures"],
                ),
                flush=True,
            )

    return processes, worker_urls


def stop_workers(processes):
    for process in processes:
        if process.is_alive():
            process.terminate()

    for process in processes:
        process.join(timeout=3)

    for process in processes:
        if process.is_alive():
            process.kill()
            process.join(timeout=1)


def run_director(args, worker_urls):
    worker_queue = queue.Queue()
    for worker_url in worker_urls:
        worker_queue.put(worker_url)

    server = ThreadingHTTPServer((args.host, args.port), DirectorHandler)
    server.worker_urls = worker_urls
    server.worker_queue = worker_queue
    server.worker_timeout = args.worker_timeout
    server.quiet = args.quiet

    print(
        "director ready on http://%s:%d workers=%d length=%d" % (
            args.host,
            server.server_address[1],
            len(worker_urls),
            args.length,
        ),
        flush=True,
    )
    server.serve_forever(poll_interval=0.25)


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Fast Binwalk detect server")
    parser.add_argument("--host", default="127.0.0.1", help="Director bind host")
    parser.add_argument("--port", type=int, default=8080, help="Director bind port")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker servers")
    parser.add_argument("--worker-host", default="127.0.0.1", help="Worker bind host")
    parser.add_argument(
        "--worker-port-start",
        type=int,
        default=0,
        help="First worker port. Default 0 lets the OS assign free ports.",
    )
    parser.add_argument("--length", type=int, default=DEFAULT_LENGTH, help="Bytes to scan per file")
    parser.add_argument("--worker-timeout", type=float, default=60.0, help="Worker HTTP timeout in seconds")
    parser.add_argument(
        "--worker-start-timeout",
        type=float,
        default=30.0,
        help="Seconds to wait for all workers to preload and start",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress HTTP access logs")
    args = parser.parse_args(argv)

    if args.workers < 1:
        parser.error("--workers must be >= 1")
    if args.length < 1:
        parser.error("--length must be >= 1")
    if args.worker_port_start and args.worker_port_start + args.workers > 65535:
        parser.error("--worker-port-start plus workers exceeds valid port range")

    return args


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    processes = []

    def handle_signal(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, handle_signal)

    try:
        processes, worker_urls = spawn_workers(args)
        run_director(args, worker_urls)
    except KeyboardInterrupt:
        pass
    finally:
        stop_workers(processes)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
