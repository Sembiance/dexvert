# Vibe coded by Claude
"""Convert raw XNB-extracted Texture2D files to PNG.

Supports SurfaceFormat.Color (RGBA), DXT1, DXT3, and DXT5 compressed textures.
Auto-detects format and dimensions when possible.

Usage:
    python texture2d2png.py <input.Texture2D> <output.png>
    python texture2d2png.py <input.Texture2D> <output.png> --width 512 --height 512
    python texture2d2png.py <input.Texture2D> <output.png> --format dxt5
"""

import argparse
import math
import struct
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# DXT decoding
# ---------------------------------------------------------------------------

def decode_rgb565(c):
    r = ((c >> 11) & 0x1F) * 255 // 31
    g = ((c >> 5) & 0x3F) * 255 // 63
    b = (c & 0x1F) * 255 // 31
    return r, g, b


def _decode_color_block(data, offset):
    """Decode a 4-byte color endpoint pair + 4-byte index block (shared by DXT1/3/5)."""
    c0, c1 = struct.unpack_from("<HH", data, offset)
    indices = struct.unpack_from("<I", data, offset + 4)[0]
    r0, g0, b0 = decode_rgb565(c0)
    r1, g1, b1 = decode_rgb565(c1)
    colors = [(r0, g0, b0), (r1, g1, b1)]
    if c0 > c1:
        colors.append(((2 * r0 + r1 + 1) // 3, (2 * g0 + g1 + 1) // 3, (2 * b0 + b1 + 1) // 3))
        colors.append(((r0 + 2 * r1 + 1) // 3, (g0 + 2 * g1 + 1) // 3, (b0 + 2 * b1 + 1) // 3))
    else:
        colors.append(((r0 + r1) // 2, (g0 + g1) // 2, (b0 + b1) // 2))
        colors.append((0, 0, 0))  # transparent black for DXT1
    rgb = [None] * 16
    for i in range(16):
        rgb[i] = colors[(indices >> (2 * i)) & 3]
    return rgb, c0 <= c1  # return has_transparent flag for DXT1


def decode_dxt1(data, width, height):
    pixels = bytearray(width * height * 4)
    bw = (width + 3) // 4
    bh = (height + 3) // 4
    off = 0
    for by in range(bh):
        for bx in range(bw):
            if off + 8 > len(data):
                break
            rgb, has_trans = _decode_color_block(data, off)
            off += 8
            for i in range(16):
                px, py = i % 4, i // 4
                x, y = bx * 4 + px, by * 4 + py
                if x < width and y < height:
                    r, g, b = rgb[i]
                    a = 0 if (has_trans and rgb[i] == (0, 0, 0) and ((struct.unpack_from("<I", data, off - 4)[0] >> (2 * i)) & 3) == 3) else 255
                    p = (y * width + x) * 4
                    pixels[p:p + 4] = bytes([r, g, b, a])
    return bytes(pixels)


def decode_dxt3(data, width, height):
    pixels = bytearray(width * height * 4)
    bw = (width + 3) // 4
    bh = (height + 3) // 4
    off = 0
    for by in range(bh):
        for bx in range(bw):
            if off + 16 > len(data):
                break
            # 8 bytes explicit alpha (4 bits per pixel, 16 pixels)
            alpha_data = struct.unpack_from("<Q", data, off)[0]
            rgb, _ = _decode_color_block(data, off + 8)
            off += 16
            for i in range(16):
                px, py = i % 4, i // 4
                x, y = bx * 4 + px, by * 4 + py
                if x < width and y < height:
                    r, g, b = rgb[i]
                    a4 = (alpha_data >> (4 * i)) & 0xF
                    a = a4 | (a4 << 4)
                    p = (y * width + x) * 4
                    pixels[p:p + 4] = bytes([r, g, b, a])
    return bytes(pixels)


def decode_dxt5(data, width, height):
    pixels = bytearray(width * height * 4)
    bw = (width + 3) // 4
    bh = (height + 3) // 4
    off = 0
    for by in range(bh):
        for bx in range(bw):
            if off + 16 > len(data):
                break
            # 2 bytes alpha endpoints + 6 bytes (48 bits) of 3-bit indices
            a0 = data[off]
            a1 = data[off + 1]
            # Build alpha lookup table
            alphas = [a0, a1]
            if a0 > a1:
                for j in range(1, 7):
                    alphas.append(((7 - j) * a0 + j * a1 + 3) // 7)
            else:
                for j in range(1, 5):
                    alphas.append(((5 - j) * a0 + j * a1 + 2) // 5)
                alphas.append(0)
                alphas.append(255)
            # Read 48-bit alpha index block
            ab = struct.unpack_from("<Q", data, off)[0] >> 16  # skip first 2 bytes
            # Color block
            rgb, _ = _decode_color_block(data, off + 8)
            off += 16
            for i in range(16):
                px, py = i % 4, i // 4
                x, y = bx * 4 + px, by * 4 + py
                if x < width and y < height:
                    r, g, b = rgb[i]
                    aidx = (ab >> (3 * i)) & 7
                    a = alphas[aidx]
                    p = (y * width + x) * 4
                    pixels[p:p + 4] = bytes([r, g, b, a])
    return bytes(pixels)


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------

def _dxt5_block_structure_score(data, size):
    """Check if byte-position means within 16-byte blocks indicate DXT5 structure.

    In DXT5, position 11 mod 16 is a color endpoint byte (RGB565 high byte)
    which has a very different mean from positions 3 and 7 (alpha index bytes).
    In RGBA, positions 3, 7, 11, 15 are all the alpha channel and have nearly
    identical means.  A large deviation at position 11 is strong DXT5 evidence.
    """
    sample_size = min(size, 160000)
    start = max(0, (size - sample_size) // 2) & ~15
    sample = data[start:start + sample_size]

    sums = [0.0] * 16
    counts = [0] * 16
    for i in range(len(sample)):
        pos = i % 16
        sums[pos] += sample[i]
        counts[pos] += 1

    means = [s / c if c else 0 for s, c in zip(sums, counts)]

    avg_37 = (means[3] + means[7]) / 2.0
    dev_11 = abs(avg_37 - means[11])

    # The deviation must be both absolutely > 2 and relatively > 20% of the
    # alpha-index mean to avoid false positives on nearly-uniform images.
    threshold = max(2.0, avg_37 * 0.2)
    return dev_11 > threshold


def _dxt5_decode_test(data, size, smoothness=1.0):
    """Check if data is DXT5 by block structure analysis and decode comparison.

    Uses a two-stage approach:
    1. Fast path: byte-position mean analysis (_dxt5_block_structure_score)
    2. Slow path: decode a test region as DXT5 and compare row similarity
       against raw RGBA interpretation. Only for large, non-smooth files
       to avoid false positives on smooth RGBA images.
    """
    # Fast path: byte-position mean deviation reliably catches most DXT5
    if _dxt5_block_structure_score(data, size):
        return True

    # Small files produce unreliable decode statistics
    if size < 100000:
        return False

    # Smooth data (smoothness >= 0.7) produces false positives because
    # smooth byte patterns decode into coherent-looking DXT5 blocks
    if smoothness >= 0.7:
        return False

    # Full decode test: compare DXT5-decoded row similarity vs raw RGBA
    total_blocks = size // 16
    cands = _find_dim_candidates(total_blocks, 4)
    if not cands:
        return False

    # Try top 3 DXT5 dimension candidates
    best_dxt5_sim = 0
    best_dxt5_w = 0
    for dxt5_w, dxt5_h, _ in cands[:3]:
        block_w = dxt5_w // 4
        block_h = dxt5_h // 4
        test_bh = min(block_h, 16)
        test_h = test_bh * 4
        test_bytes = block_w * test_bh * 16
        if test_bytes > size or test_bytes < 64:
            continue
        try:
            decoded = decode_dxt5(data[:test_bytes], dxt5_w, test_h)
            sim = _quick_row_similarity(decoded, dxt5_w, dxt5_w * test_h)
            if sim > best_dxt5_sim:
                best_dxt5_sim = sim
                best_dxt5_w = dxt5_w
        except Exception:
            continue

    if best_dxt5_w == 0:
        return False

    # Find best RGBA row similarity at candidate widths
    rgba_pixels = size // 4
    rgba_cands = _find_dim_candidates(rgba_pixels, 1)
    best_rgba_sim = 0
    tested = set()
    for pw, ph, _ in rgba_cands[:5]:
        for w in (pw, ph):
            if w in tested or w < 8 or w > 4096:
                continue
            if rgba_pixels % w != 0:
                continue
            h = rgba_pixels // w
            if h > 4096:
                continue
            tested.add(w)
            test_px = min(rgba_pixels, best_dxt5_w * 64)
            sim = _quick_row_similarity(data, w, test_px)
            if sim > best_rgba_sim:
                best_rgba_sim = sim

    # Require clear DXT5 advantage to avoid false positives
    return best_dxt5_sim > best_rgba_sim + 0.1


def detect_format(data):
    """Detect pixel format: rgba, dxt1, dxt3, or dxt5."""
    size = len(data)

    # Check alpha channel consistency (every 4th byte if RGBA)
    # Sample from multiple positions across the file
    alpha_00ff_count = 0
    alpha_total = 0
    alpha_values = []
    for frac in (0.0, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9):
        start = int(size * frac) & ~3
        chunk = data[start:start + 4000]
        for i in range(3, len(chunk), 4):
            alpha_values.append(chunk[i])
            if chunk[i] == 0xFF or chunk[i] == 0x00:
                alpha_00ff_count += 1
            alpha_total += 1

    alpha_ratio = alpha_00ff_count / alpha_total if alpha_total else 0

    # Count unique alpha values - RGBA tends to have few (mostly 0x00 and 0xFF)
    # DXT data has many distinct "alpha" byte values
    alpha_unique = len(set(alpha_values))

    # Not divisible by 8 = can't be DXT
    if size % 8 != 0:
        return "rgba"

    # Strong RGBA signal: high alpha consistency AND few unique alpha values
    if alpha_ratio > 0.92 and alpha_unique < 30:
        return "rgba"

    # Compute smoothness early - used for multiple checks below
    # In RGBA, adjacent pixels tend to be similar (smooth images)
    # In DXT data read as RGBA, adjacent "pixels" are unrelated
    smooth_count = 0
    smooth_total = 0
    for frac in (0.1, 0.3, 0.5, 0.7, 0.9):
        start = int(size * frac) & ~3
        chunk = data[start:start + 4000]
        for i in range(0, len(chunk) - 8, 4):
            p1 = chunk[i:i + 4]
            p2 = chunk[i + 4:i + 8]
            diff = sum(abs(a - b) for a, b in zip(p1, p2))
            if diff < 40:
                smooth_count += 1
            smooth_total += 1

    smoothness = smooth_count / smooth_total if smooth_total else 0

    # Strong DXT signal: very low alpha consistency
    if alpha_ratio < 0.15:
        if smoothness > 0.7:
            # Ambiguous: could be RGBA with low/gradient alpha, or DXT with uniform blocks.
            # Very high smoothness (>= 0.95) strongly indicates real RGBA pixel data
            # (gradient alpha), not DXT block data. Require much stronger DXT5 signal.
            ep_score = _dxt5_alpha_endpoint_score(data)
            if smoothness >= 0.95:
                if ep_score > 0.8:
                    return _classify_dxt(data, size)
                return "rgba"
            if ep_score > 0.5:
                return _classify_dxt(data, size)
            return "rgba"
        return _classify_dxt(data, size)

    # DXT5 decode validation for ambiguous cases.
    # DXT5 textures with mostly-opaque content have moderate alpha_ratio (0.5-0.95)
    # because alpha index bytes are often 0x00 when read as RGBA. They also have
    # many unique "alpha" values (>30) from color data at non-alpha byte positions,
    # and moderate smoothness because adjacent DXT5 block bytes are correlated.
    # The definitive test: decode a small region as DXT5 and compare row similarity
    # of the decoded output vs the raw RGBA interpretation.
    if size % 16 == 0 and size >= 1024 and alpha_unique > 30 and smoothness < 0.95:
        if _dxt5_decode_test(data, size, smoothness):
            return _classify_dxt(data, size)

    # High smoothness = real image pixels, not compressed blocks
    if smoothness > 0.7:
        return "rgba"

    # Medium-low alpha ratio with many unique values = likely DXT
    # BUT: smooth pixel data with gradient alpha also has many unique alpha values
    if alpha_ratio < 0.50 and alpha_unique > 80 and smoothness < 0.4:
        return _classify_dxt(data, size)

    # Moderate smoothness = real image pixels, not compressed blocks
    if smoothness > 0.4:
        return "rgba"

    # Also compare dimension quality: does this size give better dims as RGBA or DXT?
    rgba_pixels = size // 4
    rgba_dim_score = _squareness_score(rgba_pixels)
    dxt5_blocks = size // 16 if size % 16 == 0 else 0
    dxt5_dim_score = _squareness_score(dxt5_blocks) if dxt5_blocks else 0
    dxt1_blocks = size // 8
    dxt1_dim_score = _squareness_score(dxt1_blocks)

    # If RGBA gives much squarer dims than DXT, prefer RGBA
    if rgba_dim_score >= max(dxt5_dim_score, dxt1_dim_score) + 20:
        return "rgba"

    return _classify_dxt(data, size)


def _classify_dxt(data, size):
    """Determine if data is DXT1, DXT3, or DXT5."""
    can_dxt1 = size % 8 == 0
    can_dxt5 = size % 16 == 0

    if can_dxt5 and can_dxt1:
        # Strong signal: if 16-byte block structure analysis indicates DXT5,
        # prefer DXT5 regardless of squareness (byte statistics are more
        # reliable than dimension aesthetics).
        if _dxt5_block_structure_score(data, size):
            return _dxt3_or_dxt5(data)

        # Both possible - check which gives better (squarer) dimensions
        dxt1_blocks = size // 8
        dxt5_blocks = size // 16
        dxt1_score = _squareness_score(dxt1_blocks)
        dxt5_score = _squareness_score(dxt5_blocks)

        # Also use alpha endpoint heuristic: in DXT5, bytes 0,1 of each
        # 16-byte block are alpha endpoints (valid 0-255 each).
        # If we treat data as DXT5 and the alpha endpoints look
        # plausible (not too wild) across many blocks, favor DXT5.
        alpha_ep_score = _dxt5_alpha_endpoint_score(data)

        if dxt5_score > dxt1_score + 10:
            return _dxt3_or_dxt5(data)
        elif dxt1_score > dxt5_score + 10:
            return "dxt1"
        elif alpha_ep_score > 0.5:
            # Alpha endpoints look like DXT5 data
            return _dxt3_or_dxt5(data)
        elif dxt5_score >= dxt1_score:
            return _dxt3_or_dxt5(data) if size >= 16384 else "dxt1"
        else:
            return "dxt1"
    elif can_dxt5:
        return _dxt3_or_dxt5(data)
    elif can_dxt1:
        return "dxt1"
    else:
        return "rgba"


def _dxt5_alpha_endpoint_score(data):
    """Score how likely the data is DXT5 by examining alpha endpoint bytes.

    In DXT5, each 16-byte block starts with 2 alpha endpoint bytes.
    Valid DXT5 data tends to have a0 >= a1 in many blocks (the more
    common interpolation mode), and the endpoints should show some
    variety but not be completely random.
    """
    size = len(data)
    if size < 16:
        return 0

    a0_ge_a1 = 0
    total = 0
    endpoint_pairs = set()
    for off in range(0, min(size, 16 * 500), 16):
        a0 = data[off]
        a1 = data[off + 1]
        if a0 >= a1:
            a0_ge_a1 += 1
        total += 1
        endpoint_pairs.add((a0, a1))

    if total == 0:
        return 0

    # In real DXT5, a0 >= a1 is common (8-value interpolation mode)
    # In random/DXT1 data interpreted as 16-byte blocks, it's ~50%
    ge_ratio = a0_ge_a1 / total

    # Also check endpoint variety - real alpha endpoints aren't all identical
    # but also aren't completely random
    variety = len(endpoint_pairs) / total

    # Score: high if a0>=a1 is dominant and variety is moderate
    score = 0
    if ge_ratio > 0.6:
        score += 0.4
    if 0.05 < variety < 0.8:
        score += 0.3
    if ge_ratio > 0.75:
        score += 0.3

    return score


def _dxt3_or_dxt5(data):
    """Distinguish DXT3 from DXT5 by examining alpha block structure."""
    # DXT3: alpha is explicit 4-bit per pixel - values 0x00-0xFF in each nibble
    # DXT5: first 2 bytes are alpha endpoints, next 6 bytes are 3-bit indices
    # In DXT5, the first byte of each block tends to be >= second byte or have specific patterns
    # In practice, DXT5 is far more common than DXT3, so default to DXT5
    return "dxt5"


def _squareness_score(block_count):
    """Score how close to square the best dimension factorization is. Higher = squarer."""
    if block_count == 0:
        return 0
    sq = int(math.sqrt(block_count))
    if sq * sq == block_count:
        return 100  # perfect square
    # Find closest factorization
    best = 0
    for w in range(sq, 0, -1):
        if block_count % w == 0:
            h = block_count // w
            ratio = min(w, h) / max(w, h)
            best = max(best, ratio * 100)
            break
    return best


# ---------------------------------------------------------------------------
# Dimension detection
# ---------------------------------------------------------------------------

def _find_dim_candidates(count, block_size):
    """Find dimension candidates for a given block/pixel count, sorted by score descending."""
    if count == 0:
        return []

    candidates = []
    for w in range(1, count + 1):
        if w * w > count * 16:  # max 16:1 aspect ratio
            break
        if count % w == 0:
            h = count // w
            pw, ph = w * block_size, h * block_size
            if pw > 4096 or ph > 4096:
                continue
            ratio = max(pw, ph) / max(min(pw, ph), 1)
            # Bonus for power-of-2 dimensions
            p2_bonus = 0
            if pw & (pw - 1) == 0 and pw > 0:
                p2_bonus += 10
            if ph & (ph - 1) == 0 and ph > 0:
                p2_bonus += 10
            # Bonus for square
            sq_bonus = 50 if pw == ph else 0
            score = 100 - ratio + p2_bonus + sq_bonus
            candidates.append((pw, ph, score))

    candidates.sort(key=lambda x: -x[2])
    return candidates


def _find_best_dims(count, block_size):
    """Find the best dimensions for a given block/pixel count, preferring squarish + power-of-2."""
    candidates = _find_dim_candidates(count, block_size)
    if not candidates:
        return None, None
    return candidates[0][0], candidates[0][1]


def _quick_row_similarity(data, width, total_pixels, frac=None):
    """Quick check of row-to-row similarity at a given width.

    Samples rows from a specific fractional position in the data.
    Default (frac=None) uses 1/3 position for backward compatibility.
    """
    stride = width * 4
    height = total_pixels // width
    if height < 2:
        return 0
    if frac is None:
        start = len(data) // 3
    else:
        start = int(len(data) * frac)
    start = start - (start % stride)  # align to row boundary
    end = min(len(data), start + stride * 12)
    section = data[start:end]
    rows = len(section) // stride - 1
    if rows < 2:
        return 0
    total = 0
    for r in range(min(rows, 8)):
        off = r * stride
        r1 = section[off:off + stride]
        r2 = section[off + stride:off + stride * 2]
        total += sum(1 for a, b in zip(r1, r2) if abs(a - b) < 10) / stride
    return total / min(rows, 8)


def detect_dimensions_rgba(data):
    """Auto-detect width and height for RGBA data."""
    total_pixels = len(data) // 4
    if total_pixels == 0:
        return None, None

    # Try autocorrelation first (most reliable when data has variation)
    ac_result = _autocorrelate_rgba(data, total_pixels)

    # For large images, check if the AC picked a harmonic/sub-harmonic of the
    # true width. This happens when the image has internal repetition (e.g.,
    # tiled sprites) causing the AC to lock onto a multiple or fraction of
    # the real width. If a near-square candidate exists at a harmonic, prefer it.
    if ac_result and total_pixels >= 100000:
        ac_w, ac_h = ac_result
        ac_ratio = max(ac_w, ac_h) / max(min(ac_w, ac_h), 1)
        if ac_ratio > 2.5:
            ac_sim = _quick_row_similarity(data, ac_w, total_pixels)
            orig_ac_result = ac_result
            for mult in (2, 3, 4, 0.5, 1 / 3, 0.25):
                cand_w = int(ac_w * mult)
                if cand_w < 8 or cand_w > 4096:
                    continue
                if total_pixels % cand_w != 0:
                    continue
                cand_h = total_pixels // cand_w
                if cand_h > 4096:
                    continue
                cand_ratio = max(cand_w, cand_h) / max(min(cand_w, cand_h), 1)
                if cand_ratio < 1.5:
                    sim = _quick_row_similarity(data, cand_w, total_pixels)
                    # For sub-harmonics (mult < 1), require sim reasonably
                    # close to AC sim.  Sub-harmonics can appear to have
                    # high sim due to row splitting, so require >= AC - 0.05.
                    if mult < 1 and sim < ac_sim - 0.05:
                        continue
                    if sim >= 0.3:
                        ac_result = (cand_w, cand_h)
                        break

            # Post-harmonic verification: if the harmonic check accepted a
            # sub-harmonic (narrower width), verify it with a second sampling
            # position.  False sub-harmonics from row splitting show high sim
            # in uniform regions but fail in content-rich regions.  Pow2
            # squares (1024x1024, 512x512) bypass this check as they are
            # very likely correct for game textures.
            if ac_result != orig_ac_result:
                new_w, new_h = ac_result
                old_w = orig_ac_result[0]
                if new_w < old_w:  # sub-harmonic was accepted
                    is_pow2_sq = (new_w == new_h
                                  and new_w & (new_w - 1) == 0)
                    if not is_pow2_sq:
                        sim2_new = _quick_row_similarity(
                            data, new_w, total_pixels, frac=0.6)
                        sim2_old = _quick_row_similarity(
                            data, old_w, total_pixels, frac=0.6)
                        avg_new = (sim + sim2_new) / 2
                        avg_old = (ac_sim + sim2_old) / 2
                        if avg_new < avg_old:
                            ac_result = orig_ac_result

        # If AC still has very high ratio after harmonic check, verify against
        # heuristic candidates. The AC may have locked onto a spurious stride
        # (super-harmonic of true width) especially for smooth images where
        # wider rows always show higher or equal similarity.
        ac_w, ac_h = ac_result
        ac_ratio = max(ac_w, ac_h) / max(min(ac_w, ac_h), 1)
        if ac_ratio > 5:
            ac_sim = _quick_row_similarity(data, ac_w, total_pixels)
            candidates = _find_dim_candidates(total_pixels, 1)
            best_alt_w, best_alt_h, best_alt_score, best_alt_sim = None, None, 0, 0
            tested = set()
            for pw, ph, _ in candidates[:10]:
                for tw, th in [(pw, ph), (ph, pw)]:
                    if tw in tested or tw == ac_w:
                        continue
                    tested.add(tw)
                    cand_ratio = max(tw, th) / max(min(tw, th), 1)
                    if cand_ratio >= ac_ratio:
                        continue
                    sim = _quick_row_similarity(data, tw, total_pixels)
                    # Weight selection by squareness: elongated alternatives
                    # get a penalty so squarer dims win when sims are close
                    sq_factor = min(1.0, 1.5 / max(cand_ratio, 1))
                    score = sim * (0.7 + 0.3 * sq_factor)
                    if score > best_alt_score:
                        best_alt_score = score
                        best_alt_sim = sim
                        best_alt_w, best_alt_h = tw, th
            if best_alt_w:
                alt_ratio = max(best_alt_w, best_alt_h) / max(min(best_alt_w, best_alt_h), 1)
                if best_alt_sim > ac_sim:
                    # Alt has strictly better similarity → override
                    ac_result = (best_alt_w, best_alt_h)
                elif best_alt_sim >= ac_sim and ac_sim < 0.999:
                    # Equal sim (not at ceiling) → squareness wins
                    ac_result = (best_alt_w, best_alt_h)
                elif (best_alt_w == best_alt_h
                      and best_alt_w & (best_alt_w - 1) == 0
                      and best_alt_sim > 0.7):
                    # Perfect pow2 square with decent sim → very likely
                    # correct even when sims are at ceiling
                    ac_result = (best_alt_w, best_alt_h)
                elif (ac_ratio > 10 and alt_ratio < 2
                      and best_alt_sim >= ac_sim * 0.95):
                    # Very elongated AC with near-square alt and close sim
                    ac_result = (best_alt_w, best_alt_h)

    # For small images where AC picked a high-ratio result, verify against
    # heuristic candidates. AC is unreliable for small/smooth images where
    # many widths produce similar correlation scores (sub-harmonic effect).
    if ac_result and total_pixels < 8000:
        ac_w, ac_h = ac_result
        ac_ratio = max(ac_w, ac_h) / max(min(ac_w, ac_h), 1)
        if ac_ratio > 3:
            # Check if heuristic candidates have better row similarity
            candidates = _find_dim_candidates(total_pixels, 1)
            for pw, ph, _ in candidates[:8]:
                for tw, th in [(pw, ph), (ph, pw)]:
                    ratio = max(tw, th) / max(min(tw, th), 1)
                    if ratio >= ac_ratio:
                        continue  # skip if not squarer
                    sim = _quick_row_similarity(data, tw, total_pixels)
                    stride = tw * 4
                    damping = min(1.0, stride / 200)
                    sim *= damping
                    if sim >= 0.75 and ratio < 2:
                        ac_result = (tw, th)
                        ac_ratio = ratio
                        break
                else:
                    continue
                break

    if ac_result:
        return ac_result

    # Fallback: heuristic dimension selection
    candidates = _find_dim_candidates(total_pixels, 1)
    if not candidates:
        return None, None

    w, h = candidates[0][0], candidates[0][1]

    # For medium+ images, verify heuristic by checking row similarity
    # across top candidates (both orientations). This catches cases where
    # the heuristic's pow2/squareness bias picks the wrong factorization.
    if total_pixels >= 5000:
        heur_sim = _quick_row_similarity(data, w, total_pixels)

        best_sim_w, best_sim_h, best_sim_score, best_sim = None, None, 0, 0
        tested = set()
        for pw, ph, _ in candidates[:10]:
            for tw, th in [(pw, ph), (ph, pw)]:
                if tw in tested:
                    continue
                tested.add(tw)
                sim = _quick_row_similarity(data, tw, total_pixels)
                # Apply stride damping (same as autocorrelation) to prevent
                # narrow sub-harmonic widths from getting inflated scores
                stride = tw * 4
                damping = min(1.0, stride / 200)
                sim *= damping
                # Weight by squareness to avoid sub-harmonic fragments
                # winning over correct dims when sims are close
                cand_ratio = max(tw, th) / max(min(tw, th), 1)
                sq_factor = min(1.0, 1.5 / max(cand_ratio, 1))
                score = sim * (0.7 + 0.3 * sq_factor)
                if score > best_sim_score:
                    best_sim_score = score
                    best_sim = sim
                    best_sim_w, best_sim_h = tw, th

        # Override heuristic only when confidence is clear.
        # Same-pair orientation flips are handled by tie-breaking below.
        if best_sim_w is not None and best_sim > heur_sim:
            same_pair = sorted([best_sim_w, best_sim_h]) == sorted([w, h])
            if not same_pair:
                if heur_sim >= 0.7 and best_sim > heur_sim:
                    # Row correlation works at heuristic width; a different
                    # width with even better correlation is likely correct.
                    return best_sim_w, best_sim_h
                elif heur_sim < 0.5 and best_sim >= 0.75:
                    # Heuristic width shows poor correlation; a candidate
                    # with strong correlation likely has the real width.
                    return best_sim_w, best_sim_h
                elif 0.5 <= heur_sim < 0.7 and best_sim - heur_sim > 0.1:
                    # Medium zone: override with moderate margin when
                    # the alt width is not a harmonic (2x/3x) of the heuristic
                    # width (which would be an artifact of super-harmonic sim).
                    harmonic = False
                    for m in (2, 3, 4):
                        if best_sim_w == w * m or w == best_sim_w * m:
                            harmonic = True
                            break
                    if not harmonic:
                        return best_sim_w, best_sim_h
                    elif best_sim - heur_sim > 0.15:
                        # Even for harmonics, a very large sim gap means
                        # the wider width is the true width and the
                        # heuristic picked an incorrect sub-harmonic
                        return best_sim_w, best_sim_h

        # Exact tie between orientations - use row similarity to break it
        if len(candidates) >= 2 and w != h:
            c1_w, c1_h, c1_s = candidates[0]
            c2_w, c2_h, c2_s = candidates[1]
            if (c1_s == c2_s and
                    sorted([c1_w, c1_h]) == sorted([c2_w, c2_h])):
                sim_wh = _quick_row_similarity(data, c1_w, total_pixels)
                sim_hw = _quick_row_similarity(data, c1_h, total_pixels)
                if sim_hw > sim_wh + 0.01:
                    return c1_h, c1_w

    return w, h


def _autocorrelate_rgba(data, total_pixels):
    """Use row autocorrelation to detect image width."""
    # Find the most varied region
    best_offset = 0
    best_diversity = 0
    for off in range(0, len(data) - 4096, 4096):
        chunk = data[off:off + 4096]
        unique = len(set(chunk[i:i + 4] for i in range(0, len(chunk), 4)))
        if unique > best_diversity:
            best_diversity = unique
            best_offset = off

    if best_diversity < 8:
        return None  # not enough variation for autocorrelation

    # Collect sample offsets in varied areas
    sample_offsets = [best_offset]
    for frac in [0.25, 0.5, 0.75]:
        off = int(len(data) * frac) & ~3
        # Check this region has variation too
        chunk = data[off:off + 4096]
        unique = len(set(chunk[i:i + 4] for i in range(0, min(len(chunk), 4096), 4)))
        if unique >= 4:
            sample_offsets.append(off)

    candidates = {}

    for w in range(8, min(4097, total_pixels)):
        if total_pixels % w != 0:
            continue
        h = total_pixels // w
        if h > 4096:
            continue

        stride = w * 4
        scores = []

        for sec_off in sample_offsets:
            start = max(0, sec_off)
            end = min(len(data), start + stride * 20)
            section = data[start:end]

            num_rows = len(section) // stride - 1
            if num_rows < 2:
                continue

            # Check row variation
            first_row = section[:stride]
            row_unique = len(set(first_row[i:i + 4] for i in range(0, min(len(first_row), stride), 4)))
            if row_unique < 4:
                continue

            total_sim = 0
            n = min(num_rows, 10)
            for row in range(n):
                off = row * stride
                r1 = section[off:off + stride]
                r2 = section[off + stride:off + stride * 2]
                matches = sum(1 for a, b in zip(r1, r2) if abs(a - b) < 10)
                total_sim += matches / stride
            scores.append(total_sim / n)

        if scores:
            candidates[w] = sum(scores) / len(scores)

    if not candidates:
        return None

    # Apply stride damping: narrow widths get artificially high scores because
    # few bytes per row makes comparison unreliable (sub-harmonic effect).
    # Dampen widths with stride < 200 bytes (< 50 pixels).
    damped = {}
    for w, score in candidates.items():
        stride = w * 4
        damping = min(1.0, stride / 200)
        damped[w] = score * damping

    # Pick the highest damped score. Tiebreaker: squarer dimensions.
    best_w = max(damped.keys(), key=lambda w: (
        damped[w],
        min(w, total_pixels // w) / max(w, total_pixels // w)
    ))

    if damped[best_w] < 0.55:
        return None

    return best_w, total_pixels // best_w


def detect_dimensions_dxt(data, block_bytes):
    """Auto-detect dimensions for DXT data (8 or 16 bytes per block)."""
    num_blocks = len(data) // block_bytes
    w, h = _find_best_dims(num_blocks, 4)
    if w is None:
        return None, None

    # If width != height, try both orientations using block-level autocorrelation
    # to determine correct orientation
    if w != h:
        score_wh = _dxt_orientation_score(data, w, h, block_bytes)
        score_hw = _dxt_orientation_score(data, h, w, block_bytes)
        if score_hw > score_wh:
            w, h = h, w

    return w, h


def _dxt_orientation_score(data, width, height, block_bytes):
    """Score how well DXT blocks correlate row-to-row at given dimensions.

    Compares color endpoints of adjacent block rows to determine orientation.
    """
    bw = (width + 3) // 4  # blocks per row
    row_bytes = bw * block_bytes
    num_block_rows = (height + 3) // 4
    if num_block_rows < 2 or row_bytes == 0:
        return 0

    # Compare color endpoints between adjacent block rows
    total_sim = 0
    n_compared = 0
    # Sample from multiple positions
    for start_row in range(0, min(num_block_rows - 1, 20)):
        row_off = start_row * row_bytes
        next_off = row_off + row_bytes
        if next_off + row_bytes > len(data):
            break
        matches = 0
        total = 0
        for b in range(bw):
            # Color endpoints are at offset 0-3 in DXT1 blocks
            # and at offset 8-11 in DXT3/DXT5 blocks
            color_off = 8 if block_bytes == 16 else 0
            off1 = row_off + b * block_bytes + color_off
            off2 = next_off + b * block_bytes + color_off
            if off2 + 4 > len(data):
                break
            c0a, c1a = struct.unpack_from("<HH", data, off1)
            c0b, c1b = struct.unpack_from("<HH", data, off2)
            # Compare RGB565 color endpoints
            if abs(c0a - c0b) < 2048 and abs(c1a - c1b) < 2048:
                matches += 1
            total += 1
        if total > 0:
            total_sim += matches / total
            n_compared += 1

    return total_sim / n_compared if n_compared else 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Convert XNB-extracted Texture2D to PNG")
    parser.add_argument("input", help="Input .Texture2D file")
    parser.add_argument("output", help="Output .png file")
    parser.add_argument("--width", type=int, help="Image width (auto-detected if omitted)")
    parser.add_argument("--height", type=int, help="Image height (auto-detected if omitted)")
    parser.add_argument("--format", choices=["rgba", "dxt1", "dxt3", "dxt5"],
                        help="Pixel format (auto-detected if omitted)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    data = input_path.read_bytes()
    file_size = len(data)
    print(f"Input: {input_path.name} ({file_size} bytes)")

    # Detect or use specified format
    fmt = args.format or detect_format(data)
    print(f"Format: {fmt}")

    # Detect or use specified dimensions
    width = args.width
    height = args.height

    if width and height:
        pass
    elif fmt == "rgba":
        det_w, det_h = detect_dimensions_rgba(data)
        width = width or det_w
        height = height or det_h
    elif fmt == "dxt1":
        det_w, det_h = detect_dimensions_dxt(data, 8)
        width = width or det_w
        height = height or det_h
    elif fmt in ("dxt3", "dxt5"):
        det_w, det_h = detect_dimensions_dxt(data, 16)
        width = width or det_w
        height = height or det_h

    if not width or not height:
        print("Error: Could not auto-detect dimensions. Use --width and --height.", file=sys.stderr)
        sys.exit(1)

    print(f"Dimensions: {width}x{height}")

    # Validate size
    if fmt == "rgba":
        expected = width * height * 4
    elif fmt == "dxt1":
        expected = ((width + 3) // 4) * ((height + 3) // 4) * 8
    else:
        expected = ((width + 3) // 4) * ((height + 3) // 4) * 16

    if expected != file_size:
        print(f"Error: expected {expected} bytes for {width}x{height} {fmt}, got {file_size}",
              file=sys.stderr)
        sys.exit(1)

    # Decode
    if fmt == "rgba":
        rgba_data = data
    elif fmt == "dxt1":
        rgba_data = decode_dxt1(data, width, height)
    elif fmt == "dxt3":
        rgba_data = decode_dxt3(data, width, height)
    elif fmt == "dxt5":
        rgba_data = decode_dxt5(data, width, height)
    else:
        print(f"Error: unsupported format '{fmt}'", file=sys.stderr)
        sys.exit(1)

    img = Image.frombytes("RGBA", (width, height), rgba_data)
    img.save(args.output)
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
