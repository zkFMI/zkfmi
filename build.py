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

Inside a fragment, `{{chart:NAME}}` is replaced with an inline SVG chart from
charts.py. No dependencies beyond the standard library.
"""
import os, re, shutil, sys, json, datetime, html as htmlmod
import charts

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
    ("FAQ", "docs/faq.html"),
    ("日本語", "ja/index.html"),
]

NAV_DOCS = [
    ("Start here", [
        ("Docs home", "docs/index.html"),
        ("Architecture", "docs/architecture.html"),
        ("Principles", "docs/principles.html"),
        ("FAQ", "docs/faq.html"),
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
    ("Deep dives", [
        ("Binding computed to committed", "docs/binding.html"),
        ("Audit machinery", "docs/audit.html"),
        ("Accountability and robustness", "docs/accountability.html"),
        ("Choosing a deployment", "docs/deployment.html"),
    ]),
    ("Evidence", [
        ("Measurements", "docs/measurements.html"),
        ("Security and trust boundary", "docs/security.html"),
        ("Position against prior work", "docs/prior-art.html"),
        ("Regulation", "docs/regulation.html"),
        ("Status and acceptance", "docs/status.html"),
        ("Roadmap", "docs/roadmap.html"),
    ]),
]

REPOS = [
    ("defmi", "3c83418", "2026-09-05"),
    ("zkpi", "62a4c42", "2026-09-04"),
    ("qomm", "27299a1", "2026-09-04"),
    ("oclob", "e43d901", "2026-09-05"),
    ("dekyx", "67eb59a", "2026-09-04"),
    ("deccp", "3660eba", "2026-09-04"),
    ("aethel", "96b7e16", "2026-09-04"),
]

HEAD = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · {site}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:site_name" content="zkFMI">
<meta property="og:title" content="{title} · {site}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{domain}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b0f14">
<link rel="icon" href="{rel}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap">
<link rel="stylesheet" href="{rel}style.css">
{analytics}<script>try{{var t=localStorage.getItem('zkfmi-theme');if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}</script>
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
    <div class="tools">
      <button class="search-btn" type="button" aria-label="Search (press /)" data-search-open><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><span>Search</span><kbd>/</kbd></button>
      <button class="theme" type="button" aria-label="Toggle theme" data-theme-toggle><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
      <button class="menu" type="button" aria-label="Menu" aria-expanded="false" data-menu>≡</button>
    </div>
  </div>
</header>
<div class="search-modal" hidden data-search-modal>
  <div class="search-box" role="dialog" aria-label="Search documentation">
    <input type="search" placeholder="Search the documentation…" autocomplete="off" data-search-input>
    <ul class="search-results" data-search-results></ul>
    <p class="search-hint">Type to search titles, headings and text. Esc closes.</p>
  </div>
</div>
"""

FOOT = """
<footer class="foot">
  <div class="wrap">
    <div class="cols">
      <div>
        <div class="brand small"><span class="mark">zk</span>FMI</div>
        <p>Zero-knowledge financial market infrastructure. A research stack, measured, with its limits written down.</p>
        <p class="muted">zkfmi.com · site built {date} · content and code MIT.{analytics_note}</p>
      </div>
      <div>
        <h4>Repositories</h4>
        <ul class="repos">{repos}</ul>
      </div>
      <div>
        <h4>Read</h4>
        <ul>
          <li><a href="{rel}docs/architecture.html">Architecture</a></li>
          <li><a href="{rel}docs/principles.html">How this project works</a></li>
          <li><a href="{rel}docs/zkpi.html">zkPI wire format</a></li>
          <li><a href="{rel}docs/measurements.html">Measurements</a></li>
          <li><a href="{rel}docs/security.html">Trust boundary</a></li>
          <li><a href="{rel}docs/status.html">What is not production</a></li>
          <li><a href="{rel}docs/faq.html">FAQ</a></li>
        </ul>
      </div>
    </div>
    <p class="disclaimer">Nothing on this site is legal, investment or compliance advice. The software is a research implementation. It has not been audited, it does not custody assets, there is no token, and no deployment has run across independent organisations. Every performance figure has a JSON artifact and a Rust binary that produced it; the host is labelled, not named.</p>
  </div>
</footer>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/11.15.0/mermaid.min.js"></script>
<script src="{rel}site.js" defer></script>
</body>
</html>
"""

def analytics():
    """Plausible, enabled only when ZKFMI_PLAUSIBLE_DOMAIN is set (or a raw snippet is given)."""
    raw = os.environ.get("ZKFMI_ANALYTICS_HTML", "").strip()
    if raw:
        return raw + "\n", " · analytics: privacy-preserving, no cookies"
    domain = os.environ.get("ZKFMI_PLAUSIBLE_DOMAIN", "").strip()
    if not domain:
        return "", ""
    src = os.environ.get("ZKFMI_PLAUSIBLE_SRC", "").strip() or "https://plausible.io/js/script.outbound-links.js"
    tag = f'<script defer data-domain="{htmlmod.escape(domain)}" src="{htmlmod.escape(src)}"></script>\n'
    return tag, " · analytics by Plausible: no cookies, no personal data, no cross-site tracking"

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
    return "../" * out_path.count("/")

def build_nav(rel, current, items):
    out = []
    docs_pages = {h for _, group in NAV_DOCS for _, h in group}
    for label, href in items:
        on = href == current or (href == "docs/index.html" and current in docs_pages and current not in [h for _, h in items])
        cls = ' class="on"' if on else ""
        out.append(f'<a{cls} href="{rel}{href}">{label}</a>')
    return "\n      ".join(out)

def build_sidebar(rel, current):
    parts = ['<nav class="side" aria-label="Documentation">', '<button type="button" class="side-toggle" aria-expanded="false" data-side-toggle>Documentation menu <span aria-hidden="true">▾</span></button>', '<div class="side-body">']
    for group, items in NAV_DOCS:
        parts.append(f'<h5>{group}</h5><ul>')
        for label, href in items:
            cls = ' class="on"' if href == current else ""
            parts.append(f'<li><a{cls} href="{rel}{href}">{label}</a></li>')
        parts.append("</ul>")
    parts.append("</div></nav>")
    return "\n".join(parts)

def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()

def toc(body):
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    if len(heads) < 2:
        return ""
    items = "".join(f'<li><a href="#{i}">{strip_tags(t)}</a></li>' for i, t in heads)
    return f'<nav class="toc" aria-label="On this page"><h5>On this page</h5><ul>{items}</ul></nav>'

def expand_charts(body, chart_map):
    def rep(m):
        name = m.group(1)
        if name not in chart_map:
            sys.exit(f"unknown chart {name}")
        return chart_map[name]
    return re.sub(r"\{\{chart:([a-z_]+)\}\}", rep, body)

def search_entries(meta, body):
    """One entry per h2 section plus one for the page."""
    entries = [{"t": meta["title"], "h": "", "u": meta["path"], "x": strip_tags(re.sub(r'<h2.*', '', body, flags=re.S))[:1500]}]
    parts = re.split(r'(<h2 id="[^"]+">.*?</h2>)', body)
    for i in range(1, len(parts), 2):
        m = re.match(r'<h2 id="([^"]+)">(.*?)</h2>', parts[i])
        text = strip_tags(parts[i + 1] if i + 1 < len(parts) else "")
        entries.append({"t": meta["title"], "h": strip_tags(m.group(2)), "u": f"{meta['path']}#{m.group(1)}", "x": text[:3000]})
    return entries

def render(meta, chart_map):
    out_path = meta["path"]
    rel = rel_prefix(out_path)
    lang = "ja" if meta["section"] == "ja" else "en"
    body = expand_charts(meta["body"], chart_map)
    tag, note = analytics()
    head = HEAD.format(
        lang=lang, title=htmlmod.escape(meta["title"]), site=SITE, description=htmlmod.escape(meta["description"]),
        canonical=f"{DOMAIN}/{out_path}" if out_path != "index.html" else DOMAIN + "/",
        rel=rel, bodyclass=meta["section"], topnav=build_nav(rel, out_path, NAV_TOP), domain=DOMAIN, analytics=tag,
    )
    if meta["section"] == "docs":
        main = f"""
<div class="wrap doclayout">
  {build_sidebar(rel, out_path)}
  <main id="main" class="doc">
    <article>
    {body}
    </article>
  </main>
  {toc(body)}
</div>
"""
    else:
        main = f'\n<main id="main">\n{body}\n</main>\n'
    repos = "".join(f'<li><a href="https://github.com/shukob/{n}" rel="noopener">shukob/{n}</a> <span class="muted">{h} · {d}</span></li>' for n, h, d in REPOS)
    foot = FOOT.format(rel=rel, repos=repos, date=datetime.date.today().isoformat(), analytics_note=note)
    return head + main + foot, body

def main():
    if os.path.isdir(PUBLIC):
        for name in os.listdir(PUBLIC):
            p = os.path.join(PUBLIC, name)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(PUBLIC, exist_ok=True)
    for static in os.listdir(os.path.join(ROOT, "static")):
        shutil.copy(os.path.join(ROOT, "static", static), os.path.join(PUBLIC, static))
    chart_map = charts.all_charts()
    pages, index = [], []
    for name in sorted(os.listdir(PAGES)):
        if not name.endswith(".html"):
            continue
        meta = parse(os.path.join(PAGES, name))
        html, body = render(meta, chart_map)
        out = os.path.join(PUBLIC, meta["path"])
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(html)
        pages.append(meta["path"])
        if meta["section"] != "ja":
            index.extend(search_entries(meta, body))
    with open(os.path.join(PUBLIC, "search.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(PUBLIC, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for p in pages:
            f.write(f"  <url><loc>{DOMAIN}/{'' if p == 'index.html' else p}</loc></url>\n")
        f.write("</urlset>\n")
    print(f"built {len(pages)} pages, {len(index)} search entries into {PUBLIC}")

if __name__ == "__main__":
    main()
