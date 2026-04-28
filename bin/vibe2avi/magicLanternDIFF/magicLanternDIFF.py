#!/usr/bin/env python3
# Vibe coded by Codex
import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path


COOKIE = b"\x48\xa8\x9a\x61"
END_CHUNK = 0x0000FFFF


class DiffError(Exception):
    pass


def be32(data, off=0):
    return struct.unpack_from(">I", data, off)[0]


def be16(data, off=0):
    return struct.unpack_from(">H", data, off)[0]


def read_chunks(data, start):
    chunks = []
    pos = start
    while True:
        if pos + 8 > len(data):
            raise DiffError("chunk header extends past end of file")
        typ = be32(data, pos)
        size = be32(data, pos + 4)
        payload_start = pos + 8
        payload_end = payload_start + size
        if payload_end > len(data):
            raise DiffError("chunk payload extends past end of file")
        chunks.append((typ, data[payload_start:payload_end]))
        pos = payload_end
        if typ == END_CHUNK:
            if size != 0:
                raise DiffError("end chunk has a non-zero size")
            break
    trailing = data[pos:]
    return chunks, trailing


def validate_index(trailing, chunks):
    if not trailing:
        return None
    if len(trailing) < 16:
        raise DiffError("trailing index is too short")
    frame_count = be32(trailing, 0)
    index_size = be32(trailing, 4)
    if len(trailing) != 8 + index_size:
        raise DiffError("trailing index length does not match its size field")
    payload = trailing[8:]
    if index_size < 8 or (index_size - 8) % 8:
        raise DiffError("trailing index has an invalid entry table size")
    if payload[-4:] != COOKIE:
        raise DiffError("trailing index cookie does not match the file cookie")
    indexed_chunk_count = be32(payload, index_size - 8)
    entries = []
    for off in range(0, index_size - 8, 8):
        entries.append((be32(payload, off), be32(payload, off + 4)))
    actual = [(typ, len(payload)) for typ, payload in chunks]
    if indexed_chunk_count != len(chunks) or entries != actual:
        raise DiffError("trailing index does not match the chunk stream")
    return frame_count


def decode_palette12(payload):
    if len(payload) % 2:
        raise DiffError("12-bit palette chunk has odd length")
    palette = []
    for off in range(0, len(payload), 2):
        word = be16(payload, off)
        palette.append((((word >> 8) & 0xF) * 17,
                        ((word >> 4) & 0xF) * 17,
                        (word & 0xF) * 17))
    return palette


def decode_palette24(payload):
    if len(payload) % 3:
        raise DiffError("24-bit palette chunk length is not divisible by 3")
    return [tuple(payload[i:i + 3]) for i in range(0, len(payload), 3)]


def decode_rle12(payload):
    if len(payload) < 4:
        raise DiffError("RLE chunk is too short")
    target = be32(payload, 0)
    pos = 4
    out = bytearray()
    while pos < len(payload) and len(out) < target:
        code = payload[pos]
        pos += 1
        if code == 0x7F:
            continue
        if code < 0x80:
            if pos + code > len(payload):
                raise DiffError("RLE literal run extends past chunk")
            out.extend(payload[pos:pos + code])
            pos += code
        else:
            run = 256 - code
            if pos >= len(payload):
                raise DiffError("RLE repeat run has no value byte")
            out.extend([payload[pos]] * run)
            pos += 1
    if len(out) != target:
        raise DiffError("RLE chunk did not produce its declared size")
    remainder = payload[pos:]
    if remainder and (remainder[0] != 0x7F or len(remainder) > 2):
        raise DiffError("RLE chunk has unexpected bytes after the final marker")
    return bytes(out)


def vertical_to_row_major(buf, columns, rows):
    if columns <= 0 or rows <= 0 or len(buf) != columns * rows:
        raise DiffError("vertical data dimensions do not match decoded size")
    out = bytearray(len(buf))
    for x in range(columns):
        out[x:len(out):columns] = buf[x * rows:(x + 1) * rows]
    return bytes(out)


def row_major_to_vertical(buf, columns, rows):
    if columns <= 0 or rows <= 0 or len(buf) != columns * rows:
        raise DiffError("row-major data dimensions do not match decoded size")
    out = bytearray(len(buf))
    for x in range(columns):
        out[x * rows:(x + 1) * rows] = buf[x:len(buf):columns]
    return bytes(out)


def apply_delta(buf, payload):
    out = bytearray(buf)
    if len(payload) < 2:
        raise DiffError("delta chunk is too short")
    src = 2
    dst = be16(payload, 0)
    while src < len(payload):
        skip = payload[src]
        src += 1
        if skip == 0xFF:
            if src >= len(payload):
                break
            lo = payload[src]
            src += 1
            if lo == 0xFF:
                break
            if src >= len(payload):
                break
            hi = payload[src]
            src += 1
            skip = (hi << 8) | lo
        if src >= len(payload):
            break
        count = payload[src]
        src += 1
        dst += skip
        if dst >= len(out):
            break
        available = len(payload) - src
        take = min(count, available)
        take = min(take, len(out) - dst)
        out[dst:dst + take] = payload[src:src + take]
        src += min(count, available)
        dst += take
        if take != count:
            break
    return bytes(out)


def apply_vertical_delta(buf, payload, columns, rows, pages=1):
    page_columns = columns * pages
    vertical = bytearray(row_major_to_vertical(buf, page_columns, rows))
    src = 0
    dst = 0
    while src + 2 <= len(payload):
        skip = payload[src]
        count = payload[src + 1]
        src += 2
        if skip == 0xFF:
            if count == 0xFF:
                break
            dst = (dst // rows + 1 + count) * rows
            if dst > len(vertical):
                raise DiffError("type 22 delta skips past the planar page buffer")
            continue
        dst += skip
        if dst > len(vertical):
            raise DiffError("type 22 delta skips past the planar page buffer")
        if src + count > len(payload):
            raise DiffError("type 22 delta copy extends past chunk")
        if dst + count > len(vertical):
            raise DiffError("type 22 delta copy extends past the planar page buffer")
        available = len(payload) - src
        if count > available:
            raise DiffError("type 22 delta copy extends past chunk")
        for index, value in enumerate(payload[src:src + count]):
            vertical[dst + index] ^= value
        src += count
        dst += count
    if payload[src:] not in (b"", b"\x00"):
        raise DiffError("type 22 delta has unexpected terminal bytes")
    return vertical_to_row_major(bytes(vertical), page_columns, rows)


def expand_planar_pages(buf, columns, rows, pages):
    if pages == 1:
        return buf
    if len(buf) != columns * rows:
        raise DiffError("planar page source has the wrong size")
    out = bytearray(columns * rows * pages)
    row_stride = columns * pages
    for y in range(rows):
        src = y * columns
        row = buf[src:src + columns]
        dst = y * row_stride
        for page in range(pages):
            out[dst + page * columns:dst + (page + 1) * columns] = row
    return bytes(out)


def extract_planar_page(buf, columns, rows, pages, page=0):
    if pages == 1:
        return buf
    if len(buf) != columns * rows * pages:
        raise DiffError("planar page buffer has the wrong size")
    out = bytearray(columns * rows)
    row_stride = columns * pages
    for y in range(rows):
        src = y * row_stride + page * columns
        out[y * columns:(y + 1) * columns] = buf[src:src + columns]
    return bytes(out)


def plane_row_bytes(width):
    return ((width + 15) // 16) * 2


def planar_indices(planes, width, height):
    row_bytes = plane_row_bytes(width)
    if any(len(p) != row_bytes * height for p in planes):
        raise DiffError("planar frame has a plane with the wrong size")
    indices = bytearray(width * height)
    byte_width = (width + 7) // 8
    for plane_no, plane in enumerate(planes):
        mask_value = 1 << plane_no
        for y in range(height):
            row = y * row_bytes
            for xb in range(byte_width):
                val = plane[row + xb]
                if not val:
                    continue
                base_x = xb * 8
                for bit in range(8):
                    x = base_x + bit
                    if x < width and (val & (0x80 >> bit)):
                        indices[y * width + x] |= mask_value
    return indices


def palette_rgb(indices, palette):
    out = bytearray(len(indices) * 3)
    for i, idx in enumerate(indices):
        rgb = palette[idx] if idx < len(palette) else (0, 0, 0)
        out[i * 3:i * 3 + 3] = bytes(rgb)
    return bytes(out)


def ham_rgb(indices, width, height, palette, depth):
    bits = depth - 2
    data_mask = (1 << bits) - 1
    out = bytearray(width * height * 3)
    for y in range(height):
        r = g = b = 0
        for x in range(width):
            value = indices[y * width + x]
            control = value >> bits
            data = value & data_mask
            if control == 0:
                r, g, b = palette[data] if data < len(palette) else (0, 0, 0)
            elif control == 1:
                b = (data * 255) // data_mask
            elif control == 2:
                r = (data * 255) // data_mask
            else:
                g = (data * 255) // data_mask
            off = (y * width + x) * 3
            out[off:off + 3] = bytes((r, g, b))
    return bytes(out)


def render_packed_2bit(buf, width, height, palette):
    if len(buf) * 4 != width * height:
        raise DiffError("2-bit packed frame has the wrong size")
    out = bytearray(width * height * 3)
    dst = 0
    for byte in buf:
        for shift in (6, 4, 2, 0):
            rgb = palette[(byte >> shift) & 3] if palette else (0, 0, 0)
            out[dst:dst + 3] = bytes(rgb)
            dst += 3
    return bytes(out)


def unpack_2bit_component(buf, pixel_count):
    out = bytearray(pixel_count)
    dst = 0
    for byte in buf:
        for shift in (6, 4, 2, 0):
            if dst < pixel_count:
                out[dst] = (byte >> shift) & 3
                dst += 1
    return out


def render_packed2x4(components, width, height, palette):
    pixel_count = width * height
    indices = bytearray(pixel_count)
    for comp_no, component in enumerate(components):
        values = unpack_2bit_component(component, pixel_count)
        shift = comp_no * 2
        for i, value in enumerate(values):
            indices[i] |= value << shift
    return palette_rgb(indices, palette)


def should_use_ham(depth, palette12, palette24):
    if depth not in (6, 8) or not palette12:
        return False
    if depth == 8:
        return True
    return all(rgb == (0, 0, 0) for rgb in palette12[16:32])


def parse_diff(path):
    data = Path(path).read_bytes()
    if len(data) < 24:
        raise DiffError("file is too short")
    if data[:4] != b"DIFF" or data[4:8] != COOKIE or be32(data, 8) != 0:
        raise DiffError("not a Magic Lantern DIFF file")
    header_size = be32(data, 12)
    if header_size not in (18, 30):
        raise DiffError(f"unsupported header size {header_size}")
    header_start = 16
    chunk_start = header_start + header_size
    if chunk_start > len(data):
        raise DiffError("header extends past end of file")
    display = be16(data, 16)
    width = be16(data, 18)
    height = be16(data, 20)
    depth = data[22]
    fps = data[23]
    if not width or not height or not depth or not fps:
        raise DiffError("invalid zero width, height, depth, or frame rate")
    chunks, trailing = read_chunks(data, chunk_start)
    index_frame_count = validate_index(trailing, chunks)
    return {
        "display": display,
        "width": width,
        "height": height,
        "depth": depth,
        "fps": fps,
        "header_size": header_size,
        "index_frame_count": index_frame_count,
        "chunks": chunks,
    }


def planar_page_count(info):
    if any(typ == 22 for typ, _ in info["chunks"]):
        return 8
    return 1


def effective_fps(info):
    if planar_page_count(info) > 1:
        return info["fps"] // 2 if info["fps"] % 2 == 0 else info["fps"] / 2
    return info["fps"]


def decode_frames(info):
    width = info["width"]
    height = info["height"]
    depth = info["depth"]
    row_bytes = plane_row_bytes(width)
    plane_size = row_bytes * height
    pages = planar_page_count(info)
    chunky_size = width * height
    rgb_size = chunky_size * 3
    palette12 = []
    palette24 = []
    mode = None
    frames = []
    planes = [bytes(plane_size * pages) for _ in range(depth if depth <= 8 else 1)]
    packed_components = []
    plane_index = 0
    component_index = 0
    current = None
    unit_size = None
    planar_units = 0

    def render_current_planar():
        visible_planes = [extract_planar_page(p, row_bytes, height, pages) for p in planes[:depth]]
        indices = planar_indices(visible_planes, width, height)
        palette = palette12 or palette24
        if should_use_ham(depth, palette12, palette24):
            return ham_rgb(indices, width, height, palette12, depth)
        return palette_rgb(indices, palette)

    def emit_planar_frame():
        frame = render_current_planar()
        repeat = 3 if pages > 1 else 1
        frames.extend([frame] * repeat)

    def advance_planar_frame(display=True):
        nonlocal plane_index, planar_units
        plane_index = (plane_index + 1) % depth
        if pages > 1:
            if display and plane_index == 0:
                emit_planar_frame()
            return
        planar_units += 1
        units_for_frame = depth
        if planar_units == units_for_frame:
            emit_planar_frame()
            planar_units = 0
        elif planar_units > units_for_frame:
            raise DiffError("planar frame cadence overran expected display boundary")

    for typ, payload in info["chunks"]:
        if typ == END_CHUNK:
            break
        if typ == 1:
            if len(payload) != 256:
                raise DiffError("type 1 display setup chunk is not 256 bytes")
            continue
        if typ == 6:
            palette12 = decode_palette12(payload)
            continue
        if typ == 9:
            palette24 = decode_palette24(payload)
            continue
        if typ == 30:
            continue
        if typ in (15, 25, 26, 32):
            if payload and typ == 15:
                decoded = bytes(payload)
                raw_from_rle = False
            else:
                if typ == 32 and payload:
                    continue
                if payload:
                    raise DiffError(f"type {typ} no-op chunk has an unexpected payload")
                decoded = None
            if decoded is not None:
                if mode == "planar":
                    if len(decoded) != plane_size:
                        raise DiffError("type 15 planar chunk has the wrong size")
                    planes[plane_index] = expand_planar_pages(decoded, row_bytes, height, pages)
                    advance_planar_frame()
                elif mode == "packed2x4":
                    if len(decoded) != unit_size:
                        raise DiffError("type 15 packed component has the wrong size")
                    packed_components[component_index] = decoded
                    component_index = (component_index + 1) % 4
                    if component_index == 0:
                        frames.append(render_chunky(mode, packed_components, width, height, palette24 or palette12))
                elif mode in ("chunky8", "rgb24", "packed2"):
                    current = decoded
                    frames.append(render_chunky(mode, current, width, height, palette24 or palette12))
                continue
            if mode == "planar":
                advance_planar_frame()
            elif mode == "packed2x4":
                component_index = (component_index + 1) % 4
                if component_index == 0:
                    frames.append(render_chunky(mode, packed_components, width, height, palette24 or palette12))
            elif mode in ("chunky8", "rgb24", "packed2"):
                if current is not None:
                    frames.append(render_chunky(mode, current, width, height, palette24 or palette12))
            continue
        if typ == 10:
            decoded = bytes(payload)
            raw_from_rle = False
        elif typ == 12:
            decoded = decode_rle12(payload)
            raw_from_rle = True
        elif typ in (21, 22):
            if current is None and mode not in ("planar", "packed2x4"):
                raise DiffError("delta chunk appears before a full frame buffer")
            if mode == "planar":
                if typ == 22:
                    planes[plane_index] = apply_vertical_delta(planes[plane_index], payload, row_bytes, height, pages)
                else:
                    planes[plane_index] = apply_delta(planes[plane_index], payload)
                advance_planar_frame(display=(pages == 1))
            elif mode == "packed2x4":
                if not packed_components:
                    raise DiffError("packed delta appears before all packed components")
                packed_components[component_index] = apply_delta(packed_components[component_index], payload)
                component_index = (component_index + 1) % 4
                if component_index == 0:
                    frames.append(render_chunky(mode, packed_components, width, height, palette24 or palette12))
            else:
                current = apply_delta(current, payload)
                frames.append(render_chunky(mode, current, width, height, palette24 or palette12))
            continue
        else:
            raise DiffError(f"unsupported chunk type {typ}")

        if mode is None:
            unit_size = len(decoded)
            if unit_size == plane_size and depth <= 8:
                mode = "planar"
            elif depth == 24 and unit_size == rgb_size:
                mode = "rgb24"
            elif depth == 8 and unit_size == chunky_size:
                mode = "chunky8"
            elif depth == 8 and unit_size * 4 == chunky_size:
                mode = "packed2x4"
                packed_components = [bytes(unit_size) for _ in range(4)]
            else:
                raise DiffError(f"cannot classify video buffer size {unit_size}")

        if mode == "planar":
            if len(decoded) != plane_size:
                raise DiffError("planar chunk size changed within the stream")
            if raw_from_rle:
                decoded = vertical_to_row_major(decoded, row_bytes, height)
            planes[plane_index] = expand_planar_pages(decoded, row_bytes, height, pages)
            advance_planar_frame()
        elif mode == "packed2x4":
            if len(decoded) != unit_size:
                raise DiffError("packed component size changed within the stream")
            if raw_from_rle:
                decoded = vertical_to_row_major(decoded, width // 4, height)
            packed_components[component_index] = decoded
            component_index = (component_index + 1) % 4
            if component_index == 0:
                frames.append(render_chunky(mode, packed_components, width, height, palette24 or palette12))
        elif mode == "chunky8":
            if len(decoded) != chunky_size:
                raise DiffError("chunky frame size changed within the stream")
            if raw_from_rle:
                decoded = vertical_to_row_major(decoded, width, height)
            current = decoded
            frames.append(render_chunky(mode, current, width, height, palette24 or palette12))
        elif mode == "rgb24":
            if len(decoded) != rgb_size:
                raise DiffError("RGB frame size changed within the stream")
            current = decoded
            frames.append(current)
        elif mode == "packed2":
            if len(decoded) != unit_size:
                raise DiffError("packed 2-bit frame size changed within the stream")
            if raw_from_rle:
                decoded = vertical_to_row_major(decoded, width // 4, height)
            current = decoded
            frames.append(render_chunky(mode, current, width, height, palette24 or palette12))

    if mode == "planar" and plane_index != 0:
        raise DiffError("stream ended mid-planar-frame")
    if mode == "planar" and planar_units != 0:
        raise DiffError("stream ended before the current displayed frame completed")
    if mode == "packed2x4" and component_index != 0:
        raise DiffError("stream ended mid-packed-frame")
    if not frames:
        frames.append(bytes(width * height * 3))
    return frames


def video_units_per_frame(info):
    width = info["width"]
    height = info["height"]
    depth = info["depth"]
    plane_size = plane_row_bytes(width) * height
    chunky_size = width * height
    for typ, payload in info["chunks"]:
        if typ == 12 and len(payload) >= 4:
            unit_size = be32(payload, 0)
        elif typ in (10, 15):
            unit_size = len(payload)
        else:
            continue
        if depth <= 8 and unit_size == plane_size:
            return depth
        if depth == 8 and unit_size * 4 == chunky_size:
            return 4
        return 1
    return 1


def frame_count_before_chunk(info, chunk_index):
    if planar_page_count(info) > 1:
        units = 0
        frames = 0
        for typ, payload in info["chunks"][:chunk_index]:
            if typ not in (12, 15):
                continue
            unit_size = be32(payload, 0) if typ == 12 and len(payload) >= 4 else len(payload)
            if unit_size != plane_row_bytes(info["width"]) * info["height"]:
                continue
            units += 1
            if units == info["depth"]:
                frames += 3
                units = 0
        return frames

    units_per_frame = video_units_per_frame(info)
    units = 0
    frames = 0
    for typ, payload in info["chunks"][:chunk_index]:
        if typ in (10, 12, 15, 21, 22, 25, 26):
            units += 1
            current_units_per_frame = (
                info["depth"] if planar_page_count(info) > 1 and frames == 0 else units_per_frame
            )
            if units == current_units_per_frame:
                frames += 1
                units = 0
    return frames


def decode_audio(info):
    tracks = []
    for index, (typ, payload) in enumerate(info["chunks"]):
        if typ != 30:
            continue
        if len(payload) < 6:
            raise DiffError("audio chunk is too short")
        volume = be32(payload, 0)
        sample_rate = be16(payload, 4)
        if volume > 64 or sample_rate == 0:
            raise DiffError("audio chunk has an invalid volume or sample rate")
        frame_offset = frame_count_before_chunk(info, index)
        tracks.append((sample_rate, frame_offset, payload[6:]))
    if not tracks:
        return None
    sample_rate = tracks[0][0]
    if any(rate != sample_rate for rate, _, _ in tracks):
        raise DiffError("multiple audio chunks use different sample rates")
    timeline = bytearray()
    for _, frame_offset, samples in tracks:
        sample_offset = round(frame_offset * sample_rate / effective_fps(info))
        if len(timeline) < sample_offset:
            timeline.extend(b"\x00" * (sample_offset - len(timeline)))
        timeline.extend(samples)
    return sample_rate, bytes(timeline)


def render_chunky(mode, current, width, height, palette):
    if mode == "chunky8":
        return palette_rgb(current, palette)
    if mode == "rgb24":
        return current
    if mode == "packed2":
        return render_packed_2bit(current, width, height, palette)
    if mode == "packed2x4":
        return render_packed2x4(current, width, height, palette)
    raise DiffError(f"unknown render mode {mode}")


def write_avi(frames, width, height, fps, output_path, audio=None):
    out = Path(output_path)
    tmp = None
    audio_tmp = None
    try:
        with tempfile.NamedTemporaryFile(prefix=out.name + ".", suffix=".avi", dir=str(out.parent), delete=False) as fh:
            tmp = Path(fh.name)
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{width}x{height}", "-r", str(fps),
            "-i", "pipe:0",
        ]
        if audio:
            sample_rate, samples = audio
            with tempfile.NamedTemporaryFile(prefix=out.name + ".", suffix=".s8", dir=str(out.parent), delete=False) as fh:
                audio_tmp = Path(fh.name)
                fh.write(samples)
            cmd.extend([
                "-f", "s8", "-ar", str(sample_rate), "-ac", "1",
                "-i", str(audio_tmp),
            ])
        else:
            cmd.append("-an")
        cmd.extend(["-c:v", "rawvideo", "-pix_fmt", "bgr24"])
        if audio:
            cmd.extend(["-c:a", "pcm_u8"])
        cmd = [
            *cmd,
            str(tmp),
        ]
        proc = subprocess.run(cmd, input=b"".join(frames), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode:
            raise DiffError(proc.stderr.decode("utf-8", "replace").strip() or "ffmpeg failed")
        os.replace(tmp, out)
        os.chmod(out, 0o664)
    except Exception:
        if tmp and tmp.exists():
            tmp.unlink()
        if audio_tmp and audio_tmp.exists():
            audio_tmp.unlink()
        if out.exists():
            out.unlink()
        raise
    finally:
        if audio_tmp and audio_tmp.exists():
            audio_tmp.unlink()


def convert(input_path, output_path):
    info = parse_diff(input_path)
    frames = decode_frames(info)
    audio = decode_audio(info)
    write_avi(frames, info["width"], info["height"], effective_fps(info), output_path, audio)


def main(argv):
    if len(argv) != 3:
        print("usage: magicLanternDIFF.py <inputFile> <outputFile>", file=sys.stderr)
        return 2
    try:
        convert(argv[1], argv[2])
    except DiffError as exc:
        try:
            Path(argv[2]).unlink()
        except FileNotFoundError:
            pass
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
