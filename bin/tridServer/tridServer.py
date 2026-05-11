#!/usr/bin/env python3

# Vibe coded by Codex

import argparse
from collections import OrderedDict
from concurrent.futures import ProcessPoolExecutor, wait
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import signal
import sys
sys.dont_write_bytecode = True
from time import sleep
from time import perf_counter

import trid


DEFAULT_CACHE_SIZE = 4096

_TDB = None
_DEFS_PATH = None
_RESULT_CACHE = None
_CACHE_SIZE = DEFAULT_CACHE_SIZE


def _json_response(handler, status, payload):
    data = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _text_response(handler, status, text):
    data = text.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/plain; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _worker_init(defs_path, cache_size):
    global _TDB, _DEFS_PATH, _RESULT_CACHE, _CACHE_SIZE
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    _DEFS_PATH = defs_path
    _CACHE_SIZE = cache_size
    _RESULT_CACHE = OrderedDict()
    _TDB = trid.trdpkg2defs(defs_path, usecache=True)


def _worker_status(delay=0):
    if delay:
        sleep(delay)
    return {
        "pid": os.getpid(),
        "defs": _TDB.defs_num if _TDB else 0,
        "cache": len(_RESULT_CACHE) if _RESULT_CACHE is not None else 0,
    }


def _cache_key(file_path, n, stringcheck):
    path = Path(file_path).resolve()
    stat = path.stat()
    return (
        str(path),
        int(n),
        bool(stringcheck),
        stat.st_size,
        stat.st_mtime_ns,
        stat.st_ino,
    )


def _result_to_match(result):
    return {
        "percent": round(result.perc, 1),
        "score": result.pts,
        "extension": result.triddef.ext,
        "fileType": result.triddef.filetype,
        "mimeType": result.triddef.mime,
        "patterns": result.patt,
        "strings": result.str,
    }


def _worker_detect(file_path, n=5, stringcheck=True):
    if _TDB is None:
        raise RuntimeError("worker definitions are not loaded")

    start = perf_counter()
    key = _cache_key(file_path, n, stringcheck)
    cached = _RESULT_CACHE.get(key)
    if cached is not None:
        _RESULT_CACHE.move_to_end(key)
        response = dict(cached)
        response["cached"] = True
        response["elapsedMs"] = round((perf_counter() - start) * 1000, 3)
        return response

    results = trid.tridAnalyze(str(key[0]), _TDB, stringcheck=stringcheck)
    matches = [_result_to_match(result) for result in results[:max(0, int(n))]]
    response = {
        "matches": matches,
        "cached": False,
        "elapsedMs": round((perf_counter() - start) * 1000, 3),
    }

    _RESULT_CACHE[key] = response
    _RESULT_CACHE.move_to_end(key)
    while len(_RESULT_CACHE) > _CACHE_SIZE:
        _RESULT_CACHE.popitem(last=False)
    return response


class TrIDServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, server_address, request_handler, executor, workers):
        super().__init__(server_address, request_handler)
        self.executor = executor
        self.workers = workers
        self.ready = True


class TrIDRequestHandler(BaseHTTPRequestHandler):
    server_version = "TrIDServer/1.0"

    def log_message(self, fmt, *args):
        return

    def do_GET(self):
        if self.path == "/status":
            if self.server.ready:
                _text_response(self, 200, "a-ok")
            else:
                _text_response(self, 503, "starting")
            return

        _json_response(self, 404, {"matches": [], "error": "not found"})

    def do_POST(self):
        if self.path != "/detect":
            _json_response(self, 404, {"matches": [], "error": "not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            payload = json.loads(body.decode("utf-8")) if body else {}
        except (ValueError, json.JSONDecodeError):
            _json_response(self, 400, {"matches": [], "error": "invalid JSON"})
            return

        file_path = payload.get("filePath")
        if not isinstance(file_path, str) or not file_path:
            _json_response(self, 400, {"matches": [], "error": "filePath is required"})
            return

        try:
            n = int(payload.get("n", 5))
            stringcheck = not bool(payload.get("noStrings", False))
        except (TypeError, ValueError):
            _json_response(self, 400, {"matches": [], "error": "invalid options"})
            return

        try:
            future = self.server.executor.submit(_worker_detect, file_path, n, stringcheck)
            response = future.result()
        except FileNotFoundError:
            _json_response(self, 404, {"matches": [], "error": "file not found"})
            return
        except PermissionError:
            _json_response(self, 403, {"matches": [], "error": "permission denied"})
            return
        except Exception as exc:
            _json_response(self, 500, {"matches": [], "error": str(exc)})
            return

        _json_response(self, 200, response)


def _find_defs_path(value):
    if value:
        return str(Path(value).resolve())

    local = Path("triddefs.trd")
    if local.exists():
        return str(local.resolve())

    return str((trid.get_base_path() / "triddefs.trd").resolve())


def _warm_workers(executor, workers):
    futures = [executor.submit(_worker_status, 0.25) for _ in range(workers)]
    done, _ = wait(futures)
    statuses = [future.result() for future in done]
    pids = {status["pid"] for status in statuses}
    if len(pids) < workers:
        futures = [executor.submit(_worker_status, 0.25) for _ in range(workers * 2)]
        done, _ = wait(futures)
        statuses.extend(future.result() for future in done)
        pids = {status["pid"] for status in statuses}
    return statuses, pids


def parse_args():
    parser = argparse.ArgumentParser(description="HTTP worker pool for TrID file detection")
    parser.add_argument("--port", type=int, required=True, help="port for the main HTTP server")
    parser.add_argument("--workers", type=int, required=True, help="number of worker processes")
    parser.add_argument("--defs", help="path to triddefs.trd")
    parser.add_argument("--cache-size", type=int, default=DEFAULT_CACHE_SIZE,
                        help="per-worker bounded result cache size")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.workers < 1:
        raise SystemExit("--workers must be at least 1")
    if args.port < 1 or args.port > 65535:
        raise SystemExit("--port must be between 1 and 65535")

    defs_path = _find_defs_path(args.defs)
    if not os.path.exists(defs_path):
        raise SystemExit(f"definitions file not found: {defs_path}")

    # Build or refresh the cache once before workers start, avoiding concurrent cache writes.
    trid.trdpkg2defs(defs_path, usecache=True)

    executor = ProcessPoolExecutor(
        max_workers=args.workers,
        initializer=_worker_init,
        initargs=(defs_path, args.cache_size),
    )
    try:
        statuses, pids = _warm_workers(executor, args.workers)
        if len(pids) < args.workers:
            raise RuntimeError(f"only warmed {len(pids)} of {args.workers} workers")

        httpd = TrIDServer(("", args.port), TrIDRequestHandler, executor, args.workers)
        print(f"TrID server ready on port {args.port} with {len(pids)} workers")
        print(f"Definitions: {statuses[0]['defs'] if statuses else 0}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping TrID server")
    finally:
        executor.shutdown(cancel_futures=True)


if __name__ == "__main__":
    main()
