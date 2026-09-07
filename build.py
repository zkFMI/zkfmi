#!/usr/bin/env python3
"""Build zkfmi.com: wrap page fragments in pages/ with the shared template into public/.

A fragment starts with a header block:

    ---
    title: zkPI
    description: one line
    path: docs/zkpi.html
    section: docs          (docs | top)
    ---
    <body html>

English fragments live in pages/, Japanese ones in pages/ja/ under the same
file name and with the same `path:`; the Japanese page is written to ja/<path>.
Every page carries a language switch to its counterpart and hreflang links.

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
LANGS = ("en", "ja")

# (english label, japanese label, href relative to the language root)
NAV_TOP = [
    ("Overview", "概要", "index.html"),
    ("Architecture", "全体構成", "docs/architecture.html"),
    ("Docs", "ドキュメント", "docs/index.html"),
    ("Measurements", "計測値", "docs/measurements.html"),
    ("Status", "現状", "docs/status.html"),
    ("FAQ", "FAQ", "docs/faq.html"),
]

NAV_DOCS = [
    ("Start here", "はじめに", [
        ("Docs home", "ドキュメント一覧", "docs/index.html"),
        ("Architecture", "全体構成", "docs/architecture.html"),
        ("Principles", "この研究の進め方", "docs/principles.html"),
        ("FAQ", "よくある質問", "docs/faq.html"),
        ("Get started", "始め方", "docs/get-started.html"),
        ("Glossary", "用語集", "docs/glossary.html"),
    ]),
    ("Protocol", "プロトコル", [
        ("zkPI — payment instruction", "zkPI — 証明付き決済指図", "docs/zkpi.html"),
        ("DeFMI — settlement layer", "DeFMI — 決済層", "docs/defmi.html"),
        ("DeKYX — eligibility", "DeKYX — 資格", "docs/dekyx.html"),
        ("DeCCP — clearing", "DeCCP — 清算", "docs/deccp.html"),
        ("Cryptography in use", "暗号技術の使い方", "docs/cryptography.html"),
    ]),
    ("Venues", "市場", [
        ("QOMM — oblivious RFQ", "QOMM — 依頼を見ない見積市場", "docs/qomm.html"),
        ("OCLOB — oblivious order book", "OCLOB — 注文を見ない板", "docs/oclob.html"),
    ]),
    ("Applications", "業務システム", [
        ("Aethel — receivables", "Aethel — 債権化", "docs/aethel.html"),
        ("Applications beyond venues", "市場以外の業務システム", "docs/use-cases.html"),
    ]),
    ("Deep dives (RFQ venue)", "深掘り（見積市場）", [
        ("Binding computed to committed", "計算結果を commitment に束縛する", "docs/binding.html"),
        ("Audit machinery", "監査の仕組み", "docs/audit.html"),
        ("Accountability and robustness", "説明責任と頑健性", "docs/accountability.html"),
        ("Choosing a deployment", "配置の選び方", "docs/deployment.html"),
    ]),
    ("Evidence", "根拠", [
        ("Measurements", "計測値", "docs/measurements.html"),
        ("Security and trust boundary", "安全性と信頼境界", "docs/security.html"),
        ("Post-quantum migration", "耐量子化への移行", "docs/post-quantum.html"),
        ("Position against prior work", "先行研究との位置関係", "docs/prior-art.html"),
        ("Comparison with other systems", "他のシステムとの比較", "docs/comparison.html"),
        ("Regulation", "規制", "docs/regulation.html"),
        ("Status and acceptance", "現状と受入", "docs/status.html"),
        ("Roadmap", "今後の計画", "docs/roadmap.html"),
    ]),
]

REPOS = [
    ("defmi", "6715562", "2026-09-07"),
    ("zkpi", "d346304", "2026-09-07"),
    ("qomm", "538a63d", "2026-09-07"),
    ("oclob", "1a4af96", "2026-09-07"),
    ("dekyx", "4ea50f5", "2026-09-07"),
    ("deccp", "934343f", "2026-09-07"),
    ("aethel", "05301f6", "2026-09-07"),
    ("zkfmi-crypto", "75fdf83", "2026-09-08"),
    ("zkfmi", "site", "2026-09-07"),
]

UI = {
    "en": {
        "skip": "Skip to content", "nav_primary": "Primary", "nav_docs": "Documentation",
        "search": "Search", "search_aria": "Search (press /)", "theme": "Toggle theme", "menu": "Menu",
        "search_dialog": "Search documentation", "search_placeholder": "Search the documentation…",
        "search_hint": "Type to search titles, headings and text. Esc closes.",
        "side_menu": "Documentation menu", "side_collapse": "Collapse or expand the documentation menu", "side_lbl": "Docs",
        "toc": "On this page", "toc_collapse": "Collapse or expand the table of contents",
        "switch_label": "日本語", "switch_title": "日本語版を読む", "switch_lang": "ja",
        "tagline": "Zero-knowledge financial market infrastructure. A research stack, measured, with its limits written down.",
        "meta": "zkfmi.com · site built {date} · content and code MIT.",
        "repos": "Repositories", "read": "Read",
        "read_links": [("docs/architecture.html", "Architecture"), ("docs/principles.html", "How this project works"), ("docs/zkpi.html", "zkPI wire format"), ("docs/measurements.html", "Measurements"), ("docs/security.html", "Trust boundary"), ("docs/status.html", "What is not production"), ("docs/faq.html", "FAQ")],
        "disclaimer": "Nothing on this site is legal, investment or compliance advice. The software is a research implementation. It has not been audited, it does not custody assets, there is no token, and no deployment has run across independent organisations. Every performance figure has a JSON artifact and a Rust binary that produced it; the host is labelled, not named.",
        "analytics_note_raw": " · analytics: privacy-preserving, no cookies",
        "analytics_note": " · analytics by Plausible: no cookies, no personal data, no cross-site tracking",
    },
    "ja": {
        "skip": "本文へ", "nav_primary": "主要", "nav_docs": "ドキュメント",
        "search": "検索", "search_aria": "検索（/ キー）", "theme": "配色を切り替える", "menu": "メニュー",
        "search_dialog": "ドキュメントを検索", "search_placeholder": "ドキュメントを検索…",
        "search_hint": "題名・見出し・本文を検索します。Esc で閉じます。",
        "side_menu": "ドキュメントの目次", "side_collapse": "ドキュメントの目次を開閉する", "side_lbl": "目次",
        "toc": "このページ", "toc_collapse": "ページ内目次を開閉する",
        "switch_label": "English", "switch_title": "Read this page in English", "switch_lang": "en",
        "tagline": "ゼロ知識証明付きの金融市場基盤。計測済みの研究スタックで、限界は文書に書いてある。",
        "meta": "zkfmi.com · サイト生成 {date} · 内容とコードは MIT。",
        "repos": "リポジトリ", "read": "読む",
        "read_links": [("docs/architecture.html", "全体構成"), ("docs/principles.html", "この研究の進め方"), ("docs/zkpi.html", "zkPI の wire 形式"), ("docs/measurements.html", "計測値"), ("docs/security.html", "信頼境界"), ("docs/status.html", "本番でないもの"), ("docs/faq.html", "よくある質問")],
        "disclaimer": "このサイトの内容は法律・投資・コンプライアンスの助言ではない。ソフトウェアは研究実装であり、監査を受けておらず、資産を保管せず、トークンはなく、独立した組織をまたぐ運用は行っていない。性能の数値にはすべて JSON の artifact とそれを出した Rust バイナリがあり、ホストは名前ではなくラベルで示す。",
        "analytics_note_raw": " · 解析: プライバシー保護、cookie なし",
        "analytics_note": " · 解析は Plausible: cookie なし、個人データなし、サイト横断の追跡なし",
    },
}

LOGO = '<svg class="logo" width="26" height="26" viewBox="0 0 64 64" aria-hidden="true"><g transform="translate(32,32) scale(0.95)"><line x1="0" y1="-30" x2="0" y2="30" stroke="var(--accent)" stroke-width="3" stroke-dasharray="4 3"/><rect x="-22" y="-26" width="44" height="12" rx="3" fill="none" stroke="var(--line-2)" stroke-width="3"/><rect x="-22" y="-6" width="44" height="12" rx="3" fill="none" stroke="var(--accent)" stroke-width="3"/><rect x="-22" y="14" width="44" height="12" rx="3" fill="none" stroke="var(--line-2)" stroke-width="3"/><rect x="-14" y="-23" width="10" height="6" rx="1" fill="var(--accent-2)"/><rect x="4" y="-23" width="10" height="6" rx="1" fill="var(--accent-3)"/><rect x="-14" y="17" width="10" height="6" rx="1" fill="var(--accent-2)"/><rect x="4" y="17" width="10" height="6" rx="1" fill="var(--accent-3)"/><polygon points="0,-9 7.8,-4.5 7.8,4.5 0,9 -7.8,4.5 -7.8,-4.5" fill="var(--accent)" stroke="var(--bg)" stroke-width="2" stroke-linejoin="round"/></g></svg>'

HEAD = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · {site}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
{alternates}<meta property="og:site_name" content="zkFMI">
<meta property="og:title" content="{title} · {site}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{domain}/og.png">
<meta property="og:locale" content="{og_locale}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b0f14">
<link rel="icon" href="{rel}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600{jpfont}&display=swap">
<link rel="stylesheet" href="{rel}style.css">
{analytics}<script>try{{var t=localStorage.getItem('zkfmi-theme');if(t)document.documentElement.setAttribute('data-theme',t);var h=document.documentElement;h.classList.add(localStorage.getItem('zkfmi-toc')==='open'?'toc-open':'toc-closed');if(localStorage.getItem('zkfmi-side')==='closed')h.classList.add('side-closed');}}catch(e){{document.documentElement.classList.add('toc-closed');}}</script>
</head>
<body class="{bodyclass}" data-search="{searchurl}">
<a class="skip" href="#main">{ui[skip]}</a>
<header class="hdr">
  <div class="wrap">
    <a class="brand" href="{L}index.html">{logo}<span class="mark">zk</span>FMI</a>
    <nav class="topnav" aria-label="{ui[nav_primary]}">
      {topnav}
      <a class="gh" href="https://github.com/zkFMI" rel="noopener">GitHub</a>
    </nav>
    <div class="tools">
      <a class="lang" href="{switch_href}" lang="{ui[switch_lang]}" hreflang="{ui[switch_lang]}" title="{ui[switch_title]}"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg><span>{ui[switch_label]}</span></a>
      <button class="search-btn" type="button" aria-label="{ui[search_aria]}" data-search-open><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><span>{ui[search]}</span><kbd>/</kbd></button>
      <button class="theme" type="button" aria-label="{ui[theme]}" data-theme-toggle><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
      <button class="menu" type="button" aria-label="{ui[menu]}" aria-expanded="false" data-menu>≡</button>
    </div>
  </div>
</header>
<div class="search-modal" hidden data-search-modal>
  <div class="search-box" role="dialog" aria-label="{ui[search_dialog]}">
    <input type="search" placeholder="{ui[search_placeholder]}" autocomplete="off" data-search-input>
    <ul class="search-results" data-search-results></ul>
    <p class="search-hint">{ui[search_hint]}</p>
  </div>
</div>
"""

FOOT = """
<footer class="foot">
  <div class="wrap">
    <div class="cols">
      <div>
        <div class="brand small">{logo}<span class="mark">zk</span>FMI</div>
        <p>{ui[tagline]}</p>
        <p class="muted">{meta}{analytics_note}</p>
      </div>
      <div>
        <h4>{ui[repos]}</h4>
        <ul class="repos">{repos}</ul>
      </div>
      <div>
        <h4>{ui[read]}</h4>
        <ul>
{read_links}
        </ul>
      </div>
    </div>
    <p class="disclaimer">{ui[disclaimer]}</p>
  </div>
</footer>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/11.15.0/mermaid.min.js"></script>
<script src="{rel}site.js" defer></script>
</body>
</html>
"""

def analytics(lang):
    """Plausible, enabled only when ZKFMI_PLAUSIBLE_DOMAIN is set (or a raw snippet is given)."""
    raw = os.environ.get("ZKFMI_ANALYTICS_HTML", "").strip()
    if raw:
        return raw + "\n", UI[lang]["analytics_note_raw"]
    domain = os.environ.get("ZKFMI_PLAUSIBLE_DOMAIN", "").strip()
    if not domain:
        return "", ""
    src = os.environ.get("ZKFMI_PLAUSIBLE_SRC", "").strip() or "https://plausible.io/js/script.outbound-links.js"
    tag = f'<script defer data-domain="{htmlmod.escape(domain)}" src="{htmlmod.escape(src)}"></script>\n'
    return tag, UI[lang]["analytics_note"]

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

def out_path_for(lang, path):
    return path if lang == "en" else "ja/" + path

def rel_prefix(out_path):
    return "../" * out_path.count("/")

def label(item, lang):
    return item[0] if lang == "en" else item[1]

def build_nav(L, current, lang):
    out = []
    docs_pages = {h for _, _, group in NAV_DOCS for _, _, h in group}
    top_hrefs = [h for _, _, h in NAV_TOP]
    for item in NAV_TOP:
        href = item[2]
        on = href == current or (href == "docs/index.html" and current in docs_pages and current not in top_hrefs)
        cls = ' class="on"' if on else ""
        out.append(f'<a{cls} href="{L}{href}">{label(item, lang)}</a>')
    return "\n      ".join(out)

def build_sidebar(L, current, lang):
    ui = UI[lang]
    parts = [f'<nav class="side" aria-label="{ui["nav_docs"]}">',
             f'<button type="button" class="side-toggle" aria-expanded="false" data-side-toggle>{ui["side_menu"]} <span aria-hidden="true">▾</span></button>',
             f'<button type="button" class="rail-toggle side-rail" data-collapse="side" aria-label="{ui["side_collapse"]}" title="{ui["side_menu"]}"><span class="ico">◂</span><span class="lbl">{ui["side_lbl"]}</span></button>',
             '<div class="side-body">']
    for group in NAV_DOCS:
        parts.append(f'<h5>{label(group, lang)}</h5><ul>')
        for item in group[2]:
            href = item[2]
            cls = ' class="on"' if href == current else ""
            parts.append(f'<li><a{cls} href="{L}{href}">{label(item, lang)}</a></li>')
        parts.append("</ul>")
    parts.append("</div></nav>")
    return "\n".join(parts)

def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()

def toc(body, lang):
    ui = UI[lang]
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    if len(heads) < 2:
        return ""
    items = "".join(f'<li><a href="#{i}">{strip_tags(t)}</a></li>' for i, t in heads)
    return (f'<nav class="toc" aria-label="{ui["toc"]}"><button type="button" class="rail-toggle toc-rail" data-collapse="toc" aria-label="{ui["toc_collapse"]}" title="{ui["toc"]}">'
            f'<span class="ico">▸</span><span class="lbl">{ui["toc"]}</span></button><div class="toc-body"><h5>{ui["toc"]}</h5><ul>{items}</ul></div></nav>')

def expand_charts(body, chart_map):
    def rep(m):
        name = m.group(1)
        if name not in chart_map:
            sys.exit(f"unknown chart {name}")
        return chart_map[name]
    return re.sub(r"\{\{chart:([a-z_]+)\}\}", rep, body)

def search_entries(meta, body, out_path):
    """One entry per h2 section plus one for the page. `u` is relative to the site root."""
    entries = [{"t": meta["title"], "h": "", "u": out_path, "x": strip_tags(re.sub(r'<h2.*', '', body, flags=re.S))[:1500]}]
    parts = re.split(r'(<h2 id="[^"]+">.*?</h2>)', body)
    for i in range(1, len(parts), 2):
        m = re.match(r'<h2 id="([^"]+)">(.*?)</h2>', parts[i])
        text = strip_tags(parts[i + 1] if i + 1 < len(parts) else "")
        entries.append({"t": meta["title"], "h": strip_tags(m.group(2)), "u": f"{out_path}#{m.group(1)}", "x": text[:3000]})
    return entries

def url_for(out_path):
    return DOMAIN + "/" if out_path == "index.html" else f"{DOMAIN}/{out_path}"

def render(meta, lang, chart_map, available):
    """available: {lang: set of page paths} so the switch and hreflang only point at pages that exist."""
    ui = UI[lang]
    path = meta["path"]
    out_path = out_path_for(lang, path)
    rel = rel_prefix(out_path)
    L = rel + ("ja/" if lang == "ja" else "")          # language root
    other = "ja" if lang == "en" else "en"
    other_L = rel + ("ja/" if other == "ja" else "")
    switch_href = other_L + (path if path in available[other] else "index.html")
    alternates = ""
    if path in available["en"] and path in available["ja"]:
        alternates = (f'<link rel="alternate" hreflang="en" href="{url_for(path)}">\n'
                      f'<link rel="alternate" hreflang="ja" href="{url_for("ja/" + path)}">\n'
                      f'<link rel="alternate" hreflang="x-default" href="{url_for(path)}">\n')
    body = expand_charts(meta["body"], chart_map)
    tag, note = analytics(lang)
    head = HEAD.format(
        lang=lang, title=htmlmod.escape(meta["title"]), site=SITE, description=htmlmod.escape(meta["description"]),
        canonical=url_for(out_path), alternates=alternates, og_locale="ja_JP" if lang == "ja" else "en_US",
        jpfont="&family=Noto+Sans+JP:wght@400;500;700" if lang == "ja" else "",
        rel=rel, L=L, logo=LOGO, bodyclass=meta["section"] + (" ja" if lang == "ja" else ""),
        searchurl=f"{rel}{'ja/' if lang == 'ja' else ''}search.json",
        topnav=build_nav(L, path, lang), switch_href=switch_href, domain=DOMAIN, analytics=tag, ui=ui,
    )
    if meta["section"] == "docs":
        main = f"""
<div class="wrap doclayout">
  {build_sidebar(L, path, lang)}
  <main id="main" class="doc">
    <article>
    {body}
    </article>
  </main>
  {toc(body, lang)}
</div>
"""
    else:
        main = f'\n<main id="main">\n{body}\n</main>\n'
    repos = "".join(f'<li><a href="https://github.com/zkFMI/{n}" rel="noopener">zkFMI/{n}</a> <span class="muted">{h} · {d}</span></li>' for n, h, d in REPOS)
    read_links = "\n".join(f'          <li><a href="{L}{h}">{t}</a></li>' for h, t in ui["read_links"])
    foot = FOOT.format(rel=rel, logo=LOGO, repos=repos, read_links=read_links, ui=ui,
                       meta=ui["meta"].format(date=datetime.date.today().isoformat()), analytics_note=note)
    return head + main + foot, body, out_path

def load_pages():
    """{lang: [meta, ...]} from pages/ (en) and pages/ja/ (ja). Legacy `section: ja` fragments are skipped."""
    out = {"en": [], "ja": []}
    for lang in LANGS:
        d = PAGES if lang == "en" else os.path.join(PAGES, "ja")
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".html"):
                continue
            meta = parse(os.path.join(d, name))
            if meta["section"] == "ja":
                continue
            meta["file"] = name
            out[lang].append(meta)
    return out

def main():
    if os.path.isdir(PUBLIC):
        for name in os.listdir(PUBLIC):
            p = os.path.join(PUBLIC, name)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(PUBLIC, exist_ok=True)
    for static in os.listdir(os.path.join(ROOT, "static")):
        shutil.copy(os.path.join(ROOT, "static", static), os.path.join(PUBLIC, static))
    pages = load_pages()
    available = {lang: {m["path"] for m in pages[lang]} for lang in LANGS}
    en_files = {m["file"] for m in pages["en"]}
    for m in pages["ja"]:
        if m["file"] not in en_files:
            sys.exit(f"pages/ja/{m['file']} has no English original")
    written, urls = [], {}
    for lang in LANGS:
        chart_map = charts.all_charts(lang)
        index = []
        for meta in pages[lang]:
            html, body, out_path = render(meta, lang, chart_map, available)
            out = os.path.join(PUBLIC, out_path)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, "w", encoding="utf-8").write(html)
            written.append(out_path)
            urls.setdefault(meta["path"], {})[lang] = out_path
            index.extend(search_entries(meta, body, out_path))
        idx = os.path.join(PUBLIC, "search.json" if lang == "en" else "ja/search.json")
        if index or lang == "en":
            os.makedirs(os.path.dirname(idx), exist_ok=True)
            with open(idx, "w", encoding="utf-8") as f:
                json.dump(index, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(PUBLIC, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n')
        for path, by_lang in urls.items():
            alts = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{url_for(p)}"/>' for l, p in by_lang.items()) if len(by_lang) > 1 else ""
            for l, p in by_lang.items():
                f.write(f"  <url><loc>{url_for(p)}</loc>{alts}</url>\n")
        f.write("</urlset>\n")
    missing = available["en"] - available["ja"]
    note = f"; {len(missing)} English pages without a Japanese version" if missing else ""
    print(f"built {len(written)} pages ({len(pages['en'])} en, {len(pages['ja'])} ja) into {PUBLIC}{note}")

if __name__ == "__main__":
    main()
