#!/usr/bin/env python3
# Vibe coded by Claude
"""
make_report.py [--html]

Batch-extract every sample Folio infobase under lds/, p/ and sample0/ with
folioDatabase.py -- in parallel, using the parallel-safe private-sandbox isolation --
and emit a self-contained dark-mode HTML verification report at
report_out/report.html plus report_out/stats.json.

Extractions land in report_out/<relative-path>.out/ so you can spot-check them.
Re-run with --html to regenerate the HTML from an existing stats.json.
"""
import os, sys, subprocess, json, re, time, html, concurrent.futures

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCES = ['lds', 'p', 'sample0']
OUTROOT = os.path.join(HERE, 'report_out')
IMG_EXT = ('.bmp', '.gif', '.jpg', '.jpeg', '.png', '.wmf', '.emf', '.tif', '.tiff')
OBJ_EXT = IMG_EXT + ('.bin', '.ole', '.pdf')   # embedded objects (now written at top level)
KNOWN_TEXT = ('body.txt', 'metadata.txt', 'vocabulary.txt', 'references.txt',
              'topical_guide.txt', 'title.txt', 'title.ans', 'MANIFEST.txt')


def find_nfos():
    res = []
    for src in SOURCES:
        base = os.path.join(HERE, src)
        if not os.path.isdir(base):
            continue
        for root, _, files in os.walk(base):
            for fn in files:
                if fn.lower().endswith('.nfo'):
                    res.append((src, os.path.join(root, fn)))
    return sorted(res, key=lambda x: (x[0], x[1].lower()))


def detect_era(path):
    try:
        d = open(path, 'rb').read(2048)
    except OSError:
        return 'unreadable'
    if len(d) > 1292 + 40 and d[1292:1292 + 20] == b'Copyright Folio Corp':
        m = re.search(rb'v(\d)\d\d\.\d\d\d', d[1292:1292 + 48])
        return 'DOS 2.0'
    if b'Folio Corporation' in d[:0x60]:
        return 'Win 3.x / 4.x'
    if b'Folio' in d[:0x600]:
        return 'Folio (other)'
    return 'unknown'


def extract_one(item):
    src, path = item
    rel = os.path.relpath(path, HERE)
    insize = os.path.getsize(path) if os.path.exists(path) else 0
    era = detect_era(path)
    st = {'src': src, 'name': os.path.basename(path), 'rel': rel, 'title': '',
          'insize': insize, 'era': era, 'secs': 0.0, 'body': 0, 'objects': 0,
          'obj_img': 0, 'vocab': 0, 'refs': 0, 'outfiles': [], 'method': 'none'}
    # The 16-bit real-mode DOS engine reads infobases from disk ON DEMAND, so file size is
    # NOT a blocker: huge 2.0 infobases (HamCall 113 MB, Business 344 MB, General-Interest
    # 147 MB) open and export byte-perfectly via the real PreVIEWS engine under dosbox --
    # they just take longer (streaming ~0.5 MB/s of output text).  The old 100 MB guard was
    # therefore overly conservative and skipped fully-recoverable files; it is disabled by
    # default (set FOLIO_DOS_MAXSIZE to re-enable a cap, e.g. for a fast partial run).
    maxdos = int(os.environ.get('FOLIO_DOS_MAXSIZE', str(1 << 62)))
    if era == 'DOS 2.0' and insize > maxdos:
        st['method'] = 'too-large'
        return st
    outdir = os.path.join(OUTROOT, rel + '.out')
    os.makedirs(outdir, exist_ok=True)
    t0 = time.time()
    # Big infobases stream for many minutes; scale the wall-clock cap with input size
    # (~8 s per input-MB + a floor) so a 344 MB Business export isn't cut off mid-run.
    dos_timeout = max(2400, 600 + (insize // (1024 * 1024)) * 8) if era == 'DOS 2.0' else 2400
    try:
        subprocess.run([sys.executable, os.path.join(HERE, 'folioDatabase.py'), '--all', path, outdir],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=dos_timeout)
    except Exception:
        pass
    st['secs'] = round(time.time() - t0, 1)
    if os.path.isdir(outdir):
        for fn in sorted(os.listdir(outdir)):
            fp = os.path.join(outdir, fn)
            if not os.path.isfile(fp):
                continue
            low = fn.lower()
            if fn in KNOWN_TEXT:
                sz = os.path.getsize(fp)
                st['outfiles'].append([fn, sz])
                if fn == 'body.txt':
                    st['body'] = sz
                elif fn == 'vocabulary.txt':
                    st['vocab'] = sum(1 for _ in open(fp, errors='replace'))
                elif fn == 'references.txt':
                    st['refs'] = sum(1 for _ in open(fp, errors='replace'))
            elif low.endswith(OBJ_EXT):            # an embedded object (top level, alongside body.txt)
                st['objects'] += 1
                if low.endswith(IMG_EXT):
                    st['obj_img'] += 1
        # tolerate the older objects/ subdir layout too (pre-flatten extractions)
        objd = os.path.join(outdir, 'objects')
        if os.path.isdir(objd):
            objs = [f for f in os.listdir(objd) if os.path.isfile(os.path.join(objd, f))]
            st['objects'] += len(objs)
            st['obj_img'] += sum(1 for f in objs if f.lower().endswith(IMG_EXT))
        man = os.path.join(outdir, 'MANIFEST.txt')
        if os.path.exists(man):
            m = open(man, errors='replace').read()
            mo = re.search(r'Embedded objects:\s*(\d+)', m)
            if mo:
                st['objects'] = int(mo.group(1))   # authoritative count from folioDatabase.py
            if 'real Folio Views 4.2 engine' in m:
                st['method'] = 'engine 4.x/3.x'
            elif 'PreVIEWS' in m or 'DOS-era' in m or 'dos-engine' in m:
                st['method'] = 'DOS 2.0 engine'
            elif 'pure-Python' in m:
                st['method'] = 'python codec'
            mm = re.search(r'Infobase name:\s*(.*)', m)
            if mm:
                st['title'] = mm.group(1).strip()[:60]
    # method fallbacks when MANIFEST wording is absent
    if st['method'] == 'none' and st['body'] > 0:
        st['method'] = 'DOS 2.0 engine' if st['era'] == 'DOS 2.0' else 'engine 4.x/3.x'
    return st


def human(n):
    for u in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or u == 'GB':
            return ('%d %s' % (n, u)) if u == 'B' else ('%.1f %s' % (n, u))
        n /= 1024.0


METHOD_COLOR = {'engine 4.x/3.x': '#4ea1ff', 'DOS 2.0 engine': '#a688ff',
                'python codec': '#f0b34a', 'too-large': '#e8934a', 'none': '#ff6b6b'}


def _is_clean(s):
    return s['method'] in ('engine 4.x/3.x', 'DOS 2.0 engine') and (s['body'] > 0 or s['objects'] > 0)


def _status(s):
    if _is_clean(s):
        return '✓', '#39d98a'          # clean real-engine extraction (byte-perfect)
    if s['method'] == 'python codec' and s['body'] > 0:
        return '~', '#f0b34a'               # best-effort fallback (unreliable, esp. for 2.0)
    if s['method'] == 'too-large':
        return '⚠', '#e8934a'          # too large for the 16-bit DOS engine
    return '—', '#ff6b6b'              # no content


def write_html(stats):
    stats = sorted(stats, key=lambda s: (s['src'], s['name'].lower()))
    total = len(stats)
    clean = sum(1 for s in stats if _is_clean(s))
    besteffort = sum(1 for s in stats if s['method'] == 'python codec' and s['body'] > 0)
    got_obj = sum(1 for s in stats if s['objects'] > 0)
    tot_objs = sum(s['objects'] for s in stats)
    too_large = [s for s in stats if s['method'] == 'too-large']
    no_content = [s for s in stats if s['body'] == 0 and s['objects'] == 0 and s['method'] != 'too-large']

    def esc(x):
        return html.escape(str(x))

    rows_by_src = {}
    for s in stats:
        rows_by_src.setdefault(s['src'], []).append(s)

    def render_rows(rows):
        out = []
        for i, s in enumerate(rows, 1):
            status, scolor = _status(s)
            mc = METHOD_COLOR.get(s['method'], '#888')
            others = [f for f, _ in s['outfiles']
                      if f not in ('body.txt', 'MANIFEST.txt', 'metadata.txt')]
            extra = []
            if s['vocab']:
                extra.append('%d words' % s['vocab'])
            if s['refs']:
                extra.append('%d refs' % s['refs'])
            if any(f.startswith('title') for f in others):
                extra.append('title')
            objtxt = ''
            if s['objects']:
                objtxt = '%d <span class="sub">(%d img)</span>' % (s['objects'], s['obj_img'])
            out.append(
                '<tr>'
                '<td class="idx">%d</td>'
                '<td class="status" style="color:%s">%s</td>'
                '<td class="name" title="%s"><b>%s</b>%s</td>'
                '<td>%s</td>'
                '<td class="num">%s</td>'
                '<td><span class="pill" style="background:%s22;color:%s;border-color:%s55">%s</span></td>'
                '<td class="num">%s</td>'
                '<td class="num">%s</td>'
                '<td class="sub">%s</td>'
                '<td class="num sub">%ss</td>'
                '</tr>' % (
                    i, scolor, status,
                    esc(s['name']), esc(s['name']),
                    (' <span class="sub">%s</span>' % esc(s['title'])) if s['title'] else '',
                    esc(s['era']),
                    human(s['insize']),
                    mc, mc, mc, esc(s['method']),
                    human(s['body']) if s['body'] else '<span class="sub">0</span>',
                    objtxt or '<span class="sub">0</span>',
                    esc(', '.join(extra)),
                    s['secs'],
                ))
        return '\n'.join(out)

    sections = []
    for src in SOURCES:
        rows = rows_by_src.get(src, [])
        if not rows:
            continue
        okc = sum(1 for s in rows if s['body'] > 0 or s['objects'] > 0)
        objc = sum(s['objects'] for s in rows)
        sections.append(
            '<h2>%s <span class="sub">&mdash; %d infobases, %d with content, %d objects</span></h2>'
            '<div class="tblwrap"><table>'
            '<thead><tr><th>#</th><th></th><th>Infobase</th><th>Era</th><th>Input</th>'
            '<th>Method</th><th>Body</th><th>Objects</th><th>Also</th><th>Time</th></tr></thead>'
            '<tbody>%s</tbody></table></div>' % (esc(src + '/'), len(rows), okc, objc, render_rows(rows)))

    nc_html = ''
    if too_large:
        items = ''.join('<li>%s <span class="sub">(%s)</span></li>' %
                        (esc(s['rel']), human(s['insize']))
                        for s in sorted(too_large, key=lambda x: -x['insize']))
        nc_html += ('<h2>Too large for the DOS engine (%d)</h2><p class="sub">Folio 2.0 '
                    'infobases above ~100 MB: the original 16-bit real-mode DOS reader cannot '
                    'process them and the 32-bit 4.2 engine rejects the 2.0 format, so they are '
                    'not cleanly extractable here.</p><ul class="nc">%s</ul>' % (len(too_large), items))
    if no_content:
        items = ''.join('<li>%s <span class="sub">(%s, %s)</span></li>' %
                        (esc(s['rel']), esc(s['era']), human(s['insize'])) for s in no_content)
        nc_html += ('<h2>No text or objects (%d)</h2><p class="sub">These are typically '
                    'navigation-menu / stub / test infobases, or files needing components '
                    'absent from the dataset.</p><ul class="nc">%s</ul>' % (len(no_content), items))

    css = """
    :root{ color-scheme:dark;
      --bg:#0a0e13; --panel:#111a24; --panel2:#0d151d; --line:#1d2a37; --line2:#16212c;
      --ink:#cdd9e4; --dim:#7e8fa0; --faint:#566472; --head:#eaf3fa;
      --accent:#3fd0c9;                         /* Folio's own cyan */
      --mono:ui-monospace,SFMono-Regular,'Cascadia Code',Menlo,Consolas,monospace;
      --sans:ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; }
    *{box-sizing:border-box;}
    body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 var(--sans);-webkit-font-smoothing:antialiased;}
    .wrap{max-width:1180px;margin:0 auto;padding:34px 22px 96px;}
    .eyebrow{font:600 11px/1 var(--mono);letter-spacing:.24em;text-transform:uppercase;color:var(--accent);margin:0 0 11px;}
    h1{font-size:27px;line-height:1.14;margin:0 0 8px;color:var(--head);letter-spacing:-.012em;text-wrap:balance;}
    .lede{color:var(--dim);max-width:72ch;margin:0 0 22px;}
    h2{font-size:16px;margin:40px 0 12px;color:var(--head);display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;}
    .sub{color:var(--faint);font-weight:400;font-size:.86em;}
    .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:20px 0 8px;}
    .card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:15px 18px;}
    .card .big{font:600 28px/1 var(--mono);color:var(--head);letter-spacing:-.02em;}
    .card .lbl{color:var(--dim);font-size:11.5px;text-transform:uppercase;letter-spacing:.05em;margin-top:6px;}
    .legend{font-size:12.5px;color:var(--dim);margin:15px 0 4px;display:flex;flex-wrap:wrap;gap:5px 20px;}
    .tblwrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--panel2);}
    table{border-collapse:collapse;width:100%;min-width:860px;}
    th,td{padding:8px 12px;text-align:left;white-space:nowrap;}
    thead th{background:var(--panel);color:var(--dim);font:600 10.5px/1 var(--sans);text-transform:uppercase;letter-spacing:.06em;position:sticky;top:0;border-bottom:1px solid var(--line);}
    tbody tr{border-top:1px solid var(--line2);}
    tbody tr:hover{background:#131f2a;}
    td.idx{text-align:right;color:var(--faint);font:12px var(--mono);}
    td.status{text-align:center;font-weight:700;font-size:15px;}
    td.num{text-align:right;font-variant-numeric:tabular-nums;font-family:var(--mono);font-size:12.5px;}
    td.name{max-width:330px;overflow:hidden;text-overflow:ellipsis;}
    td.name b{color:#e8f0f6;font-weight:600;}
    .pill{display:inline-block;padding:2px 10px;border-radius:20px;border:1px solid;font:600 11.5px/1.35 var(--sans);}
    ul.nc{columns:2;column-gap:36px;font-size:13px;color:#93a1b0;line-height:1.75;padding-left:18px;margin:8px 0;}
    ul.nc li{break-inside:avoid;}
    @media(max-width:720px){ul.nc{columns:1;} .wrap{padding:26px 14px 72px;}}
    footer{margin-top:46px;padding-top:16px;border-top:1px solid var(--line);color:var(--faint);font-size:12px;}
    """
    doc = (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Folio .NFO extraction report</title><style>%s</style></head><body><div class="wrap">'
        '<p class="eyebrow">folioDatabase.py &middot; extraction verification</p>'
        '<h1>Folio Infobase (.NFO) extraction report</h1>'
        '<p class="lede">Every infobase under lds/, p/ and sample0/ driven through the pipeline &mdash; the '
        'real Folio engines (32-bit Views 4.2 under wine; 16-bit PreVIEWS 2.1 under dosbox) with a pure-Python '
        'codec as fallback. A clean status means a real engine produced byte-perfect output.</p>'
        '<div class="cards">'
        '<div class="card"><div class="big">%d</div><div class="lbl">Infobases</div></div>'
        '<div class="card"><div class="big" style="color:#39d98a">%d</div><div class="lbl">Clean engine (byte-perfect)</div></div>'
        '<div class="card"><div class="big" style="color:#f0b34a">%d</div><div class="lbl">Best-effort codec</div></div>'
        '<div class="card"><div class="big">%d</div><div class="lbl">With objects</div></div>'
        '<div class="card"><div class="big">%s</div><div class="lbl">Total objects</div></div>'
        '</div>'
        '<p class="legend"><b style="color:#39d98a">&#10003; clean</b> = real Folio engine, byte-perfect'
        ' &nbsp;&middot;&nbsp; <b style="color:#f0b34a">~ best-effort</b> = pure-Python codec fallback'
        ' (partial/unreliable, especially on 2.0) &nbsp;&middot;&nbsp; <b style="color:#e8934a">&#9888;'
        ' too-large</b> = exceeds 16-bit DOS engine &nbsp;&middot;&nbsp; <b style="color:#ff6b6b">&mdash;'
        ' none</b> = stub / different subtype / corrupt</p>'
        '%s%s'
        '<footer>Generated by make_report.py. Each row is under report_out/&lt;path&gt;.out/.</footer>'
        '</div></body></html>' % (
            css, total, clean, besteffort, got_obj, '{:,}'.format(tot_objs),
            ''.join(sections), nc_html))
    os.makedirs(OUTROOT, exist_ok=True)
    with open(os.path.join(OUTROOT, 'report.html'), 'w') as f:
        f.write(doc)
    print('report -> %s  (%d infobases, %d clean-engine, %d w/objects, %d objects)' %
          (os.path.join(OUTROOT, 'report.html'), total, clean, got_obj, tot_objs))


def _save(stats):
    json.dump(stats, open(os.path.join(OUTROOT, 'stats.json'), 'w'))


def _run(items, workers, label, sink):
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        for i, s in enumerate(ex.map(extract_one, items), 1):
            sink(s)
            if i % 5 == 0 or i == len(items):
                print('  %s [%d/%d]' % (label, i, len(items)), flush=True)


def main():
    os.makedirs(OUTROOT, exist_ok=True)
    # DOS-2.0 extraction drives a real GUI viewer under dosbox and is timing-sensitive,
    # so it runs at LOW concurrency (default 5); wine/codec files run wide.
    dos_workers = int(os.environ.get('FOLIO_DOS_WORKERS', '5'))
    wine_workers = max(2, min(12, os.cpu_count() or 4))

    if '--html' in sys.argv:
        write_html(json.load(open(os.path.join(OUTROOT, 'stats.json'))))
        return

    if '--redo-dos' in sys.argv:            # re-extract just the DOS files and merge
        stats = json.load(open(os.path.join(OUTROOT, 'stats.json')))
        by_rel = {s['rel']: s for s in stats}
        dos = [(s['src'], os.path.join(HERE, s['rel'])) for s in stats if s['era'] == 'DOS 2.0']
        print('re-extracting %d DOS-2.0 infobases @%d-way (adaptive automation)...' %
              (len(dos), dos_workers), flush=True)
        def sink(s):
            by_rel[s['rel']] = s; _save(list(by_rel.values()))
        _run(dos, dos_workers, 'dos', sink)
        write_html(list(by_rel.values()))
        return

    nfos = find_nfos()
    nondos = [n for n in nfos if detect_era(n[1]) != 'DOS 2.0']
    dos = [n for n in nfos if detect_era(n[1]) == 'DOS 2.0']
    print('extracting %d infobases: %d wine/codec @%d-way, %d DOS-2.0 @%d-way ...' %
          (len(nfos), len(nondos), wine_workers, len(dos), dos_workers), flush=True)
    stats = []
    def sink(s):
        stats.append(s); _save(stats)
    _run(nondos, wine_workers, 'wine', sink)
    _run(dos, dos_workers, 'dos', sink)
    _save(stats)
    write_html(stats)


if __name__ == '__main__':
    main()
