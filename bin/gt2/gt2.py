#!/usr/bin/env python3
# Vibe coded by Codex
"""Headless GT2 HTTP supervisor. Uses only the Python standard library."""
import argparse
import asyncio
from dataclasses import dataclass
from http import HTTPStatus
import json
import logging
import os
from pathlib import Path
import signal
import socket
import sys

LOG = logging.getLogger("gt2")
MAX_BODY = 65536
MAX_RESPONSE = 8 * 1024 * 1024


class HTTPError(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message
        super().__init__(message)


async def read_message(reader, *, response=False):
    try:
        raw = await reader.readuntil(b"\r\n\r\n")
    except (asyncio.LimitOverrunError, asyncio.IncompleteReadError) as exc:
        raise HTTPError(400, "Invalid or oversized HTTP headers") from exc
    if len(raw) > 16384:
        raise HTTPError(431, "HTTP headers too large")
    lines = raw[:-4].decode("iso-8859-1").split("\r\n")
    parts = lines[0].split(" ")
    if (len(parts) < 3 or (not response and len(parts) != 3)
            or (parts[0] if response else parts[-1]) not in ("HTTP/1.0", "HTTP/1.1")):
        raise HTTPError(400, "Invalid HTTP request line")
    headers = {}
    for line in lines[1:]:
        name, sep, value = line.partition(":")
        if not sep or not name or name != name.strip() or any(ord(c) < 33 or ord(c) > 126 for c in name):
            raise HTTPError(400, "Invalid HTTP header")
        name = name.lower()
        if name in headers and name in ("content-length", "transfer-encoding"):
            raise HTTPError(400, "Duplicate framing header")
        headers[name] = value.strip()
    limit = MAX_RESPONSE if response else MAX_BODY
    if "transfer-encoding" in headers:
        if headers["transfer-encoding"].lower() != "chunked" or "content-length" in headers:
            raise HTTPError(400, "Unsupported or ambiguous HTTP framing")
        body = bytearray()
        while True:
            line = await reader.readuntil(b"\r\n")
            try:
                value = line[:-2].split(b";", 1)[0]
                if not value or any(c not in b"0123456789abcdefABCDEF" for c in value):
                    raise ValueError()
                size = int(value, 16)
            except ValueError as exc:
                raise HTTPError(400, "Invalid chunk size") from exc
            if size + len(body) > limit:
                raise HTTPError(413, "HTTP body too large")
            if not size:
                trailers = 0
                while True:
                    trailer = await reader.readuntil(b"\r\n")
                    trailers += len(trailer)
                    if trailers > 8192:
                        raise HTTPError(431, "HTTP trailers too large")
                    if trailer == b"\r\n":
                        break
                break
            body.extend(await reader.readexactly(size))
            if await reader.readexactly(2) != b"\r\n":
                raise HTTPError(400, "Invalid chunk terminator")
        body = bytes(body)
    else:
        length = headers.get("content-length", "0")
        if not length.isascii() or not length.isdecimal():
            raise HTTPError(400, "Invalid Content-Length")
        length = int(length)
        if length > limit:
            raise HTTPError(413, "HTTP body too large")
        body = await reader.readexactly(length)
    return parts, headers, body


async def exchange(port, method, endpoint, body=b"", timeout=30):
    async def perform():
        reader, writer = await asyncio.open_connection("127.0.0.1", port, limit=16384)
        try:
            header = (f"{method} {endpoint} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
                      f"Content-Type: application/json\r\nContent-Length: {len(body)}\r\n"
                      "Connection: close\r\n\r\n").encode("ascii")
            writer.write(header + body)
            await writer.drain()
            parts, headers, result = await read_message(reader, response=True)
            return int(parts[1]), headers.get("content-type", "application/json"), result
        finally:
            writer.close()
            await writer.wait_closed()
    return await asyncio.wait_for(perform(), timeout)


@dataclass
class Job:
    body: bytes
    result: asyncio.Future


class Worker:
    def __init__(self, pool, number):
        self.pool, self.number = pool, number
        self.process = None
        self.port = None
        self.ready = False
        self.busy = False
        self.exit_task = None

    async def healthy(self):
        if not self.ready or self.process is None or self.process.returncode is not None:
            return False
        try:
            status, _, body = await exchange(self.port, "GET", "/status", timeout=2)
            return status == 200 and body == b"a-ok"
        except (OSError, ValueError, HTTPError, asyncio.TimeoutError, asyncio.IncompleteReadError):
            return False

    async def start(self):
        self.ready = False
        # Pass a bound listener to the child, avoiding port reservation races.
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            listener.bind(("127.0.0.1", 0))
            listener.listen(128)
            self.port = listener.getsockname()[1]
            self.process = await asyncio.create_subprocess_exec(
                str(self.pool.binary), "--host", "127.0.0.1", "--port", str(self.port),
                "--listen-fd", str(listener.fileno()), pass_fds=(listener.fileno(),),
                stdin=asyncio.subprocess.DEVNULL, stdout=sys.stdout, stderr=sys.stderr,
                cwd=str(self.pool.binary.parent))
        finally:
            listener.close()
        self.exit_task = asyncio.create_task(self.process.wait())
        deadline = asyncio.get_running_loop().time() + self.pool.startup_timeout
        while asyncio.get_running_loop().time() < deadline:
            if self.process.returncode is not None:
                raise RuntimeError(f"worker exited during startup ({self.process.returncode})")
            try:
                status, _, body = await exchange(self.port, "GET", "/status", timeout=1)
                if status == 200 and body == b"a-ok":
                    self.ready = True
                    LOG.info("worker %d ready: pid=%d port=%d", self.number, self.process.pid, self.port)
                    return
            except (OSError, ValueError, HTTPError, asyncio.TimeoutError, asyncio.IncompleteReadError):
                pass
            await asyncio.sleep(0.05)
        raise RuntimeError("worker startup timed out")

    async def stop(self):
        self.ready = False
        if self.process is not None and self.process.returncode is None:
            try:
                self.process.terminate()
            except ProcessLookupError:
                pass
            try:
                await asyncio.wait_for(self.process.wait(), 2)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()
        if self.exit_task is not None:
            await self.exit_task
        self.process = None

    async def serve(self):
        pending_get = None
        job = None
        try:
            while True:
                try:
                    await self.start()
                    while True:
                        pending_get = asyncio.create_task(self.pool.queue.get())
                        done, _ = await asyncio.wait((pending_get, self.exit_task), return_when=asyncio.FIRST_COMPLETED)
                        if self.exit_task in done:
                            if pending_get.done():
                                orphan = pending_get.result()
                                self.pool.queue.task_done()
                                if not orphan.result.done():
                                    self.pool.queue.put_nowait(orphan)
                            else:
                                pending_get.cancel()
                                await asyncio.gather(pending_get, return_exceptions=True)
                            pending_get = None
                            raise RuntimeError(f"worker exited ({self.process.returncode})")
                        job = pending_get.result()
                        pending_get = None
                        if job.result.done():
                            self.pool.queue.task_done()
                            job = None
                            continue
                        self.busy = True
                        try:
                            result = await exchange(self.port, "POST", "/detect", job.body, self.pool.request_timeout)
                            # Reject a truncated/non-JSON response before reusing the worker.
                            parsed = json.loads(result[2])
                            if result[0] == 200 and not isinstance(parsed, list):
                                raise ValueError("worker returned an invalid detection result")
                            if not job.result.done():
                                job.result.set_result(result)
                        except (OSError, ValueError, HTTPError, asyncio.TimeoutError, asyncio.IncompleteReadError) as exc:
                            if not job.result.done():
                                job.result.set_exception(HTTPError(502, "Detection worker failed or timed out; it is being restarted"))
                            raise RuntimeError(str(exc)) from exc
                        finally:
                            self.busy = False
                            self.pool.queue.task_done()
                            job = None
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    LOG.warning("worker %d restarting: %s", self.number, exc)
                finally:
                    await self.stop()
                await asyncio.sleep(0.2)
        finally:
            if pending_get is not None:
                pending_get.cancel()
                await asyncio.gather(pending_get, return_exceptions=True)
            if job is not None and not job.result.done():
                job.result.set_exception(HTTPError(503, "Supervisor shutting down"))
            await self.stop()


class Pool:
    def __init__(self, binary, count, request_timeout, startup_timeout):
        self.binary, self.request_timeout, self.startup_timeout = binary, request_timeout, startup_timeout
        self.queue = asyncio.Queue()
        self.workers = [Worker(self, i + 1) for i in range(count)]
        self.tasks = []
        self.stopping = False

    def start(self):
        self.tasks = [asyncio.create_task(worker.serve()) for worker in self.workers]

    async def healthy(self):
        return not self.stopping and all(await asyncio.gather(*(w.healthy() for w in self.workers)))

    async def detect(self, body):
        if self.stopping:
            raise HTTPError(503, "Supervisor shutting down")
        future = asyncio.get_running_loop().create_future()
        self.queue.put_nowait(Job(body, future))
        return await future

    async def stop(self):
        self.stopping = True
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        while not self.queue.empty():
            job = self.queue.get_nowait()
            if not job.result.done():
                job.result.set_exception(HTTPError(503, "Supervisor shutting down"))
            self.queue.task_done()


async def send_response(writer, status, body, content_type="application/json; charset=utf-8"):
    reason = HTTPStatus(status).phrase
    header = (f"HTTP/1.1 {status} {reason}\r\nContent-Type: {content_type}\r\n"
              f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n").encode("ascii")
    writer.write(header + body)
    await asyncio.wait_for(writer.drain(), 10)


async def handle(reader, writer, pool):
    try:
        parts, _, body = await asyncio.wait_for(read_message(reader), 15)
        method, target = parts[:2]
        if target == "/status":
            if method != "GET":
                raise HTTPError(405, "Use GET /status")
            ready = await pool.healthy()
            await send_response(writer, 200 if ready else 503, b"a-ok" if ready else b"not-ready", "text/plain; charset=utf-8")
        elif target == "/detect":
            if method != "POST":
                raise HTTPError(405, "Use POST /detect")
            try:
                request = json.loads(body)
            except (ValueError, UnicodeError) as exc:
                raise HTTPError(400, "Invalid JSON") from exc
            path = request.get("filePath") if isinstance(request, dict) else None
            if not isinstance(path, str) or not path.startswith("/") or "\0" in path:
                raise HTTPError(400, "filePath must be an absolute path string without NUL bytes")
            status, content_type, result = await pool.detect(body)
            await send_response(writer, status, result, content_type)
        else:
            raise HTTPError(404, "Unknown endpoint")
    except HTTPError as exc:
        try:
            await send_response(writer, exc.status, json.dumps({"error": exc.message}).encode())
        except (OSError, asyncio.TimeoutError):
            pass
    except (asyncio.TimeoutError, asyncio.IncompleteReadError, asyncio.LimitOverrunError):
        try:
            await send_response(writer, 400, b'{"error":"Incomplete or timed-out HTTP request"}')
        except (OSError, asyncio.TimeoutError):
            pass
    except (OSError, ConnectionError):
        pass
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except OSError:
            pass


async def run(args, binary):
    pool = Pool(binary, args.workers, args.request_timeout, args.startup_timeout)
    clients = set()

    def connected(reader, writer):
        task = asyncio.create_task(handle(reader, writer, pool))
        clients.add(task)
        task.add_done_callback(clients.discard)

    server = await asyncio.start_server(connected, args.host, args.port, limit=16384, backlog=512)
    stopped = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stopped.set)
    pool.start()
    LOG.info("supervisor listening on %s; starting %d workers", ", ".join(str(s.getsockname()) for s in server.sockets), args.workers)
    try:
        await stopped.wait()
    finally:
        server.close()
        await server.wait_closed()
        await pool.stop()
        for task in list(clients):
            task.cancel()
        await asyncio.gather(*clients, return_exceptions=True)


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--workers", type=positive, default=10)
    parser.add_argument("--request-timeout", type=positive, default=30, help="active worker timeout in seconds; queued requests do not time out")
    parser.add_argument("--startup-timeout", type=positive, default=30)
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("--port must be between 0 and 65535")
    here = Path(__file__).resolve().parent
    binary = here / "gt2-server"
    if not binary.is_file():
        binary = here / "build/gt2-server"
    if not binary.is_file() or not os.access(binary, os.X_OK):
        parser.error("gt2-server was not found beside gt2.py or in build/. Run ./install.sh <directory> first.")
    status_handler = logging.StreamHandler(sys.stdout)
    status_handler.addFilter(lambda record: record.levelno < logging.WARNING)
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s: %(message)s",
                        handlers=[status_handler, error_handler])
    try:
        asyncio.run(run(args, binary))
    except (OSError, KeyboardInterrupt) as exc:
        LOG.error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
