#!/usr/bin/env python3
"""Check a Japanese page against its English original: same structure, same
numbers, same code, translated text, no banned words. Usage:
    python3 tools/check_ja.py pages/ja/NAME.html [...]   (no args: all)
"""
import re, sys, os, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANNED = ["取引所", "上流", "梯子", "バックオフ"]
KEEP_ATTRS = ("id", "class", "href", "colspan", "rowspan", "src", "data-collapse", "data-side-toggle", "style")

def header(text, path):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m: return None, None, f"{path}: missing header"
    meta = dict((k.strip(), v.strip()) for k, _, v in (l.partition(":") for l in m.group(1).splitlines()))
    return meta, m.group(2), None

def skeleton(body):
    out = []
    for m in re.finditer(r"<(/?)([a-zA-Z0-9]+)([^>]*)>", body):
        closing, tag, attrs = m.groups()
        if tag in ("br",) : continue
        kept = []
        for a in KEEP_ATTRS:
            am = re.search(r'\b%s="([^"]*)"' % a, attrs)
            if am: kept.append(f'{a}={am.group(1)}')
        out.append(("/" if closing else "") + tag + (" " + " ".join(kept) if kept else ""))
    return out

def text_only(body):
    body = re.sub(r"<pre class=\"mermaid\">.*?</pre>", " ", body, flags=re.S)
    return re.sub(r"<[^>]+>", " ", body)

def numbers(body):
    return {n.rstrip(",.") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", text_only(body))}

def codes(body):
    return re.findall(r"<code>(.*?)</code>", body, re.S)

def check(ja_path):
    name = os.path.basename(ja_path)
    en_path = os.path.join(ROOT, "pages", name)
    errs = []
    if not os.path.exists(en_path): return [f"no English original for {name}"]
    en_meta, en_body, e = header(open(en_path, encoding="utf-8").read(), en_path)
    ja_meta, ja_body, e2 = header(open(ja_path, encoding="utf-8").read(), ja_path)
    if e or e2: return [x for x in (e, e2) if x]
    for k in ("path", "section"):
        if en_meta.get(k) != ja_meta.get(k): errs.append(f"header {k} differs: {en_meta.get(k)!r} vs {ja_meta.get(k)!r}")
    for k in ("title", "description"):
        if not ja_meta.get(k): errs.append(f"header {k} empty")
        elif ja_meta[k] == en_meta.get(k): errs.append(f"header {k} not translated")
    se, sj = skeleton(en_body), skeleton(ja_body)
    if se != sj:
        i = next((i for i, (a, b) in enumerate(zip(se, sj)) if a != b), min(len(se), len(sj)))
        errs.append(f"structure differs at tag #{i}: en={se[i] if i < len(se) else 'END'!r} ja={sj[i] if i < len(sj) else 'END'!r} (en {len(se)} tags, ja {len(sj)})")
    ce, cj = codes(en_body), codes(ja_body)
    if ce != cj:
        i = next((i for i, (a, b) in enumerate(zip(ce, cj)) if a != b), min(len(ce), len(cj)))
        errs.append(f"<code> #{i} differs: en={ce[i] if i < len(ce) else 'END'!r} ja={cj[i] if i < len(cj) else 'END'!r}")
    if re.findall(r"\{\{chart:[a-z_]+\}\}", en_body) != re.findall(r"\{\{chart:[a-z_]+\}\}", ja_body): errs.append("chart tokens differ")
    missing = numbers(en_body) - numbers(ja_body)
    if missing: errs.append(f"numbers missing in ja: {sorted(missing)[:15]}")
    txt = text_only(ja_body)
    for w in BANNED:
        if w in txt: errs.append(f"banned word: {w}")
    cjk = len(re.findall(r"[぀-ヿ一-鿿]", txt)); latin = len(re.findall(r"[A-Za-z]", txt))
    if cjk < 0.6 * latin: errs.append(f"looks untranslated: {cjk} CJK vs {latin} Latin letters")
    for m in re.finditer(r"<pre class=\"mermaid\">(.*?)</pre>", ja_body, re.S):
        for line in m.group(1).splitlines():
            if ";" in line: errs.append(f"';' in mermaid line: {line.strip()[:60]}")
    return errs

if __name__ == "__main__":
    paths = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, "pages", "ja", "*.html")))
    bad = 0
    for p in paths:
        errs = check(p)
        print(("PASS " if not errs else "FAIL ") + os.path.basename(p))
        for e in errs: print("   -", e)
        bad += bool(errs)
    sys.exit(1 if bad else 0)
