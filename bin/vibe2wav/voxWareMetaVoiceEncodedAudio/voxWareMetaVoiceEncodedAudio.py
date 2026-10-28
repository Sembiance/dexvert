#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict Voxware VOX!/VOXd reader and reference-decoder WAV converter.

Python 3.10+, standard library only. Synthesis uses the supplied x86 bridge
and original Voxware DLLs; on POSIX, Wine with 32-bit support is required.
See voxWareMetaVoiceEncodedAudio.txt for the verified scope and limitations.
"""

import argparse
import base64
from dataclasses import dataclass, field, asdict
import hashlib
import json
import math
import os
from pathlib import Path
import selectors
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import wave
import zlib


class FormatError(ValueError):
    """Not this supported format (no output is permitted)."""


class DecodeError(RuntimeError):
    """A recognized stream cannot be decoded."""


PROFILES = {0x0403: (11025, "file-mode narrowband"),
            0x0504: (8000, "RT24"),
            0x0605: (22050, "file-mode wideband")}
# Exact 16 x 256 voicing/pitch lookup from MM32DCMP, RVA 0x5f710.
# The reference parser special-cases voicing 0 and caps every other entry at 31.
HARMONICS = zlib.decompress(base64.b85decode(
    "c%1Fm32wqL5I|AUg|>k}AdnCU(7oLMgdNqfJ!=-!7FFuM!90yE`*{3w9iTl_*YytCLRD35pb{#IVhydJJkOWV0?M*%4$Yu6O{dTVN|I!ZyB*%m@UDk<HM~*3CT5A%gVnv+oz>Xv4DmDgMhjfVoAYM8lsDyd!*)Y<yLB_^C}r6kn%Ek*!sVzX&Q>(>Y&6r#G_q+-60hLyk)~Z}8>&K^SQ*mTR4@%oV^W1Q9L+^F(KLd?v+t?t(TA_wgTHh4*o$KcDWN2Y1dp&0Fakx02o6CJ9Zp|;xZYiFuGgj)7j<GvIuZ3@Iywz?VJeh_fiMkf!5|{Tsc(dc2q`>@4Uth?6cj~-cqkeQh2nq|de7f&gJ=YdV8JMYM1Tkmgn=xCgm6F#&fr_-Z)0I7jD(9Y52m47L<$DM82B<cgrA(hMTCL`52`^is70Wl5Y!<sPz7x8yYshkknQjoWHE#Udh?T4e`N3qVHdc;Mdv4J7K}oJ;12rd2mgME!KJ6xY9tT@azKXzF(3tmkVgb$fC&EQ{{%EjYk~"))
SUPPORT_HASHES = {
    "mm32dcmp.dll": "583a2a7e705a2c1a93bf26a8055677ff417d90025e078495077a9d48daeebf9c",
    "VDK32116.DLL": "e3c412bcc3d0cd6beaa1e988772b5cfab43ef49fc18bc9d64a3ca0cb151fea2f",
    "decoder_bridge.exe": "02a6f13bae2747e79fb417adea788c8d891b1c9c13e2c17c92f79cb8cc4ab570",
}
U32 = struct.Struct("<I")
VOX_HEADER = struct.Struct("<HHHHIIIIffff")


@dataclass
class Stream:
    index: int
    offset: int
    end: int
    codec: int
    rate: int
    frame_samples_hint: int
    source_sample_bytes: int
    bookkeeping: int
    flags: int
    declared_frames: int
    encoder_private: int
    pitch_low: float
    pitch_mean: float
    pitch_high: float
    amplitude_scale: float
    fact: int | None
    fmt: tuple
    payload_offset: int
    payload_size: int
    header: bytes = field(repr=False)
    warnings: list = field(default_factory=list)
    regions: list = field(default_factory=list)
    complete_frames: int = 0
    frame_bits: int = 0
    tail_bits: int = 0
    tail_hex: str = ""

    def metadata(self):
        d = asdict(self)
        d["header"] = self.header.hex()
        d["profile"] = PROFILES[self.codec][1]
        return d


def _chunks(buf, start, end, regions, warnings, scope):
    """Length-driven traversal; never scan payload bytes for magic strings."""
    pos = start
    while pos < end:
        if end - pos < 8:
            regions.append((pos, end, scope + " incomplete chunk header"))
            warnings.append(f"{scope}: {end-pos} trailing byte(s) at {pos}")
            return
        tag = bytes(buf[pos:pos+4])
        size = U32.unpack_from(buf, pos+4)[0]
        data_start = pos+8
        data_end = min(data_start+size, end)
        regions.append((pos, data_start, scope + " " + repr(tag) + " header"))
        if data_start+size > end:
            warnings.append(f"{scope} {tag!r} at {pos}: declared length {size} "
                            f"exceeds parent; using {end-data_start} available bytes")
        yield tag, data_start, data_end, size
        pos = data_end
        if data_start+size > end:
            return
        if size & 1:
            if pos < end:
                regions.append((pos, pos+1, scope + " alignment byte"))
                pos += 1
            else:
                warnings.append(f"{scope}: missing final alignment byte at {pos}")


def inspect_file(buf):
    """Prescan every RIFF member before decoding or creating output paths."""
    streams, global_warnings = [], []
    offset = 0
    while offset < len(buf):
        if len(buf)-offset < 12 or bytes(buf[offset:offset+4]) != b"RIFF":
            if not streams:
                raise FormatError("not a little-endian RIFF/WAVE Voxware file")
            global_warnings.append(f"{len(buf)-offset} unparsed trailing bytes at {offset}; "
                                   "no valid next RIFF boundary")
            break
        if bytes(buf[offset+8:offset+12]) != b"WAVE":
            raise FormatError(f"RIFF member at {offset} is not WAVE")
        declared_end = offset+8+U32.unpack_from(buf, offset+4)[0]
        if declared_end < offset+12:
            if not streams:
                raise FormatError("RIFF size too small to identify target format")
            global_warnings.append(f"invalid next RIFF length at {offset}; stopped")
            break
        end = min(declared_end, len(buf))
        regions = [(offset, offset+12, "RIFF/WAVE header")]
        warnings, fmt, fact, data = [], None, None, None
        if end != declared_end:
            warnings.append(f"RIFF truncated: expected end {declared_end}, actual {end}")
        for tag, lo, hi, size in _chunks(buf, offset+12, end, regions, warnings, "RIFF"):
            if tag == b"fmt ":
                regions.append((lo, hi, "WAVE format descriptor"))
                if fmt is not None or hi-lo < 16:
                    raise FormatError(f"missing, short, or duplicate fmt chunk at {lo}")
                fmt = struct.unpack_from("<HHIIHH", buf, lo)
                if fmt[0] != 0x62:
                    raise FormatError(f"WAVE codec 0x{fmt[0]:04x} is not target codec 0x0062")
                if hi-lo != 16:
                    raise FormatError("extended WAVE fmt descriptors are not implemented")
            elif tag == b"fact":
                regions.append((lo, hi, "WAVE fact count"))
                if hi-lo >= 4:
                    fact = U32.unpack_from(buf, lo)[0]
                if hi-lo != 4:
                    warnings.append(f"fact payload has {hi-lo} bytes, expected four")
            elif tag == b"data":
                if data is not None:
                    raise FormatError("multiple data chunks in one WAVE are not implemented")
                data = (lo, hi)
            else:
                regions.append((lo, hi, "uninterpreted RIFF " + repr(tag)))
                warnings.append(f"uninterpreted RIFF chunk {tag!r} at {lo}; skipped by length")
        if fmt is None or data is None:
            if not streams:
                raise FormatError("cannot identify target: fmt or data chunk missing")
            global_warnings.append(f"incomplete member at {offset}; stopped")
            break
        if bytes(buf[data[0]:data[0]+4]) != b"VOX!":
            raise FormatError("WAVE 0x0062 data does not begin with supported VOX! header")
        header, payload = None, None
        for tag, lo, hi, size in _chunks(buf, *data, regions, warnings, "Voxware"):
            if tag == b"VOX!":
                regions.append((lo, hi, "Voxware stream descriptor"))
                if header is not None or hi-lo != 40 or size != 40:
                    raise FormatError("only one 40-byte VOX! descriptor is implemented")
                header = bytes(buf[lo:hi])
            elif tag == b"VOXd":
                if payload is not None:
                    raise FormatError("multiple VOXd payloads in one member are not implemented")
                payload = (lo, hi)
                regions.append((lo, hi, "compressed frames and terminal bits"))
            else:
                regions.append((lo, hi, "uninterpreted Voxware " + repr(tag)))
                warnings.append(f"uninterpreted Voxware chunk {tag!r} at {lo}; skipped by length")
        if header is None or payload is None:
            raise FormatError("VOX! descriptor or VOXd payload missing")
        codec, fs, width, book, flags, frames, private, rate, low, mean, high, scale = VOX_HEADER.unpack(header)
        if codec not in PROFILES:
            raise FormatError(f"Voxware codec 0x{codec:04x} is not implemented")
        if fmt[1] != 1 or rate != PROFILES[codec][0] or fmt[2] != rate:
            raise FormatError("unsupported channel count or inconsistent/profile sample rate")
        if width not in (1, 2) or fmt[4] != width or fmt[5] != width*8:
            raise FormatError("unsupported source PCM sample width/alignment")
        if flags != (6 if codec == 0x504 else 0):
            raise FormatError(f"unsupported codec packing flags 0x{flags:x}")
        if any(not math.isfinite(v) for v in (low, mean, high, scale)):
            warnings.append("nonfinite floating header metadata; normalized for reference decoder")
        streams.append(Stream(len(streams)+1, offset, end, codec, rate, fs, width,
                              book, flags, frames, private, low, mean, high, scale,
                              fact, fmt, payload[0], payload[1]-payload[0], header,
                              warnings, regions))
        offset = end
        if declared_end & 1 and offset < len(buf):
            # RIFF alignment is outside its own declared size.
            streams[-1].regions.append((offset, offset+1, "RIFF alignment byte"))
            offset += 1
    if not streams:
        raise FormatError("no supported Voxware stream")
    return streams, global_warnings


def audit_frames(buf, stream):
    """Exact frame boundary parser, using the reference codec's width table."""
    data = memoryview(buf)[stream.payload_offset:stream.payload_offset+stream.payload_size]
    limit, bit, count = len(data)*8, 0, 0
    if stream.codec == 0x504:
        count = min(stream.declared_frames, limit//54)
        bit = count*54
    else:
        base = 57 if stream.codec == 0x403 else 83
        while count < stream.declared_frames and bit+12 <= limit:
            pos, shift = divmod(bit, 8)
            word = int.from_bytes(data[pos:pos+3], "little") >> shift
            voicing, pitch = word & 15, (word >> 4) & 255
            harmonics = min(31, HARMONICS[voicing*256+pitch]) if voicing else 0
            size = base + 4*harmonics
            if bit+size > limit:
                break
            bit += size
            count += 1
    stream.complete_frames, stream.frame_bits = count, bit
    stream.tail_bits = limit-bit
    # Preserve a byte-exact representation of all unused/partial final bits.
    tail = bytes(data[bit//8:])
    stream.tail_hex = tail.hex() if len(tail) < 4096 else hashlib.sha256(tail).hexdigest()
    if count < stream.declared_frames:
        stream.warnings.append(f"only {count} complete frames of {stream.declared_frames}; "
                               "incomplete final data excluded from synthesis")
    if stream.tail_bits > 8 and count == stream.declared_frames:
        stream.warnings.append(f"{stream.tail_bits} terminal bits after declared frames")
    return count


def _chunk(tag, payload):
    return tag+U32.pack(len(payload))+payload+(b"\0" if len(payload) & 1 else b"")


def decoder_input(buf, s):
    """Construct bounded decoder input; retain all complete compressed frames."""
    header = bytearray(s.header)
    struct.pack_into("<I", header, 12, s.complete_frames)
    for off in (24, 28, 32, 36):
        if not math.isfinite(struct.unpack_from("<f", header, off)[0]):
            struct.pack_into("<f", header, off, 1.0 if off == 36 else 0.0)
    size = (s.frame_bits+7)//8
    encoded = bytes(buf[s.payload_offset:s.payload_offset+size])
    # The decoder reads the frame count, so trailing fill bits are not decoded.
    data = _chunk(b"VOX!", header)+_chunk(b"VOXd", encoded)
    body = b"WAVE"+_chunk(b"fmt ", struct.pack("<HHIIHH", *s.fmt))
    body += _chunk(b"fact", U32.pack(s.fact or 0))+_chunk(b"data", data)
    return b"RIFF"+U32.pack(len(body))+body


class Decoder:
    """Persistent binary IPC to the original codecs, with bounded reads."""

    def __init__(self):
        self.process = None
        self.temporary = None
        self.env = dict(os.environ)
        support = Path(__file__).resolve().parent / "voxware_support"
        for name, expected in SUPPORT_HASHES.items():
            path = support/name
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise DecodeError(f"missing or modified required decoder file: {path}")
        args = [str(support/n) for n in ("decoder_bridge.exe", "mm32dcmp.dll", "VDK32116.DLL")]
        if os.name != "nt":
            wine_exe = shutil.which("wine")
            if not wine_exe:
                raise DecodeError("Wine with 32-bit Windows support is required")
            # An explicitly supplied prefix is reused. Otherwise isolate all Wine
            # bookkeeping in a temporary directory and remove it on completion.
            if not self.env.get("WINEPREFIX"):
                self.temporary = tempfile.TemporaryDirectory(prefix="voxware-runtime-")
                self.env["WINEPREFIX"] = str(Path(self.temporary.name)/"wine")
                self.env["WINEARCH"] = "win32"
            self.env.update(WINEDEBUG="-all", DISPLAY="", LIBGL_ALWAYS_SOFTWARE="1",
                            WINEDLLOVERRIDES="winex11.drv,winemenubuilder.exe,winedbg.exe=d")
            args = [wine_exe, args[0]] + ["Z:"+p.replace("/", "\\") for p in args[1:]]
        self.args = args
        try:
            self._start()
        except Exception:
            self.close()
            raise

    def _start(self):
        self.process = subprocess.Popen(self.args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, env=self.env, bufsize=0)
        try:
            if self._read(4, 90) != b"VWX1":
                raise DecodeError("decoder bridge handshake failed")
        except Exception:
            self._stop(force=True)
            raise

    def _stop(self, force=False):
        if self.process is None:
            return
        process, self.process = self.process, None
        if force and process.poll() is None:
            process.kill()
        try:
            process.stdin.close()
            process.wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            if process.poll() is None:
                process.kill()
            process.wait()
        process.stdout.close()

    def _read(self, n, timeout=60):
        result = bytearray()
        deadline = time.monotonic()+timeout
        if os.name == "nt":
            # Windows anonymous pipes do not support select().
            while len(result) < n:
                part = self.process.stdout.read(min(n-len(result), 65536))
                if not part:
                    raise DecodeError("decoder stopped before completing response")
                result.extend(part)
            return bytes(result)
        with selectors.DefaultSelector() as selector:
            selector.register(self.process.stdout, selectors.EVENT_READ)
            while len(result) < n:
                if not selector.select(max(0, deadline-time.monotonic())):
                    raise DecodeError("decoder timed out")
                part = os.read(self.process.stdout.fileno(), min(n-len(result), 65536))
                if not part:
                    raise DecodeError("decoder stopped before completing response")
                result.extend(part)
        return bytes(result)

    def decode(self, buf, s):
        if not s.complete_frames:
            raise DecodeError("no complete encoded frame")
        encoded = decoder_input(buf, s)
        # A 15 ms file-mode or 22.5 ms RT24 frame, plus two flush frames.
        # Capacity is an allocation bound, never an output duration estimate.
        capacity = ((s.complete_frames+2)*s.rate*(45 if s.codec == 0x504 else 30)//1000+64)
        if len(encoded) > 64*1024*1024 or capacity > 512*1024*1024:
            raise DecodeError("stream exceeds the bridge's per-stream memory limit")
        request = struct.pack("<III", int(s.codec == 0x504), len(encoded), capacity)+encoded
        try:
            if self.process is None:
                self._start()
            view = memoryview(request)
            while view:
                written = self.process.stdin.write(view)
                if not written:
                    raise DecodeError("decoder input pipe closed")
                view = view[written:]
            status, detail, size, rate, consumed = struct.unpack("<5I", self._read(20))
            if size > capacity:
                raise DecodeError("invalid decoder output length")
            pcm = self._read(size)
        except OSError as exc:
            self._stop(force=True)
            raise DecodeError(f"decoder communication failed: {exc}") from exc
        except DecodeError:
            # A crash or timeout must not desynchronize subsequent members.
            self._stop(force=True)
            raise
        if status or not pcm or size & 1 or rate != s.rate:
            self._stop(force=True)
            raise DecodeError(f"reference decoder returned status={status}, detail={detail}, "
                              f"bytes={size}, rate={rate}")
        return pcm, consumed

    def close(self):
        self._stop()
        if self.temporary:
            server = shutil.which("wineserver")
            if server:
                subprocess.run([server, "-k"], env=self.env, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=10)
                subprocess.run([server, "-w"], env=self.env, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=10)
            self.temporary.cleanup()
            self.temporary = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def _mkdir(path):
    missing = []
    p = path
    while not p.exists():
        missing.append(p)
        p = p.parent
    path.mkdir(parents=True, exist_ok=True)
    for p in missing:
        p.chmod(0o775)


def convert(input_file, output_dir, verbose=False, decoder=None, progress=None):
    input_file, output_dir = Path(input_file), Path(output_dir)
    buf = input_file.read_bytes()
    streams, warnings = inspect_file(buf)
    for s in streams:
        audit_frames(buf, s)
    names = [f"{input_file.stem}.wav" if len(streams) == 1 else
             f"{input_file.stem}_{s.index:06d}.wav" for s in streams]
    if output_dir.exists() and not output_dir.is_dir():
        raise DecodeError(f"output path is not a directory: {output_dir}")
    # Never overwrite an existing result or the input itself.
    existing = {p.name for p in output_dir.iterdir()} if output_dir.exists() else set()
    for name in names:
        if name in existing:
            raise DecodeError(f"output file already exists: {output_dir/name}")
    if verbose and input_file.stem+".voxware.json" in existing:
        raise DecodeError("verbose diagnostic file already exists")
    own_decoder = decoder is None
    results = []
    directory_ready = False
    try:
        if own_decoder:
            decoder = Decoder()
        for s, name in zip(streams, names):
            result = {"index": s.index, "offset": s.offset, "codec": s.codec,
                      "rate": s.rate, "warnings": s.warnings}
            try:
                pcm, consumed = decoder.decode(buf, s)
                if not directory_ready:
                    _mkdir(output_dir)
                    directory_ready = True
                target = output_dir/name
                created = False
                try:
                    # Exclusive creation keeps preexisting output directories safe.
                    with target.open("xb") as raw:
                        created = True
                        with wave.open(raw, "wb") as wav:
                            wav.setparams((1, 2, s.rate, 0, "NONE", "not compressed"))
                            wav.writeframes(pcm)
                    target.chmod(0o664)
                except Exception:
                    if created and target.is_file():
                        target.unlink()
                    raise
                result.update(output=str(target), samples=len(pcm)//2,
                              duration=len(pcm)/(2*s.rate), decoder_consumed=consumed)
            except DecodeError as exc:
                result["error"] = str(exc)
            if verbose:
                result["structure"] = s.metadata()
            results.append(result)
            if progress:
                progress(result, len(streams))
    finally:
        if own_decoder and decoder:
            decoder.close()
    if not any("output" in r for r in results):
        raise DecodeError("; ".join(dict.fromkeys(r.get("error", "no output") for r in results)))
    report = {"input": str(input_file), "input_bytes": len(buf),
              "warnings": warnings, "streams": results}
    if verbose:
        report["input_sha256"] = hashlib.sha256(buf).hexdigest()
        path = output_dir/(input_file.stem+".voxware.json")
        with path.open("x", encoding="utf-8") as f:
            json.dump(report, f, indent=2, allow_nan=True)
            f.write("\n")
        path.chmod(0o664)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    parser.add_argument("-verbose", "--verbose", action="store_true",
                        help="also write a structural diagnostic JSON file")
    args = parser.parse_args(argv)
    try:
        report = convert(args.inputFile, args.outputDir, args.verbose)
    except (OSError, ValueError, DecodeError, subprocess.SubprocessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    failed = sum("error" in r for r in report["streams"])
    warnings = report["warnings"] + [w for r in report["streams"] for w in r["warnings"]]
    for warning in dict.fromkeys(warnings):
        print(f"warning: {warning}", file=sys.stderr)
    for r in report["streams"]:
        if "error" in r:
            print(f"warning: stream {r['index']}: {r['error']}", file=sys.stderr)
    print(f"Wrote {len(report['streams'])-failed} WAV file(s) to {args.outputDir}")
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
