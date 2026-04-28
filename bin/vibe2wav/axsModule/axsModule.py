#!/usr/bin/env python3
# Vibe coded by Claude

import struct
import sys
import os
import wave
import array
import math
import numpy as np

VALID_CHUNK_IDS = {b'USER', b'SHDR', b'SONG', b'BLOK', b'TRAK', b'INST', b'INNM', b'DNOT', b'SAMP'}
FIXED_CHUNK_SIZES = {
    b'SHDR': 20,
    b'BLOK': 24,
    b'TRAK': 256,
    b'INST': 128,
    b'INNM': 9,
    b'DNOT': 40,
}

OUTPUT_RATE = 44100


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def parse_axs(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()

    if len(data) < 12:
        fail("File too small to be an AXS module")
    if data[0:4] != b'FORM':
        fail(f"Missing FORM header (got {data[0:4]!r})")

    form_size = struct.unpack('>I', data[4:8])[0]
    declared_end = 8 + form_size
    file_size = len(data)
    truncation = declared_end - file_size
    if truncation < 0:
        fail(f"File is larger than FORM declares: file={file_size}, FORM says {declared_end}")
    if truncation > 16:
        fail(f"File is severely truncated: expected {declared_end} bytes, got {file_size}")
    if data[8:12] != b'AXSF':
        fail(f"Not an AXSF file (type is {data[8:12]!r})")

    end = file_size
    offset = 12
    chunks = []

    while offset < end:
        if offset + 8 > end:
            if offset + 8 <= declared_end:
                break
            fail(f"Incomplete chunk header at offset 0x{offset:X}")

        chunk_id = data[offset:offset + 4]
        chunk_size = struct.unpack('>I', data[offset + 4:offset + 8])[0]

        if chunk_id not in VALID_CHUNK_IDS:
            fail(f"Unknown chunk ID {chunk_id!r} at offset 0x{offset:X}")

        available = end - offset - 8
        if chunk_size > available:
            if chunk_id == b'SAMP' and available >= 176:
                chunk_data = data[offset + 8:end]
                chunks.append((chunk_id, chunk_size, chunk_data, offset))
                offset = end
                break
            fail(f"Chunk {chunk_id!r} at 0x{offset:X} claims size {chunk_size} but only {available} bytes remain")

        if chunk_id in FIXED_CHUNK_SIZES and chunk_size != FIXED_CHUNK_SIZES[chunk_id]:
            fail(f"Chunk {chunk_id!r} at 0x{offset:X} has unexpected size {chunk_size} (expected {FIXED_CHUNK_SIZES[chunk_id]})")

        chunk_data = data[offset + 8:offset + 8 + chunk_size]
        chunks.append((chunk_id, chunk_size, chunk_data, offset))
        offset += 8 + chunk_size

    validate_structure(chunks)
    return chunks


def validate_structure(chunks):
    chunk_ids = [c[0] for c in chunks]
    if not chunk_ids:
        fail("No chunks found in file")

    idx = 0
    n = len(chunk_ids)

    if idx >= n or chunk_ids[idx] != b'USER':
        fail("First chunk must be USER")
    idx += 1
    if idx >= n or chunk_ids[idx] != b'SHDR':
        fail("Second chunk must be SHDR")
    idx += 1
    if idx >= n or chunk_ids[idx] != b'SONG':
        fail("Third chunk must be SONG")
    song_size = chunks[idx][1]
    if song_size % 8 != 0:
        fail(f"SONG chunk size {song_size} is not a multiple of 8")
    idx += 1

    blok_count = 0
    while idx < n and chunk_ids[idx] == b'BLOK':
        blok_count += 1
        idx += 1
        for t in range(16):
            if idx >= n or chunk_ids[idx] != b'TRAK':
                fail(f"Expected TRAK #{t + 1} after BLOK #{blok_count}")
            idx += 1
    if blok_count == 0:
        fail("No BLOK chunks found")

    inst_count = 0
    while idx < n and chunk_ids[idx] == b'INST':
        inst_count += 1
        idx += 1
    if inst_count != 8:
        fail(f"Expected exactly 8 INST chunks, found {inst_count}")

    innm_count = 0
    while idx < n and chunk_ids[idx] == b'INNM':
        innm_count += 1
        idx += 1
    if innm_count != 8:
        fail(f"Expected exactly 8 INNM chunks, found {innm_count}")

    while idx < n and chunk_ids[idx] == b'DNOT':
        idx += 1

    while idx < n and chunk_ids[idx] == b'SAMP':
        samp_data = chunks[idx][2]
        actual_data_len = len(samp_data)
        declared_size = chunks[idx][1]
        if actual_data_len < 176:
            fail(f"SAMP chunk too small ({actual_data_len} < 176)")
        sample_count = struct.unpack('<I', samp_data[164:168])[0]
        expected_size = 176 + sample_count * 2
        if declared_size != expected_size:
            fail(f"SAMP chunk size mismatch: declared {declared_size}, expected {expected_size}")
        idx += 1

    if idx != n:
        fail(f"Unexpected chunk {chunk_ids[idx]!r} at index {idx}")


def build_module(chunks):
    chunks_by_type = {}
    for cid, csz, cd, off in chunks:
        chunks_by_type.setdefault(cid, []).append(cd)

    shdr = chunks_by_type[b'SHDR'][0]
    bpm = shdr[2]
    speed = shdr[3]
    if bpm == 0:
        bpm = 125
    if speed == 0:
        speed = 6

    song_data = chunks_by_type[b'SONG'][0]
    song_entries = []
    for i in range(0, len(song_data), 8):
        block_idx = struct.unpack('<I', song_data[i:i + 4])[0]
        mute_mask = struct.unpack('<H', song_data[i + 4:i + 6])[0]
        song_entries.append((block_idx, mute_mask))

    bloks = chunks_by_type[b'BLOK']
    traks = chunks_by_type[b'TRAK']
    blocks = []
    for bi, bd in enumerate(bloks):
        track_bytes = list(bd[8:24])
        track_data = []
        for ti in range(16):
            td = traks[bi * 16 + ti]
            steps = []
            for s in range(64):
                steps.append(td[s * 4:(s + 1) * 4])
            track_data.append(steps)
        blocks.append((track_bytes, track_data))

    dnots = chunks_by_type.get(b'DNOT', [])
    dnot_by_key = {}
    for dd in dnots:
        fields = struct.unpack('<10I', dd)
        key = fields[0]
        base_note = fields[1]
        velocity = fields[3]
        sample_slot = fields[6]
        dnot_by_key[key] = {
            'base_note': base_note,
            'velocity': velocity,
            'sample_slot': sample_slot,
        }

    samps = chunks_by_type.get(b'SAMP', [])
    sample_by_slot = {}
    for sd in samps:
        slot = sd[0]
        count = struct.unpack('<I', sd[164:168])[0]
        rate = struct.unpack('<I', sd[168:172])[0]
        audio = sd[176:]
        available = len(audio)
        available -= available % 2
        audio = audio[:available]
        actual_count = available // 2
        if actual_count > 0 and rate > 0:
            samples_arr = struct.unpack(f'<{actual_count}h', audio)
            sample_by_slot[slot] = {
                'rate': rate,
                'count': actual_count,
                'data': samples_arr,
            }

    return {
        'bpm': bpm,
        'speed': speed,
        'song': song_entries,
        'blocks': blocks,
        'dnot_by_key': dnot_by_key,
        'sample_by_slot': sample_by_slot,
    }


def render_song(module):
    bpm = module['bpm']
    speed = module['speed']
    song = module['song']
    blocks = module['blocks']
    dnot_by_key = module['dnot_by_key']
    sample_by_slot = module['sample_by_slot']

    samples_per_row = int(OUTPUT_RATE * speed * 5 / (bpm * 2))

    np_samples = {}
    for slot, info in sample_by_slot.items():
        np_samples[slot] = np.array(info['data'], dtype=np.float64) / 32768.0

    channels = []
    for _ in range(16):
        channels.append({
            'slot': -1,
            'pos': 0.0,
            'step': 0.0,
            'volume': 0.5,
            'active': False,
        })

    total_rows = len(song) * 64
    output = np.zeros(total_rows * samples_per_row, dtype=np.float64)
    out_idx = 0

    for song_idx, (block_idx, mute_mask) in enumerate(song):
        if block_idx >= len(blocks):
            out_idx += 64 * samples_per_row
            continue

        track_bytes, track_data = blocks[block_idx]

        for row in range(64):
            for ti in range(16):
                ch = channels[ti]
                step = track_data[ti][row]
                note = step[0]
                vol = step[1]
                fx = step[2]
                param = step[3]

                blok_byte = track_bytes[ti]
                is_sampler = (blok_byte & 0x0F) == 7
                inst_idx = blok_byte & 0x0F

                if note == 0x81:
                    ch['active'] = False
                    continue

                if note > 0:
                    slot = -1
                    pitch_step = 0.0
                    dnot_key = -1

                    if is_sampler:
                        dnot_key = note - 1
                        if dnot_key in dnot_by_key:
                            dnot = dnot_by_key[dnot_key]
                            slot = dnot['sample_slot']
                            if slot in sample_by_slot:
                                pitch_step = sample_by_slot[slot]['rate'] / OUTPUT_RATE
                    else:
                        if inst_idx in dnot_by_key:
                            dnot = dnot_by_key[inst_idx]
                            slot = dnot['sample_slot']
                            base_note = dnot['base_note']
                            if slot in sample_by_slot:
                                semitones = note - base_note
                                pitch_ratio = 2.0 ** (semitones / 12.0)
                                pitch_step = sample_by_slot[slot]['rate'] * pitch_ratio / OUTPUT_RATE

                    if slot in np_samples and pitch_step > 0:
                        start_pos = 0.0
                        if fx == 0x09 and param > 0:
                            start_pos = float(param * 256)
                            if start_pos >= len(np_samples[slot]):
                                start_pos = 0.0

                        ch['slot'] = slot
                        ch['pos'] = start_pos
                        ch['step'] = pitch_step
                        ch['active'] = True

                        if vol > 0:
                            ch['volume'] = vol / 127.0
                        elif is_sampler and dnot_key in dnot_by_key:
                            ch['volume'] = dnot_by_key[dnot_key]['velocity'] / 127.0
                        elif not is_sampler and inst_idx in dnot_by_key:
                            ch['volume'] = dnot_by_key[inst_idx]['velocity'] / 127.0
                        else:
                            ch['volume'] = 0.7
                elif vol > 0 and ch['active']:
                    ch['volume'] = vol / 127.0

            for ti in range(16):
                if not (mute_mask & (1 << ti)):
                    continue
                ch = channels[ti]
                if not ch['active'] or ch['slot'] not in np_samples:
                    continue

                sdata = np_samples[ch['slot']]
                slen = len(sdata)
                pos = ch['pos']
                stp = ch['step']
                cvol = ch['volume']

                indices = pos + np.arange(samples_per_row, dtype=np.float64) * stp
                valid = indices < slen
                n_valid = np.searchsorted(indices >= slen, True)
                if n_valid == 0:
                    ch['active'] = False
                    continue

                idx = indices[:n_valid]
                ipos = idx.astype(np.intp)
                frac = idx - ipos
                np.clip(ipos, 0, slen - 1, out=ipos)
                ipos1 = np.minimum(ipos + 1, slen - 1)
                interp = sdata[ipos] + (sdata[ipos1] - sdata[ipos]) * frac
                output[out_idx:out_idx + n_valid] += interp * cvol

                ch['pos'] = pos + samples_per_row * stp
                if ch['pos'] >= slen:
                    ch['active'] = False

            out_idx += samples_per_row

    return output[:out_idx]


def normalize_and_write_wav(filepath, float_samples):
    if len(float_samples) == 0:
        fail("No audio rendered")

    peak = np.max(np.abs(float_samples))
    if peak < 0.001:
        fail("Rendered audio is silent")

    scale = 0.9 / peak
    int_samples = np.clip(float_samples * scale * 32767, -32768, 32767).astype(np.int16)

    with wave.open(filepath, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(OUTPUT_RATE)
        w.writeframes(int_samples.tobytes())


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        fail(f"Input file not found: {input_file}")

    chunks = parse_axs(input_file)
    module = build_module(chunks)

    if not module['sample_by_slot']:
        fail("No audio samples found in file")

    os.makedirs(output_dir, exist_ok=True)

    basename = os.path.splitext(os.path.basename(input_file))[0]
    wav_path = os.path.join(output_dir, f"{basename}.wav")

    print(f"  Rendering: BPM={module['bpm']}, speed={module['speed']}, "
          f"blocks={len(module['blocks'])}, song_len={len(module['song'])}, "
          f"samples={len(module['sample_by_slot'])}")

    float_audio = render_song(module)

    duration = len(float_audio) / OUTPUT_RATE
    print(f"  Duration: {duration:.1f}s ({len(float_audio)} samples)")

    normalize_and_write_wav(wav_path, float_audio)
    print(f"  Wrote: {wav_path}")


if __name__ == '__main__':
    main()
