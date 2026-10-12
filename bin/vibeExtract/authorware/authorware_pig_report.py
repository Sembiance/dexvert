#!/usr/bin/env python3
# Vibe coded by Codex
"""Self-contained, dark review pages for all extracted Authorware resources.

Usage: python3 authorware_pig_report.py --output report/pig-review sample/a3m/Bienvenue.A3M
"""

import argparse
import base64
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
from html import escape
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import authorware
from authorware_pig import dib_png


def data_url(mime, content):
    return 'data:' + mime + ';base64,' + base64.b64encode(content).decode('ascii')


def collect_assets(directory, names, pictures):
    """Read only this extraction's outputs; imported .bin files stay opaque."""
    represented = {p.get('file') for p in pictures}
    pig_info = {p['raw_file']: p for p in pictures if p.get('raw_file')}
    dib_info = {}
    for name in names:
        if name.startswith('dib_manifest') and name.endswith('.json'):
            manifest = json.loads((Path(directory) / name).read_text())
            dib_info.update((item['raw_file'], item) for item in manifest['dibs'] if item.get('raw_file'))
    images = {'.bmp': 'image/bmp', '.png': 'image/png', '.jpg': 'image/jpeg',
              '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.svg': 'image/svg+xml'}
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
            item['handling'] = 'Bitmap rendered in PIG SVG; original PIG bytes retained'
            item['rendered_by'] = [{'id': picture['id'], 'index': picture['index'], 'file': picture['file']}]
        if suffix in images:
            item['kind'] = 'image'
            item['preview'] = item['url']
            if suffix == '.bmp':
                try:
                    png, width, height = dib_png(authorware, content[14:])
                    item.update(preview=data_url('image/png', png), width=width, height=height)
                except (ValueError, IndexError, OverflowError) as exc:
                    item['warning'] = 'Bitmap preview unavailable: ' + str(exc)
        elif suffix in sounds:
            item['kind'] = 'audio'
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
            style = ''
            if kind == 'image':
                dimensions = ''
                if item.get('width') and item.get('height'):
                    dimensions = f' width="{item["width"]}" height="{item["height"]}"'
                    style = f' style="--picture-width:{item["width"] + 2}px"'
                body = '<div class="art"><img loading="lazy" decoding="async"' + dimensions + ' src="' + item['preview'] + '" alt="' + escape(item['name'], quote=True) + '"></div>'
            elif kind in ('audio', 'video'):
                body = '<' + kind + ' controls preload="metadata" src="' + item['url'] + '"></' + kind + '>'
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
    counts = Counter(p.get('status', 'unrendered') for p in pictures)
    totals = str(len(pictures)) + ' pictures'
    if counts:
        totals += ' · ' + ' · '.join(f'{count} {status}' for status, count in counts.items())
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
            art = '<div class="art"><img loading="lazy" decoding="async"' + size + ' src="' + escape(svg, quote=True) + '" alt="' + escape(label, quote=True) + '"></div>'
        else:
            art = '<p class="missing">No renderable picture recovered.</p>'
        warnings = ''.join('<p class="warning">' + escape(str(w)) + '</p>' for w in picture.get('warnings', []))
        caption = dimensions if status == 'converted' else str(status) + (' · ' + dimensions if dimensions else '')
        download = ''
        if picture.get('file') and svg:
            download = '<p class="meta"><a download="' + escape(picture['file'], quote=True) + '" href="' + escape(svg, quote=True) + '">Download SVG</a></p>'
        cards.append('<section class="picture" id="' + anchor + '"' + card_size + '><h2><a href="#' + anchor + '">Entry ' + escape(entry_id) + '<span class="entry-index">index ' + escape(index) + '</span></a></h2>' + art + '<p class="meta">' + escape(caption) + '</p>' + download + warnings + '</section>')
    other_sections, links = asset_sections(assets, {p.get('file'): 'picture-' + str(i + 1) for i, p in enumerate(pictures)})
    if pictures:
        links.insert(0, '<a href="#pig-pictures">PIG pictures (' + str(len(pictures)) + ')</a>')
    navigation = '<nav>' + ' · '.join(links) + '</nav>'
    notice_html = '<p class="warning">' + escape(notice) + '</p>' if notice else ''
    if assets:
        totals += ' · ' + str(len(assets) + sum(bool(p.get('file')) for p in pictures)) + ' extracted files'
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
<p>Scroll through all extracted content. Report problems by entry number or filename. Click a filename to download the original extracted file.</p>
<p class="muted">Each image keeps its original dimensions when it fits the window. The checkerboard marks transparency within the image. Original fonts may be substituted.</p>''' + notice_html + navigation + '''</header>
<main>''' + ('<section id="pig-pictures"><h2 class="section-title">PIG pictures · ' + str(len(pictures)) + '</h2><div class="grid">' + ''.join(cards) + '</div></section>' if cards else '') + other_sections + ('' if cards or assets else '<p class="missing">No extracted content recovered.</p>') + '''</main>
<footer>Source SHA-256: <code>''' + escape(str(source_hash)) + '''</code></footer>
<script id="payload" type="application/json">''' + encoded + '</script></html>'


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
                                 str(source), str(directory)], capture_output=True, text=True)
        manifest = directory / 'pig_manifest.json'
        pictures = json.loads(manifest.read_text())['pictures'] if manifest.exists() else []
        for picture in pictures:
            filename = picture.get('file')
            picture['svg'] = data_url('image/svg+xml', (directory / filename).read_bytes()) if filename else None
        assets = collect_assets(directory, [p.name for p in directory.iterdir() if p.is_file()], pictures)
        notice = result.stderr.strip() if result.returncode else ''
        if result.returncode and not notice:
            notice = f'Extractor exited with status {result.returncode}'
        (output / name).write_text(report_html(str(source), summary['sha256'], pictures, assets, notice), encoding='utf-8')
    summary.update(page=name, pictures=len(pictures), statuses=dict(Counter(p['status'] for p in pictures)),
                   assets=dict(Counter(a['kind'] for a in assets)),
                   warnings=dict(Counter(w for p in pictures for w in p['warnings'])),
                   exit_code=result.returncode, seconds=round(time.monotonic()-start, 2))
    if notice:
        summary['error'] = notice
    return summary


def re_safe_name(name):
    import re
    return re.sub(r'[^A-Za-z0-9._-]+', '_', name)[:90]


def write_index(output, summaries):
    rows = []
    for item in sorted(summaries, key=lambda row: row['source']):
        label = escape(item['source'])
        if item.get('page'):
            label = '<a href="' + escape(item['page'], quote=True) + '">' + label + '</a>'
        counts = item.get('statuses', {})
        rows.append('<tr><td>'+label+'</td><td>'+str(item['pictures'])+'</td><td>'+str(counts.get('converted',0))+'</td><td>'+str(counts.get('partial',0))+'</td><td>'+str(counts.get('unrendered',0))+'</td><td>'+escape(item.get('error',''))+'</td></tr>')
    page = '''<!doctype html><!-- Vibe coded by Codex --><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Authorware PIG review reports</title><style>:root{color-scheme:dark}body{background:#10151d;color:#e7eef8;font:15px/1.5 system-ui;margin:30px}a{color:#84caff}table{border-collapse:collapse;width:100%}th,td{text-align:left;padding:8px;border-bottom:1px solid #354258}input{padding:10px;width:350px;background:#243044;color:white;border:1px solid #506078}th{position:sticky;top:0;background:#182230}</style><h1>Authorware PIG review reports</h1><p>Each source opens one self-contained page showing all its pictures. Scroll down and report any problem using the filename, entry number and table index. Converted means no known decoding limitation; visual verification is still needed.</p><input id="search" placeholder="Filter source files" aria-label="Filter source files"><p>''' + str(len(summaries)) + ' source files · ' + str(sum(s['pictures'] for s in summaries)) + ''' PIG pictures</p><table><thead><tr><th>Source file</th><th>PIGs</th><th>Converted</th><th>Partial</th><th>Unrendered</th><th>Input issue</th></tr></thead><tbody>''' + ''.join(rows) + '''</tbody></table><script>// Vibe coded by Codex
document.getElementById('search').oninput=e=>{const q=e.target.value.toLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q))};</script></html>'''
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
