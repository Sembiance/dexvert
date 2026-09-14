#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract the fixed-layout Roland S-7xx SCSI filesystem. Standard library only.

See rolandDisk.txt for the format, recovery rules and unresolved semantics.
Native .prm files contain unmodified parameter records, not generated metadata.
Only --all writes JSON and a reversible physical byte audit.
"""

from __future__ import annotations

import argparse
import array
from collections import Counter
import hashlib
import json
import mmap
import os
from pathlib import Path
import re
import struct
import sys
import wave

BLOCK = 512
CLUSTER = 9216
FAT_OFFSET = 0x80800
DATA_OFFSET = 0x2B5800
FIRST_RESERVED = 0xFFF6
RATES = {0: 48000, 1: 44100, 2: 24000, 3: 22050, 4: 30000, 5: 15000}
LOOPS = {0: "forward_end", 1: "forward_release", 2: "one_shot",
         3: "forward_one_shot", 4: "alternate", 5: "reverse_one_shot",
         6: "reverse_loop"}
# kind, tag, directory offset, capacity, parameter offset, parameter size
TABLES = (
    ("volume", 0x40, 0xA0800, 128, 0x10D800, 256),
    ("performance", 0x41, 0xA1800, 512, 0x115800, 512),
    ("patch", 0x42, 0xA5800, 1024, 0x155800, 512),
    ("partial", 0x43, 0xAD800, 4096, 0x1D5800, 128),
    ("sample", 0x44, 0xCD800, 8192, 0x255800, 48),
)


class UnsupportedFormat(ValueError):
    """Not a supported fixed-layout image; no output may be created."""


def u16(data, offset=0):
    return struct.unpack_from("<H", data, offset)[0]


def u32(data, offset=0):
    return struct.unpack_from("<I", data, offset)[0]


def text_name(raw):
    # DEL is a Roland display glyph, not a path separator. Preserve it in JSON.
    return raw.decode("ascii", "backslashreplace").rstrip("\x00 ")


def safe_name(value):
    value = value.replace("\x7f", "_")
    value = re.sub(r"[^A-Za-z0-9 ._()+,=@-]", "_", value).strip(" .")
    return value[:100] or "unnamed"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def identify(data):
    """Fixed signatures and structural fields only; no extension/name guessing."""
    if len(data) < 14 or data[4:14] != b"S770 MR25A":
        raise UnsupportedFormat("missing Roland S770 MR25A signature at byte 4")
    if len(data) < 0x11E:
        raise UnsupportedFormat("Roland signature present, but insufficient header to identify the layout")
    counts = struct.unpack_from("<5H", data, 0x114)
    capacity = u32(data, 0x110)
    descriptor = (re.fullmatch(rb"ID[0-7]:[\x20-\x7f]{12}", data[0x100:0x110])
                  and capacity >= DATA_OFFSET // BLOCK
                  and all(n <= t[3] for n, t in zip(counts, TABLES)))
    fat_id = len(data) >= FAT_OFFSET + 2 and u16(data, FAT_OFFSET) == 0xFFFA
    if not descriptor and not fat_id:
        raise UnsupportedFormat(
            "Roland signature present, but neither the fixed-layout disk descriptor nor FAT ID exists; "
            "system-floppy/other layouts are not implemented")
    return {"format": "Roland S-7xx fixed-layout SCSI", "input_bytes": len(data),
            "revision_raw": u32(data), "media_byte_raw": data[15],
            "system_description": text_name(data[0x20:0x3F]),
            "copyright": text_name(data[0x40:0x5F]),
            "disk_name": text_name(data[0x100:0x110]),
            "declared_blocks": capacity,
            "declared_counts": dict(zip((t[0] for t in TABLES), counts)),
            "descriptor_valid": bool(descriptor), "fat_id_valid": bool(fat_id)}


def decode_parameters(kind, p):
    """Expose established field locations; retain every unassigned byte explicitly.

    Instrument scalar names describe controls. Their full physical scaling and
    firmware-dependent bit encodings are not claimed to be decoded.
    """
    result = {"name": text_name(p[:16])}
    covered = bytearray(len(p))
    covered[:16] = b"\1" * min(16, len(p))

    def field(name, off, fmt):
        length = struct.calcsize("<" + fmt)
        if off + length > len(p):
            return
        values = struct.unpack_from("<" + fmt, p, off)
        result[name] = values[0] if len(values) == 1 else list(values)
        covered[off:off + length] = b"\1" * length

    def bytes_fields(names, off, signed=()):
        for i, name in enumerate(names.split()):
            field(name, off + i, "b" if name in signed else "B")

    if kind == "volume":
        field("performance_slots", 32, "64h")
    elif kind == "performance":
        for name, off, fmt in (
            ("part_patch_selectors", 16, "32b"), ("midi_channels_packed_raw", 48, "16B"),
            ("part_levels_and_switches_raw", 64, "32B"), ("key_low", 96, "32B"),
            ("key_high", 128, "32B"), ("fade_low", 160, "32B"), ("fade_high", 192, "32B"),
            ("controller_switches_raw", 224, "8H"), ("velocity_curves_packed_raw", 240, "16B"),
            ("patch_slots", 256, "32h")):
            field(name, off, fmt)
    elif kind == "patch":
        bytes_fields("program_change stereo_mix_level pan patch_level output_assign_8 priority "
                     "cutoff velocity_sensitivity octave_shift coarse_tune fine_tune "
                     "smt_control smt_sensitivity output_assign analog_feel", 16)
        field("key_partial_selectors", 32, "88B")
        field("key_assign_types_raw", 128, "88B")
        field("pitch_bender_controls_raw", 224, "4B")
        field("aftertouch_controls_raw", 228, "7B")
        field("modulation_controls_raw", 235, "4B")
        field("controller_controls_raw", 240, "8B")
        field("partial_slots", 256, "88h")
    elif kind == "partial":
        for j, off in enumerate((16, 32, 48, 64)):
            field(f"sample_{j + 1}_index", off, "h")
            names = "pitch_keyfollow level pan coarse_tune fine_tune velocity_low fade_low velocity_high fade_high".split()
            for k, name in enumerate(names):
                field(f"sample_{j + 1}_{name}", off + 2 + k,
                      "b" if name in ("pan", "coarse_tune", "fine_tune") else "B")
        bytes_fields("output_assign_8 stereo_mix_level partial_level output_assign_6", 28)
        bytes_fields("pan coarse_tune fine_tune breath_control", 44, ("coarse_tune", "fine_tune"))
        field("tvf_controls_raw", 75, "21B")
        field("tva_controls_raw", 96, "16B")
        field("lfo_controls_raw", 112, "9B")
    elif kind == "sample":
        for j, name in enumerate(("start", "sustain_start", "sustain_end", "release_start", "release_end")):
            field(name + "_fixed_24_8", 16 + 4 * j, "I")
        bytes_fields("loop_mode sustain_enable_raw sustain_tune release_tune", 36,
                     ("sustain_tune", "release_tune"))
        field("cluster_offset", 40, "H")
        field("cluster_count", 42, "H")
        field("options_raw", 44, "B")
        field("original_key", 45, "B")
        if len(p) >= 46:
            result["sample_rate"] = RATES.get(p[44] & 15)
            result["sample_mode_raw"] = p[44] >> 4
            result["loop_mode_name"] = LOOPS.get(p[36], "unresolved")
    unknown = []
    i = 0
    while i < len(p):
        if covered[i]:
            i += 1
            continue
        start = i
        while i < len(p) and not covered[i]:
            i += 1
        unknown.append({"offset": start, "length": i - start, "hex": p[start:i].hex()})
    result["unassigned_bytes"] = unknown
    return result


class Image:
    def __init__(self, data):
        self.data = data
        self.header = identify(data)
        self.issues = []
        self.entries = []
        self.by_kind = {}
        self.owners = {}
        nfat = max(0, min(131072, len(data) - FAT_OFFSET)) // 2
        self.fat = struct.unpack_from(f"<{nfat}H", data, FAT_OFFSET) if nfat else ()
        self.header["fat_metadata"] = {
            "entries_present": nfat,
            "id_raw": self.fat[0] if nfat else None,
            "free_cluster_count": self.fat[1] if nfat > 1 else None,
            "tail_words_raw": list(self.fat[0xFFF6:]),
            "version_words_raw": list(self.fat[0xFFFE:]),
        }
        self.header["capacity_interpretation"] = (
            "Raw sector capacity used as a conservative exclusive bound; "
            "last-LBA versus sector-count convention is not fully established.")
        if not self.header["descriptor_valid"]:
            self.issues.append("Damaged disk descriptor; fixed directories identified by FAT signature.")
        if not self.header["fat_id_valid"]:
            self.issues.append("FAT missing or damaged; only independently located resources can be recovered.")
        declared_end = self.header["declared_blocks"] * BLOCK
        if len(data) < declared_end:
            self.issues.append(f"Image is {declared_end - len(data)} bytes shorter than its declared capacity.")
        if self.header["descriptor_valid"]:
            self.top_cluster = min(FIRST_RESERVED - 1, 1 + (declared_end - DATA_OFFSET) // CLUSTER)
        else:
            self.top_cluster = FIRST_RESERVED - 1
        for kind, tag, directory, capacity, parameters, size in TABLES:
            entries = {}
            available = max(0, min(capacity, (len(data) - directory) // 32))
            # All fixed slots are examined. Counts are not high-water indices:
            # deletion and sorting may leave holes or reorder the linked list.
            for index in range(available):
                off = directory + index * 32
                raw = data[off:off + 32]
                if raw[16] != tag:
                    continue
                name = text_name(raw[:16])
                poff = parameters + index * size
                p = data[poff:poff + size] if poff < len(data) else b""
                entry = {"kind": kind, "index": index, "name": name,
                         "directory_offset": off, "parameter_offset": poff,
                         "parameter_size": size, "parameter_bytes_present": len(p),
                         "attributes_raw": raw[17], "next_raw": u16(raw, 18),
                         "previous_raw": u16(raw, 20), "link_id_raw": u16(raw, 22),
                         "directory_reserved_raw": raw[24:28].hex(),
                         "first_cluster": u16(raw, 28), "directory_cluster_count": u16(raw, 30),
                         "parameters": decode_parameters(kind, p), "issues": [], "outputs": []}
                if len(p) != size:
                    entry["issues"].append(f"Parameter record truncated: {len(p)}/{size} bytes.")
                entries[index] = entry
                self.entries.append(entry)
            self.by_kind[kind] = entries
            declared = self.header["declared_counts"][kind]
            if len(entries) != declared:
                self.issues.append(f"{kind}: header declares {declared}; {len(entries)} typed directory slots available.")
        self._resolve_references()
        for entry in self.by_kind["sample"].values():
            self._sample_chain(entry)

    def _resolve_references(self):
        for kind, target, key in (("volume", "performance", "performance_slots"),
                                  ("performance", "patch", "patch_slots"),
                                  ("patch", "partial", "partial_slots"),
                                  ("partial", "sample", None)):
            for entry in self.by_kind[kind].values():
                p = entry["parameters"]
                refs = p.get(key, []) if key else [p.get(f"sample_{i}_index", -1) for i in range(1, 5)]
                entry["references"] = [{"kind": target, "slot": i, "index": ref}
                                       for i, ref in enumerate(refs) if ref >= 0]
                missing = sorted({ref for ref in refs if ref >= 0 and ref not in self.by_kind[target]})
                if missing:
                    entry["issues"].append(f"Unresolved {target} references: {missing}")

    def _sample_chain(self, entry):
        count = entry["directory_cluster_count"]
        cluster = entry["first_cluster"]
        chain, seen = [], set()
        if not self.header["fat_id_valid"]:
            entry["issues"].append("Cannot follow sample allocation without a valid FAT ID.")
            entry["clusters"] = []
            return
        for _ in range(count):
            if not 2 <= cluster <= self.top_cluster or cluster >= len(self.fat):
                entry["issues"].append(f"Invalid or unavailable FAT cluster {cluster}.")
                break
            if cluster in seen:
                entry["issues"].append(f"Cyclic FAT chain at cluster {cluster}.")
                break
            nxt = self.fat[cluster]
            if nxt in (0, 1, 0xFFF6, 0xFFF7):
                entry["issues"].append(f"Cluster {cluster} has free/reserved/bad FAT status 0x{nxt:04x}; stopped before it.")
                break
            seen.add(cluster)
            chain.append(cluster)
            self.owners.setdefault(cluster, []).append(entry["index"])
            if nxt >= 0xFFF8:
                break
            cluster = nxt
        if len(chain) != count:
            entry["issues"].append(f"Recovered chain contains {len(chain)}/{count} declared clusters.")
        elif chain and self.fat[chain[-1]] < 0xFFF8:
            entry["issues"].append("Chain continues past declared cluster count; extra clusters not attributed to this sample.")
        entry["clusters"] = chain
        p = entry["parameters"]
        if "cluster_count" in p and p["cluster_count"] != count:
            entry["issues"].append("Directory and parameter cluster counts differ; directory bounds used.")

    def pcm(self, entry):
        chunks = []
        skip = entry["parameters"].get("cluster_offset", 0)
        for c in entry.get("clusters", [])[skip:]:
            at = DATA_OFFSET + (c - 2) * CLUSTER
            b = self.data[at:at + CLUSTER] if at < len(self.data) else b""
            chunks.append(b)
            if len(b) < CLUSTER:
                entry["issues"].append(f"Audio truncated in cluster {c}; contiguous available prefix recovered.")
                break
        return b"".join(chunks)

    def audio(self, entry):
        p = entry["parameters"]
        raw = self.pcm(entry)
        entry["recovered_pcm_bytes"] = len(raw)
        if not raw:
            entry["issues"].append("No sample payload is available.")
            return None
        if entry["parameter_bytes_present"] != 48:
            entry["issues"].append("WAV skipped: complete sample parameters are required; raw PCM retained.")
            return None
        rate = p["sample_rate"]
        mode = p["loop_mode"]
        if rate is None or mode not in LOOPS or p["sample_mode_raw"] not in (0, 1):
            entry["issues"].append("WAV skipped: unresolved rate, loop mode, or sample mode; raw PCM retained.")
            return None
        # One directory entry addresses one mono stream, including mode-nibble 1.
        # Do not infer or interleave a second channel from names or that nibble.
        start = p["start_fixed_24_8"] >> 8
        end_key = "release_end_fixed_24_8" if mode in (1, 3) else "sustain_end_fixed_24_8"
        end = (p[end_key] >> 8) + 1  # Roland endpoint is inclusive.
        if end <= start:
            entry["issues"].append("WAV skipped: end precedes start; raw PCM retained.")
            return None
        available = len(raw) // 2
        if end > available:
            entry["issues"].append(f"Playback ends at frame {end}; only {available} frames available; clipped to available prefix.")
        if start >= available:
            entry["issues"].append("WAV skipped: start is beyond available PCM; raw PCM retained.")
            return None
        pcm = raw[start * 2:min(end, available) * 2]
        if mode in (5, 6):
            words = array.array("h")
            words.frombytes(pcm)
            words.reverse()  # Word order only, no host-endian conversion needed.
            pcm = words.tobytes()
        entry["audio"] = {"rate": rate, "channels": 1, "bits": 16,
                          "frames": len(pcm) // 2, "seconds": len(pcm) / (2 * rate),
                          "source_start_frame": start, "source_end_frame_exclusive": min(end, available),
                          "reversed": mode in (5, 6), "pcm_sha256": digest(pcm)}
        return pcm


class Output:
    """Exclusive-create output: existing unrelated files and symlinks are safe."""
    def __init__(self, root):
        self.root = Path(root).absolute()
        self.files = []

    def mkdir(self, path):
        missing = []
        p = path
        while not p.exists() and not p.is_symlink():
            missing.append(p)
            p = p.parent
        for ancestor in [p, *p.parents]:
            if ancestor.is_symlink():
                raise OSError(f"Refusing output path through symlink: {ancestor}")
        if not p.is_dir():
            raise OSError(f"Output parent is not a directory: {p}")
        for p in reversed(missing):
            p.mkdir(mode=0o755)
            p.chmod(0o755)

    def write(self, relative, data=None, writer=None):
        target = self.root / relative
        if target.is_absolute() and not target.is_relative_to(self.root):
            raise OSError("Output escaped destination")
        if ".." in Path(relative).parts:
            raise OSError("Parent traversal in output path")
        self.mkdir(target.parent)
        attempt = 1
        original = target
        while True:
            try:
                fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o644)
                break
            except FileExistsError:
                attempt += 1
                target = original.with_name(f"{original.stem}~{attempt}{original.suffix}")
        try:
            with os.fdopen(fd, "wb") as f:
                os.fchmod(f.fileno(), 0o644)
                if writer:
                    writer(f)
                else:
                    f.write(data)
        except BaseException:
            target.unlink(missing_ok=True)
            raise
        rel = target.relative_to(self.root).as_posix()
        self.files.append({"path": rel, "bytes": target.stat().st_size})
        return rel


def write_wave(f, pcm, rate):
    # fmt/data are necessary WAV framing; no generated smpl/INFO metadata.
    with wave.open(f, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(pcm)


def physical_audit(image, output, program_path):
    """Disjoint, exhaustive byte preservation. This is NOT semantic decoding."""
    data = image.data
    size = len(data)
    pieces = []

    def save(start, stop, label, existing=None):
        stop = min(stop, size)
        if start >= stop:
            return
        raw = memoryview(data)[start:stop]
        sha = hashlib.sha256(raw).hexdigest()
        path = existing or output.write(f"audit/{start:010x}_{label}.bin", raw)
        pieces.append({"offset": start, "length": stop - start, "category": label,
                       "path": path, "sha256": sha,
                       "semantically_complete": False if label in ("header", "reserved", "program",
                           "outside_declared_filesystem", "unaddressable_tail") or "parameter" in label else None})

    save(0, 0x200, "header")
    save(0x200, 0x800, "reserved")
    save(0x800, FAT_OFFSET, "program", program_path)
    save(FAT_OFFSET, 0xA0800, "fat")
    for kind, _, directory, capacity, parameters, record_size in TABLES:
        save(directory, directory + capacity * 32, kind + "_directory")
    for kind, _, directory, capacity, parameters, record_size in TABLES:
        save(parameters, parameters + capacity * record_size, kind + "_parameters")
    declared_end = image.header["declared_blocks"] * BLOCK
    fs_end = min(size, declared_end) if image.header["descriptor_valid"] else size
    start = DATA_OFFSET
    current = None
    for c in range(2, image.top_cluster + 1):
        at = DATA_OFFSET + (c - 2) * CLUSTER
        if at >= fs_end:
            break
        v = image.fat[c] if c < len(image.fat) else None
        if c in image.owners:
            category = "sample_allocations"
        elif v == 0:
            category = "free_clusters"
        elif v == 1:
            category = "reserved_clusters"
        elif v == 0xFFF7:
            category = "bad_clusters"
        elif v is None:
            category = "unknown_allocation"
        else:
            category = "unreferenced_allocations"
        if current is not None and category != current:
            save(start, at, current)
            start = at
        current = category
    if current is not None:
        end = min(fs_end, DATA_OFFSET + max(0, image.top_cluster - 1) * CLUSTER)
        save(start, end, current)
        start = end
    if start < fs_end:
        save(start, fs_end, "unaddressable_tail")
    if size > max(DATA_OFFSET, fs_end):
        save(max(DATA_OFFSET, fs_end), size, "outside_declared_filesystem")
    pieces.sort(key=lambda item: item["offset"])
    cursor = 0
    for part in pieces:
        if part["offset"] != cursor:
            raise RuntimeError(f"Audit has a gap/overlap at {cursor}")
        cursor += part["length"]
    if cursor != size:
        raise RuntimeError(f"Audit stops at {cursor}, expected {size}")
    return {"preserved_bytes": cursor, "semantic_coverage": "incomplete; preservation is not decoding",
            "reconstruction": "Concatenate the listed files in ascending offset order; no headers are added.",
            "pieces": pieces}


def extract(input_file, output_dir, all_metadata=False):
    input_file = Path(input_file)
    if not input_file.is_file() or input_file.stat().st_size == 0:
        raise UnsupportedFormat("input is empty or is not a regular file")
    with input_file.open("rb") as source, mmap.mmap(source.fileno(), 0, access=mmap.ACCESS_READ) as data:
        image = Image(data)  # Complete recognition precedes any output filesystem change.
        output = Output(output_dir)
        result = {"input": str(input_file), "header": image.header, "issues": image.issues,
                  "entries": image.entries, "outputs": output.files,
                  "limitations": [
                      "No claim of complete semantic reverse engineering: opaque bytes are preserved by --all.",
                      "System-floppy layouts and continuation sets are unsupported.",
                      "Instrument controls are preserved natively; no synthesizer/SFZ rendering.",
                      "One WAV per directory sample; mode nibble 1 is not used to guess stereo pairs.",
                      "Firmware internals, device descriptors, several flags and reserved fields remain unresolved."]}
        program_path = None
        if len(data) > 0x800:
            program_path = output.write("system/program.bin", data[0x800:min(FAT_OFFSET, len(data))])
            result["program_path"] = program_path
        for entry in image.entries:
            stem = f"{entry['index']:04d}_{safe_name(entry['name'])}"
            kind = entry["kind"]
            at = entry["parameter_offset"]
            p = data[at:at + entry["parameter_bytes_present"]] if at < len(data) else b""
            if p:
                suffix = ".prm" if len(p) == entry["parameter_size"] else ".partial.prm"
                entry["outputs"].append(output.write(f"resources/{kind}/{stem}{suffix}", p))
            if kind == "sample":
                pcm = image.audio(entry)
                if pcm is not None:
                    path = output.write(f"audio/{stem}.wav", writer=lambda f, p=pcm, r=entry["audio"]["rate"]: write_wave(f, p, r))
                    entry["outputs"].append(path)
                    entry["audio"]["path"] = path
                elif entry.get("recovered_pcm_bytes"):
                    entry["outputs"].append(output.write(f"resources/sample/{stem}.recovered.pcm", image.pcm(entry)))
        crosslinks = {str(c): ids for c, ids in image.owners.items() if len(ids) > 1}
        if crosslinks:
            image.issues.append(f"{len(crosslinks)} sample clusters are shared/cross-linked; see metadata.")
        result["crosslinked_clusters"] = crosslinks
        result["counts"] = {"native_parameter_records": sum(bool(e["parameter_bytes_present"]) for e in image.entries),
                            "wav_files": sum("audio" in e for e in image.entries),
                            "system_resources": int(program_path is not None),
                            "entries_with_issues": sum(bool(e["issues"]) for e in image.entries)}
        result["status"] = "recovered_with_issues" if image.issues or result["counts"]["entries_with_issues"] else "extracted"
        if all_metadata:
            result["input_sha256"] = hashlib.sha256(data).hexdigest()
            result["audit"] = physical_audit(image, output, program_path)
            result["counts"]["files_before_metadata"] = len(output.files)
            # Serialize a snapshot: the metadata file cannot contain its own final size/hash.
            output.write("metadata.json", (json.dumps(result, indent=2, ensure_ascii=True) + "\n").encode())
        result["counts"]["total_files"] = len(output.files)
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    parser.add_argument("--all", action="store_true", help="also write decoded metadata and a lossless physical byte audit")
    args = parser.parse_args(argv)
    try:
        result = extract(args.inputFile, args.outputDir, args.all)
    except UnsupportedFormat as error:
        print(f"Unsupported: {error}", file=sys.stderr)
        return 2
    except (OSError, ValueError, struct.error) as error:
        print(f"Extraction failed: {error}", file=sys.stderr)
        return 1
    c = result["counts"]
    print(f"{c['wav_files']} WAV files, {c['native_parameter_records']} native parameter records, "
          f"{c['system_resources']} system resources; {c['total_files']} files written.")
    for issue in result["issues"]:
        print(f"Warning: {issue}", file=sys.stderr)
    for entry in result["entries"]:
        for issue in entry["issues"]:
            print(f"Warning: {entry['kind']}[{entry['index']}] {issue}", file=sys.stderr)
    print("Semantic decoding is incomplete; see rolandDisk.txt for unresolved fields.", file=sys.stderr)
    return 3 if result["status"] == "recovered_with_issues" else 0


if __name__ == "__main__":
    sys.exit(main())
