#!/usr/bin/env python3
# Vibe coded by Codex
"""MacDraw 0.9, 1.x, II, Pro and wrapped PICT decoder and SVG renderer.

Missing font families use bundled Geneva at the requested size and face.
The default attempts recovery of damaged native documents and reports losses.
--strict rejects damage and unresolved drawing semantics without writing.
--preview retains the older structurally strict research-rendering mode.
Wrapped PICT drawings use deark for embedded bitmaps; other rendering uses
Python's standard library. See macDraw.txt for the support boundary.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
from dataclasses import dataclass, field
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
import tempfile
import xml.etree.ElementTree as ET
import zlib

import macDrawText
import macDrawContainer

SVG = "http://www.w3.org/2000/svg"
XLINK = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG)
ET.register_namespace("xlink", XLINK)


class FormatError(ValueError):
    """Invalid or out-of-scope binary syntax; no output may be committed."""


class UnsupportedError(FormatError):
    """Valid framing, but a required drawing interpretation is not established."""


def wrapped_pict_version(data):
    """Return 1/2 for a recognized export prefix, or None; not full validation.

    Only the first 526 bytes are needed. The unversioned DRWG signature is
    shared with native files, so also require the PICT version opcode.
    """
    if data[:8] not in (b"DRWGD2\x00\x06", b"DRWG\x00\x00\x00\x00",
                       b"DRWGMD\x00\x06"):
        return None
    if data[522:524] == b"\x11\x01":
        return 1
    if data[522:526] == b"\x00\x11\x02\xff":
        return 2
    return None


@dataclass(frozen=True)
class Issue:
    offset: int
    length: int
    code: str
    detail: str

    def as_dict(self):
        return dict(offset=self.offset, length=self.length, code=self.code,
                    detail=self.detail)


@dataclass
class Object:
    offset: int
    kind: int
    attrs: tuple
    fields: dict = field(default_factory=dict)
    children: list = field(default_factory=list)
    end: int = 0
    count: int = 1
    memory_small: int = 0
    memory_large: int = 0


@dataclass
class Document:
    data: bytes
    revision: int | str
    header: dict
    objects: list
    spans: list
    issues: list
    record_count: int

    @property
    def recovered(self):
        return any(i.code.startswith("recovery_") for i in self.issues)

    def require_complete(self):
        if self.issues:
            i = self.issues[0]
            counts = Counter(x.code for x in self.issues)
            raise UnsupportedError(
                f"0x{i.offset:x}: {i.detail}; unresolved categories: "
                + ", ".join(sorted(counts))
                + ". No SVG written in strict mode. Default conversion attempts "
                  "documented recovery and marks incomplete results.")

    def audit(self):
        position = 0
        for offset, length, name in self.spans:
            if offset != position:
                raise AssertionError(f"coverage gap/overlap at {position}: {name}")
            position += length
        if position != len(self.data):
            raise AssertionError("incomplete byte coverage")
        # The union avoids counting overlapping limitations more than once.
        intervals = sorted((i.offset, i.offset + i.length) for i in self.issues)
        union = []
        for a, b in intervals:
            if union and a <= union[-1][1]:
                union[-1][1] = max(union[-1][1], b)
            else:
                union.append([a, b])
        fonts = {}
        def collect(objects):
            for obj in objects:
                fragments = obj.fields.get("text_fragments", [])
                if "text_layout" in obj.fields:
                    fragments = [obj.fields]
                for fragment in fragments:
                    m = fragment["text_layout"].metrics
                    key = (fragment["font_id"],m.size,fragment["face"],
                           fragment["font_index"])
                    fonts[key] = dict(family=key[0], size=key[1], face=key[2],
                                      menu_index=key[3],
                                      resolved_family=m.strike.family,
                                      substituted=macDrawText.is_substituted(key[0], m.strike.family),
                                      family_alias='application font' if key[0] == 1 else None,
                                      synthesized_face=m.face,
                                      strike_size=m.strike.size, strike_face=m.strike.face,
                                      name=m.strike.name, source=m.strike.source,
                                      sha256=m.strike.digest)
                collect(obj.children)
        collect(self.objects)
        omitted = [dict(offset=a, length=n) for a,n,name in self.spans
                   if name == "recovery_uninterpreted_bytes"]
        unframed = sum(x["length"] for x in omitted)
        return dict(bytes=len(self.data), accounted_bytes=position,
                    framed_bytes=position-unframed, uninterpreted_bytes=unframed,
                    omitted_byte_ranges=omitted,
                    conversion_status=("recovered" if self.recovered else
                                       "approximate" if self.issues else "converted"),
                    recovery_events=[i.as_dict() for i in self.issues
                                     if i.code.startswith("recovery_")],
                    text_environment=(self.header.get("text_environment_override") or
                                      macDrawText.text_environment(self.revision)) if fonts else None,
                    native_format=self.header.get("native_format", "MacDraw"),
                    layers=self.header.get("layers", []),
                    original_font_menu=self.header.get("original_font_menu"),
                    input_container=self.header.get("input_container"),
                    drawing_resources=self.header.get("drawing_resources"),
                    picture=self.header.get("picture"),
                    external_resource_fork=self.header.get("external_resource_fork"),
                    inactive_suffix=self.header.get("inactive_suffix"),
                    font_resources=list(fonts.values()),
                    font_substitutions=[v for v in fonts.values() if v['substituted']],
                    full_format_semantics_established=False,
                    metadata_limitations=self.header.get("metadata_limitations_override", [
                        "Printer-driver extension remains driver-owned opaque data.",
                        "Some saved editor preferences lack individual bit meanings; "
                        "ruler units used by drawing geometry are decoded."]),
                    bytes_affected_by_limitations=sum(b-a for a, b in union),
                    revision=self.revision, top_level_objects=len(self.objects),
                    total_objects=sum(o.count for o in self.objects),
                    records=self.record_count,
                    sha256=hashlib.sha256(self.data).hexdigest(),
                    issues=[i.as_dict() for i in self.issues])


class Reader:
    def __init__(self, data):
        self.data, self.pos, self.spans = data, 0, []

    def take(self, length, name):
        start = self.pos
        if length < 0 or length > len(self.data) - start:
            raise FormatError(f"0x{start:x}: truncated {name}; need {length} bytes, "
                              f"have {len(self.data)-start}")
        self.pos += length
        if length:
            self.spans.append((start, length, name))
        return self.data[start:self.pos]

    def unpack(self, fmt, name):
        return struct.unpack(">" + fmt, self.take(struct.calcsize(">" + fmt), name))

    def one(self, fmt, name):
        return self.unpack(fmt, name)[0]


class Parser:
    def __init__(self, data, require_complete=False, fonts=None, recover=False, resource_fork=None):
        if recover and require_complete:
            raise ValueError("recovery and complete validation are mutually exclusive")
        self.r = Reader(data)
        self.resource_fork = resource_fork
        self.issues = []
        self.records = 0
        self.revision = 0
        self.header = {}
        self.require_complete = require_complete
        self.fonts = fonts
        self.recover = recover

    def issue(self, offset, length, code, detail):
        if self.require_complete:
            raise UnsupportedError(f"0x{offset:x}: {detail}. No SVG written. "
                                   "This drawing feature is not fully supported; "
                                   "--preview explicitly enables research rendering.")
        self.issues.append(Issue(offset, length, code, detail))

    def damage(self, offset, length, code, detail):
        """A known invariant may fail without losing the surrounding framing."""
        if not self.recover:
            raise FormatError(f"0x{offset:x}: {detail}")
        self.issue(offset, length, "recovery_"+code, detail)

    def record_extent(self, start):
        """Return only a format-defined end; never search for a plausible header.

        A group has no serialized subtree length. Invalid polygon size/count
        pairs and invalid bitmap strides likewise cannot establish a next record.
        """
        data = self.r.data
        if len(data)-start < 8:
            return None
        kind = data[start]
        size = {2:24, 3:24, 4:24, 5:24, 6:24, 7:28}.get(kind)
        if kind == 1 and len(data)-start >= 28:
            size = 28+struct.unpack_from(">H", data, start+18)[0]
        elif kind in (8,9) and len(data)-start >= 32:
            block, count = struct.unpack_from(">IH", data, start+8)
            if count and block == (26+2*count if kind == 8 else 20+8*count):
                size = 12+block
        elif kind == 11 and self.revision == 6 and len(data)-start >= 50:
            row, top, left, bottom, right = struct.unpack_from(">H4h", data, start+40)
            if 0 < row < 0x4000 and 0 < right-left <= row*8 and bottom > top:
                size = 50+row*(bottom-top)
        return start+size if size is not None else None

    def discard_failed_record(self, start, span_count, issue_count, records, error):
        r = self.r
        end = self.record_extent(start)
        # Roll back partially decoded fields: unreadable records must not be
        # reported as semantically framed, nor leave speculative font issues.
        r.pos = start
        del r.spans[span_count:]
        del self.issues[issue_count:]
        self.records = records
        bounded = end is not None and end <= len(r.data)
        stop = end if bounded else len(r.data)
        r.take(stop-start, "recovery_uninterpreted_bytes")
        self.damage(start, stop-start, "omitted_record" if bounded else "omitted_suffix",
                    str(error)+("; object omitted; resumed at its declared end"
                                if bounded else "; remaining bytes omitted: no reliable next record boundary"))
        return bounded

    def nonzero_opaque(self, length, name):
        start = self.r.pos
        b = self.r.take(length, name)
        if any(b):
            self.issue(start, length, name, f"nonzero {name} is not fully decoded")
        return b.hex()

    def parse(self):
        try:
            container = macDrawContainer.unpack_macbinary(self.r.data, recover=self.recover)
        except macDrawContainer.ContainerError as error:
            raise FormatError(str(error)) from error
        if container is not None:
            return self.parse_container(container)
        return self.parse_native()

    def parse_container(self, container):
        child = Parser(container.data, require_complete=self.require_complete,
                       fonts=self.fonts, recover=self.recover, resource_fork=self.resource_fork if self.resource_fork is not None else container.resource)
        # Only one outer container is supported; never recursively scan or
        # unwrap arbitrary data in search of a recognizable document.
        doc = child.parse_native()
        offset = container.data_offset
        doc.data = self.r.data
        native_spans = [(a+offset,n,name) for a,n,name in doc.spans]
        doc.spans = []
        for a,n,name in container.spans:
            doc.spans.extend(native_spans if name == 'macbinary_data_fork' else [(a,n,name)])
        doc.issues = [Issue(i.offset+offset,i.length,i.code,i.detail) for i in doc.issues]
        doc.issues += [Issue(*issue) for issue in container.issues]
        def rebase(objects):
            for obj in objects:
                obj.offset += offset
                obj.end += offset
                if 'data_offset' in obj.fields:obj.fields['data_offset'] += offset
                if 'pixel_offset' in obj.fields:obj.fields['pixel_offset'] += offset
                rebase(obj.children)
        rebase(doc.objects)
        for zone in doc.header.get('zones',[]):zone['offset'] += offset
        if doc.header.get('picture'):
            doc.header['picture']['end_offset'] += offset
            doc.header['picture']['data_fork_offset'] = offset
        for name in ('inactive_suffix','unreferenced_trailing_storage'):
            if doc.header.get(name):doc.header[name]['offset'] += offset
        doc.header['input_container'] = container.metadata
        doc.header['metadata_limitations_override'] = [
            *doc.audit()['metadata_limitations'],
            'MacBinary Finder metadata, padding and complete resource fork are preserved; application-specific resource semantics are not completely decoded.']
        self.r.pos = len(self.r.data)
        doc.audit()
        return doc

    def parse_native(self):
        r = self.r
        if r.data[:4] in (b'dDoc',b'dLib'):
            import macDrawPro
            return macDrawPro.parse(r.data, sys.modules[__name__], fonts=self.fonts,
                recover=self.recover, require_complete=self.require_complete, resource_fork=self.resource_fork)
        if r.data[:4] in (b"DRWG", b"STAT"):
            if (wrapped_pict_version(r.data) is not None and
                    (r.data[4:8] == b"D2\0\6" or not any(r.data[256:500]))):
                import macDrawPICT
                return macDrawPICT.parse(r.data, sys.modules[__name__], fonts=self.fonts,
                    recover=self.recover, require_complete=self.require_complete)
            if r.data[4:8] in (b"D2\x00\x00", b"D2\x00\x01", b"D2\xff\xff", b"\x00"*4):
                import macDrawII
                return macDrawII.parse(r.data, sys.modules[__name__], fonts=self.fonts,
                                       recover=self.recover, require_complete=self.require_complete)
            if r.data[4:8] == b"D2\x00\x06":
                raise FormatError("MacDraw-wrapped PICT export lacks its required PICT version marker")
        signature = r.take(8, "signature")
        if signature == b"DRWGMD\x00\x06":
            self.revision = 6
        elif signature == b"MD\x00\x04\x00\x00\x00\x00":
            self.revision = 4
        else:
            raise FormatError("0x0: expected native MacDraw revision 4, revision 6, MacDraw II, or MacDraw Pro")
        # Classic Printing Manager TPrint: exactly 120 bytes, not a size field.
        h = self.header
        print_fields = [
            ("print_version", "h"), ("device", "h"),
            ("v_resolution", "h"), ("h_resolution", "h"),
            ("page_rect", "4h"), ("paper_rect", "4h"),
            ("style", "3h2B"), ("print_info_pt", "7h"),
            ("band_info", "5h6b"), ("print_job", "3h2B2Ih2b"),
        ]
        for name, fmt in print_fields:
            values = r.unpack(fmt, name)
            h[name] = values[0] if len(values) == 1 else values
        # TPrint's driver-owned extension is passed to Printing Manager, not
        # interpreted as drawing data by the original native loader/renderer.
        h["driver_private"] = r.take(38, "printer_driver_private").hex()
        assert r.pos == 128
        if h["print_version"] not in (0, 1, 2, 3):
            self.issue(8, 120, "printer_version", "unrecognized Printing Manager record version")
        if self.revision == 4:
            # Original 0.9 writer: 1 + ceil(list allocation size / 512).
            # This is an allocation-block estimate, not an object count or
            # serialized length. The loader only tests whether it exceeds 1.
            h["allocation_blocks"] = r.one("H", "revision4_allocation_blocks")
            if not 1 <= h["allocation_blocks"] <= 32767:
                self.damage(128, 2, "allocation_blocks", "invalid revision-4 allocation-block estimate; attempting the native object payload")
        h["origin"] = r.unpack("2i", "origin")
        h["scale"] = r.unpack("2i", "scale")
        if h["origin"] != (0, 0) or h["scale"] != (72*65536, 72*65536):
            self.issue(r.pos-16, 16, "coordinate_mapping", "nondefault origin/scale mapping is unverified")
        editor = r.take(62, "saved_editor_preferences")
        h["editor_state"] = editor.hex()
        h["editor"] = dict(
            current_attributes=struct.unpack_from(">BBHBBBB", editor),
            current_tool=editor[8], tool_padding=editor[9],
            current_text_style=tuple(editor[10:16]),
            page_flags=tuple(editor[16:22]),
            page_points=struct.unpack_from(">8h", editor, 22),
            ruler_flags=tuple(editor[38:46]),
            ruler_points=struct.unpack_from(">4i", editor, 46))
        # This preference is used by the actual rounded-rectangle renderer.
        h["ruler_units"] = editor[39]
        if self.revision == 6:
            h["top_count"], h["total_count"], h["memory_size"] = r.unpack("HHI", "document_list")
            h["bounds"] = r.unpack("4i", "document_bounds")
            # This is a one-based font menu table. No string names are stored.
            h["font_table"] = r.unpack("141H", "font_menu_table_and_unused_tail")

        else:
            h["old_tail"] = self.nonzero_opaque(512-r.pos, "revision4_header_tail")
        assert r.pos == 512
        if (len(r.data) == 512 and self.revision == 6
                and (h["top_count"] or h["total_count"] or h["memory_size"])):
            raise FormatError(
                f"0x200: header declares {h['top_count']} top-level and "
                f"{h['total_count']} total objects, but the object payload is missing")
        # Detection is anchored at the prescribed payload offset, never scanned.
        empty_old = self.revision == 4 and h["allocation_blocks"] == 1
        if not empty_old and len(r.data) >= 524:
            frame = struct.unpack_from(">4h", r.data, 514)
            if (frame[0] < frame[2] and frame[1] < frame[3]
                    and (r.data[522:524] == b"\x11\x01"
                         or r.data[522:526] == b"\x00\x11\x02\xff")):
                import macDrawPICT
                return macDrawPICT.parse(r.data, sys.modules[__name__], fonts=self.fonts,
                    recover=self.recover, require_complete=self.require_complete)
        if (empty_old or (len(r.data) == 512 and self.revision == 6
                and h["top_count"] == h["total_count"] == h["memory_size"] == 0)):
            objects = []
        else:
            objects = self.read_list(None, 0)
        if r.pos != len(r.data):
            if self.revision != 4:
                self.damage(r.pos, len(r.data)-r.pos, "trailing_bytes",
                            f"{len(r.data)-r.pos} trailing bytes after the document terminator; omitted")
                r.take(len(r.data)-r.pos, "recovery_uninterpreted_bytes")
            # The 0.9 save path rewrites an existing data fork without SetEOF.
            # Its loader stops at the logical list end (or the header when
            # allocation_blocks == 1). Remaining bytes are inactive storage,
            # irrespective of their contents; never scan them for objects.
            if self.revision == 4:
                offset = r.pos
                suffix = r.take(len(r.data)-offset, "revision4_inactive_saved_file_suffix")
                h["inactive_suffix"] = dict(offset=offset, length=len(suffix),
                                            sha256=hashlib.sha256(suffix).hexdigest())
        if self.revision == 6:
            total = sum(o.count for o in objects)
            if len(objects) != h["top_count"] or total != h["total_count"]:
                self.damage(206, 4, "object_counts",
                            f"document declares {h['top_count']} top-level / {h['total_count']} total objects; "
                            f"retained {len(objects)} / {total}")
            sizes = (sum(o.memory_small for o in objects), sum(o.memory_large for o in objects))
            if h["memory_size"] not in sizes:
                self.damage(210, 4, "memory_size", f"list memory size {h['memory_size']} disagrees with retained allocation layouts {sizes}")
        else:
            allocation = sum(o.memory_small for o in objects)
            expected = 1+(allocation+511)//512
            if h["allocation_blocks"] != expected:
                self.damage(128, 2, "allocation_blocks", f"allocation-block estimate {h['allocation_blocks']} "
                            f"disagrees with revision-4 allocation total {allocation} ({expected} blocks)")
        def has_leaf(items):
            return any(o.kind != 10 or has_leaf(o.children) for o in items)
        if self.recover and self.issues and not has_leaf(objects):
            raise FormatError("recognized MacDraw header, but no drawable objects could be recovered; no SVG written")
        doc = Document(r.data, self.revision, h, objects, r.spans, self.issues, self.records)
        doc.audit()
        return doc

    def read_list(self, count, depth):
        if depth > 128:
            raise FormatError(f"0x{self.r.pos:x}: group nesting exceeds supported resource limit 128")
        out = []
        while True:
            if not self.recover and count is not None and len(out) > count:
                raise FormatError(f"0x{self.r.pos:x}: too many group children")
            if self.recover and self.r.pos == len(self.r.data):
                self.damage(self.r.pos, 0, "missing_terminator",
                            f"missing {'group' if depth else 'document'} terminator; retained complete preceding objects")
                return out
            start = self.r.pos
            checkpoint = (len(self.r.spans), len(self.issues), self.records)
            try:
                obj = self.read_object(depth)
            except FormatError as error:
                if not self.recover:
                    raise
                if self.discard_failed_record(start, *checkpoint, error):
                    continue
                return out
            if obj.kind == 0:
                if count is not None and len(out) != count:
                    self.damage(obj.offset, 8, "group_child_count",
                                f"group declares {count} children; retained {len(out)} before its terminator")
                return out
            if not self.recover and count is not None and len(out) == count:
                raise FormatError(f"0x{obj.offset:x}: expected group terminator")
            out.append(obj)

    def read_object(self, depth):
        r = self.r
        start = r.pos
        kind, lock, state, width, pen, fill, option = r.unpack("BBHBBBB", "object_attributes")
        self.records += 1
        if kind not in range(12):
            raise FormatError(f"0x{start:x}: unknown object type {kind}")
        if kind == 11 and self.revision == 4:
            raise FormatError(f"0x{start:x}: bitmap object type 11 is not part of revision 4")
        o = Object(start, kind, (lock, state, width, pen, fill, option))
        f = o.fields
        if kind == 0 and (lock not in (0,1) or state not in (0,256)
                          or not 1 <= width <= 5 or not 1 <= pen <= 36 or not 1 <= fill <= 36):
            # A damaged delimiter cannot establish which enclosing list ends.
            # Retain the objects but do not invent nesting from these bytes.
            raise FormatError(f"0x{start:x}: damaged list terminator")
        if lock not in (0, 1) or state not in (0, 256):
            self.damage(start+1, 3, "editor_state", "unsupported object state/lock encoding; ignored non-rendering state")
        if not 1 <= width <= 5 or not 1 <= pen <= 36 or not 1 <= fill <= 36:
            replacement = (width if 1 <= width <= 5 else 2,
                           pen if 1 <= pen <= 36 else 3,
                           fill if 1 <= fill <= 36 else 1)
            self.damage(start+4, 3, "paint_selection",
                        f"unsupported pen width/pattern selection {(width,pen,fill)}; "
                        + ("unused on this list/group record" if kind in (0,10) else
                           f"rendered with selections {replacement} (invalid width: 1 point; pen: black; fill: none)"))
            width, pen, fill = replacement
            o.attrs = (lock, state, width, pen, fill, option)
        # The common byte at +2 is initialized to 1 by MacDraw; +3 is
        # padding. Neither is read by the drawing dispatcher. Selection lives
        # outside the serialized record, in the in-memory object prefix.
        if kind == 0:
            o.end = r.pos
            return o
        if kind == 1:
            f["handle"] = r.one("I", "text_handle")
            face, font, size, spacing, align, transform, length = r.unpack("6BH", "text_style_and_length")
            f.update(face=face, font_index=font, size_index=size, spacing=spacing,
                     align=align, transform=transform)
            alignments = (1, 2, 3) if self.revision == 4 else (1, 2, 3, 5, 6, 7)
            if face & 128 or spacing not in (1, 2, 3) or align not in alignments or transform > 7:
                replacement = (face & 127, spacing if spacing in (1,2,3) else 1,
                               align if align in alignments else 1, transform if transform <= 7 else 0)
                self.damage(start+12, 6, "text_style",
                            f"unsupported text style {(face,spacing,align,transform)}; "
                            f"rendered with face/spacing/alignment/transform {replacement}")
                face, spacing, align, transform = replacement
                f.update(face=face, spacing=spacing, align=align, transform=transform)
            if size not in range(1, 9):
                self.damage(start+14, 1, "text_size",
                            f"unsupported font size menu index {size}; used 12-point recovery default")
                size = f["size_index"] = 3
            f["box"] = r.unpack("4h", "text_rectangle")
            if self.recover and length > len(r.data)-r.pos:
                available = len(r.data)-r.pos
                self.damage(r.pos, available, "partial_text",
                            f"text declares {length} bytes; retained {available} available bytes")
                length = available
            f["text_bytes"] = r.take(length, "text_characters")
            if any(c < 32 and c not in (9, 10, 13) for c in f["text_bytes"]):
                raise FormatError(f"0x{start+28:x}: unsupported text control character")
            if self.revision == 6:
                if not 1 <= font <= 141:
                    self.damage(start+13, 1, "font_index", "font index outside header table; used Geneva")
                    f["font_id"] = None
                else:
                    f["font_id"] = self.header["font_table"][font-1]
            else:
                if not 1 <= font <= 10:
                    self.damage(start+13, 1, "font_index", "font index outside revision-4 menu capacity; used Geneva")
                # 0.9 never saves its installed-font ID table. Only an explicit
                # original menu can resolve this index without guessing.
                menu = self.fonts.menu if self.fonts is not None else None
                f["font_id"] = menu[font-1] if menu and 1 <= font <= len(menu) else None
                if menu:
                    self.header["original_font_menu"] = self.fonts.menu_metadata
                    self.header["text_environment_override"] = dict(
                        macDrawText.text_environment(4),
                        family_identity='explicitly supplied original font-menu mapping')
            # Any nonzero option clears TE's CR-only flag. Alignment bit 4
            # affects exported PICT comments, not native text positioning.
            if length or fill != 1:
                try:
                    if self.fonts is None:
                        self.fonts = macDrawText.default_fonts()
                    f["text_layout"] = macDrawText.layout(f, option, self.fonts,
                                                         revision=self.revision)
                except macDrawText.MissingFont as exc:
                    self.issue(start+13, 1, "missing_font", str(exc))
                except macDrawText.FontError as exc:
                    self.issue(start+12, 16+length, "text_environment", str(exc))
            o.memory_small = (38 if self.revision == 4 else 58) + length
            o.memory_large = (38 if self.revision == 4 else 74) + length
        elif kind in (2, 3, 4, 5, 6, 7):
            f["box"] = tuple(x / 65536 for x in r.unpack("4i", "fixed_rectangle_or_endpoints"))
            if kind == 7:
                f["start_angle"], f["sweep_angle"] = r.unpack("2h", "arc_angles")
            if kind in (2, 3):
                if option & ~3:
                    self.damage(start+7, 1, "arrow_flags", f"unsupported arrow flags {option}; used the two defined bits")
                    o.attrs = (*o.attrs[:-1], option & 3)
            elif kind == 5:
                if not 1 <= option <= 6:
                    self.damage(start+7, 1, "corner_selection", "unsupported corner menu index; used square corners")
                    option = 1
                    o.attrs = (*o.attrs[:-1], option)
                if option != 1 and self.header["ruler_units"] not in (1, 2):
                    self.issue(183 if self.revision == 6 else 185, 1,
                               "corner_units", "rounded corner uses an unsupported ruler-unit selector")
            # For rectangle, ellipse and arc records, +7 is inherited from
            # the current drawing attributes but never read by the native
            # fill/outline paths. Every byte value is an unused selection.
            o.memory_small = o.memory_large = r.pos-start+(10 if self.revision == 4 else 22)
        elif kind in (8, 9):
            size = r.one("I", "polygon_storage_size")
            n = r.one("H", "polygon_point_count")
            f["box"] = tuple(x / 65536 for x in r.unpack("4i", "polygon_bounds"))
            mode = r.one("H", "polygon_flags_and_type")
            expected = 26+2*n if kind == 8 else 20+8*n
            if n == 0 or size != expected:
                raise FormatError(f"0x{start+8:x}: polygon storage size/count disagreement")
            if mode & 255 != kind:
                raise FormatError(f"0x{start+30:x}: polygon block type {mode & 255} "
                                  f"disagrees with object type {kind}; corrupt polygon record")
            if mode >> 8 not in ((0, 1) if kind == 8 else (0, 1, 2, 3)):
                raise FormatError(f"0x{start+30:x}: unsupported polygon mode 0x{mode:04x}")
            f.update(closed=bool(mode & 256), smooth=bool(mode & 512))
            truncated = False
            if self.recover and start+12+size > len(r.data):
                available = len(r.data)-r.pos
                retained = (1+(available-8)//2 if available >= 8 else 0) if kind == 8 else available//8
                if not retained:
                    raise FormatError(f"0x{r.pos:x}: polygon has no complete vertices")
                self.damage(r.pos, available, "partial_polygon",
                            f"polygon declares {n} vertices; retained {retained} complete vertices as an open, unsmoothed path")
                n, truncated = retained, True
                f.update(closed=False, smooth=False)
            if kind == 8:
                y, x = r.unpack("2i", "freehand_initial_point")
                points = [(x / 65536, y / 65536)]
                for _ in range(n-1):
                    dx, dy = r.unpack("2b", "freehand_delta_xy")
                    x, y = points[-1]
                    points.append((x+dx, y+dy))
            else:
                coords = r.unpack(f"{2*n}i", "polygon_points_yx")
                points = [(coords[i+1]/65536, coords[i]/65536) for i in range(0, 2*n, 2)]
            f["points"] = points
            if truncated:
                xs, ys = zip(*points)
                f["box"] = (min(ys), min(xs), max(ys), max(xs))
                r.take(len(r.data)-r.pos, "recovery_uninterpreted_bytes")
            if f["smooth"] and n < 3:
                self.issue(start+12, 2, "degenerate_spline",
                           "smooth polygon with fewer than three controls is unsupported")
            # Polygon closure and smoothing live in the polygon block's mode
            # word. The common option byte is an unused inherited selection.
            o.memory_small = o.memory_large = r.pos-start+(10 if self.revision == 4 else 30)
        elif kind == 10:
            if self.revision == 6:
                f["box"] = tuple(x/65536 for x in r.unpack("4i", "group_bounds"))
            n, total, size = r.unpack("HHI", "group_list")
            if self.revision == 4:
                f["box"] = tuple(x/65536 for x in r.unpack("4i", "group_bounds"))
            f["list_handles"] = r.unpack("2I", "group_list_handles")
            # Zero/nonzero selects ordinary/picture-group PICT comments.
            # The native renderer traverses the same children in both cases.
            f["picture_group"] = bool(option)
            o.children = self.read_list(n, depth+1)
            o.count += sum(c.count for c in o.children)
            if total != o.count-1:
                self.damage(start, 40, "group_descendant_count",
                            f"group declares {total} descendants; retained {o.count-1}")
            small = sum(c.memory_small for c in o.children)
            large = sum(c.memory_large for c in o.children)
            if size not in (small, large):
                self.damage(start, 40, "group_memory_size", f"group memory size {size} disagrees with {small} and {large}")
            f["list_memory_size"] = size
            own = 50 if self.revision == 4 else 62
            o.memory_small, o.memory_large = own+small, own+large
        elif kind == 11:
            f["bitmap_handle"] = r.one("I", "bitmap_handle")
            f["source_rect"] = r.unpack("4h", "bitmap_source_rect")
            f["box"] = tuple(x/65536 for x in r.unpack("4i", "bitmap_destination_rect"))
            f["base_address"] = r.one("I", "bitmap_base_address")
            row = r.one("H", "bitmap_row_bytes")
            f["bitmap_bounds"] = bounds = r.unpack("4h", "bitmap_storage_bounds")
            top, left, bottom, right = bounds
            st, sl, sb, sr = f["source_rect"]
            if not (row > 0 and row < 0x4000 and row*8 >= right-left > 0
                    and top <= st < sb <= bottom and left <= sl < sr <= right):
                raise FormatError(f"0x{start+12:x}: invalid monochrome bitmap bounds or stride")
            f["row_bytes"] = row
            required = row*(bottom-top)
            if self.recover and required > len(r.data)-r.pos:
                available = len(r.data)-r.pos
                rows = available//row
                kept_bottom = min(sb, top+rows)
                if kept_bottom <= st:
                    raise FormatError(f"0x{r.pos:x}: truncated bitmap has no complete visible rows")
                self.damage(r.pos, available, "partial_bitmap",
                            f"bitmap needs {required} bytes; retained {rows} complete storage rows and cropped missing image rows")
                f["bitmap"] = r.take(rows*row, "bitmap_rows_and_padding_bits")
                r.take(len(r.data)-r.pos, "recovery_uninterpreted_bytes")
                f["bitmap_bounds"] = (top, left, top+rows, right)
                f["source_rect"] = (st, sl, kept_bottom, sr)
                dt, dl, db, dr = f["box"]
                f["box"] = (dt, dl, dt+(db-dt)*(kept_bottom-st)/(sb-st), dr)
            else:
                f["bitmap"] = r.take(required, "bitmap_rows_and_padding_bits")
            # CopyBits takes its composition mode from the drawing path,
            # independently of the unused common option byte.
            o.memory_small = o.memory_large = r.pos-start+30
        o.end = r.pos
        return o


# Fixed application palette data, indexed by menu item. Item 1 is transparent;
# item 2 is opaque white. These are format data, not imported parser code.
PATTERNS_6 = """
0000000000000000 ffffffffffffffff 77dd77dd77dd77dd aa55aa55aa55aa55
8822882288228822 8800220088002200 8000080080000800 8000000008000000
8080413e080814e3 ff808080ff080808 8142241881422418 8040201008040201
e070381c0e0783c1 77bbddee77bbddee 8844221188442211 99cc663399cc6633
2040800008040200 ff00ff00ff00ff00 ff000000ff000000 cc00000033000000
f0f0f0f00f0f0f0f ff888888ff888888 aa44aa11aa44aa11 0102040810204080
83070e1c3870e0c1 eeddbb77eeddbb77 1122448811224488 3366cc993366cc99
40a00000040a0000 aaaaaaaaaaaaaaaa 8888888888888888 0101101001011010
0008142a552a1408 ff80808080808080 8244281028448201
""".split()
PATTERNS_4 = """
0000000000000000 ffffffffffffffff bbeebbeebbeebbee 55aa55aa55aa55aa
8822882288228822 8800220088002200 8000080080000800 0800000080000000
8080413e080814e3 081c224180010204 ff808080ff080808 0180402010080402
81c06030180c0603 1188440011884400 1188442211884422 3399cc663399cc66
0180400002040800 6600000099000000 ff000000ff000000 5020202050882788
849f80800404e784 010101ff010101ff 5588552255885522 8001020408102040
c08103060c183060 8811220088112200 8811224488112244 cc993366cc993366
2050000002050000 0808080808080808 0404404004044040 038448300c020101
0a11a04000b14a4a 404040ff40404040 4122140814224180
""".split()
FONT_NAMES = {
    0: ("Chicago", "sans-serif"), 1: ("Geneva", "sans-serif"),
    2: ("New York", "serif"), 3: ("Geneva", "sans-serif"),
    4: ("Monaco", "monospace"), 5: ("Venice", "cursive"),
    6: ("London", "serif"), 7: ("Athens", "serif"),
    8: ("San Francisco", "serif"), 9: ("Toronto", "sans-serif"),
    11: ("Cairo", "fantasy"), 12: ("Los Angeles", "cursive"),
    13: ("Zapf Dingbats", "fantasy"), 14: ("Bookman", "serif"),
    15: ("Helvetica Narrow", "sans-serif"), 16: ("Palatino", "serif"),
    18: ("Zapf Chancery", "cursive"), 20: ("Times", "serif"),
    21: ("Helvetica", "sans-serif"), 22: ("Courier", "monospace"),
    23: ("Symbol", "serif"), 24: ("Mobile", "fantasy"),
    33: ("Avant Garde", "sans-serif"), 34: ("New Century Schoolbook", "serif"),
}
FONT_SIZES = (9, 10, 12, 14, 18, 24, 36, 48)
PEN_WIDTHS = (0, 1, 2, 4, 6)
# Original application tables: corner oval DIAMETERS in 72-unit coordinates.
CORNER_DIAMETERS = {1: (0, 18, 27, 36, 45, 54),
                    2: (0, 22, 28, 34, 45, 56)}


def spline_vertices(points, closed):
    """Native 16-step fixed-point curve iterator (signed 16.16 inputs).

    Verified against the isolated original 68000 routine. Duplicate controls
    are retained. Results precede device scaling and QuickDraw pixel rounding.
    """
    def wrap(n):
        return (n + 0x80000000) % 0x100000000 - 0x80000000

    def add(a, b):
        return tuple(wrap(x+y) for x, y in zip(a, b))

    def sub(a, b):
        return tuple(wrap(x-y) for x, y in zip(a, b))

    def divide(a, n):
        return tuple((abs(x)//n)*(-1 if x < 0 else 1) for x in a)

    n = len(points)
    a, b, c = (points[i % n] for i in range(3))
    if not closed:
        a = sub(a, sub(b, a))
    position = divide(add(a, b), 2)
    start = position
    delta = divide(sub(b, a), 16)
    position = add(position, divide(delta, 2))
    count = n+2 if closed else n
    segment, step = 3, 0
    out = [start]
    while segment <= count:
        if segment == 3 and step == 0:
            step = 1
        else:
            if step == 1:
                if segment == count and not closed:
                    c = sub(c, sub(b, c))
                acceleration = divide(sub(sub(add(c, a), b), b), 256)
            delta = add(delta, acceleration)
            position = add(position, delta)
            step += 1
            if step > 16:
                if segment == count:
                    position = sub(position, divide(delta, 2))
                a, b, c = b, c, points[segment % n]
                step = 1
                segment += 1
        out.append(position)
    return out


# Native arrow radii for the five pen-menu selections. No-pen is unused.
ARROW_RADII = (0, 10, 15, 20, 25)
# The historical tables are intentional: they differ from modern rounded
# sine/tangent calculations at several entries. See the specification.
ARROW_SINES = (
    0, 1144, 2287, 3430, 4572, 5712, 6850, 7987, 9121, 10252,
    11380, 12505, 13626, 14742, 15854, 16962, 18064, 19161, 20252, 21336,
    22415, 23486, 24550, 25607, 26656, 27697, 28729, 29753, 30767, 31772,
    32768, 33754, 34729, 35693, 36647, 37590, 38521, 39441, 40348, 41243,
    42126, 42995, 43852, 44695, 45525, 46341, 47143, 47930, 48703, 49461,
    50203, 50931, 51643, 52339, 53020, 53684, 54332, 54963, 55578, 56175,
    56756, 57319, 57865, 58393, 58903, 59396, 59870, 60326, 60764, 61183,
    61584, 61966, 62328, 62672, 62997, 63303, 63589, 63856, 64104, 64332,
    64540, 64729, 64898, 65048, 65177, 65287, 65376, 65446, 65496, 65526,
    65536,
)
ANGLE_SLOPES = (
    0, 1144, 2289, 3435, 4583, 5734, 6888, 8047, 9210, 10380,
    11556, 12739, 13930, 15130, 16340, 17560, 18792, 20036, 21294, 22566,
    23853, 25157, 26478, 27818, 29179, 30560, 31964, 33392, 34846, 36327,
    37837, 39378, 40951, 42560, 44205, 45889, 47615, 49385, 51202, 53070,
    54991, 56970, 59009, 61113, 63287, 65536, 67865, 70279, 72785, 75391,
    78103, 80930, 83882, 86969, 90203, 93595, 97161, 100917, 104879, 109070,
    113512, 118230, 123255, 128622, 134369, 140542, 147196, 154393, 162207, 170727,
    180059, 190330, 201699, 214358, 228551, 244584, 262850, 283867, 308322, 337153,
    371673, 413777, 466312, 533747, 623533, 749079, 937205, 1250493, 1876695, 3754544,
    2147483647,
)


def signed16(value):
    return (value+32768) % 65536-32768


def signed32(value):
    return (value+2147483648) % 4294967296-2147483648


def fixed_sine(angle):
    angle %= 360
    sign = -1 if angle > 180 else 1
    if angle > 180:
        angle -= 180
    if angle > 90:
        angle = 180-angle
    return sign*ARROW_SINES[angle]


def fixed_ratio(numer, denom):
    if not denom:
        return -2147483648 if numer < 0 else 2147483647
    value = (abs(numer)*65536)//abs(denom)
    if (numer < 0) != (denom < 0):
        value = -value
    return max(-2147483648,min(2147483647,value))


def fixed_multiply(a, b):
    return max(-2147483648,min(2147483647,(a*b+32768)//65536))


def quickdraw_angle(rect, point):
    """Original integer PtToAngle slope thresholds, including its 500 bias."""
    t,l,b,r = rect
    x,y = point
    dx = signed16(x-(signed16(l+r)//2))
    dy = signed16(y-(signed16(t+b)//2))
    if dx == 0:
        return 180 if dy > 0 else 0
    slope = fixed_multiply(fixed_ratio(dx,dy),fixed_ratio(signed16(b-t),signed16(r-l)))
    threshold = signed32(abs(slope)-500)
    angle = next(i for i,value in enumerate(ANGLE_SLOPES) if value >= threshold)
    if slope >= 0:
        angle = 180-angle
    if dx < 0:
        angle += 180
    return angle % 360


def arrow_geometry(a, b, width_index, flags, revision=6):
    """Return native PaintArc heads and MoveTo/LineTo pen-origin endpoints.

    Coordinates are rounded from file Fixed values as in the original loader's
    draw path. The SVG caller converts square-pen origins to stroke centers.
    """
    if revision not in (4, 6):
        raise FormatError('unsupported arrow drawing revision')
    if not 1 <= width_index <= 5 or flags & ~3:
        raise FormatError('invalid arrow pen selection or flags')
    if width_index == 1:
        return [], None
    def fixed_to_word(value):
        # 0.9's local FIXROUND rounds negative ties away from zero; 1.x
        # adds 0x8000 then takes HiWord, rounding ties toward +infinity.
        if revision == 4 and value < 0:
            return signed16(-((abs(value)+32768)//65536))
        return signed16((value+32768)//65536)
    def rounded(point):
        return tuple(fixed_to_word(int(v*65536)) for v in point)
    a,b = rounded(a),rounded(b)
    original_b = b
    radius = ARROW_RADII[width_index-1]
    dx,dy = signed16(b[0]-a[0]),signed16(b[1]-a[1])
    def absolute_word(n):
        return signed16(-n) if n < 0 else n
    heads = []
    def head(tip, other):
        x,y = tip
        rect = tuple(map(signed16,(y-radius,x-radius,y+radius,x+radius)))
        angle = quickdraw_angle(rect,other)
        t,l,bb,r = rect
        # MacDraw 1.x moves only the painted sector one unit right. The
        # 0.9 routine paints the original rectangle without this correction.
        shift = 1 if revision == 6 else 0
        heads.append(((t,signed16(l+shift),bb,signed16(r+shift)),angle-24))
        # Shorten against the unshifted circle inset by two units. Keep the
        # fixed-point arithmetic and integer rounding of the native helper.
        t,l,bb,r = map(signed16,(t+2,l+2,bb-2,r-2))
        cx = macDrawText.trunc(signed32((l+r)*65536),2)
        cy = macDrawText.trunc(signed32((t+bb)*65536),2)
        rx,ry = signed32(cx-l*65536),signed32(cy-t*65536)
        xx = signed32(cx+fixed_multiply(rx,fixed_sine(angle)))
        yy = signed32(cy+fixed_multiply(ry,fixed_sine(angle-90)))
        return fixed_to_word(xx),fixed_to_word(yy)
    if flags and (absolute_word(dx) > radius or absolute_word(dy) > radius):
        if flags & 1:
            b = head(b,a)
        if flags & 2:
            a = head(a,original_b)
    half = PEN_WIDTHS[width_index-1]//2
    shaft = tuple(tuple(signed16(c-half) for c in point) for point in (a,b))
    return heads,shaft


def number(n):
    # All fixed-point source coordinates are dyadic and exactly representable.
    return str(int(n)) if n == int(n) else str(n)


def element(parent, tag, **attributes):
    return ET.SubElement(parent, "{"+SVG+"}"+tag,
                         {key.replace("_", "-"): str(value) for key, value in attributes.items()})


def png_bitmap(o):
    """Cropped 1-bit PNG: white transparent, black opaque (native srcOr)."""
    f = o.fields
    t, l, b, r = f["source_rect"]
    bt, bl, _, _ = f["bitmap_bounds"]
    w, h = r-l, b-t
    raw = bytearray()
    for y in range(t, b):
        row = bytearray((w+7)//8)
        for x in range(w):
            source_x = l+x-bl
            black = (f["bitmap"][(y-bt)*f["row_bytes"]+source_x//8] >> (7-source_x%8)) & 1
            if black:
                row[x//8] |= 128 >> (x%8)
        raw.append(0)
        raw.extend(row)
    def chunk(kind, data):
        return struct.pack(">I", len(data))+kind+data+struct.pack(">I", zlib.crc32(kind+data))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">2I5B", w, h, 1, 3, 0, 0, 0))
            + chunk(b"PLTE", b"\xff\xff\xff\x00\x00\x00")
            + chunk(b"tRNS", b"\x00\xff")
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))+chunk(b"IEND", b""))


class Renderer:
    """Deterministic research preview; unresolved decisions are explicit issues."""
    def __init__(self, doc, layer=None):
        self.doc = doc
        self.layer = layer
        self.root = ET.Element("{"+SVG+"}svg", {"version": "1.1"})
        self.defs = element(self.root, "defs")
        self.patterns = set()
        self.bounds = []

    def paint(self, index):
        if index <= 3:
            return ("none", "white", "black")[index-1]
        ident = f"pattern{index}"
        if index not in self.patterns:
            self.patterns.add(index)
            table = PATTERNS_4 if self.doc.revision == 4 else PATTERNS_6
            rows = bytes.fromhex(table[index-2])
            pat = element(self.defs, "pattern", id=ident, width=8, height=8,
                          patternUnits="userSpaceOnUse")
            element(pat, "rect", width=8, height=8, fill="white")
            path = " ".join(f"M{x} {y}h1v1h-1z" for y, row in enumerate(rows)
                            for x in range(8) if row & (128 >> x))
            element(pat, "path", d=path, fill="black", shape_rendering="crispEdges")
        return f"url(#{ident})"

    def attributes(self, o):
        _, _, width, pen, fill, _ = o.attrs
        return dict(stroke=self.paint(pen) if width > 1 else "none", fill=self.paint(fill),
                    stroke_width=PEN_WIDTHS[width-1],
                    stroke_linejoin="round", stroke_linecap="square", fill_rule="evenodd")

    def add_bounds(self, box, padding=4):
        t, l, b, r = box
        self.bounds.append((min(l,r)-padding, min(t,b)-padding,
                            max(l,r)+padding, max(t,b)+padding))

    def draw(self, parent, o):
        f, k = o.fields, o.kind
        if f.get("native_pict"):
            import macDrawPICT
            return macDrawPICT.render(self, parent, o)
        if f.get("native_pro"):
            import macDrawPro
            return macDrawPro.render(self, parent, o)
        if f.get("native2"):
            import macDrawII
            return macDrawII.render(self, parent, o)
        group = element(parent, "g", id=f"object-{o.offset:x}", data_macdraw_type=k,
                        data_source_offset=o.offset)
        if k == 10:
            for child in o.children:
                self.draw(group, child)
            return
        t, l, b, r = f["box"]
        if k != 1 or "text_layout" not in f:
            self.add_bounds(f["box"])
        attrs = self.attributes(o)
        if k == 1:
            self.text(group, o)
        elif k in (2, 3):
            attrs["fill"] = "none"
            opt = o.attrs[-1]
            if opt:
                self.arrow_line(group, (l,t), (r,b), o.attrs[2], opt, attrs)
            else:
                element(group, "line", x1=number(l), y1=number(t), x2=number(r), y2=number(b), **attrs)
        elif k in (4, 5):
            if r < l or b < t:
                return  # An inverted QuickDraw rectangle is empty.
            if k == 5:
                unit = self.doc.header["ruler_units"]
                if o.attrs[-1] == 1:
                    diameter = 0
                elif unit in CORNER_DIAMETERS:
                    diameter = CORNER_DIAMETERS[unit][o.attrs[-1]-1]
                else:
                    # Only the explicitly requested preview reaches this case.
                    diameter = (o.attrs[-1]+1)*9
                attrs.update(rx=number(min(diameter/2, (r-l)/2)),
                             ry=number(min(diameter/2, (b-t)/2)))
            element(group, "rect", x=number(l), y=number(t), width=number(r-l), height=number(b-t), **attrs)
        elif k == 6:
            if r < l or b < t:
                return
            element(group, "ellipse", cx=number((l+r)/2), cy=number((t+b)/2),
                    rx=number((r-l)/2), ry=number((b-t)/2), **attrs)
        elif k == 7:
            self.arc(group, o, attrs)
        elif k in (8, 9):
            element(group, "path", d=self.polygon(f), **attrs)
        elif k == 11:
            if r <= l or b <= t:
                return
            href = "data:image/png;base64,"+base64.b64encode(png_bitmap(o)).decode("ascii")
            im = element(group, "image", x=number(l), y=number(t), width=number(r-l), height=number(b-t),
                         preserveAspectRatio="none", image_rendering="pixelated")
            im.set("{"+XLINK+"}href", href)

    def arrow_line(self, parent, a, b, width_index, flags, attrs):
        if attrs["stroke"] == "none":
            return
        heads,shaft = arrow_geometry(a,b,width_index,flags,self.doc.revision)
        for box,angle in heads:
            t,l,bb,r = box
            if r <= l or bb <= t:
                continue
            cx,cy,rx,ry = (l+r)/2,(t+bb)/2,(r-l)/2,(bb-t)/2
            def point(degrees):
                radians = math.radians(degrees)
                return cx+rx*math.sin(radians),cy-ry*math.cos(radians)
            x,y = point(angle); xx,yy = point(angle+48)
            path = (f"M{number(cx)} {number(cy)} L{number(x)} {number(y)} "
                    f"A{number(rx)} {number(ry)} 0 0 1 {number(xx)} {number(yy)} Z")
            element(parent,"path",d=path,fill=attrs["stroke"],stroke="none",data_arrow_head="true")
            # Sector extrema are its tip, end points, and included cardinals.
            extrema = [(cx,cy),(x,y),(xx,yy)]
            extrema += [point(a) for a in (0,90,180,270) if (a-angle)%360 <= 48]
            xs,ys = zip(*extrema)
            self.add_bounds((min(ys),min(xs),max(ys),max(xs)))
        if shaft is not None:
            # QuickDraw positions the top-left of its rectangular pen.
            half = PEN_WIDTHS[width_index-1]/2
            (x,y),(xx,yy) = [(x+half,y+half) for x,y in shaft]
            element(parent,"line",x1=number(x),y1=number(y),x2=number(xx),y2=number(yy),**attrs)
            self.add_bounds((min(y,yy),min(x,xx),max(y,yy),max(x,xx)))

    def arc(self, parent, o, attrs):
        f = o.fields
        t,l,b,r = f["box"]
        rx,ry = (r-l)/2,(b-t)/2
        if rx <= 0 or ry <= 0 or f["sweep_angle"] == 0:
            return
        cx,cy = (l+r)/2,(t+b)/2
        start, sweep = f["start_angle"], f["sweep_angle"]
        if abs(sweep) >= 360:
            element(parent, "ellipse", cx=number(cx), cy=number(cy), rx=number(rx), ry=number(ry), **attrs)
            return
        def pt(angle):
            rad = math.radians(angle)
            return cx+rx*math.sin(rad), cy-ry*math.cos(rad)
        x,y = pt(start)
        xx,yy = pt(start+sweep)
        path = f"M{number(x)} {number(y)} A{number(rx)} {number(ry)} 0 {int(abs(sweep)>180)} {int(sweep>0)} {number(xx)} {number(yy)}"
        if attrs["fill"] != "none":
            filled = dict(attrs, stroke="none")
            element(parent, "path", d=path+f" L{number(cx)} {number(cy)} Z", **filled)
        # QuickDraw fills the sector but frames only its elliptical edge.
        element(parent, "path", d=path, **dict(attrs, fill="none"))

    @staticmethod
    def polygon(f):
        pts = f["points"]
        if f["smooth"] and len(pts) >= 3:
            fixed = [(int(x*65536), int(y*65536)) for x,y in pts]
            pts = [(x/65536, y/65536)
                   for x,y in spline_vertices(fixed, f["closed"])]
        path = "M"+number(pts[0][0])+" "+number(pts[0][1])
        path += " "+" ".join("L"+number(x)+" "+number(y) for x,y in pts[1:])
        return path+(" Z" if f["closed"] else "")

    def text(self, parent, o):
        if "text_layout" in o.fields:
            self.resource_text(parent, o)
            return
        if not o.fields["text_bytes"] and o.attrs[4] == 1:
            return
        self.preview_text(parent, o)

    def resource_text(self, parent, o):
        f = o.fields
        layout = f["text_layout"]
        metrics = layout.metrics
        box = layout.box
        t,l,b,r = box
        code = f["transform"]
        corners = [macDrawText.transform_point(x,y,box,code)
                   for x,y in ((l,t),(r,t),(r,b),(l,b))]
        xs,ys = zip(*corners)
        self.add_bounds((min(ys),min(xs),max(ys),max(xs)))
        # EraseRect's BackPat is anchored in destination coordinates, even
        # when the text is rotated. Text itself always uses black foreground.
        fill = self.paint(o.attrs[4])
        if fill != "none":
            element(parent, "rect", x=number(min(xs)), y=number(min(ys)),
                    width=number(max(xs)-min(xs)), height=number(max(ys)-min(ys)), fill=fill)
        group = element(parent, "g", data_font_family=f["font_id"],
                        data_font_menu_index=f["font_index"],
                        data_rendered_font_family=metrics.strike.family,
                        data_font_substituted=str(macDrawText.is_substituted(f["font_id"], metrics.strike.family)).lower(),
                        data_font_size=metrics.size, data_font_strike=metrics.strike.size,
                        data_font_sha256=metrics.strike.digest)
        element(group, "title").text = f["text_bytes"].decode("mac_roman")
        if code:
            a,bb,c,d = macDrawText.TRANSFORMS[code]
            cx,cy = (l+r)/2,(t+b)/2
            group.set("transform", f"matrix({a} {bb} {c} {d} {number(cx-a*cx-c*cy)} {number(cy-bb*cx-d*cy)})")
        scale = metrics.numer/256
        chunk_size = 13 if metrics.shadow or code else 34
        if not hasattr(self, "text_chunks"):
            self.text_chunks = {}
        for x,y,chars in layout.lines:
            for i in range(0,len(chars),chunk_size):
                chunk = chars[i:i+chunk_size]
                black,white = metrics.pixels(chunk)
                if code:
                    # Rotated/reflected text is painted into a clear bitmap
                    # and copied with srcOr: white interiors are transparent.
                    white = frozenset()
                if black or white:
                    key = (metrics.strike.digest,metrics.face,chunk,bool(code))
                    if key not in self.text_chunks:
                        ident = "text-chunk-"+str(len(self.text_chunks))
                        definition = element(self.defs, "g", id=ident,
                                             shape_rendering="crispEdges")
                        if white:
                            element(definition,"path",d=macDrawText.pixel_path(white),fill="white")
                        if black:
                            element(definition,"path",d=macDrawText.pixel_path(black),fill="black")
                        self.text_chunks[key] = ident
                    target = group
                    translation = f"translate({number(x)} {number(y)})"
                    if code:
                        clip_id = f"text-clip-{o.offset:x}-{i}-{y}"
                        clip = element(self.defs,"clipPath",id=clip_id)
                        element(clip,"rect",x=0,y=-metrics.ascent,
                                width=max(0,metrics.width(chunk)),height=metrics.ascent+metrics.descent)
                        target = element(group,"g",transform=translation,clip_path=f"url(#{clip_id})")
                        translation = ""
                    use = element(target,"use",transform=f"{translation} scale({number(scale)})".strip())
                    use.set("{"+XLINK+"}href", "#"+self.text_chunks[key])
                    pixels = black | white
                    px = [p[0] for p in pixels]; py = [p[1] for p in pixels]
                    ink_corners = [macDrawText.transform_point(x+xx*scale,y+yy*scale,box,code)
                                   for xx,yy in ((min(px),min(py)),(max(px)+1,min(py)),
                                                 (max(px)+1,max(py)+1),(min(px),max(py)+1))]
                    ix,iy = zip(*ink_corners)
                    self.add_bounds((min(iy),min(ix),max(iy),max(ix)))
                x += metrics.width(chunk)

    def preview_text(self, parent, o):
        f=o.fields
        t,l,b,r=f["box"]
        size=FONT_SIZES[f["size_index"]-1]
        family,fallback=FONT_NAMES.get(f["font_id"], (f"Macintosh font {f['font_id']}","sans-serif"))
        # The preview intentionally delegates font metrics to SVG's consumer.
        raw=f["text_bytes"].decode("mac_roman")
        lines=raw.replace("\r\n","\r").replace("\n","\r").split("\r")
        align=f["align"]&3
        x=(l, (l+r)/2, r)[align-1]
        anchor=("start","middle","end")[align-1]
        face=f["face"]
        attrs=dict(font_family=f"'{family}', {fallback}", font_size=size,
                   fill="black", text_anchor=anchor, dominant_baseline="text-before-edge")
        if len(lines) == 1 and lines[0] and r > l:
            attrs.update(textLength=number(r-l), lengthAdjust="spacingAndGlyphs")
        if face & 1:attrs["font_weight"]="bold"
        if face & 2:attrs["font_style"]="italic"
        if face & 4:attrs["text_decoration"]="underline"
        if face & 8:attrs.update(fill="white",stroke="black",stroke_width="0.6",paint_order="stroke fill")
        if face & 32:attrs["letter_spacing"]="-1"
        if face & 64:attrs["letter_spacing"]="1"
        if f["transform"]:
            cx,cy=(l+r)/2,(t+b)/2
            a,bb,c,d = macDrawText.TRANSFORMS[f["transform"]]
            parent.set("transform", f"matrix({a} {bb} {c} {d} {number(cx-a*cx-c*cy)} {number(cy-bb*cx-d*cy)})")
        # Rect height supplies line box height only when lines are explicitly
        # present. No font-size guessing or content-dependent font selection.
        step=(b-t)/len(lines) if b>t else size*1.2*(1,1.5,2)[f["spacing"]-1]
        for i,line in enumerate(lines):
            if face & 16:
                shadow=element(parent,"text",x=number(x+1),y=number(t+i*step+1),**attrs)
                shadow.set("{"+"http://www.w3.org/XML/1998/namespace"+"}space","preserve")
                shadow.text=line.expandtabs(8)
            text=element(parent,"text",x=number(x),y=number(t+i*step),**attrs)
            text.set("{"+"http://www.w3.org/XML/1998/namespace"+"}space","preserve")
            text.text=line.expandtabs(8)

    def render(self):
        title=element(self.root,"title")
        title.text=("MacDraw recovered drawing — damaged or incomplete source" if self.doc.recovered else
                    "MacDraw research preview — fidelity is not certified"
                    if self.doc.issues else "MacDraw drawing")
        desc=element(self.root,"desc")
        desc.text=("Recovered from the original damaged source. Missing objects or substituted fields are recorded in metadata."
                   if self.doc.recovered else
                   "This preview contains documented approximations. See metadata for unresolved fields."
                   if self.doc.issues else "SVG of the supported MacDraw drawing subset. "
                   "Full printer/editor metadata semantics are not established.")
        meta=element(self.root,"metadata")
        # Preserve the entire source separately from claims about its meaning.
        audit = self.doc.audit()
        meta.text=json.dumps(dict(format=("MacDraw recovered SVG" if self.doc.recovered else
                                         "MacDraw research preview" if self.doc.issues else "MacDraw SVG"), revision=self.doc.revision,
                                  conversion_status=audit["conversion_status"],
                                  native_format=audit['native_format'],
                                  layers=audit['layers'], selected_layer=self.layer,
                                  recovery_events=audit["recovery_events"],
                                  omitted_byte_ranges=audit["omitted_byte_ranges"],
                                  full_format_semantics_established=False,
                                  metadata_limitations=audit["metadata_limitations"],
                                  inactive_suffix=audit["inactive_suffix"],
                                  text_environment=audit["text_environment"],
                                  font_resources=audit["font_resources"],
                                  font_substitutions=audit["font_substitutions"],
                                  original_font_menu=audit["original_font_menu"],
                                  input_container=audit["input_container"],
                                  drawing_resources=audit["drawing_resources"],
                                  picture=audit["picture"],
                                  external_resource_fork=audit["external_resource_fork"],
                                  issues=[i.as_dict() for i in self.doc.issues],
                                  source_zlib_base64=base64.b64encode(zlib.compress(self.doc.data,9)).decode("ascii")),
                             ensure_ascii=True, separators=(",",":"))
        content=element(self.root,"g")
        for o in self.doc.objects:self.draw(content,o)
        if self.doc.header.get('picture'):
            y,x,bottom,right=self.doc.header['picture']['frame']
        elif self.bounds:
            x=min(b[0] for b in self.bounds);y=min(b[1] for b in self.bounds)
            right=max(b[2] for b in self.bounds);bottom=max(b[3] for b in self.bounds)
        else:x,y,right,bottom=0,0,576,720
        width,height=max(1,right-x),max(1,bottom-y)
        self.root.set("viewBox"," ".join(number(n) for n in (x,y,width,height)))
        # Display one drawing unit as one CSS pixel. Bitmap glyphs request
        # crisp edges independently of the continuous vector geometry.
        self.root.set("width",number(width)+"px")
        self.root.set("height",number(height)+"px")
        self.root.set("style","background:white")
        # Explicit white background also works in renderers ignoring root CSS.
        bg=ET.Element("{"+SVG+"}rect",dict(x=number(x),y=number(y),width=number(width),height=number(height),fill="white"))
        self.root.insert(list(self.root).index(content),bg)
        return b'<?xml version="1.0" encoding="UTF-8"?>\n<!-- Vibe coded by Codex -->\n'+ET.tostring(self.root,encoding="utf-8")+b"\n"


def parse_document(data, *, require_complete=False, fonts=None, recover=False, resource_fork=None):
    doc = Parser(data, require_complete=require_complete, fonts=fonts, recover=recover, resource_fork=resource_fork).parse()
    if resource_fork is not None:
        if doc.header.get('native_format') != 'MacDraw Pro':
            raise FormatError('--resource-fork is supported only for native MacDraw Pro drawings')
        doc.header['external_resource_fork'] = dict(bytes=len(resource_fork),
            sha256=hashlib.sha256(resource_fork).hexdigest(),
            source_zlib_base64=base64.b64encode(zlib.compress(resource_fork,9)).decode('ascii'))
    return doc


def render_svg(document, *, preview=False, recover=False, layer=None):
    if not preview and not recover:
        document.require_complete()
    if layer is not None and (document.header.get('native_format') not in ('MacDraw II','MacDraw Pro') or
                              not 1 <= layer <= len(document.header['layers'])):
        raise FormatError('layer selection requires a valid one-based MacDraw II/Pro layer number')
    return Renderer(document, layer=layer).render()


def write_atomic(path, data):
    """Validate/render before calling. Never truncate a destination on failure."""
    path=Path(path)
    temp=None
    try:
        with tempfile.NamedTemporaryFile(prefix=".macDraw-",dir=path.parent,delete=False) as out:
            temp=out.name
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
            os.fchmod(out.fileno(),0o664)
        os.replace(temp,path)
        temp=None
    finally:
        if temp is not None:
            os.unlink(temp)


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("inputFile",type=Path)
    ap.add_argument("outputFile",type=Path)
    ap.add_argument("--layer",type=int,help="render only this one-based MacDraw II/Pro layer, including a saved hidden layer")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--strict", action="store_true", help="reject damage and unsupported drawing semantics without writing")
    mode.add_argument("--preview",action="store_true",help="legacy preview: permit drawing approximations, but reject damaged framing")
    ap.add_argument("--font-resource", action="append", type=Path, default=[],
                    help="add/override original FONT/NFNT/FOND resources (raw resource fork or AppleDouble); repeatable")
    ap.add_argument("--resource-fork", type=Path, help="MacDraw Pro drawing resource fork (raw fork or AppleDouble); MacBinary resources are read automatically")
    ap.add_argument("--font-menu", type=Path,
                    help="original MacDraw 0.9 menu order as a documented JSON family-ID list")
    args=ap.parse_args(argv)
    try:
        if args.inputFile.resolve()==args.outputFile.resolve():
            raise FormatError("input and output must be different files")
        if args.outputFile.exists() and os.path.samefile(args.inputFile,args.outputFile):
            raise FormatError("input and output are aliases of the same file")
        if args.resource_fork and (args.resource_fork.resolve()==args.outputFile.resolve() or
                (args.outputFile.exists() and os.path.samefile(args.resource_fork,args.outputFile))):
            raise FormatError("resource input and output must be different files")
        fonts = None
        if args.font_resource or args.font_menu:
            fonts = macDrawText.FontBook()
            for path in args.font_resource:
                fonts.load_resource(path)
            if args.font_menu:
                fonts.load_menu(args.font_menu)
        recover = not (args.strict or args.preview)
        doc=parse_document(args.inputFile.read_bytes(),require_complete=args.strict,fonts=fonts,recover=recover,
                           resource_fork=args.resource_fork.read_bytes() if args.resource_fork else None)
        svg=render_svg(doc,preview=args.preview,recover=recover,layer=args.layer)
        write_atomic(args.outputFile,svg)
        if args.preview:
            print("Research preview only; unresolved: "+", ".join(sorted({i.code for i in doc.issues})),file=sys.stderr)
        elif doc.issues:
            print("macDraw: wrote "+("recovered" if doc.recovered else "approximate")+
                  f" SVG with {sum(o.count for o in doc.objects)} retained objects; "
                  "see SVG metadata for limitations: "+", ".join(sorted({i.code for i in doc.issues})),file=sys.stderr)
    except (FormatError,macDrawText.FontError,OSError,OverflowError,RecursionError,MemoryError) as e:
        print(f"macDraw: {e}",file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    sys.exit(main())
