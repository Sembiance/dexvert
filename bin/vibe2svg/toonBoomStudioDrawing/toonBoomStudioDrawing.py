#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert a Toon Boom Studio .tbd vector drawing to an SVG file.

Usage: python3 toonBoomStudioDrawing.py inputFile outputFile

Standalone Python 3.10+ implementation using only the standard library. Handles
observed drawing revisions 25, 27, 30, 31 and 51; rejects .tbp project headers.
Outputs editable vector paths and gradients with a transparent background. No
rasterizer, FFmpeg, or companion Python file is required. Only the SVG is left
by default; -verbose also writes outputFile.json with the decoded byte map.

The drawing grammar and rendering interpretation match the drawing subset of
toonBoomStudioAnimation.py. Some editor/style flags remain unresolved, and exact
native rendering fidelity is unverified; see toonBoomStudioAnimation.txt for the
research limitations. Neither companion file is needed to run this converter.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
import os
from pathlib import Path
import struct
import sys
import tempfile
import xml.etree.ElementTree as ET

SIGNATURE = b'ToonBoomTechnologiesInc \x00'
VERSIONS = {25, 27, 30, 31, 51}
MAX_COUNT = 1_000_000
MAX_INPUT = 256 * 1024 * 1024


class FormatError(Exception):
    """Recognized input cannot be decoded safely."""


class NotThisFormat(FormatError):
    pass


class Unsupported(FormatError):
    pass


class Malformed(FormatError):
    pass


def identify(data):
    if not data.startswith(SIGNATURE):
        raise NotThisFormat('Not a Toon Boom Studio serialized document (signature mismatch).')
    if len(data) < 32:
        raise Malformed('Truncated Toon Boom header.')
    version_text = data[25:28]
    if version_text[-1:] != b'\x00' or not version_text[:2].isdigit():
        raise Unsupported('Unrecognized Toon Boom serialization revision.')
    version = int(version_text[:2])
    kind = struct.unpack_from('<I', data, 28)[0]
    if version not in VERSIONS:
        raise Unsupported(f'Toon Boom revision {version} is not implemented.')
    if kind == 0:
        raise Unsupported('Project files (.tbp) are not supported; supply a vector drawing (.tbd).')
    if kind != 1:
        raise Unsupported(f'Toon Boom document kind {kind} is not a vector drawing.')
    return version, kind


class Reader:
    """Bounded, sequential reader. Verbose traces cover fields, never scan for tags."""
    def __init__(self, data, trace=False):
        self.data = data
        self.version, self.kind = identify(data)
        self.pos = 0
        self.trace = [] if trace else None
        self.warnings = []
        self.objects = [None]
        self.nodes = []
        self.colors = {}
        self.fields = Counter()
        self.blob(25, 'signature')
        self.blob(3, 'revision')
        self.get('I', 'document_kind')
        if self.version >= 51:
            self.header_flags = self.get('B', 'header_flags_unresolved')

    def record(self, start, label, encoding, value):
        if self.trace is not None:
            self.trace.append(dict(offset=start, length=self.pos-start, field=label,
                                   encoding=encoding, value=value))

    def blob(self, size, label):
        if size < 0 or size > len(self.data) - self.pos:
            raise Malformed(f'{label}: truncated at byte {self.pos}; need {size} bytes.')
        start = self.pos
        self.pos += size
        value = self.data[start:self.pos]
        self.record(start, label, 'bytes', value.hex())
        return value

    def get(self, fmt, label):
        size = struct.calcsize('<' + fmt)
        if size > len(self.data) - self.pos:
            raise Malformed(f'{label}: truncated at byte {self.pos}; need {size} bytes.')
        start = self.pos
        values = struct.unpack_from('<' + fmt, self.data, start)
        self.pos += size
        value = values[0] if len(values) == 1 else values
        self.record(start, label, '<' + fmt, value)
        if any(isinstance(x, float) and (not math.isfinite(x) or abs(x) > 1e15)
               for x in values):
            raise Malformed(f'{label}: non-finite or excessive coordinate at byte {start}.')
        return value

    def count(self, label, minimum=1, fmt='I'):
        n = self.get(fmt, label)
        if n > MAX_COUNT or n * minimum > len(self.data) - self.pos:
            raise Malformed(f'{label}: count {n} exceeds remaining input at byte {self.pos}.')
        return n

    def expect(self, fmt, expected, label):
        start = self.pos
        actual = self.get(fmt, label)
        if actual != expected:
            raise Unsupported(f'{label} at byte {start}: expected {expected}, found {actual}.')

    def string(self, label):
        width = 2 if self.version >= 51 else 1
        n = self.count(label + '.length', width)
        raw = self.blob(n * width, label + '.text')
        try:
            return raw.decode('utf-16le' if width == 2 else 'latin1')
        except UnicodeDecodeError as exc:
            raise Malformed(f'{label}: invalid UTF-16 at byte {self.pos-len(raw)}.') from exc

    def tag(self, number, legacy, label):
        if self.version == 25:
            if self.string(label) != legacy:
                raise Unsupported(f'{label}: unknown class name at byte {self.pos}.')
        else:
            self.expect('H', number, label)

    def fill(self):
        is_new = self.get('H', 'fill.is_new')
        if is_new == 0:
            ref = self.get('I', 'fill.object_reference')
            if ref >= len(self.objects) or (ref and not isinstance(self.objects[ref], dict)):
                raise Malformed(f'Invalid fill reference {ref} at byte {self.pos-4}.')
            return self.objects[ref]
        if is_new != 1:
            raise Unsupported(f'Unknown fill record {is_new} at byte {self.pos-2}.')
        self.tag(205, 'GR_Color', 'fill.class')
        mode = self.get('B', 'fill.transform_enabled') if self.version >= 51 else 1
        if mode not in (0, 1):
            raise Unsupported(f'Unknown fill transform flag {mode}.')
        matrix = self.get('6d' if self.version >= 51 else '4d', 'fill.transform')
        uid = self.get('Q', 'fill.color_id')
        fill = dict(matrix=matrix, color=uid, transform_enabled=mode)
        self.objects.append(fill)
        return fill

    def edge(self):
        mode = self.get('B', 'edge.style')
        if mode not in (0, 1, 2, 4):
            raise Unsupported(f'Edge style {mode} is not implemented.')
        width = self.get('f', 'edge.width')
        color = self.get('Q', 'edge.stroke_color_id')
        left, right = self.fill(), self.fill()
        flags = self.get('2B', 'edge.endpoint_flags_unresolved') if self.version >= 30 else (0, 0)
        if any(x not in (0, 1) for x in flags):
            raise Unsupported(f'Unknown edge endpoint flags {flags}.')
        reference = self.get('B', 'edge.geometry_is_reference') if self.version >= 51 else 0
        if reference == 1:
            index = self.get('I', 'edge.geometry_reference')
            if index >= len(self.objects) or not isinstance(self.objects[index], tuple):
                raise Malformed(f'Invalid geometry reference {index}.')
            mask, points = self.objects[index]
        elif reference == 0:
            n = self.count('edge.point_count', 8, 'H')
            mask = self.blob((n + 7) // 8, 'edge.on_curve_bitmap')
            points = tuple(self.get('2f', 'edge.point') for _ in range(n))
            if self.version >= 51:
                self.objects.append((mask, points))
        else:
            raise Unsupported(f'Unknown geometry storage code {reference}.')
        if points:
            on = [i for i in range(len(points)) if mask[i // 8] >> (i % 8) & 1]
            if not on or on[0] != 0 or on[-1] != len(points)-1:
                raise Malformed('A curve does not start and end on an on-curve point.')
            if any(b-a not in (1, 2, 3) for a, b in zip(on, on[1:])):
                raise Unsupported('Curve with more than two consecutive control points.')
        if width < 0:
            raise Malformed('Negative stroke width.')
        self.fields['edges'] += 1
        self.fields['points_including_references'] += len(points)
        return dict(mode=mode, width=width, color=color, left=left, right=right,
                    flags=flags, points=points, mask=mask)

    def node(self):
        if self.version == 25:
            self.objects = [None]
            self.tag(0, 'Layer', 'layer.class')
        if self.version >= 51:
            self.expect('I', 2, 'node.type')
            self.expect('B', 1, 'node.flag_unresolved')
            self.get('H', 'node.attribute_unresolved')
        else:
            self.get('I', 'layer.index')
        n = self.count('node.edge_count', 27)
        edges = [self.edge() for _ in range(n)]
        if self.version >= 51:
            self.expect('I', 0, 'node.children_count')
        self.fields['nodes'] += 1
        return edges

    def color_definition(self, expected_uid=None):
        self.tag(121, 'CM_Color', 'color.class')
        mode = self.get('I', 'color.type')
        if mode not in (0, 1, 2):
            raise Unsupported(f'Color type {mode} (texture or other paint) is not implemented.')
        self.get('I', 'color.attribute_0_unresolved')
        self.get('I', 'color.attribute_1_unresolved')
        n = self.count('color.stop_count', 16)
        stops = tuple(self.get('d4BI', 'color.stop_position_rgba_editor_id') for _ in range(n))
        if not stops or any(s[0] < 0 or s[0] > 1 for s in stops):
            raise Malformed('Empty gradient or invalid gradient stop position.')
        if any(a[0] > b[0] for a, b in zip(stops, stops[1:])):
            raise Malformed('Gradient stop positions are not ordered.')
        name = self.string('color.name')
        uid = self.get('Q', 'color.id')
        if expected_uid is not None and expected_uid != uid:
            raise Malformed('Palette entry key does not match its color identifier.')
        self.fields['colors'] += 1
        return uid, dict(type=mode, stops=stops, name=name)

    def drawing(self):
        self.tag(202, 'VectorDrawingObj', 'drawing.class')
        if self.version >= 51:
            self.get('B', 'drawing.attribute_unresolved')
            present = self.get('B', 'drawing.has_art')
            blocks = self.count('drawing.art_count', 4)
            if present not in (0, 1) or bool(blocks) != bool(present):
                raise Malformed('Inconsistent drawing art count and presence flag.')
            if blocks > 1:
                raise Unsupported('Multiple drawing art collections are not implemented.')
        else:
            blocks = 1
        for _ in range(blocks):
            for _ in range(self.count('drawing.node_count', 8)):
                self.nodes.append(self.node())
        self.geometry_end = self.pos
        # An art-less revision 51 document ends immediately, with no palette.
        if not blocks:
            if self.pos != len(self.data):
                raise Unsupported('Unexpected bytes after an empty drawing.')
            return self
        try:
            n = self.count('drawing.palette_count', 1)
            for _ in range(n):
                uid = self.get('Q', 'drawing.palette_key')
                uid, definition = self.color_definition(uid)
                self.colors[uid] = definition
        except Malformed as exc:
            if not self.colors:
                raise
            self.warnings.append(f'Partial palette recovery: {exc}')
        if self.pos != len(self.data) and not self.warnings:
            raise Unsupported(f'{len(self.data)-self.pos} unimplemented trailing bytes at {self.pos}.')
        return self


def read_drawing(path, verbose=False):
    """Check the drawing header before reading the body or creating any output."""
    with open(path, 'rb') as stream:
        identify(stream.read(33))
        stream.seek(0, os.SEEK_END)
        if stream.tell() > MAX_INPUT:
            raise Unsupported('Input exceeds the 256 MiB resource limit.')
        stream.seek(0)
        data = stream.read()
    return Reader(data, trace=verbose).drawing()


def curve_commands(edge, reverse=False):
    """Keep original line, quadratic and cubic geometry as SVG L, Q and C."""
    points, mask = edge['points'], edge['mask']
    if not points:
        return []
    on_curve = [i for i in range(len(points)) if mask[i // 8] >> (i % 8) & 1]
    commands = [('M', points[0])]
    for a, b in zip(on_curve, on_curve[1:]):
        if b-a == 1:
            commands.append(('L', points[b]))
        elif b-a == 2:
            commands.append(('Q', points[a+1] + points[b]))
        else:
            commands.append(('C', points[a+1] + points[a+2] + points[b]))
    if reverse:
        reversed_segments, previous = [], points[0]
        for command, values in commands[1:]:
            if command == 'L':
                reversed_segments.append(('L', previous))
            elif command == 'Q':
                reversed_segments.append(('Q', values[:2] + previous))
            else:
                reversed_segments.append(('C', values[2:4] + values[:2] + previous))
            previous = values[-2:]
        commands = [('M', previous)] + reversed_segments[::-1]
    return commands


def prepare_drawing(doc):
    """Reconstruct fills by exact directed-edge connectivity, with no snapping."""
    layers, missing = [], set()
    for node in doc.nodes:
        groups, strokes = {}, []
        for edge in node:
            for side, reverse in (('left', False), ('right', True)):
                fill = edge[side]
                if fill is None or not edge['points']:
                    continue
                if fill['color'] not in doc.colors:
                    missing.add(fill['color'])
                    continue
                key = (fill['color'], fill['matrix'])
                groups.setdefault(key, (fill, []))[1].append(curve_commands(edge, reverse))
            if edge['mode'] == 4 and edge['points']:
                if edge['color'] not in doc.colors:
                    missing.add(edge['color'])
                else:
                    strokes.append((edge, curve_commands(edge)))
        fills = []
        for fill, segments in groups.values():
            graph, balance = defaultdict(list), Counter()
            for commands in segments:
                first, last = commands[0][1], commands[-1][1][-2:]
                graph[first].append(commands)
                balance[first] += 1
                balance[last] -= 1
            if any(balance.values()):
                raise Malformed('Fill boundaries do not join exactly; refusing coordinate guessing.')
            contours = []
            while graph:
                start = current = next(iter(graph))
                contour = []
                while current in graph:
                    commands = graph[current].pop()
                    if not graph[current]:
                        del graph[current]
                    contour.extend(commands if not contour else commands[1:])
                    current = commands[-1][1][-2:]
                    if current == start:
                        break
                if current != start:
                    raise Malformed('Open fill contour.')
                contours.append(contour)
            fills.append((fill, contours))
        layers.append((fills, strokes))
    if missing:
        doc.warnings.append('Missing palette colors; omitted affected artwork: ' +
                            ', '.join(f'{uid:016x}' for uid in sorted(missing)))
        if not any(fills or strokes for fills, strokes in layers):
            raise Malformed('No artwork can be recovered with the available palette.')
    return layers


def number(value):
    """Round-trip finite coordinates; do not quantize the source geometry."""
    if not math.isfinite(value):
        raise Malformed('Non-finite value in SVG geometry.')
    if value == 0:
        return '0'
    if float(value).is_integer():
        return str(int(value))
    return repr(float(value))


def path_data(commands):
    return ' '.join(command + ' ' + ' '.join(number(x) for x in values)
                    for command, values in commands)


def quadratic_roots(a, b, c):
    """Real roots, using a stable formula for the cubic-extrema calculation."""
    if a == 0:
        return (-c/b,) if b else ()
    discriminant = b*b - 4*a*c
    if discriminant < 0:
        return ()
    q = -0.5 * (b + math.copysign(math.sqrt(discriminant), b))
    return (q/a, c/q) if q else (-b/(2*a),)


def path_bounds(commands):
    """Compute extrema of the Bezier segments, not a sampled approximation."""
    xs, ys = [], []
    current = None

    def include(point):
        xs.append(point[0])
        ys.append(point[1])

    for command, values in commands:
        endpoint = values[-2:]
        include(endpoint)
        if command == 'Q':
            control = values[:2]
            for axis in (0, 1):
                denominator = current[axis] - 2*control[axis] + endpoint[axis]
                if denominator:
                    t = (current[axis]-control[axis]) / denominator
                    if 0 < t < 1:
                        s = 1-t
                        include(tuple(s*s*current[i] + 2*s*t*control[i] + t*t*endpoint[i]
                                      for i in (0, 1)))
        elif command == 'C':
            c1, c2 = values[:2], values[2:4]
            for axis in (0, 1):
                p0, p1, p2, p3 = current[axis], c1[axis], c2[axis], endpoint[axis]
                for t in quadratic_roots(-p0+3*p1-3*p2+p3,
                                         2*(p0-2*p1+p2), p1-p0):
                    if 0 < t < 1:
                        s = 1-t
                        include(tuple(s*s*s*current[i] + 3*s*s*t*c1[i] +
                                      3*s*t*t*c2[i] + t*t*t*endpoint[i] for i in (0, 1)))
        current = endpoint
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def drawing_viewbox(layers):
    bounds = []
    for fills, strokes in layers:
        for _, contours in fills:
            bounds.extend(path_bounds(contour) for contour in contours)
        for edge, commands in strokes:
            box = path_bounds(commands)
            if box is not None:
                half_width = edge['width']/2
                bounds.append((box[0]-half_width, box[1]-half_width,
                               box[2]+half_width, box[3]+half_width))
    bounds = [box for box in bounds if box is not None]
    if not bounds:
        return (0, 0, 1, 1)
    x0, y0 = min(b[0] for b in bounds), min(b[1] for b in bounds)
    x1, y1 = max(b[2] for b in bounds), max(b[3] for b in bounds)
    # A drawing has no stored viewport. Add a documented 1% presentation margin.
    span = max(x1-x0, y1-y0)
    margin = span/100 if span else 0.5
    return (x0-margin, -y1-margin, x1-x0+2*margin, y1-y0+2*margin)


SVG_NAMESPACE = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG_NAMESPACE)


def svg_element(parent, tag, attributes=None):
    return ET.SubElement(parent, '{' + SVG_NAMESPACE + '}' + tag, attributes or {})


def affine_matrix(fill):
    matrix = fill['matrix']
    if len(matrix) == 4:
        x0, y0, x1, y1 = matrix
        a, b = x1-x0, y1-y0
        matrix = (a, b, -b, a, x0, y0)
    if matrix[0]*matrix[3] - matrix[1]*matrix[2] == 0:
        raise Malformed('Singular gradient transformation.')
    return matrix


def svg_document(doc, *, width=640, height=480):
    """Return a self-contained SVG: native paths and gradients, no bitmap assets."""
    layers = prepare_drawing(doc)
    viewbox = drawing_viewbox(layers)
    root = ET.Element('{' + SVG_NAMESPACE + '}svg', {
        'version': '1.1', 'width': str(width), 'height': str(height),
        'viewBox': ' '.join(number(x) for x in viewbox),
        'preserveAspectRatio': 'xMidYMid meet', 'color-interpolation': 'sRGB',
    })
    definitions = svg_element(root, 'defs')
    drawing = svg_element(root, 'g', {
        'transform': 'scale(1 -1)', 'fill-rule': 'nonzero',
        'stroke-linecap': 'round', 'stroke-linejoin': 'round',
    })
    gradients = {}
    paths = 0

    def paint_attributes(fill, attribute):
        color = doc.colors[fill['color']]
        stops = color['stops']
        if color['type'] == 0:
            _, red, green, blue, alpha, _ = stops[0]
            attrs = {attribute: f'#{red:02x}{green:02x}{blue:02x}'}
            if alpha != 255:
                attrs[attribute + '-opacity'] = number(alpha/255)
            return attrs
        matrix = affine_matrix(fill)
        key = (fill['color'], matrix)
        if key not in gradients:
            gradient_id = f'gradient-{len(gradients)+1}'
            gradients[key] = gradient_id
            attrs = {
                'id': gradient_id, 'gradientUnits': 'userSpaceOnUse',
                'gradientTransform': 'matrix(' + ' '.join(number(x) for x in matrix) + ')',
                'spreadMethod': 'pad', 'color-interpolation': 'sRGB',
            }
            if color['type'] == 1:
                attrs.update(x1='0', y1='0', x2='1', y2='0')
                gradient = svg_element(definitions, 'linearGradient', attrs)
            elif color['type'] == 2:
                attrs.update(cx='0', cy='0', r='1', fx='0', fy='0')
                gradient = svg_element(definitions, 'radialGradient', attrs)
            else:
                raise Unsupported(f'Unsupported SVG paint type {color["type"]}.')
            for position, red, green, blue, alpha, _ in stops:
                attrs = {'offset': number(position), 'stop-color': f'#{red:02x}{green:02x}{blue:02x}'}
                if alpha != 255:
                    attrs['stop-opacity'] = number(alpha/255)
                svg_element(gradient, 'stop', attrs)
        return {attribute: f'url(#{gradients[key]})'}

    for index, (fills, strokes) in enumerate(layers, 1):
        layer = svg_element(drawing, 'g', {'id': f'layer-{index}'})
        for fill, contours in fills:
            attrs = {'d': ' '.join(path_data(contour) + ' Z' for contour in contours)}
            attrs.update(paint_attributes(fill, 'fill'))
            svg_element(layer, 'path', attrs)
            paths += 1
        for edge, commands in strokes:
            attrs = {'d': path_data(commands), 'fill': 'none', 'stroke-width': number(edge['width'])}
            attrs.update(paint_attributes({'color': edge['color'], 'matrix': (1, 0, 0, 1, 0, 0)}, 'stroke'))
            svg_element(layer, 'path', attrs)
            paths += 1
    if not len(definitions):
        root.remove(definitions)
    ET.indent(root, space='  ')
    data = (b'<?xml version="1.0" encoding="UTF-8"?>\n'
            b'<!-- Vibe coded by Codex -->\n' + ET.tostring(root, encoding='utf-8') + b'\n')
    return data, dict(paths=paths, gradients=len(gradients), viewBox=viewbox)


def atomic_write(path, data):
    """Preserve an existing destination on failure and leave no temporary files."""
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        os.chmod(temporary, 0o664)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def convert(input_file, output_file, *, verbose=False, width=640, height=480):
    source, output = Path(input_file), Path(output_file)
    if source.resolve() == output.resolve():
        raise FormatError('Input and output must be different files.')
    if not (isinstance(width, int) and isinstance(height, int) and
            1 <= width <= 8192 and 1 <= height <= 8192):
        raise FormatError('SVG viewport dimensions must be integers from 1 to 8192.')
    if verbose and Path(str(output) + '.json').resolve() == source.resolve():
        raise FormatError('The verbose sidecar path would overwrite the input file.')
    doc = read_drawing(source, verbose)
    data, svg_stats = svg_document(doc, width=width, height=height)
    result = dict(input=str(source), output=str(output), version=doc.version,
                  bytes=len(doc.data), parsed_to=doc.pos, width=width, height=height,
                  warnings=doc.warnings, statistics=dict(doc.fields), **svg_stats)
    if verbose:
        result['fields'] = doc.trace
        # Serialize before committing output so serialization failures are harmless.
        trace_data = (json.dumps(result, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
    atomic_write(output, data)
    if verbose:
        atomic_write(Path(str(output) + '.json'), trace_data)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputFile', type=Path)
    parser.add_argument('outputFile', type=Path)
    parser.add_argument('-verbose', '--verbose', action='store_true',
                        help='also write outputFile.json with the decoded byte map')
    parser.add_argument('--width', type=int, default=640, help='SVG viewport width (default 640)')
    parser.add_argument('--height', type=int, default=480, help='SVG viewport height (default 480)')
    args = parser.parse_args(argv)
    try:
        result = convert(args.inputFile, args.outputFile, verbose=args.verbose,
                         width=args.width, height=args.height)
    except (FormatError, OSError, ValueError) as exc:
        print(f'toonBoomStudioDrawing: {exc}', file=sys.stderr)
        return 1
    for warning in result['warnings']:
        print('Warning: ' + warning, file=sys.stderr)
    if args.verbose:
        print(f'Revision {result["version"]}: {result["paths"]} SVG paths, '
              f'{result["gradients"]} gradients; {result["parsed_to"]}/{result["bytes"]} bytes parsed.',
              file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
