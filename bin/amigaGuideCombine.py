#!/usr/bin/env python3
# Vibe coded by Claude

"""
amigaGuideCombine - Combines multiple interlinked HTML files from an
Amiga Guide conversion into a single navigable HTML file with
SPA-style page switching.

Usage:
  python3 amigaGuideCombine.py <start_html> <output_html>

Arguments:
  start_html   Path to the entry-point HTML file (e.g. ./guide/out/main.html)
               The directory containing this file is used as the input directory.
  output_html  Path where the combined HTML file will be written.

Examples:
  python3 amigaGuideCombine.py ./my_guide/out/main.html ./my_guide/my_guide.html
  python3 amigaGuideCombine.py /data/FICHEROS/out/main.html /data/FICHEROS/FICHEROS.html
"""

import os
import re
import sys
from collections import OrderedDict
from html import escape as html_escape
from urllib.parse import quote as url_quote


def escape_attr(s):
    """Escape a string for use inside an HTML attribute value."""
    return html_escape(s, quote=True)


def escape_href_fragment(s):
    """Percent-encode a string for use as a URL fragment identifier."""
    return url_quote(s, safe="")


def path_to_id(filepath):
    """Convert a relative file path to a unique, valid HTML id."""
    name = filepath.replace("\\", "/")
    name = re.sub(r"\.html?$", "", name, flags=re.IGNORECASE)
    name = name.replace("/", "--")
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    return f"page-{name}"


def extract_body(html):
    """Return the inner content of the <body> element."""
    m = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else html


def extract_title(html):
    """Return the text inside the <title> element."""
    m = re.search(r"<title>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def extract_body_colors(html):
    """Extract bgcolor and text color from the <body> tag attributes."""
    m = re.search(r"<body\s+([^>]*)>", html, re.IGNORECASE)
    if not m:
        return "#CFCFCF", "#000000"
    attrs = m.group(1)
    bg = re.search(r'bgcolor="([^"]*)"', attrs, re.IGNORECASE)
    tx = re.search(r'text="([^"]*)"', attrs, re.IGNORECASE)
    return (bg.group(1) if bg else "#CFCFCF"), (tx.group(1) if tx else "#000000")


def discover_files(base_dir, start="main.html"):
    """BFS crawl from start file, returning OrderedDict {relpath: html_content}."""
    found = OrderedDict()
    queue = [start]

    while queue:
        relpath = queue.pop(0)
        if relpath in found:
            continue
        abspath = os.path.join(base_dir, relpath)
        if not os.path.isfile(abspath):
            continue
        with open(abspath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        found[relpath] = content

        file_dir = os.path.dirname(relpath)
        for m in re.finditer(r'href="([^"]*)"', content, re.IGNORECASE):
            href = m.group(1)
            if href.startswith(("http://", "https://", "mailto:", "javascript:", "#")):
                continue
            path = href.split("#")[0]
            if not path or not re.search(r"\.html?$", path, re.IGNORECASE):
                continue
            resolved = os.path.normpath(os.path.join(file_dir, path))
            if resolved not in found:
                queue.append(resolved)

    return found


def rewrite_external_guide_link(resolved):
    """Rewrite a link to a file in an external guide.

    The resolved path must have at least one directory component to be
    considered external (same-directory broken links are left as-is).

    main.html  -> guidename/guidename.html
    other.html -> guidename/guidename.html#file-other.html
    """
    dirname = os.path.dirname(resolved)
    if not dirname:
        return None  # same-directory link, not an external guide reference
    basename = os.path.basename(resolved)
    guidename = os.path.basename(dirname)
    if not guidename:
        return None
    safe_guide = url_quote(guidename, safe="")
    if basename.lower() in ("main.html", "main.htm"):
        return f"{safe_guide}/{safe_guide}.html"
    return f"{safe_guide}/{safe_guide}.html#{escape_href_fragment('file-' + basename)}"


def rewrite_html(html, current_file, known_files):
    """Rewrite hrefs to internal anchors and namespace name= attributes."""
    current_dir = os.path.dirname(current_file)
    page_id = path_to_id(current_file)

    def href_replacer(m):
        href = m.group(1)
        # Leave external / special links untouched
        if href.startswith(("http://", "https://", "mailto:", "javascript:")):
            return m.group(0)
        # Pure fragment — namespace it to this page
        if href.startswith("#"):
            return f'href="#{page_id}--{href[1:]}"'
        parts = href.split("#", 1)
        path, frag = parts[0], (parts[1] if len(parts) > 1 else None)
        if not re.search(r"\.html?$", path, re.IGNORECASE):
            return m.group(0)
        resolved = os.path.normpath(os.path.join(current_dir, path))
        # Internal link — rewrite to anchor
        if resolved in known_files:
            target_id = path_to_id(resolved)
            if frag:
                return f'href="#{target_id}--{frag}"'
            return f'href="#{target_id}"'
        # External guide link — rewrite to guidename/guidename.html[#file-xxx]
        ext = rewrite_external_guide_link(resolved)
        if ext:
            return f'href="{ext}"'
        # Unknown link — leave as-is
        return m.group(0)

    html = re.sub(r'href="([^"]*)"', href_replacer, html, flags=re.IGNORECASE)

    # Namespace <a name="..."> anchors to avoid cross-page collisions
    html = re.sub(
        r'(<a\s[^>]*?)name="([^"]*)"',
        lambda m: f'{m.group(1)}name="{page_id}--{m.group(2)}"',
        html,
        flags=re.IGNORECASE,
    )

    return html


def find_all_html_files(base_dir, output_path=None):
    """Return a set of all .html file relpaths under base_dir, excluding output."""
    total = set()
    for root, _dirs, filenames in os.walk(base_dir):
        for fn in filenames:
            if re.search(r"\.html?$", fn, re.IGNORECASE):
                rel = os.path.relpath(os.path.join(root, fn), base_dir)
                total.add(rel)
    if output_path:
        out_rel = os.path.relpath(output_path, base_dir)
        total.discard(out_rel)
    return total


def load_unreachable_files(base_dir, all_html, reachable):
    """Load HTML files that exist on disk but weren't reachable via links."""
    unreachable = OrderedDict()
    for relpath in sorted(all_html - set(reachable.keys())):
        abspath = os.path.join(base_dir, relpath)
        if not os.path.isfile(abspath):
            continue
        with open(abspath, "r", encoding="utf-8", errors="replace") as f:
            unreachable[relpath] = f.read()
    return unreachable


UNREACHABLE_INDEX_ID = "page--unreachable"


def build_unreachable_index(unreachable_files):
    """Build a synthetic section that lists all unreachable pages as links."""
    count = len(unreachable_files)
    links = []
    for relpath in unreachable_files:
        pid = path_to_id(relpath)
        title = extract_title(unreachable_files[relpath]) or relpath
        safe_title = (
            title.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
        )
        links.append(f'  <a href="#{pid}">{safe_title}</a>  ({relpath})')

    body = (
        '<hr>\n<pre>\n\n'
        f'<b><u>UNREACHABLE PAGES ({count:,})</u></b>\n\n'
        'The following pages were found in the directory but are\n'
        f'not reachable from the start page via hyperlinks:\n\n'
        + "\n".join(links)
        + '\n\n</pre>\n<hr>'
    )

    safe_title = f"Unreachable Pages ({count:,})"
    return (
        f'<section id="{UNREACHABLE_INDEX_ID}" class="page" style="display:none" '
        f'data-title="{safe_title}">\n{body}\n</section>'
    )


# ---------------------------------------------------------------------------
# HTML template pieces
# ---------------------------------------------------------------------------

TEMPLATE_HEAD = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{
    background-color: {bgcolor};
    color: {textcolor};
    margin: 0;
    padding: 0;
    font-family: monospace;
  }}
  .page {{
    padding: 10px 20px 30px 20px;
  }}
  pre {{
    white-space: pre-wrap;
    word-wrap: break-word;
  }}
  #nav-bar {{
    position: sticky;
    top: 0;
    background: #2b2b2b;
    color: #eee;
    padding: 6px 12px;
    font-size: 13px;
    z-index: 100;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }}
  #nav-bar .guide-title {{
    font-weight: bold;
    white-space: nowrap;
  }}
  #nav-bar select {{
    background: #444;
    color: #eee;
    border: 1px solid #666;
    padding: 3px 6px;
    font-size: 13px;
    max-width: 450px;
    flex-shrink: 1;
    min-width: 120px;
  }}
  #page-count {{
    margin-left: auto;
    opacity: 0.6;
    white-space: nowrap;
  }}
  #unreachable-link {{
    color: #f9a825;
    text-decoration: none;
    white-space: nowrap;
    cursor: pointer;
  }}
  #unreachable-link:hover {{
    text-decoration: underline;
  }}
  noscript .page {{ display: block !important; }}
</style>
</head>
<body>
<div id="nav-bar">
  <span class="guide-title">{title}</span>
  <select id="page-select" aria-label="Navigate to page"></select>
  {unreachable_link}
  <span id="page-count"></span>
</div>
<noscript><style>.page {{ display: block !important; }}</style></noscript>
"""

TEMPLATE_SCRIPT = """\
<script>
(function() {
  var pages = document.querySelectorAll('.page');
  var select = document.getElementById('page-select');
  var countEl = document.getElementById('page-count');
  var currentId = null;
  var startId = '%s';

  // Populate dropdown
  for (var i = 0; i < pages.length; i++) {
    var opt = document.createElement('option');
    opt.value = pages[i].id;
    opt.textContent = pages[i].getAttribute('data-title') || pages[i].id;
    select.appendChild(opt);
  }
  countEl.textContent = pages.length + ' pages';

  select.addEventListener('change', function() {
    showPage(this.value, true);
  });

  function findSection(id) {
    // Direct match by page id
    var el = document.getElementById(id);
    if (el && el.classList.contains('page')) return { section: el, fragment: null };

    // Match by file-anchor name (for cross-guide links like #file-copyright.html)
    // Decode in case the browser percent-encoded the fragment
    var decoded = id;
    try { decoded = decodeURIComponent(id); } catch(e) {}
    var anchor = document.querySelector('a[name="' + CSS.escape(decoded) + '"]');
    if (anchor) {
      var parent = anchor.closest('.page');
      if (parent) return { section: parent, fragment: null };
    }

    // Progressive strip from last '--' to find the page section
    var testId = id, fragment = null;
    while (testId.lastIndexOf('--') > 0) {
      var pos = testId.lastIndexOf('--');
      fragment = testId.substring(pos + 2) + (fragment ? '--' + fragment : '');
      testId = testId.substring(0, pos);
      el = document.getElementById(testId);
      if (el && el.classList.contains('page')) return { section: el, fragment: fragment };
    }
    return { section: null, fragment: null };
  }

  function showPage(id, pushState) {
    var result = findSection(id);
    var section = result.section;
    var fragment = result.fragment;

    if (!section) {
      section = document.getElementById(startId);
      fragment = null;
      id = startId;
    }

    var pageId = section.id;

    // Hide all, show target
    if (currentId !== pageId) {
      for (var i = 0; i < pages.length; i++) {
        pages[i].style.display = 'none';
      }
      section.style.display = 'block';
      currentId = pageId;
      select.value = pageId;
      document.title = section.getAttribute('data-title') || pageId;
    }

    // Scroll to fragment anchor or top of page
    if (fragment) {
      var fragName = pageId + '--' + fragment;
      var anchor = document.querySelector('[name="' + CSS.escape(fragName) + '"]');
      if (anchor) { anchor.scrollIntoView(); }
      else { window.scrollTo(0, 0); }
    } else {
      window.scrollTo(0, 0);
    }

    if (pushState !== false) {
      history.pushState({ page: id }, '', '#' + id);
    }
  }

  // Intercept local link clicks
  document.addEventListener('click', function(e) {
    var a = e.target.closest ? e.target.closest('a') : null;
    if (!a) return;
    var href = a.getAttribute('href');
    if (!href || !href.startsWith('#')) return;
    e.preventDefault();
    showPage(href.substring(1), true);
  });

  // Browser back / forward
  window.addEventListener('popstate', function(e) {
    if (e.state && e.state.page) {
      showPage(e.state.page, false);
    } else if (location.hash) {
      showPage(location.hash.substring(1), false);
    } else {
      showPage(startId, false);
    }
  });

  // Initial navigation
  if (location.hash) {
    showPage(location.hash.substring(1), false);
  } else {
    history.replaceState({ page: startId }, '', '#' + startId);
  }
})();
</script>
"""

TEMPLATE_TAIL = """\
</body>
</html>
"""


def combine(start_html, output):
    """Discover, rewrite, and combine HTML files into a single output."""
    start_html = os.path.abspath(start_html)
    output = os.path.abspath(output)
    base_dir = os.path.dirname(start_html)
    start = os.path.basename(start_html)

    reachable = discover_files(base_dir, start)
    if not reachable:
        print(f"Error: no files found from '{start}' in '{base_dir}'", file=sys.stderr)
        sys.exit(1)

    print(f"Reachable: {len(reachable)} HTML file(s)", file=sys.stderr)

    # Find and load unreachable files
    all_html = find_all_html_files(base_dir, output)
    unreachable = load_unreachable_files(base_dir, all_html, reachable)

    if unreachable:
        print(f"Unreachable: {len(unreachable)} HTML file(s)", file=sys.stderr)

    # All files combined — used for link rewriting so cross-links work everywhere
    all_files = OrderedDict(list(reachable.items()) + list(unreachable.items()))
    known = set(all_files.keys())

    print(f"Total: {len(all_files)} HTML file(s)", file=sys.stderr)

    main_html = reachable[start]
    main_title = extract_title(main_html) or "Combined Guide"
    bgcolor, textcolor = extract_body_colors(main_html)
    start_id = path_to_id(start)

    # Build page sections for reachable files
    sections = []
    first = True
    for relpath, html in reachable.items():
        pid = path_to_id(relpath)
        title = extract_title(html) or relpath
        body = extract_body(html)
        body = rewrite_html(body, relpath, known)
        display = "block" if first else "none"
        first = False
        safe_title = (
            title.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
        )
        file_anchor = f'<a name="{escape_attr("file-" + os.path.basename(relpath))}"></a>'
        sections.append(
            f'<section id="{pid}" class="page" style="display:{display}" '
            f'data-title="{safe_title}">\n{file_anchor}\n{body}\n</section>'
        )

    # Build unreachable index + unreachable page sections
    unreachable_link_html = ""
    if unreachable:
        sections.append(build_unreachable_index(unreachable))
        unreachable_link_html = (
            f'<a id="unreachable-link" href="#{UNREACHABLE_INDEX_ID}">'
            f'{len(unreachable):,} unreachable page{"s" if len(unreachable) != 1 else ""}'
            f'</a>'
        )
        for relpath, html in unreachable.items():
            pid = path_to_id(relpath)
            title = extract_title(html) or relpath
            body = extract_body(html)
            body = rewrite_html(body, relpath, known)
            safe_title = (
                title.replace("&", "&amp;")
                .replace('"', "&quot;")
                .replace("<", "&lt;")
            )
            file_anchor = f'<a name="{escape_attr("file-" + os.path.basename(relpath))}"></a>'
            sections.append(
                f'<section id="{pid}" class="page" style="display:none" '
                f'data-title="{safe_title}">\n{file_anchor}\n{body}\n</section>'
            )

    with open(output, "w", encoding="utf-8") as f:
        f.write(
            TEMPLATE_HEAD.format(
                title=main_title,
                bgcolor=bgcolor,
                textcolor=textcolor,
                unreachable_link=unreachable_link_html,
            )
        )
        f.write("\n".join(sections))
        f.write("\n")
        f.write(TEMPLATE_SCRIPT % start_id)
        f.write(TEMPLATE_TAIL)

    print(f"\nWritten: {output} ({len(all_files)} pages combined)", file=sys.stderr)


def main():
    if len(sys.argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(1)

    start_html = sys.argv[1]
    output = sys.argv[2]

    if not os.path.isfile(start_html):
        print(f"Error: '{start_html}' is not a file", file=sys.stderr)
        sys.exit(1)

    combine(start_html, output)


if __name__ == "__main__":
    main()
