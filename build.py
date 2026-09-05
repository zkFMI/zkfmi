#!/usr/bin/env python3
"""Build zkfmi.com: wrap page fragments in pages/ with the shared template into public/.

A fragment starts with a header block:

    ---
    title: zkPI
    description: one line
    path: docs/zkpi.html
    section: docs          (docs | top | ja)
    ---
    <body html>

No dependencies beyond the standard library.
"""
import os, re, shutil, sys, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES = os.path.join(ROOT, "pages")
PUBLIC = os.path.join(ROOT, "public")
SITE = "zkFMI"
DOMAIN = "https://zkfmi.com"

NAV_TOP = [
    ("Overview", "index.html"),
    ("Architecture", "docs/architecture.html"),
    ("Docs", "docs/index.html"),
    ("Measurements", "docs/measurements.html"),
    ("Status", "docs/status.html"),
    ("日本語", "ja/index.html"),
]

NAV_DOCS = [
    ("Start here", [
        ("Docs home", "docs/index.html"),
        ("Architecture", "docs/architecture.html"),
        ("Get started", "docs/get-started.html"),
        ("Glossary", "docs/glossary.html"),
    ]),
    ("Protocol", [
        ("zkPI — payment instruction", "docs/zkpi.html"),
        ("DeFMI — settlement layer", "docs/defmi.html"),
        ("DeKYX — eligibility", "docs/dekyx.html"),
        ("DeCCP — clearing", "docs/deccp.html"),
    ]),
    ("Venues and upstream", [
        ("QOMM — oblivious RFQ", "docs/qomm.html"),
        ("OCLOB — oblivious order book", "docs/oclob.html"),
        ("Aethel — receivables", "docs/aethel.html"),
        ("Use cases beyond RFQ", "docs/use-cases.html"),
    ]),
    ("Evidence", [
        ("Measurements", "docs/measurements.html"),
        ("Security and trust boundary", "docs/security.html"),
        ("Position against prior work", "docs/prior-art.html"),
        ("Regulation", "docs/regulation.html"),
        ("Status and acceptance", "docs/status.html"),
    ]),
]

REPOS = [
    ("defmi", "https://github.com/shukob/defmi"),
    ("zkpi", "https://github.com/shukob/zkpi"),
    ("qomm", "https://github.com/shukob/qomm"),
    ("oclob", "https://github.com/shukob/oclob"),
    ("dekyx", "https://github.com/shukob/dekyx"),
    ("deccp", "https://github.com/shukob/deccp"),
    ("aethel", "https://github.com/shukob/aethel"),
]

HEAD = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · {site}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title} · {site}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta name="theme-color" content="#0b0f14">
<link rel="icon" href="{rel}favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{rel}style.css">
</head>
<body class="{bodyclass}">
<a class="skip" href="#main">Skip to content</a>
<header class="hdr">
  <div class="wrap">
    <a class="brand" href="{rel}index.html"><span class="mark">zk</span>FMI</a>
    <nav class="topnav" aria-label="Primary">
      {topnav}
      <a class="gh" href="https://github.com/shukob" rel="noopener">GitHub</a>
    </nav>
    <button class="menu" aria-label="Menu" aria-expanded="false" data-menu>≡</button>
  </div>
</header>
"""

FOOT = """
<footer class="foot">
  <div class="wrap">
    <div class="cols">
      <div>
        <div class="brand small"><span class="mark">zk</span>FMI</div>
        <p>Zero-knowledge financial market infrastructure. A research stack, measured, with its limits written down.</p>
        <p class="muted">zkfmi.com · built {date} · content MIT, like the code.</p>
      </div>
      <div>
        <h4>Repositories</h4>
        <ul>{repos}</ul>
      </div>
      <div>
        <h4>Read</h4>
        <ul>
          <li><a href="{rel}docs/architecture.html">Architecture</a></li>
          <li><a href="{rel}docs/zkpi.html">zkPI wire format</a></li>
          <li><a href="{rel}docs/measurements.html">Measurements</a></li>
          <li><a href="{rel}docs/security.html">Trust boundary</a></li>
          <li><a href="{rel}docs/status.html">What is not production</a></li>
        </ul>
      </div>
    </div>
    <p class="disclaimer">Nothing on this site is legal, investment or compliance advice. The software is a research implementation. It has not been audited, it does not custody assets, and no deployment has run across independent organisations. Every performance figure has a JSON artifact and a Rust binary that produced it; the host is labelled, not named.</p>
  </div>
</footer>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/11.15.0/mermaid.min.js"></script>
<script src="{rel}site.js"></script>
</body>
</html>
"""

def parse(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        sys.exit(f"{path}: missing header")
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    meta["body"] = m.group(2)
    for k in ("title", "description", "path", "section"):
        if k not in meta:
            sys.exit(f"{path}: header lacks {k}")
    return meta

def rel_prefix(out_path):
    depth = out_path.count("/")
    return "../" * depth

def build_nav(rel, current, items):
    out = []
    for label, href in items:
        cls = ' class="on"' if href == current or (href.endswith("docs/index.html") and current.startswith("docs/") and current not in [h for _, h in items]) else ""
        out.append(f'<a{cls} href="{rel}{href}">{label}</a>')
    return "\n      ".join(out)

def build_sidebar(rel, current):
    parts = ['<nav class="side" aria-label="Documentation">']
    for group, items in NAV_DOCS:
        parts.append(f'<h5>{group}</h5><ul>')
        for label, href in items:
            cls = ' class="on"' if href == current else ""
            parts.append(f'<li><a{cls} href="{rel}{href}">{label}</a></li>')
        parts.append("</ul>")
    parts.append("</nav>")
    return "\n".join(parts)

def toc(body):
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    if len(heads) < 2:
        return ""
    items = "".join(f'<li><a href="#{i}">{re.sub("<[^>]+>", "", t)}</a></li>' for i, t in heads)
    return f'<nav class="toc" aria-label="On this page"><h5>On this page</h5><ul>{items}</ul></nav>'

def render(meta):
    out_path = meta["path"]
    rel = rel_prefix(out_path)
    lang = "ja" if meta["section"] == "ja" else "en"
    head = HEAD.format(
        lang=lang, title=meta["title"], site=SITE, description=meta["description"],
        canonical=f"{DOMAIN}/{out_path}" if out_path != "index.html" else DOMAIN + "/",
        rel=rel, bodyclass=meta["section"], topnav=build_nav(rel, out_path, NAV_TOP),
    )
    if meta["section"] == "docs":
        main = f"""
<div class="wrap doclayout">
  {build_sidebar(rel, out_path)}
  <main id="main" class="doc">
    <article>
    {meta["body"]}
    </article>
  </main>
  {toc(meta["body"])}
</div>
"""
    else:
        main = f'\n<main id="main">\n{meta["body"]}\n</main>\n'
    repos = "".join(f'<li><a href="{u}" rel="noopener">shukob/{n}</a></li>' for n, u in REPOS)
    foot = FOOT.format(rel=rel, repos=repos, date=datetime.date.today().isoformat())
    return head + main + foot

def main():
    if os.path.isdir(PUBLIC):
        for name in os.listdir(PUBLIC):
            p = os.path.join(PUBLIC, name)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(PUBLIC, exist_ok=True)
    for static in ("style.css", "site.js", "favicon.svg", "robots.txt"):
        src = os.path.join(ROOT, "static", static)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(PUBLIC, static))
    pages = []
    for name in sorted(os.listdir(PAGES)):
        if not name.endswith(".html"):
            continue
        meta = parse(os.path.join(PAGES, name))
        out = os.path.join(PUBLIC, meta["path"])
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(render(meta))
        pages.append(meta["path"])
    with open(os.path.join(PUBLIC, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for p in pages:
            f.write(f"  <url><loc>{DOMAIN}/{'' if p == 'index.html' else p}</loc></url>\n")
        f.write("</urlset>\n")
    print(f"built {len(pages)} pages into {PUBLIC}")

if __name__ == "__main__":
    main()
