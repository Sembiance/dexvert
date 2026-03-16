# Vibe coded by Claude
"""
WBNK file extractor (Koei Tecmo WaveBank).

Extracts audio from .WBNK sound bank files. Supports two layouts:

  1. Streamed WBNK: Self-contained file with Vorbis packet entries + optional
     trailing PCM data. Vorbis streams output as .vorbis.bin (need external
     codebooks). PCM sections output as .wav.

  2. Indexed WBNK pair: A small index WBNK + a large data WBNK containing raw
     PCM audio. The index stores per-segment channel count, sample rate, offset,
     and size. Each segment is extracted as an individual .wav file.

Usage:
  python unwbnk.py <input.wbnk> <outputDir> [--dump]
  python unwbnk.py <index.wbnk> <data.wbnk> <outputDir> [--dump]

  --dump  Also output .raw section data and .json metadata
"""

import struct
import json
import os
import sys
import wave

EOS_FLAG = 0x0000_0200_0000_0000
GRANULE_NONE = 0xFFFF_FFFF_FFFF_FFFF
HEADER_SIZE = 32
MAX_DATA_SIZE = 0x100000


# ──────────────────────────────────────────────────────────
# Index WBNK detection and parsing
# ──────────────────────────────────────────────────────────

def try_parse_index_wbnk(data):
    """Try to parse data as an index WBNK.

    Index format (header = 16 bytes):
      uint32  version
      uint32  entry_count
      uint32  header_size  (always 16)
      uint32  file_size

    Followed by entry_count * 20-byte entries:
      uint8   channels
      uint8   flags
      uint16  sample_rate
      uint32  audio_offset
      uint32  audio_size
      uint32  unk1
      uint32  unk2

    Returns parsed dict or None if not an index WBNK.
    """
    if len(data) < 16:
        return None
    version = struct.unpack_from('<I', data, 0)[0]
    entry_count = struct.unpack_from('<I', data, 4)[0]
    header_size = struct.unpack_from('<I', data, 8)[0]
    file_size = struct.unpack_from('<I', data, 12)[0]

    if file_size != len(data):
        return None
    if header_size != 16:
        return None
    if header_size + entry_count * 20 != file_size:
        return None
    if entry_count == 0 or entry_count > 100000:
        return None

    entries = []
    off = header_size
    for _ in range(entry_count):
        channels = data[off]
        flags = data[off + 1]
        sample_rate = struct.unpack_from('<H', data, off + 2)[0]
        audio_offset = struct.unpack_from('<I', data, off + 4)[0]
        audio_size = struct.unpack_from('<I', data, off + 8)[0]
        unk1 = struct.unpack_from('<I', data, off + 12)[0]
        unk2 = struct.unpack_from('<I', data, off + 16)[0]
        if sample_rate == 0 or channels == 0:
            return None
        entries.append({
            'channels': channels, 'flags': flags, 'sample_rate': sample_rate,
            'offset': audio_offset, 'size': audio_size,
            'unk1': unk1, 'unk2': unk2,
        })
        off += 20

    return {'version': version, 'entry_count': entry_count, 'entries': entries}


def extract_indexed_wbnk(index_path, data_path, output_dir, dump=False):
    """Extract audio from an index WBNK + data WBNK pair."""
    with open(index_path, 'rb') as f:
        index_data = f.read()
    with open(data_path, 'rb') as f:
        audio_data = f.read()

    idx = try_parse_index_wbnk(index_data)
    if idx is None:
        print(f"Error: {index_path} is not a valid index WBNK")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    print(f"Index: {index_path} ({idx['entry_count']} segments)")
    print(f"Data:  {data_path} ({len(audio_data)} bytes)")

    for i, e in enumerate(idx['entries']):
        audio_num = i + 1
        ch = e['channels']
        sr = e['sample_rate']
        start = e['offset']
        size = e['size']
        end = start + size

        if end > len(audio_data):
            print(f"  {audio_num:03d}.wav  SKIP - offset 0x{start:x}+{size} past data end")
            continue

        pcm = audio_data[start:end]
        duration = size / (ch * 2 * sr)

        wav_path = os.path.join(output_dir, f"{audio_num:03d}.wav")
        with wave.open(wav_path, 'wb') as wf:
            wf.setnchannels(ch)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(pcm)

        ch_str = "mono" if ch == 1 else f"{ch}ch"
        print(f"  {audio_num:03d}.wav  {ch_str} {sr}Hz, ~{duration:.1f}s")

    if dump:
        meta = {
            'index_file': os.path.basename(index_path),
            'data_file': os.path.basename(data_path),
            'data_file_size': len(audio_data),
            'version': idx['version'],
            'segments': [{
                'channels': e['channels'], 'flags': e['flags'],
                'sample_rate': e['sample_rate'],
                'offset': e['offset'], 'size': e['size'],
                'unk1': e['unk1'], 'unk2': e['unk2'],
            } for e in idx['entries']],
        }
        with open(os.path.join(output_dir, "file_info.json"), 'w') as f:
            json.dump(meta, f, indent=2)

    print(f"  {len(idx['entries'])} file(s) extracted")


# ──────────────────────────────────────────────────────────
# Streamed WBNK (original format with Vorbis entries)
# ──────────────────────────────────────────────────────────

def parse_entry(data, offset):
    if offset + HEADER_SIZE > len(data):
        return None, offset
    flags = struct.unpack_from('<I', data, offset)[0]
    data_size = struct.unpack_from('<I', data, offset + 4)[0]
    packet_flags = struct.unpack_from('<Q', data, offset + 8)[0]
    granule_pos = struct.unpack_from('<Q', data, offset + 16)[0]
    seq = struct.unpack_from('<Q', data, offset + 24)[0]
    payload_start = offset + HEADER_SIZE
    payload_end = payload_start + data_size
    if payload_end > len(data) or data_size > MAX_DATA_SIZE:
        return None, offset
    return {
        'header_offset': offset, 'flags': flags, 'data_size': data_size,
        'packet_flags': packet_flags, 'granule_pos': granule_pos,
        'seq': seq, 'payload_offset': payload_start,
    }, payload_end


def parse_stream(data, offset):
    entries = []
    while True:
        entry, next_offset = parse_entry(data, offset)
        if entry is None:
            break
        entries.append(entry)
        offset = next_offset
        if entry['packet_flags'] & EOS_FLAG:
            break
    return entries, offset


def align4(offset):
    return (offset + 3) & ~3


def is_stream_start(data, offset):
    if offset + HEADER_SIZE > len(data):
        return False
    flags = struct.unpack_from('<I', data, offset)[0]
    data_size = struct.unpack_from('<I', data, offset + 4)[0]
    seq = struct.unpack_from('<Q', data, offset + 24)[0]
    return flags <= 1 and 0 < data_size < 0x10000 and seq == 3


def parse_streamed_wbnk(data):
    filesize = len(data)
    streams = []
    gaps = []
    offset = 0
    while offset < filesize:
        entries, end = parse_stream(data, offset)
        if not entries:
            break
        stream = {
            'index': len(streams), 'start': offset, 'end': end,
            'entries': entries, 'entry_count': len(entries),
        }
        granules = [(e['seq'], e['granule_pos']) for e in entries
                    if e['granule_pos'] != GRANULE_NONE]
        stream['last_granule'] = granules[-1][1] if granules else 0
        stream['granule_count'] = len(granules)
        stream['total_payload_bytes'] = sum(e['data_size'] for e in entries)
        stream['total_bytes'] = end - offset
        seqs = [e['seq'] for e in entries]
        stream['seq_min'] = min(seqs)
        stream['seq_max'] = max(seqs)
        streams.append(stream)
        aligned = align4(end)
        if aligned > end and aligned <= filesize:
            gaps.append({'offset': end, 'size': aligned - end})
        if aligned >= filesize:
            break
        if is_stream_start(data, aligned):
            offset = aligned
        else:
            return {'streams': streams, 'pcm_offset': aligned,
                    'pcm_size': filesize - aligned, 'gaps': gaps}
    return {'streams': streams, 'pcm_offset': None, 'pcm_size': 0, 'gaps': gaps}


def extract_streamed_wbnk(input_path, output_dir, dump=False):
    with open(input_path, 'rb') as f:
        data = f.read()

    os.makedirs(output_dir, exist_ok=True)
    print(f"Parsing {input_path} ({len(data)} bytes)...")
    result = parse_streamed_wbnk(data)
    streams = result['streams']
    total_accounted = 0
    audio_num = 0
    vorbis_count = 0

    for stream in streams:
        entries = stream['entries']
        audio_num += 1

        bin_path = os.path.join(output_dir, f"{audio_num:03d}.vorbis.bin")
        with open(bin_path, 'wb') as f:
            for e in entries:
                f.write(data[e['payload_offset']:e['payload_offset'] + e['data_size']])

        total_accounted += stream['total_bytes']
        vorbis_count += 1

        duration = stream['last_granule'] / 48000 if stream['last_granule'] else 0
        print(f"  {audio_num:03d}.vorbis.bin  {stream['entry_count']} packets, "
              f"~{duration:.1f}s (Vorbis - needs codebooks to decode)")

        if dump:
            label = f"stream_{stream['index'] + 1:03d}"
            with open(os.path.join(output_dir, f"{label}.raw"), 'wb') as f:
                f.write(data[stream['start']:stream['end']])
            meta = {
                'stream_index': stream['index'], 'codec': 'vorbis',
                'offset_start': stream['start'], 'offset_end': stream['end'],
                'entry_count': stream['entry_count'],
                'total_payload_bytes': stream['total_payload_bytes'],
                'seq_range': [stream['seq_min'], stream['seq_max']],
                'last_granule_position': stream['last_granule'],
                'entries': [{
                    'seq': e['seq'], 'data_size': e['data_size'],
                    'granule_pos': e['granule_pos'] if e['granule_pos'] != GRANULE_NONE else None,
                    'is_eos': bool(e['packet_flags'] & EOS_FLAG),
                } for e in entries],
            }
            with open(os.path.join(output_dir, f"{label}.json"), 'w') as f:
                json.dump(meta, f, indent=2)

    for gap in result['gaps']:
        total_accounted += gap['size']

    if result['pcm_offset'] is not None and result['pcm_size'] > 0:
        pcm_data = data[result['pcm_offset']:result['pcm_offset'] + result['pcm_size']]
        audio_num += 1
        wav_path = os.path.join(output_dir, f"{audio_num:03d}.wav")
        with wave.open(wav_path, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(48000)
            wf.writeframes(pcm_data)
        duration = result['pcm_size'] / (2 * 2 * 48000)
        print(f"  {audio_num:03d}.wav         PCM stereo 48kHz, ~{duration:.1f}s")
        total_accounted += result['pcm_size']

        if dump:
            with open(os.path.join(output_dir, "pcm_data.raw"), 'wb') as f:
                f.write(pcm_data)

    if dump:
        file_meta = {
            'source_file': os.path.basename(input_path),
            'file_size': len(data), 'stream_count': len(streams),
            'has_pcm_data': result['pcm_offset'] is not None,
            'pcm_offset': result['pcm_offset'], 'pcm_size': result['pcm_size'],
            'alignment_gaps': [{'offset': g['offset'], 'size': g['size']}
                               for g in result['gaps']],
            'total_bytes_accounted': total_accounted,
            'bytes_match': total_accounted == len(data),
        }
        with open(os.path.join(output_dir, "file_info.json"), 'w') as f:
            json.dump(file_meta, f, indent=2)

    status = "OK" if total_accounted == len(data) else f"WARN: {len(data) - total_accounted} bytes unaccounted"
    print(f"  {audio_num} file(s) extracted ({status})")
    if vorbis_count > 0:
        print(f"  NOTE: {vorbis_count} Vorbis stream(s) need external codebooks to play.")
        print(f"        The codebooks are not in the WBNK file (likely in the game engine).")


# ──────────────────────────────────────────────────────────
# Auto-detection and CLI
# ──────────────────────────────────────────────────────────

def find_companion(wbnk_path, wbnk_data, is_index):
    """Find the companion WBNK in the same directory.

    If is_index=True, find the data file.  If is_index=False, find the index.
    Picks the best match by size proximity.
    """
    directory = os.path.dirname(wbnk_path) or '.'
    my_size = len(wbnk_data)
    candidates = []

    for f in sorted(os.listdir(directory)):
        if not f.upper().endswith('.WBNK'):
            continue
        fp = os.path.join(directory, f)
        if os.path.abspath(fp) == os.path.abspath(wbnk_path):
            continue

        peer_size = os.path.getsize(fp)
        with open(fp, 'rb') as fh:
            peer_hdr = fh.read(min(peer_size, 65536))

        if is_index:
            idx = try_parse_index_wbnk(wbnk_data)
            if idx is None:
                return None
            last = idx['entries'][-1]
            needed = last['offset'] + last['size']
            if try_parse_index_wbnk(peer_hdr) is not None:
                continue  # skip other index files
            if peer_size >= needed:
                candidates.append((fp, abs(peer_size - needed)))
        else:
            peer_idx = try_parse_index_wbnk(peer_hdr)
            if peer_idx is None:
                continue
            last = peer_idx['entries'][-1]
            needed = last['offset'] + last['size']
            if my_size >= needed:
                candidates.append((fp, abs(my_size - needed)))

    if not candidates:
        return None
    candidates.sort(key=lambda x: x[1])
    return candidates[0][0]


def main():
    dump = '--dump' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--dump']

    if len(args) == 2:
        input_path = args[0]
        output_dir = args[1]

        if not os.path.isfile(input_path):
            print(f"Error: File not found: {input_path}")
            sys.exit(1)

        with open(input_path, 'rb') as f:
            data = f.read()

        idx = try_parse_index_wbnk(data)
        if idx is not None:
            # This is an index-only WBNK — no audio to extract
            print(f"Skipping {input_path} (index file, no audio data)")
            return

        # Not an index — check if it's a data file with a nearby index
        index_path = find_companion(input_path, data, is_index=False)
        if index_path is not None:
            print(f"Auto-detected index file: {index_path}")
            extract_indexed_wbnk(index_path, input_path, output_dir, dump=dump)
            return

        # Fallback: treat as self-contained streamed WBNK
        extract_streamed_wbnk(input_path, output_dir, dump=dump)

    elif len(args) == 3:
        index_path = args[0]
        data_path = args[1]
        output_dir = args[2]

        if not os.path.isfile(index_path):
            print(f"Error: File not found: {index_path}")
            sys.exit(1)
        if not os.path.isfile(data_path):
            print(f"Error: File not found: {data_path}")
            sys.exit(1)

        extract_indexed_wbnk(index_path, data_path, output_dir, dump=dump)

    else:
        print(f"Usage: {sys.argv[0]} <input.wbnk> <outputDir> [--dump]")
        print(f"       {sys.argv[0]} <index.wbnk> <data.wbnk> <outputDir> [--dump]")
        sys.exit(1)


if __name__ == '__main__':
    main()
