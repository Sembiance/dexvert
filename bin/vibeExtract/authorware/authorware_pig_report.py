#!/usr/bin/env python3
# Vibe coded by Codex
"""Self-contained, dark review pages for all extracted Authorware resources.

Usage: python3 authorware_pig_report.py --output report/a5p-review sample/a5p
"""

import argparse
import base64
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
from html import escape
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

import authorware
from authorware_pig import dib_png


OUTPUT_KINDS = (('pigs', 'PIGs'), ('animations', 'Animations'), ('cursors', 'Cursors'),
                ('images', 'Images'), ('text', 'Text files'), ('sounds', 'Sounds'),
                ('videos', 'Videos'), ('other', 'Other files'))


def output_counts(pictures, assets):
    """Count each exported file once; image subtypes have separate columns."""
    counts = dict.fromkeys((key for key, _ in OUTPUT_KINDS), 0)
    represented = {p['file'] for p in pictures if p.get('file')}
    counts['pigs'] = len(represented)
    for asset in assets:
        name = asset['name']
        if name in represented:
            continue
        represented.add(name)
        kind = asset['kind']
        if kind == 'image':
            if 'cursor_id' in asset:
                category = 'cursors'
            elif 'frames' in asset or name.lower().endswith('.apng'):
                category = 'animations'
            else:
                category = 'images'
        else:
            category = {'audio': 'sounds', 'video': 'videos', 'text': 'text'}.get(kind, 'other')
        counts[category] += 1
    counts['total'] = sum(counts.values())
    return counts


def saved_output_counts(directory, item):
    """Read old report metadata without re-extracting its source or rewriting it.

    Early reports contain only PIG previews. Their other output counts are
    unknown, not zero. Preserve that distinction in both the HTML and inventory.
    """
    unknown = dict.fromkeys([key for key, _ in OUTPUT_KINDS] + ['total'])
    if not item.get('page'):
        return unknown
    try:
        html = (Path(directory) / item['page']).read_text(encoding='utf-8')
        payload = json.loads(html.split('<script id="payload" type="application/json">', 1)[1].split('</script>', 1)[0])
    except (OSError, ValueError, IndexError):
        return unknown
    if 'assets' in payload:
        return output_counts(payload.get('pictures', []), payload['assets'])
    # Those older pages embed one SVG URL per rendered PIG, but omit its
    # filename from the payload. Unrendered PIG records are not output files.
    unknown['pigs'] = html.count('data:image/svg+xml;base64,')
    return unknown


def data_url(mime, content):
    return 'data:' + mime + ';base64,' + base64.b64encode(content).decode('ascii')


def compressed_wav_preview(content):
    """Decode MS/IMA ADPCM for browser playback; retain the download unchanged."""
    if content[:4] != b'RIFF' or content[8:12] != b'WAVE':
        return None, None
    offset = 12
    while offset + 8 <= len(content):
        length = int.from_bytes(content[offset + 4:offset + 8], 'little')
        end = offset + 8 + length
        if end > len(content):
            return None, None
        if content[offset:offset + 4] == b'fmt ':
            # Do not feed arbitrary reused codec tags (notably Voxware's
            # 0x0062, which FFmpeg treats as DK3) to the wrong decoder.
            if (length >= 22 and content[offset + 8:offset + 10] == b'\x62\0'
                    and content[offset + 26:offset + 30] == b'VOX.'):
                return None, 'Voxware audio retained in its original WAV; no browser-playable conversion is available in this extractor'
            if length < 16 or int.from_bytes(content[offset + 8:offset + 10], 'little') not in (2, 17):
                return None, None
            break
        offset = end + (length & 1)
    else:
        return None, None
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        return None, 'Audio preview needs FFmpeg to decode this compressed WAV'
    try:
        with tempfile.TemporaryDirectory(prefix='authorware-audio-preview-') as temporary:
            output = Path(temporary) / 'preview.wav'
            result = subprocess.run([ffmpeg, '-nostdin', '-v', 'error', '-xerror', '-f', 'wav',
                                     '-i', 'pipe:0', '-map', '0:a:0', '-c:a', 'pcm_s16le', str(output)],
                                    input=content, capture_output=True, timeout=30)
            if result.returncode or not output.is_file():
                return None, 'Audio preview could not be decoded; original WAV is available to download'
            return output.read_bytes(), None
    except (OSError, subprocess.TimeoutExpired):
        return None, 'Audio preview could not be decoded; original WAV is available to download'


def collect_assets(directory, names, pictures, dibs=None, cursors=(), animations=()):
    """Read only this extraction's outputs; imported .bin files stay opaque."""
    represented = {p.get('file') for p in pictures}
    pig_info = {p['raw_file']: p for p in pictures if p.get('raw_file')}
    if dibs is None:
        dibs = []
        for name in names:
            if name.startswith('dib_manifest') and name.endswith('.json'):
                manifest = json.loads((Path(directory) / name).read_text())
                dibs.extend(manifest['dibs'])
    dib_info = {item['raw_file']: item for item in dibs if item.get('raw_file')}
    cursor_info = {item['file']: item for item in cursors}
    cursor_originals = {item['raw_file'] for item in cursors if item.get('raw_file')}
    animation_info = {item['file']: item for item in animations if item.get('file')}
    images = {'.bmp': 'image/bmp', '.png': 'image/png', '.jpg': 'image/jpeg',
              '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.svg': 'image/svg+xml', '.apng': 'image/png'}
    sounds = {'.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg',
              '.flac': 'audio/flac', '.aiff': 'audio/aiff', '.aif': 'audio/aiff',
              '.m4a': 'audio/mp4', '.aac': 'audio/aac'}
    videos = {'.mp4': 'video/mp4', '.webm': 'video/webm', '.mov': 'video/quicktime'}
    assets = []
    for name in sorted(names):
        if name in represented:
            continue
        path = Path(directory) / name
        content = path.read_bytes()
        suffix = path.suffix.lower()
        mime = images.get(suffix) or sounds.get(suffix) or videos.get(suffix) or 'application/octet-stream'
        item = {'name': name, 'bytes': len(content), 'url': data_url(mime, content), 'kind': 'file'}
        if name in dib_info:
            info = dib_info[name]
            item['handling'] = info.get('reason', 'Standalone BMP exported; original DIB bytes retained')
            item['rendered_by'] = info.get('rendered_by', [])
        elif name in pig_info:
            picture = pig_info[name]
            item['handling'] = picture.get('raw_reason', 'Original PIG bytes retained')
            if picture.get('file'):
                item['rendered_by'] = [{'id': picture['id'], 'index': picture['index'], 'file': picture['file']}]
        elif name in cursor_originals:
            item['handling'] = 'Original cursor table retained by --deep; cursors exported as PNG'
        if suffix in images:
            item['kind'] = 'image'
            item['preview'] = item['url']
            if name in animation_info:
                animation = animation_info[name]
                item.update(width=animation['width'], height=animation['height'],
                            frames=animation['frames'], stored_rate=animation['stored_rate'],
                            playback_rate=animation.get('playback_rate', animation['stored_rate']),
                            rate_source=animation.get('rate_source', 'cached'),
                            entry_id=animation['id'], entry_index=animation['index'],
                            status=animation['status'], warning=' '.join(animation['warnings']))
            if name in cursor_info:
                cursor = cursor_info[name]
                item.update(width=cursor['width'], height=cursor['height'],
                            cursor_id=cursor['cursor_id'], entry_id=cursor['id'], entry_index=cursor['index'])
                if cursor['inverting_pixels']:
                    item['warning'] = (f'{cursor["inverting_pixels"]} background-inverting pixels rendered black; '
                                       'PNG cannot invert the background')
            if suffix == '.bmp':
                try:
                    png, width, height = dib_png(authorware, content[14:])
                    item.update(preview=data_url('image/png', png), width=width, height=height)
                except (ValueError, IndexError, OverflowError) as exc:
                    item['warning'] = 'Bitmap preview unavailable: ' + str(exc)
        elif suffix in sounds:
            item['kind'] = 'audio'
            if suffix == '.wav':
                preview, warning = compressed_wav_preview(content)
                if preview is not None:
                    item['preview'] = data_url('audio/wav', preview)
                if warning:
                    item['warning'] = warning
        elif suffix in videos:
            item['kind'] = 'video'
        elif suffix in ('.txt', '.json', '.xml', '.csv') and not name.startswith(('pig_manifest', 'dib_manifest')):
            item.update(kind='text', text=content.decode('utf-8', errors='replace'))
        else:
            item['hex'] = content[:32].hex(' ')
        assets.append(item)
    return assets


def asset_sections(assets, picture_anchors=None):
    """Native media players and sandboxed text frames need no page scripts."""
    sections, links = [], []
    for kind, title in (('image', 'Extracted images'), ('audio', 'Sounds'),
                        ('video', 'Videos'), ('text', 'Text'), ('file', 'Other files')):
        items = [item for item in assets if item['kind'] == kind]
        if not items:
            continue
        section_id = 'assets-' + kind
        links.append('<a href="#' + section_id + '">' + title + ' (' + str(len(items)) + ')</a>')
        cards = []
        for number, item in enumerate(items, 1):
            filename = escape(item['name'])
            download = '<a download="' + escape(item['name'], quote=True) + '" href="' + item['url'] + '">' + filename + '</a>'
            label = '<h3>' + download + '</h3>'
            size = '<p class="meta">' + f'{item["bytes"]:,}' + ' bytes</p>'
            if 'frames' in item:
                rate = item.get('playback_rate', item['stored_rate'])
                rate_label = 'authored rate' if item.get('rate_source') == 'authored' else 'cached fallback'
                size = ('<p class="meta">' + f'{item["frames"]} frames · {item["width"]} × {item["height"]}'
                        + f' · {rate} fps ({rate_label})</p>' + size)
            style = ''
            if kind == 'image':
                dimensions = ''
                if item.get('width') and item.get('height'):
                    dimensions = f' width="{item["width"]}" height="{item["height"]}"'
                    style = f' style="--picture-width:{item["width"] + 2}px"'
                body = '<div class="art"><img loading="lazy" decoding="async"' + dimensions + ' src="' + item['preview'] + '" alt="' + escape(item['name'], quote=True) + '"></div>'
            elif kind in ('audio', 'video'):
                body = '<' + kind + ' controls preload="metadata" src="' + item.get('preview', item['url']) + '"></' + kind + '>'
            elif kind == 'text':
                document = '<!doctype html><!-- Vibe coded by Codex --><html lang="en"><meta charset="utf-8"><style>:root{color-scheme:dark}body{margin:10px;background:#111923;color:#e7eef8;font:13px/1.5 monospace}pre{white-space:pre-wrap;overflow-wrap:anywhere;margin:0}</style><pre>' + escape(item['text']) + '</pre></html>'
                body = '<iframe loading="lazy" sandbox="" title="' + escape(item['name'], quote=True) + '" srcdoc="' + escape(document, quote=True) + '"></iframe>'
            else:
                handling = ''
                if item.get('handling'):
                    handling = '<p class="meta">' + escape(item['handling'])
                    references = []
                    for reference in item.get('rendered_by', []):
                        label = 'PIG ' + str(reference['id']) + ' (index ' + str(reference['index']) + ')'
                        anchor = (picture_anchors or {}).get(reference['file'])
                        references.append('<a href="#' + anchor + '">' + escape(label) + '</a>' if anchor else escape(label))
                    if references:
                        handling += ': ' + ', '.join(references)
                    handling += '</p>'
                cards.append('<tr><td>' + download + handling + '</td><td>' + f'{item["bytes"]:,}' + '</td><td><code>' + escape(item.get('hex', '')) + '</code></td></tr>')
                continue
            warning = '<p class="warning">' + escape(item['warning']) + '</p>' if item.get('warning') else ''
            cards.append('<article class="asset ' + kind + '" id="' + section_id + '-' + str(number) + '"' + style + '>' + label + body + size + warning + '</article>')
        content = '<div class="grid">' + ''.join(cards) + '</div>'
        if kind == 'file':
            content = '<div class="file-list"><table><thead><tr><th>File (download)</th><th>Bytes</th><th>First 32 bytes</th></tr></thead><tbody>' + ''.join(cards) + '</tbody></table></div>'
        sections.append('<section id="' + section_id + '"><h2 class="section-title">' + title + ' · ' + str(len(items)) + '</h2>' + content + '</section>')
    return ''.join(sections), links


def report_html(source, source_hash, pictures, assets=(), notice=''):
    """Show every picture in document order on one self-contained scrollable page."""
    counts = output_counts(pictures, assets)
    totals = f'{counts["total"]:,} extracted files'
    totals += ' · ' + ' · '.join(f'{counts[key]:,} {label.lower() if key != "pigs" else label}'
                                for key, label in OUTPUT_KINDS if counts[key]) if counts['total'] else ''
    cards = []
    for number, picture in enumerate(pictures):
        entry_id = str(picture.get('id', number))
        index = str(picture.get('index', number))
        anchor = 'picture-' + str(number + 1)
        label = 'Entry ' + entry_id + ' · table index ' + index
        status = picture.get('status', 'unrendered')
        bounds = picture.get('bounds')
        dimensions = ''
        size = ''
        card_size = ''
        if bounds and len(bounds) == 4:
            width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
            if width > 0 and height > 0:
                size = f' width="{int(width)}" height="{int(height)}"'
                card_size = f' style="--picture-width:{int(width) + 2}px"'
                dimensions = f'{width} × {height}'
        svg = picture.get('svg')
        if svg and svg.startswith('data:image/svg+xml;base64,'):
            title = 'Open ' + picture.get('file', 'SVG for ' + label)
            art = ('<div class="art"><a class="svg-link" href="#' + anchor + '" target="_blank" rel="noopener" title="' + escape(title, quote=True) + '">'
                   '<img loading="lazy" decoding="async"' + size + ' src="' + escape(svg, quote=True) + '" alt="' + escape(label, quote=True) + '"></a></div>')
        else:
            art = '<p class="missing">No renderable picture recovered.</p>'
        warnings = ''.join('<p class="warning">' + escape(str(w)) + '</p>' for w in picture.get('warnings', []))
        caption = dimensions if status == 'converted' else str(status) + (' · ' + dimensions if dimensions else '')
        cards.append('<section class="picture" id="' + anchor + '"' + card_size + '><h2><a href="#' + anchor + '">Entry ' + escape(entry_id) + '<span class="entry-index">index ' + escape(index) + '</span></a></h2>' + art + '<p class="meta">' + escape(caption) + '</p>' + warnings + '</section>')
    other_sections, links = asset_sections(assets, {p.get('file'): 'picture-' + str(i + 1) for i, p in enumerate(pictures)})
    if pictures:
        links.insert(0, '<a href="#pig-pictures">PIG pictures (' + str(len(pictures)) + ')</a>')
    navigation = '<nav>' + ' · '.join(links) + '</nav>'
    notice_html = '<p class="warning">' + escape(notice) + '</p>' if notice else ''
    if any('frames' in asset for asset in assets):
        notice_html += ('<p class="muted">APNG animations repeat the full stored sequence. '
                        'Playback uses the authored rate when readable, otherwise a cached fallback; '
                        'runtime scripts and synchronization are not replayed.</p>')
    # Keep diagnostic metadata without duplicating the embedded image data.
    data = {'source': str(source), 'sha256': source_hash,
            'pictures': [{k: v for k, v in p.items() if k != 'svg'} for p in pictures],
            'assets': [{k: v for k, v in a.items() if k not in ('url', 'preview', 'text')} for a in assets]}
    encoded = json.dumps(data, ensure_ascii=True).replace('<', '\\u003c')
    return '''<!doctype html>
<!-- Vibe coded by Codex -->
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Authorware extraction review — ''' + escape(Path(source).name) + '''</title>
<style>
:root{color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:#10151d;color:#e7eef8;font:14px/1.4 system-ui,sans-serif}header,footer{padding:16px;overflow-wrap:anywhere}header{background:#17202d;border-bottom:1px solid #354258}h1{font-size:23px;margin:0 0 6px}p{margin:6px 0}a{color:#84caff}.muted,.meta,.entry-index,footer{color:#aebed2}main{width:100%}.grid{display:flex;flex-wrap:wrap;align-items:flex-start;gap:12px;padding:16px;width:100%}.picture{flex:0 1 auto;width:max(100px,var(--picture-width,200px));max-width:100%;min-width:0;margin:0;border:1px solid #354258;border-radius:6px;background:#1b2432;overflow:hidden;scroll-margin-top:12px}h2{font-size:13px;font-weight:600;margin:0;padding:6px 8px;overflow-wrap:anywhere}h2 a{display:block;text-decoration:none}h2 a:hover{text-decoration:underline}.entry-index{display:block;font-size:11px;font-weight:400}.meta{font-size:11px;font-weight:400;padding:4px 8px;margin:0;overflow-wrap:anywhere}.art{width:fit-content;max-width:100%;margin:0 auto;background-color:#eee;background-image:conic-gradient(#ddd 25%,transparent 0 50%,#ddd 0 75%,transparent 0);background-size:20px 20px}.art img{display:block;max-width:100%;height:auto}.warning,.missing{padding:6px 8px;overflow-wrap:anywhere;font-size:12px}.warning{color:#ffd087}.missing{color:#aebed2}footer{font-size:12px;border-top:1px solid #354258}
nav{margin-top:10px}.section-title{font-size:18px;padding:18px 16px 0;margin:0}.asset{width:340px;max-width:100%;min-width:0;border:1px solid #354258;border-radius:6px;background:#1b2432;overflow:hidden}.asset.image{width:max(120px,var(--picture-width,240px))}.asset.text{width:420px}.asset.video{width:480px}.asset h3{font-size:12px;line-height:1.4;margin:0;padding:8px;overflow-wrap:anywhere}.asset audio,.asset video{display:block;width:100%;max-width:100%}.asset iframe{display:block;border:0;border-top:1px solid #354258;width:100%;height:170px;background:#111923}.file-list{padding:16px}table{border-collapse:collapse;width:100%;table-layout:fixed}th,td{text-align:left;vertical-align:top;border-bottom:1px solid #354258;padding:8px;overflow-wrap:anywhere}th:nth-child(1){width:35%}th:nth-child(2){width:12%}td code{font-size:11px}
</style>
<header><h1>Authorware extraction review</h1><p>''' + escape(str(source)) + '''</p><p class="muted">''' + escape(totals) + '''</p>
<p>Scroll through all extracted content. Report problems by entry number or filename. Click a picture to open its SVG in a new tab; click other filenames to download the extracted file.</p>
<p class="muted">Each image keeps its original dimensions when it fits the window. The checkerboard marks transparency within the image. Original fonts may be substituted.</p>''' + notice_html + navigation + '''</header>
<main>''' + ('<section id="pig-pictures"><h2 class="section-title">PIG pictures · ' + str(len(pictures)) + '</h2><div class="grid">' + ''.join(cards) + '</div></section>' if cards else '') + other_sections + ('' if cards or assets else '<p class="missing">No extracted content recovered.</p>') + '''</main>
<footer>Source SHA-256: <code>''' + escape(str(source_hash)) + '''</code></footer>
<script id="payload" type="application/json">''' + encoded + '''</script>
<script>
// Vibe coded by Codex
// Blob links open embedded SVGs offline without blocked data-URL navigation
// or a second copy of every SVG in the HTML.
for (const link of document.querySelectorAll('.svg-link')) {
    const encoded = link.querySelector('img').getAttribute('src').split(',')[1];
    const bytes = Uint8Array.from(atob(encoded), character => character.charCodeAt(0));
    link.href = URL.createObjectURL(new Blob([bytes], {type: 'image/svg+xml'}));
}
</script></html>'''


def review_file(task):
    """Extract only the requested source, then embed every output in its page."""
    source, output = map(Path, task)
    start = time.monotonic()
    summary = {'source': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
    name = re_safe_name(source.name) + '-' + hashlib.sha256(str(source).encode()).hexdigest()[:10] + '.html'
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='authorware-report-') as temporary:
        directory = Path(temporary)
        result = subprocess.run([sys.executable, str(Path(authorware.__file__).resolve()),
                                 str(source), str(directory), '--report'], capture_output=True, text=True)
        notice = result.stderr.strip() if result.returncode else ''
        if result.returncode and not notice:
            notice = f'Extractor exited with status {result.returncode}'
        report = directory / 'pig-report.html'
        if report.exists():
            # The extractor builds its page from in-memory results, including
            # partial/unrendered pictures. No manifest files are needed.
            payload = json.loads(report.read_text(encoding='utf-8').split(
                '<script id="payload" type="application/json">', 1)[1].split('</script>', 1)[0])
            pictures, assets = payload['pictures'], payload['assets']
            shutil.copyfile(report, output / name)
        else:
            # Early failures (such as a missing entry table) can still leave
            # recovered files, even though normal report generation was skipped.
            pictures = []
            assets = collect_assets(directory, [p.name for p in directory.iterdir() if p.is_file()], pictures)
            (output / name).write_text(report_html(str(source), summary['sha256'], pictures, assets, notice), encoding='utf-8')
    summary.update(page=name, pictures=len(pictures), statuses=dict(Counter(p['status'] for p in pictures)),
                   assets=dict(Counter(a['kind'] for a in assets)),
                   output_counts=output_counts(pictures, assets),
                   warnings=dict(Counter(w for p in pictures for w in p['warnings'])),
                   exit_code=result.returncode, seconds=round(time.monotonic()-start, 2))
    if notice:
        summary['error'] = notice
    return summary


def re_safe_name(name):
    import re
    return re.sub(r'[^A-Za-z0-9._-]+', '_', name)[:90]


def write_index(output, summaries):
    output = Path(output)
    summaries = [dict(item, output_counts=item.get('output_counts') or saved_output_counts(output, item))
                 for item in summaries]
    columns = OUTPUT_KINDS + (('total', 'Total'),)
    known_totals = {key: sum(item['output_counts'].get(key) or 0 for item in summaries)
                    for key, _ in OUTPUT_KINDS}
    recorded_outputs = sum(known_totals.values())
    incomplete = any(item['output_counts']['total'] is None for item in summaries)
    output_label = 'recorded outputs' if incomplete else 'extracted files'
    count_note = ('Some older reports only recorded PIG previews. Their missing counts are shown as —; totals below include recorded outputs only.'
                  if incomplete else 'Counts are exported files. Images exclude PIGs, animations and cursors; text includes scripts.')
    stats = ''.join('<div class="stat"><strong>' + f'{known_totals[key]:,}' + '</strong><span>'
                    + label + '</span></div>' for key, label in OUTPUT_KINDS)
    groups = {}
    for item in sorted(summaries, key=lambda row: row['source']):
        source = Path(item['source'])
        if source.is_absolute():
            try:
                source = source.relative_to(Path.cwd())
            except ValueError:
                pass
        # Keep a sample family together; show deeper archive folders in each row.
        folder = source.parent
        if not source.is_absolute():
            folder = Path(*folder.parts[:2])
        groups.setdefault(str(folder), []).append((item, source.relative_to(folder)))

    navigation, sections = [], []
    for group_number, (folder, items) in enumerate(groups.items()):
        group_id = f'folder-{group_number}'
        navigation.append(f'<a href="#{group_id}">{escape(folder)} '
                          f'<span class="folder-count">{len(items):,}</span></a>')
        rows = []
        for item, relative_source in items:
            label = escape(str(relative_source))
            if item.get('page'):
                label = '<a href="' + escape(item['page'], quote=True) + '">' + label + '</a>'
            counts = item['output_counts']
            search = escape(item['source'] + ' ' + item.get('error', ''), quote=True)
            cells = ''.join('<td' + (' class="unknown" title="Not recorded in this older report"' if counts.get(key) is None else '')
                            + '>' + ('—' if counts.get(key) is None else f'{counts[key]:,}') + '</td>'
                            for key, _ in columns)
            rows.append(f'<tr data-search="{search}"><th scope="row">{label}</th>'
                        + cells +
                        f'<td class="issue">{escape(item.get("error", ""))}</td></tr>')
        group_outputs = sum(sum(item['output_counts'].get(key) or 0 for key, _ in OUTPUT_KINDS) for item, _ in items)
        group_partial = any(item['output_counts']['total'] is None for item, _ in items)
        group_label = 'recorded outputs' if group_partial else 'extracted files'
        headers = ''.join('<th scope="col">' + label + '</th>' for _, label in columns)
        sections.append(
            f'<section class="source-group" id="{group_id}"><div class="group-heading">'
            f'<h2>{escape(folder)}</h2><p><span class="group-count">{len(items):,} {"file" if len(items) == 1 else "files"}</span>'
            f' · {group_outputs:,} {group_label}</p><a class="back-top" href="#top">Back to folders ↑</a></div>'
            '<div class="table-scroll"><table><colgroup><col class="source-col">'
            f'<col span="{len(columns)}" class="count-col"><col class="issue-col"></colgroup>'
            f'<thead><tr><th scope="col">File within {escape(folder)}</th>'
            + headers + '<th scope="col">Input issue</th></tr></thead>'
            '<tbody>' + ''.join(rows) + '</tbody></table></div></section>')

    page = '''<!doctype html>
<!-- Vibe coded by Codex -->
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Authorware review reports</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}[hidden]{display:none!important}
body{background:#10151d;color:#e7eef8;font:15px/1.5 system-ui;margin:0;padding:28px clamp(16px,3vw,48px)}
a{color:#84caff;text-decoration:none}a:hover{text-decoration:underline}a:focus-visible,input:focus-visible{outline:2px solid #84caff;outline-offset:3px}
h1{margin:0 0 8px;font-size:28px}header>p{color:#b7c5d8;max-width:1000px;margin:8px 0}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:20px 0}.stat{background:#182230;border:1px solid #354258;border-radius:6px;padding:12px 16px}.stat strong{display:block;font-size:23px;font-variant-numeric:tabular-nums}.stat span{color:#b7c5d8;font-size:13px}.unknown{color:#718298}
.toolbar{display:flex;align-items:center;gap:20px;flex-wrap:wrap;margin:24px 0 18px}
input{padding:12px 14px;width:420px;max-width:100%;background:#182230;color:#e7eef8;border:1px solid #506078;border-radius:6px;font:inherit}
input::placeholder{color:#a9b8cc}.toolbar p{margin:0;color:#b7c5d8}
.folder-nav{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:30px}
.folder-nav a{display:inline-flex;align-items:center;gap:12px;padding:8px 12px;border:1px solid #354258;border-radius:6px;background:#182230}
.folder-nav a:hover{background:#243248;text-decoration:none;border-color:#84caff}.folder-count{color:#bccade;font-size:12px}
.source-group{margin-bottom:32px;scroll-margin-top:16px;border:1px solid #354258;border-radius:8px;overflow:hidden}
.group-heading{display:flex;align-items:baseline;flex-wrap:wrap;gap:8px 20px;padding:16px 18px;background:#1c2a3c}
h2{margin:0;font-size:20px;overflow-wrap:anywhere}.group-heading p{margin:0;color:#b7c5d8;font-size:13px}.back-top{margin-left:auto;font-size:13px;white-space:nowrap}
.table-scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;table-layout:fixed;min-width:1100px}
.source-col{width:25%}.count-col{width:7%}.issue-col{width:12%}th,td{text-align:right;padding:10px 8px;border-bottom:1px solid #293548;vertical-align:top;font-variant-numeric:tabular-nums}
thead th{background:#151f2c;color:#b7c5d8;font-size:12px;font-weight:600}th:first-child,th:last-child,td.issue{text-align:left}
tbody th{font-weight:400;overflow-wrap:anywhere}tbody tr:last-child>*{border-bottom:0}tbody tr:hover{background:#1b2738}
.issue{font-size:12px;color:#efb8aa;overflow-wrap:anywhere}#empty{padding:24px;border:1px solid #354258;border-radius:8px;color:#b7c5d8}
@media(max-width:600px){body{padding:20px 12px}h1{font-size:24px}.group-heading{padding:12px}.back-top{margin-left:0}.folder-nav{gap:6px}.folder-nav a{padding:6px 10px}}
</style></head><body id="top"><header><h1>Authorware review reports</h1>
<p>Browse by source folder, then open a file to review its extracted pictures, animations, cursors, text, sounds and other content.</p>
<p>''' + count_note + '''</p></header><div class="stats" aria-label="Recorded output totals">''' + stats + '''</div>
<div class="toolbar"><input id="search" type="search" placeholder="Filter by filename or folder…" aria-label="Filter by filename or folder" aria-controls="groups">
<p id="result-count" aria-live="polite">''' + f'{len(summaries):,} source files · {len(groups):,} {"folder" if len(groups) == 1 else "folders"} · {recorded_outputs:,} {output_label}' + '''</p></div>
<nav class="folder-nav" aria-label="Source folders">''' + ''.join(navigation) + '''</nav>
<main id="groups">''' + ''.join(sections) + '''</main><p id="empty" hidden>No files match this filter.</p>
<script>
// Vibe coded by Codex
const search = document.getElementById('search');
const resultCount = document.getElementById('result-count');
const totalLabel = resultCount.textContent;
const groups = Array.from(document.querySelectorAll('.source-group'), section => ({
    section,
    rows: Array.from(section.querySelectorAll('tbody tr'), row => ({row, text: row.dataset.search.toLowerCase()})),
    link: document.querySelector(`.folder-nav a[href="#${section.id}"]`),
    count: section.querySelector('.group-count')
}));
const total = groups.reduce((sum, group) => sum + group.rows.length, 0);
function filterFiles() {
    const query = search.value.trim().toLowerCase();
    let files = 0, folders = 0;
    for (const group of groups) {
        let visible = 0;
        for (const {row, text} of group.rows) {
            row.hidden = !text.includes(query);
            if (!row.hidden) visible++;
        }
        group.section.hidden = group.link.hidden = visible === 0;
        group.link.querySelector('.folder-count').textContent = visible.toLocaleString();
        group.count.textContent = query ? `${visible.toLocaleString()} of ${group.rows.length.toLocaleString()} files` : `${visible.toLocaleString()} ${visible === 1 ? 'file' : 'files'}`;
        files += visible;
        if (visible) folders++;
    }
    resultCount.textContent = query ? `${files.toLocaleString()} of ${total.toLocaleString()} files · ${folders.toLocaleString()} ${folders === 1 ? 'folder' : 'folders'}` : totalLabel;
    document.getElementById('empty').hidden = files !== 0;
}
search.addEventListener('input', filterFiles);
filterFiles();
</script></body></html>'''
    (output/'index.html').write_text(page, encoding='utf-8')
    (output/'inventory.json').write_text(json.dumps(summaries, indent=2)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('roots', nargs='+', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    sources = sorted({p for root in args.roots for p in ([root] if root.is_file() else root.rglob('*')) if p.is_file()})
    results = []
    with ProcessPoolExecutor(max_workers=max(1,args.jobs)) as pool:
        futures = [pool.submit(review_file, (str(source), str(args.output))) for source in sources]
        for future in as_completed(futures):
            results.append(future.result())
            if len(results) % 25 == 0:
                print(f'{len(results)}/{len(sources)} reports generated', flush=True)
    write_index(args.output, results)
    print(args.output/'index.html', flush=True)


if __name__ == '__main__':
    main()
