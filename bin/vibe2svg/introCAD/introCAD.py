#!/usr/bin/env python3
# Vibe coded by Claude
#
# introCAD.py - Convert an IntroCAD (Amiga) drawing file into an SVG vector image.
#
#   usage: introCAD.py <inputFile> <outputFile>
#
# IntroCAD was an object-oriented 2D drawing/CAD program for the Commodore
# Amiga, written by Tim Mooney and published by Progressive Peripherals &
# Software (1987-1990).  Every drawing it saves is a flat list of "primitive
# objects", each of which is simply a poly-line: an ordered list of (x, y)
# points connected by straight segments.  Curved shapes (circles, arcs, text,
# freehand) are pre-flattened into many short segments at save time, so a
# faithful renderer only has to stroke/fill poly-lines.
#
# The complete byte-level file format is documented in introCAD.txt.
#
# The 4-byte magic verifies the file is genuinely an IntroCAD file; if it is
# missing the converter fails fast (non-zero exit, nothing written).  Past the
# magic the body is read best-effort: every object that parses is rendered, and
# if the stream is truncated or corrupt the valid prefix is still emitted (with
# a warning on stderr).  Output is withheld only when the magic is present but
# not a single drawable object can be decoded.

import sys
import os
import struct

MAGIC = b"\x00\x12\xd6\x44"          # 0x0012D644 == 1234500 decimal
HEADER_LEN = 6                        # per-object header, in bytes
POINT_LEN = 8                         # one (x, y) point: two 32-bit FFP floats


class IntroCADError(Exception):
    """Raised when the input is not a parseable IntroCAD drawing."""


# --------------------------------------------------------------------------
# Motorola "Fast Floating Point" (FFP) decoder
#
# FFP packs a real number into 32 bits, big-endian:
#     bits 31..8  (3 bytes) : 24-bit mantissa, normalised so bit 31 == 1
#     bit  7              : sign (1 == negative)
#     bits 6..0           : exponent, excess-64 (bias 64)
# The binary point sits immediately to the left of the mantissa, so the
# mantissa is a fraction in [0.5, 1.0) and the value is:
#     (-1)^sign * (mantissa / 2**24) * 2**(exponent - 64)
# Zero is the single all-bits-zero word.  Any other word whose mantissa MSB
# is clear is not a legal normalised FFP value -- we use that fact to
# validate that we are really looking at coordinate data.
# --------------------------------------------------------------------------
def ffp_is_valid(word):
    return (word[0] & 0x80) != 0 or word == b"\x00\x00\x00\x00"


def ffp_decode(word):
    mant = (word[0] << 16) | (word[1] << 8) | word[2]
    if mant == 0:
        return 0.0
    sign = word[3] >> 7
    exp = word[3] & 0x7F
    val = (mant / 16777216.0) * (2.0 ** (exp - 64))
    return -val if sign else val


# --------------------------------------------------------------------------
# IntroCAD's default 16-entry screen palette (from the shipped IntroCAD.rgb).
# Each Amiga register holds 4-bit R/G/B; we expand to 8-bit.  Index 0 is the
# paper / background colour; index 4 (black) is the default plot colour.
# --------------------------------------------------------------------------
_PALETTE_4BIT = [
    "dca", "b00", "cba", "000", "000", "0c0", "f00", "00f",
    "a50", "ff0", "0ff", "f7f", "02a", "f00", "fda", "fff",
]


def _expand(nibbles):
    r, g, b = (int(c, 16) for c in nibbles)
    return (r * 17, g * 17, b * 17)


PALETTE = [_expand(c) for c in _PALETTE_4BIT]


# --------------------------------------------------------------------------
# Line-type dash masks, lifted from the IntroCAD executable.  Each is a
# 16-bit repeating on/off stipple, drawn most-significant-bit first.
# Index 0 (solid) is rendered without a dash array.
# --------------------------------------------------------------------------
LINE_PATTERNS = [0xFFFF, 0xCCCC, 0xF0F0, 0xFFF0, 0xFFCC, 0xFF3C, 0xFCCC]


def pattern_to_dash(mask, unit):
    """Turn a 16-bit stipple into an SVG stroke-dasharray run list (in `unit`)."""
    if mask in (0xFFFF, 0x0000):
        return None
    bits = [(mask >> (15 - i)) & 1 for i in range(16)]
    # Rotate so the array starts on an "on" run (dasharray must start with a dash).
    start = bits.index(1)
    bits = bits[start:] + bits[:start]
    runs = []
    cur = bits[0]
    length = 0
    for bit in bits:
        if bit == cur:
            length += 1
        else:
            runs.append(length)
            cur = bit
            length = 1
    runs.append(length)
    if len(runs) % 2:                 # dasharray needs dash/gap pairs
        runs.append(0)
    return " ".join("%.4g" % (r * unit) for r in runs if True)


# --------------------------------------------------------------------------
# Object model
# --------------------------------------------------------------------------
class CadObject(object):
    __slots__ = ("points", "color", "line_type", "thick", "filled",
                 "grouped", "layer")

    def __init__(self, points, color, line_type, thick, filled, grouped, layer):
        self.points = points
        self.color = color
        self.line_type = line_type
        self.thick = thick
        self.filled = filled
        self.grouped = grouped
        self.layer = layer


def parse(data):
    """Best-effort parse of an IntroCAD file.

    The 4-byte magic is the gate that verifies the file really is an IntroCAD
    file; a missing/wrong magic raises IntroCADError (the caller writes nothing).

    Past the magic we decode object records back-to-back for as long as they
    remain well-formed.  The moment a record fails to parse -- a zero point
    count, a record that runs off the end, or a coordinate that is not a legal
    FFP value -- we stop and keep everything decoded so far.  This salvages the
    valid prefix of a truncated or corrupted drawing instead of discarding it.

    Returns (objects, consumed, total, stop_reason):
      objects     - list of CadObject successfully decoded
      consumed    - byte offset at which parsing stopped
      total       - file length in bytes
      stop_reason - None if the records parsed cleanly all the way to EOF,
                    otherwise a human-readable description of where/why parsing
                    stopped early (i.e. the file is truncated or corrupt).
    """
    if len(data) < 4 or data[:4] != MAGIC:
        raise IntroCADError("not an IntroCAD file (bad magic)")

    objects = []
    pos = 4
    n = len(data)
    stop_reason = None
    while pos < n:
        if pos + HEADER_LEN > n:
            stop_reason = "truncated object header at offset %d" % pos
            break
        count = data[pos]
        color = data[pos + 1]
        line_byte = data[pos + 2]
        group_byte = data[pos + 3]
        flag_byte = data[pos + 4]
        layer = data[pos + 5]
        if count == 0:
            stop_reason = "zero-point object at offset %d" % pos
            break
        end = pos + HEADER_LEN + count * POINT_LEN
        if end > n:
            stop_reason = "object at offset %d overruns end of file" % pos
            break

        pts = []
        off = pos + HEADER_LEN
        bad_off = None
        for _ in range(count):
            xw = data[off:off + 4]
            yw = data[off + 4:off + 8]
            if not ffp_is_valid(xw) or not ffp_is_valid(yw):
                bad_off = off
                break
            pts.append((ffp_decode(xw), ffp_decode(yw)))
            off += POINT_LEN
        if bad_off is not None:
            stop_reason = "invalid coordinate data at offset %d" % bad_off
            break

        objects.append(CadObject(
            points=pts,
            color=color & 0x0F,
            line_type=line_byte & 0x07,
            thick=bool(flag_byte & 0x01),
            filled=bool(flag_byte & 0x04),
            grouped=bool(group_byte & 0x01),
            layer=layer,
        ))
        pos = end

    return objects, pos, n, stop_reason


# --------------------------------------------------------------------------
# SVG emitter
# --------------------------------------------------------------------------
def to_svg(objects):
    xs = [p[0] for o in objects for p in o.points]
    ys = [p[1] for o in objects for p in o.points]
    if xs:
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
    else:
        # an empty (records-free) drawing: emit a valid 1x1 canvas
        minx, maxx, miny, maxy = 0.0, 1.0, 0.0, 1.0
    width = maxx - minx
    height = maxy - miny
    span = max(width, height, 1e-6)

    margin = span * 0.02
    thin = span * 0.0015
    thick = span * 0.0035
    dash_unit = span * 0.006

    vb_x = minx - margin
    vb_y = -maxy - margin                 # SVG y grows downward; we flip world y
    vb_w = width + 2 * margin
    vb_h = height + 2 * margin

    paper = "#%02x%02x%02x" % PALETTE[0]

    out = []
    out.append(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'viewBox="%.4f %.4f %.4f %.4f" '
        'shape-rendering="geometricPrecision">' % (vb_x, vb_y, vb_w, vb_h)
    )
    out.append('<rect x="%.4f" y="%.4f" width="%.4f" height="%.4f" fill="%s"/>'
               % (vb_x, vb_y, vb_w, vb_h, paper))

    for o in objects:
        col = "#%02x%02x%02x" % PALETTE[o.color]
        d = "M " + " L ".join("%.4f %.4f" % (x, -y) for x, y in o.points)
        attrs = ['d="%s"' % d]
        if o.filled:
            attrs.append('fill="%s"' % col)
            attrs.append('stroke="none"')
        else:
            attrs.append('fill="none"')
            attrs.append('stroke="%s"' % col)
            attrs.append('stroke-width="%.4f"' % (thick if o.thick else thin))
            attrs.append('stroke-linecap="round"')
            attrs.append('stroke-linejoin="round"')
            dash = pattern_to_dash(LINE_PATTERNS[o.line_type], dash_unit)
            if dash:
                attrs.append('stroke-dasharray="%s"' % dash)
        out.append("<path %s/>" % " ".join(attrs))

    out.append("</svg>\n")
    return "\n".join(out)


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("usage: introCAD.py <inputFile> <outputFile>\n")
        return 2
    in_path, out_path = argv[1], argv[2]

    try:
        with open(in_path, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        sys.stderr.write("cannot read %s: %s\n" % (in_path, exc))
        return 1

    try:
        objects, consumed, total, stop_reason = parse(data)
    except IntroCADError as exc:
        # Only reached when the file is not an IntroCAD file at all (bad magic):
        # fail fast and write nothing.
        sys.stderr.write("%s: %s\n" % (in_path, exc))
        return 1

    if not objects and stop_reason is not None:
        # The IntroCAD magic is present but not a single drawable record could
        # be decoded -- there is genuinely nothing to render (e.g. a settings
        # file that merely shares the magic).  Fail rather than emit a blank.
        sys.stderr.write("%s: no drawable objects (%s)\n" % (in_path, stop_reason))
        return 1

    if stop_reason is not None:
        # Salvaged the valid prefix of a truncated/corrupt drawing.
        sys.stderr.write(
            "%s: warning: input appears truncated or corrupt -- rendered the "
            "first %d object(s); stopped at offset %d of %d (%s)\n"
            % (in_path, len(objects), consumed, total, stop_reason))

    svg = to_svg(objects)
    try:
        with open(out_path, "w") as fh:
            fh.write(svg)
    except OSError as exc:
        sys.stderr.write("cannot write %s: %s\n" % (out_path, exc))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
